#!/usr/bin/env python3
"""chint-pptx 渲染层（S3 的「执行」侧）—— 零判断、只按 Change List 执行

Change List ─[Renderer]→ pptx

设计原则（来自 2026-09-17 重构计划 S3）
  * 零判断（renderer 不得出现对 IR / 源稿内容的新分支判断）：凡是「该页是否深底 /
    是否不位移 / 是否跳页脚 / 是否无章页」这类**判定**，一律由 Change List 的显式
    指令字段（entry["dark"] / entry["no_shift"] / entry["skip_footer"] /
    entry["single_line"]）携带，Renderer 只照做。
  * 复用引擎现有 XML 变更函数（**搬移而非重写**，降低回归风险）；本文件里的函数与
    旧 shell_rebuild_engine.py 中的同名函数逐字节等价，只是从「边判定边改」改为
    「只执行 change_list 给定的指令」。
  * config 在 Renderer 里只用于**语义层与几何校准**（章节名/tagline、封面几何、
    title_grid 基准值、tight_pages 覆盖、footer 位置）。形态事实不再从 config 读。

入口：
    render(prs, change_list, config, theme, spec, scale_f=1.0) -> (report, footer_skipped) | None
"""
from __future__ import annotations

# 独立运行保障：本模块既被引擎入口调用，也应可被单独导入/单测/被其他 skill 复用。
# 兄弟包 core/ 与 scripts/ 的可导入性由本文件自解析，不依赖调用方预先注入 sys.path。
import os as _os
import sys as _sys

_SKILL_ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
for _p in (_SKILL_ROOT, _os.path.join(_SKILL_ROOT, "scripts")):
    if _p not in _sys.path:
        _sys.path.insert(0, _p)

from core.common import (
    LANG_ZH,
    LANG_EN,
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

import datetime
import os

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE, MSO_SHAPE_TYPE
from pptx.enum.text import PP_ALIGN
from pptx.util import Emu, Inches, Pt

# 保真度门禁提供确定性抽取（find_source_title 等位于此，非判定）——Renderer 仅用来
# 定位要移除/改写的形状载体，分支判断不在本层。
from verify_preserve_source import (          # noqa: E402
    is_bottom_furniture,
    is_footer_like,
    is_full_bleed_background,
    find_source_title,
    find_promoted_heading,
    table_row_heights,
)
# 共享纯工具（几何换算、语言/文案常量）来自 planner。
from core.planner import (                     # noqa: E402
    EMU, DESIGN_W, DESIGN_H, inn, emu, rgb,
)

# 运行期上下文：``_SCALE``（画布比例）与 ``_LANG``（外壳语言）。
# 画布比例已下沉为显式参数贯穿各函数（``scale=``），此处仅作为**未显式传入时的回退**，
# 由 render() 在每次运行开头设定一次；外壳语言是整稿级不变量（一次运行一种语言），
# 故仍以运行期上下文读取。二者都不在 config 里，也不跨运行泄漏。
_SCALE = (1.0, 1.0)
_LANG = LANG_ZH


def ref(v: float, axis: int = 1, scale=None) -> float:
    """A reference-canvas length (inches or points) expressed on this deck's canvas.

    缺省几何基准值一律按当次画布比例缩放，使非标准画布（旧 16:9 的 10"x5.625" 等）
    不必在 config 里手工标定：config 给了就用 config 的（画布绝对）值，
    没给就用缩放后的参考值——两者在同一坐标系下，永不混用。
    ``axis``: 0 = 水平（按宽比），1 = 垂直（按高比）；``scale`` 显式传入时优先
    （标量或 (sx, sy) 元组皆可）。
    """
    return v * _scale_tuple(scale)[axis]


def _scale_tuple(scale=None) -> tuple:
    """Normalise a run-time scale (scalar or (sx, sy)) to a two-tuple."""
    s = scale if scale is not None else _SCALE
    return (float(s), float(s)) if isinstance(s, (int, float)) else tuple(s)


# --------------------------------------------------------------------------- #
# text helpers
# --------------------------------------------------------------------------- #
def set_font(paragraph, text, *, font, size=None, bold=None, color=None, align=None,
             space_before=None):
    paragraph.text = text
    if align is not None:
        paragraph.alignment = align
    if space_before is not None:
        paragraph.space_before = Pt(space_before)
    if size:
        paragraph.font.size = Pt(size)
    if bold is not None:
        paragraph.font.bold = bold
    if color is not None:
        paragraph.font.color.rgb = color
    if font:
        paragraph.font.name = font
    for run in paragraph.runs:
        if font:
            run.font.name = font
        if size:
            run.font.size = Pt(size)
        if bold is not None:
            run.font.bold = bold
        if color is not None:
            run.font.color.rgb = color


def add_textbox(slide, left, top, width, height, text, *, font, size, bold, color,
                align=None):
    box = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    frame = box.text_frame
    frame.word_wrap = True
    frame.margin_left = frame.margin_top = frame.margin_right = frame.margin_bottom = 0
    # 多行标题必须落成**真段落**：paragraph.text 的 \n/\v 都只产生段内软换行 <a:br/>
    # （实测：写入 'A\nB' 读回 'A\x0bB'，段落数仍为 1），而源稿是段落换行——门禁 [F4]
    # 会据此判"主标题被改动"。故多行走 text_frame.text（实测产生 2 段、读回 'A\nB'）。
    flat = (text or "").replace("\v", "\n").replace("\x0b", "\n")
    if "\n" in flat:
        frame.text = flat
        for para in frame.paragraphs:
            set_font(para, para.text, font=font, size=size, bold=bold, color=color, align=align)
    else:
        set_font(frame.paragraphs[0], flat, font=font, size=size, bold=bold, color=color, align=align)
    return box


def add_clean_slide(prs, layout):
    """Add a slide and strip the layout placeholders cloned into it."""
    slide = prs.slides.add_slide(layout)
    for placeholder in list(slide.placeholders):
        element = placeholder._element
        element.getparent().remove(element)
    return slide


# --------------------------------------------------------------------------- #
# slide-level surgery
# --------------------------------------------------------------------------- #
def delete_slide(prs, index: int):
    """Delete the 1-based slide, dropping its relationship with it."""
    sld_id_lst = prs.slides._sldIdLst
    sld_id = list(sld_id_lst)[index - 1]
    r_id = sld_id.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id")
    prs.part.drop_rel(r_id)
    sld_id_lst.remove(sld_id)


def reorder_slides(prs, order):
    """Reorder slides so that the final sequence is ``order`` (0-based current indices)."""
    sld_id_lst = prs.slides._sldIdLst
    elements = list(sld_id_lst)
    for idx in order:
        sld_id_lst.append(elements[idx])


def shape_rect(shape):
    left, top = inn(shape.left), inn(shape.top)
    width, height = inn(shape.width), inn(shape.height)
    if None in (left, top, width, height) or width <= 0 or height <= 0:
        return None
    if getattr(shape, "has_table", False):
        width = inn(sum(c.width for c in shape.table.columns)) or width
        height = inn(sum(r.height for r in shape.table.rows)) or height
    return (left, top, left + width, top + height)


def intersects(a, b, pad=0.02) -> bool:
    return not (a[2] <= b[0] + pad or a[0] >= b[2] - pad
                or a[3] <= b[1] + pad or a[1] >= b[3] - pad)


# --------------------------------------------------------------------------- #
# shell pages
# --------------------------------------------------------------------------- #
def build_cover(prs, layout, cfg, theme, s=1.0):
    slide = add_clean_slide(prs, layout)
    assets = cfg.get("assets", {})
    if assets.get("cover_bg") and os.path.exists(assets["cover_bg"]):
        slide.shapes.add_picture(assets["cover_bg"], Inches(0), Inches(0),
                                 Inches(DESIGN_W * s), Inches(DESIGN_H * s))
    spec = cfg.get("cover", {})
    pack = SHELL_COPY[_LANG]
    # the cover art and the two bars are never touched; only the words in them change, and
    # a title too wide for its bar is reduced in type size rather than re-worded
    title_pt = fit_title_size(spec.get("title", ""), spec.get("title_pt", 28) * s, 9.0 * s)
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(3.93 * s), Inches(4.85 * s),
                                 Inches(9.4 * s), Inches(1.05 * s))
    bar.fill.solid(); bar.fill.fore_color.rgb = rgb(theme["blue"]); bar.line.fill.background()
    add_textbox(slide, 4.1 * s, 4.95 * s, 9.0 * s, 0.85 * s, spec.get("title", ""),
                font=theme["font"], size=title_pt, bold=True,
                color=rgb(theme["white"]))
    bar2 = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(3.93 * s), Inches(5.90 * s),
                                  Inches(9.4 * s), Inches(0.42 * s))
    bar2.fill.solid(); bar2.fill.fore_color.rgb = rgb(theme["cyan"]); bar2.line.fill.background()
    add_textbox(slide, 4.1 * s, 5.92 * s, 9.0 * s, 0.38 * s,
                spec.get("subtitle") or pack["department"],
                font=theme["font"], size=spec.get("subtitle_pt", 13) * s, bold=True,
                color=rgb(theme["white"]))
    # NOTE: no copyright line is drawn here on purpose — the official cover artwork
    # already carries it, and stacking a second one is the classic ghost-copyright defect.
    return slide


def build_toc(prs, layout, entries, cfg, theme, s=1.0):
    slide = add_clean_slide(prs, layout)
    assets = cfg.get("assets", {})
    if assets.get("toc_bg") and os.path.exists(assets["toc_bg"]):
        slide.shapes.add_picture(assets["toc_bg"], Inches(0), Inches(0),
                                 Inches(DESIGN_W * s), Inches(DESIGN_H * s))
    spec = cfg.get("toc", {})
    pill_left, pill_w, pill_h = 4.8 * s, 7.8 * s, 1.05 * s
    gap = spec.get("gap", 1.30) * s
    count = len(entries)
    # The configured gap is a preference, not a guarantee: with enough entries the block
    # (count * pill_h + (count-1) * gap) grows past the page and the first pill is placed
    # off the top edge. Clamp the gap so the block always fits a symmetric safe band.
    avail = DESIGN_H * s - 2 * 0.55 * s
    natural = count * pill_h + max(0, count - 1) * gap
    if count > 1 and natural > avail:
        gap = max(0.06 * s, (avail - count * pill_h) / (count - 1))
    block_h = count * pill_h + max(0, count - 1) * gap
    first_top = spec.get("center_y", 3.975) * s - block_h / 2.0
    step = pill_h + gap
    for i, (num, name) in enumerate(entries):
        top = first_top + i * step
        pill = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(pill_left), Inches(top),
                                      Inches(pill_w), Inches(pill_h))
        pill.fill.solid(); pill.fill.fore_color.rgb = rgb(theme["light_bg"])
        pill.line.color.rgb = rgb(theme["card_border"]); pill.line.width = Pt(1.5 * s)
        add_textbox(slide, pill_left + 0.2 * s, top + 0.18 * s, 0.9 * s, 0.7 * s, num,
                    font=theme["font"], size=28 * s, bold=True, color=rgb(theme["blue"]))
        divider = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(pill_left + 1.15 * s),
                                         Inches(top + 0.22 * s),
                                         Inches(0.02 * s), Inches(0.6 * s))
        divider.fill.solid(); divider.fill.fore_color.rgb = rgb(theme["card_border"])
        divider.line.fill.background()
        add_textbox(slide, pill_left + 1.35 * s, top + 0.22 * s, pill_w - 2.2 * s, 0.6 * s, name,
                    font=theme["font"], size=18 * s, bold=True, color=rgb(theme["navy"]))
        for offset in (7.2 * s, 7.35 * s):
            chevron = slide.shapes.add_shape(MSO_SHAPE.CHEVRON, Inches(pill_left + offset),
                                             Inches(top + 0.42 * s),
                                             Inches(0.12 * s), Inches(0.2 * s))
            chevron.fill.solid(); chevron.fill.fore_color.rgb = rgb(theme["cyan"])
            chevron.line.fill.background()
    return slide


def build_chapter(prs, layout, num, name, tagline, cfg, theme, s=1.0):
    slide = add_clean_slide(prs, layout)
    assets = cfg.get("assets", {})
    if assets.get("chapter_bg") and os.path.exists(assets["chapter_bg"]):
        slide.shapes.add_picture(assets["chapter_bg"], Inches(0), Inches(0),
                                 Inches(DESIGN_W * s), Inches(DESIGN_H * s))
    spec = cfg.get("chapter", {})
    box = slide.shapes.add_textbox(Inches(spec.get("x", 1.0) * s), Inches(spec.get("y", 2.7) * s),
                                   Inches(spec.get("w", 11.33) * s), Inches(spec.get("h", 1.8) * s))
    frame = box.text_frame
    frame.word_wrap = True
    frame.margin_left = frame.margin_top = frame.margin_right = frame.margin_bottom = 0
    # "CHAPTER" stays English in every deck, Chinese ones included: it is a decorative
    # divider label rather than copy, and it is written up as an explicit exception to the
    # "shell language follows the source" rule in the SOP so the two never read as
    # contradictory. The chapter's own name below it does follow the language.
    head = f"CHAPTER {num}  |  {tagline}" if tagline else f"CHAPTER {num}"
    set_font(frame.paragraphs[0], head, font=theme["font"], size=13 * s, bold=True,
             color=rgb(theme["ice"]), align=PP_ALIGN.CENTER)
    second = frame.add_paragraph()
    set_font(second, f"{num} {name}", font=theme["font"], size=32 * s, bold=True,
             color=rgb(theme["white"]), align=PP_ALIGN.CENTER, space_before=8 * s)
    return slide


def build_closing(prs, layout, cfg, theme, s=1.0):
    slide = add_clean_slide(prs, layout)
    assets = cfg.get("assets", {})
    if assets.get("closing_bg") and os.path.exists(assets["closing_bg"]):
        slide.shapes.add_picture(assets["closing_bg"], Inches(0), Inches(0),
                                 Inches(DESIGN_W * s), Inches(DESIGN_H * s))
    spec = cfg.get("closing", {})
    pack = SHELL_COPY[_LANG]
    # NO title and NO slogan are drawn here, on purpose. closing_26_bg.jpg already renders
    # the "THANKS" wordmark plus the copyright line inside the picture, so a text title or
    # slogan would print the same message twice on one screen. ``validate_config`` rejects
    # such copy outright; this function simply never draws it. (2026-09-16)
    # The contact line is the only copy this page carries. The department name lives exactly
    # once in the whole deck — as the cover subtitle — so nothing here may repeat it.
    contact = spec["contact"] if "contact" in spec else pack["closing_contact"]
    if contact:
        add_textbox(slide, 1.0 * s, spec.get("contact_y", 6.72) * s, 11.33 * s, 0.32 * s, contact,
                    font=theme["font"], size=9.5 * s, bold=False, color=rgb(theme["muted"]),
                    align=PP_ALIGN.CENTER)
    # closing artwork already carries the copyright line — do not stack another one
    return slide


# --------------------------------------------------------------------------- #
# sub-page chrome: title grid + footer
# --------------------------------------------------------------------------- #
def content_shapes(slide, bottom_limit, scale=None, skip_ids=frozenset()):
    """Body shapes of a page: no full-bleed art, no bottom furniture, no footer, no title.

    The title element must be passed in via ``skip_ids`` (captured *before* it is
    removed). Re-detecting it here would be a bug: with the real title already gone,
    the topmost remaining candidate is the page's *lead line*, which would then be
    excluded from the give-way shift and left overlapping the new title grid.
    """
    out = []
    for shape in slide.shapes:
        if id(shape._element) in skip_ids:
            continue
        if is_footer_like(shape, bottom_limit):
            continue
        if is_full_bleed_background(shape, _scale_tuple(scale)) or is_bottom_furniture(shape, bottom_limit):
            continue
        if shape_rect(shape) is None:
            continue
        # invisible layout residue (empty placeholder / empty text box) must never
        # trigger a give-way shift: it has no pixels, but pushing content down for it
        # is what pushes dense tables through the bottom safety line.
        if shape.has_text_frame and not (shape.text or "").strip():
            if shape.shape_type in (MSO_SHAPE_TYPE.PLACEHOLDER, MSO_SHAPE_TYPE.TEXT_BOX):
                continue
        out.append(shape)
    return out


def apply_title_grid(slide, title_text, category, geom, theme, report, page_label, scale=None):
    """Replace the source title with the 2026 VI two-line grid; shift content minimally.

    注意：本函数**不判定**任何形态事实。它只看 Change List 通过 ``geom`` /
    ``category`` / ``title_text`` 显式传入的指令（dark / no_shift 已由调用方从 change_list
    写入 geom），定位要替换的标题载体属确定性抽取（find_source_title），不构成新分支判断。
    """
    title_shape = find_source_title(list(slide.shapes))
    skip_ids = {id(title_shape._element)} if title_shape is not None else set()
    if title_shape is not None:
        title_shape._element.getparent().remove(title_shape._element)

    box_w = geom.get("box_width", ref(10.5, 0, scale))
    grid_x = 0.8 * _scale_tuple(scale)[0]        # VI grid line, scaled to this canvas
    box_h = 0.28 * _scale_tuple(scale)[1]
    ttl_h = 0.42 * _scale_tuple(scale)[1]
    # A chapterless page draws no category line, so its collision block starts at the
    # main title rather than at the (absent) category row.
    block_top = geom["cat_top"] if category else geom["ttl_top"]
    block = (grid_x, block_top, grid_x + box_w,
             geom["ttl_top"] + geom["title_pt"] * 1.2 / 72.0 + geom.get("block_bottom_margin", 0.02))

    targets = content_shapes(slide, geom.get("bottom_limit", ref(7.30, 1, scale)), scale, skip_ids)
    hits = [s for s in targets if shape_rect(s) and intersects(shape_rect(s), block)]
    shift = 0.0
    if hits and geom.get("no_shift"):
        # Page-scale background art (a watermark, a full-page panel) is the plate the
        # title grid is laid onto, not content that can step aside: shifting it would
        # push the page off canvas. Reported, never silent.
        report.append(f"{page_label}: 背景美术页（no_shift）—— "
                      f"标题网格按标准位置绘制，底图不让位")
    elif hits:
        cut = min(inn(s.top) for s in hits)
        shift = max(0.0, block[3] - cut)
        if shift > 0.0005:
            delta = emu(shift)
            for shape in targets:
                if inn(shape.top) >= cut - 1e-6:
                    shape.top = Emu(shape.top + delta)

    ttl_color = rgb(geom.get("dark_title_color", theme["navy"])) if geom.get("dark") \
        else rgb(theme["navy"])
    if category:
        add_textbox(slide, grid_x, geom["cat_top"], box_w, box_h, category,
                    font=theme["font"], size=geom["cat_pt"], bold=True,
                    color=rgb(theme["cyan"]))
    add_textbox(slide, grid_x, geom["ttl_top"], box_w, ttl_h, title_text, font=theme["font"],
                size=geom["title_pt"], bold=True, color=ttl_color)

    bottom = max((shape_rect(s)[3] for s in targets if shape_rect(s)), default=0.0)
    cat_note = "（无章节名行）" if not category else ""
    cat_pt = "—" if not category else "%d" % round(geom["cat_pt"])
    report.append(f"{page_label}: 标题网格 {cat_pt}/{geom['title_pt']:.0f}pt{cat_note}"
                  f"{'（深底白字）' if geom.get('dark') else ''}，让位 {shift:.3f}\"，内容底边 {bottom:.2f}\"")
    return shift


def normalize_and_add_footer(slide, footer_cfg, theme, report, page_label, page_number=0,
                             dark: bool = False, scale=None):
    """Three-piece footer with an adaptive baseline and a table-only conflict policy.

    Bottom-up layout: the decorative strip (if the source page has one) is the hard
    floor; the rule sits just above it and the copyright line sits above the rule.
    Conflict policy: tighten TABLE ROW heights only; if that is impossible the footer
    is skipped for this page and the reason is reported (never silently ignored).
    """
    bottom_limit = footer_cfg.get("bottom_limit", ref(7.30, 1, scale))
    strip_tops = [inn(s.top) for s in slide.shapes
                  if is_bottom_furniture(s, bottom_limit) and inn(s.top) is not None]
    floor = min(strip_tops) if strip_tops else footer_cfg.get("rule_y", ref(7.35, 1, scale)) + ref(0.15, 1, scale)

    rule_y = min(footer_cfg.get("rule_y", ref(7.35, 1, scale)), floor - ref(0.05, 1, scale))
    text_y = rule_y - ref(0.30, 1, scale)
    limit = text_y - ref(0.03, 1, scale)

    # remove source footer furniture (normalisation is allowed by the SOP)
    for shape in list(slide.shapes):
        if is_footer_like(shape, bottom_limit):
            shape._element.getparent().remove(shape._element)

    body = content_shapes(slide, bottom_limit, scale)
    colliding = [s for s in body if shape_rect(s) and shape_rect(s)[3] > limit]

    adjusted = []
    if colliding:
        for shape in colliding:
            if not getattr(shape, "has_table", False):
                report.append(f"{page_label}: 跳过页脚 —— 底部存在非表格内容 "
                              f"({(shape.name or '?')} 底边 {shape_rect(shape)[3]:.2f}\" > {limit:.2f}\")，"
                              f"按策略不改动该形状")
                return False
        # every colliding shape is a table: tighten row heights only
        for shape in colliding:
            table = shape.table
            top = inn(shape.top)
            allowed = limit - top
            current = inn(sum(r.height for r in table.rows)) or 0
            if allowed <= 0 or current <= 0:
                report.append(f"{page_label}: 跳过页脚 —— 表格 {(shape.name or '?')} 顶部已低于页脚基线")
                return False
            factor = allowed / current
            new_heights, blocked = [], None
            for row in table.rows:
                target = inn(row.height) * factor
                floor = natural_row_min_in(row)
                if target < floor - 0.002:
                    blocked = f"行高需 {target:.3f}\" 但文字自然高度下限为 {floor:.3f}\""
                    break
                new_heights.append(emu(target))
            if blocked:
                report.append(f"{page_label}: 跳过页脚 —— 表格 {(shape.name or '?')} 无法在不改内容的前提下腾出空间（{blocked}）；"
                              f"压缩行高会被渲染器自动涨回，属无效操作")
                return False
            if sum(new_heights) > emu(allowed) + 1000:
                report.append(f"{page_label}: 跳过页脚 —— 表格 {(shape.name or '?')} 行高压缩后仍放不下")
                return False
            for row, height in zip(table.rows, new_heights):
                row.height = height
            adjusted.append(f"{(shape.name or '?')} {current:.3f}\"→{inn(sum(new_heights)):.3f}\"")
        report.append(f"{page_label}: 为容纳页脚微调表格行高（仅行高）: {', '.join(adjusted)}")

    if footer_cfg.get("rule", True):
        rule = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE,
                                      Inches(footer_cfg.get("x", ref(0.8, 0, scale))),
                                      Inches(rule_y), Inches(footer_cfg.get("w", ref(11.73, 0, scale))),
                                      Inches(ref(0.02, 1, scale)))
        rule.fill.solid(); rule.fill.fore_color.rgb = rgb(footer_cfg.get("rule_color", theme["blue"]))
        rule.line.fill.background()
    # on a dark source page the standard muted grey would be low-contrast chrome
    text_color = footer_cfg.get("dark_color", theme["ice"]) if dark \
        else footer_cfg.get("color", theme["muted"])
    add_textbox(slide, footer_cfg.get("x", ref(0.8, 0, scale)), text_y,
                footer_cfg.get("w", ref(11.73, 0, scale)), ref(0.28, 1, scale),
                footer_cfg.get("text") or default_footer_text(), font=theme["font"],
                size=footer_cfg.get("pt", 8.5),
                bold=False, color=rgb(text_color), align=PP_ALIGN.RIGHT)
    if footer_cfg.get("page_number", True) and page_number:
        right = footer_cfg.get("x", ref(0.8, 0, scale)) + footer_cfg.get("w", ref(11.73, 0, scale))
        add_textbox(slide, right - ref(2.0, 0, scale), text_y, ref(2.0, 0, scale), ref(0.28, 1, scale),
                    f"{page_number} / {footer_cfg.get('total_pages', '')}".strip(" /"),
                    font=theme["font"], size=footer_cfg.get("pt", 8.5), bold=False,
                    color=rgb(text_color), align=PP_ALIGN.RIGHT)
    report.append(f"{page_label}: 页脚已加（版权行 y={text_y:.2f}\"，装饰线 y={rule_y:.2f}\"）")
    return True


def natural_row_min_in(row) -> float:
    """Smallest row height a renderer will actually honour.

    `<a:tr h>` is a *minimum*: PowerPoint/LibreOffice grow a row back to fit its text.
    Shrinking a row below the natural text height therefore buys nothing on screen —
    the footer would still collide once rendered. The engine treats that as "this page
    cannot host a footer" instead of pretending to have made room.
    """
    tallest = 0.0
    for cell in row.cells:
        for paragraph in cell.text_frame.paragraphs:
            size = paragraph.font.size.pt if paragraph.font.size is not None else 0.0
            for run in paragraph.runs:
                if run.font.size is not None:
                    size = max(size, run.font.size.pt)
            tallest = max(tallest, size)
    margins = 0.0
    for cell in row.cells:
        margins = max(margins,
                      (inn(cell.margin_top) or 0.0) + (inn(cell.margin_bottom) or 0.0))
    return tallest * 1.2 / 72.0 + margins + 0.01


# --------------------------------------------------------------------------- #
# geometry resolution（基准值 + tight_pages 校准来自 config；dark/no_shift 由调用方覆盖）
# --------------------------------------------------------------------------- #
def resolve_geometry(cfg, source_page: int, theme, scale=None):
    grid = dict(cfg.get("title_grid", {}))
    geom = {
        "cat_top": grid.get("cat_top", ref(0.42, 1, scale)),
        "ttl_top": grid.get("ttl_top", ref(0.62, 1, scale)),
        "cat_pt": grid.get("category_pt", ref(10.0, 1, scale)),
        "title_pt": grid.get("title_pt", ref(22.0, 1, scale)),
        "box_width": grid.get("box_width", ref(10.5, 0, scale)),
        "block_bottom_margin": grid.get("block_bottom_margin", ref(0.02, 1, scale)),
        "bottom_limit": cfg.get("footer", {}).get("bottom_limit", ref(7.30, 1, scale)),
        # 注：dark / no_shift 不再从 config 形态键读取（已下线）；调用方以 Change List
        # 显式指令覆盖。这里给保守默认 False，绝不作为判定来源。
        "dark": False,
        "no_shift": False,
        "dark_title_color": grid.get("dark_title_color", theme["white"]),
    }
    tight = dict(grid.get("tight_pages", {}) or {}).get(str(source_page))
    if tight:
        geom.update(tight)
    return geom


# --------------------------------------------------------------------------- #
# measured text width —— the copy gate
# --------------------------------------------------------------------------- #
def name_render_sites(s: float, grid: dict):
    """Every place a chapter name / intro label is rendered, as (label, pt, box width).

    ``title_grid`` values are already canvas-absolute (the config carries them scaled),
    while the contents pill and divider geometry is reference-sized and multiplied by
    ``s`` here — the same split the shell builders use.
    """
    cat_pt = float(grid.get("category_pt", 10.0))
    box = float(grid.get("box_width", 10.5))
    intro_box = float(grid.get("intro_box_width", box))
    return (
        ("目录胶囊", 18.0 * s, 5.6 * s),
        ("章节页大字", 32.0 * s, 11.33 * s),
        ("分类行", cat_pt, max(box, intro_box)),
    )


def check_name_width(text: str, sites):
    """(ok|None, detail) measured against the tightest site; None = no font metrics."""
    measured = []
    for label, pt, box in sites:
        width = text_width_in(text, pt)
        if width is None:
            return None, "字体度量不可用（fontTools 缺失）"
        measured.append((label, width, box))
    worst = min(measured, key=lambda item: item[2] - item[1])
    ok = all(box - width >= 0.02 for _label, width, box in measured)
    detail = "，".join(f"{label} {width:.2f}\"/{box:.2f}\"" for label, width, box in measured)
    return ok, f"最紧位 {worst[0]}；{detail}"


def fit_title_size(text: str, pt: float, box_w: float, floor: float = 0.65) -> float:
    """Shrink a cover title until it fits its bar, announcing any reduction it makes."""
    width = text_width_in(text, pt)
    if width is None or width <= box_w:
        return pt
    target = max(pt * floor, pt * box_w / width)
    print(f"[文案适配] 封面主标题实测 {width:.2f}\" 超出可用 {box_w:.2f}\"，"
          f"字号 {pt:.1f}→{target:.1f}pt（文字内容未改，仅缩号）")
    return target


def default_footer_text() -> str:
    """Copyright line only — the department is named once, on the cover."""
    return f"Copyright © CHINT GROUP {datetime.datetime.now().year}"


# --------------------------------------------------------------------------- #
# 标题提升载体移除（确定性抽取，非判定）
# --------------------------------------------------------------------------- #
def _remove_promoted_carriers(prs, promoted_pages):
    """移除被提升页的「标题槽 + 正文首行」两个载体（与旧引擎 step 1 等价）。

    纯粹按 Change List 的 promoted_pages 指令执行；定位用 find_source_title /
    find_promoted_heading（确定性抽取）。
    """
    for idx, slide in enumerate(prs.slides, start=1):
        if idx not in set(promoted_pages):
            continue
        shapes = list(slide.shapes)
        title_shape = find_source_title(shapes)
        if title_shape is None:
            continue
        promoted = find_promoted_heading(shapes, {id(title_shape._element)})
        title_shape._element.getparent().remove(title_shape._element)
        if promoted is not None:
            promoted._element.getparent().remove(promoted._element)


# --------------------------------------------------------------------------- #
# 入口：按 Change List 执行
# --------------------------------------------------------------------------- #
def render(prs, change_list, config, theme, spec, scale_f=1.0):
    """只按 Change List 改写 prs；返回 (report, footer_skipped) 或 None（失败）。

    零判断：所有形态决策（dark / no_shift / skip_footer / single_line）来自 change_list
    的显式指令字段；本函数不做任何新的 IR / 源稿内容分支。
    """
    global _SCALE, _LANG
    _SCALE = (scale_f, scale_f)
    _LANG = change_list.get("shell_language", LANG_ZH)

    report, footer_skipped = [], []

    # 1. 标题提升载体移除（确定性抽取，非判定）
    _remove_promoted_carriers(prs, change_list.get("promoted_pages", []))

    # 2. 空白版式查找（跨全部 master）
    layout = None
    wanted = config.get("blank_layout", "空白")
    for master in prs.slide_masters:
        for candidate in master.slide_layouts:
            if candidate.name == wanted:
                layout = candidate
                break
        if layout is not None:
            break
    if layout is None:
        print(f"[FAIL] 原稿中找不到版式「{wanted}」，无法创建外壳页。可用版式: "
              f"{[l.name for m in prs.slide_masters for l in m.slide_layouts]}")
        return None

    chapters = config.get("chapters", []) or []
    build_cover(prs, layout, config, theme, scale_f)
    build_toc(prs, layout, [(c["num"], c["name"]) for c in chapters], config, theme, scale_f)
    for chapter in chapters:
        build_chapter(prs, layout, chapter["num"], chapter["name"], chapter.get("tagline"),
                      config, theme, scale_f)
    build_closing(prs, layout, config, theme, scale_f)

    # 3. 移除被替换源稿页（来自 Change List，非 config 形态键）
    for page in sorted(change_list.get("removed_pages", []), reverse=True):
        delete_slide(prs, page)

    # 4. 重排为目标顺序
    order = change_list.get("order", [])
    plan = change_list.get("plan", [])
    if sorted(order) != list(range(len(prs.slides))) or len(plan) != len(order):
        print(f"[FAIL] 页序映射不完整：{len(order)} 个位置 / {len(plan)} 个计划 vs "
              f"{len(prs.slides)} 页")
        return None
    reorder_slides(prs, order)

    # 5. 子页外壳性元素（标题网格 / 页脚）—— 指令全部来自 change_list
    grid_cfg = config.get("title_grid", {}) or {}
    footer_cfg = config.get("footer", {}) or {}
    for pos, entry in enumerate(plan):
        kind = entry["kind"]
        if kind not in ("intro", "content", "standalone"):
            continue
        slide = prs.slides[pos]                      # position-addressed: no drift
        label = f"第{pos + 1}页(原 p{entry['source_page']:02d})"
        geom = resolve_geometry(config, entry["source_page"], theme, scale=scale_f)
        # 形态事实来自 Change List（覆盖 resolve_geometry 的保守默认）
        geom["dark"] = entry["dark"]
        geom["no_shift"] = entry["no_shift"]
        if grid_cfg.get("enabled", True):
            if kind == "intro":
                geom["box_width"] = grid_cfg.get("intro_box_width", geom["box_width"])
            apply_title_grid(slide, entry["title_text"], entry["category"], geom, theme,
                             report, label, scale=scale_f)
        if footer_cfg.get("enabled", True):
            if entry["skip_footer"]:
                report.append(f"{label}: 跳过页脚 —— 该页列在 footer.skip_pages"
                              f"（满版内容铺到画布底边，页脚会与内容重叠）")
                footer_skipped.append(pos + 1)
            elif not normalize_and_add_footer(slide, footer_cfg, theme, report, label,
                                              page_number=pos + 1,
                                              dark=entry["dark"], scale=scale_f):
                footer_skipped.append(pos + 1)

    return report, footer_skipped
