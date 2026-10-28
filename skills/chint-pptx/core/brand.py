"""CHINT typography and logo normalization shared by every deck workflow."""
from __future__ import annotations

import hashlib
from pathlib import Path

from pptx.oxml import parse_xml
from pptx.oxml.ns import nsdecls, qn
from pptx.util import Inches


FONT_FAMILY = "正泰拓新体"
LOGO_BOX = (11.415, 0.0, 1.332, 1.002)


def _walk_shapes(shapes):
    for shape in shapes:
        yield shape
        if getattr(shape, "shape_type", None) == 6:  # grouped shapes
            yield from _walk_shapes(shape.shapes)


def _set_run_font(run, family: str) -> None:
    run.font.name = family
    r_pr = run._r.get_or_add_rPr()
    for tag in ("a:latin", "a:ea", "a:cs"):
        node = r_pr.find(qn(tag))
        if node is None:
            node = parse_xml(f"<{tag} {nsdecls('a')}/>")
            r_pr.append(node)
        node.set("typeface", family)


def normalize_slide_text(slide, family: str = FONT_FAMILY) -> None:
    """Set explicit Latin, East Asian, and complex-script faces on editable text."""
    for shape in _walk_shapes(slide.shapes):
        if getattr(shape, "has_text_frame", False):
            for paragraph in shape.text_frame.paragraphs:
                for run in paragraph.runs:
                    _set_run_font(run, family)
        if getattr(shape, "has_table", False):
            for row in shape.table.rows:
                for cell in row.cells:
                    for paragraph in cell.text_frame.paragraphs:
                        for run in paragraph.runs:
                            _set_run_font(run, family)
        if getattr(shape, "has_chart", False):
            chart = shape.chart
            axes = []
            for axis_name in ("category_axis", "value_axis"):
                try:
                    axes.append(getattr(chart, axis_name))
                except (AttributeError, ValueError):
                    continue
            for axis in axes:
                if axis is not None:
                    try:
                        axis.tick_labels.font.name = family
                    except (AttributeError, ValueError):
                        pass
            if chart.has_legend:
                try:
                    chart.legend.font.name = family
                except (AttributeError, ValueError):
                    pass
            for plot in chart.plots:
                try:
                    labels = plot.data_labels
                    has_visible_labels = any(getattr(labels, flag, False) for flag in
                                             ("show_value", "show_category_name", "show_series_name",
                                              "show_legend_key", "show_percentage", "show_bubble_size"))
                    if plot.has_data_labels and has_visible_labels:
                        labels.font.name = family
                except (AttributeError, ValueError):
                    pass
            if chart.has_title:
                for paragraph in chart.chart_title.text_frame.paragraphs:
                    for run in paragraph.runs:
                        _set_run_font(run, family)


def _logo_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _is_logo_shape(shape, logo_digest: str, bounds) -> bool:
    if getattr(shape, "shape_type", None) != 13:
        return False
    left, top, right, bottom = bounds
    try:
        return (
            hashlib.sha256(shape.image.blob).hexdigest() == logo_digest
            and shape.left < right and shape.left + shape.width > left
            and shape.top < bottom and shape.top + shape.height > top
        )
    except (AttributeError, KeyError, ValueError):
        return False


def _shape_overlaps_bounds(shape, bounds) -> bool:
    left, top, right, bottom = bounds
    return (shape.left < right and shape.top < bottom
            and shape.left + shape.width > left
            and shape.top + shape.height > top)


def _logo_shapes(shapes, logo_digest: str, bounds):
    return [shape for shape in _walk_shapes(shapes) if _is_logo_shape(shape, logo_digest, bounds)]


def _master_is_visible(slide) -> bool:
    layout = slide.slide_layout
    return slide._element.get("showMasterSp") != "0" and layout._element.get("showMasterSp") != "0"


def _logo_is_suppressed(slide) -> bool:
    return slide.slide_layout.name == "节标题" or slide._element.get("showMasterSp") == "0"


def _inherited_logo_shapes(slide, logo_digest: str, bounds):
    layout = slide.slide_layout
    logos = _logo_shapes(layout.shapes, logo_digest, bounds)
    if _master_is_visible(slide):
        logos.extend(_logo_shapes(layout.slide_master.shapes, logo_digest, bounds))
    return logos


def _master_has_logo(slide, logo_digest: str, x_limit: int, y_limit: int) -> bool:
    """Return whether one visible layout or master layer already supplies the badge."""
    width, height = Inches(LOGO_BOX[2]), Inches(LOGO_BOX[3])
    bounds = (x_limit, y_limit, x_limit + width, y_limit + height)
    return bool(_inherited_logo_shapes(slide, logo_digest, bounds))


def visible_logo_occurrences(slide, logo_digest: str, box=LOGO_BOX):
    """Count effective upper-right marks, accounting for slide, layout, and master layers."""
    left, top, width, height = box
    left_emu, top_emu = Inches(left), Inches(top)
    right_emu, bottom_emu = Inches(left + width), Inches(top + height)
    bounds = (left_emu, top_emu, right_emu, bottom_emu)
    explicit = _logo_shapes(slide.shapes, logo_digest, bounds)
    inherited = _inherited_logo_shapes(slide, logo_digest, bounds)
    obscured = False
    for shape in _walk_shapes(slide.shapes):
        if getattr(shape, "shape_type", None) != 13 or _is_logo_shape(shape, logo_digest, bounds):
            continue
        if _shape_overlaps_bounds(shape, bounds):
            obscured = True
    visible = len(explicit) if obscured else len(explicit) + len(inherited)
    return visible, len(explicit), len(inherited), obscured


def _deduplicate_shared_logo_layers(prs, logo_digest: str, bounds) -> None:
    """Remove repeated logo pictures from shared layers without editing the source file."""
    for master in prs.slide_masters:
        logos = _logo_shapes(master.shapes, logo_digest, bounds)
        for duplicate in logos[1:]:
            duplicate._element.getparent().remove(duplicate._element)

    for layout in prs.slide_layouts:
        layout_logos = _logo_shapes(layout.shapes, logo_digest, bounds)
        master_visible = layout._element.get("showMasterSp") != "0"
        master_logos = _logo_shapes(layout.slide_master.shapes, logo_digest, bounds) if master_visible else []
        duplicates = layout_logos if master_logos else layout_logos[1:]
        for duplicate in duplicates:
            duplicate._element.getparent().remove(duplicate._element)


def ensure_top_right_logo(slide, logo_path: str, box=LOGO_BOX) -> None:
    """Leave one CHINT badge on an interior slide, accounting for a covering image."""
    path = Path(logo_path)
    digest = _logo_hash(path)
    left, top, width, height = box
    left_emu, top_emu = Inches(left), Inches(top)
    right_emu, bottom_emu = Inches(left + width), Inches(top + height)
    bounds = (left_emu, top_emu, right_emu, bottom_emu)
    slide_logos = _logo_shapes(slide.shapes, digest, bounds)
    inherited_logos = _inherited_logo_shapes(slide, digest, bounds)
    obscured = False

    for shape in _walk_shapes(slide.shapes):
        if (getattr(shape, "shape_type", None) == 13
                and not _is_logo_shape(shape, digest, bounds)
                and _shape_overlaps_bounds(shape, bounds)):
            obscured = True

    if inherited_logos and not obscured:
        for duplicate in slide_logos:
            duplicate._element.getparent().remove(duplicate._element)
        return

    if slide_logos:
        keep = slide_logos[-1]
        for duplicate in slide_logos[:-1]:
            duplicate._element.getparent().remove(duplicate._element)
        keep.left, keep.top = left_emu, top_emu
        keep.width, keep.height = Inches(width), Inches(height)
        element = keep._element
        parent = element.getparent()
        if parent is not None:
            parent.append(element)
        return
    slide.shapes.add_picture(str(path), left_emu, top_emu, Inches(width), Inches(height))


def uses_template_edge_mark(slide, media_directory: str) -> bool:
    """Recognize the official cover/closing artwork whose logo already lives elsewhere."""
    if slide.slide_layout.name in {"标题幻灯片", "末尾幻灯片"}:
        return True
    known = []
    for name in ("cover_26_bg.jpg", "closing_26_bg.jpg"):
        asset = Path(media_directory) / name
        if asset.is_file():
            known.append(_logo_hash(asset))
    for source in (slide.shapes, slide.slide_layout.shapes):
        for shape in _walk_shapes(source):
            if shape.shape_type == 13:
                try:
                    if hashlib.sha256(shape.image.blob).hexdigest() in known:
                        return True
                except (AttributeError, KeyError, ValueError):
                    continue
    return False


def apply_brand(prs, logo_path: str, *, first_and_last_use_template_marks: bool = True) -> None:
    """Apply editable-text fonts and a single interior CHINT badge to the whole deck."""
    media_directory = str(Path(logo_path).parent)
    digest = _logo_hash(Path(logo_path))
    left, top, width, height = LOGO_BOX
    bounds = (Inches(left), Inches(top), Inches(left + width), Inches(top + height))
    _deduplicate_shared_logo_layers(prs, digest, bounds)
    for slide in prs.slides:
        normalize_slide_text(slide)
        if first_and_last_use_template_marks and uses_template_edge_mark(slide, media_directory):
            continue
        if _logo_is_suppressed(slide):
            for duplicate in _logo_shapes(slide.shapes, digest, bounds):
                duplicate._element.getparent().remove(duplicate._element)
            continue
        ensure_top_right_logo(slide, logo_path)
