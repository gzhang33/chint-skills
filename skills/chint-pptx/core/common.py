#!/usr/bin/env python3
"""chint-pptx 共享助手（core 四模块 + 引擎入口的唯一定义源）。

这批函数此前在 `scripts/shell_rebuild_engine.py` 与 `core/{planner,renderer,analyzer}.py`
各存一份（审查发现：其中 `appended_cover_suffix` / `looks_like_introduction_suffix`
是**校验规则**——封面禁止追加后缀的硬错误；两份独立实现意味着任一边改动另一边不会同步，
而门禁只走其中一边）。故收敛至此，四处一律 import 本模块。

本模块只依赖 python-pptx 与标准库，不 import 任何 core.*（避免循环依赖）。
"""
from __future__ import annotations

import os
import re

from pptx.dml.color import RGBColor

from pptx import Presentation
from pptx.util import Emu

# ---- 共享常量（此前 engine 与 planner 各存一份）----
EMU = 914400
DESIGN_W, DESIGN_H = 13.333, 7.5          # 2026 VI 参考画布（英寸）
LANG_ZH, LANG_EN = "zh", "en"
LANG_CJK_THRESHOLD = 0.30                 # CJK 占比阈值：> 此值判中文外壳
_CJK_RE = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")


def shell_font_path() -> str:
    """CHINTinno-Bold 字体路径，按本文件位置解析（与 skill 落点无关）。"""
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(root, "assets", "fonts", "CHINTinno-Bold.ttf")


def inn(value) -> float:
    return value / EMU


def emu(inches: float) -> int:
    return int(round(inches * EMU))


def rgb(hex_str: str) -> RGBColor:
    """Convert a #RRGGBB / RRGGBB string to an RGBColor (shared by engine + renderer)."""
    value = hex_str.lstrip("#")
    return RGBColor(int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16))


def canvas_scale(prs):
    """(sx, sy) of a presentation against the 2026 VI reference canvas."""
    sx = inn(prs.slide_width) / DESIGN_W
    sy = inn(prs.slide_height) / DESIGN_H
    return sx, sy


def looks_like_department(text: str) -> bool:
    stripped = (text or "").strip()
    if not stripped or len(stripped) > DEPT_NAME_MAX_LEN:
        return False
    if any(sep in stripped for sep in ("·", "／", "|", "/")):
        return False
    return not any(char.isdigit() for char in stripped)


def looks_like_introduction_suffix(tail: str) -> bool:
    return (tail or "").strip().lower() in COVER_TITLE_SUFFIXES


def appended_cover_suffix(configured: str, source: str) -> str:
    """The tail added to the source title, or '' when the configured title is not an extension."""
    configured, source = (configured or "").strip(), (source or "").strip()
    if not configured or not source or configured == source:
        return ""
    if not configured.lower().startswith(source.lower()):
        return ""
    return configured[len(source):].strip(" -–—:：·|")


# ---- 共享判定常量（此前 engine 与 planner 各存一份）----
COVER_TITLE_SUFFIXES = ("introduction", "product introduction", "overview",
                        "产品介绍", "简介", "概述")


# Effective shell language for the deck being rebuilt. Module-level for the same reason as
# _SCALE: shell helpers never see the config, and it must stay consistent between them.
_LANG = LANG_ZH

_CJK_RE = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")


# A bare department name: no product line, no year, no separator chaining. This is the
# guard the house rule exists for — a source subtitle like
# "万能式断路器产品线 · 产品管理部 2026版" is a product line plus a year stacked onto a
# department name, and reusing it verbatim would print the exact wording the rule forbids
# on a brand-new cover. Reuse still comes first *within* the shape: a source that names a
# different department keeps that department.
DEPT_NAME_MAX_LEN = 40


def skill_root() -> str:
    """skill 根目录（按本文件位置解析，与落点无关）。"""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def resolve_asset_paths(cfg: dict) -> list:
    """展开 config 资产路径中的 ${CHINT_PPTX_SKILL} 令牌，并强制存在性校验。

    令牌原由语料驱动器展开；直接调用引擎时无人展开，而渲染层是
    `if assets.get(k) and os.path.exists(...)`——缺失即**静默跳过**，成品壳页会
    整页空白却仍判 PASS。故此处补齐解析，并让缺失显式报错（不静默降级）。
    """
    root = skill_root()
    assets = cfg.get("assets") or {}
    resolved = []
    for key, raw in list(assets.items()):
        if not raw:
            continue
        text = str(raw).replace("${CHINT_PPTX_SKILL}", root).replace("$CHINT_PPTX_SKILL", root)
        text = os.path.expanduser(text)
        assets[key] = text
        if not os.path.exists(text):
            raise SystemExit(
                f"[FAIL] 资产缺失: assets.{key} = {raw}\n"
                f"        解析为: {text}\n"
                f"        skill 根目录: {root}\n"
                f"        底图缺失会让壳页整页空白——不静默跳过，请修正路径或放入资产目录。")
        resolved.append({"key": key, "path": text})
    cfg["assets"] = assets
    return resolved


# ---- 外壳文案（唯一定义源；此前 engine 与 planner 各存一份，renderer 从 planner 拿）----
SHELL_COPY = {
    LANG_ZH: {
        "department": "产品管理部",
        # 中文外壳（国内）官网用 www.chint.com；海外（英文）外壳用 www.chintglobal.com
        "closing_contact": "客服热线：400-8877-666  |  官网：www.chint.com",
    },
    LANG_EN: {
        "department": "Product Management Department",
        "closing_contact": "Customer Service Hotline : 400-8877-666  |  Website: www.chintglobal.com",
    },
}


_FONT_CACHE = {}          # font-path -> TTFont | None


def text_width_in(text: str, pt: float, font_path=None):
    """Rendered width in inches, or None when font metrics are unavailable."""
    font_path = font_path or shell_font_path()
    if font_path not in _FONT_CACHE:
        try:
            from fontTools.ttLib import TTFont
        except ImportError:
            _FONT_CACHE[font_path] = None
        else:
            try:
                _FONT_CACHE[font_path] = TTFont(font_path, fontNumber=0)
            except Exception:                        # unreadable font: degrade, never crash
                _FONT_CACHE[font_path] = None
    font = _FONT_CACHE[font_path]
    if font is None:
        return None
    cmap, hmtx = font.getBestCmap(), font["hmtx"]
    em = font["head"].unitsPerEm
    total = sum(hmtx[cmap[ord(char)]][0] for char in text if ord(char) in cmap)
    return total / em * pt / 72.0


def detect_source_language(prs):
    """('zh'|'en', cjk_ratio, letter_count) for the source deck's own text."""
    chunks = []
    for slide in prs.slides:
        for shape in slide.shapes:
            if shape.has_text_frame and (shape.text or "").strip():
                chunks.append(shape.text)
            if getattr(shape, "has_table", False):
                try:
                    for row in shape.table.rows:
                        for cell in row.cells:
                            chunks.append(cell.text or "")
                except (AttributeError, ValueError):
                    pass
    letters = [c for c in "".join(chunks) if c.isalpha() or _CJK_RE.match(c)]
    if not letters:
        return LANG_EN, 0.0, 0
    cjk = sum(1 for c in letters if _CJK_RE.match(c))
    ratio = cjk / len(letters)
    return (LANG_ZH if ratio > LANG_CJK_THRESHOLD else LANG_EN), ratio, len(letters)


def source_cover_copy(prs):
    """(title, subtitle) lifted *verbatim* from the source deck's own cover page.

    The cover is the one element whose wording is reused rather than re-authored: the
    source already carries the product's own title in its own language, and re-typing it
    in another language is precisely the defect this rule exists to remove.
    """
    if not len(prs.slides):
        return "", ""
    lines = []
    for shape in prs.slides[0].shapes:
        if not shape.has_text_frame:
            continue
        for para in shape.text_frame.paragraphs:
            # a soft line break inside one paragraph (<a:br/>) separates the cover's two
            # lines exactly like a paragraph boundary does
            for piece in re.split(r"[\v\n]", para.text or ""):
                piece = piece.strip()
                if piece:
                    lines.append(piece)
    return (lines[0] if lines else ""), (lines[1] if len(lines) > 1 else "")

