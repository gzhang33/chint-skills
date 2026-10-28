#!/usr/bin/env python3
"""chint-pptx 规划层（S3 的「计划」侧）—— Change List 纯函数生成器

Slide IR ─[Planner 纯函数]→ Change List（可 diff、可评审、可单测）

设计原则（来自 2026-09-17 重构计划 S3）
  * 纯函数：`build_change_list(ir, spec, config) -> change_list`，无副作用
    （不写任何文件、不读全局可变态），同输入两次调用逐字节一致。
  * 事实来源：六类形态事实（remove / promote / dark / skip / no_shift / standalone）
    一律来自 IR（Analyzer 产出）；config 只承载**语义层与校准**
    （chapters、standalone_pages 及其 reason、cover/closing 文案、
     title_grid 几何校准 tight_pages 等）。planner 不得读 config 的形态键。
  * 判定与执行分离：planner 只「决定做什么」，Renderer 只「照做」。Change List 的
    每条变更带 kind / target / evidence，落盘后人工可读、可 diff，复盘时能量出
    「判错了还是改错了」。

本模块同时承载少量「纯工具」常量（几何换算、语言/文案常量），供 engine 与 renderer
共享，避免重复定义（core/ 仅 analyzer/planner/renderer(+verifier) 四模块）。
"""
from __future__ import annotations

from core.common import (
    SHELL_COPY,
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
    EMU,
    DESIGN_W,
    DESIGN_H,
    LANG_ZH,
    LANG_EN,
    LANG_CJK_THRESHOLD,
    _CJK_RE,
    DEPT_NAME_MAX_LEN,
    COVER_TITLE_SUFFIXES,
    shell_font_path,
)

import re

from pptx.dml.color import RGBColor

# --------------------------------------------------------------------------- #
# 几何换算（共享纯工具）
# --------------------------------------------------------------------------- #


# --------------------------------------------------------------------------- #
# 语言与文案常量（共享纯工具）
# --------------------------------------------------------------------------- #
# Shell copy pack. House rule: an English source gets an English shell; a Chinese
# source gets a Chinese. The department name is the ONLY thing a deck may name in
# shell copy, exactly once — as the cover subtitle.
# Words that must never be appended to a source cover title.
# --------------------------------------------------------------------------- #
# Change List 生成（纯函数）
# --------------------------------------------------------------------------- #
# 六类形态事实键（来自 IR）。planner 只从 IR 读这些，不读 config 的同名形态键。
_FORM_CLASSES = (
    "remove_source_pages",
    "promote_heading_pages",
    "footer_skip_pages",
    "dark_pages",
    "no_shift_pages",
    "standalone_pages",
)


def _ir_pages_by_form(ir, cls):
    return sorted(p["page"] for p in ir["pages"] if p["form"][cls]["value"])


def _form_evidence(ir, page, cls):
    for p in ir["pages"]:
        if p["page"] == page:
            return p["form"][cls]["evidence"]
    return ""


def _resolve_cover(ir, config, lang):
    """解析封面主/副标题（纯函数，不读全局态）。返回 (title, subtitle, warnings)。"""
    pack = SHELL_COPY[lang]
    cover_cfg = config.get("cover", {}) or {}
    cover_src = ir.get("cover_source", {}) or {}
    src_title = (cover_src.get("title") or "").strip()
    src_subtitle = (cover_src.get("subtitle") or "").strip()

    warnings = []
    if src_subtitle and looks_like_department(src_subtitle):
        resolved_sub = src_subtitle
    else:
        resolved_sub = pack["department"]
        if src_subtitle:
            warnings.append(
                f"源稿封面副标「{src_subtitle}」不符合「只放部门名」的规范形态"
                f"（不得带产品线、年份或串联符），已按外壳语言改为「{resolved_sub}」")
        else:
            warnings.append(f"源稿封面无副标行，按外壳语言（{lang}）回退为「{resolved_sub}」")

    configured_sub = (cover_cfg.get("subtitle") or "").strip()
    if configured_sub and configured_sub != resolved_sub:
        warnings.append(
            f"已忽略封面副标配置值「{configured_sub}」—— 副标只能是源稿原词，"
            f"或本语言的部门名「{pack['department']}」")

    configured_title = (cover_cfg.get("title") or "").strip()
    if not configured_title and src_title:
        cover_title = src_title
    elif configured_title:
        cover_title = configured_title
    else:
        cover_title = ""

    if configured_title and src_title and configured_title != src_title:
        warnings.append(
            f"封面主标题未逐字复用源稿（配置「{configured_title}」"
            f"vs 源稿「{src_title}」）—— 规范要求逐字复用，除非源稿封面本身不可用")

    return cover_title, resolved_sub, warnings


def build_change_list(ir: dict, spec: dict, config: dict) -> dict:
    """纯函数：Slide IR × spec × config → Change List。

    * 无副作用（不写文件、不读全局可变态）。
    * 同输入两次调用输出逐字节一致（可由单测证明）。
    * 六类形态事实来自 ir；config 仅语义层与校准。

    返回 dict（Change List），含：
      schema / deck / source / spec / shell_language / canvas_in
      cover / titles / removed_pages / promoted_pages / standalone_pages
      order / plan（逐页 kind/target/evidence 执行指令）/ problems / warnings
    """
    problems = []
    lang = ir.get("shell_language", LANG_EN)
    source_page_count = len(ir["pages"])

    # ---- 六类形态事实：一律来自 IR（不读 config 形态键）----
    removed_pages = _ir_pages_by_form(ir, "remove_source_pages")
    promoted_pages = _ir_pages_by_form(ir, "promote_heading_pages")
    skip_pages = _ir_pages_by_form(ir, "footer_skip_pages")
    dark_pages = _ir_pages_by_form(ir, "dark_pages")
    no_shift_pages = _ir_pages_by_form(ir, "no_shift_pages")

    # 逐页标题文本：只有**判定的 promote 页**才取提升后文本（与原引擎语义一致：
    # promote 是页级声明/判定，不是全局优先级——某稿 promote=[] 时全部用真标题，
    # 否则多行正文会被误当主标题，门禁 [F4] + navy 计数即漂移）。
    promoted_set = {str(x) for x in promoted_pages}
    titles = {}
    for p in ir["pages"]:
        key = str(p["page"])
        raw = (p["promoted_title"] if (key in promoted_set and p.get("promoted_title"))
               else (p.get("title") or ""))
        # 软换行统一为硬换行：python-pptx 用 \x0b 表示段内 <a:br/>，源稿标题用 \n；
        # 不归一则门禁 [F4] 判"主标题被改动"（实测新稿 p9/p10）。
        # python-pptx 的 paragraph.text：\n → 段内软换行 <a:br/>，\v → 段落换行。
        # 源稿标题读出来是 \n（段落换行），故写入前统一转成 \v 才能复现源稿形态。
        titles[key] = raw.replace("\x0b", "\n").replace("\v", "\n")

    # ---- 语义层：standalone_pages 由 config 声明（计划分界：人工取舍，保留）----
    standalone = config.get("standalone_pages", {}) or {}
    standalone_pages = sorted(standalone.get("pages", []) or [])

    # ---- 封面文案解析 ----
    cover_title, cover_subtitle, cover_warnings = _resolve_cover(ir, config, lang)

    # 封面主标题追加 Introduction / 产品介绍 / 概述 类后缀 = 硬失败（规范禁止）。
    configured_title = (config.get("cover", {}) or {}).get("title") or ""
    src_title = (ir.get("cover_source", {}) or {}).get("title") or ""
    tail = appended_cover_suffix(configured_title, src_title)
    if tail and looks_like_introduction_suffix(tail):
        problems.append(
            f"封面主标题「{configured_title}」= 源稿标题「{src_title}」+ 后缀「{tail}」。"
            f"规范禁止在源稿标题上追加 Introduction / 产品介绍 / 概述 这类后缀词 —— "
            f"同系列各稿必须共用源稿原句式（本稿应为「{src_title}」）。"
            f"如确需改动，先确认源稿封面本身不可用。")

    # ---- 章节结构（语义层）----
    chapters = config.get("chapters", []) or []
    intro = config.get("intro", {}) or {}

    seen_pages = []
    for ch in chapters:
        seen_pages.extend(ch.get("pages", []) or [])
    if intro.get("enabled"):
        seen_pages.extend(intro.get("pages", []) or [])
    seen_pages.extend(standalone_pages)
    seen_pages_set = set(seen_pages)

    # ---- 形态事实一致性校验（原 config 形态键校验的等价物，作用于 IR 派生事实）----
    for page in promoted_pages:
        if page not in seen_pages_set:
            problems.append(
                f"title_grid.promote_heading_pages 含非内容页 p{page}"
                f"（未出现在 chapters / intro / standalone_pages 中）")
    if len(set(promoted_pages)) != len(promoted_pages):
        problems.append(f"title_grid.promote_heading_pages 有重复页: {promoted_pages}")
    for page in skip_pages:
        if page not in seen_pages_set:
            problems.append(
                f"footer.skip_pages 含非内容页 p{page}"
                f"（未出现在 chapters / intro / standalone_pages 中）")
    overlap = sorted(set(removed_pages) & seen_pages_set)
    if overlap:
        problems.append(f"以下页码同时被引用与移除: {overlap}")

    # ---- 构建目标顺序 + 逐页执行指令（position-addressed）----
    surviving = [p for p in range(1, source_page_count + 1)
                 if p not in set(removed_pages)]
    current_index = {page: idx for idx, page in enumerate(surviving)}
    new_start = len(surviving)
    slot = {"cover": new_start, "toc": new_start + 1}
    cursor = new_start + 2
    for ch in chapters:
        slot[f"div-{ch['num']}"] = cursor
        cursor += 1
    slot["closing"] = cursor

    dark_set = set(dark_pages)
    no_shift_set = set(no_shift_pages)
    skip_set = set(skip_pages)

    def content_entry(kind, source_page, category):
        return {
            "kind": kind,
            "target": source_page,
            "source_page": source_page,
            "category": category or "",
            "dark": source_page in dark_set,
            "no_shift": source_page in no_shift_set,
            "skip_footer": source_page in skip_set,
            "single_line": (kind == "standalone"),
            "title_text": titles.get(str(source_page), ""),
            "evidence": {
                "kind": kind,
                "target": source_page,
                "title_text": titles.get(str(source_page), ""),
                "dark": _form_evidence(ir, source_page, "dark_pages"),
                "no_shift": _form_evidence(ir, source_page, "no_shift_pages"),
                "footer_skip": _form_evidence(ir, source_page, "footer_skip_pages"),
                "standalone": "derive(dark ∪ no_shift)" if kind == "standalone" else "",
            },
        }

    def shell_entry(kind):
        return {
            "kind": kind,
            "target": kind,
            "source_page": None,
            "category": "",
            "dark": False, "no_shift": False, "skip_footer": False, "single_line": False,
            "title_text": "",
            "evidence": {"kind": kind, "target": kind,
                         "note": f"{kind} 外壳页（固定新增，仅承载壳层文案）"},
        }

    def append_content_page(page, kind, category):
        if type(page) is not int:
            return
        source_index = current_index.get(page)
        if source_index is None:
            return
        order.append(source_index)
        plan.append(content_entry(kind, page, category))

    order = [slot["cover"], slot["toc"]]
    plan = [shell_entry("cover"), shell_entry("toc")]
    if intro.get("enabled"):
        for page in intro.get("pages", []) or []:
            append_content_page(page, "intro", intro.get("label"))
    for page in standalone_pages:
        append_content_page(page, "standalone", None)
    for ch in chapters:
        order.append(slot[f"div-{ch['num']}"])
        plan.append({
            "kind": "divider", "target": f"div-{ch['num']}", "source_page": None,
            "category": "", "dark": False, "no_shift": False, "skip_footer": False,
            "single_line": False, "title_text": "",
            "chapter": {"num": ch["num"], "name": ch["name"],
                        "tagline": ch.get("tagline", "") or ""},
            "evidence": {"kind": "divider", "target": f"div-{ch['num']}",
                         "note": f"章节页 {ch['num']} {ch['name']}（固定新增）"},
        })
        for page in ch.get("pages", []) or []:
            append_content_page(page, "content", f"{ch['num']} {ch['name']}")
    order.append(slot["closing"])
    plan.append(shell_entry("closing"))

    # 目标页数 = surviving + 新增壳页（cover/toc/各章节 divider/closing）：
    # closing 槽位本身 = cursor，故总数为 cursor+1（原式漏 +1：20 页稿会误判 19）。
    total_target = slot["closing"] + 1
    if sorted(order) != list(range(total_target)):
        # order 必须恰好覆盖 0..(total_target-1) 每个位置一次
        problems.append(f"页序映射不完整：{len(order)} 个位置 vs 目标 "
                        f"{total_target} 页")

    change_list = {
        "schema": "chint-modeb-changelist/1",
        "deck": ir.get("deck"),
        "source": ir.get("source"),
        "spec": "2026VI.yaml",
        "shell_language": lang,
        "canvas_in": ir.get("canvas_in"),
        "cover": {
            "title": cover_title,
            "subtitle": cover_subtitle,
            "source_title": (ir.get("cover_source", {}) or {}).get("title", ""),
            "configured_title": (config.get("cover", {}) or {}).get("title", ""),
            "warnings": cover_warnings,
        },
        "titles": titles,
        "removed_pages": removed_pages,
        "promoted_pages": promoted_pages,
        "standalone_pages": standalone_pages,
        "order": order,
        "plan": plan,
        "problems": problems,
        "warnings": cover_warnings,
    }
    return change_list


def derive_baseline(change_list: dict) -> dict:
    """从 Change List 派生门禁 baseline 豁免清单（与原 config 派生等价）。

    门禁 verify_preserve_source.py 一行不改；其豁免权仍来自这份 baseline，
    但数值现由 Change List / IR 派生，不再是 config 人工形态声明。
    """
    plan = change_list["plan"]
    allow_single_line = [pos + 1 for pos, entry in enumerate(plan)
                         if entry.get("kind") == "standalone"]
    return {
        "allow_removed_pages": change_list["removed_pages"],
        "allow_changed_pages": [],
        "allow_single_line_grid_pages": allow_single_line,
        "allow_promoted_heading_pages": change_list["promoted_pages"],
    }
