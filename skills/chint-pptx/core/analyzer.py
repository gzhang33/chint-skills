#!/usr/bin/env python3
"""chint-pptx 测定层 / 分析层（S2 + S3 的「判定」侧）

源稿 ─[Analyzer]→ Slide IR（含六类形态判定 + 置信度 + 逐页标题/外壳语言）

设计原则（来自 2026-09-17 重构计划 Q9/Q15/Q16 与 S3 目标架构）
  * 零形态声明：所有判定由阈值与 XML/渲染证据推出，不读人工形态清单。
  * 阈值唯一来源：spec/2026VI.yaml。本文件不出现任何散落魔法数，全部经 load_spec 读取。
  * 低置信才渲染：仅「深底候选页」触发 LibreOffice→PDF→栅格，取中位亮度；渲染调用计数并受上限约束。
  * 不猜默认：判定不出/不确定显式写入 decisions.json（与稿同目录），报告列出。
  * Analyzer 只认源稿，不读 config 的形态键；其产出（Slide IR）是 Planner 的唯一事实来源。

输入：源稿 pptx 路径（+ spec）
输出：JSON 测定报告（每页 IR + 六类形态判定 + 置信度/依据 + 逐页标题）+ 外壳语言 + 封面原文
      低置信记录：<deck>.decisions.json（与稿同目录，可删可重算）

本模块是 scripts/measure_form.py 测定核心的迁入目标；measure_form.py 现已退化为薄 CLI 壳。

用法（等价原 measure_form.py）：
    python3 -m core.analyzer <source.pptx> [--out DIR] [--spec PATH] [--deck NAME]
"""
from __future__ import annotations

from core.common import (
    inn,
    emu,
    rgb,
    canvas_scale,
    looks_like_department,
    looks_like_introduction_suffix,
    appended_cover_suffix,
    text_width_in,
    detect_source_language,
    source_cover_copy,
)

import argparse
import json
import pathlib
import re
import subprocess
import sys
import tempfile

from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE

import yaml  # pyyaml

# find_source_title / find_promoted_heading 来自保真度门禁（确定性抽取，非判定），
# 供 _extract_title 把标题事实搬进 IR。Analyzer 读源稿、Planner 不读，故放在分析层。
_SCRIPTS = pathlib.Path(__file__).resolve().parent.parent / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))
from verify_preserve_source import find_source_title, find_promoted_heading  # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent
SKILL = HERE.parent
SPEC_DEFAULT = SKILL / "spec" / "2026VI.yaml"
SOFFICE = "/Applications/LibreOffice.app/Contents/MacOS/soffice"

# Analyzer 需要读取源稿的「外壳语言」与「封面原文」，这两件事是判定的前置事实提取，
# 故放在分析层（Analyzer 读源稿，Planner 不读）。语言常量与 Planner 共享，避免漂移。
from core.planner import LANG_ZH, LANG_EN, LANG_CJK_THRESHOLD, _CJK_RE  # noqa: E402

PPTX_NS = "http://schemas.openxmlformats.org/presentationml/2006/main"
DRAW_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"

SCHEMA_REPORT = "chint-form-measure/1"
SCHEMA_DECISIONS = "chint-form-decisions/1"


# --------------------------------------------------------------------------- #
# spec 加载
# --------------------------------------------------------------------------- #
def load_spec(path: pathlib.Path = SPEC_DEFAULT) -> dict:
    if not path.exists():
        raise SystemExit(f"[FAIL] 找不到规格文件: {path}")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    # 守卫：本文件不得出现 6 位十六进制色值
    bad = re.findall(r"#[0-9A-Fa-f]{6}\b", json.dumps(data, ensure_ascii=False, default=str))
    if bad:
        raise SystemExit(f"[FAIL] 2026VI.yaml 含散落色值 {bad}；颜色必须引用 brand_tokens 键名")
    return data


def T(spec, *keys):
    """读取 form_measurement.thresholds 下的阈值。"""
    node = spec["form_measurement"]["thresholds"]
    for k in keys:
        node = node[k]
    return node


def markers(spec, kind):
    return spec["form_measurement"]["vocabulary"]["layout_markers"][kind]


# --------------------------------------------------------------------------- #
# 源稿事实提取（外壳语言 / 封面原文 / 逐页标题）—— Analyzer 读源稿的权限内
# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #
# 单页 XML 层指标
# --------------------------------------------------------------------------- #
def inch(emu):
    return emu / 914400.0


def is_marker_layout(name, marker_list):
    if not name:
        return False
    low = name.lower()
    return any(m.lower() in low for m in marker_list)


def slide_bg(slide):
    root = slide._element
    bg = root.find(f"{{{PPTX_NS}}}cSld/{{{PPTX_NS}}}bg")
    if bg is None:
        return ("inherit", None)
    bgpr = bg.find(f"{{{PPTX_NS}}}bgPr")
    if bgpr is None:
        return ("inherit", None)
    solid = bgpr.find(f"{{{DRAW_NS}}}solidFill/{{{DRAW_NS}}}srgbClr")
    blip = bgpr.find(f"{{{DRAW_NS}}}blipFill/{{{DRAW_NS}}}blip")
    if solid is not None:
        # 只读键名引用语义：实际色值不在此文件，由 brand_tokens 守卫；这里仅记录存在
        return ("solid", "brand_tokens")
    if blip is not None:
        return ("image", "media")
    grad = bgpr.find(f"{{{DRAW_NS}}}gradFill")
    if grad is not None:
        return ("grad", None)
    return ("other", None)


def union_coverage(pics, W, H, grid):
    """图片并集覆盖率（网格采样）。"""
    if not pics:
        return 0.0
    cov = 0
    total = grid * grid
    for gy in range(grid):
        for gx in range(grid):
            cx = ((gx + 0.5) / grid) * W
            cy = ((gy + 0.5) / grid) * H
            if any(l <= cx <= l + w and t <= cy <= t + h for (l, t, w, h) in pics):
                cov += 1
    return cov / total


def edge_gaps(pics, W, H):
    if not pics:
        return (None, None, None, None)
    return (min(l for l, t, w, h in pics),
            min(t for l, t, w, h in pics),
            min(W - (l + w) for l, t, w, h in pics),
            min(H - (t + h) for l, t, w, h in pics))


def measure_page(slide, W, H, spec):
    grid = int(T(spec, "sampling_grid"))
    pics = []
    sizes = set()
    n_text = 0
    n_shapes = 0
    max_bottom = 0.0
    for sh in slide.shapes:
        n_shapes += 1
        if sh.shape_type == MSO_SHAPE_TYPE.PICTURE:
            l, t, w, h = (round(inch(sh.left), 4), round(inch(sh.top), 4),
                          round(inch(sh.width), 4), round(inch(sh.height), 4))
            pics.append((l, t, w, h))
            if None not in (l, t, w, h):
                max_bottom = max(max_bottom, t + h)
        if sh.has_text_frame:
            n_text += 1
            for para in sh.text_frame.paragraphs:
                for run in para.runs:
                    if run.font.size is not None:
                        sizes.add(round(run.font.size.pt, 1))
    union = union_coverage(pics, W, H, grid)
    gaps = edge_gaps(pics, W, H)
    area_sum = sum(w * h for (_, _, w, h) in pics)
    layout = slide.slide_layout.name if slide.slide_layout else None
    title_m = markers(spec, "title")
    shell_m = markers(spec, "shell")
    blank_m = markers(spec, "blank")
    return {
        "page": None,  # 外层填
        "layout": layout,
        "is_title_layout": is_marker_layout(layout, title_m),
        "is_shell_layout": is_marker_layout(layout, shell_m),
        "is_blank_layout": is_marker_layout(layout, blank_m),
        "bg": slide_bg(slide),
        "n_shapes": n_shapes,
        "n_text_shapes": n_text,
        "n_pics": len(pics),
        "pic_area_frac": round(area_sum / (W * H), 3),
        "union_coverage": round(union, 3),
        "edge_gaps": [None if g is None else round(g, 3) for g in gaps],
        "max_font_pt": round(max(sizes), 1) if sizes else 0.0,
        "shape_bottom_in": round(max_bottom, 3),
    }


# --------------------------------------------------------------------------- #
# 渲染（仅深底候选）：LibreOffice→PDF→栅格→中位亮度
# --------------------------------------------------------------------------- #
def ensure_dir(p):
    if not p.is_dir():
        p.mkdir(parents=True)
    return p


def render_luminance(pptx, pages, spec):
    """渲染给定页，返回 {page: median_luminance(0-255)}。受 max_render_pages 上限约束。"""
    cap = int(T(spec, "max_render_pages"))
    dpi = int(T(spec, "render_dpi"))
    pages = pages[:cap]
    if not pages:
        return {}, 0
    import fitz
    from PIL import Image
    import numpy as np
    with tempfile.TemporaryDirectory() as td:
        tmp = pathlib.Path(td)
        profile = ensure_dir(tmp / "loprofile")
        cmd = [SOFFICE, f"-env:UserInstallation=file://{profile}", "--headless",
               "--convert-to", "pdf", "--outdir", str(tmp), str(pptx)]
        subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        pdf = tmp / (pathlib.Path(pptx).stem + ".pdf")
        if not pdf.exists():
            return {}, 0
        doc = fitz.open(pdf)
        out = {}
        for pno in pages:
            pix = doc.load_page(pno - 1).get_pixmap(dpi=dpi)
            img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples).convert("L")
            out[pno] = round(float(np.median(np.asarray(img))), 1)
        doc.close()
        return out, len(pages)


# --------------------------------------------------------------------------- #
# 判定（阈值全部来自 spec）
# --------------------------------------------------------------------------- #
def classify(ir, render_lum, spec):
    fullbleed_union = T(spec, "fullbleed_union")
    gap_tol = T(spec, "gap_tol")
    title_only_min = T(spec, "title_only_min_pt")
    skip_lo = T(spec, "skip_union_lo")
    skip_hi = T(spec, "skip_union_hi")
    skip_top = T(spec, "skip_top_gap")
    prom_lo = T(spec, "promote_area_lo")
    prom_hi = T(spec, "promote_area_hi")
    prom_font = T(spec, "promote_font_pt")
    dark_lum = T(spec, "dark_luminance_max")
    dark_band = T(spec, "dark_luminance_band")
    no_shift_union = T(spec, "no_shift_union")
    shell_single = int(T(spec, "shell_single_picture"))
    collage_min = int(T(spec, "collage_min_pictures"))
    contain_gap = T(spec, "containment_gap")

    gaps = ir["edge_gaps"]
    u = ir["union_coverage"]
    full_bleed = (u >= fullbleed_union
                  and gaps[0] is not None and abs(gaps[0]) <= gap_tol
                  and gaps[1] is not None and abs(gaps[1]) <= gap_tol
                  and gaps[2] is not None and abs(gaps[2]) <= gap_tol
                  and gaps[3] is not None and abs(gaps[3]) <= gap_tol)

    res = {}

    # ---- 壳页 remove ----
    rm = False
    rm_ev = ""
    if ir["is_shell_layout"] or (full_bleed
                                and (ir["n_pics"] == shell_single or ir["is_title_layout"])):
        rm = True
        rm_ev = f"满版单图/标题版式壳页 (union={u}, n_pics={ir['n_pics']})"
    elif ir["is_title_layout"] and ir["n_pics"] == 0 and ir["max_font_pt"] >= title_only_min:
        rm = True
        rm_ev = f"标题型裸页 (layout={ir['layout']}, max_font={ir['max_font_pt']})"
    res["remove_source_pages"] = {"value": rm, "confidence": "high" if rm else "high",
                                  "evidence": rm_ev or "非壳页（有正文/未命中壳页形态）"}

    # ---- 深底 dark（仅低置信渲染路径）----
    is_dark = False
    dark_conf = "high"
    dark_ev = "非满版候选，无需渲染"
    if not rm and u >= T(spec, "dark_fullbleed"):
        lum = render_lum.get(ir["page"])
        if lum is None:
            dark_conf = "low"
            dark_ev = "深底候选但渲染未能取得亮度（标记低置信，未猜默认）"
        else:
            is_dark = lum < dark_lum
            near = abs(lum - dark_lum) <= dark_band
            dark_conf = "medium" if near else "high"
            dark_ev = f"渲染中位亮度={lum} {'<' if is_dark else '>='} 阈值{dark_lum}（已栅格化取证）"
    res["dark_pages"] = {"value": is_dark, "confidence": dark_conf, "evidence": dark_ev}

    # ---- 满版截图页脚跳落 skip ----
    sk = (not rm and ir["n_pics"] == shell_single
          and skip_lo <= u < skip_hi
          and gaps[3] is not None and gaps[3] >= contain_gap
          and gaps[1] is not None and gaps[1] >= skip_top)
    sk_ev = (f"单图满版截图 (union={u}, top_gap={gaps[1]}, bottom_gap={gaps[3]})" if sk
             else "非单图满版截图")
    res["footer_skip_pages"] = {"value": sk, "confidence": "high" if sk else "high",
                                "evidence": sk_ev}

    # ---- 重复组标签标题提升 promote ----
    pr = (not rm and ir["is_blank_layout"]
          and prom_lo <= ir["pic_area_frac"] <= prom_hi
          and ir["max_font_pt"] >= prom_font)
    pr_ev = (f"空白版式重复组页 (area={ir['pic_area_frac']}, max_font={ir['max_font_pt']})" if pr
             else "非空白版式重复组页")
    res["promote_heading_pages"] = {"value": pr, "confidence": "high" if pr else "high",
                                    "evidence": pr_ev}

    # ---- 满版不位移 no_shift ----
    ns = (not rm and not sk and not is_dark
          and u >= no_shift_union and ir["n_pics"] >= collage_min and not ir["is_blank_layout"])
    ns_ev = (f"满版多图非空白页 (union={u}, n_pics={ir['n_pics']})" if ns
             else "非满版不位移页")
    res["no_shift_pages"] = {"value": ns, "confidence": "high" if ns else "high",
                             "evidence": ns_ev}

    # ---- 无章页 standalone = dark ∪ no_shift（三稿实测等价）----
    sa = is_dark or ns
    res["standalone_pages"] = {"value": sa, "confidence": "high",
                               "evidence": "derive(dark ∪ no_shift)"}

    return res


def _extract_title(slide):
    """提取本页的源稿标题文本与（若提升）提升后标题。

    返回 (title_text, promoted_title_or_None)。find_source_title 等来自保真度门禁，
    属确定性抽取（非判定）——Analyzer 用它把标题事实搬进 IR，判定由 Planner 消费。
    """
    shapes = list(slide.shapes)
    title_shape = find_source_title(shapes)
    title = (title_shape.text or "").strip() if title_shape is not None else ""
    promoted = None
    if title_shape is not None:
        promoted_shape = find_promoted_heading(
            shapes, {id(title_shape._element)})
        if promoted_shape is not None:
            promoted = (promoted_shape.text or "").strip() or None
    return title, promoted


# --------------------------------------------------------------------------- #
# 主流程
# --------------------------------------------------------------------------- #
def apply_decisions(declarations: dict, path: pathlib.Path) -> list:
    """回读人工裁决覆盖测定声明。schema 不符/未知形态类/非法条目一律显式报错。"""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise SystemExit(f"[FAIL] decisions 不可解析: {path} ({exc})")
    if data.get("schema") != SCHEMA_DECISIONS:
        raise SystemExit(f"[FAIL] decisions schema 不符（期望 {SCHEMA_DECISIONS}）: {path}")
    applied = []
    for item in data.get("decisions", []):
        cls, page, value = item.get("class"), item.get("page"), item.get("value")
        if cls not in declarations:
            raise SystemExit(f"[FAIL] decisions 含未知形态类 {cls!r}: {path}")
        if not isinstance(page, int):
            raise SystemExit(f"[FAIL] decisions 条目缺合法 page: {item} ({path})")
        if value:
            if page not in declarations[cls]:
                declarations[cls].append(page)
        else:
            declarations[cls] = [p for p in declarations[cls] if p != page]
        applied.append({"page": page, "class": cls, "value": bool(value)})
    return applied


def measure_deck(source: pathlib.Path, spec, deck_name=None, decisions=None):
    prs = Presentation(str(source))
    W = inch(prs.slide_width)
    H = inch(prs.slide_height)
    lang, _ratio, _letters = detect_source_language(prs)
    cover_title, cover_subtitle = source_cover_copy(prs)

    pages_ir = []
    for i, slide in enumerate(prs.slides, start=1):
        ir = measure_page(slide, W, H, spec)
        ir["page"] = i
        pages_ir.append(ir)

    # 深底候选：满版且非壳页 → 触发渲染（计数+上限）
    candidates = [p["page"] for p in pages_ir
                  if p["union_coverage"] >= T(spec, "dark_fullbleed")
                  and not (p["union_coverage"] >= T(spec, "fullbleed_union")
                           and (p["n_pics"] == int(T(spec, "shell_single_picture"))
                                or p["is_title_layout"]))]
    lum, render_calls = render_luminance(source, candidates, spec)

    pages_out = []
    declarations = {k: [] for k in
                   ("remove_source_pages", "promote_heading_pages", "footer_skip_pages",
                    "dark_pages", "standalone_pages", "no_shift_pages")}
    low_conf = []
    for idx, ir in enumerate(pages_ir):
        form = classify(ir, lum, spec)
        slide = prs.slides[idx]
        title, promoted = _extract_title(slide)
        for cls, info in form.items():
            if info["value"]:
                declarations[cls].append(ir["page"])
            if info["confidence"] != "high":
                low_conf.append({"page": ir["page"], "class": cls,
                                 "confidence": info["confidence"],
                                 "evidence": info["evidence"]})
        pages_out.append({"page": ir["page"], "ir": ir, "form": form,
                          "title": title, "promoted_title": promoted})

    dec_path = decisions or source.with_name(f"{source.stem}.decisions.json")
    overrides = apply_decisions(declarations, pathlib.Path(dec_path)) \
        if pathlib.Path(dec_path).exists() else []

    for k in declarations:
        declarations[k].sort()

    # 裁决同步到逐页 form：planner 读的是逐页值，不同步则裁决只在报告里生效、不进 Change List
    if overrides:
        for p in pages_out:
            for cls, info in (p.get("form") or {}).items():
                want = p["page"] in declarations.get(cls, [])
                if info.get("value") != want:
                    info["value"] = want
                    info["evidence"] = "人工裁决覆盖（decisions.json）"
                    info["confidence"] = "decided"

    report = {
        "schema": SCHEMA_REPORT,
        "deck": deck_name or source.stem,
        "source": str(source),
        "spec": "2026VI.yaml",
        "shell_language": lang,
        "cover_source": {"title": cover_title, "subtitle": cover_subtitle},
        "canvas_in": [round(W, 4), round(H, 4)],
        "thresholds_snapshot": spec["form_measurement"]["thresholds"],
        "render": {
            "calls": render_calls,
            "cap": int(T(spec, "max_render_pages")),
            "pages_rendered": candidates[:int(T(spec, "max_render_pages"))],
            "note": "仅深底候选页栅格化；非每页渲染" if render_calls else "无深底候选，零渲染",
        },
        "pages": pages_out,
        "declarations": declarations,
        "low_confidence_count": len(low_conf),
        "decisions_file": str(dec_path),
        "decisions_applied": overrides,
    }
    return report, low_conf


def build_decisions(report, low_conf, deck_name):
    return {
        "schema": SCHEMA_DECISIONS,
        "deck": deck_name or report["deck"],
        "generated_by": "core.analyzer",
        "spec": "2026VI.yaml",
        "note": "低置信/渲染取证判定记录；可删可重算。high 置信不在此列。",
        "decisions": low_conf,
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description="chint-pptx 测定层")
    ap.add_argument("source", help="源稿 pptx 路径")
    ap.add_argument("--out", help="报告输出目录（默认源稿同级 measurements/）")
    ap.add_argument("--spec", help="规格文件（默认 scripts/../spec/2026VI.yaml）")
    ap.add_argument("--deck", help="deck 名（用于报告/决策文件命名）")
    args = ap.parse_args(argv)

    source = pathlib.Path(args.source)
    if not source.exists():
        print(f"[FAIL] 找不到源稿: {source}")
        return 2
    spec = load_spec(pathlib.Path(args.spec) if args.spec else SPEC_DEFAULT)

    report, low_conf = measure_deck(source, spec, deck_name=args.deck)

    out_dir = pathlib.Path(args.out) if args.out else source.parent / "measurements"
    ensure_dir(out_dir)
    deck = args.deck or source.stem
    report_path = out_dir / f"{deck}_measurement.json"
    dec_path = out_dir / f"{deck}.decisions.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2, default=str) + "\n", encoding="utf-8")
    dec_path.write_text(json.dumps(build_decisions(report, low_conf, deck),
                                   ensure_ascii=False, indent=2, default=str) + "\n", encoding="utf-8")
    print(f"测定报告: {report_path}")
    print(f"判定记录: {dec_path}")
    print(f"渲染调用: {report['render']['calls']}/{report['render']['cap']}  "
          f"声明: " + ", ".join(f"{k}={v}" for k, v in report["declarations"].items()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
