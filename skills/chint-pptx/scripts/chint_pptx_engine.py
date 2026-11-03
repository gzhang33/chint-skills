#!/usr/bin/env python3
"""
CHINT PPTX Generation Engine (2026 VI Standard)

Content pages use one layout: `ARCH_TABLE`. Cover, contents, chapter dividers, and
closing are rendered from the 2026 master template; three native charts remain for
trend, composition, and multi-dimension comparison. Any other archetype is rejected
before a slide is created.

- Full 1:1 alignment with the 2026 master template (26年模板拓新体.pptx).
- Official 2026 VI Color Palette Tokens & Multi-series 8-stage Chart Palette.
"""

import os
import json
import math
import re
import sys
import tempfile
import zipfile
import hashlib
from copy import deepcopy
from pathlib import Path
from typing import Dict, Any, Optional

from lxml import etree
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE, PP_PLACEHOLDER
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION
from pptx.chart.data import CategoryChartData


# Official VI theme values have one source: spec/brand_tokens.json.
from _brand_tokens import TOKENS as _BRAND_TOKENS

_theme_hex = _BRAND_TOKENS
C_BLUE = RGBColor.from_string(_theme_hex["blue"])
C_CYAN = RGBColor.from_string(_theme_hex["cyan"])
C_RED_TEXT = RGBColor(215, 10, 50)        # CHINT Alert Red #D70A32 (Alert / Threat)
C_RED_BG = RGBColor(255, 235, 238)        # Soft Red Alert Background #FFEBEB
C_GREEN = RGBColor(20, 200, 50)           # Growth Green #14C832 (Opportunity / Growth)
C_GREEN_BG = RGBColor(232, 248, 238)      # Soft Green Background #E8F8EE
C_TEAL = RGBColor(20, 200, 180)           # Smart Teal #14C8B4
C_DEEP_BLUE = RGBColor.from_string(_theme_hex["navy"])
C_BLUE_BG = RGBColor(235, 243, 255)       # Soft Blue Container #EBF3FF
C_ICE_BLUE = RGBColor.from_string(_theme_hex["ice"])
C_ORANGE = RGBColor(245, 158, 11)         # Warning Orange #F59E0B
C_DARK = RGBColor(30, 32, 36)             # Primary Dark Text #1E2024
C_MUTED = RGBColor.from_string(_theme_hex["muted"])
C_LIGHT_BG = RGBColor.from_string(_theme_hex["light_bg"])
C_BORDER = RGBColor.from_string(_theme_hex["card_border"])
C_WHITE = RGBColor.from_string(_theme_hex["white"])
C_CARD_HEADER_BG = RGBColor(228, 238, 255)# Card Header Light Blue #E4EEFF

# Multi-series Data Chart 8-stage Palette
CHART_PALETTE = [
    C_BLUE,                    # 1. Primary #1E50E6
    C_CYAN,                    # 2. Contrast #50C8FF
    C_GREEN,                   # 3. Growth #14C832
    C_TEAL,                    # 4. Smart #14C8B4
    RGBColor(35, 120, 255),    # 5. Accent Blue #2378FF
    RGBColor(90, 220, 25),     # 6. Soft Green #5ADC19
    C_ORANGE,                  # 7. Warning #F59E0B
    C_RED_TEXT                 # 8. Alert #D70A32
]

FONT_FAMILY = _theme_hex["font"]
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), "assets")
MEDIA_DIR = os.path.join(ASSETS_DIR, "media")
SKILL_ROOT = os.path.dirname(SCRIPT_DIR)
TEMPLATES_DIR = os.path.join(SKILL_ROOT, "assets", "templates")
if SKILL_ROOT not in sys.path:
    sys.path.insert(0, SKILL_ROOT)
from core.output_paths import default_output_dir, ensure_output_path
from core.common import TABLE_MAX_ROWS, TOC_MAX_ENTRIES

_REQUIRED_FIELDS = {
    "ARCH_01": ("title",), "ARCH_02": ("items",), "ARCH_03": ("title",),
}

# --- Content-page contract (2026-11 revision) -------------------------------
# Only these archetypes produce slides. Anything else is rejected at payload
# validation before a slide is created.
ALLOWED_ARCHETYPES = (
    "ARCH_01_COVER",
    "ARCH_02_TOC",
    "ARCH_03_CHAPTER",
    "ARCH_11_CLOSING",
    "ARCH_TABLE",
    "ARCH_16_CHART_BAR_TREND",
    "ARCH_17_CHART_PIE_DONUT",
    "ARCH_16_RADAR",
)


# Frame pages reuse the template's own layout artwork; body layouts inherit the
# interior badge from the master instead of stamping a second picture.
FRAME_LAYOUTS = {
    "ARCH_01_COVER": "标题幻灯片",
    "ARCH_03_CHAPTER": "节标题",
    "ARCH_11_CLOSING": "末尾幻灯片",
    "ARCH_TABLE": "标题和内容",
    "ARCH_16_CHART_BAR_TREND": "标题和内容",
    "ARCH_17_CHART_PIE_DONUT": "标题和内容",
    "ARCH_16_RADAR": "标题和内容",
}


def _normalize_arch(arch: str) -> str:
    return (arch or "").strip().upper()


def _reject_retired(arch: str) -> None:
    raise ValueError(
        f"{arch} 不是受支持的版式。内容页现仅支持："
        + "、".join(ALLOWED_ARCHETYPES)
    )


def _validate_table_payload(arch: str, data: Dict[str, Any]) -> None:
    headers = data.get("headers")
    rows = data.get("rows")
    if not isinstance(headers, list) or not headers:
        raise ValueError(f"{arch} 需要非空 headers 数组")
    if not all(isinstance(h, str) and h.strip() for h in headers):
        raise ValueError(f"{arch}.headers 每项必须是非空字符串")
    if not isinstance(rows, list) or not rows:
        raise ValueError(f"{arch} 需要非空 rows 数组")
    if len(rows) > TABLE_MAX_ROWS:
        raise ValueError(
            f"{arch}.rows 有 {len(rows)} 行，超过单页上限 {TABLE_MAX_ROWS} 行；请拆成多页，不要压缩字号硬塞"
        )
    for index, row in enumerate(rows):
        if not isinstance(row, list):
            raise ValueError(f"{arch}.rows[{index}] 必须是数组")
        if len(row) != len(headers):
            raise ValueError(
                f"{arch}.rows[{index}] 有 {len(row)} 个单元格，与 {len(headers)} 个表头不一致"
            )

    merge_groups = data.get("merge_groups") or []
    if merge_groups:
        if "levels" not in data:
            raise ValueError(f"{arch} 提供 merge_groups 时必须同时提供 levels（多层表头）")
        if "header_tree" not in data:
            raise ValueError(f"{arch} 提供 merge_groups 时必须同时提供 header_tree，否则合并后的表头为空")
        levels = data["levels"]
        if not isinstance(levels, list) or len(levels) != 2:
            raise ValueError(f"{arch}.levels 必须是两层表头的高度列表，例如 [2, 1]")
        if len(headers) > 1 and isinstance(headers[0], list):
            raise ValueError(f"{arch}.headers 必须是扁平字符串数组；多层表头写在 levels/header_tree 中")
        for index, group in enumerate(merge_groups):
            if not isinstance(group, dict) or "row" not in group or "columns" not in group:
                raise ValueError(f"{arch}.merge_groups[{index}] 需要 row 与 columns")
            cols = group["columns"]
            if not isinstance(cols, list) or len(cols) < 2:
                raise ValueError(f"{arch}.merge_groups[{index}].columns 至少两列才能合并")
            if any(not isinstance(c, int) or c < 0 or c >= len(headers) for c in cols):
                raise ValueError(f"{arch}.merge_groups[{index}].columns 越界")
            if any(cols[i] + 1 != cols[i + 1] for i in range(len(cols) - 1)):
                raise ValueError(f"{arch}.merge_groups[{index}].columns 必须是连续列区间")

    aligns = data.get("align")
    if aligns is not None:
        if not isinstance(aligns, list) or len(aligns) not in (len(headers),):
            raise ValueError(f"{arch}.align 长度必须等于列数")
        if any(a not in ("center", "left", "right") for a in aligns):
            raise ValueError(f"{arch}.align 只能取 center / left / right")


def _validate_slide_payload(arch, data):
    if not isinstance(data, dict):
        raise ValueError(f"Slide payload for {arch} must be an object")

    arch = _normalize_arch(arch)
    if arch not in ALLOWED_ARCHETYPES:
        _reject_retired(arch)

    if arch == "ARCH_TABLE":
        _validate_table_payload(arch, data)

    if not arch.startswith(("ARCH_02", "ARCH_11")) and not (data.get("title") or data.get("headline")):
        raise ValueError(f"{arch} requires a source-backed title")

    required = next((fields for prefix, fields in _REQUIRED_FIELDS.items()
                     if arch.startswith(prefix)), ())
    if arch.startswith("ARCH_17"):
        required = ("slices", "center_metric", "center_label")

    chart_fields = ()
    if arch == "ARCH_16_CHART_BAR_TREND":
        chart_fields = ("categories", "series", "summary_bullets")
    elif arch == "ARCH_16_RADAR":
        chart_fields = ("categories", "series")

    missing = [key for key in (*required, *chart_fields) if key not in data or data[key] is None or data[key] == "" or data[key] == []]
    if missing:
        raise ValueError(f"{arch} is missing source-backed content: {', '.join(dict.fromkeys(missing))}")

    lists = set(required) | set(chart_fields)
    limits = {"slices": 6}

    for key in lists:
        value = data.get(key)
        if isinstance(value, list):
            if not value:
                raise ValueError(f"{arch}.{key} cannot be empty")
            max_count = limits.get(key)
            if max_count is not None and len(value) > max_count:
                raise ValueError(f"{arch}.{key} 超出单页可读上限，请拆分到多页")

    if arch.startswith("ARCH_02"):
        if not isinstance(data["items"], list):
            raise ValueError("ARCH_02.items must be a list of section titles")
        if len(data["items"]) > TOC_MAX_ENTRIES:
            raise ValueError("ARCH_02.items exceeds the one-page capacity; condense or group section names")
        for index, item in enumerate(data["items"]):
            title = item.get("title") if isinstance(item, dict) else item
            if not isinstance(title, str) or not title.strip():
                raise ValueError(f"ARCH_02.items[{index}] needs a title")
    if arch.startswith(("ARCH_16", "ARCH_17")):
        categories = data.get("categories")
        for series in data.get("series", []):
            if not isinstance(series, dict) or not series.get("values"):
                raise ValueError(f"{arch} data series needs source-backed values")
            if categories is not None and len(categories) != len(series["values"]):
                raise ValueError(f"{arch} categories and series do not match")

    if arch == "ARCH_16_RADAR":
        categories = data.get("categories")
        series_data = data.get("series")
        if not isinstance(categories, list) or not 3 <= len(categories) <= 6:
            raise ValueError("Radar charts require 3 to 6 source-backed categories")
        if any(not isinstance(label, str) or not label.strip() for label in categories):
            raise ValueError("Radar chart categories must be non-empty strings")
        if not isinstance(series_data, list) or not series_data:
            raise ValueError("Radar charts require at least one source-backed series")
        for index, series in enumerate(series_data):
            if not isinstance(series, dict) or not isinstance(series.get("name"), str) or not series["name"].strip():
                raise ValueError(f"Radar series {index} needs a source-backed name")
            values = series.get("values")
            if not isinstance(values, list) or len(values) != len(categories):
                raise ValueError(f"Radar series {index} needs one value for every category")
            if any(isinstance(value, bool) or not isinstance(value, (int, float))
                   or not math.isfinite(value) for value in values):
                raise ValueError(f"Radar series {index} values must be finite numbers")

    if arch == "ARCH_16_RADAR" and not data.get("full_width", False):
        if not (data.get("insights") or data.get("bullets")):
            raise ValueError(f"{arch} requires source-backed insights for its insight panel")

    if arch.startswith("ARCH_11"):
        extras = [key for key in ("tagline", "team", "call_to_action", "contact", "title")
                  if data.get(key)]
        if extras:
            raise ValueError(
                "ARCH_11_CLOSING 使用模板原生尾页图版，页面已自带 THANKS、标记与版权行，"
                f"不接受额外文字字段：{', '.join(extras)}"
            )


def calc_autofit_fontsize(text: str, base_size: float = 11.0, min_size: float = 9.5,
                          threshold_len: int = 40, step: float = 0.5) -> float:
    """Dynamically scale font size based on text character length to prevent card overflow."""
    if not text:
        return base_size
    length = len(text)
    if length <= threshold_len:
        return base_size
    excess = length - threshold_len
    reduction = (excess // 15 + 1) * step
    return max(min_size, base_size - reduction)


def set_para(p, text: str, font_name: str = FONT_FAMILY, font_size: Optional[float] = None,
             bold: Optional[bool] = None, color_rgb: Optional[RGBColor] = None,
             align: Optional[PP_ALIGN] = None):
    p.text = text
    if font_name: p.font.name = font_name
    if font_size: p.font.size = Pt(font_size)
    if bold is not None: p.font.bold = bold
    if color_rgb: p.font.color.rgb = color_rgb
    if align: p.alignment = align
    for r in p.runs:
        if font_name: r.font.name = font_name
        if font_size: r.font.size = Pt(font_size)
        if bold is not None: r.font.bold = bold
        if color_rgb: r.font.color.rgb = color_rgb


def resolve_template_path(custom_dir: Optional[str] = None) -> Optional[str]:
    """Dynamically resolve the 2026 Master Template path across environments without hardcoded paths."""
    candidates = [
        os.path.join(custom_dir, "26年模板拓新体.pptx") if custom_dir else None,
        os.getenv("CHINT_PPTX_TEMPLATE"),
        os.path.join(TEMPLATES_DIR, "26年模板拓新体.pptx"),
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(SCRIPT_DIR)))), "resources", "品牌资产", "26年模板拓新体(1).pptx"),
        os.path.join(os.getcwd(), "resources", "品牌资产", "26年模板拓新体(1).pptx"),
    ]
    for p in candidates:
        if p and os.path.exists(p):
            return p
    return None


class ChintPresentationEngine:
    def __init__(self, media_dir: Optional[str] = None, templates_dir: Optional[str] = None):
        self.media_dir = media_dir or MEDIA_DIR
        self.templates_dir = templates_dir or TEMPLATES_DIR
        self._toc_layout = None
        self._toc_template_shapes = []
        self._toc_template_geometry = []
        
        tmpl_file = resolve_template_path(self.templates_dir)
        if tmpl_file and os.path.exists(tmpl_file):
            self.prs = Presentation(tmpl_file)
            if len(self.prs.slides) < 2:
                raise ValueError("The CHINT template is missing its contents page")
            template_toc = self.prs.slides[1]
            self._toc_layout = template_toc.slide_layout
            self._toc_template_shapes = [deepcopy(shape._element) for shape in template_toc.shapes]
            self._toc_template_geometry = [(shape.left, shape.top, shape.width, shape.height)
                                           for shape in template_toc.shapes]
            for i in range(len(self.prs.slides) - 1, -1, -1):
                r_id = self.prs.slides._sldIdLst[i].rId
                self.prs.part.drop_rel(r_id)
                del self.prs.slides._sldIdLst[i]
        else:
            raise FileNotFoundError(f"Required CHINT template was not found: {os.path.join(self.templates_dir, '26年模板拓新体.pptx')}")

        self.prs.slide_width = Inches(13.333)
        self.prs.slide_height = Inches(7.5)
        self.blank_layout = self.prs.slide_layouts[0] if len(self.prs.slide_layouts) > 0 else self.prs.slide_layouts[0]
        # Template frame layouts carry the real artwork (pictures, gradient bands,
        # marks, copyright). Slides are built on them instead of pasting a flat image.
        self.frame_layouts = {layout.name: layout for layout in self.prs.slide_layouts}
        # Detect if master slide already contains the official CHINT logo/badge
        self.has_master_logo = any(
            s.shape_type == 13 and s.left > Inches(10)
            for master in self.prs.slide_masters
            for s in master.shapes
        )

    def _frame_layout(self, name: str):
        layout = self.frame_layouts.get(name)
        if layout is None:
            raise ValueError(f"The CHINT template is missing its '{name}' layout")
        return layout

    def _add_frame_slide(self, layout_name: str, keep_text: bool = False):
        """Start a slide on a template frame layout.

        The layout's pictures, gradient bands and marks stay inherited, so the
        frame is real artwork rather than a pasted bitmap. Text placeholders are
        dropped unless the caller fills them.
        """
        slide = self.prs.slides.add_slide(self._frame_layout(layout_name))
        if not keep_text:
            for shape in list(slide.shapes):
                if shape.is_placeholder:
                    shape._element.getparent().remove(shape._element)
        return slide

    def _frame_placeholder(self, slide, ph_type):
        for shape in slide.placeholders:
            if shape.placeholder_format.type == ph_type:
                return shape
        raise ValueError(f"The CHINT template layout has no {ph_type} placeholder")


    def _find_media(self, base_name: str) -> Optional[str]:
        for extension in (".jpg", ".jpeg", ".png"):
            path = os.path.join(self.media_dir, base_name + extension)
            if os.path.isfile(path):
                return path
        return None

    @staticmethod
    def _set_existing_text(shape, value: str) -> None:
        paragraph = shape.text_frame.paragraphs[0]
        runs = paragraph.runs
        if runs:
            runs[0].text = value
            for run in runs[1:]:
                run.text = ""
        else:
            paragraph.add_run().text = value

    def _add_template_toc_page(self, items):
        """Fill the original contents artwork on one page; adapt rows and text to fit."""
        if self._toc_layout is None or len(self._toc_template_shapes) != 35:
            raise ValueError("The CHINT contents slide does not match the expected 35-shape template layout")
        if not 1 <= len(items) <= TOC_MAX_ENTRIES:
            raise ValueError("The CHINT contents page supports too many entries to fit one readable page. Condense or group the section names to keep one page.")

        shapes_per_row = 7
        source_row_tops = [self._toc_template_shapes[index * shapes_per_row].xpath("./p:spPr/a:xfrm/a:off")[0]
                           for index in range(5)]
        source_card = self._toc_template_shapes[0].xpath("./p:spPr/a:xfrm/a:ext")[0]
        source_left = int(source_row_tops[0].get("x"))
        source_top = int(source_row_tops[0].get("y"))
        source_card_height = int(source_card.get("cy"))
        content_bottom = int(source_row_tops[4].get("y")) + int(self._toc_template_shapes[28].xpath("./p:spPr/a:xfrm/a:ext")[0].get("cy"))
        content_height = content_bottom - source_top

        row_step = int(content_height / len(items)) if len(items) > 5 else 0
        row_height = min(source_card_height, int(row_step * 0.9)) if len(items) > 5 else source_card_height
        scale_y = row_height / source_card_height

        slide = self.prs.slides.add_slide(self._toc_layout)
        for placeholder in list(slide.placeholders):
            placeholder._element.getparent().remove(placeholder._element)

        from core.common import shell_font_path, text_width_in
        font_path = shell_font_path()
        for index, source_item in enumerate(items):
            target_left = source_left
            source_slot = index % 5
            source_row_top = int(source_row_tops[source_slot].get("y"))
            target_top = (source_top + index * row_step + int((row_step - row_height) / 2)
                          if len(items) > 5 else source_row_top)
            label = source_item.get("title", "") if isinstance(source_item, dict) else str(source_item)

            for shape_slot in range(shapes_per_row):
                source_element = self._toc_template_shapes[source_slot * shapes_per_row + shape_slot]
                element = deepcopy(source_element)
                for metadata in list(element.iter()):
                    if metadata.tag == "{http://schemas.openxmlformats.org/presentationml/2006/main}tags":
                        metadata.getparent().remove(metadata)
                slide.shapes._spTree.append(element)
                shape = slide.shapes[-1]
                source_geometry = self._toc_template_geometry[source_slot * shapes_per_row + shape_slot]
                shape.left = target_left + source_geometry[0] - source_left
                shape.top = target_top + int((source_geometry[1] - source_row_top) * scale_y)
                shape.width = source_geometry[2]
                shape.height = int(source_geometry[3] * scale_y)

            row_start = index * shapes_per_row
            self._set_existing_text(slide.shapes[row_start + 2], f"{index + 1:02d}")
            title_shape = slide.shapes[row_start + 4]
            self._set_existing_text(title_shape, label)
            title_shape.text_frame.word_wrap = False
            title_paragraph = title_shape.text_frame.paragraphs[0]
            source_size = title_paragraph.runs[0].font.size.pt if title_paragraph.runs and title_paragraph.runs[0].font.size else 18.0
            text_box_width = max(0.1, title_shape.width / 914400 - 0.08)
            text_box_height = max(0.1, title_shape.height / 914400 - 0.04)
            font_size = min(source_size * scale_y, text_box_height * 72 * 0.78)
            if font_size < 7.5:
                raise ValueError("TOC entries cannot fit legibly on one page. Reduce the number of sections.")
            measured = text_width_in(label, font_size, font_path)
            while measured is not None and measured > text_box_width and font_size > 7.5:
                font_size -= 0.5
                measured = text_width_in(label, font_size, font_path)
            if measured is not None and measured > text_box_width:
                raise ValueError(f"TOC entry '{label}' is too long to fit legibly on one page. Shorten its title.")
            for run in title_paragraph.runs:
                run.font.size = Pt(max(7.5, font_size))
        return slide

    def _add_body_master(self, slide, title: str, category: Optional[str] = None):
        if not getattr(self, "has_master_logo", False):
            badge_path = os.path.join(self.media_dir, "chint_badge.png")
            if os.path.exists(badge_path):
                slide.shapes.add_picture(badge_path, Inches(11.4), Inches(0.0), Inches(1.53), Inches(1.15))
            
        tb = slide.shapes.add_textbox(Inches(0.8), Inches(0.45), Inches(10.5), Inches(0.8))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        if category:
            set_para(p, f"[{category}]  {title}", font_size=20, bold=True, color_rgb=C_BLUE)
        else:
            set_para(p, title, font_size=22, bold=True, color_rgb=C_BLUE)
            
        tb_foot = slide.shapes.add_textbox(Inches(9.5), Inches(7.0), Inches(3.2), Inches(0.4))
        p_f = tb_foot.text_frame.paragraphs[0]
        set_para(p_f, "Copyright © CHINT GROUP 2025-2026", font_size=9, bold=False, color_rgb=RGBColor(160, 160, 160), align=PP_ALIGN.RIGHT)

    @staticmethod
    def _set_tf_margins(tf, top: float = 8, bottom: float = 8, left: float = 8, right: float = 8):
        tf.margin_top = Pt(top)
        tf.margin_bottom = Pt(bottom)
        tf.margin_left = Pt(left)
        tf.margin_right = Pt(right)

    # =========================================================================
    # 12 CORE COMPOSITION ENGINES (_render_*)
    # =========================================================================

    def _render_master_frame(self, slide, s_data: Dict[str, Any], arch: str):
        """Engine 1: Master Frames (Cover, TOC, Chapter, Closing, Contact).

        Every frame is built from its template layout, so the artwork (KV photo,
        gradient bands, accent line, marks, copyright) is native and editable.
        """
        if arch.startswith("ARCH_01"):
            title_shape = self._frame_placeholder(slide, PP_PLACEHOLDER.CENTER_TITLE)
            set_para(title_shape.text_frame.paragraphs[0],
                     s_data.get("title", "演示文稿标题"), font_size=28, bold=True,
                     color_rgb=C_WHITE)

            sub_shape = self._frame_placeholder(slide, PP_PLACEHOLDER.BODY)
            cover_details = []
            for key in ("subtitle", "date", "author"):
                value = s_data.get(key, "")
                if value:
                    if not isinstance(value, str):
                        raise ValueError(f"ARCH_01_COVER.{key} must be text")
                    cover_details.append(value.strip())
            cover_line = " · ".join(value for value in cover_details if value)
            if cover_line:
                from core.common import shell_font_path, text_width_in
                font_size = 16
                measured = text_width_in(cover_line, font_size, shell_font_path())
                while measured is not None and measured > 6.4 and font_size > 9:
                    font_size -= 0.5
                    measured = text_width_in(cover_line, font_size, shell_font_path())
                if measured is not None and measured > 6.4:
                    raise ValueError("Cover subtitle, date, and author do not fit the template; shorten the supplied text")
                set_para(sub_shape.text_frame.paragraphs[0], cover_line,
                         font_size=font_size, bold=False, color_rgb=C_WHITE)

        elif arch.startswith("ARCH_02"):
            raise RuntimeError("ARCH_02 must use the template-aware single-page contents renderer")

        elif arch == "ARCH_03_CHAPTER":
            # The layout's banner, gradient band and accent line are the artwork;
            # the template suppresses the master badge on this layout already.
            page = s_data.get("subtitle") or s_data.get("category") or ""
            if page:
                label = slide.shapes.add_textbox(Inches(1.0), Inches(2.30), Inches(11.33), Inches(0.55))
                set_para(label.text_frame.paragraphs[0], page.upper(), font_size=13, bold=True,
                         color_rgb=C_ICE_BLUE, align=PP_ALIGN.CENTER)
            title_shape = self._frame_placeholder(slide, PP_PLACEHOLDER.TITLE)
            set_para(title_shape.text_frame.paragraphs[0],
                     s_data.get("title") or s_data.get("headline") or "添加章节标题",
                     font_size=32, bold=True, color_rgb=C_WHITE, align=PP_ALIGN.CENTER)

        elif arch.startswith("ARCH_11"):
            # The closing layout already carries the KV, THANKS, the group mark and
            # the copyright line. Nothing is drawn on top of that artwork.
            pass

    def _render_table(self, slide, s_data: Dict[str, Any], arch: str):
        """ARCH_TABLE: the single generic content layout (multi-level header, zebra rows)."""
        self._add_body_master(slide, s_data.get("title", ""), s_data.get("category"))

        headers = s_data["headers"]
        rows = s_data["rows"]
        levels = s_data.get("levels") or [1]   # one entry per header row
        merge_groups = s_data.get("merge_groups") or []
        aligns = s_data.get("align") or ["center"] * len(headers)
        note = s_data.get("note")

        n_cols = len(headers)
        n_header_rows = len(levels)
        n_body = len(rows)
        left_m = Inches(0.8)
        top_m = Inches(1.55)
        width = Inches(11.73)
        bottom_limit = Inches(6.75 if note else 7.05)
        note_reserve = Inches(0.3) if note else Inches(0)
        avail_h = bottom_limit - top_m - note_reserve

        font_body = 11.0
        font_header = 12.0
        min_body = 8.5
        while True:
            row_h = Inches(0.34) + Inches(0.05) * min(font_body - min_body, 6)
            header_h = row_h * 1.15
            total = header_h * n_header_rows + row_h * n_body
            if total <= avail_h or font_body <= min_body:
                break
            font_body -= 0.5
            font_header = min(13.0, font_body + 1.0)

        row_h = min(row_h, int(avail_h / max(1, n_header_rows + n_body)))
        header_h = int(row_h * 1.15)
        total_h = min(int(avail_h), header_h * n_header_rows + row_h * n_body)

        table_shape = slide.shapes.add_table(
            n_header_rows + n_body, n_cols, left_m, top_m, width, Emu(total_h))
        table = table_shape.table

        # Merge the header groups before any cell text is written.
        for group in merge_groups:
            group_row = group["row"]
            cols = group["columns"]
            table.cell(group_row, cols[0]).merge(table.cell(group_row, cols[-1]))

        for r in range(n_header_rows):
            table.rows[r].height = Emu(header_h)
        for r in range(n_body):
            table.rows[n_header_rows + r].height = Emu(row_h)

        header_labels = s_data.get("header_tree")
        if header_labels:
            for r, level in enumerate(header_labels):
                for c in range(n_cols):
                    cell = table.cell(r, c)
                    cell.fill.solid()
                    cell.fill.fore_color.rgb = C_BLUE
                    label = level[c] if c < len(level) else None
                    self._set_tf_margins(cell.text_frame, top=6, bottom=6, left=8, right=8)
                    set_para(cell.text_frame.paragraphs[0], "" if label is None else str(label),
                             font_size=font_header, bold=True, color_rgb=C_WHITE, align=PP_ALIGN.CENTER)
        else:
            for c, label in enumerate(headers):
                cell = table.cell(0, c)
                cell.fill.solid()
                cell.fill.fore_color.rgb = C_BLUE
                self._set_tf_margins(cell.text_frame, top=6, bottom=6, left=8, right=8)
                set_para(cell.text_frame.paragraphs[0], label, font_size=font_header,
                         bold=True, color_rgb=C_WHITE, align=PP_ALIGN.CENTER)
            for r in range(1, n_header_rows):
                for c in range(n_cols):
                    cell = table.cell(r, c)
                    cell.fill.solid()
                    cell.fill.fore_color.rgb = C_BLUE
                    self._set_tf_margins(cell.text_frame, top=6, bottom=6, left=8, right=8)
                    set_para(cell.text_frame.paragraphs[0], "", font_size=font_header,
                             bold=True, color_rgb=C_WHITE, align=PP_ALIGN.CENTER)

        align_map = {"center": PP_ALIGN.CENTER, "left": PP_ALIGN.LEFT, "right": PP_ALIGN.RIGHT}
        for r_idx, row in enumerate(rows):
            for c_idx, value in enumerate(row):
                cell = table.cell(n_header_rows + r_idx, c_idx)
                cell.fill.solid()
                cell.fill.fore_color.rgb = C_LIGHT_BG if r_idx % 2 == 1 else C_WHITE
                self._set_tf_margins(cell.text_frame, top=6, bottom=6, left=8, right=8)
                text = "" if value is None else str(value)
                set_para(cell.text_frame.paragraphs[0], text, font_size=font_body, bold=False,
                         color_rgb=C_DARK, align=align_map[aligns[c_idx]])

        for c in range(n_cols):
            table.columns[c].width = Emu(int(width / n_cols))

        if note:
            tb_note = slide.shapes.add_textbox(left_m, bottom_limit - Inches(0.05), width, Inches(0.3))
            self._set_tf_margins(tb_note.text_frame, top=0, bottom=0, left=4, right=4)
            set_para(tb_note.text_frame.paragraphs[0], note, font_size=9, bold=False,
                     color_rgb=C_MUTED, align=PP_ALIGN.LEFT)

    def _render_chart_bar_trend(self, slide, s_data: Dict[str, Any], arch: str):
        """Native Bar & Trend Chart Engine (ARCH_16)"""
        self._add_body_master(slide, s_data.get("title", "核心指标趋势与对比分析"), s_data.get("category", "数据量化"))
        top_m, box_h = Inches(1.6), Inches(5.0)
        
        left_w = Inches(4.2)
        left_bg = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), top_m, left_w, box_h)
        left_bg.fill.solid()
        left_bg.fill.fore_color.rgb = C_LIGHT_BG
        left_bg.line.color.rgb = C_BORDER
        left_bg.line.width = Pt(1)
        
        tb_l = slide.shapes.add_textbox(Inches(1.0), top_m + Inches(0.25), left_w - Inches(0.4), box_h - Inches(0.5))
        tf_l = tb_l.text_frame
        tf_l.word_wrap = True
        self._set_tf_margins(tf_l, top=8, bottom=8, left=8, right=8)
        set_para(tf_l.paragraphs[0], s_data.get("summary_title", "数据洞察与业务启示"), font_size=14, bold=True, color_rgb=C_BLUE)
        
        summary_bullets = s_data["summary_bullets"]
        for j, b in enumerate(summary_bullets):
            p = tf_l.add_paragraph()
            set_para(p, f"• {b}", font_size=11.5, bold=False, color_rgb=C_DARK)
            p.space_before = Pt(10)
            p.space_after = Pt(2)
        
        right_w, right_left = Inches(7.2), Inches(5.33)
        cats = s_data.get("categories", ["2023", "2024", "2025", "2026E"])
        series_data = s_data.get("series", [
            {"name": "主营业务收入 (亿元)", "values": [120, 150, 185, 220]},
            {"name": "战略新品产值 (亿元)", "values": [45, 68, 95, 130]}
        ])
        
        try:
            cdata = CategoryChartData()
            cdata.categories = cats
            for s in series_data:
                cdata.add_series(s.get("name", "系列"), tuple(s.get("values", [])))
            
            chart_shape = slide.shapes.add_chart(
                XL_CHART_TYPE.COLUMN_CLUSTERED,
                right_left, top_m, right_w, box_h, cdata
            )
            chart = chart_shape.chart
            chart.has_legend = True
            chart.legend.position = XL_LEGEND_POSITION.TOP
            chart.legend.include_in_layout = False
            
            # Enable value data labels on columns
            if chart.plots and len(chart.plots) > 0:
                plot = chart.plots[0]
                plot.has_data_labels = True
                data_labels = plot.data_labels
                data_labels.font.name = FONT_FAMILY
                data_labels.font.size = Pt(9.5)
                data_labels.font.color.rgb = C_DARK

            for s_idx, series in enumerate(chart.series):
                color = CHART_PALETTE[s_idx % len(CHART_PALETTE)]
                fill = series.format.fill
                fill.solid()
                fill.fore_color.rgb = color
        except Exception as e:
            right_bg = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, right_left, top_m, right_w, box_h)
            right_bg.fill.solid()
            right_bg.fill.fore_color.rgb = C_WHITE
            right_bg.line.color.rgb = C_BORDER
            right_bg.line.width = Pt(1)
            
            tb_fb = slide.shapes.add_textbox(right_left + Inches(0.3), top_m + Inches(0.3), right_w - Inches(0.6), box_h - Inches(0.6))
            tf_fb = tb_fb.text_frame
            self._set_tf_margins(tf_fb, top=8, bottom=8, left=8, right=8)
            set_para(tf_fb.paragraphs[0], s_data.get("chart_title", "核心业务指标量化看板"), font_size=14, bold=True, color_rgb=C_BLUE)
            for idx, cat in enumerate(cats):
                p = tf_fb.add_paragraph()
                val_str = " | ".join([f"{s.get('name', '指标')}: {s.get('values', [])[idx]}" for s in series_data if idx < len(s.get('values', []))])
                set_para(p, f"【{cat}】 {val_str}", font_size=12, bold=False, color_rgb=C_DARK)
                p.space_before = Pt(8)

    def _render_chart_pie_donut(self, slide, s_data: Dict[str, Any], arch: str):
        """Native Doughnut & Pie Chart Breakdown Engine with Dynamic Reflow (ARCH_17, 2-6 Slices)"""
        self._add_body_master(slide, s_data.get("title", "业务结构与占比分布"), s_data.get("category", "结构拆解"))
        top_m, box_h = Inches(1.6), Inches(5.0)
        
        slices = s_data["slices"]
        num_s = max(1, min(len(slices), 6))
        
        left_w = Inches(5.0)
        chart_top = top_m + Inches(0.2)
        chart_h = Inches(4.6)

        cdata = CategoryChartData()
        cdata.categories = [sl.get("label", "") for sl in slices[:num_s]]
        cdata.add_series("", tuple(sl.get("value", 0) for sl in slices[:num_s]))
        
        try:
            chart_shape = slide.shapes.add_chart(
                XL_CHART_TYPE.DOUGHNUT,
                Inches(0.8), chart_top, left_w, chart_h, cdata
            )
            chart = chart_shape.chart
            chart.has_legend = False
            chart.has_title = False

            # Explicitly color each slice to match right-hand card palette
            if chart.series and len(chart.series) > 0:
                series = chart.series[0]
                for p_idx, pt in enumerate(series.points):
                    fill = pt.format.fill
                    fill.solid()
                    fill.fore_color.rgb = CHART_PALETTE[p_idx % len(CHART_PALETTE)]

            # Precisely compute doughnut center
            cx = Inches(0.8) + left_w / 2
            cy = chart_top + chart_h / 2
            hole_w, hole_h = Inches(1.85), Inches(1.85)
            center_left = cx - hole_w / 2
            center_top = cy - hole_h / 2
            
            center_circle = slide.shapes.add_shape(MSO_SHAPE.OVAL, center_left, center_top, hole_w, hole_h)
            center_circle.fill.solid()
            center_circle.fill.fore_color.rgb = C_WHITE
            center_circle.line.color.rgb = C_BLUE_BG
            center_circle.line.width = Pt(2)
            
            tf_c = center_circle.text_frame
            tf_c.word_wrap = True
            tf_c.vertical_anchor = MSO_ANCHOR.MIDDLE
            self._set_tf_margins(tf_c, top=0, bottom=0, left=2, right=2)
            set_para(tf_c.paragraphs[0], s_data.get("center_metric", "100%"), font_size=20, bold=True, color_rgb=C_BLUE, align=PP_ALIGN.CENTER)
            p_clbl = tf_c.add_paragraph()
            set_para(p_clbl, s_data.get("center_label", "核心业务分布"), font_size=10.0, bold=False, color_rgb=C_MUTED, align=PP_ALIGN.CENTER)
            p_clbl.space_before = Pt(2)
        except Exception as e:
            print(f"[WARN] ARCH_17 doughnut chart rendering fallback: {e}")
        
        right_w, right_left = Inches(6.3), Inches(6.2)
        if num_s <= 3:
            card_h, gap_y = Inches(1.35), Inches(0.25)
            f_pct, f_lbl, f_desc = 22, 14, 11.5
        elif num_s == 4:
            card_h, gap_y = Inches(1.08), Inches(0.18)
            f_pct, f_lbl, f_desc = 20, 13, 11.0
        elif num_s == 5:
            card_h, gap_y = Inches(0.85), Inches(0.12)
            f_pct, f_lbl, f_desc = 17, 12, 10.0
        else: # 6 slices
            card_h, gap_y = Inches(0.70), Inches(0.10)
            f_pct, f_lbl, f_desc = 15, 11, 9.5

        for idx, sl in enumerate(slices[:num_s]):
            cur_top = top_m + idx * (card_h + gap_y)
            bg = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, right_left, cur_top, right_w, card_h)
            bg.fill.solid()
            bg.fill.fore_color.rgb = C_LIGHT_BG
            bg.line.color.rgb = C_BORDER
            bg.line.width = Pt(1)
            
            bar = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, right_left + Inches(0.1), cur_top + Inches(0.12), Inches(0.1), card_h - Inches(0.24))
            bar.fill.solid()
            bar.fill.fore_color.rgb = CHART_PALETTE[idx % len(CHART_PALETTE)]
            bar.line.fill.background()
            
            tb_pct = slide.shapes.add_textbox(right_left + Inches(0.25), cur_top + Inches(0.08), Inches(1.2), card_h - Inches(0.16))
            tf_pct = tb_pct.text_frame
            self._set_tf_margins(tf_pct, top=2, bottom=2, left=2, right=2)
            set_para(tf_pct.paragraphs[0], f"{sl.get('value', '')}%", font_size=f_pct, bold=True, color_rgb=C_BLUE)
            
            tb_txt = slide.shapes.add_textbox(right_left + Inches(1.5), cur_top + Inches(0.08), right_w - Inches(1.6), card_h - Inches(0.16))
            tf_txt = tb_txt.text_frame
            tf_txt.word_wrap = True
            self._set_tf_margins(tf_txt, top=2, bottom=2, left=4, right=4)
            set_para(tf_txt.paragraphs[0], sl.get("label", ""), font_size=f_lbl, bold=True, color_rgb=C_DARK)
            p_d = tf_txt.add_paragraph()
            f_auto = calc_autofit_fontsize(sl.get("desc", ""), base_size=f_desc, min_size=8.5, threshold_len=25)
            set_para(p_d, sl.get("desc", ""), font_size=f_auto, bold=False, color_rgb=C_MUTED)
            p_d.space_before = Pt(2)

    def _render_radar_chart(self, slide, s_data: Dict[str, Any], arch: str):
        """ARCH_16_RADAR: the only retained rich chart, rendered as an editable native radar."""
        self._add_body_master(slide, s_data.get("title", "多维能力对标"), s_data.get("category", "对标"))
        top_m = Inches(1.6)
        full_width = s_data.get("full_width", False)
        chart_w = Inches(11.73) if full_width else Inches(6.5)
        chart_h = Inches(5.0)

        chart_data = CategoryChartData()
        chart_data.categories = s_data["categories"]
        for series in s_data["series"]:
            chart_data.add_series(series["name"], series["values"])
        chart = slide.shapes.add_chart(
            XL_CHART_TYPE.RADAR, Inches(0.8), top_m, chart_w, chart_h, chart_data
        ).chart
        chart.has_legend = True
        chart.legend.position = XL_LEGEND_POSITION.BOTTOM
        chart.legend.include_in_layout = False
        chart.value_axis.minimum_scale = min(0, min(min(series["values"]) for series in s_data["series"]))
        for index, series in enumerate(chart.series):
            series.format.line.color.rgb = CHART_PALETTE[index % len(CHART_PALETTE)]
            series.format.line.width = Pt(2)
        plot = chart.plots[0]
        plot.has_data_labels = True
        plot.data_labels.show_value = True
        plot.data_labels.font.name = FONT_FAMILY
        plot.data_labels.font.size = Pt(8.5)
        plot.data_labels.font.color.rgb = C_DARK

        if not full_width:
            right_w = Inches(4.9)
            right_left = Inches(7.63)

            card_bg = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, right_left, top_m, right_w, chart_h)
            card_bg.fill.solid()
            card_bg.fill.fore_color.rgb = C_LIGHT_BG
            card_bg.line.color.rgb = C_BORDER
            card_bg.line.width = Pt(1)

            h_bg = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, right_left, top_m, right_w, Inches(0.65))
            h_bg.fill.solid()
            h_bg.fill.fore_color.rgb = C_CARD_HEADER_BG
            h_bg.line.fill.background()

            tb_h = slide.shapes.add_textbox(right_left + Inches(0.15), top_m + Inches(0.1), right_w - Inches(0.3), Inches(0.5))
            tf_h = tb_h.text_frame
            tf_h.word_wrap = True
            self._set_tf_margins(tf_h, top=4, bottom=4, left=6, right=6)
            set_para(tf_h.paragraphs[0], s_data.get("insight_header", "核心发现与战略洞察"), font_size=13.5, bold=True, color_rgb=C_BLUE, align=PP_ALIGN.CENTER)

            tb_body = slide.shapes.add_textbox(right_left + Inches(0.2), top_m + Inches(0.8), right_w - Inches(0.4), chart_h - Inches(0.95))
            tf_b = tb_body.text_frame
            tf_b.word_wrap = True
            self._set_tf_margins(tf_b, top=6, bottom=6, left=6, right=6)

            takeaways = s_data.get("insights") or s_data.get("bullets") or []

            for j, t in enumerate(takeaways[:4]):
                p = tf_b.paragraphs[0] if j == 0 else tf_b.add_paragraph()
                f_auto = calc_autofit_fontsize(t, base_size=11.0, min_size=9.0, threshold_len=30)
                set_para(p, f"• {t}", font_size=f_auto, bold=False, color_rgb=C_DARK)
                p.space_before = Pt(8)
                p.space_after = Pt(2)

    # =========================================================================
    # BUILD FROM PAYLOAD MAIN ENTRYPOINT & DISPATCH ROUTING
    # =========================================================================

    def build_from_payload(self, payload: Dict[str, Any], output_path: str):
        output_path = str(ensure_output_path(output_path))
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        if not isinstance(payload, dict):
            raise ValueError("The JSON payload must be an object")
        slides_data = payload.get("slides", [])
        if not isinstance(slides_data, list) or not slides_data:
            raise ValueError("The JSON payload needs a non-empty slides array")
        toc_count = sum(
            1 for slide_data in slides_data
            if isinstance(slide_data, dict)
            and str(slide_data.get("archetype") or slide_data.get("type") or slide_data.get("layout") or slide_data.get("arch") or "").upper().startswith("ARCH_02")
        )
        if toc_count > 1:
            raise ValueError("The presentation supports one single-page ARCH_02 contents slide; combine all section titles into its items list")
        template_path = resolve_template_path(self.templates_dir)
        if template_path and os.path.abspath(output_path) == os.path.abspath(template_path):
            raise ValueError("The CHINT source template cannot be used as the output path")

        # Archetype dispatch for the allowed content contract
        ENGINE_ROUTER = {
            "ARCH_01_COVER": self._render_master_frame,
            "ARCH_02_TOC": self._render_master_frame,
            "ARCH_03_CHAPTER": self._render_master_frame,
            "ARCH_11_CLOSING": self._render_master_frame,
            "ARCH_TABLE": self._render_table,
            "ARCH_16_CHART_BAR_TREND": self._render_chart_bar_trend,
            "ARCH_17_CHART_PIE_DONUT": self._render_chart_pie_donut,
            "ARCH_16_RADAR": self._render_radar_chart,
        }

        for s_data in slides_data:
            arch = (s_data.get("archetype") or s_data.get("type") or s_data.get("layout") or s_data.get("arch") or "").upper()
            _validate_slide_payload(arch, s_data)
            arch = _normalize_arch(arch)
            if arch == "ARCH_TABLE":
                engine_fn = self._render_table
            else:
                engine_fn = ENGINE_ROUTER.get(arch)
            if engine_fn is None:
                raise ValueError(f"Unknown CHINT slide archetype: {arch or '<missing>'}")
            if arch.startswith("ARCH_02"):
                self._add_template_toc_page(s_data["items"])
                continue
            slide = self._add_frame_slide(
                FRAME_LAYOUTS.get(arch, "标题和内容"),
                keep_text=arch.startswith(("ARCH_01", "ARCH_03", "ARCH_11")))
            engine_fn(slide, s_data, arch)

        if payload.get("validation_fixture") is True:
            for slide in self.prs.slides:
                fixture_mark = slide.shapes.add_shape(
                    MSO_SHAPE.ROUNDED_RECTANGLE, Inches(4.9), Inches(0.06), Inches(3.6), Inches(0.3))
                fixture_mark.fill.solid()
                fixture_mark.fill.fore_color.rgb = C_RED_BG
                fixture_mark.line.color.rgb = C_RED_TEXT
                fixture_mark.text_frame.word_wrap = False
                set_para(fixture_mark.text_frame.paragraphs[0],
                         "TEST DATA ONLY · NOT PRODUCT CONTENT", font_size=7,
                         bold=True, color_rgb=C_RED_TEXT, align=PP_ALIGN.CENTER)

        from core.brand import apply_brand
        badge = self._find_media("chint_badge")
        if not badge:
            raise FileNotFoundError("Required CHINT badge assets/media/chint_badge.png is missing")
        apply_brand(self.prs, badge)
        self.prs.save(output_path)

        from check_deck_compliance import check_deck
        report = check_deck(output_path)
        if not report["passed"]:
            for issue in report["issues"]:
                print(f"[FAIL] {issue}", file=sys.stderr)
            raise ValueError(
                f"Deck saved to {output_path} 但未通过结构合规校验，共 {len(report['issues'])} 项。"
                "修正后重跑；校验规则见 scripts/check_deck_compliance.py"
            )
        return output_path


_EDIT_P_NS = "http://schemas.openxmlformats.org/presentationml/2006/main"
_EDIT_A_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"
_EDIT_NS = {"p": _EDIT_P_NS, "a": _EDIT_A_NS}
_EDIT_P_SP = f"{{{_EDIT_P_NS}}}sp"
_EDIT_P_GRAPHIC_FRAME = f"{{{_EDIT_P_NS}}}graphicFrame"
_EDIT_P_SP_TREE = f"{{{_EDIT_P_NS}}}spTree"
_EDIT_A_TBL = f"{{{_EDIT_A_NS}}}tbl"
_EDIT_CNVPR_PATHS = {
    _EDIT_P_SP: f"{{{_EDIT_P_NS}}}nvSpPr/{{{_EDIT_P_NS}}}cNvPr",
    _EDIT_P_GRAPHIC_FRAME: f"{{{_EDIT_P_NS}}}nvGraphicFramePr/{{{_EDIT_P_NS}}}cNvPr",
    f"{{{_EDIT_P_NS}}}pic": f"{{{_EDIT_P_NS}}}nvPicPr/{{{_EDIT_P_NS}}}cNvPr",
    f"{{{_EDIT_P_NS}}}cxnSp": f"{{{_EDIT_P_NS}}}nvCxnSpPr/{{{_EDIT_P_NS}}}cNvPr",
    f"{{{_EDIT_P_NS}}}grpSp": f"{{{_EDIT_P_NS}}}nvGrpSpPr/{{{_EDIT_P_NS}}}cNvPr",
}
_EDIT_FILL_TAGS = {
    f"{{{_EDIT_A_NS}}}{name}"
    for name in ("noFill", "solidFill", "gradFill", "blipFill", "pattFill", "grpFill")
}
_EDIT_RUN_PROPERTY_ORDER = [
    f"{{{_EDIT_A_NS}}}{name}"
    for name in (
        "ln", "noFill", "solidFill", "gradFill", "blipFill", "pattFill", "grpFill",
        "effectLst", "effectDag", "highlight", "uLnTx", "uLn", "latin", "ea", "cs",
        "sym", "hlinkClick", "hlinkMouseOver", "rtl", "extLst",
    )
]
_EDIT_ALIGNMENT = {"left": "l", "center": "ctr", "right": "r", "justify": "just"}
_EDIT_EMU_PER_INCH = 914400


def _edit_shape_kind(element):
    if element.tag == _EDIT_P_SP and element.find(f"{{{_EDIT_P_NS}}}txBody") is not None:
        return "text"
    if element.tag == _EDIT_P_GRAPHIC_FRAME and element.find(f".//{_EDIT_A_TBL}") is not None:
        return "table"
    return "unsupported"


def _edit_text_body_text(text_body):
    paragraphs = []
    for paragraph in text_body.findall(f"./{{{_EDIT_A_NS}}}p"):
        pieces = []
        for child in paragraph:
            if child.tag == f"{{{_EDIT_A_NS}}}br":
                pieces.append("\v")
            elif child.tag in (f"{{{_EDIT_A_NS}}}r", f"{{{_EDIT_A_NS}}}fld"):
                text_node = child.find(f"./{{{_EDIT_A_NS}}}t")
                if text_node is not None:
                    pieces.append(text_node.text or "")
        paragraphs.append("".join(pieces))
    return "\n".join(paragraphs)


def _edit_table_text(table):
    rows = []
    for row in table.findall(f"./{{{_EDIT_A_NS}}}tr"):
        cells = []
        for cell in row.findall(f"./{{{_EDIT_A_NS}}}tc"):
            text_body = cell.find(f"./{{{_EDIT_A_NS}}}txBody")
            cells.append(_edit_text_body_text(text_body) if text_body is not None else "")
        rows.append("\t".join(cells))
    return "\n".join(rows)


def _edit_run_groups(paragraph):
    """Return adjacent editable text runs, separated by fields or other paragraph markup."""
    groups = []
    current = []
    for child in paragraph:
        if child.tag == f"{{{_EDIT_A_NS}}}r":
            text_node = child.find(f"./{{{_EDIT_A_NS}}}t")
            if text_node is not None:
                current.append((child, text_node, text_node.text or ""))
                continue
        if current:
            groups.append(current)
            current = []
    if current:
        groups.append(current)
    return groups


def _edit_create_run(source_run, text):
    run = etree.Element(f"{{{_EDIT_A_NS}}}r")
    if source_run is not None:
        r_pr = source_run.find(f"./{{{_EDIT_A_NS}}}rPr")
        if r_pr is not None:
            run.append(deepcopy(r_pr))
    text_node = etree.SubElement(run, f"{{{_EDIT_A_NS}}}t")
    text_node.text = text
    if text[:1].isspace() or text[-1:].isspace():
        text_node.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    return run


def _edit_create_break(source_run):
    line_break = etree.Element(f"{{{_EDIT_A_NS}}}br")
    if source_run is not None:
        r_pr = source_run.find(f"./{{{_EDIT_A_NS}}}rPr")
        if r_pr is not None:
            line_break.append(deepcopy(r_pr))
    return line_break


def _edit_replace_full_text_body(text_body, replacement, operation_number):
    old_paragraphs = text_body.findall(f"./{{{_EDIT_A_NS}}}p")
    paragraph_tags = {
        f"{{{_EDIT_A_NS}}}pPr", f"{{{_EDIT_A_NS}}}r", f"{{{_EDIT_A_NS}}}fld",
        f"{{{_EDIT_A_NS}}}br", f"{{{_EDIT_A_NS}}}endParaRPr",
        f"{{{_EDIT_A_NS}}}extLst",
    }
    for paragraph in old_paragraphs:
        if paragraph.find(f".//{{{_EDIT_A_NS}}}fld") is not None:
            raise ValueError(f"operation {operation_number}: full-text replacement cannot alter fields")
        if any(child.tag not in paragraph_tags for child in paragraph):
            raise ValueError(f"operation {operation_number}: full-text replacement cannot alter custom paragraph markup")
        if any((run.find(f"./{{{_EDIT_A_NS}}}rPr/{{{_EDIT_A_NS}}}hlinkClick") is not None)
               for run in paragraph.findall(f"./{{{_EDIT_A_NS}}}r")):
            raise ValueError(f"operation {operation_number}: full-text replacement cannot alter hyperlinks")

    normalized = replacement.replace("\r\n", "\n").replace("\r", "\n")
    new_paragraphs = []
    for index, paragraph_text in enumerate(normalized.split("\n")):
        source_paragraph = old_paragraphs[min(index, len(old_paragraphs) - 1)] if old_paragraphs else None
        paragraph = etree.Element(f"{{{_EDIT_A_NS}}}p")
        source_run = None
        if source_paragraph is not None:
            p_pr = source_paragraph.find(f"./{{{_EDIT_A_NS}}}pPr")
            if p_pr is not None:
                paragraph.append(deepcopy(p_pr))
            source_runs = source_paragraph.findall(f"./{{{_EDIT_A_NS}}}r")
            source_run = source_runs[0] if source_runs else None

        for line_index, line in enumerate(paragraph_text.split("\v")):
            if line_index:
                paragraph.append(_edit_create_break(source_run))
            if line:
                paragraph.append(_edit_create_run(source_run, line))

        if source_paragraph is not None:
            end_properties = source_paragraph.find(f"./{{{_EDIT_A_NS}}}endParaRPr")
            if end_properties is not None:
                paragraph.append(deepcopy(end_properties))
            extension = source_paragraph.find(f"./{{{_EDIT_A_NS}}}extLst")
            if extension is not None:
                paragraph.append(deepcopy(extension))
        new_paragraphs.append(paragraph)

    insertion_index = (text_body.index(old_paragraphs[0]) if old_paragraphs else len(text_body))
    for paragraph in old_paragraphs:
        text_body.remove(paragraph)
    for offset, paragraph in enumerate(new_paragraphs):
        text_body.insert(insertion_index + offset, paragraph)


def _edit_replace_text(text_body, current_text, old_text, new_text, operation_number):
    if old_text == current_text:
        _edit_replace_full_text_body(text_body, new_text, operation_number)
        return
    if not old_text:
        raise ValueError(f"operation {operation_number}: empty from is allowed only for an empty target")
    if "\n" in old_text or "\r" in old_text or "\v" in old_text:
        raise ValueError(f"operation {operation_number}: a partial replacement cannot cross paragraph or line breaks")

    matches = []
    for paragraph in text_body.findall(f"./{{{_EDIT_A_NS}}}p"):
        for group in _edit_run_groups(paragraph):
            combined = "".join(value for _run, _node, value in group)
            offset = 0
            while True:
                start = combined.find(old_text, offset)
                if start < 0:
                    break
                matches.append((paragraph, group, start, start + len(old_text)))
                offset = start + 1
    if len(matches) != 1:
        raise ValueError(f"operation {operation_number}: from must match exactly once within a paragraph")

    paragraph, group, match_start, match_end = matches[0]
    spans = []
    offset = 0
    for run, text_node, value in group:
        spans.append((run, text_node, value, offset, offset + len(value)))
        offset += len(value)
    affected = [item for item in spans if item[3] < match_end and item[4] > match_start]
    start_run, _start_node, start_value, start_at, _start_end = affected[0]
    end_run, _end_node, end_value, end_at, _end_end = affected[-1]
    prefix = start_value[:match_start - start_at]
    suffix = end_value[match_end - end_at:]

    normalized = new_text.replace("\r\n", "\n").replace("\r", "\n")
    lines = re.split(r"\n|\v", normalized)
    replacement_nodes = []
    first_line = prefix + lines[0]
    if first_line:
        replacement_nodes.append(_edit_create_run(start_run, first_line))
    for line in lines[1:]:
        replacement_nodes.append(_edit_create_break(start_run))
        if line:
            replacement_nodes.append(_edit_create_run(start_run, line))
    if suffix:
        replacement_nodes.append(_edit_create_run(end_run, suffix))

    parent = start_run.getparent()
    siblings = list(parent)
    start_index, end_index = siblings.index(start_run), siblings.index(end_run)
    for child in siblings[start_index:end_index + 1]:
        parent.remove(child)
    for offset, child in enumerate(replacement_nodes):
        parent.insert(start_index + offset, child)


def _edit_insert_ordered(parent, child):
    order = {tag: index for index, tag in enumerate(_EDIT_RUN_PROPERTY_ORDER)}
    child_order = order.get(child.tag, len(order))
    for index, existing in enumerate(list(parent)):
        if order.get(existing.tag, len(order)) > child_order:
            parent.insert(index, child)
            return
    parent.append(child)


def _edit_ensure_paragraph_properties(paragraph):
    p_pr = paragraph.find(f"./{{{_EDIT_A_NS}}}pPr")
    if p_pr is None:
        p_pr = etree.Element(f"{{{_EDIT_A_NS}}}pPr")
        paragraph.insert(0, p_pr)
    return p_pr


def _edit_ensure_run_properties(run):
    r_pr = run.find(f"./{{{_EDIT_A_NS}}}rPr")
    if r_pr is None:
        r_pr = etree.Element(f"{{{_EDIT_A_NS}}}rPr")
        run.insert(0, r_pr)
    return r_pr


def _edit_set_run_property(r_pr, style):
    if "font_size_pt" in style:
        r_pr.set("sz", str(round(float(style["font_size_pt"]) * 100)))
    if "bold" in style:
        r_pr.set("b", "1" if style["bold"] else "0")
    if "italic" in style:
        r_pr.set("i", "1" if style["italic"] else "0")
    if "font_color" in style:
        for child in list(r_pr):
            if child.tag in _EDIT_FILL_TAGS:
                r_pr.remove(child)
        solid_fill = etree.Element(f"{{{_EDIT_A_NS}}}solidFill")
        rgb = etree.SubElement(solid_fill, f"{{{_EDIT_A_NS}}}srgbClr")
        rgb.set("val", style["font_color"])
        _edit_insert_ordered(r_pr, solid_fill)
    if "font_family" in style:
        for script in ("latin", "ea", "cs"):
            tag = f"{{{_EDIT_A_NS}}}{script}"
            node = r_pr.find(f"./{tag}")
            if node is None:
                node = etree.Element(tag)
                _edit_insert_ordered(r_pr, node)
            node.set("typeface", style["font_family"])


def _edit_apply_style(text_body, style, operation_number):
    if not isinstance(style, dict):
        raise ValueError(f"operation {operation_number}: style must be an object")
    style = dict(style)
    allowed = {"font_family", "font_size_pt", "font_color", "alignment", "bold", "italic"}
    unknown = set(style) - allowed
    if unknown:
        raise ValueError(f"operation {operation_number}: unsupported style fields: {', '.join(sorted(unknown))}")
    if not style:
        raise ValueError(f"operation {operation_number}: style cannot be empty")
    if "font_family" in style and (not isinstance(style["font_family"], str) or not style["font_family"].strip()):
        raise ValueError(f"operation {operation_number}: font_family must be a non-empty string")
    if "font_size_pt" in style:
        size = style["font_size_pt"]
        if isinstance(size, bool) or not isinstance(size, (int, float)) or not math.isfinite(size) or not 1 <= size <= 200:
            raise ValueError(f"operation {operation_number}: font_size_pt must be between 1 and 200")
    if "font_color" in style:
        if not isinstance(style["font_color"], str):
            raise ValueError(f"operation {operation_number}: font_color must be a six-digit RGB string")
        color = style["font_color"].removeprefix("#")
        if re.fullmatch(r"[0-9A-Fa-f]{6}", color) is None:
            raise ValueError(f"operation {operation_number}: font_color must be a six-digit RGB color")
        style["font_color"] = color.upper()
    if "alignment" in style and (not isinstance(style["alignment"], str)
                                  or style["alignment"] not in _EDIT_ALIGNMENT):
        raise ValueError(f"operation {operation_number}: alignment must be left, center, right, or justify")
    for key in ("bold", "italic"):
        if key in style and not isinstance(style[key], bool):
            raise ValueError(f"operation {operation_number}: {key} must be a boolean")

    paragraphs = text_body.findall(f"./{{{_EDIT_A_NS}}}p")
    if not paragraphs:
        raise ValueError(f"operation {operation_number}: target has no editable paragraphs")
    for paragraph in paragraphs:
        p_pr = paragraph.find(f"./{{{_EDIT_A_NS}}}pPr")
        if "alignment" in style:
            p_pr = p_pr if p_pr is not None else _edit_ensure_paragraph_properties(paragraph)
            p_pr.set("algn", _EDIT_ALIGNMENT[style["alignment"]])
        if set(style) - {"alignment"}:
            run_properties = []
            for run in paragraph:
                if run.tag in (f"{{{_EDIT_A_NS}}}r", f"{{{_EDIT_A_NS}}}fld"):
                    run_properties.append(_edit_ensure_run_properties(run))
            if p_pr is not None:
                default_rpr = p_pr.find(f"./{{{_EDIT_A_NS}}}defRPr")
                if default_rpr is not None:
                    run_properties.append(default_rpr)
            end_rpr = paragraph.find(f"./{{{_EDIT_A_NS}}}endParaRPr")
            if end_rpr is not None:
                run_properties.append(end_rpr)
            if not run_properties:
                p_pr = p_pr if p_pr is not None else _edit_ensure_paragraph_properties(paragraph)
                default_rpr = etree.Element(f"{{{_EDIT_A_NS}}}defRPr")
                p_pr.append(default_rpr)
                run_properties.append(default_rpr)
            for r_pr in run_properties:
                _edit_set_run_property(r_pr, style)


def _edit_apply_geometry(shape, geometry, slide_width, slide_height, operation_number):
    allowed = {"left", "top", "width", "height"}
    unknown = set(geometry) - allowed
    if unknown or not geometry:
        raise ValueError(f"operation {operation_number}: geometry_in accepts left, top, width, height")
    if shape.tag == _EDIT_P_SP:
        xfrm = shape.find(f"./{{{_EDIT_P_NS}}}spPr/{{{_EDIT_A_NS}}}xfrm")
    else:
        xfrm = shape.find(f"./{{{_EDIT_P_NS}}}xfrm")
    if xfrm is None:
        raise ValueError(f"operation {operation_number}: target has no editable geometry")
    offset = xfrm.find(f"./{{{_EDIT_A_NS}}}off")
    extent = xfrm.find(f"./{{{_EDIT_A_NS}}}ext")
    if offset is None or extent is None:
        raise ValueError(f"operation {operation_number}: target geometry is incomplete")
    values = {
        "left": int(offset.get("x")), "top": int(offset.get("y")),
        "width": int(extent.get("cx")), "height": int(extent.get("cy")),
    }
    for key, value in geometry.items():
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
            raise ValueError(f"operation {operation_number}: geometry {key} must be a finite number of inches")
        values[key] = round(value * _EDIT_EMU_PER_INCH)
    if (values["left"] < 0 or values["top"] < 0 or values["width"] <= 0 or values["height"] <= 0
            or values["left"] + values["width"] > slide_width
            or values["top"] + values["height"] > slide_height):
        raise ValueError(f"operation {operation_number}: geometry must remain within the slide bounds")
    offset.set("x", str(values["left"]))
    offset.set("y", str(values["top"]))
    extent.set("cx", str(values["width"]))
    extent.set("cy", str(values["height"]))


def _edit_shape_fingerprints(root):
    sp_tree = root.find(f".//{{{_EDIT_P_NS}}}spTree")
    if sp_tree is None:
        return {}
    result = {}
    for element in sp_tree:
        path = _EDIT_CNVPR_PATHS.get(element.tag)
        if path is None:
            continue
        c_nv_pr = element.find(path)
        if c_nv_pr is not None and c_nv_pr.get("id"):
            result[c_nv_pr.get("id")] = etree.tostring(element, method="c14n")
    return result


def _edit_apply_operation(root, operation, operation_number, expected_slide_part,
                          slide_width, slide_height):
    if not isinstance(operation, dict):
        raise ValueError(f"operation {operation_number} must be an object")
    allowed = {"slide", "slide_part", "shape_id", "shape_name", "target_type", "expected_text",
               "cell", "replace_text", "style", "geometry_in"}
    unknown = set(operation) - allowed
    if unknown:
        raise ValueError(f"operation {operation_number} has unsupported fields: {', '.join(sorted(unknown))}")
    slide_number, shape_id = operation.get("slide"), operation.get("shape_id")
    if isinstance(slide_number, bool) or not isinstance(slide_number, int) or slide_number < 1:
        raise ValueError(f"operation {operation_number}: slide must be a one-based integer")
    if isinstance(shape_id, bool) or not isinstance(shape_id, int) or shape_id < 1:
        raise ValueError(f"operation {operation_number}: shape_id must be a positive integer")
    if operation.get("slide_part") != expected_slide_part:
        raise ValueError(f"operation {operation_number}: slide_part does not match the inspected source")
    if not isinstance(operation.get("shape_name"), str):
        raise ValueError(f"operation {operation_number}: shape_name from editable-target inventory is required")
    if operation.get("target_type") not in {"text", "table"}:
        raise ValueError(f"operation {operation_number}: target_type must be text or table")
    if not any(key in operation for key in ("replace_text", "style", "geometry_in")):
        raise ValueError(f"operation {operation_number}: no edit action was provided")

    sp_tree = root.find(f".//{{{_EDIT_P_NS}}}spTree")
    if sp_tree is None:
        raise ValueError(f"operation {operation_number}: slide has no shape tree")
    matches = []
    for element in sp_tree.iter():
        path = _EDIT_CNVPR_PATHS.get(element.tag)
        if path is None:
            continue
        c_nv_pr = element.find(path)
        if c_nv_pr is not None and c_nv_pr.get("id") == str(shape_id):
            matches.append((element, c_nv_pr))
    if len(matches) != 1:
        raise ValueError(f"operation {operation_number}: shape_id {shape_id} is missing or ambiguous")
    shape, c_nv_pr = matches[0]
    if shape.getparent() is not sp_tree:
        raise ValueError(f"operation {operation_number}: grouped shapes are outside the supported edit scope")
    kind = _edit_shape_kind(shape)
    if kind == "unsupported":
        raise ValueError(f"operation {operation_number}: charts, images, and complex objects cannot be edited")
    if kind != operation["target_type"]:
        raise ValueError(f"operation {operation_number}: target_type does not match the source object")
    if c_nv_pr.get("name", "") != operation["shape_name"]:
        raise ValueError(f"operation {operation_number}: shape_name no longer matches shape_id {shape_id}")

    cell_spec = operation.get("cell")
    text_body = None
    target_text = None
    table = None
    if kind == "text":
        if cell_spec is not None:
            raise ValueError(f"operation {operation_number}: cell is only valid for table targets")
        text_body = shape.find(f"./{{{_EDIT_P_NS}}}txBody")
        target_text = _edit_text_body_text(text_body) if text_body is not None else None
    else:
        table = shape.find(f".//{_EDIT_A_TBL}")
        if table is None:
            raise ValueError(f"operation {operation_number}: table object no longer exists")
        if cell_spec is not None:
            row = cell_spec.get("row") if isinstance(cell_spec, dict) else None
            column = cell_spec.get("column") if isinstance(cell_spec, dict) else None
            if any(isinstance(value, bool) or not isinstance(value, int) or value < 0
                   for value in (row, column)):
                raise ValueError(f"operation {operation_number}: cell requires zero-based row and column integers")
            rows = table.findall(f"./{{{_EDIT_A_NS}}}tr")
            if row >= len(rows):
                raise ValueError(f"operation {operation_number}: table row {row} does not exist")
            cells = rows[row].findall(f"./{{{_EDIT_A_NS}}}tc")
            if column >= len(cells):
                raise ValueError(f"operation {operation_number}: table column {column} does not exist")
            cell = cells[column]
            try:
                merged = (cell.get("hMerge") == "1" or cell.get("vMerge") == "1"
                          or int(cell.get("gridSpan", "1")) > 1)
            except ValueError as exc:
                raise ValueError(f"operation {operation_number}: table cell gridSpan is invalid") from exc
            if merged:
                raise ValueError(f"operation {operation_number}: merged table cells are unsupported")
            text_body = cell.find(f"./{{{_EDIT_A_NS}}}txBody")
            target_text = _edit_text_body_text(text_body) if text_body is not None else None
        else:
            if "replace_text" in operation or "style" in operation:
                raise ValueError(f"operation {operation_number}: table text/style edits require a cell target")
            target_text = _edit_table_text(table)

    if not isinstance(operation.get("expected_text"), str) or operation["expected_text"] != target_text:
        raise ValueError(f"operation {operation_number}: expected_text does not match the inspected source")

    if "replace_text" in operation:
        replacement = operation["replace_text"]
        if not isinstance(replacement, dict) or set(replacement) != {"from", "to"}:
            raise ValueError(f"operation {operation_number}: replace_text needs exact from/to strings")
        old_text, new_text = replacement["from"], replacement["to"]
        if not isinstance(old_text, str) or not isinstance(new_text, str):
            raise ValueError(f"operation {operation_number}: replacement from/to must be strings")
        if text_body is None:
            raise ValueError(f"operation {operation_number}: text replacement needs a text shape or table cell")
        _edit_replace_text(text_body, target_text, old_text, new_text, operation_number)

    if "style" in operation:
        style = operation["style"]
        if not isinstance(style, dict) or not style:
            raise ValueError(f"operation {operation_number}: style must be a non-empty object")
        if text_body is None:
            raise ValueError(f"operation {operation_number}: style edits need a text shape or table cell")
        _edit_apply_style(text_body, style, operation_number)

    if "geometry_in" in operation:
        geometry = operation["geometry_in"]
        if not isinstance(geometry, dict):
            raise ValueError(f"operation {operation_number}: geometry_in must be an object")
        _edit_apply_geometry(shape, geometry, slide_width, slide_height, operation_number)


def edit_existing_presentation(config, output_override=None):
    """Apply safe text/style/geometry edits to a copy of an existing PPTX package."""
    if not isinstance(config, dict):
        raise ValueError("The edit config must be a JSON object")
    unknown_config = set(config) - {"source", "source_sha256", "output", "edits"}
    if unknown_config:
        raise ValueError(f"unsupported edit config fields: {', '.join(sorted(unknown_config))}")
    source_value = config.get("source")
    edits = config.get("edits")
    if not isinstance(source_value, str) or not source_value:
        raise ValueError("The edit config needs a source PPTX path")
    if not isinstance(edits, list) or not edits:
        raise ValueError("The edit config needs a non-empty edits array")
    expected_digest = config.get("source_sha256")
    if not isinstance(expected_digest, str) or re.fullmatch(r"[0-9a-fA-F]{64}", expected_digest) is None:
        raise ValueError("The edit config needs the source_sha256 from --edit-targets")

    source_path = Path(source_value).expanduser().resolve()
    if not source_path.is_file() or source_path.suffix.lower() != ".pptx":
        raise ValueError("source must be an existing .pptx file")
    actual_digest = hashlib.sha256(source_path.read_bytes()).hexdigest()
    if actual_digest.lower() != expected_digest.lower():
        raise ValueError("source_sha256 does not match the inspected source; inspect the current file again")

    output_value = output_override or config.get("output")
    if output_value:
        output_path = ensure_output_path(output_value)
    else:
        output_path = ensure_output_path(default_output_dir() / f"{source_path.stem}_edited.pptx")
    same_file = output_path == source_path
    if output_path.exists():
        same_file = same_file or os.path.samefile(source_path, output_path)
    if same_file:
        raise ValueError("source and output must be different files; the source deck is never overwritten")
    if output_path.suffix.lower() != ".pptx":
        raise ValueError("output must use the .pptx extension")

    try:
        source_prs = Presentation(str(source_path))
    except Exception as exc:
        raise ValueError(f"source PPTX could not be opened: {exc}") from exc
    slide_parts = [str(slide.part.partname).lstrip("/") for slide in source_prs.slides]
    slide_width, slide_height = source_prs.slide_width, source_prs.slide_height
    modified_parts = {}
    targeted_ids = {}
    roots = {}
    original_shape_fingerprints = {}

    try:
        with zipfile.ZipFile(source_path, "r") as source_zip:
            if any(name.lower().startswith("_xmlsignatures/") for name in source_zip.namelist()):
                raise ValueError("digitally signed PPTX files cannot be edited without invalidating the signature")
            for operation_number, operation in enumerate(edits, 1):
                if not isinstance(operation, dict):
                    raise ValueError(f"operation {operation_number} must be an object")
                slide_number = operation.get("slide")
                if isinstance(slide_number, bool) or not isinstance(slide_number, int) or not 1 <= slide_number <= len(slide_parts):
                    raise ValueError(f"operation {operation_number}: slide is outside the source deck")
                part_name = slide_parts[slide_number - 1]
                if part_name not in roots:
                    if part_name not in source_zip.namelist():
                        raise ValueError(f"source slide part is missing: {part_name}")
                    parser = etree.XMLParser(resolve_entities=False, no_network=True, recover=False,
                                             remove_blank_text=False)
                    roots[part_name] = etree.fromstring(source_zip.read(part_name), parser)
                    targeted_ids[part_name] = set()
                    original_shape_fingerprints[part_name] = _edit_shape_fingerprints(roots[part_name])
                if operation.get("slide_part") != part_name:
                    raise ValueError(f"operation {operation_number}: slide_part does not match the inspected source")
                shape_id = operation.get("shape_id")
                if isinstance(shape_id, bool) or not isinstance(shape_id, int):
                    raise ValueError(f"operation {operation_number}: shape_id must be an integer")
                targeted_ids[part_name].add(str(shape_id))
                _edit_apply_operation(roots[part_name], operation, operation_number, part_name,
                                      slide_width, slide_height)

            for part_name, root in roots.items():
                original_shapes = original_shape_fingerprints[part_name]
                edited_shapes = _edit_shape_fingerprints(root)
                if list(original_shapes) != list(edited_shapes):
                    raise ValueError(f"shape order or count changed unexpectedly in {part_name}")
                for shape_id, fingerprint in original_shapes.items():
                    if shape_id not in targeted_ids[part_name] and edited_shapes[shape_id] != fingerprint:
                        raise ValueError(f"an unselected shape changed unexpectedly in {part_name}: shape_id {shape_id}")
                modified_parts[part_name] = etree.tostring(
                    root, encoding="UTF-8", xml_declaration=True, standalone=True)

            os.makedirs(str(output_path.parent), exist_ok=True)
            fd, temp_path = tempfile.mkstemp(prefix=".chint-edit-", suffix=".pptx", dir=str(output_path.parent))
            os.close(fd)
            try:
                with zipfile.ZipFile(temp_path, "w") as output_zip:
                    for info in source_zip.infolist():
                        payload = modified_parts.get(info.filename)
                        if payload is None:
                            payload = source_zip.read(info.filename)
                        output_zip.writestr(deepcopy(info), payload)
                with zipfile.ZipFile(temp_path, "r") as output_zip:
                    bad_part = output_zip.testzip()
                    if bad_part:
                        raise ValueError(f"edited PPTX package failed CRC validation at {bad_part}")
                    for info in source_zip.infolist():
                        if info.filename not in modified_parts and source_zip.read(info.filename) != output_zip.read(info.filename):
                            raise ValueError(f"an untouched package part changed unexpectedly: {info.filename}")
                output_prs = Presentation(temp_path)
                if len(output_prs.slides) != len(source_prs.slides):
                    raise ValueError("slide count changed during local edit")
                os.replace(temp_path, output_path)
            except Exception:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                raise
    except (zipfile.BadZipFile, etree.XMLSyntaxError) as exc:
        raise ValueError(f"source PPTX contains an unreadable package part: {exc}") from exc

    from check_deck_compliance import check_deck
    report = check_deck(output_path)
    if not report["passed"]:
        for issue in report["issues"]:
            print(f"[FAIL] {issue}", file=sys.stderr)
        raise ValueError(
            f"Edited deck saved to {output_path} 但未通过结构合规校验，共 {len(report['issues'])} 项。"
            "修正后重跑；校验规则见 scripts/check_deck_compliance.py"
        )

    return str(output_path)


def main(argv=None):
    import argparse

    parser = argparse.ArgumentParser(description="Create or locally edit an editable CHINT presentation using JSON data.")
    parser.add_argument("payload_pos", nargs="?", help=argparse.SUPPRESS)
    parser.add_argument("output_pos", nargs="?", help=argparse.SUPPRESS)
    parser.add_argument("--config", dest="payload", help="JSON payload file")
    parser.add_argument("--edit-config", dest="edit_config", help="JSON edit manifest for supported local edits to an existing PPTX")
    parser.add_argument("--output", dest="output", help="output .pptx path")
    args = parser.parse_args(argv)
    if args.edit_config:
        if args.payload or args.payload_pos or args.output_pos:
            parser.error("Use --edit-config alone; do not combine it with creation payload paths")
        try:
            edit_config_path = Path(args.edit_config).expanduser().resolve()
            with open(edit_config_path, "r", encoding="utf-8") as source:
                edit_config = json.load(source)
            result = edit_existing_presentation(edit_config, args.output)
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            print(f"[FAIL] {exc}", file=sys.stderr)
            return 1
        print(f"Edited {result} successfully.")
        return 0
    if (args.payload and args.payload_pos) or (args.output and args.output_pos):
        parser.error("Do not combine a named option with its positional equivalent")
    payload_path = args.payload or args.payload_pos
    output_path = args.output or args.output_pos
    if not payload_path or not output_path:
        parser.error("Provide --config and --output, or the two legacy positional paths")
    try:
        payload_path = Path(payload_path).expanduser().resolve()
        with open(payload_path, "r", encoding="utf-8") as source:
            payload = json.load(source)
        result = ChintPresentationEngine().build_from_payload(payload, output_path)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"[FAIL] {exc}", file=sys.stderr)
        return 1
    print(f"Generated {result} successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
