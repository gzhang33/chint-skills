#!/usr/bin/env python3
"""
CHINT PPTX Generation Engine (2026 VI Standard Master Edition - Modularized 12-Engine Architecture)

Features:
- Modularized 12 Core Composition Engines (_render_*) handling all 34 Slide Layout Archetypes cleanly.
- 100% Backward-Compatible Semantic Dispatch Routing for all 34 Archetype Aliases (ARCH_01 to ARCH_34).
- Full 1:1 alignment with the six-slide 2026 master template (26年模板拓新体.pptx).
- Official 2026 VI Color Palette Tokens & Multi-series 8-stage Chart Palette.
"""

import os
import io
import json
import math
import re
import sys
import tempfile
import zipfile
import hashlib
from copy import deepcopy
from pathlib import Path
from typing import Dict, Any, List, Optional, Union

from lxml import etree
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION
from pptx.chart.data import CategoryChartData

from chint_vector_chart_builder import ChintVectorChartBuilder

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

_REQUIRED_FIELDS = {
    "ARCH_01": ("title",), "ARCH_02": ("items",), "ARCH_03": ("title",),
    "ARCH_15": ("channels", "offices"),
    "ARCH_07": ("pain_points", "solutions", "pain_summary", "solution_summary"),
    "ARCH_21": ("before_items", "after_items", "before_summary", "after_summary"),
    "ARCH_22": ("problems", "improvements", "problem_summary", "improve_summary"),
    "ARCH_10": ("client_name", "hero_metric", "hero_desc", "bullets"),
    "ARCH_13": ("coverage_title", "stats", "offices", "network_title"),
    "ARCH_19": ("hero_label", "hero_number", "hero_unit", "hero_desc", "bullets"),
    "ARCH_04": ("kpi_cards",), "ARCH_05": ("columns",), "ARCH_12": ("members",),
    "ARCH_18": ("metrics",), "ARCH_23": ("risks",), "ARCH_24": ("pillars",),
    "ARCH_33": ("honors",), "ARCH_25": ("steps",), "ARCH_27": ("steps",),
    "ARCH_28": ("gates",), "ARCH_30": ("milestones",), "ARCH_26": ("stages",),
    "ARCH_20": ("strengths", "weaknesses", "opportunities", "threats"),
    "ARCH_09": ("modules",), "ARCH_34": ("partners",), "ARCH_08": ("layers",),
    "ARCH_31": ("pillars", "base_title", "base_desc"), "ARCH_32": ("nodes",),
    "ARCH_29": ("tasks",),
}

# --- Content-page contract (2026-11 revision) -------------------------------
# Only these archetypes produce slides. The other renderers stay in the file as
# history but are rejected at payload validation; see ARCHETYPE_MIGRATION.
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

ARCHETYPE_MIGRATION = {
    "ARCH_04": "ARCH_TABLE（两列：指标名 / 数值）",
    "ARCH_05": "ARCH_TABLE（多列表格，每列一个主题）",
    "ARCH_06": "ARCH_TABLE（阶段 / 时间 / 说明 三列）",
    "ARCH_07": "ARCH_TABLE（问题 / 应对 两列）",
    "ARCH_08": "ARCH_TABLE（层级 / 内容 两列）",
    "ARCH_09": "ARCH_TABLE（场景 / 方案 两列）",
    "ARCH_10": "ARCH_TABLE（指标 / 数值 / 说明 三列）",
    "ARCH_12": "ARCH_TABLE（姓名 / 角色 / 职责 三列）",
    "ARCH_13": "ARCH_TABLE（区域 / 覆盖 两列）",
    "ARCH_14": "ARCH_TABLE（节点 / 说明 两列）",
    "ARCH_15": "ARCH_TABLE（渠道 / 联系方式 两列）",
    "ARCH_16_COMBO": "ARCH_TABLE 或 ARCH_16_CHART_BAR_TREND",
    "ARCH_16_DIVERGING": "ARCH_TABLE 或 ARCH_16_CHART_BAR_TREND",
    "ARCH_16_FUNNEL": "ARCH_TABLE（阶段 / 数量 / 转化率 三列）",
    "ARCH_16_GAUGE": "ARCH_TABLE（指标 / 当前值 / 目标值 三列）",
    "ARCH_16_HEATMAP": "ARCH_TABLE（行标签 + 数值列）",
    "ARCH_16_SANKEY": "ARCH_TABLE（来源 / 去向 / 数量 三列）",
    "ARCH_16_STACKED_AREA": "ARCH_TABLE 或 ARCH_16_CHART_BAR_TREND",
    "ARCH_16_WATERFALL": "ARCH_TABLE（项目 / 变动额 两列）",
    "ARCH_18": "ARCH_TABLE（指标 / 数值 / 说明 三列）",
    "ARCH_19": "ARCH_TABLE（指标 / 数值 两列）",
    "ARCH_20": "ARCH_TABLE（象限 / 内容 两列）",
    "ARCH_21": "ARCH_TABLE（现状 / 改进 两列）",
    "ARCH_22": "ARCH_TABLE（短板 / 改善动作 两列）",
    "ARCH_23": "ARCH_TABLE（风险 / 等级 / 预案 三列）",
    "ARCH_24": "ARCH_TABLE（支柱 / 说明 两列）",
    "ARCH_25": "ARCH_TABLE（步骤 / 动作 / 交付物 三列）",
    "ARCH_26": "ARCH_TABLE（阶段 / 数量 / 转化率 三列）",
    "ARCH_27": "ARCH_TABLE（版本 / 说明 两列）",
    "ARCH_28": "ARCH_TABLE（阶段 / 决策点 两列）",
    "ARCH_29": "ARCH_TABLE（任务 / 责任人 / 时间 多列表格）",
    "ARCH_30": "ARCH_TABLE（年份 / 里程碑 两列）",
    "ARCH_31": "ARCH_TABLE（支柱 / 说明 两列）",
    "ARCH_32": "ARCH_TABLE（参与方 / 职责 两列）",
    "ARCH_33": "ARCH_TABLE（认证 / 机构 / 指标 三列）",
    "ARCH_34": "ARCH_TABLE（伙伴 / 能力 两列）",
}

TABLE_MAX_ROWS = 20


def _normalize_arch(arch: str) -> str:
    arch = (arch or "").strip().upper()
    if arch.startswith("ARCH_TABLE"):
        return "ARCH_TABLE"
    if arch.startswith("ARCH_17"):
        return "ARCH_17_CHART_PIE_DONUT"
    if arch.startswith("ARCH_16_RADAR"):
        return "ARCH_16_RADAR"
    if arch.startswith("ARCH_16_CHART_BAR") or arch in ("ARCH_16_BAR_CHART", "ARCH_16_CHART_TREND"):
        return "ARCH_16_CHART_BAR_TREND"
    return arch


def _reject_retired(arch: str) -> None:
    for prefix, replacement in ARCHETYPE_MIGRATION.items():
        if arch.startswith(prefix):
            raise ValueError(
                f"{arch} 已停用。改用 {replacement}。内容页现仅支持："
                + "、".join(ALLOWED_ARCHETYPES)
            )
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
    if arch.startswith("ARCH_06"):
        required = ("nodes",) if arch == "ARCH_06_CONCENTRIC_HUB" else ("stages",)
    if arch.startswith("ARCH_14"):
        required = ("nodes",)
    if arch.startswith("ARCH_17"):
        required = ("slices", "center_metric", "center_label")

    chart_kind = (data.get("chart_type") or "").strip().lower()
    if arch.startswith("ARCH_16") and not chart_kind:
        for marker, value in (("RADAR", "radar"), ("COMBO", "combo"), ("DUAL_AXIS", "combo"),
                              ("DIVERGING", "diverging"), ("EVOLUTION", "evolution"),
                              ("HEATMAP", "heatmap"), ("MATRIX", "heatmap"),
                              ("WATERFALL", "waterfall"), ("SANKEY", "sankey"),
                              ("FUNNEL", "funnel"), ("GAUGE", "gauge"), ("BULLET", "gauge"),
                              ("STACKED_AREA", "stacked_area"), ("AREA", "area")):
            if marker in arch:
                chart_kind = value
                break
    chart_fields = ()
    if arch in ("ARCH_16_CHART_BAR_TREND", "ARCH_16_BAR_CHART", "ARCH_16_CHART_TREND"):
        chart_fields = ("categories", "series", "summary_bullets")
    elif arch.startswith("ARCH_16"):
        chart_fields = {
            "radar": ("categories", "series"), "combo": ("categories", "bar_series", "line_series"),
            "diverging": ("categories", "values", "unit"),
            "evolution": ("stages", "values", "sub_labels", "unit"),
            "heatmap": ("row_labels", "col_labels", "data_matrix"),
            "waterfall": ("categories", "values", "unit"), "sankey": ("flows",),
            "funnel": ("stages", "values", "unit"),
            "gauge": ("current_val", "target_val", "min_val", "max_val", "unit"),
            "stacked_area": ("categories", "series", "unit"), "area": ("categories", "series", "unit"),
        }.get(chart_kind, ())
        if not chart_fields:
            raise ValueError(f"{arch} requires explicit source-backed chart data and a supported chart type")

    missing = [key for key in (*required, *chart_fields) if key not in data or data[key] is None or data[key] == "" or data[key] == []]
    if missing:
        raise ValueError(f"{arch} is missing source-backed content: {', '.join(dict.fromkeys(missing))}")

    lists = set(required) | set(chart_fields)
    limits = {
        "channels": 4, "kpi_cards": 4, "columns": 5, "members": 5, "metrics": 5,
        "risks": 4, "honors": 5, "pillars": 4, "stages": 5, "steps": 6, "gates": 6,
        "milestones": 4, "slices": 6, "layers": 4, "tasks": 5,
    }
    for key in lists:
        value = data.get(key)
        if isinstance(value, list):
            if not value:
                raise ValueError(f"{arch}.{key} cannot be empty")
            max_count = limits.get(key)
            if max_count is not None and len(value) > max_count:
                raise ValueError(f"{arch}.{key} exceeds the visible layout capacity; split the content across slides")

    if arch.startswith("ARCH_02"):
        if not isinstance(data["items"], list):
            raise ValueError("ARCH_02.items must be a list of section titles")
        if len(data["items"]) > 12:
            raise ValueError("ARCH_02.items exceeds the one-page capacity of 12 readable entries; condense or group section names")
        for index, item in enumerate(data["items"]):
            title = item.get("title") if isinstance(item, dict) else item
            if not isinstance(title, str) or not title.strip():
                raise ValueError(f"ARCH_02.items[{index}] needs a title")
    if arch.startswith("ARCH_15"):
        for index, item in enumerate(data["channels"]):
            if not isinstance(item, dict) or not item.get("title") or not item.get("desc"):
                raise ValueError(f"ARCH_15.channels[{index}] needs a source-backed title and description")
    row_fields = {
        "ARCH_04": {"kpi_cards": ("number|metric", "label")},
        "ARCH_05": {"columns": ("header",)},
        "ARCH_12": {"members": ("name", "title", "role")},
        "ARCH_18": {"metrics": ("number", "label", "desc")},
        "ARCH_23": {"risks": ("level", "title", "desc", "impact", "probability", "response", "prevent", "owner", "timeline")},
        "ARCH_24": {"pillars": ("en_title", "cn_title", "slogan", "details", "commitment")},
        "ARCH_33": {"honors": ("badge", "title", "org", "metric")},
        "ARCH_06": {"stages": ("phase", "title", "desc")},
        "ARCH_25": {"steps": ("phase", "title", "subtitle", "actions", "deliverable", "duration")},
        "ARCH_27": {"steps": ("ver", "title", "desc")},
        "ARCH_28": {"gates": ("gate", "title")},
        "ARCH_30": {"milestones": ("year", "title", "desc")},
        "ARCH_26": {"stages": ("stage", "value", "desc")},
        "ARCH_09": {"modules": ("title", "desc")},
        "ARCH_34": {"partners": ("category", "title", "desc")},
        "ARCH_08": {"layers": ("layer_name", "headline", "modules")},
        "ARCH_31": {"pillars": ("title", "desc")},
        "ARCH_14": {"nodes": ("title", "desc")},
        "ARCH_32": {"nodes": ("title", "desc")},
    }
    if arch == "ARCH_06_CONCENTRIC_HUB":
        required_rows = {"nodes": ("title", "desc")}
    else:
        required_rows = next((fields for prefix, fields in row_fields.items()
                              if arch.startswith(prefix)), {})
    for key, fields in required_rows.items():
        for index, row in enumerate(data.get(key, [])):
            if not isinstance(row, dict):
                raise ValueError(f"{arch}.{key}[{index}] must be an object with source-backed fields")
            for field in fields:
                alternatives = field.split("|")
                if not any(row.get(option) not in (None, "", []) for option in alternatives):
                    raise ValueError(f"{arch}.{key}[{index}] is missing {field}")
    if arch.startswith("ARCH_25"):
        for index, step in enumerate(data["steps"]):
            actions = step["actions"]
            if not isinstance(actions, list) or not actions or len(actions) > 3:
                raise ValueError(f"ARCH_25.steps[{index}].actions needs a short source-backed list")
    if arch.startswith("ARCH_17"):
        for index, item in enumerate(data["slices"]):
            if not isinstance(item, dict) or not item.get("label") or item.get("value") is None:
                raise ValueError(f"ARCH_17.slices[{index}] needs a source-backed label and value")
    if arch in ("ARCH_16_CHART_BAR_TREND", "ARCH_16_BAR_CHART", "ARCH_16_CHART_TREND"):
        if not data["series"] or not data["categories"] or not data["summary_bullets"]:
            raise ValueError(f"{arch} requires categories, populated series, and evidence-based insights")
        for index, item in enumerate(data["series"]):
            if not isinstance(item, dict) or not item.get("name") or not item.get("values"):
                raise ValueError(f"{arch}.series[{index}] needs a name and values")
            if len(data["categories"]) != len(item["values"]):
                raise ValueError(f"{arch}.series[{index}] values must match its category count")
    if arch.startswith("ARCH_16_RICH_CHART") and not (data.get("insights") or data.get("bullets")):
        raise ValueError("ARCH_16_RICH_CHART requires evidence-based insights or bullets")
    if arch.startswith("ARCH_29"):
        for index, row in enumerate(data["tasks"]):
            if not isinstance(row, list) or len(row) != 6 or not row[0] or not row[1]:
                raise ValueError(f"ARCH_29.tasks[{index}] needs a task, owner, and all time-period cells")
    if arch.startswith("ARCH_20"):
        for field in ("strengths", "weaknesses", "opportunities", "threats"):
            if len(data[field]) > 3:
                raise ValueError(f"ARCH_20.{field} has more points than the quadrant displays")
    if arch.startswith(("ARCH_16", "ARCH_17")):
        categories = data.get("categories")
        for series in data.get("series", []):
            if not isinstance(series, dict) or not series.get("values"):
                raise ValueError(f"{arch} data series needs source-backed values")
            if categories is not None and len(categories) != len(series["values"]):
                raise ValueError(f"{arch} categories and series do not match")

    if arch.startswith("ARCH_16") and chart_kind == "radar":
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

    if arch.startswith("ARCH_16") and not data.get("full_width", False):
        insight_content = data.get("insights") or data.get("bullets")
        if arch in ("ARCH_16_CHART_BAR_TREND", "ARCH_16_BAR_CHART", "ARCH_16_CHART_TREND"):
            insight_content = insight_content or data.get("summary_bullets")
        if not insight_content:
            raise ValueError(f"{arch} requires source-backed insights for its insight panel")


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
        # Detect if master slide already contains the official CHINT logo/badge
        self.has_master_logo = any(
            s.shape_type == 13 and s.left > Inches(10)
            for master in self.prs.slide_masters
            for s in master.shapes
        )

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
        if not 1 <= len(items) <= 12:
            raise ValueError("The CHINT contents page supports up to 12 readable entries. Condense or group the section names to keep one page.")

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
        """Engine 1: Master Frames (Cover, TOC, Chapter, Closing, Contact)"""
        if arch.startswith("ARCH_01"):
            cover_bg = self._find_media("cover_26_bg")
            if cover_bg:
                slide.shapes.add_picture(cover_bg, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
            else:
                cover_img = os.path.join(self.media_dir, "image2.jpeg")
                if os.path.exists(cover_img):
                    slide.shapes.add_picture(cover_img, Inches(0), Inches(0), Inches(13.333), Inches(7.5))

            bar1 = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(3.93), Inches(4.85), Inches(9.4), Inches(1.05))
            bar1.fill.solid()
            bar1.fill.fore_color.rgb = C_BLUE
            bar1.line.fill.background()
            
            tb_t = slide.shapes.add_textbox(Inches(4.1), Inches(4.95), Inches(9.0), Inches(0.85))
            tf_t = tb_t.text_frame
            tf_t.word_wrap = True
            set_para(tf_t.paragraphs[0], s_data.get("title", "演示文稿标题"), font_size=28, bold=True, color_rgb=C_WHITE)

            bar2 = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(3.93), Inches(5.90), Inches(9.4), Inches(0.42))
            bar2.fill.solid()
            bar2.fill.fore_color.rgb = C_CYAN
            bar2.line.fill.background()

            tb_sub = slide.shapes.add_textbox(Inches(4.1), Inches(5.92), Inches(9.0), Inches(0.38))
            tf_sub = tb_sub.text_frame
            tf_sub.word_wrap = True
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
                font_size = 13
                measured = text_width_in(cover_line, font_size, shell_font_path())
                while measured is not None and measured > 8.8 and font_size > 8:
                    font_size -= 0.5
                    measured = text_width_in(cover_line, font_size, shell_font_path())
                if measured is not None and measured > 8.8:
                    raise ValueError("Cover subtitle, date, and author do not fit the template; shorten the supplied text")
                set_para(tf_sub.paragraphs[0], cover_line, font_size=font_size,
                         bold=False, color_rgb=C_WHITE)

        elif arch.startswith("ARCH_02"):
            raise RuntimeError("ARCH_02 must use the template-aware single-page contents renderer")

        elif arch == "ARCH_03_CHAPTER":
            # Chapter dividers intentionally suppress the template's master badge.
            slide._element.set("showMasterSp", "0")
            chap_banner = os.path.join(self.media_dir, "chapter_26_bg_clean.jpg")
            
            if os.path.exists(chap_banner):
                slide.shapes.add_picture(chap_banner, Inches(0), Inches(1.71), Inches(13.333), Inches(3.42))
            else:
                band = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(1.71), Inches(13.333), Inches(3.42))
                band.fill.solid()
                band.fill.fore_color.rgb = C_BLUE
                band.line.fill.background()

            line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(5.13), Inches(13.333), Inches(0.06))
            line.fill.solid()
            line.fill.fore_color.rgb = C_CYAN
            line.line.fill.background()

            title_text = s_data.get("title") or s_data.get("headline") or "添加章节标题"
            subtitle_text = s_data.get("subtitle") or s_data.get("category") or ""

            if subtitle_text:
                tb_c = slide.shapes.add_textbox(Inches(1.0), Inches(2.7), Inches(11.33), Inches(1.8))
                tf_c = tb_c.text_frame
                tf_c.word_wrap = True
                set_para(tf_c.paragraphs[0], subtitle_text.upper(), font_size=13, bold=True, color_rgb=C_ICE_BLUE, align=PP_ALIGN.CENTER)
                p_t = tf_c.add_paragraph()
                set_para(p_t, title_text, font_size=32, bold=True, color_rgb=C_WHITE, align=PP_ALIGN.CENTER)
                p_t.space_before = Pt(6)
            else:
                tb_c = slide.shapes.add_textbox(Inches(1.0), Inches(3.0), Inches(11.33), Inches(1.4))
                tf_c = tb_c.text_frame
                tf_c.word_wrap = True
                set_para(tf_c.paragraphs[0], title_text, font_size=32, bold=True, color_rgb=C_WHITE, align=PP_ALIGN.CENTER)

        elif arch.startswith("ARCH_11"):
            closing_bg = self._find_media("closing_26_bg")
            if closing_bg:
                slide.shapes.add_picture(closing_bg, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
            else:
                closing_img = os.path.join(self.media_dir, "image6.jpeg")
                if os.path.exists(closing_img):
                    slide.shapes.add_picture(closing_img, Inches(0), Inches(0), Inches(13.333), Inches(7.5))

                band = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(5.2), Inches(13.333), Inches(0.8))
                band.fill.solid()
                band.fill.fore_color.rgb = C_BLUE
                band.line.fill.background()

                tb_thx = slide.shapes.add_textbox(Inches(1.0), Inches(5.3), Inches(11.33), Inches(0.6))
                set_para(tb_thx.text_frame.paragraphs[0], "THANKS", font_size=28, bold=True, color_rgb=C_WHITE, align=PP_ALIGN.CENTER)

            contact = s_data.get("contact", "")
            if contact:
                tb_sub = slide.shapes.add_textbox(Inches(9.4), Inches(6.42), Inches(3.55), Inches(0.62))
                tb_sub.text_frame.word_wrap = True
                set_para(tb_sub.text_frame.paragraphs[0], contact, font_size=9, bold=False, color_rgb=C_MUTED, align=PP_ALIGN.RIGHT)

            closing_details = []
            for key in ("tagline", "team", "call_to_action"):
                value = s_data.get(key, "")
                if value:
                    if not isinstance(value, str):
                        raise ValueError(f"ARCH_11_CLOSING.{key} must be text")
                    closing_details.append(value.strip())
            closing_line = " · ".join(value for value in closing_details if value)
            if closing_line:
                from core.common import shell_font_path, text_width_in
                font_size = 9
                measured = text_width_in(closing_line, font_size, shell_font_path())
                while measured is not None and measured > 11.0 and font_size > 7:
                    font_size -= 0.5
                    measured = text_width_in(closing_line, font_size, shell_font_path())
                if measured is not None and measured > 11.0:
                    raise ValueError("Closing tagline, team, and call to action do not fit the template; shorten the supplied text")
                detail_box = slide.shapes.add_textbox(Inches(1.0), Inches(5.78), Inches(11.33), Inches(0.18))
                detail_box.text_frame.word_wrap = False
                self._set_tf_margins(detail_box.text_frame, top=0, bottom=0, left=4, right=4)
                set_para(detail_box.text_frame.paragraphs[0], closing_line, font_size=font_size,
                         bold=False, color_rgb=C_WHITE, align=PP_ALIGN.CENTER)

        elif arch.startswith("ARCH_15"):
            self._add_body_master(slide, s_data.get("title", "联系我们与办事处网点"), s_data.get("category", "服务网络"))
            channels = s_data["channels"]
            card_w, card_h, gap_y, top_m = Inches(5.6), Inches(1.1), Inches(0.18), Inches(1.6)
            
            for i, ch in enumerate(channels[:4]):
                cur_top = top_m + i * (card_h + gap_y)
                bg = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), cur_top, card_w, card_h)
                bg.fill.solid()
                bg.fill.fore_color.rgb = C_LIGHT_BG
                bg.line.color.rgb = C_BORDER
                bg.line.width = Pt(1)
                
                ic = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(1.0), cur_top + Inches(0.2), Inches(0.7), Inches(0.7))
                ic.fill.solid()
                ic.fill.fore_color.rgb = C_BLUE_BG
                ic.line.color.rgb = C_BLUE
                ic.line.width = Pt(1)
                tf_ic = ic.text_frame
                self._set_tf_margins(tf_ic, top=2, bottom=2, left=2, right=2)
                set_para(tf_ic.paragraphs[0], ch.get("icon_label", "服务"), font_size=11, bold=True, color_rgb=C_BLUE, align=PP_ALIGN.CENTER)
                
                tb_c = slide.shapes.add_textbox(Inches(1.85), cur_top + Inches(0.12), card_w - Inches(1.2), Inches(0.85))
                tf_c = tb_c.text_frame
                tf_c.word_wrap = True
                self._set_tf_margins(tf_c, top=6, bottom=6, left=6, right=6)
                set_para(tf_c.paragraphs[0], ch.get("title", ""), font_size=13.5, bold=True, color_rgb=C_DARK)
                p_desc = tf_c.add_paragraph()
                set_para(p_desc, ch.get("desc", ""), font_size=11, bold=False, color_rgb=C_MUTED)
                p_desc.space_before = Pt(4)
                
            right_w = Inches(5.8)
            right_bg = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.73), top_m, right_w, Inches(5.0))
            right_bg.fill.solid()
            right_bg.fill.fore_color.rgb = C_LIGHT_BG
            right_bg.line.color.rgb = C_BORDER
            right_bg.line.width = Pt(1)
            
            h_bar = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.73), top_m, right_w, Inches(0.7))
            h_bar.fill.solid()
            h_bar.fill.fore_color.rgb = C_CARD_HEADER_BG
            h_bar.line.fill.background()
            tf_hbar = h_bar.text_frame
            self._set_tf_margins(tf_hbar, top=4, bottom=4, left=8, right=8)
            set_para(tf_hbar.paragraphs[0], s_data.get("directory_title", "主要大区办事处与分支机构"), font_size=14, bold=True, color_rgb=C_BLUE, align=PP_ALIGN.CENTER)
            
            tb_r = slide.shapes.add_textbox(Inches(7.0), top_m + Inches(0.85), right_w - Inches(0.5), Inches(3.9))
            tf_r = tb_r.text_frame
            tf_r.word_wrap = True
            self._set_tf_margins(tf_r, top=8, bottom=8, left=8, right=8)
            offices = s_data["offices"]
            for j, o in enumerate(offices):
                p = tf_r.paragraphs[0] if j == 0 else tf_r.add_paragraph()
                set_para(p, f"• {o}", font_size=11.5, bold=False, color_rgb=C_DARK)
                p.space_before = Pt(8)

    def _render_dual_pane_split(self, slide, s_data: Dict[str, Any], arch: str):
        """Engine 2: 50:50 Dual-Pane Comparison (ARCH_07, ARCH_21, ARCH_22)"""
        self._add_body_master(slide, s_data.get("title", ""), s_data.get("category", ""))
        box_w, box_h, top_m = Inches(5.65), Inches(5.0), Inches(1.6)
        
        # Configure theme parameters based on archetype
        if arch.startswith("ARCH_07"):
            left_title = s_data.get("pain_header", "核心挑战与痛点剖析")
            left_items = s_data.get("pain_points", [])
            left_bg_color, left_border_color, left_title_color = C_RED_BG, RGBColor(255, 180, 180), C_RED_TEXT
            left_summary_title = "【核心挑战瓶颈】"
            left_summary_text = s_data.get("pain_summary", "传统电气运维与配电系统缺乏统一协同，存在安全与成本隐患")
            
            right_title = s_data.get("solution_header", "针对性应对解决方案")
            right_items = s_data.get("solutions", [])
            right_bg_color, right_border_color, right_title_color = C_BLUE_BG, RGBColor(180, 210, 255), C_BLUE
            right_summary_title = "【针对性破局方案】"
            right_summary_text = s_data.get("solution_summary", "构建正泰一站式智慧低压配电综合方案，实现全局数智化协同")
        elif arch.startswith("ARCH_21"):
            left_title = s_data.get("before_title", "传统模式 / 改造前 (Before)")
            left_items = s_data.get("before_items", [
                "人工巡检维护，响应周期长达 24-48 小时",
                "数据孤岛严重，系统互通性不足",
                "能效粗放管理，无实时负荷监测",
                "运维成本高昂，故障后被动抢修"
            ])
            left_bg_color, left_border_color, left_title_color = C_LIGHT_BG, C_BORDER, C_MUTED
            left_summary_title = "【传统模式痛点瓶颈】"
            left_summary_text = s_data.get("before_summary", "故障平均响应 > 24h | 年均额外运维成本超 120 万元 | 故障被动抢修")
            
            right_title = s_data.get("after_title", "正泰智能方案 / 升级后 (After)")
            right_items = s_data.get("after_items", [
                "AI 预测性维护，分钟级告警与远程诊断",
                "统一云边物联底座，设备无缝接入",
                "精细化动态节能，综合能耗降低 30%+",
                "全生命周期资产数字化管理"
            ])
            right_bg_color, right_border_color, right_title_color = C_BLUE_BG, RGBColor(180, 210, 255), C_BLUE
            right_summary_title = "【数字化升级核心价值】"
            right_summary_text = s_data.get("after_summary", "综合能耗降低 30%+ | 设备故障预警率 99.5% | 全域资产数字孪生")
        else: # ARCH_22
            left_title = s_data.get("problem_title", "当前现存主要问题与短板")
            left_items = s_data.get("problems", [
                "交付瓶颈：非标定制订单响应周期偏长",
                "供应链波动：部分关键电子元器件供货承压",
                "数字化渗透率不足：部分一线现场依赖纸质记录"
            ])
            left_bg_color, left_border_color, left_title_color = C_RED_BG, RGBColor(255, 180, 180), C_RED_TEXT
            left_summary_title = "【现存短板影响】"
            left_summary_text = s_data.get("problem_summary", "影响重大项目敏捷履约，面临供应链波动与现场协同交付风险")
            
            right_title = s_data.get("improve_title", "系统化改善对策与推进计划")
            right_items = s_data.get("improvements", [
                "柔性制造升级：交付周期压缩至 48 小时以内",
                "战略安全库存：建立核心物料双供应商机制",
                "移动数字赋能：推行移动 APP 巡检与电子看板"
            ])
            right_bg_color, right_border_color, right_title_color = C_BLUE_BG, RGBColor(180, 210, 255), C_BLUE
            right_summary_title = "【改进目标与落地收益】"
            right_summary_text = s_data.get("improve_summary", "交付准时率提升至 99.2% | 核心物料双供覆盖率 100% | 48h 极速交付")

        # --- Left Pane ---
        l_bg = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), top_m, box_w, box_h)
        l_bg.fill.solid()
        l_bg.fill.fore_color.rgb = left_bg_color
        l_bg.line.color.rgb = left_border_color
        l_bg.line.width = Pt(1.2)

        # Left Header Banner
        l_hdr = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), top_m, box_w, Inches(0.7))
        l_hdr.fill.solid()
        l_hdr.fill.fore_color.rgb = RGBColor(255, 240, 240) if left_bg_color == C_RED_BG else C_CARD_HEADER_BG
        l_hdr.line.fill.background()

        tb_lh = slide.shapes.add_textbox(Inches(1.0), top_m + Inches(0.1), box_w - Inches(0.4), Inches(0.5))
        tf_lh = tb_lh.text_frame
        tf_lh.word_wrap = True
        self._set_tf_margins(tf_lh, top=4, bottom=4, left=4, right=4)
        set_para(tf_lh.paragraphs[0], left_title, font_size=14, bold=True, color_rgb=left_title_color)

        # Left Body Content
        tb_lb = slide.shapes.add_textbox(Inches(1.0), top_m + Inches(0.85), box_w - Inches(0.4), Inches(2.65))
        tf_lb = tb_lb.text_frame
        tf_lb.word_wrap = True
        self._set_tf_margins(tf_lb, top=6, bottom=6, left=6, right=6)
        spacing_l = Pt(20) if len(left_items) <= 3 else Pt(14)
        for j, item in enumerate(left_items):
            p = tf_lb.paragraphs[0] if j == 0 else tf_lb.add_paragraph()
            p.space_before = spacing_l
            p.space_after = Pt(2)
            if "：" in item:
                lead, rest = item.split("：", 1)
                r_lead = p.add_run()
                r_lead.text = f"• {lead}："
                r_lead.font.name = "正泰拓新体"
                r_lead.font.size = Pt(12.0)
                r_lead.font.bold = True
                r_lead.font.color.rgb = C_DARK
                
                r_rest = p.add_run()
                r_rest.text = rest
                r_rest.font.name = "正泰拓新体"
                r_rest.font.size = Pt(11.0)
                r_rest.font.bold = False
                r_rest.font.color.rgb = C_DARK
            elif ":" in item:
                lead, rest = item.split(":", 1)
                r_lead = p.add_run()
                r_lead.text = f"• {lead}: "
                r_lead.font.name = "正泰拓新体"
                r_lead.font.size = Pt(12.0)
                r_lead.font.bold = True
                r_lead.font.color.rgb = C_DARK
                
                r_rest = p.add_run()
                r_rest.text = rest
                r_rest.font.name = "正泰拓新体"
                r_rest.font.size = Pt(11.0)
                r_rest.font.bold = False
                r_rest.font.color.rgb = C_DARK
            else:
                f_auto = calc_autofit_fontsize(item, base_size=11.5, min_size=9.5, threshold_len=26)
                set_para(p, f"• {item}", font_size=f_auto, bold=False, color_rgb=C_DARK)

        # Left Bottom Summary Box
        l_bot_box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.0), top_m + Inches(3.6), box_w - Inches(0.4), Inches(1.15))
        l_bot_box.fill.solid()
        l_bot_box.fill.fore_color.rgb = C_WHITE
        l_bot_box.line.color.rgb = left_border_color
        l_bot_box.line.width = Pt(1)
        
        tb_l_bot = slide.shapes.add_textbox(Inches(1.1), top_m + Inches(3.65), box_w - Inches(0.6), Inches(1.05))
        tf_l_bot = tb_l_bot.text_frame
        tf_l_bot.word_wrap = True
        self._set_tf_margins(tf_l_bot, top=4, bottom=4, left=4, right=4)
        set_para(tf_l_bot.paragraphs[0], left_summary_title, font_size=11, bold=True, color_rgb=left_title_color)
        p_l_bs = tf_l_bot.add_paragraph()
        f_sauto = calc_autofit_fontsize(left_summary_text, base_size=10.0, min_size=8.5, threshold_len=30)
        set_para(p_l_bs, left_summary_text, font_size=f_sauto, bold=False, color_rgb=C_DARK)
        p_l_bs.space_before = Pt(3)

        # --- Right Pane ---
        r_bg = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.88), top_m, box_w, box_h)
        r_bg.fill.solid()
        r_bg.fill.fore_color.rgb = right_bg_color
        r_bg.line.color.rgb = right_border_color
        r_bg.line.width = Pt(1.2)

        # Right Header Banner
        r_hdr = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.88), top_m, box_w, Inches(0.7))
        r_hdr.fill.solid()
        r_hdr.fill.fore_color.rgb = C_CARD_HEADER_BG
        r_hdr.line.fill.background()

        tb_rh = slide.shapes.add_textbox(Inches(7.08), top_m + Inches(0.1), box_w - Inches(0.4), Inches(0.5))
        tf_rh = tb_rh.text_frame
        tf_rh.word_wrap = True
        self._set_tf_margins(tf_rh, top=4, bottom=4, left=4, right=4)
        set_para(tf_rh.paragraphs[0], right_title, font_size=14, bold=True, color_rgb=right_title_color)

        # Right Body Content
        tb_rb = slide.shapes.add_textbox(Inches(7.08), top_m + Inches(0.85), box_w - Inches(0.4), Inches(2.65))
        tf_rb = tb_rb.text_frame
        tf_rb.word_wrap = True
        self._set_tf_margins(tf_rb, top=6, bottom=6, left=6, right=6)
        spacing_r = Pt(20) if len(right_items) <= 3 else Pt(14)
        for j, item in enumerate(right_items):
            p = tf_rb.paragraphs[0] if j == 0 else tf_rb.add_paragraph()
            p.space_before = spacing_r
            p.space_after = Pt(2)
            if "：" in item:
                lead, rest = item.split("：", 1)
                r_lead = p.add_run()
                r_lead.text = f"• {lead}："
                r_lead.font.name = "正泰拓新体"
                r_lead.font.size = Pt(12.0)
                r_lead.font.bold = True
                r_lead.font.color.rgb = C_DARK
                
                r_rest = p.add_run()
                r_rest.text = rest
                r_rest.font.name = "正泰拓新体"
                r_rest.font.size = Pt(11.0)
                r_rest.font.bold = False
                r_rest.font.color.rgb = C_DARK
            elif ":" in item:
                lead, rest = item.split(":", 1)
                r_lead = p.add_run()
                r_lead.text = f"• {lead}: "
                r_lead.font.name = "正泰拓新体"
                r_lead.font.size = Pt(12.0)
                r_lead.font.bold = True
                r_lead.font.color.rgb = C_DARK
                
                r_rest = p.add_run()
                r_rest.text = rest
                r_rest.font.name = "正泰拓新体"
                r_rest.font.size = Pt(11.0)
                r_rest.font.bold = False
                r_rest.font.color.rgb = C_DARK
            else:
                f_auto = calc_autofit_fontsize(item, base_size=11.5, min_size=9.5, threshold_len=26)
                set_para(p, f"• {item}", font_size=f_auto, bold=False, color_rgb=C_DARK)

        # Right Bottom Summary Box
        r_bot_box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.08), top_m + Inches(3.6), box_w - Inches(0.4), Inches(1.15))
        r_bot_box.fill.solid()
        r_bot_box.fill.fore_color.rgb = C_WHITE
        r_bot_box.line.color.rgb = right_border_color
        r_bot_box.line.width = Pt(1)
        
        tb_r_bot = slide.shapes.add_textbox(Inches(7.18), top_m + Inches(3.65), box_w - Inches(0.6), Inches(1.05))
        tf_r_bot = tb_r_bot.text_frame
        tf_r_bot.word_wrap = True
        self._set_tf_margins(tf_r_bot, top=4, bottom=4, left=4, right=4)
        set_para(tf_r_bot.paragraphs[0], right_summary_title, font_size=11, bold=True, color_rgb=right_title_color)
        p_r_bs = tf_r_bot.add_paragraph()
        f_sauto_r = calc_autofit_fontsize(right_summary_text, base_size=10.0, min_size=8.5, threshold_len=30)
        set_para(p_r_bs, right_summary_text, font_size=f_sauto_r, bold=False, color_rgb=C_DARK)
        p_r_bs.space_before = Pt(3)

    def _render_hero_split_pane(self, slide, s_data: Dict[str, Any], arch: str):
        """Engine 3: Asymmetric Hero Split (ARCH_10, ARCH_13, ARCH_19)"""
        self._add_body_master(slide, s_data.get("title", ""), s_data.get("category", ""))
        top_m, box_h = Inches(1.6), Inches(5.0)
        left_w, right_w = Inches(4.5), Inches(6.8)

        # Left Hero Card (Deep Blue / Electric Blue)
        left_bg = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), top_m, left_w, box_h)
        left_bg.fill.solid()
        left_bg.fill.fore_color.rgb = C_DEEP_BLUE if arch == "ARCH_13_GLOBAL_FOOTPRINT" else C_BLUE
        left_bg.line.fill.background()

        tb_l = slide.shapes.add_textbox(Inches(1.0), top_m + Inches(0.35), left_w - Inches(0.4), box_h - Inches(0.7))
        tf_l = tb_l.text_frame
        tf_l.word_wrap = True
        self._set_tf_margins(tf_l, top=8, bottom=8, left=8, right=8)

        if arch.startswith("ARCH_10"):
            set_para(tf_l.paragraphs[0], s_data.get("client_name", "标杆客户示范项目"), font_size=16, bold=True, color_rgb=C_WHITE)
            p_val = tf_l.add_paragraph()
            set_para(p_val, s_data.get("hero_metric", "核心成效提升"), font_size=34, bold=True, color_rgb=C_ICE_BLUE)
            p_val.space_before = Pt(14)
            p_val.space_after = Pt(4)
            p_sub = tf_l.add_paragraph()
            set_para(p_sub, s_data.get("hero_desc", "系统化解决方案端到端落地实施"), font_size=12, bold=False, color_rgb=C_WHITE)
            p_sub.space_before = Pt(8)
        elif arch.startswith("ARCH_13"):
            set_para(tf_l.paragraphs[0], s_data.get("coverage_title", "全球业务覆盖"), font_size=18, bold=True, color_rgb=C_WHITE)
            stats = s_data.get("stats", [("140+", "覆盖国家与地区"), ("30,000+", "全球员工总数"), ("4 大", "全球研发中心")])
            for val, lbl in stats:
                p1 = tf_l.add_paragraph()
                set_para(p1, val, font_size=30, bold=True, color_rgb=C_ICE_BLUE)
                p1.space_before = Pt(12)
                p2 = tf_l.add_paragraph()
                set_para(p2, lbl, font_size=11, bold=False, color_rgb=C_WHITE)
                p2.space_before = Pt(2)
        else: # ARCH_19
            set_para(tf_l.paragraphs[0], s_data.get("hero_label", "年度核心战果突破"), font_size=14, bold=True, color_rgb=C_ICE_BLUE)
            p_num = tf_l.add_paragraph()
            set_para(p_num, s_data.get("hero_number", "9,000 W+"), font_size=40, bold=True, color_rgb=C_WHITE)
            p_num.space_before = Pt(12)
            p_unit = tf_l.add_paragraph()
            set_para(p_unit, s_data.get("hero_unit", "智能终端设备累计安全运行量"), font_size=13, bold=False, color_rgb=C_ICE_BLUE)
            p_unit.space_before = Pt(4)
            p_desc = tf_l.add_paragraph()
            set_para(p_desc, s_data.get("hero_desc", "广泛应用于电力、新能源及工业基础设施。"), font_size=11, bold=False, color_rgb=C_WHITE)
            p_desc.space_before = Pt(14)

        # Right Container Card
        right_bg = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(5.73), top_m, right_w, box_h)
        right_bg.fill.solid()
        right_bg.fill.fore_color.rgb = C_LIGHT_BG
        right_bg.line.color.rgb = C_BORDER
        right_bg.line.width = Pt(1)

        tb_r = slide.shapes.add_textbox(Inches(6.0), top_m + Inches(0.35), right_w - Inches(0.5), box_h - Inches(0.7))
        tf_r = tb_r.text_frame
        tf_r.word_wrap = True
        self._set_tf_margins(tf_r, top=8, bottom=8, left=8, right=8)

        if arch.startswith("ARCH_13"):
            offices = s_data["offices"]
            set_para(tf_r.paragraphs[0], s_data.get("network_title", "主要区域总部与研发网点"), font_size=15, bold=True, color_rgb=C_BLUE)
            for o in offices:
                p = tf_r.add_paragraph()
                set_para(p, f"• {o}", font_size=12, bold=False, color_rgb=C_DARK)
                p.space_before = Pt(10)
                p.space_after = Pt(2)
        else:
            bullets = s_data["bullets"]
            set_para(tf_r.paragraphs[0], s_data.get("narrative_title", "核心价值与项目实践拆解"), font_size=15, bold=True, color_rgb=C_BLUE)
            for j, b in enumerate(bullets):
                p = tf_r.add_paragraph()
                set_para(p, f"• {b}", font_size=12, bold=False, color_rgb=C_DARK)
                p.space_before = Pt(12)
                p.space_after = Pt(2)

    def _render_n_column_card_grid(self, slide, s_data: Dict[str, Any], arch: str):
        """Engine 4: Vertical N-Column Card Grid with Dynamic Reflow (ARCH_04, ARCH_05, ARCH_12, ARCH_18, ARCH_24, ARCH_23, ARCH_33)"""
        self._add_body_master(slide, s_data.get("title", ""), s_data.get("category", ""))
        top_m, card_h, left_m = Inches(1.6), Inches(5.0), Inches(0.8)

        if arch.startswith("ARCH_04"):
            cards = s_data.get("kpi_cards", [])
            num_c = max(1, min(len(cards), 4)) if cards else 3
            gap = Inches(0.25) if num_c >= 4 else Inches(0.4)
            card_w = Inches((11.73 - (num_c - 1) * gap.inches) / num_c)
            band_h = Inches(1.35) if num_c >= 4 else Inches(1.5)
            num_fsize = 26 if num_c >= 4 else 32

            for i, card in enumerate(cards[:num_c]):
                cur_left = left_m + i * (card_w + gap)
                bg = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cur_left, top_m, card_w, card_h)
                bg.fill.solid()
                bg.fill.fore_color.rgb = C_LIGHT_BG
                bg.line.color.rgb = C_BORDER
                bg.line.width = Pt(1)

                band = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cur_left, top_m, card_w, band_h)
                band.fill.solid()
                band.fill.fore_color.rgb = C_BLUE
                band.line.fill.background()

                tb_band = slide.shapes.add_textbox(cur_left, top_m + Inches(0.12), card_w, band_h - Inches(0.2))
                tf_band = tb_band.text_frame
                tf_band.word_wrap = True
                self._set_tf_margins(tf_band, top=6, bottom=6, left=6, right=6)
                set_para(tf_band.paragraphs[0], card.get("number", card.get("metric", "")), font_size=num_fsize, bold=True, color_rgb=C_WHITE, align=PP_ALIGN.CENTER)
                p_lbl = tf_band.add_paragraph()
                set_para(p_lbl, card.get("label", ""), font_size=12 if num_c >= 4 else 13, bold=True, color_rgb=C_ICE_BLUE, align=PP_ALIGN.CENTER)
                p_lbl.space_before = Pt(3)

                details = card.get("details", card.get("bullets", []))
                tb_b = slide.shapes.add_textbox(cur_left + Inches(0.15), top_m + band_h + Inches(0.15), card_w - Inches(0.3), card_h - band_h - Inches(0.3))
                tf_b = tb_b.text_frame
                tf_b.word_wrap = True
                self._set_tf_margins(tf_b, top=6, bottom=6, left=6, right=6)
                f_detail = 10.5 if num_c >= 4 else 11.5
                for j, b in enumerate(details):
                    p = tf_b.paragraphs[0] if j == 0 else tf_b.add_paragraph()
                    f_auto = calc_autofit_fontsize(b, base_size=f_detail, min_size=9.0, threshold_len=30)
                    set_para(p, f"• {b}", font_size=f_auto, bold=False, color_rgb=C_DARK)
                    p.space_before = Pt(6 if num_c >= 4 else 8)
                    p.space_after = Pt(2)

        elif arch.startswith("ARCH_05"):
            cols = s_data.get("columns", [])
            num_cols = max(1, min(len(cols), 5)) if cols else 3
            gap = Inches(0.2) if num_cols >= 5 else (Inches(0.25) if num_cols == 4 else Inches(0.35))
            card_w = Inches((11.73 - (num_cols - 1) * gap.inches) / num_cols)
            f_hdr = 11.5 if num_cols >= 5 else (12.5 if num_cols == 4 else 13.5)
            f_body = 9.5 if num_cols >= 5 else (10.5 if num_cols == 4 else 11.5)

            for i, col in enumerate(cols[:num_cols]):
                cur_left = left_m + i * (card_w + gap)
                bg = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cur_left, top_m, card_w, card_h)
                bg.fill.solid()
                bg.fill.fore_color.rgb = C_LIGHT_BG
                bg.line.color.rgb = C_BORDER
                bg.line.width = Pt(1)

                h_bg = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cur_left, top_m, card_w, Inches(0.65))
                h_bg.fill.solid()
                h_bg.fill.fore_color.rgb = C_CARD_HEADER_BG
                h_bg.line.fill.background()

                tb_h = slide.shapes.add_textbox(cur_left + Inches(0.1), top_m + Inches(0.1), card_w - Inches(0.2), Inches(0.5))
                tf_h = tb_h.text_frame
                tf_h.word_wrap = True
                self._set_tf_margins(tf_h, top=4, bottom=4, left=6, right=6)
                set_para(tf_h.paragraphs[0], col.get("header", ""), font_size=f_hdr, bold=True, color_rgb=C_BLUE, align=PP_ALIGN.CENTER)

                bullets = col.get("bullets", [])
                tb_b = slide.shapes.add_textbox(cur_left + Inches(0.15), top_m + Inches(0.8), card_w - Inches(0.3), card_h - Inches(0.95))
                tf_b = tb_b.text_frame
                tf_b.word_wrap = True
                self._set_tf_margins(tf_b, top=6, bottom=6, left=6, right=6)
                for j, b in enumerate(bullets):
                    p = tf_b.paragraphs[0] if j == 0 else tf_b.add_paragraph()
                    f_auto = calc_autofit_fontsize(b, base_size=f_body, min_size=8.5, threshold_len=25)
                    set_para(p, f"• {b}", font_size=f_auto, bold=False, color_rgb=C_DARK)
                    p.space_before = Pt(5 if num_cols >= 5 else 7)
                    p.space_after = Pt(2)

        elif arch.startswith("ARCH_12"):
            members = s_data.get("members", [])
            num_m = max(1, min(len(members), 5)) if members else 3
            gap = Inches(0.2) if num_m >= 5 else (Inches(0.25) if num_m == 4 else Inches(0.35))
            card_w = Inches((11.73 - (num_m - 1) * gap.inches) / num_m)
            f_name = 13.0 if num_m >= 5 else (14.0 if num_m == 4 else 15.5)
            f_cred = 9.5 if num_m >= 5 else (10.0 if num_m == 4 else 10.5)

            for i, m in enumerate(members[:num_m]):
                cur_left = left_m + i * (card_w + gap)
                bg = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cur_left, top_m, card_w, card_h)
                bg.fill.solid()
                bg.fill.fore_color.rgb = C_LIGHT_BG
                bg.line.color.rgb = C_BORDER
                bg.line.width = Pt(1)

                pill = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cur_left + Inches(0.15), top_m + Inches(0.25), card_w - Inches(0.3), Inches(0.42))
                pill.fill.solid()
                pill.fill.fore_color.rgb = C_BLUE
                pill.line.fill.background()
                tf_pill = pill.text_frame
                self._set_tf_margins(tf_pill, top=2, bottom=2, left=4, right=4)
                set_para(tf_pill.paragraphs[0], m.get("role", "核心成员"), font_size=10.5 if num_m >= 5 else 11, bold=True, color_rgb=C_WHITE, align=PP_ALIGN.CENTER)

                tb = slide.shapes.add_textbox(cur_left + Inches(0.15), top_m + Inches(0.8), card_w - Inches(0.3), card_h - Inches(0.95))
                tf = tb.text_frame
                tf.word_wrap = True
                self._set_tf_margins(tf, top=6, bottom=6, left=6, right=6)
                set_para(tf.paragraphs[0], m.get("name", ""), font_size=f_name, bold=True, color_rgb=C_DARK, align=PP_ALIGN.CENTER)
                p_title = tf.add_paragraph()
                set_para(p_title, m.get("title", ""), font_size=10.5 if num_m >= 5 else 11, bold=False, color_rgb=C_BLUE, align=PP_ALIGN.CENTER)
                p_title.space_before = Pt(3)

                for b in m.get("credentials", []):
                    p_c = tf.add_paragraph()
                    f_auto = calc_autofit_fontsize(b, base_size=f_cred, min_size=8.5, threshold_len=20)
                    set_para(p_c, f"• {b}", font_size=f_auto, bold=False, color_rgb=C_MUTED)
                    p_c.space_before = Pt(4 if num_m >= 5 else 6)
                    p_c.space_after = Pt(2)

        elif arch.startswith("ARCH_18"):
            metrics = s_data.get("metrics", [
                {"number": "99.98%", "label": "核心供电可靠率", "trend": "+0.45% YoY", "desc": "关键回路连续安全运行 3000+ 天"},
                {"number": "32.5%", "label": "综合综合节能率", "trend": "+5.2% 提升", "desc": "全周期智慧能效管理降耗"},
                {"number": "140+", "label": "全球服务国家与地区", "trend": "+12 区域拓展", "desc": "本地化营销与服务网络全覆盖"},
                {"number": "48 h", "label": "定制化交付周期", "trend": "-35% 提速", "desc": "智能制造柔性产线极速交付"}
            ])
            num_m = max(1, min(len(metrics), 5))
            gap = Inches(0.2) if num_m >= 5 else (Inches(0.25) if num_m == 4 else Inches(0.35))
            card_w = Inches((11.73 - (num_m - 1) * gap.inches) / num_m)
            f_num = 26 if num_m >= 5 else (28 if num_m == 4 else 32)

            for i, m in enumerate(metrics[:num_m]):
                cur_left = left_m + i * (card_w + gap)
                bg = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cur_left, top_m, card_w, card_h)
                bg.fill.solid()
                bg.fill.fore_color.rgb = C_LIGHT_BG
                bg.line.color.rgb = C_BORDER
                bg.line.width = Pt(1)

                top_bar = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cur_left + Inches(0.15), top_m + Inches(0.15), card_w - Inches(0.3), Inches(0.08))
                top_bar.fill.solid()
                top_bar.fill.fore_color.rgb = C_BLUE
                top_bar.line.fill.background()

                tb_num = slide.shapes.add_textbox(cur_left + Inches(0.1), top_m + Inches(0.35), card_w - Inches(0.2), Inches(1.1))
                tf_num = tb_num.text_frame
                tf_num.word_wrap = True
                self._set_tf_margins(tf_num, top=6, bottom=6, left=6, right=6)
                set_para(tf_num.paragraphs[0], m.get("number", ""), font_size=f_num, bold=True, color_rgb=C_BLUE, align=PP_ALIGN.CENTER)

                trend = m.get("trend", "")
                if trend:
                    pill = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cur_left + Inches(0.2), top_m + Inches(1.5), card_w - Inches(0.4), Inches(0.36))
                    pill.fill.solid()
                    pill.fill.fore_color.rgb = C_GREEN_BG if "+" in trend or "提升" in trend else C_RED_BG
                    pill.line.fill.background()
                    tf_p = pill.text_frame
                    self._set_tf_margins(tf_p, top=2, bottom=2, left=4, right=4)
                    set_para(tf_p.paragraphs[0], trend, font_size=10, bold=True, color_rgb=C_GREEN if "+" in trend or "提升" in trend else C_RED_TEXT, align=PP_ALIGN.CENTER)

                tb_lbl = slide.shapes.add_textbox(cur_left + Inches(0.15), top_m + Inches(1.95), card_w - Inches(0.3), Inches(2.8))
                tf_lbl = tb_lbl.text_frame
                tf_lbl.word_wrap = True
                self._set_tf_margins(tf_lbl, top=6, bottom=6, left=6, right=6)
                set_para(tf_lbl.paragraphs[0], m.get("label", ""), font_size=12.5 if num_m >= 5 else 13.5, bold=True, color_rgb=C_DARK, align=PP_ALIGN.CENTER)
                p_d = tf_lbl.add_paragraph()
                f_desc = calc_autofit_fontsize(m.get("desc", ""), base_size=10.5 if num_m >= 5 else 11.0, min_size=9.0, threshold_len=20)
                set_para(p_d, m.get("desc", ""), font_size=f_desc, bold=False, color_rgb=C_MUTED, align=PP_ALIGN.CENTER)
                p_d.space_before = Pt(6)
                p_d.space_after = Pt(2)

        elif arch.startswith("ARCH_24"):
            pillars = s_data.get("pillars", [
                {"en_title": "MISSION", "cn_title": "企业使命", "slogan": "让电力能源更安全、绿色、便捷、高效", "details": ["以客户为中心，提供高品质智慧能源解决方案", "赋能全球清洁能源转型与工业数智化升级", "推动绿色低碳发展与全生命周期能效服务"], "commitment": "2030 绿色低碳战略承诺  |  赋能全球产业转型"},
                {"en_title": "VISION", "cn_title": "企业愿景", "slogan": "成为全球领先的智慧能源解决方案提供商", "details": ["打造绿色低碳与数字化双轮驱动的产业生态群", "成为备受全球信赖与尊重的可持续发展标杆", "构建开放协同、共生共赢的能源互联网生态"], "commitment": "全球 140+ 国家业务覆盖  |  世界一流品牌"},
                {"en_title": "VALUES", "cn_title": "核心价值观", "slogan": "客户导向、创新驱动、诚信立业、共创共享", "details": ["始终以客户价值创造为一切业务出发点", "坚持科技创新与组织活力，引领行业技术迭代", "恪守诚信合规经营，与全球生态伙伴共创共享"], "commitment": "客户第一  |  创新驱动  |  共赢未来"}
            ])
            num_p = max(1, min(len(pillars), 4))
            gap = Inches(0.25) if num_p >= 4 else Inches(0.4)
            card_w = Inches((11.73 - (num_p - 1) * gap.inches) / num_p)

            for i, p in enumerate(pillars[:num_p]):
                cur_left = left_m + i * (card_w + gap)
                bg = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cur_left, top_m, card_w, card_h)
                bg.fill.solid()
                bg.fill.fore_color.rgb = C_LIGHT_BG
                bg.line.color.rgb = C_BORDER
                bg.line.width = Pt(1)

                # English Pill
                en_pill = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cur_left + Inches(0.15), top_m + Inches(0.2), card_w - Inches(0.3), Inches(0.36))
                en_pill.fill.solid()
                en_pill.fill.fore_color.rgb = C_BLUE_BG
                en_pill.line.fill.background()
                tf_en = en_pill.text_frame
                self._set_tf_margins(tf_en, top=2, bottom=2, left=4, right=4)
                set_para(tf_en.paragraphs[0], p.get("en_title", ""), font_size=10.5 if num_p >= 4 else 11, bold=True, color_rgb=C_BLUE, align=PP_ALIGN.CENTER)

                # Chinese Title
                tb_title = slide.shapes.add_textbox(cur_left + Inches(0.15), top_m + Inches(0.62), card_w - Inches(0.3), Inches(0.45))
                tf_title = tb_title.text_frame
                tf_title.word_wrap = True
                self._set_tf_margins(tf_title, top=2, bottom=2, left=4, right=4)
                set_para(tf_title.paragraphs[0], p.get("cn_title", ""), font_size=16 if num_p >= 4 else 17, bold=True, color_rgb=C_BLUE, align=PP_ALIGN.CENTER)

                # Slogan Card Box
                slog_box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cur_left + Inches(0.12), top_m + Inches(1.15), card_w - Inches(0.24), Inches(0.85))
                slog_box.fill.solid()
                slog_box.fill.fore_color.rgb = C_WHITE
                slog_box.line.color.rgb = RGBColor(180, 210, 255)
                slog_box.line.width = Pt(1)
                tf_slog = slog_box.text_frame
                tf_slog.word_wrap = True
                tf_slog.vertical_anchor = MSO_ANCHOR.MIDDLE
                self._set_tf_margins(tf_slog, top=4, bottom=4, left=6, right=6)
                set_para(tf_slog.paragraphs[0], f"“{p.get('slogan', '')}”", font_size=11 if num_p >= 4 else 12.0, bold=True, color_rgb=C_DARK, align=PP_ALIGN.CENTER)

                # Details / Tenets Box
                tb_det = slide.shapes.add_textbox(cur_left + Inches(0.12), top_m + Inches(2.1), card_w - Inches(0.24), Inches(2.0))
                tf_det = tb_det.text_frame
                tf_det.word_wrap = True
                self._set_tf_margins(tf_det, top=4, bottom=4, left=6, right=6)
                for d_idx, d in enumerate(p.get("details", [])):
                    p_d = tf_det.paragraphs[0] if d_idx == 0 else tf_det.add_paragraph()
                    f_auto = calc_autofit_fontsize(d, base_size=10.0 if num_p >= 4 else 11.0, min_size=8.5, threshold_len=24)
                    set_para(p_d, f"• {d}", font_size=f_auto, bold=False, color_rgb=C_DARK)
                    p_d.space_before = Pt(14)
                    p_d.space_after = Pt(2)

                # Bottom Commitment Tag
                cmt_box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cur_left + Inches(0.12), top_m + Inches(4.2), card_w - Inches(0.24), Inches(0.6))
                cmt_box.fill.solid()
                cmt_box.fill.fore_color.rgb = C_BLUE_BG
                cmt_box.line.color.rgb = RGBColor(180, 210, 255)
                cmt_box.line.width = Pt(1)
                tf_cmt = cmt_box.text_frame
                tf_cmt.word_wrap = True
                tf_cmt.vertical_anchor = MSO_ANCHOR.MIDDLE
                self._set_tf_margins(tf_cmt, top=2, bottom=2, left=4, right=4)
                set_para(tf_cmt.paragraphs[0], p.get("commitment", "2030 绿色低碳战略承诺  |  赋能产业转型"), font_size=9.5 if num_p >= 4 else 10.0, bold=True, color_rgb=C_BLUE, align=PP_ALIGN.CENTER)

        elif arch.startswith("ARCH_23"):
            risks = s_data.get("risks", [
                {"level": "高风险", "title": "技术集成与接口兼容风险", "desc": "异构系统协议标准不统一", "impact": "★★★★★ 极高", "probability": "高 (35%)", "response": "制定标准化网关协议中间件", "prevent": "建立统一物模型标准与跨系统联调机制", "owner": "研发与技术 PMO", "timeline": "T+30天闭环"},
                {"level": "中风险", "title": "工期排程与协同延误", "desc": "涉及多个施工方交叉作业", "impact": "★★★★☆ 显著", "probability": "中 (20%)", "response": "设立联合 PMO 与每日站会机制", "prevent": "推行关键路径甘特图预警与资源动态调配", "owner": "工程管理部", "timeline": "全程常态化"},
                {"level": "低风险", "title": "运维人员操作培训门槛", "desc": "新型数字化系统操作习惯", "impact": "★★☆☆☆ 轻微", "probability": "低 (10%)", "response": "编制图文/视频微课与实操手册", "prevent": "上线模拟演练考核系统，实现持证上岗", "owner": "客户成功部", "timeline": "交付前 2 周"}
            ])
            num_r = max(1, min(len(risks), 4))
            gap = Inches(0.25) if num_r >= 4 else Inches(0.4)
            card_w = Inches((11.73 - (num_r - 1) * gap.inches) / num_r)

            for i, r in enumerate(risks[:num_r]):
                cur_left = left_m + i * (card_w + gap)
                lvl = r.get("level", "中风险")
                lvl_color = C_RED_TEXT if "高" in lvl else (C_BLUE if "低" in lvl else C_ORANGE)
                lvl_bg = C_RED_BG if "高" in lvl else (C_BLUE_BG if "低" in lvl else RGBColor(255, 245, 230))
                
                bg = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cur_left, top_m, card_w, card_h)
                bg.fill.solid()
                bg.fill.fore_color.rgb = C_LIGHT_BG
                bg.line.color.rgb = C_BORDER
                bg.line.width = Pt(1)
                
                # Risk Badge
                badge = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cur_left + Inches(0.15), top_m + Inches(0.2), card_w - Inches(0.3), Inches(0.38))
                badge.fill.solid()
                badge.fill.fore_color.rgb = lvl_bg
                badge.line.color.rgb = lvl_color
                badge.line.width = Pt(1)
                tf_bdg = badge.text_frame
                self._set_tf_margins(tf_bdg, top=2, bottom=2, left=4, right=4)
                set_para(tf_bdg.paragraphs[0], lvl, font_size=11 if num_r >= 4 else 12, bold=True, color_rgb=lvl_color, align=PP_ALIGN.CENTER)
                
                # Title & Description Box
                tb = slide.shapes.add_textbox(cur_left + Inches(0.15), top_m + Inches(0.65), card_w - Inches(0.3), Inches(1.55))
                tf = tb.text_frame
                tf.word_wrap = True
                self._set_tf_margins(tf, top=4, bottom=4, left=4, right=4)
                set_para(tf.paragraphs[0], r.get("title", ""), font_size=12.5 if num_r >= 4 else 13.5, bold=True, color_rgb=C_DARK)
                p_d = tf.add_paragraph()
                set_para(p_d, r.get("desc", ""), font_size=10.0 if num_r >= 4 else 10.5, bold=False, color_rgb=C_MUTED)
                p_d.space_before = Pt(4)
                
                p_dim = tf.add_paragraph()
                dim_str = f"影响: {r.get('impact', '极高')}  |  概率: {r.get('probability', '35%')}"
                set_para(p_dim, dim_str, font_size=9.5 if num_r >= 4 else 10.0, bold=True, color_rgb=lvl_color)
                p_dim.space_before = Pt(6)
                
                # Strategy Response Box
                resp_box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cur_left + Inches(0.12), top_m + Inches(2.3), card_w - Inches(0.24), Inches(2.5))
                resp_box.fill.solid()
                resp_box.fill.fore_color.rgb = C_WHITE
                resp_box.line.color.rgb = C_BORDER
                resp_box.line.width = Pt(1)
                
                tb_resp = slide.shapes.add_textbox(cur_left + Inches(0.15), top_m + Inches(2.35), card_w - Inches(0.3), Inches(2.4))
                tf_resp = tb_resp.text_frame
                tf_resp.word_wrap = True
                self._set_tf_margins(tf_resp, top=6, bottom=6, left=6, right=6)
                set_para(tf_resp.paragraphs[0], "【应对对策与落地预案】", font_size=11, bold=True, color_rgb=C_BLUE)
                
                p_r = tf_resp.add_paragraph()
                f_resp = calc_autofit_fontsize(r.get("response", ""), base_size=10.0 if num_r >= 4 else 10.5, min_size=8.5, threshold_len=24)
                set_para(p_r, f"• 核心对策: {r.get('response', '')}", font_size=f_resp, bold=False, color_rgb=C_DARK)
                p_r.space_before = Pt(8)
                
                p_prev = tf_resp.add_paragraph()
                prevent_txt = r.get("prevent", "建立多方联合评审与标准化接口联调机制")
                f_prev = calc_autofit_fontsize(prevent_txt, base_size=9.5 if num_r >= 4 else 10.0, min_size=8.0, threshold_len=24)
                set_para(p_prev, f"• 防控机制: {prevent_txt}", font_size=f_prev, bold=False, color_rgb=C_MUTED)
                p_prev.space_before = Pt(8)
                
                p_own = tf_resp.add_paragraph()
                own_txt = f"责任: {r.get('owner', '研发与交付 PMO')} | 时限: {r.get('timeline', 'T+30天闭环')}"
                set_para(p_own, own_txt, font_size=9.0 if num_r >= 4 else 9.5, bold=True, color_rgb=C_BLUE)
                p_own.space_before = Pt(12)

        else: # ARCH_33
            honors = s_data.get("honors", [
                {"badge": "国家级", "title": "国家科学技术进步奖", "org": "中华人民共和国国务院", "metric": "连续 5 年获奖"},
                {"badge": "国际化", "title": "IEC / UL 全球双重认证", "org": "国际电工委员会 / UL 认证", "metric": "100% 覆盖导出产品"},
                {"badge": "数智化", "title": "国家级智能制造示范工厂", "org": "工业和信息化部", "metric": "行业首批示范"},
                {"badge": "绿色零碳", "title": "零碳工厂与ESG A级认证", "org": "国际权威评级机构", "metric": "绿色电力率 100%"}
            ])
            num_h = max(1, min(len(honors), 5))
            gap = Inches(0.2) if num_h >= 5 else (Inches(0.25) if num_h == 4 else Inches(0.35))
            card_w = Inches((11.73 - (num_h - 1) * gap.inches) / num_h)

            for i, h in enumerate(honors[:num_h]):
                cur_left = left_m + i * (card_w + gap)
                bg = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cur_left, top_m, card_w, card_h)
                bg.fill.solid()
                bg.fill.fore_color.rgb = C_LIGHT_BG
                bg.line.color.rgb = C_BORDER
                bg.line.width = Pt(1)

                oval_w = Inches(0.75) if num_h >= 5 else Inches(0.8)
                bdg = slide.shapes.add_shape(MSO_SHAPE.OVAL, cur_left + card_w / 2 - oval_w / 2, top_m + Inches(0.3), oval_w, oval_w)
                bdg.fill.solid()
                bdg.fill.fore_color.rgb = C_BLUE_BG
                bdg.line.color.rgb = C_BLUE
                bdg.line.width = Pt(1)
                tf_bdg = bdg.text_frame
                self._set_tf_margins(tf_bdg, top=2, bottom=2, left=2, right=2)
                set_para(tf_bdg.paragraphs[0], h.get("badge", "荣誉"), font_size=10 if num_h >= 5 else 10.5, bold=True, color_rgb=C_BLUE, align=PP_ALIGN.CENTER)

                tb = slide.shapes.add_textbox(cur_left + Inches(0.1), top_m + Inches(1.2), card_w - Inches(0.2), Inches(3.5))
                tf = tb.text_frame
                tf.word_wrap = True
                self._set_tf_margins(tf, top=6, bottom=6, left=6, right=6)
                set_para(tf.paragraphs[0], h.get("title", ""), font_size=12.5 if num_h >= 5 else 13.5, bold=True, color_rgb=C_BLUE, align=PP_ALIGN.CENTER)
                p_org = tf.add_paragraph()
                set_para(p_org, h.get("org", ""), font_size=9.5 if num_h >= 5 else 10.5, bold=False, color_rgb=C_DARK, align=PP_ALIGN.CENTER)
                p_org.space_before = Pt(5)
                p_m = tf.add_paragraph()
                set_para(p_m, f"★ {h.get('metric', '')}", font_size=10.5 if num_h >= 5 else 11, bold=True, color_rgb=C_GREEN, align=PP_ALIGN.CENTER)
                p_m.space_before = Pt(8)
                p_m.space_after = Pt(2)

    def _render_horizontal_pipeline(self, slide, s_data: Dict[str, Any], arch: str):
        """Engine 5: Sequential Pipeline / Roadmap with Dynamic Reflow (ARCH_06, ARCH_25, ARCH_27, ARCH_28, ARCH_30)"""
        self._add_body_master(slide, s_data.get("title", ""), s_data.get("category", ""))
        top_m, left_m = Inches(1.6), Inches(0.8)

        if arch.startswith("ARCH_06"):
            stages = s_data.get("stages", [
                {"phase": "第一阶段", "title": "规划启动", "desc": "明确战略目标与需求"},
                {"phase": "第二阶段", "title": "试点验证", "desc": "关键业务验证与标准沉淀"},
                {"phase": "第三阶段", "title": "全面推广", "desc": "全链路赋能与规模化推广"},
                {"phase": "第四阶段", "title": "持续优化", "desc": "长效机制建设与运营迭代"}
            ])
            num_s = max(1, min(len(stages), 5))
            gap = Inches(0.2) if num_s >= 5 else Inches(0.3)
            card_w = Inches((11.73 - (num_s - 1) * gap.inches) / num_s)

            line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left_m + Inches(0.4), Inches(3.8), Inches(11.73 - 0.8), Inches(0.04))
            line.fill.solid()
            line.fill.fore_color.rgb = C_BLUE
            line.line.fill.background()

            for i, stg in enumerate(stages[:num_s]):
                cur_left = left_m + i * (card_w + gap)
                circle = slide.shapes.add_shape(MSO_SHAPE.OVAL, cur_left + card_w / 2 - Inches(0.2), Inches(3.62), Inches(0.4), Inches(0.4))
                circle.fill.solid()
                circle.fill.fore_color.rgb = C_CYAN
                circle.line.fill.background()

                bg = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cur_left, Inches(1.6), card_w, Inches(1.8))
                bg.fill.solid()
                bg.fill.fore_color.rgb = C_LIGHT_BG
                bg.line.color.rgb = C_BORDER
                bg.line.width = Pt(1)

                tb_top = slide.shapes.add_textbox(cur_left + Inches(0.1), Inches(1.7), card_w - Inches(0.2), Inches(1.5))
                tf_top = tb_top.text_frame
                tf_top.word_wrap = True
                self._set_tf_margins(tf_top, top=4, bottom=4, left=4, right=4)
                set_para(tf_top.paragraphs[0], stg.get("phase", f"阶段 0{i+1}"), font_size=11 if num_s >= 5 else 12, bold=True, color_rgb=C_BLUE, align=PP_ALIGN.CENTER)
                p_t = tf_top.add_paragraph()
                set_para(p_t, stg.get("title", ""), font_size=12.5 if num_s >= 5 else 14, bold=True, color_rgb=C_DARK, align=PP_ALIGN.CENTER)
                p_t.space_before = Pt(3)

                tb_bot = slide.shapes.add_textbox(cur_left, Inches(4.3), card_w, Inches(2.2))
                tf_bot = tb_bot.text_frame
                tf_bot.word_wrap = True
                self._set_tf_margins(tf_bot, top=4, bottom=4, left=4, right=4)
                f_desc = calc_autofit_fontsize(stg.get("desc", ""), base_size=10.0 if num_s >= 5 else 11.0, min_size=8.5, threshold_len=20)
                set_para(tf_bot.paragraphs[0], stg.get("desc", ""), font_size=f_desc, bold=False, color_rgb=C_MUTED, align=PP_ALIGN.CENTER)

        elif arch.startswith("ARCH_25"):
            steps = s_data.get("steps", [
                {"phase": "01", "title": "现场调研", "subtitle": "需求摸底与配电勘测", "actions": ["电力拓扑实地测绘与摸底", "用电设备安全隐患排查", "全天候能耗负荷数据采集"], "deliverable": "《现场勘测诊断报告》", "duration": "1-2 周"},
                {"phase": "02", "title": "系统设计", "subtitle": "元器件选型与图纸深化", "actions": ["断路器与配电设备精准选型", "BIM 3D 机房布局深化设计", "定制化通信协议拓扑规划"], "deliverable": "《电气系统深化设计蓝图》", "duration": "2-3 周"},
                {"phase": "03", "title": "智能排产", "subtitle": "灯塔工厂柔性定制生产", "actions": ["智能制造全流程自动化装配", "100% 关键元器件质量质检", "全链路数字化追溯码生成"], "deliverable": "《产品出厂合格质检报告》", "duration": "1 周"},
                {"phase": "04", "title": "现场联调", "subtitle": "通电联调与云平台接入", "actions": ["现场设备安装与母排搭接", "边缘网关数据采集上云联调", "保护定值校验与带电试运行"], "deliverable": "《系统联调验收签署单》", "duration": "1 周"},
                {"phase": "05", "title": "智慧运营", "subtitle": "全生命周期云端运维", "actions": ["7x24h 智能能效与负荷优化", "AI 故障预测性维护与预警", "定期巡检与主动式备件保障"], "deliverable": "《年度智慧能效运营报告》", "duration": "长效运营"}
            ])
            num_s = max(1, min(len(steps), 6))
            gap = Inches(0.2) if num_s >= 5 else Inches(0.35)
            card_w = Inches((11.73 - (num_s - 1) * gap.inches) / num_s)
            card_h = Inches(5.0)

            for i, st in enumerate(steps[:num_s]):
                cur_left = left_m + i * (card_w + gap)
                bg = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cur_left, top_m, card_w, card_h)
                bg.fill.solid()
                bg.fill.fore_color.rgb = C_LIGHT_BG
                bg.line.color.rgb = C_BORDER
                bg.line.width = Pt(1)

                # Step Badge Pill
                pill = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cur_left + Inches(0.12), top_m + Inches(0.2), card_w - Inches(0.24), Inches(0.42))
                pill.fill.solid()
                pill.fill.fore_color.rgb = C_BLUE
                pill.line.fill.background()
                tf_pill = pill.text_frame
                self._set_tf_margins(tf_pill, top=2, bottom=2, left=4, right=4)
                set_para(tf_pill.paragraphs[0], f"STEP {st.get('phase', f'0{i+1}')}", font_size=10.5 if num_s >= 5 else 11.5, bold=True, color_rgb=C_WHITE, align=PP_ALIGN.CENTER)

                # Title & Subtitle Box
                tb_hdr = slide.shapes.add_textbox(cur_left + Inches(0.08), top_m + Inches(0.68), card_w - Inches(0.16), Inches(0.85))
                tf_hdr = tb_hdr.text_frame
                tf_hdr.word_wrap = True
                self._set_tf_margins(tf_hdr, top=2, bottom=2, left=2, right=2)
                set_para(tf_hdr.paragraphs[0], st.get("title", ""), font_size=12.5 if num_s >= 5 else 14, bold=True, color_rgb=C_DARK, align=PP_ALIGN.CENTER)
                p_sub = tf_hdr.add_paragraph()
                f_sub = calc_autofit_fontsize(st.get("subtitle", st.get("desc", "")), base_size=9.5 if num_s >= 5 else 10.5, min_size=8.0, threshold_len=16)
                set_para(p_sub, st.get("subtitle", st.get("desc", "")), font_size=f_sub, bold=False, color_rgb=C_BLUE, align=PP_ALIGN.CENTER)
                p_sub.space_before = Pt(2)

                # Key Actions Box
                actions_box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cur_left + Inches(0.1), top_m + Inches(1.58), card_w - Inches(0.2), Inches(1.95))
                actions_box.fill.solid()
                actions_box.fill.fore_color.rgb = C_WHITE
                actions_box.line.color.rgb = C_BORDER
                actions_box.line.width = Pt(1)

                tb_acts = slide.shapes.add_textbox(cur_left + Inches(0.12), top_m + Inches(1.62), card_w - Inches(0.24), Inches(1.85))
                tf_acts = tb_acts.text_frame
                tf_acts.word_wrap = True
                self._set_tf_margins(tf_acts, top=4, bottom=4, left=4, right=4)
                
                act_list = st.get("actions", [])
                if not act_list and st.get("desc"):
                    act_list = [st.get("desc")]
                    
                for a_idx, act in enumerate(act_list[:3]):
                    p_a = tf_acts.paragraphs[0] if a_idx == 0 else tf_acts.add_paragraph()
                    f_a = calc_autofit_fontsize(act, base_size=9.0 if num_s >= 5 else 9.5, min_size=7.5, threshold_len=18)
                    set_para(p_a, f"• {act}", font_size=f_a, bold=False, color_rgb=C_DARK)
                    p_a.space_before = Pt(9)
                    p_a.space_after = Pt(2)

                # Bottom Deliverable Box
                deliv_box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cur_left + Inches(0.1), top_m + Inches(3.62), card_w - Inches(0.2), Inches(1.2))
                deliv_box.fill.solid()
                deliv_box.fill.fore_color.rgb = C_BLUE_BG
                deliv_box.line.color.rgb = RGBColor(180, 210, 255)
                deliv_box.line.width = Pt(1)

                tb_deliv = slide.shapes.add_textbox(cur_left + Inches(0.12), top_m + Inches(3.65), card_w - Inches(0.24), Inches(1.1))
                tf_deliv = tb_deliv.text_frame
                tf_deliv.word_wrap = True
                self._set_tf_margins(tf_deliv, top=2, bottom=2, left=2, right=2)
                set_para(tf_deliv.paragraphs[0], "【核心交付】", font_size=9.5 if num_s >= 5 else 10.0, bold=True, color_rgb=C_BLUE, align=PP_ALIGN.CENTER)
                
                p_del = tf_deliv.add_paragraph()
                f_del = calc_autofit_fontsize(st.get("deliverable", "《阶段交付物》"), base_size=9.0 if num_s >= 5 else 9.5, min_size=7.5, threshold_len=18)
                set_para(p_del, st.get("deliverable", "《阶段交付物》"), font_size=f_del, bold=False, color_rgb=C_DARK, align=PP_ALIGN.CENTER)
                p_del.space_before = Pt(2)

                p_dur = tf_deliv.add_paragraph()
                set_para(p_dur, f"周期: {st.get('duration', '1-2周')}", font_size=8.5 if num_s >= 5 else 9.0, bold=True, color_rgb=C_MUTED, align=PP_ALIGN.CENTER)
                p_dur.space_before = Pt(2)

                if i < num_s - 1:
                    chv_w = Inches(0.14) if num_s >= 5 else Inches(0.18)
                    chv = slide.shapes.add_shape(MSO_SHAPE.CHEVRON, cur_left + card_w + (gap - chv_w) / 2, top_m + Inches(2.25), chv_w, Inches(0.35))
                    chv.fill.solid()
                    chv.fill.fore_color.rgb = C_CYAN
                    chv.line.fill.background()

        elif arch.startswith("ARCH_27"):
            steps = s_data.get("steps", [
                {"ver": "2.0", "title": "基础电气化", "desc": "传统元器件与被动保护"},
                {"ver": "3.0", "title": "自动化联控", "desc": "PLC 逻辑控制与本地监测"},
                {"ver": "4.0", "title": "数智化能效", "desc": "云边协同与 AI 优化调度"},
                {"ver": "5.0", "title": "零碳自愈", "desc": "全自愈微网与生态赋能"}
            ])
            num_s = max(1, min(len(steps), 5))
            gap = Inches(0.2) if num_s >= 5 else Inches(0.35)
            card_w = Inches((11.73 - (num_s - 1) * gap.inches) / num_s)
            min_h, max_h = Inches(2.2), Inches(4.9)
            heights = [min_h + (max_h - min_h) * (i / max(1, num_s - 1)) for i in range(num_s)]

            for i, st in enumerate(steps[:num_s]):
                cur_left = left_m + i * (card_w + gap)
                cur_h = heights[i]
                cur_top = top_m + (Inches(5.0) - cur_h)
                is_last = (i == num_s - 1)

                bg = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cur_left, cur_top, card_w, cur_h)
                bg.fill.solid()
                bg.fill.fore_color.rgb = C_BLUE_BG
                bg.line.color.rgb = C_BLUE if is_last else C_BORDER
                bg.line.width = Pt(1.5 if is_last else 1)

                cap = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cur_left, cur_top, card_w, Inches(0.55))
                cap.fill.solid()
                cap.fill.fore_color.rgb = C_BLUE if is_last else RGBColor(70, 120, 230)
                cap.line.fill.background()
                tf_cap = cap.text_frame
                self._set_tf_margins(tf_cap, top=3, bottom=3, left=4, right=4)
                set_para(tf_cap.paragraphs[0], f"V {st.get('ver', '')}", font_size=12 if num_s >= 5 else 13, bold=True, color_rgb=C_WHITE, align=PP_ALIGN.CENTER)

                tb = slide.shapes.add_textbox(cur_left + Inches(0.1), cur_top + Inches(0.65), card_w - Inches(0.2), cur_h - Inches(0.75))
                tf = tb.text_frame
                tf.word_wrap = True
                self._set_tf_margins(tf, top=6, bottom=6, left=6, right=6)
                set_para(tf.paragraphs[0], st.get("title", ""), font_size=12.5 if num_s >= 5 else 14, bold=True, color_rgb=C_DARK, align=PP_ALIGN.CENTER)
                p_d = tf.add_paragraph()
                f_desc = calc_autofit_fontsize(st.get("desc", ""), base_size=10.0 if num_s >= 5 else 11.0, min_size=8.5, threshold_len=20)
                set_para(p_d, st.get("desc", ""), font_size=f_desc, bold=False, color_rgb=C_MUTED, align=PP_ALIGN.CENTER)
                p_d.space_before = Pt(5)

        elif arch.startswith("ARCH_28"):
            gates = s_data.get("gates", [
                {"gate": "G1 概念门禁", "title": "需求定义与可行性立项"},
                {"gate": "G2 计划门禁", "title": "系统架构与包方案冻结"},
                {"gate": "G3 开发门禁", "title": "样品试制与全测试验证"},
                {"gate": "G4 验证门禁", "title": "试点试运行与准入评估"},
                {"gate": "G5 发布门禁", "title": "量产上市与全球商业化"}
            ])
            num_g = max(1, min(len(gates), 6))
            gap = Inches(0.18) if num_g >= 6 else (Inches(0.22) if num_g == 5 else Inches(0.3))
            card_w = Inches((11.73 - (num_g - 1) * gap.inches) / num_g)

            line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), top_m + Inches(0.5), Inches(11.73), Inches(0.04))
            line.fill.solid()
            line.fill.fore_color.rgb = C_BORDER
            line.line.fill.background()

            for i, g in enumerate(gates[:num_g]):
                cur_left = left_m + i * (card_w + gap)
                d_w = Inches(0.55) if num_g >= 6 else Inches(0.65)
                node = slide.shapes.add_shape(MSO_SHAPE.DIAMOND, cur_left + card_w / 2 - d_w / 2, top_m + Inches(0.2), d_w, d_w)
                node.fill.solid()
                node.fill.fore_color.rgb = C_BLUE if i < num_g - 1 else C_CYAN
                node.line.fill.background()

                bg = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cur_left, top_m + Inches(1.1), card_w, Inches(3.8))
                bg.fill.solid()
                bg.fill.fore_color.rgb = C_LIGHT_BG
                bg.line.color.rgb = C_BORDER
                bg.line.width = Pt(1)

                tb = slide.shapes.add_textbox(cur_left + Inches(0.1), top_m + Inches(1.2), card_w - Inches(0.2), Inches(3.5))
                tf = tb.text_frame
                tf.word_wrap = True
                self._set_tf_margins(tf, top=6, bottom=6, left=4, right=4)
                set_para(tf.paragraphs[0], g.get("gate", f"G{i+1}"), font_size=11 if num_g >= 6 else 12, bold=True, color_rgb=C_BLUE, align=PP_ALIGN.CENTER)
                p_t = tf.add_paragraph()
                f_title = calc_autofit_fontsize(g.get("title", ""), base_size=10.5 if num_g >= 6 else 11.5, min_size=8.5, threshold_len=15)
                set_para(p_t, g.get("title", ""), font_size=f_title, bold=True, color_rgb=C_DARK, align=PP_ALIGN.CENTER)
                p_t.space_before = Pt(5)

        else: # ARCH_30
            milestones = s_data.get("milestones", [
                {"year": "2024", "title": "战略升级与智慧能效平台发布", "desc": "正泰发布全新智慧能效物联网平台，奠定数智化转型根基"},
                {"year": "2025", "title": "全球交付网络突破与生态共建", "desc": "海外业务增长超 40%，全产业生态伙伴突破 500 家"},
                {"year": "2026", "title": "2026 VI 规范全面重构与赋能", "desc": "全面推行企业级标准化交付，实现产品与营销端全面焕新"}
            ])
            num_ms = max(1, min(len(milestones), 4))
            gap_y_in = 0.15 if num_ms >= 4 else 0.25
            card_h_in = (5.0 - (num_ms - 1) * gap_y_in) / num_ms
            gap_y = Inches(gap_y_in)
            card_h_inch = Inches(card_h_in)

            for idx, ms in enumerate(milestones[:num_ms]):
                cur_top = top_m + idx * (card_h_inch + gap_y)
                year_pill = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), cur_top, Inches(2.2), card_h_inch)
                year_pill.fill.solid()
                year_pill.fill.fore_color.rgb = C_BLUE
                year_pill.line.fill.background()
                tf_yp = year_pill.text_frame
                self._set_tf_margins(tf_yp, top=6, bottom=6, left=6, right=6)
                set_para(tf_yp.paragraphs[0], ms.get("year", ""), font_size=20 if num_ms >= 4 else 24, bold=True, color_rgb=C_WHITE, align=PP_ALIGN.CENTER)

                card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(3.2), cur_top, Inches(9.33), card_h_inch)
                card.fill.solid()
                card.fill.fore_color.rgb = C_LIGHT_BG
                card.line.color.rgb = C_BORDER
                card.line.width = Pt(1)

                tb = slide.shapes.add_textbox(Inches(3.5), cur_top + Inches(0.12), Inches(8.8), card_h_inch - Inches(0.24))
                tf = tb.text_frame
                tf.word_wrap = True
                self._set_tf_margins(tf, top=6, bottom=6, left=6, right=6)
                set_para(tf.paragraphs[0], ms.get("title", ""), font_size=13 if num_ms >= 4 else 14, bold=True, color_rgb=C_DARK)
                p_d = tf.add_paragraph()
                f_desc = calc_autofit_fontsize(ms.get("desc", ""), base_size=10.5 if num_ms >= 4 else 11.0, min_size=9.0, threshold_len=40)
                set_para(p_d, ms.get("desc", ""), font_size=f_desc, bold=False, color_rgb=C_MUTED)
                p_d.space_before = Pt(4)

    def _render_funnel_stepped(self, slide, s_data: Dict[str, Any], arch: str):
        """Engine 6: Stepped Funnel Conversion (ARCH_26)"""
        self._add_body_master(slide, s_data.get("title", "营销转化与客户全生命周期漏斗"), s_data.get("category", "漏斗模型"))
        top_m = Inches(1.6)
        stages = s_data.get("stages", [
            {"stage": "1. 泛客户触达 (Awareness)", "value": "10,000+", "desc": "品牌曝光与白皮书下载触达"},
            {"stage": "2. 意向商机挖掘 (Interest)", "value": "2,500+", "desc": "技术交流与现场需求对接"},
            {"stage": "3. 方案PoC验证 (Evaluation)", "value": "600+", "desc": "定制化方案PoC与试点验证"},
            {"stage": "4. 最终签约落地 (Conversion)", "value": "180+", "desc": "商业合同签署与项目交付"}
        ])
        funnel_widths = [Inches(11.2), Inches(9.2), Inches(7.2), Inches(5.2)]
        colors = [C_BLUE, RGBColor(35, 120, 255), C_CYAN, C_ICE_BLUE]
        text_colors = [C_WHITE, C_WHITE, C_DARK, C_BLUE]

        for idx, stg in enumerate(stages[:4]):
            cur_w = funnel_widths[idx]
            cur_left = Inches(6.66) - (cur_w / 2)
            cur_top = top_m + idx * Inches(1.2)

            bar = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cur_left, cur_top, cur_w, Inches(1.05))
            bar.fill.solid()
            bar.fill.fore_color.rgb = colors[idx]
            bar.line.color.rgb = C_BORDER if idx == 3 else C_BLUE
            bar.line.width = Pt(1)

            tb = slide.shapes.add_textbox(cur_left + Inches(0.3), cur_top + Inches(0.1), cur_w - Inches(0.6), Inches(0.85))
            tf = tb.text_frame
            tf.word_wrap = True
            self._set_tf_margins(tf, top=4, bottom=4, left=6, right=6)
            set_para(tf.paragraphs[0], f"{stg.get('stage', '')}  —  【{stg.get('value', '')}】", font_size=13.5, bold=True, color_rgb=text_colors[idx], align=PP_ALIGN.CENTER)
            p_d = tf.add_paragraph()
            set_para(p_d, stg.get("desc", ""), font_size=11, bold=False, color_rgb=text_colors[idx], align=PP_ALIGN.CENTER)
            p_d.space_before = Pt(3)

    def _render_matrix_2x2_quadrant(self, slide, s_data: Dict[str, Any], arch: str):
        """Engine 7: 2x2 SWOT / TOWS Matrix (ARCH_20)"""
        self._add_body_master(slide, s_data.get("title", "SWOT 战略态势与业务诊断矩阵"), s_data.get("category", "战略诊断"))
        top_m, quad_w, quad_h = Inches(1.6), Inches(5.7), Inches(2.4)
        gap_x, gap_y = Inches(0.33), Inches(0.2)

        quadrants = [
            (0, 0, "S", "优势 (Strengths)", C_BLUE_BG, C_BLUE, C_BLUE, "strengths"),
            (0, 1, "W", "劣势 (Weaknesses)", C_RED_BG, C_RED_TEXT, C_RED_TEXT, "weaknesses"),
            (1, 0, "O", "机会 (Opportunities)", C_GREEN_BG, C_GREEN, C_GREEN, "opportunities"),
            (1, 1, "T", "威胁 (Threats)", C_LIGHT_BG, C_BORDER, C_DARK, "threats"),
        ]

        for r, c, letter, q_title, q_bg, q_border, q_color, key in quadrants:
            cur_left = Inches(0.8) + c * (quad_w + gap_x)
            cur_top = top_m + r * (quad_h + gap_y)

            bg = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cur_left, cur_top, quad_w, quad_h)
            bg.fill.solid()
            bg.fill.fore_color.rgb = q_bg
            bg.line.color.rgb = q_border
            bg.line.width = Pt(1)

            badge = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cur_left + Inches(0.15), cur_top + Inches(0.15), Inches(0.5), Inches(0.4))
            badge.fill.solid()
            badge.fill.fore_color.rgb = q_color if key != "threats" else C_MUTED
            badge.line.fill.background()
            tf_bdg = badge.text_frame
            self._set_tf_margins(tf_bdg, top=2, bottom=2, left=2, right=2)
            set_para(tf_bdg.paragraphs[0], letter, font_size=14, bold=True, color_rgb=C_WHITE, align=PP_ALIGN.CENTER)

            tb_t = slide.shapes.add_textbox(cur_left + Inches(0.75), cur_top + Inches(0.12), quad_w - Inches(0.9), Inches(0.45))
            tf_t = tb_t.text_frame
            tf_t.word_wrap = True
            self._set_tf_margins(tf_t, top=4, bottom=4, left=4, right=4)
            set_para(tf_t.paragraphs[0], q_title, font_size=13.5, bold=True, color_rgb=q_color)

            tb_b = slide.shapes.add_textbox(cur_left + Inches(0.2), cur_top + Inches(0.65), quad_w - Inches(0.4), quad_h - Inches(0.75))
            tf_b = tb_b.text_frame
            tf_b.word_wrap = True
            self._set_tf_margins(tf_b, top=6, bottom=6, left=6, right=6)
            items = s_data.get(key, ["关键分析点 01：核心业务影响与战略要素分析", "关键分析点 02：协同推进策略与落地要点"])
            for j, it in enumerate(items[:3]):
                p = tf_b.paragraphs[0] if j == 0 else tf_b.add_paragraph()
                set_para(p, f"• {it}", font_size=11, bold=False, color_rgb=C_DARK)
                p.space_before = Pt(4)
                p.space_after = Pt(2)

    def _render_matrix_grid_flat(self, slide, s_data: Dict[str, Any], arch: str):
        """Engine 8: 2xN Flat Grid Matrix with Dynamic Reflow (ARCH_09, ARCH_34)"""
        self._add_body_master(slide, s_data.get("title", ""), s_data.get("category", ""))
        top_m, left_m = Inches(1.6), Inches(0.8)

        if arch.startswith("ARCH_09"):
            modules = s_data.get("modules", [{"title": f"方案模块 0{i+1}", "desc": "业务应用场景与技术方案说明"} for i in range(6)])
            num_m = len(modules) if modules else 6
            if num_m <= 4:
                cols = 2
                card_w, card_h = Inches(5.6), Inches(2.25)
                gap_x, gap_y = Inches(0.53), Inches(0.35)
            elif num_m <= 6:
                cols = 3
                card_w, card_h = Inches(3.64), Inches(2.25)
                gap_x, gap_y = Inches(0.4), Inches(0.35)
            else:
                cols = 4
                card_w, card_h = Inches(2.72), Inches(2.25)
                gap_x, gap_y = Inches(0.28), Inches(0.35)

            f_t = 12.5 if cols >= 4 else 13.5
            f_d_base = 10.0 if cols >= 4 else 11.0

            for i, mod in enumerate(modules[:cols * 2]):
                col, row = i % cols, i // cols
                cur_left = left_m + col * (card_w + gap_x)
                cur_top = top_m + row * (card_h + gap_y)

                bg = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cur_left, cur_top, card_w, card_h)
                bg.fill.solid()
                bg.fill.fore_color.rgb = C_BLUE_BG
                bg.line.color.rgb = RGBColor(200, 220, 255)
                bg.line.width = Pt(1)

                tb_t = slide.shapes.add_textbox(cur_left + Inches(0.15), cur_top + Inches(0.12), card_w - Inches(0.3), Inches(0.45))
                tf_t = tb_t.text_frame
                tf_t.word_wrap = True
                self._set_tf_margins(tf_t, top=4, bottom=4, left=4, right=4)
                set_para(tf_t.paragraphs[0], mod.get("title", ""), font_size=f_t, bold=True, color_rgb=C_BLUE)

                tb_d = slide.shapes.add_textbox(cur_left + Inches(0.15), cur_top + Inches(0.6), card_w - Inches(0.3), card_h - Inches(0.75))
                tf_d = tb_d.text_frame
                tf_d.word_wrap = True
                self._set_tf_margins(tf_d, top=4, bottom=4, left=4, right=4)
                f_auto = calc_autofit_fontsize(mod.get("desc", ""), base_size=f_d_base, min_size=8.5, threshold_len=25)
                set_para(tf_d.paragraphs[0], mod.get("desc", ""), font_size=f_auto, bold=False, color_rgb=C_MUTED)

        else: # ARCH_34
            partners = s_data.get("partners", [
                {"category": "电力与能源巨头", "title": "国家电网 / 南方电网", "desc": "特高压与智慧配电战略合作"},
                {"category": "科技与物联网", "title": "阿里云 / 腾讯云", "desc": "工业云与 AI 能效算法联合开发"},
                {"category": "工业制造领军", "title": "中国中车 / 宝武钢铁", "desc": "高端制造示范工程落地实施"},
                {"category": "全球生态伙伴", "title": "施耐德 / 西门子合作项目", "desc": "国际标准联合推进与项目协同"}
            ])
            num_p = len(partners) if partners else 4
            if num_p > 4:
                cols = 3
                card_w, card_h = Inches(3.64), Inches(2.25)
                gap_x, gap_y = Inches(0.4), Inches(0.35)
            else:
                cols = 2
                card_w, card_h = Inches(5.6), Inches(2.25)
                gap_x, gap_y = Inches(0.53), Inches(0.35)

            for idx, pt in enumerate(partners[:cols * 2]):
                col, row = idx % cols, idx // cols
                cur_left = left_m + col * (card_w + gap_x)
                cur_top = top_m + row * (card_h + gap_y)

                bg = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cur_left, cur_top, card_w, card_h)
                bg.fill.solid()
                bg.fill.fore_color.rgb = C_WHITE
                bg.line.color.rgb = C_BORDER
                bg.line.width = Pt(1)

                tag_w = Inches(1.8) if cols == 3 else Inches(2.2)
                tag = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cur_left + Inches(0.15), cur_top + Inches(0.15), tag_w, Inches(0.38))
                tag.fill.solid()
                tag.fill.fore_color.rgb = C_BLUE_BG
                tag.line.fill.background()
                tf_tag = tag.text_frame
                self._set_tf_margins(tf_tag, top=2, bottom=2, left=4, right=4)
                set_para(tf_tag.paragraphs[0], pt.get("category", ""), font_size=10 if cols == 3 else 10.5, bold=True, color_rgb=C_BLUE, align=PP_ALIGN.CENTER)

                tb = slide.shapes.add_textbox(cur_left + Inches(0.15), cur_top + Inches(0.6), card_w - Inches(0.3), card_h - Inches(0.75))
                tf = tb.text_frame
                tf.word_wrap = True
                self._set_tf_margins(tf, top=4, bottom=4, left=4, right=4)
                set_para(tf.paragraphs[0], pt.get("title", ""), font_size=13 if cols == 3 else 14, bold=True, color_rgb=C_DARK)
                p_d = tf.add_paragraph()
                f_desc = calc_autofit_fontsize(pt.get("desc", ""), base_size=10.0 if cols == 3 else 11.0, min_size=8.5, threshold_len=25)
                set_para(p_d, pt.get("desc", ""), font_size=f_desc, bold=False, color_rgb=C_MUTED)
                p_d.space_before = Pt(4)

    def _render_platform_architecture(self, slide, s_data: Dict[str, Any], arch: str):
        """Engine 9: 4-Layer Stacked Architecture (ARCH_08)"""
        self._add_body_master(slide, s_data.get("title", ""), s_data.get("category", ""))
        layers = s_data.get("layers", [])
        arch_w, layer_h, gap, top_start = Inches(11.73), Inches(1.15), Inches(0.12), Inches(1.6)
        tag_colors = [C_BLUE, RGBColor(35, 120, 255), C_CYAN, C_DEEP_BLUE]

        for i, l in enumerate(layers[:4]):
            cur_top = top_start + i * (layer_h + gap)
            bg = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), cur_top, arch_w, layer_h)
            bg.fill.solid()
            bg.fill.fore_color.rgb = C_WHITE
            bg.line.color.rgb = C_BLUE if i == 0 else C_BORDER
            bg.line.width = Pt(1.5) if i == 0 else Pt(1)

            tag = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.0), cur_top + Inches(0.22), Inches(2.2), Inches(0.7))
            tag.fill.solid()
            tag.fill.fore_color.rgb = tag_colors[i] if i < len(tag_colors) else C_BLUE
            tag.line.fill.background()
            tf_tag = tag.text_frame
            self._set_tf_margins(tf_tag, top=4, bottom=4, left=4, right=4)
            set_para(tf_tag.paragraphs[0], l.get("layer_name", ""), font_size=12, bold=True, color_rgb=C_WHITE, align=PP_ALIGN.CENTER)

            tb_h = slide.shapes.add_textbox(Inches(3.4), cur_top + Inches(0.15), Inches(3.2), Inches(0.8))
            tf_h = tb_h.text_frame
            tf_h.word_wrap = True
            self._set_tf_margins(tf_h, top=6, bottom=6, left=6, right=6)
            set_para(tf_h.paragraphs[0], l.get("headline", ""), font_size=12.5, bold=True, color_rgb=C_BLUE if i == 0 else C_DARK)

            mods = l.get("modules", [])
            mod_text = "  |  ".join(mods)
            tb_m = slide.shapes.add_textbox(Inches(6.8), cur_top + Inches(0.15), arch_w - Inches(6.2), Inches(0.8))
            tf_m = tb_m.text_frame
            tf_m.word_wrap = True
            self._set_tf_margins(tf_m, top=6, bottom=6, left=6, right=6)
            set_para(tf_m.paragraphs[0], mod_text, font_size=11, bold=False, color_rgb=C_MUTED)

    def _render_pillars_and_base(self, slide, s_data: Dict[str, Any], arch: str):
        """Engine 10: 3 Pillars + Base Platform (ARCH_31)"""
        self._add_body_master(slide, s_data.get("title", "三支柱与平台底座支撑体系"), s_data.get("category", "平台支撑"))
        top_m = Inches(1.6)
        pillars = s_data.get("pillars", [
            {"title": "支柱一：产品硬实力", "bullets": ["标准化高端硬件", "极致质量管控与认证"]},
            {"title": "支柱二：软件数智化", "bullets": ["云边端协同平台", "AI 算法与能效调度"]},
            {"title": "支柱三：服务生态化", "bullets": ["7×24 全生命周期运维", "全球本地化交付网络"]}
        ])
        card_w, gap, left_m = Inches(3.64), Inches(0.4), Inches(0.8)

        for i, p in enumerate(pillars[:3]):
            cur_left = left_m + i * (card_w + gap)
            bg = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cur_left, top_m, card_w, Inches(3.3))
            bg.fill.solid()
            bg.fill.fore_color.rgb = C_BLUE_BG
            bg.line.color.rgb = C_BLUE
            bg.line.width = Pt(1)

            h_bar = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cur_left, top_m, card_w, Inches(0.6))
            h_bar.fill.solid()
            h_bar.fill.fore_color.rgb = C_BLUE
            h_bar.line.fill.background()
            tf_hbar = h_bar.text_frame
            self._set_tf_margins(tf_hbar, top=4, bottom=4, left=6, right=6)
            set_para(tf_hbar.paragraphs[0], p.get("title", ""), font_size=13, bold=True, color_rgb=C_WHITE, align=PP_ALIGN.CENTER)

            tb = slide.shapes.add_textbox(cur_left + Inches(0.2), top_m + Inches(0.75), card_w - Inches(0.4), Inches(2.4))
            tf = tb.text_frame
            tf.word_wrap = True
            self._set_tf_margins(tf, top=8, bottom=8, left=8, right=8)
            for j, b in enumerate(p.get("bullets", [])):
                para = tf.paragraphs[0] if j == 0 else tf.add_paragraph()
                set_para(para, f"• {b}", font_size=11, bold=False, color_rgb=C_DARK)
                para.space_before = Pt(8)
                para.space_after = Pt(2)

        base = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), top_m + Inches(3.5), Inches(11.73), Inches(1.5))
        base.fill.solid()
        base.fill.fore_color.rgb = C_DEEP_BLUE
        base.line.fill.background()

        tb_base = slide.shapes.add_textbox(Inches(1.0), top_m + Inches(3.6), Inches(11.33), Inches(1.3))
        tf_base = tb_base.text_frame
        tf_base.word_wrap = True
        self._set_tf_margins(tf_base, top=8, bottom=8, left=8, right=8)
        set_para(tf_base.paragraphs[0], s_data.get("base_title", "底座支撑：正泰统一云边物联 OS 与全球合规供应链"), font_size=14, bold=True, color_rgb=C_WHITE, align=PP_ALIGN.CENTER)
        p_bdesc = tf_base.add_paragraph()
        set_para(p_bdesc, s_data.get("base_desc", "提供强稳健、高并发、安全可信的底层技术支撑，全面赋能三大业务支柱高品质落地。"), font_size=11, bold=False, color_rgb=C_ICE_BLUE, align=PP_ALIGN.CENTER)
        p_bdesc.space_before = Pt(6)

    def _render_circular_hub_topology(self, slide, s_data: Dict[str, Any], arch: str):
        """Engine 11: Circular Hub Topology (ARCH_14, ARCH_32)"""
        top_m = Inches(1.6)
        if arch.startswith("ARCH_14"):
            self._add_body_master(slide, s_data.get("title", "核心战略闭环体系"), s_data.get("category", "战略闭环"))
            ring3 = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(3.8), Inches(1.5), Inches(5.7), Inches(5.7))
            ring3.fill.background()
            ring3.line.color.rgb = RGBColor(210, 230, 255)
            ring3.line.width = Pt(1)

            ring2 = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(4.5), Inches(2.2), Inches(4.3), Inches(4.3))
            ring2.fill.background()
            ring2.line.color.rgb = C_CYAN
            ring2.line.width = Pt(1.5)

            center_c = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(5.5), Inches(3.2), Inches(2.33), Inches(2.33))
            center_c.fill.solid()
            center_c.fill.fore_color.rgb = C_BLUE
            center_c.line.fill.background()

            center_label = s_data.get("center_label", "核心战略\n闭环赋能")
            c_lines = center_label.split("\n")
            tb_cc = slide.shapes.add_textbox(Inches(5.5), Inches(3.7), Inches(2.33), Inches(1.2))
            tf_cc = tb_cc.text_frame
            self._set_tf_margins(tf_cc, top=4, bottom=4, left=4, right=4)
            for line_i, cline in enumerate(c_lines):
                p_cline = tf_cc.paragraphs[0] if line_i == 0 else tf_cc.add_paragraph()
                set_para(p_cline, cline, font_size=15, bold=True, color_rgb=C_WHITE, align=PP_ALIGN.CENTER)

            node_positions = [
                (Inches(0.8), Inches(1.8), PP_ALIGN.RIGHT),
                (Inches(8.8), Inches(1.8), PP_ALIGN.LEFT),
                (Inches(0.8), Inches(4.8), PP_ALIGN.RIGHT),
                (Inches(8.8), Inches(4.8), PP_ALIGN.LEFT),
                (Inches(4.8), Inches(6.1), PP_ALIGN.CENTER),
            ]
            payload_nodes = s_data.get("nodes", s_data.get("items", []))
            default_nodes = [{"title": f"维度 0{i+1}", "desc": "关键业务推进策略与执行要点"} for i in range(5)]
            nodes_to_render = payload_nodes if payload_nodes else default_nodes

            for idx, nd in enumerate(nodes_to_render[:5]):
                n_left, n_top, n_align = node_positions[idx]
                tb_n = slide.shapes.add_textbox(n_left, n_top, Inches(3.8), Inches(1.1))
                tf_n = tb_n.text_frame
                tf_n.word_wrap = True
                self._set_tf_margins(tf_n, top=4, bottom=4, left=6, right=6)
                set_para(tf_n.paragraphs[0], nd.get("title", ""), font_size=14, bold=True, color_rgb=C_BLUE, align=n_align)
                p_d = tf_n.add_paragraph()
                set_para(p_d, nd.get("desc", nd.get("detail", "")), font_size=11, bold=False, color_rgb=C_MUTED, align=n_align)
                p_d.space_before = Pt(3)

        else: # ARCH_32
            self._add_body_master(slide, s_data.get("title", "产业协同与 4 方生态拓扑"), s_data.get("category", "生态拓扑"))
            ring = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(3.8), top_m + Inches(0.2), Inches(5.73), Inches(4.6))
            ring.fill.background()
            ring.line.color.rgb = C_CYAN
            ring.line.width = Pt(2)

            hub = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(5.66), top_m + Inches(1.5), Inches(2.0), Inches(2.0))
            hub.fill.solid()
            hub.fill.fore_color.rgb = C_BLUE
            hub.line.fill.background()
            tf_hub = hub.text_frame
            self._set_tf_margins(tf_hub, top=4, bottom=4, left=4, right=4)
            set_para(tf_hub.paragraphs[0], s_data.get("hub_label", "正泰生态\n中枢矩阵"), font_size=15, bold=True, color_rgb=C_WHITE, align=PP_ALIGN.CENTER)

            nodes = s_data.get("nodes", [
                {"title": "终端客户与业主", "desc": "需求牵引与场景体验"},
                {"title": "系统集成商", "desc": "联合开发与交付实施"},
                {"title": "设计院与专家", "desc": "标准制定与技术前瞻"},
                {"title": "供应与制造伙伴", "desc": "品质保障与极速履约"}
            ])
            pos = [
                (Inches(0.8), top_m + Inches(0.5)),
                (Inches(8.53), top_m + Inches(0.5)),
                (Inches(0.8), top_m + Inches(3.2)),
                (Inches(8.53), top_m + Inches(3.2))
            ]
            for idx, nd in enumerate(nodes[:4]):
                n_left, n_top = pos[idx]
                card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, n_left, n_top, Inches(4.0), Inches(1.3))
                card.fill.solid()
                card.fill.fore_color.rgb = C_BLUE_BG
                card.line.color.rgb = C_BLUE
                card.line.width = Pt(1)

                tb = slide.shapes.add_textbox(n_left + Inches(0.15), n_top + Inches(0.15), Inches(3.7), Inches(1.0))
                tf = tb.text_frame
                tf.word_wrap = True
                self._set_tf_margins(tf, top=6, bottom=6, left=6, right=6)
                set_para(tf.paragraphs[0], nd.get("title", ""), font_size=13.5, bold=True, color_rgb=C_BLUE)
                p_d = tf.add_paragraph()
                set_para(p_d, nd.get("desc", ""), font_size=11, bold=False, color_rgb=C_DARK)
                p_d.space_before = Pt(4)

    def _render_table(self, slide, s_data: Dict[str, Any], arch: str):
        """ARCH_TABLE: the single generic content layout (multi-level header, zebra rows)."""
        self._add_body_master(slide, s_data.get("title", ""), s_data.get("category"))

        headers = s_data["headers"]
        rows = s_data["rows"]
        levels = s_data.get("levels") or [1]
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

    def _render_gantt_table(self, slide, s_data: Dict[str, Any], arch: str):
        """Engine 12: Gantt Schedule Table (ARCH_29)"""
        self._add_body_master(slide, s_data.get("title", "项目排期与推进进度甘特表"), s_data.get("category", "甘特排期"))
        top_m = Inches(1.6)

        table_shape = slide.shapes.add_table(6, 6, Inches(0.8), top_m, Inches(11.73), Inches(4.8))
        table = table_shape.table

        headers = ["阶段与关键任务", "责任人", "Q1 排期", "Q2 排期", "Q3 排期", "Q4 排期"]
        col_widths = [Inches(3.73), Inches(1.5), Inches(1.62), Inches(1.62), Inches(1.62), Inches(1.62)]
        for idx, width in enumerate(col_widths):
            table.columns[idx].width = width

        for idx, text in enumerate(headers):
            cell = table.cell(0, idx)
            cell.fill.solid()
            cell.fill.fore_color.rgb = C_BLUE
            tf_c = cell.text_frame
            self._set_tf_margins(tf_c, top=6, bottom=6, left=6, right=6)
            set_para(tf_c.paragraphs[0], text, font_size=12, bold=True, color_rgb=C_WHITE, align=PP_ALIGN.CENTER)

        task_rows = s_data.get("tasks", [
            ["1. 方案设计与规范冻结", "张经理", "■ 部署中", "✔ 已完成", "-", "-"],
            ["2. 核心系统开发与联调", "李工", "-", "■ 部署中", "■ 部署中", "-"],
            ["3. 试点验证与 PoC 测试", "王工", "-", "-", "■ 部署中", "-"],
            ["4. 全局上线与商业推广", "赵经理", "-", "-", "-", "■ 部署中"],
            ["5. 复盘总结与持续迭代", "刘工", "-", "-", "-", "■ 部署中"]
        ])

        for row_idx, r_data in enumerate(task_rows[:5]):
            for col_idx, cell_text in enumerate(r_data[:6]):
                cell = table.cell(row_idx + 1, col_idx)
                cell.fill.solid()
                cell.fill.fore_color.rgb = C_LIGHT_BG if row_idx % 2 == 1 else C_WHITE
                align = PP_ALIGN.LEFT if col_idx == 0 else PP_ALIGN.CENTER
                color = C_BLUE if "部署" in cell_text or "完成" in cell_text else C_DARK
                tf_cell = cell.text_frame
                self._set_tf_margins(tf_cell, top=6, bottom=6, left=6, right=6)
                set_para(tf_cell.paragraphs[0], cell_text, font_size=11, bold=("部署" in cell_text or "完成" in cell_text), color_rgb=color, align=align)


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
        
        summary_bullets = s_data.get("summary_bullets", [
            "主营业务营收稳步上扬，同比增长显著超出行业大盘",
            "战略新品替代率持续攀升，高附加值产品占比突破 45%",
            "海外业务保持高速扩张态势，全球交付履约韧性进一步夯实"
        ])
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
        
        slices = s_data.get("slices", [
            {"label": "新能源与绿色电工", "value": 42, "desc": "光伏、储能与智能配电方案高速增长"},
            {"label": "智能电气核心主业", "value": 35, "desc": "低压元器件与成套设备稳健支撑"},
            {"label": "工业自动化与物联网", "value": 15, "desc": "智慧能效管理与工业物联软件平台"},
            {"label": "海外新兴市场布局", "value": 8, "desc": "一带一路沿线及欧美战略新兴市场"}
        ])
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

    def _render_rich_chart(self, slide, s_data: Dict[str, Any], arch: str):
        """Vector Charts & Graphics Engine (ARCH_16_RICH_CHART, Radar, Combo, Diverging, Evolution, Heatmap)"""
        self._add_body_master(slide, s_data.get("title", "数据量化与战略对标看板"), s_data.get("category", "量化对标"))
        top_m = Inches(1.6)
        full_width = s_data.get("full_width", False)
        
        # Determine chart type from archetype name or explicit property
        chart_kind = s_data.get("chart_type", "").lower()
        if not chart_kind:
            if "RADAR" in arch:
                chart_kind = "radar"
            elif "COMBO" in arch or "DUAL_AXIS" in arch:
                chart_kind = "combo"
            elif "DIVERGING" in arch:
                chart_kind = "diverging"
            elif "EVOLUTION" in arch:
                chart_kind = "evolution"
            elif "HEATMAP" in arch or "MATRIX" in arch:
                chart_kind = "heatmap"
            elif "WATERFALL" in arch:
                chart_kind = "waterfall"
            elif "SANKEY" in arch:
                chart_kind = "sankey"
            elif "FUNNEL" in arch:
                chart_kind = "funnel"
            elif "GAUGE" in arch or "BULLET" in arch:
                chart_kind = "gauge"
            elif "STACKED_AREA" in arch or "AREA" in arch:
                chart_kind = "stacked_area"
            else:
                chart_kind = "radar" if "categories" in s_data and "series" in s_data else "combo"

        chart_w = Inches(11.73) if full_width else Inches(6.5)
        chart_h = Inches(5.0)
        img_w_in = 11.73 if full_width else 6.5
        img_h_in = 5.0
        
        chart_buf = None
        try:
            if chart_kind == "radar":
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
            elif chart_kind in ("combo", "dual_axis"):
                categories = s_data.get("categories", ["2022", "2023", "2024", "2025", "2026E"])
                bar_series = s_data.get("bar_series", {
                    "name": "业务营收", "values": [120, 155, 195, 245, 320], "unit": "亿", "color": "#1E50E6"
                })
                line_series = s_data.get("line_series", {
                    "name": "同比增速", "values": [16.5, 29.1, 25.8, 25.6, 30.6], "unit": "%", "color": "#14C832"
                })
                chart_buf = ChintVectorChartBuilder.render_combo_chart(
                    categories=categories,
                    bar_series=bar_series,
                    line_series=line_series,
                    title=s_data.get("chart_title", ""),
                    figsize=(img_w_in, img_h_in)
                )
            elif chart_kind == "diverging":
                categories = s_data.get("categories", ["新能源光伏", "智能电网", "数据中心", "轨道交通", "传统工商业", "高耗能冶金"])
                values = s_data.get("values", [42.5, 31.0, 26.8, 18.2, -8.5, -16.4])
                chart_buf = ChintVectorChartBuilder.render_diverging_bar(
                    categories=categories,
                    values=values,
                    title=s_data.get("chart_title", ""),
                    unit=s_data.get("unit", "%"),
                    figsize=(img_w_in, img_h_in)
                )
            elif chart_kind == "evolution":
                stages = s_data.get("stages", ["第一代标准断路器", "第二代数显断路器", "第三代物联网断路器", "第四代AI自愈断路器"])
                values = s_data.get("values", [65, 78, 89, 98])
                sub_labels = s_data.get("sub_labels", ["基础保护", "状态监测", "云边联动", "自主决策"])
                chart_buf = ChintVectorChartBuilder.render_evolution_chart(
                    stages=stages,
                    values=values,
                    sub_labels=sub_labels,
                    title=s_data.get("chart_title", ""),
                    unit=s_data.get("unit", "分"),
                    figsize=(img_w_in, img_h_in)
                )
            elif chart_kind == "heatmap":
                row_labels = s_data.get("row_labels", ["NXA 系列", "NA8 系列", "NM8N 系列", "NXM 系列"])
                col_labels = s_data.get("col_labels", ["集中光伏", "工商业储能", "智算中心", "轨道交通", "重工制造"])
                data_matrix = s_data.get("data_matrix", [
                    [95, 92, 96, 94, 90],
                    [90, 88, 92, 95, 86],
                    [85, 94, 88, 82, 92],
                    [80, 85, 78, 75, 88]
                ])
                chart_buf = ChintVectorChartBuilder.render_heatmap_matrix(
                    row_labels=row_labels,
                    col_labels=col_labels,
                    data_matrix=data_matrix,
                    title=s_data.get("chart_title", ""),
                    figsize=(img_w_in, img_h_in)
                )
            elif chart_kind == "waterfall":
                categories = s_data.get("categories", ["2025基准净利", "销量规模增长", "高端新品溢价", "原材料成本上涨", "数字化研发投入", "2026E净利"])
                values = s_data.get("values", [180.0, 52.0, 36.0, -18.0, -15.0, 235.0])
                chart_buf = ChintVectorChartBuilder.render_waterfall_chart(
                    categories=categories,
                    values=values,
                    initial_value=s_data.get("initial_value", None),
                    title=s_data.get("chart_title", ""),
                    unit=s_data.get("unit", "万"),
                    figsize=(img_w_in, img_h_in)
                )
            elif chart_kind == "sankey":
                flows = s_data.get("flows", None)
                nodes = s_data.get("nodes", None)
                links = s_data.get("links", None)
                chart_buf = ChintVectorChartBuilder.render_sankey_chart(
                    flows=flows,
                    nodes=nodes,
                    links=links,
                    title=s_data.get("chart_title", ""),
                    unit=s_data.get("unit", "万"),
                    figsize=(img_w_in, img_h_in)
                )
            elif chart_kind == "funnel":
                stages = s_data.get("stages", ["线索获取", "技术交流", "PoC 试点", "招投标入围", "商务签约"])
                values = s_data.get("values", [1200, 750, 420, 260, 180])
                conversion_rates = s_data.get("conversion_rates", None)
                chart_buf = ChintVectorChartBuilder.render_funnel_chart(
                    stages=stages,
                    values=values,
                    conversion_rates=conversion_rates,
                    title=s_data.get("chart_title", ""),
                    unit=s_data.get("unit", "个"),
                    figsize=(img_w_in, img_h_in)
                )
            elif chart_kind in ("gauge", "bullet"):
                current_val = float(s_data.get("current_val", s_data.get("value", 92.4)))
                target_val = float(s_data.get("target_val", 100.0))
                min_val = float(s_data.get("min_val", 0.0))
                max_val = float(s_data.get("max_val", 100.0))
                subtitle = s_data.get("subtitle", "")
                chart_buf = ChintVectorChartBuilder.render_gauge_kpi_chart(
                    current_val=current_val,
                    target_val=target_val,
                    min_val=min_val,
                    max_val=max_val,
                    title=s_data.get("chart_title", ""),
                    subtitle=subtitle,
                    unit=s_data.get("unit", "%"),
                    figsize=(img_w_in, img_h_in)
                )
            elif chart_kind in ("stacked_area", "area"):
                categories = s_data["categories"]
                series_data = s_data["series"]
                chart_buf = ChintVectorChartBuilder.render_stacked_area_chart(
                    categories=categories,
                    series_data=series_data,
                    title=s_data.get("chart_title", ""),
                    unit=s_data.get("unit", "亿"),
                    figsize=(img_w_in, img_h_in)
                )
            else:
                raise ValueError(f"Unsupported chart type: {chart_kind}")
        except Exception as e:
            raise ValueError(f"{arch} {chart_kind} chart rendering failed: {e}") from e

        if chart_buf is not None:
            slide.shapes.add_picture(chart_buf, Inches(0.8), top_m, chart_w, chart_h)
            print(f"[WARN] {arch} is rendered as an image; chart data is not directly editable in PowerPoint.")

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

    def _render_fallback(self, slide, s_data: Dict[str, Any], arch: str):
        """Fallback Engine for Unknown Archetype IDs"""
        print(f"[WARN] Engine encountered unknown archetype '{arch}', rendering fallback body card.")
        self._add_body_master(slide, s_data.get("title", "未定义版式页"), s_data.get("category", "默认版式"))
        bg = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.6), Inches(11.73), Inches(5.0))
        bg.fill.solid()
        bg.fill.fore_color.rgb = C_LIGHT_BG
        bg.line.color.rgb = C_BORDER
        bg.line.width = Pt(1)

        tb = slide.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(11.33), Inches(4.5))
        tf = tb.text_frame
        tf.word_wrap = True
        self._set_tf_margins(tf, top=8, bottom=8, left=8, right=8)
        bullets = s_data.get("bullets", s_data.get("details", []))
        for j, b in enumerate(bullets):
            p = tf.paragraphs[0] if j == 0 else tf.add_paragraph()
            set_para(p, f"• {b}", font_size=13, bold=False, color_rgb=C_DARK)
            p.space_before = Pt(10)

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

        # 34 Archetype Semantic Alias Dispatch Router
        ENGINE_ROUTER = {
            # 1. Master Frames
            "ARCH_01_COVER": self._render_master_frame,
            "ARCH_01_COVER_EARTH": self._render_master_frame,
            "ARCH_01_EARTH_COVER": self._render_master_frame,
            "ARCH_01_COVER_CITY": self._render_master_frame,
            "ARCH_01_CITY_COVER": self._render_master_frame,
            "ARCH_02_TOC": self._render_master_frame,
            "ARCH_02_FROSTED_GRID": self._render_master_frame,
            "ARCH_02_TOC_LIST": self._render_master_frame,
            "ARCH_02_RIBBON_TOC": self._render_master_frame,
            "ARCH_03_CHAPTER": self._render_master_frame,
            "ARCH_11_CLOSING": self._render_master_frame,
            "ARCH_11_CLOSING_MOSAIC": self._render_master_frame,
            "ARCH_11_MOSAIC_CLOSING": self._render_master_frame,
            "ARCH_11_CLOSING_BRAND": self._render_master_frame,
            "ARCH_11_SLOGAN_CLOSING": self._render_master_frame,
            "ARCH_15_CONTACT_US": self._render_master_frame,
            "ARCH_15_CONTACT": self._render_master_frame,

            # 2. Dual-Pane Split
            "ARCH_07_PROBLEM_SOLUTION_SWOT": self._render_dual_pane_split,
            "ARCH_21_BEFORE_AFTER_DIFF": self._render_dual_pane_split,
            "ARCH_21_BEFORE_AFTER": self._render_dual_pane_split,
            "ARCH_22_PROBLEM_IMPROVE_SPLIT": self._render_dual_pane_split,
            "ARCH_22_PROBLEM_IMPROVE": self._render_dual_pane_split,

            # 3. Hero Split Pane
            "ARCH_10_CASE_STUDY": self._render_hero_split_pane,
            "ARCH_13_GLOBAL_FOOTPRINT": self._render_hero_split_pane,
            "ARCH_19_HERO_METRIC_SPLIT": self._render_hero_split_pane,
            "ARCH_19_HERO_METRIC": self._render_hero_split_pane,

            # 4. N-Column Card Grid
            "ARCH_04_KPI_DASHBOARD": self._render_n_column_card_grid,
            "ARCH_05_MULTI_COLUMN_CARDS": self._render_n_column_card_grid,
            "ARCH_12_TEAM_PROFILE": self._render_n_column_card_grid,
            "ARCH_18_KPI_METRIC_GRID": self._render_n_column_card_grid,
            "ARCH_18_METRIC_GRID": self._render_n_column_card_grid,
            "ARCH_23_RISK_MATRIX_RESPONSE": self._render_n_column_card_grid,
            "ARCH_23_RISK_MATRIX": self._render_n_column_card_grid,
            "ARCH_24_MISSION_VISION_VALUES": self._render_n_column_card_grid,
            "ARCH_24_CULTURE": self._render_n_column_card_grid,
            "ARCH_33_HONOR_CERTIFICATION": self._render_n_column_card_grid,
            "ARCH_33_HONOR": self._render_n_column_card_grid,

            # Charts
            "ARCH_16_CHART_BAR_TREND": self._render_chart_bar_trend,
            "ARCH_16_BAR_CHART": self._render_chart_bar_trend,
            "ARCH_16_CHART_TREND": self._render_chart_bar_trend,
            "ARCH_16_RICH_CHART": self._render_rich_chart,
            "ARCH_16_RADAR": self._render_rich_chart,
            "ARCH_16_COMBO": self._render_rich_chart,
            "ARCH_16_DUAL_AXIS": self._render_rich_chart,
            "ARCH_16_DIVERGING": self._render_rich_chart,
            "ARCH_16_HEATMAP": self._render_rich_chart,
            "ARCH_16_EVOLUTION": self._render_rich_chart,
            "ARCH_16_MATRIX": self._render_rich_chart,
            "ARCH_16_WATERFALL": self._render_rich_chart,
            "ARCH_16_SANKEY": self._render_rich_chart,
            "ARCH_16_FUNNEL": self._render_rich_chart,
            "ARCH_16_GAUGE": self._render_rich_chart,
            "ARCH_16_BULLET": self._render_rich_chart,
            "ARCH_16_STACKED_AREA": self._render_rich_chart,
            "ARCH_16_AREA": self._render_rich_chart,
            "ARCH_17_CHART_PIE_DONUT": self._render_chart_pie_donut,
            "ARCH_17_PIE_CHART": self._render_chart_pie_donut,
            "ARCH_17_DONUT_CHART": self._render_chart_pie_donut,

            # 5. Horizontal Pipeline & Sequential
            "ARCH_06_TIMELINE_ROADMAP": self._render_horizontal_pipeline,
            "ARCH_25_PROCESS_STEP_HORIZONTAL": self._render_horizontal_pipeline,
            "ARCH_25_PROCESS_STEP": self._render_horizontal_pipeline,
            "ARCH_27_STEP_LADDER_MATURITY": self._render_horizontal_pipeline,
            "ARCH_27_MATURITY_LADDER": self._render_horizontal_pipeline,
            "ARCH_28_WATERFALL_DIAMOND": self._render_horizontal_pipeline,
            "ARCH_28_DIAMOND_PROCESS": self._render_horizontal_pipeline,
            "ARCH_30_MILESTONE_LIST_BADGE": self._render_horizontal_pipeline,
            "ARCH_30_MILESTONE_LIST": self._render_horizontal_pipeline,

            # 6. Stepped Funnel
            "ARCH_26_FUNNEL_CONVERSION": self._render_funnel_stepped,
            "ARCH_26_FUNNEL": self._render_funnel_stepped,

            # 7. 2x2 Matrix Quadrant
            "ARCH_20_SWOT_TOWS_MATRIX": self._render_matrix_2x2_quadrant,
            "ARCH_20_SWOT_MATRIX": self._render_matrix_2x2_quadrant,
            "ARCH_20_TOWS": self._render_matrix_2x2_quadrant,

            # 8. Flat Grid Matrix
            "ARCH_09_SOLUTION_GRID": self._render_matrix_grid_flat,
            "ARCH_34_PARTNER_LOGO_WALL": self._render_matrix_grid_flat,
            "ARCH_34_PARTNER_WALL": self._render_matrix_grid_flat,

            # 9. Platform Architecture
            "ARCH_08_PLATFORM_ARCHITECTURE": self._render_platform_architecture,

            # 10. Pillars and Base
            "ARCH_31_THREE_PILLARS_PLATFORM": self._render_pillars_and_base,
            "ARCH_31_THREE_PILLARS": self._render_pillars_and_base,

            # 11. Circular Hub Topology
            "ARCH_14_CONCENTRIC_HUB": self._render_circular_hub_topology,
            "ARCH_06_CONCENTRIC_HUB": self._render_circular_hub_topology,
            "ARCH_32_ECOSYSTEM_CIRCULAR": self._render_circular_hub_topology,
            "ARCH_32_ECOSYSTEM": self._render_circular_hub_topology,

            # 12. Gantt Table
            "ARCH_29_GANTT_SCHEDULE_TABLE": self._render_gantt_table,
            "ARCH_29_GANTT": self._render_gantt_table,
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
            slide = self.prs.slides.add_slide(self.blank_layout)

            # Purge placeholder ghost shapes
            for shape in list(slide.shapes):
                if shape.is_placeholder:
                    sp = shape._element
                    sp.getparent().remove(sp)

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
