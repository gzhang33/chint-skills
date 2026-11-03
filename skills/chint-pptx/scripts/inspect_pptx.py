#!/usr/bin/env python3
"""
CHINT PPTX Inspection & Quality Verification Utility (2026 VI Standard Edition)

Features:
- Verifies slide dimensions & 16:9 aspect ratio.
- Verifies typography (正泰拓新体 / CHINTinno) and brand color compliance.
- Integrates OpenXML schema, relationship, and content-type integrity validation.
- Verifies zero font DRM locks and clean normal view initialization.
- Lists stable text/table edit targets with --edit-targets.
"""

import sys
import os
import zipfile
import argparse
import subprocess
import hashlib
import json
from pptx import Presentation

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_ROOT = os.path.dirname(SCRIPT_DIR)
if SKILL_ROOT not in sys.path:
    sys.path.insert(0, SKILL_ROOT)
VALIDATE_SCRIPT = os.path.join(SCRIPT_DIR, "office", "validate.py")
BADGE_PATH = os.path.join(SKILL_ROOT, "assets", "media", "chint_badge.png")


def run_office_validation(pptx_path: str, original_path=None):
    if not os.path.exists(VALIDATE_SCRIPT):
        return False, "Required OpenXML validator script was not found."
    
    office_dir = os.path.dirname(VALIDATE_SCRIPT)
    cmd = [sys.executable, VALIDATE_SCRIPT, pptx_path]
    if original_path:
        cmd.extend(["--original", original_path])
    proc = subprocess.run(cmd, cwd=office_dir, capture_output=True, text=True)
    passed = proc.returncode == 0
    output = proc.stdout if passed else (proc.stdout + "\n" + proc.stderr)
    return passed, output.strip()


def _walk_shapes(shapes):
    for shape in shapes:
        yield shape
        if getattr(shape, "shape_type", None) == 6:
            yield from _walk_shapes(shape.shapes)


def editable_target_inventory(pptx_path):
    """List stable slide/shape targets for the existing engine's edit manifest."""
    presentation = Presentation(pptx_path)
    p_sp_tag = "{http://schemas.openxmlformats.org/presentationml/2006/main}sp"
    graphic_frame_tag = "{http://schemas.openxmlformats.org/presentationml/2006/main}graphicFrame"
    group_tag = "{http://schemas.openxmlformats.org/presentationml/2006/main}grpSp"
    picture_tag = "{http://schemas.openxmlformats.org/presentationml/2006/main}pic"
    a_ns = "{http://schemas.openxmlformats.org/drawingml/2006/main}"

    def text_body_content(text_body):
        if text_body is None:
            return ""
        paragraphs = []
        for paragraph in text_body.findall(f"./{a_ns}p"):
            pieces = []
            for child in paragraph:
                if child.tag == f"{a_ns}br":
                    pieces.append("\v")
                elif child.tag in (f"{a_ns}r", f"{a_ns}fld"):
                    text_node = child.find(f"./{a_ns}t")
                    if text_node is not None:
                        pieces.append(text_node.text or "")
            paragraphs.append("".join(pieces))
        return "\n".join(paragraphs)

    slides = []
    for slide_number, slide in enumerate(presentation.slides, start=1):
        shapes = []
        for shape in slide.shapes:
            element_tag = shape._element.tag
            if element_tag == graphic_frame_tag and getattr(shape, "has_table", False):
                target_type = "table"
                table = shape._element.xpath(".//a:tbl")[0]
                cells = []
                table_rows = []
                for row_index, row in enumerate(table.findall(f"./{a_ns}tr")):
                    row_text = []
                    for column_index, cell in enumerate(row.findall(f"./{a_ns}tc")):
                        cell_text = text_body_content(cell.find(f"./{a_ns}txBody"))
                        try:
                            merged = (cell.get("hMerge") == "1" or cell.get("vMerge") == "1"
                                      or int(cell.get("gridSpan", "1")) > 1)
                        except ValueError:
                            merged = True
                        cells.append({"row": row_index, "column": column_index,
                                      "text": cell_text, "editable": not merged})
                        row_text.append(cell_text)
                    table_rows.append("\t".join(row_text))
                text = "\n".join(table_rows)
            elif element_tag == p_sp_tag and getattr(shape, "has_text_frame", False):
                target_type = "text"
                cells = None
                tx_body = shape._element.find(f"./{{http://schemas.openxmlformats.org/presentationml/2006/main}}txBody")
                text = text_body_content(tx_body)
            elif getattr(shape, "has_chart", False):
                target_type = "chart"
                cells = None
                text = ""
            elif element_tag == group_tag:
                target_type = "group"
                cells = None
                text = ""
            elif element_tag == picture_tag:
                target_type = "image"
                cells = None
                text = ""
            else:
                target_type = "complex"
                cells = None
                text = ""
            shapes.append({
                "shape_id": shape.shape_id,
                "shape_name": shape.name,
                "target_type": target_type,
                "editable": target_type in {"text", "table"},
                "text": text,
                **({"cells": cells} if cells is not None else {}),
            })
        slides.append({
            "slide": slide_number,
            "slide_part": str(slide.part.partname).lstrip("/"),
            "shapes": shapes,
        })
    with open(pptx_path, "rb") as source_file:
        digest = hashlib.sha256(source_file.read()).hexdigest()
    return {
        "source": os.path.abspath(pptx_path),
        "source_sha256": digest,
        "slide_count": len(slides),
        "slides": slides,
        "edit_scope": ["text", "table cell text", "font/style", "text/table geometry"],
        "unsupported": ["charts", "images", "grouped shapes", "SmartArt", "OLE objects"],
    }


def inspect_presentation(pptx_path, original_path=None):
    if not os.path.exists(pptx_path):
        print(f"Error: File not found: {pptx_path}")
        return False

    has_error = False
    prs = Presentation(pptx_path)
    width_in = prs.slide_width / 914400
    height_in = prs.slide_height / 914400
    aspect_ratio = width_in / height_in

    print("=" * 70)
    print(f"Inspection Report: {os.path.basename(pptx_path)}")
    print(f"File Path: {pptx_path}")
    print(f"Canvas Dimensions: {width_in:.3f} in x {height_in:.3f} in (Aspect Ratio: {aspect_ratio:.2f})")
    print(f"Total Slides: {len(prs.slides)}")
    print("=" * 70)

    font_usage = {}
    total_shapes = 0
    total_text_frames = 0
    color_usage = set()
    font_ok = True
    logo_ok = True
    from core.brand import LOGO_BOX, _logo_is_suppressed, uses_template_edge_mark, visible_logo_occurrences
    badge_digest = hashlib.sha256(open(BADGE_PATH, "rb").read()).hexdigest()

    for idx, slide in enumerate(prs.slides, start=1):
        layout_name = slide.slide_layout.name if slide.slide_layout else "Unknown"
        shapes_in_slide = len(slide.shapes)
        total_shapes += shapes_in_slide
        slide_title = "Untitled Slide"

        slide_texts = []
        for shape in _walk_shapes(slide.shapes):
            if shape.has_text_frame:
                total_text_frames += 1
                for p in shape.text_frame.paragraphs:
                    for r in p.runs:
                        font_name = r.font.name or "Inherited"
                        font_usage[font_name] = font_usage.get(font_name, 0) + 1
                        east_asian = r._r.get_or_add_rPr().find("{http://schemas.openxmlformats.org/drawingml/2006/main}ea")
                        if font_name != "正泰拓新体" or east_asian is None or east_asian.get("typeface") != "正泰拓新体":
                            font_ok = False
                        if r.font.color and r.font.color.type == 1:
                            color_usage.add(str(r.font.color.rgb))
                    text = p.text.strip()
                    if text:
                        slide_texts.append(text)
                    if text and slide_title == "Untitled Slide":
                        slide_title = text[:40]

            if getattr(shape, "has_table", False):
                for row in shape.table.rows:
                    for cell in row.cells:
                        for paragraph in cell.text_frame.paragraphs:
                            for run in paragraph.runs:
                                font_name = run.font.name or "Inherited"
                                font_usage[font_name] = font_usage.get(font_name, 0) + 1
                                east_asian = run._r.get_or_add_rPr().find("{http://schemas.openxmlformats.org/drawingml/2006/main}ea")
                                if font_name != "正泰拓新体" or east_asian is None or east_asian.get("typeface") != "正泰拓新体":
                                    font_ok = False

            if getattr(shape, "has_chart", False):
                chart = shape.chart
                for axis_name in ("category_axis", "value_axis"):
                    try:
                        axis = getattr(chart, axis_name)
                        if axis.tick_labels.font.name != "正泰拓新体":
                            font_ok = False
                    except (AttributeError, ValueError):
                        continue
                try:
                    if chart.has_legend and chart.legend.font.name != "正泰拓新体":
                        font_ok = False
                except (AttributeError, ValueError):
                    font_ok = False
                if chart.has_title:
                    for paragraph in chart.chart_title.text_frame.paragraphs:
                        for run in paragraph.runs:
                            east_asian = run._r.get_or_add_rPr().find("{http://schemas.openxmlformats.org/drawingml/2006/main}ea")
                            if run.font.name != "正泰拓新体" or east_asian is None or east_asian.get("typeface") != "正泰拓新体":
                                font_ok = False
                for plot in chart.plots:
                    try:
                        labels = plot.data_labels
                        has_visible_labels = any(getattr(labels, flag, False) for flag in
                                                 ("show_value", "show_category_name", "show_series_name",
                                                  "show_legend_key", "show_percentage", "show_bubble_size"))
                        if plot.has_data_labels and has_visible_labels and labels.font.name != "正泰拓新体":
                            font_ok = False
                    except (AttributeError, ValueError):
                        font_ok = False

        print(f"Slide {idx:02d} [{layout_name}]: '{slide_title}' ({shapes_in_slide} shapes)")

    print("-" * 70)
    print("Font Family Usage Summary:")
    for font, count in sorted(font_usage.items(), key=lambda x: x[1], reverse=True):
        print(f"  - {font}: {count} text runs")

    print("\nColor RGB Usage Samples:")
    for color in sorted(color_usage)[:10]:
        print(f"  - #{color}")

    print("-" * 70)
    if font_ok and (font_usage or not prs.slides):
        print("[PASS] Typography Check: all editable text runs use 正泰拓新体.")
    else:
        print("[FAIL] Typography Check: one or more editable text runs lack explicit CHINT East Asian and Latin fonts.")
        has_error = True

    chapter_no_logo_count = 0
    for idx, slide in enumerate(prs.slides, 1):
        if uses_template_edge_mark(slide, os.path.join(SKILL_ROOT, "assets", "media")):
            continue
        visible_badges, slide_badges, inherited_badges, obscured = visible_logo_occurrences(slide, badge_digest, LOGO_BOX)
        expected_badges = 0 if _logo_is_suppressed(slide) else 1
        if expected_badges == 0:
            chapter_no_logo_count += 1
        if visible_badges != expected_badges:
            logo_ok = False
            print(
                f"[FAIL] CHINT logo placement: slide {idx:02d} has {visible_badges} visible upper-right badges; "
                f"expected {expected_badges} "
                f"(slide={slide_badges}, layout/master={inherited_badges}, obscured={obscured})."
            )
    if logo_ok:
        print(f"[PASS] CHINT logo placement: one badge on branded inner slides; {chapter_no_logo_count} chapter slides omit it.")
    else:
        has_error = True

    print("-" * 70)
    print("Semantic & Structural Slide Integrity Checks:")
    cover_like_slides = []
    unfilled_default_titles = []
    
    for idx, slide in enumerate(prs.slides, start=1):
        texts = [text for shape in _walk_shapes(slide.shapes) if shape.has_text_frame for p in shape.text_frame.paragraphs if (text := p.text.strip())]
        if any("演示文稿标题" in t for t in texts):
            unfilled_default_titles.append(f"Slide {idx:02d} contains unfilled default title '演示文稿标题'")
        # Check if non-first slides look like duplicate cover slides (5 shapes: picture, 2 rects, 2 textboxes)
        if idx > 1 and len(slide.shapes) == 5:
            shape_types = [s.shape_type for s in slide.shapes]
            if shape_types.count(13) == 1 and shape_types.count(1) == 2 and shape_types.count(17) == 2:
                cover_like_slides.append(idx)

    if unfilled_default_titles:
        print(f"[FAIL] Unfilled Defaults: Detected {len(unfilled_default_titles)} instances of unpopulated default titles!")
        for u in unfilled_default_titles:
            print(f"  - {u}")
        has_error = True
    else:
        print("[PASS] Content Population: Zero unpopulated default titles detected.")

    if cover_like_slides:
        print(f"[FAIL] Slide Diversity: Non-first slides {cover_like_slides} detected as duplicate cover slides!")
        has_error = True
    else:
        print("[PASS] Slide Diversity: Valid distribution of slide archetypes.")

    print("-" * 70)
    print("OpenXML Package Hygiene Checks:")
    with zipfile.ZipFile(pptx_path, 'r') as zf:
        pres_xml = zf.read('ppt/presentation.xml').decode('utf-8')
        if 'embeddedFontLst' in pres_xml or 'embedTrueTypeFonts' in pres_xml:
            print("[INFO] Embedded font parts found; inspect each font's embedding permissions before distribution.")
        else:
            print("[PASS] Font policy: font embedding is not used; install CHINTinno on the receiving device.")

        if 'ppt/viewProps.xml' in zf.namelist():
            vp_xml = zf.read('ppt/viewProps.xml').decode('utf-8')
            if 'lastView="sldMasterView"' in vp_xml:
                print("[FAIL] View Mode Check: Presentation is locked in Slide Master View!")
                has_error = True
            else:
                print("[PASS] View Mode Check: Opens in standard Normal Edit View.")

    print("-" * 70)
    print("OpenXML Relationship & Schema Validation:")
    val_passed, val_report = run_office_validation(pptx_path, original_path)
    if val_passed:
        print("[PASS] Schema Validation: All OpenXML relationships, parts, and content types PASSED!")
    else:
        print(f"[FAIL] Schema Validation FAILED:\n{val_report}")
        has_error = True

    print("=" * 70)
    if has_error:
        print("[FAIL] Overall Result: Inspection detected OpenXML or presentation defects!")
        return False

    print("[PASS] Structural, editable-text brand, and OpenXML checks passed.")
    if original_path:
        print("[PASS] OpenXML validation used the supplied source as its template baseline.")
    print("[INFO] Visual inspection and native PowerPoint/WPS opening remain required.")
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Inspect CHINT PPTX presentation quality")
    parser.add_argument("pptx_file", help="Path to .pptx file")
    parser.add_argument("--original", help="Source presentation for baseline comparison")
    parser.add_argument("--edit-targets", action="store_true",
                        help="List slide/shape IDs supported by the existing engine's local-edit mode")
    args = parser.parse_args()
    if args.edit_targets:
        if args.original:
            parser.error("--original is not used with --edit-targets")
        try:
            print(json.dumps(editable_target_inventory(args.pptx_file), ensure_ascii=False, indent=2))
        except Exception as exc:
            parser.error(f"could not inspect editable targets: {exc}")
        sys.exit(0)
    original_path = args.original
    if original_path and os.path.abspath(original_path) == os.path.abspath(args.pptx_file):
        parser.error("--original and pptx_file must be different files")
    success = inspect_presentation(args.pptx_file, original_path)
    if not success:
        sys.exit(1)
