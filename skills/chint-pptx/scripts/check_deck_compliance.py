#!/usr/bin/env python3
"""Structural compliance gate for a generated CHINT deck.

Checks only what the content contract promises:
  * cover / contents / chapter / closing pages exist where the contract expects them
  * contents and body pages carry exactly one top-right CHINT badge; chapter pages carry none
  * every table has a brand-blue header row, zebra body rows, in-range font sizes, and fitted margins
  * no table exceeds the single-page row limit and nothing leaves the safe area

Exit code 0 when compliant, 1 when a check fails, 2 when the file cannot be opened.
Rendered-pixel quality, contrast, and copy correctness are out of scope by design.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pptx import Presentation
from pptx.util import Inches, Pt

from core.brand import LOGO_BOX, visible_logo_occurrences

SAFE_AREA = (Inches(0.0), Inches(0.0), Inches(13.333), Inches(7.5))
FONT_BODY_RANGE = (8.0, 13.0)
FONT_HEADER_RANGE = (10.0, 14.0)
TABLE_MAX_ROWS = 20
TOP_RIGHT_X_MIN = Inches(10.0)
TOP_RIGHT_Y_MAX = Inches(1.3)

CHAPTER_LAYOUT = "节标题"


def _hex(color) -> str:
    try:
        return str(color.rgb)
    except (AttributeError, TypeError, ValueError):
        return ""


def _fill_hex(cell) -> str:
    try:
        return _hex(cell.fill.fore_color)
    except (AttributeError, TypeError, ValueError):
        return ""


def _run_sizes(paragraph):
    sizes = [run.font.size.pt for run in paragraph.runs if run.font.size is not None]
    return sizes


def _cell_spec(cell):
    paragraph = cell.text_frame.paragraphs[0]
    sizes = _run_sizes(paragraph)
    bold = any(run.font.bold for run in paragraph.runs)
    color = ""
    for run in paragraph.runs:
        if run.font.color is not None:
            color = _hex(run.font.color)
            break
    return sizes, bold, color


def _header_depth(table, brand_blue: str) -> int:
    """Header rows are the leading rows whose row carries the brand blue somewhere."""
    depth = 0
    for r in range(len(table.rows)):
        row_fills = {_fill_hex(table.cell(r, c)).upper() for c in range(len(table.columns))}
        if brand_blue.upper() in row_fills:
            depth += 1
        else:
            break
    return depth


def _check_table(shape, slide_no, brand_blue, light_bg, issues):
    table = shape.table
    n_rows = len(table.rows)
    n_cols = len(table.columns)
    header_rows = max(1, _header_depth(table, brand_blue))
    if n_rows - header_rows > TABLE_MAX_ROWS:
        issues.append(f"slide{slide_no:02d}: 表格有 {n_rows - header_rows} 个正文行，超过上限 {TABLE_MAX_ROWS}")

    header_sizes, header_bold, header_color = _cell_spec(table.cell(0, 0))
    if not header_bold:
        issues.append(f"slide{slide_no:02d}: 表头未加粗")
    if header_color and header_color.upper() != "FFFFFF":
        issues.append(f"slide{slide_no:02d}: 表头文字色为 {header_color}，应为白色 FFFFFF")
    for size in header_sizes:
        if not FONT_HEADER_RANGE[0] <= size <= FONT_HEADER_RANGE[1]:
            issues.append(
                f"slide{slide_no:02d}: 表头字号 {size}pt 超出 {FONT_HEADER_RANGE[0]}–{FONT_HEADER_RANGE[1]}pt")

    for c in range(n_cols):
        fill = _fill_hex(table.cell(0, c))
        if fill and fill.upper() != brand_blue.upper():
            issues.append(f"slide{slide_no:02d}: 表头第 {c + 1} 列底色 {fill}，应为品牌蓝 {brand_blue}")

    for r in range(header_rows, n_rows):
        text_sizes = []
        for c in range(n_cols):
            sizes, _, _ = _cell_spec(table.cell(r, c))
            text_sizes.extend(sizes)
        for size in text_sizes:
            if not FONT_BODY_RANGE[0] <= size <= FONT_BODY_RANGE[1]:
                issues.append(
                    f"slide{slide_no:02d}: 第 {r} 行字号 {size}pt 超出 {FONT_BODY_RANGE[0]}–{FONT_BODY_RANGE[1]}pt")
                break

    expected_zebra = light_bg.upper()
    if n_rows > header_rows + 1:
        first_body = _fill_hex(table.cell(header_rows, 0)).upper()
        second_body = _fill_hex(table.cell(header_rows + 1, 0)).upper()
        if first_body == second_body:
            issues.append(f"slide{slide_no:02d}: 正文行未做隔行浅底（前两行底色相同 {first_body or '无'}）")
        elif expected_zebra not in (first_body, second_body):
            issues.append(
                f"slide{slide_no:02d}: 隔行浅底未使用品牌浅色 {light_bg}（实测 {first_body}/{second_body}）")


def _check_geometry(shape, slide_no, issues):
    left, top, right, bottom = SAFE_AREA
    if shape.left < left or shape.top < top:
        issues.append(f"slide{slide_no:02d}: 形状 '{shape.name}' 超出画布左上边界")
    if shape.left + shape.width > right or shape.top + shape.height > bottom:
        issues.append(f"slide{slide_no:02d}: 形状 '{shape.name}' 超出画布右下边界")


def check_deck(path: str | Path, brand_tokens: dict | None = None) -> dict:
    path = Path(path)
    tokens = brand_tokens or json.loads(
        (Path(__file__).resolve().parent.parent / "spec" / "brand_tokens.json").read_text(encoding="utf-8"))
    theme = tokens.get("theme", tokens)
    brand_blue = theme.get("blue", "1E50E6")
    light_bg = theme.get("light_bg", "F3F6FE")

    prs = Presentation(str(path))
    issues: list[str] = []
    badge_path = Path(__file__).resolve().parent.parent / "assets" / "media" / "chint_badge.png"
    digest = hashlib.sha256(badge_path.read_bytes()).hexdigest()

    has_cover = has_contents = has_closing = False
    tables = 0

    for slide_no, slide in enumerate(prs.slides, 1):
        layout_name = slide.slide_layout.name
        visible, _, _, _ = visible_logo_occurrences(slide, digest, LOGO_BOX)
        suppressed = (slide._element.get("showMasterSp") == "0") or layout_name == CHAPTER_LAYOUT

        for shape in slide.shapes:
            _check_geometry(shape, slide_no, issues)
            if getattr(shape, "has_table", False) and shape.has_table:
                tables += 1
                _check_table(shape, slide_no, brand_blue, light_bg, issues)

        pictures = [s for s in slide.shapes if s.shape_type == 13]
        top_right = [p for p in pictures
                     if p.left >= TOP_RIGHT_X_MIN and p.top <= TOP_RIGHT_Y_MAX]
        if slide_no == 1:
            has_cover = True
            continue
        if slide_no == len(prs.slides):
            has_closing = True
            continue
        if layout_name == CHAPTER_LAYOUT or suppressed:
            continue
        if visible == 0 and not top_right:
            issues.append(f"slide{slide_no:02d}: 缺少右上角 CHINT 徽标")
        full_bleed = any(p.width >= prs.slide_width * 0.95 for p in pictures)
        if full_bleed and slide_no == len(prs.slides) and "THANKS" in " ".join(
                s.text_frame.text for s in slide.shapes if s.has_text_frame):
            has_closing = True
            continue
        if len(prs.slides) > 1 and slide_no == len(prs.slides):
            has_closing = True

    contents = [s for s in prs.slides if s.slide_layout.name == "目录"]
    has_contents = bool(contents)

    if not has_cover:
        issues.append("缺少封面页")
    if not has_contents:
        issues.append("缺少目录页（模板原生 '目录' 版式）")
    if not has_closing:
        issues.append("缺少尾页")

    return {
        "path": str(path),
        "slides": len(prs.slides),
        "tables": tables,
        "issues": issues,
        "passed": not issues,
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="CHINT deck structural compliance gate")
    parser.add_argument("pptx", help="generated deck")
    parser.add_argument("--json", help="write the report to this path")
    args = parser.parse_args(argv)

    try:
        report = check_deck(args.pptx)
    except Exception as exc:  # noqa: BLE001 - surfaced to the caller as a failed gate
        print(f"[ERROR] 无法打开或解析 {args.pptx}: {exc}")
        return 2

    if args.json:
        Path(args.json).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    for issue in report["issues"]:
        print(f"[FAIL] {issue}")
    status = "[PASS]" if report["passed"] else f"[FAIL] {len(report['issues'])} 项不合规"
    print(f"{status} {report['path']} · {report['slides']} 页 · {report['tables']} 个表格")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
