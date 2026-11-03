#!/usr/bin/env python3
"""Generic source-page fidelity gate for chint-pptx **Mode B** (preserve-source-pages).

Mode B rebuilds a deck by keeping every source content page untouched and only
swapping the shell (cover / TOC / chapter dividers / closing). This tool is the
trust anchor for that promise: it proves, shape by shape, that the source pages
were *not* re-authored.

What it proves
--------------
  F1  page accounting      matched / newly added shell pages / removed pages
  F2  inventory identity   every surviving source shape still exists with the same
                           name, width, height, left edge and text (table cell text
                           included). Tables are compared by COLUMN widths and cell
                           text only: row-height micro-adjustment is the one spacing
                           change the SOP permits, and every such change is reported,
                           never silently accepted.
  F3  uniform shift only   all surviving shapes of a page moved by ONE identical
                           vertical delta (the minimal "give way" shift), never
                           re-laid-out individually. Bottom-edge furniture (the
                           decorative strip) is pinned and therefore exempt.
  F4  title grid           each mapped content page carries the two-line 2026 VI title
                           grid, and its main-title text equals the source title text.
  F5  bottom safety        no non-furniture shape is pushed ACROSS the bottom strip
                           limit by the shell rewrite. Content that already sat past
                           the line in the source is reported, not failed: the gate
                           grades the rewrite, not the author's original layout.

Canvas tolerance
----------------
Every geometric threshold is stated in 2026 VI reference inches (13.333" x 7.5") and
scaled by the deck's own canvas ratio. A deck authored on a legacy canvas (e.g. the
10" x 5.625" 16:9 that older CHINT decks use) is therefore graded on its own terms —
the reference canvas stays the yardstick, but a smaller deck is not failed merely for
being smaller. On a 13.333" x 7.5" deck every scale factor is 1.0 and behaviour is
byte-identical to a canvas-blind gate.

Page mapping
------------
By default the mapping is **inferred**: an order-preserving (monotone) alignment
between source and target pages that maximises title-text matches plus shape
fingerprint overlap. Inference is robust for the common case (source titles are
carried over verbatim) and degrades loudly, never silently. Pass ``--map`` to
override it with an explicit table.

Usage
-----
    python3 verify_preserve_source.py --source src.pptx --target out.pptx
    python3 verify_preserve_source.py --source src.pptx --target out.pptx \
        --map map.json --baseline baseline.json --json report.json

map.json        {"4": 2, "5": 3, "7": 5, ...}   target page -> source page (1-based)
baseline.json   {"allow_changed_pages": [12], "allow_removed_pages": [1, 4],
                 "allow_single_line_grid_pages": [7],
                 "allow_promoted_heading_pages": [25, 26]}

Exit codes: 0 = PASS, 1 = FAIL, 2 = usage error.
"""

from __future__ import annotations

import argparse
import json
import posixpath
import re
import sys
from dataclasses import dataclass, field
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile

SKILL_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_ROOT))
from core.output_paths import ensure_output_path

from defusedxml import ElementTree as SafeET
from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE

EMU_PER_INCH = 914400

# 2026 VI reference canvas. Thresholds below are expressed in reference inches and
# scaled by the deck's own canvas ratio (see "Canvas tolerance" in the module docstring).
DESIGN_W, DESIGN_H = 13.333, 7.5
FULL_BLEED_MIN_W, FULL_BLEED_MIN_H = 12.0, 4.5
GRID_LEFT, GRID_TOP_MAX = 0.8, 0.95
DEFAULT_BOTTOM_LIMIT = 7.30

FOOTER_TEXT_RE = re.compile(r"(copyright|©|版权|保留所有权利)", re.IGNORECASE)
# Bare ("9"), dashed ("- 9 -") and over-total ("9 / 19", "9|19") page numbers are all
# produced or permitted by the house footer spec; a regex that only accepted the bare
# form made the gate report the standard page-number box as an unauthorised addition.
PAGE_NUM_RE = re.compile(r"^\s*[-–—]?\s*\d{1,3}\s*(?:[/|]\s*\d{1,3}\s*)?[-–—]?\s*$")
TITLE_SHAPE_NAMES = {"标题 1", "标题1", "Title 1", "Title 2"}

# Shapes whose top edge sits at/below this offset from the bottom limit are treated
# as pinned bottom-edge furniture (decorative strip): never shifted, never bounded.
FURNITURE_TOP_MARGIN = 0.05

# Top-band geometry for the title-carrier fallback (reference inches). A deck whose page
# titles live in a BODY placeholder -- or in a text box narrower than the 5.0" heuristic --
# has no idx==0 title at all, so the three specific rules in find_source_title all miss.
# This source is exactly that: all 33 page titles sit in the top band as body placeholders
# or narrow text boxes, and without the fallback the title role resolves to None, the
# source title is never removed, and the rebuilt grid lands on top of it -- a double title
# on every single page.
TOP_BAND_MAX_TOP = 1.15
TOP_BAND_MIN_LEFT = 1.30
TOP_BAND_MIN_W = 3.0


# --------------------------------------------------------------------------- #
# geometry helpers
# --------------------------------------------------------------------------- #
def inches(value):
    return None if value is None else value / EMU_PER_INCH


def canvas_scale(deck):
    """(sx, sy) of a deck against the 2026 VI reference canvas — 1.0 when it matches."""
    sx = (inches(deck.slide_width) or DESIGN_W) / DESIGN_W
    sy = (inches(deck.slide_height) or DESIGN_H) / DESIGN_H
    return sx, sy


def rect(shape):
    left, top = inches(shape.left), inches(shape.top)
    width, height = inches(shape.width), inches(shape.height)
    if None in (left, top, width, height) or width <= 0 or height <= 0:
        return None
    if getattr(shape, "has_table", False):
        col_sum = inches(sum(c.width for c in shape.table.columns))
        row_sum = inches(sum(r.height for r in shape.table.rows))
        width = col_sum or width
        height = row_sum or height
    return (left, top, left + width, top + height)


def is_full_bleed_background(shape, scale=(1.0, 1.0)) -> bool:
    """Page-filling artwork: pinned, never shifted, never bounded."""
    if shape.shape_type != MSO_SHAPE_TYPE.PICTURE:
        return False
    width = inches(shape.width) or 0
    height = inches(shape.height) or 0
    return (width >= FULL_BLEED_MIN_W * scale[0]
            and height >= FULL_BLEED_MIN_H * scale[1])


def is_bottom_furniture(shape, bottom_limit: float) -> bool:
    """The source deck's own bottom decorative strip: pinned, exempt from F3/F5."""
    top = inches(shape.top)
    return top is not None and top >= bottom_limit - FURNITURE_TOP_MARGIN


# --------------------------------------------------------------------------- #
# shape roles
# --------------------------------------------------------------------------- #
def is_footer_like(shape, bottom_limit: float) -> bool:
    """Existing footer furniture: copyright line, page number, or thin bottom rule.

    Normalising an existing footer and adding the standard three-piece footer are
    both allowed by the Mode B SOP, so these shapes are excluded from the inventory
    comparison on *both* sides — an existing footer normalised into the standard one
    must not be reported as a lost source shape.
    """
    top = inches(shape.top)
    height = inches(shape.height) or 0
    width = inches(shape.width) or 0
    if top is None:
        return False
    if shape.has_text_frame:
        text = (shape.text or "").strip()
        if text and FOOTER_TEXT_RE.search(text):
            return True
        if text and top > bottom_limit - 0.8 and PAGE_NUM_RE.match(text):
            return True
    if height <= 0.07 and width > 6.0 and top > bottom_limit - 0.6:
        return True
    return False


def find_source_title(shapes):
    """The shape playing the title role on a **source** page.

    The title is the UPPERMOST candidate in the top band. Decks commonly carry a
    lead line just below it (e.g. "7个壳架，电流覆盖200-6300A"). Judging by an
    absolute top bound mis-classifies such a lead as the title on the source side
    while the target side (whose content moved by the give-way shift) no longer
    matches that bound — the lead would then be excluded on one side and read as
    an added shape on the other. Taking the topmost candidate is shift-invariant.
    """
    candidates = []
    for shape in shapes:
        top = inches(shape.top)
        width = inches(shape.width) or 0
        if top is None:
            continue
        try:
            if shape.is_placeholder and shape.placeholder_format.idx == 0:
                candidates.append((top, -width, shape))
                continue
        except (AttributeError, ValueError):
            pass
        if (shape.name or "").strip() in TITLE_SHAPE_NAMES:
            candidates.append((top, -width, shape))
            continue
        if shape.has_text_frame and shape.shape_type == MSO_SHAPE_TYPE.TEXT_BOX:
            left = inches(shape.left)
            if left is not None and left < 1.3 and top < 1.15 and width > 5.0:
                candidates.append((top, -width, shape))
                continue
        # Top-band fallback. A text-bearing shape sitting in the top band at the left grid
        # margin plays the title role even when it is a BODY placeholder or a text box
        # narrower than 5.0". The three specific rules above assume a deck authored with a
        # real title placeholder; a deck whose titles are body placeholders resolves to
        # None without this, and the rebuilt grid is then drawn over the old title.
        if shape.has_text_frame and (shape.text or "").strip():
            left = inches(shape.left)
            if (left is not None and left < TOP_BAND_MIN_LEFT
                    and top < TOP_BAND_MAX_TOP and width > TOP_BAND_MIN_W):
                candidates.append((top, -width, shape))
    if not candidates:
        return None
    candidates.sort(key=lambda item: (item[0], item[1]))
    return candidates[0][2]


def find_promoted_heading(shapes, skip_ids=frozenset()):
    """The source page's REAL title when its title slot only carries a group label.

    Some decks label an entire section with one repeated word in the title slot --
    "Highlights" on eight consecutive pages -- and put the page's actual topic one line
    further down. Taking the title slot verbatim there yields eight identically titled
    pages, and naming the chapter after it produces a category line and a main title that
    read the same. Promoting the topmost remaining text line yields the page's own topic.

    The page is always declared by the caller (``title_grid.promote_heading_pages``);
    this is never inferred, because on a normal page the topmost remaining line is body
    copy, not a title.
    """
    best = None
    for shape in shapes:
        if id(shape._element) in skip_ids:
            continue
        if not shape.has_text_frame or not (shape.text or "").strip():
            continue
        r = rect(shape)
        if r is None:
            continue
        key = (r[1], -r[0])
        if best is None or key < best[0]:
            best = (key, shape)
    return best[1] if best is not None else None


def title_grid_boxes(shapes, scale=(1.0, 1.0)):
    """The newly drawn two-line 2026 VI title grid (left edge on the VI grid line).

    The grid line and the top-band bound are reference inches scaled to this deck's
    canvas, so the same engine output is recognised whether the deck is on the
    13.333" x 7.5" reference canvas or a proportionally smaller legacy one.
    """
    grid_left = GRID_LEFT * scale[0]
    top_max = GRID_TOP_MAX * scale[1]
    boxes = []
    for shape in shapes:
        if not shape.has_text_frame or shape.shape_type != MSO_SHAPE_TYPE.TEXT_BOX:
            continue
        left, top = inches(shape.left), inches(shape.top)
        if left is None or top is None:
            continue
        if abs(left - grid_left) < 0.02 and top < top_max:
            boxes.append((top, (shape.text or "").strip(), shape))
    boxes.sort(key=lambda item: item[0])
    return boxes


# --------------------------------------------------------------------------- #
# signatures
# --------------------------------------------------------------------------- #
def table_cell_text(shape) -> str:
    return "|".join(cell.text.strip() for row in shape.table.rows for cell in row.cells)


def embedded_workbook_signature(blob: bytes):
    """Read editable values and formulas from a chart's embedded XLSX workbook."""
    with ZipFile(BytesIO(blob)) as workbook:
        workbook_xml = SafeET.fromstring(workbook.read("xl/workbook.xml"))
        rels_xml = SafeET.fromstring(workbook.read("xl/_rels/workbook.xml.rels"))
        rel_ns = "http://schemas.openxmlformats.org/package/2006/relationships"
        office_rel_ns = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
        rel_targets = {
            rel.get("Id"): rel.get("Target")
            for rel in rels_xml.findall(f"{{{rel_ns}}}Relationship")
        }

        shared_strings = []
        if "xl/sharedStrings.xml" in workbook.namelist():
            strings_xml = SafeET.fromstring(workbook.read("xl/sharedStrings.xml"))
            shared_strings = [
                "".join(node.text or "" for node in item.iter() if node.tag.endswith("}t"))
                for item in strings_xml if item.tag.endswith("}si")
            ]

        sheets = []
        for sheet in workbook_xml.iter():
            if not sheet.tag.endswith("}sheet"):
                continue
            rel_id = sheet.get(f"{{{office_rel_ns}}}id")
            target = rel_targets.get(rel_id)
            if not target:
                raise ValueError(f"Embedded chart workbook sheet has no relationship: {sheet.get('name')}")
            sheet_path = (target.lstrip("/") if target.startswith("/")
                          else posixpath.normpath(posixpath.join("xl", target)))
            sheet_xml = SafeET.fromstring(workbook.read(sheet_path))
            cells = []
            for cell in sheet_xml.iter():
                if not cell.tag.endswith("}c"):
                    continue
                cell_type = cell.get("t", "n")
                value_node = next((item for item in cell if item.tag.endswith("}v")), None)
                formula_node = next((item for item in cell if item.tag.endswith("}f")), None)
                value = value_node.text if value_node is not None else None
                formula = formula_node.text if formula_node is not None else None
                if cell_type == "s" and value is not None:
                    value = shared_strings[int(value)]
                elif cell_type == "inlineStr":
                    value = "".join(item.text or "" for item in cell.iter()
                                    if item.tag.endswith("}t"))
                cells.append((cell.get("r"), cell_type, value, formula))
            sheets.append((sheet.get("name", ""), tuple(cells)))
        return tuple(sheets)


def chart_content_signature(shape):
    """Capture visible chart facts and the editable workbook behind the chart."""
    chart = shape.chart
    plots = []
    for plot in chart.plots:
        try:
            categories = tuple(str(category.label) for category in plot.categories)
        except (AttributeError, ValueError):
            categories = ()
        series = []
        for item in plot.series:
            values = tuple(getattr(item, "values", ()))
            x_values = tuple(getattr(item, "x_values", ()))
            series.append((str(item.name or ""), values, x_values))
        plots.append((tuple(categories), tuple(series)))

    title = chart.chart_title.text_frame.text if chart.has_title else ""
    axis_titles = []
    for axis_name in ("category_axis", "value_axis", "category_axis2", "value_axis2"):
        try:
            axis = getattr(chart, axis_name)
            axis_title = axis.axis_title.text_frame.text if axis.has_title else ""
        except (AttributeError, ValueError):
            axis_title = ""
        if axis_title:
            axis_titles.append((axis_name, axis_title))

    package_rel = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/package"
    workbooks = []
    for relationship in chart.part.rels.values():
        if relationship.reltype != package_rel:
            continue
        if relationship.is_external:
            workbooks.append(("external", relationship.target_ref))
        else:
            workbooks.append(("embedded", embedded_workbook_signature(relationship.target_part.blob)))

    number_formats = tuple(
        (element.get("formatCode"), element.get("sourceLinked"))
        for element in chart._element.iter() if element.tag.endswith("}numFmt")
    )
    return (str(chart.chart_type), title, tuple(axis_titles), tuple(plots),
            number_formats, tuple(workbooks))


def shape_sig(shape):
    """Position-independent identity of a shape."""
    name = (shape.name or "").strip()
    width, height = inches(shape.width), inches(shape.height)
    text = ""
    if getattr(shape, "has_table", False):
        text = table_cell_text(shape)
        width = inches(sum(c.width for c in shape.table.columns)) or width
        height = None                      # row heights may be micro-adjusted
    elif shape.has_text_frame:
        text = (shape.text or "").strip()
    chart = chart_content_signature(shape) if getattr(shape, "has_chart", False) else None
    return (name, round(width or -1, 3), None if height is None else round(height, 3), text, chart)


def table_row_heights(shape):
    if not getattr(shape, "has_table", False):
        return None
    return round(inches(sum(r.height for r in shape.table.rows)) or 0, 4)


@dataclass
class PageShapes:
    shape: object
    sig: tuple
    top: float
    bottom: float
    background: bool
    furniture: bool


@dataclass
class PageInventory:
    index: int
    title_text: str = ""
    shapes: list = field(default_factory=list)        # [PageShapes] (body content)
    grid: list = field(default_factory=list)          # [(top, text)] new title grid
    excluded: list = field(default_factory=list)      # [(name, reason)]


def read_inventory(deck, side: str, bottom_limit: float, scale=(1.0, 1.0),
                   promote_pages=frozenset()):
    """Inventory of one deck, split into title carriers, footer furniture and body."""
    pages = []
    for idx, slide in enumerate(deck.slides, start=1):
        page = PageInventory(index=idx)
        shapes = list(slide.shapes)
        skip_ids = set()

        if side == "source":
            title_shape = find_source_title(shapes)
            if title_shape is not None:
                skip_ids.add(id(title_shape._element))
                page.excluded.append(((title_shape.name or "?"), "title"))
                page.title_text = (title_shape.text or "").strip()
            if idx in promote_pages:
                # On these pages the title slot held a group label and the engine promoted
                # the topmost body line into the title slot, removing both carriers. The
                # promoted line is therefore a title carrier on the source side too --
                # otherwise the gate reads it as a lost body shape -- and its text is what
                # the rebuilt main title must equal.
                promoted = find_promoted_heading(shapes, skip_ids)
                if promoted is not None:
                    skip_ids.add(id(promoted._element))
                    page.excluded.append(((promoted.name or "?"), "promoted_title"))
                    page.title_text = (promoted.text or "").strip()
        else:
            boxes = title_grid_boxes(shapes, scale)
            if boxes:
                page.grid = [(top, text) for top, text, _sh in boxes]
                page.title_text = boxes[-1][1]          # lower box == main title
                for _top, _text, shape in boxes:
                    skip_ids.add(id(shape._element))
                    page.excluded.append(((shape.name or "?"), "title_grid"))

        for shape in shapes:
            if id(shape._element) in skip_ids:
                continue
            if is_footer_like(shape, bottom_limit):
                page.excluded.append(((shape.name or "?"), "footer"))
                continue
            r = rect(shape)
            if r is None:
                continue
            page.shapes.append(PageShapes(
                shape=shape,
                sig=shape_sig(shape),
                top=inches(shape.top) or 0.0,
                bottom=r[3],
                background=is_full_bleed_background(shape, scale),
                furniture=is_bottom_furniture(shape, bottom_limit),
            ))
        pages.append(page)
    return pages


# --------------------------------------------------------------------------- #
# page mapping (monotone DP alignment)
# --------------------------------------------------------------------------- #
def infer_map(source_pages, target_pages, min_score: int = 1):
    n, m = len(source_pages), len(target_pages)
    src_sets = [{ps.sig for ps in p.shapes} for p in source_pages]
    tgt_sets = [{ps.sig for ps in p.shapes} for p in target_pages]

    def score(i, j):
        overlap = len(src_sets[i] & tgt_sets[j])
        title = 1 if (source_pages[i].title_text
                      and source_pages[i].title_text == target_pages[j].title_text) else 0
        return title * 1000 + overlap

    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            best = dp[i - 1][j] if dp[i - 1][j] > dp[i][j - 1] else dp[i][j - 1]
            pair = dp[i - 1][j - 1] + score(i - 1, j - 1)
            dp[i][j] = best if best > pair else pair

    pairs, i, j = [], n, m
    while i > 0 and j > 0:
        if dp[i][j] == dp[i - 1][j]:
            i -= 1
        elif dp[i][j] == dp[i][j - 1]:
            j -= 1
        else:
            if score(i - 1, j - 1) >= min_score:
                pairs.append((j, i, score(i - 1, j - 1)))
            i -= 1
            j -= 1
    pairs.reverse()
    return {t: s for t, s, _ in pairs}, pairs


# --------------------------------------------------------------------------- #
# per-page verification
# --------------------------------------------------------------------------- #
def verify_pair(src: PageInventory, tgt: PageInventory, tolerance: float, bottom_limit: float):
    failures, notes = [], []

    src_by_sig, tgt_by_sig = {}, {}
    for ps in src.shapes:
        src_by_sig.setdefault(ps.sig, []).append(ps)
    for ps in tgt.shapes:
        tgt_by_sig.setdefault(ps.sig, []).append(ps)

    # ---- F2 inventory identity -------------------------------------------- #
    for sig, items in src_by_sig.items():
        if len(items) > len(tgt_by_sig.get(sig, [])):
            kind = "图表数据不同或原子页形状丢失" if sig[4] is not None else "原子页形状丢失"
            failures.append(f"[F2] {kind}: {sig[0]!r} w={sig[1]} h={sig[2]} text={sig[3][:30]!r}")
    for sig, items in tgt_by_sig.items():
        if len(items) > len(src_by_sig.get(sig, [])):
            kind = "目标页图表数据与原稿不符" if sig[4] is not None else "目标页多出原子页没有的形状"
            failures.append(f"[F2] {kind}: {sig[0]!r} w={sig[1]} h={sig[2]} text={sig[3][:30]!r}")

    # ---- F3 uniform shift -------------------------------------------------- #
    pool = {}
    for ps in src.shapes:
        if ps.background or ps.furniture:
            continue
        pool.setdefault(ps.sig, []).append(ps)

    deltas = []
    paired = {}                      # id(target shape element) -> source PageShapes
    for ps in tgt.shapes:
        if ps.background or ps.furniture:
            continue
        candidates = pool.get(ps.sig)
        if not candidates:
            continue
        src_ps = candidates.pop(0)
        paired[id(ps.shape._element)] = src_ps
        deltas.append((round(ps.top - src_ps.top, 4), ps.sig[0], src_ps.top))
        before = table_row_heights(src_ps.shape)
        after = table_row_heights(ps.shape)
        if before is not None and after is not None and abs(before - after) > 0.005:
            notes.append(
                f"[F2] 表格行高间距微调: {ps.sig[0]!r} {before:.3f}\" -> {after:.3f}\" "
                f"(Δ{before - after:+.3f}\"，仅行高，文字与列宽未改)"
            )
    if deltas:
        distinct = sorted({d for d, _n, _t in deltas})
        if len(distinct) == 1:
            notes.append(f"[F3] 统一平移量 {distinct[0]:+.3f}\"")
        elif len(distinct) == 2 and abs(distinct[0]) < 1e-6:
            # Two-tier pattern: header chrome that sits ABOVE the give-way block
            # (a top-corner brand logo, for instance) stays pinned at 0 while the
            # block and everything below it move by one shared delta. That is a
            # legitimate minimal-shift result, not a re-layout.
            shift = distinct[1]
            pinned = [t for d, _n, t in deltas if abs(d) < 1e-6]
            moved = [t for d, _n, t in deltas if abs(d) > 1e-6]
            if pinned and moved and max(pinned) < min(moved) - 0.001:
                notes.append(f"[F3] 两级位移：标题块之上的顶部元素保持原位，其余内容统一下移 {shift:+.3f}\"")
            else:
                failures.append(
                    f"[F3] 非统一平移：0 位移的元素并非全部位于下移组之上（pinned tops={sorted(pinned)[:3]}，"
                    f"moved tops={sorted(moved)[:3]}）"
                )
        else:
            spread = distinct[-1] - distinct[0]
            outliers = sorted(deltas, key=lambda x: abs(x[0] - distinct[0]))[-3:]
            failures.append(
                f"[F3] 非统一平移：本页出现 {len(distinct)} 种位移量，极差 {spread:.3f}\"，异常样例 "
                f"{[(d, n) for d, n, _t in outliers]}"
            )

    # ---- F5 bottom safety -------------------------------------------------- #
    # Only a shape the shell rewrite PUSHED past the line is a defect. A shape that
    # already sat past it in the source is reported as a note: on a full-bleed deck
    # (content designed to the very bottom edge) the canvas-blind version of this
    # check fails the gate on the author's own layout, which is not this gate's job.
    for ps in tgt.shapes:
        if ps.background or ps.furniture:
            continue
        if ps.bottom <= bottom_limit + 0.02:
            continue
        src_ps = paired.get(id(ps.shape._element))
        if src_ps is not None and src_ps.bottom <= bottom_limit + 0.02:
            failures.append(
                f"[F5] 被外壳改写挤到底线 {bottom_limit}\" 之下: {ps.sig[0]!r} "
                f"底边={ps.bottom:.3f}\"（原子页 {src_ps.bottom:.3f}\"）"
            )
        else:
            origin = f"原子页 {src_ps.bottom:.3f}\"" if src_ps is not None else "新增形状"
            notes.append(
                f"[F5] 原稿既有越线（非本次改动所致，仅留痕）: {ps.sig[0]!r} "
                f"底边={ps.bottom:.3f}\"（{origin}）"
            )

    return failures, notes


# --------------------------------------------------------------------------- #
# main
# --------------------------------------------------------------------------- #
def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="chint-pptx Mode B source-page fidelity gate")
    ap.add_argument("--source", required=True, help="original uploaded deck (.pptx)")
    ap.add_argument("--target", required=True, help="Mode B output deck (.pptx)")
    ap.add_argument("--map", help="explicit {target_page: source_page} JSON; inferred when omitted")
    ap.add_argument("--baseline", help="JSON with allow_changed_pages / allow_removed_pages")
    ap.add_argument("--json", dest="json_out", help="write a machine-readable report here")
    ap.add_argument("--shift-tolerance", type=float, default=0.01, help="inches (default 0.01)")
    ap.add_argument("--bottom-limit", type=float, default=None,
                    help="bottom strip line in inches; default = 7.30\" scaled to the "
                         "target deck's canvas height")
    args = ap.parse_args(argv)
    if args.json_out:
        try:
            args.json_out = str(ensure_output_path(args.json_out))
        except ValueError as exc:
            ap.error(str(exc))

    try:
        source = Presentation(args.source)
        target = Presentation(args.target)
    except Exception as exc:                                  # noqa: BLE001
        print(f"[FAIL] 无法读取文稿: {exc}")
        return 2

    scale = canvas_scale(target)
    bottom_limit = (args.bottom_limit if args.bottom_limit is not None
                    else round(DEFAULT_BOTTOM_LIMIT * scale[1], 4))

    baseline = {"allow_changed_pages": [], "allow_removed_pages": []}
    if args.baseline:
        baseline.update(json.loads(open(args.baseline, encoding="utf-8").read()))
    allow_changed = set(baseline.get("allow_changed_pages", []))
    allow_removed = set(baseline.get("allow_removed_pages", []))
    allow_single_line = set(baseline.get("allow_single_line_grid_pages", []))
    allow_promoted = set(baseline.get("allow_promoted_heading_pages", []))

    src_pages = read_inventory(source, "source", bottom_limit, scale,
                               promote_pages=allow_promoted)
    tgt_pages = read_inventory(target, "target", bottom_limit, scale)

    print("=" * 78)
    print("chint-pptx Mode B 保真度门禁 / source-page fidelity gate")
    print(f"  原稿 source : {args.source}  ({len(src_pages)} 页)")
    print(f"  成品 target : {args.target}  ({len(tgt_pages)} 页)")
    print(f"  画布比例    : {scale[0]:.4f} x {scale[1]:.4f}（基准 13.333\" x 7.5\"；"
          f"标题网格左沿 {GRID_LEFT * scale[0]:.3f}\"，顶部带上限 {GRID_TOP_MAX * scale[1]:.3f}\"）")
    print(f"  底部安全线  : {bottom_limit}\"    平移容差: {args.shift_tolerance}\"")
    if allow_promoted:
        print(f"  标题提升页  : {sorted(allow_promoted)}"
              f"（源稿标题槽为组标签，页标题取自正文首行 —— baseline 已声明）")
    print("=" * 78)

    if args.map:
        page_map = {int(k): int(v) for k, v in json.loads(open(args.map, encoding="utf-8").read()).items()}
        print(f"\n[F0] 页映射：显式 --map（{len(page_map)} 对）")
    else:
        # Pages the baseline declares as superseded are excluded from the alignment: a
        # rebuilt shell page sits at the same *position* as the shell page it replaced,
        # so the monotone pass would pair them and report every cosmetic difference as a
        # lost sub-page. Their removal is already accounted for in F1.
        keep = [p for p in src_pages if p.index not in allow_removed]
        small_map, pairs_small = infer_map(keep, tgt_pages)
        page_map = {t: keep[s - 1].index for t, s, _sc in pairs_small}
        pairs = [(t, keep[s - 1].index, sc) for t, s, sc in pairs_small]
        print(f"\n[F0] 页映射：自动推断（{len(page_map)} 对；页序单调对齐 + 标题文本 + 形状指纹）；"
              f"已排除 baseline 声明的被替换页 {sorted(allow_removed) or '无'}")
        for t, s, sc in pairs:
            print(f"      target p{t:>3}  <-  source p{s:<3}   匹配分={sc}")

    failures, notes, exempt = [], [], []

    print("\n[F2/F3/F4/F5] 逐页核验")
    print(f"    {'目标页':>6} {'原页':>5} {'形状数':>6}  判定")
    for tgt_i in sorted(page_map):
        src_i = page_map[tgt_i]
        if not (1 <= src_i <= len(src_pages)) or not (1 <= tgt_i <= len(tgt_pages)):
            failures.append(f"[F0] 映射越界: target p{tgt_i} -> source p{src_i}")
            continue
        src_page, tgt_page = src_pages[src_i - 1], tgt_pages[tgt_i - 1]

        # ---- F4 title grid -------------------------------------------------- #
        if src_page.title_text:
            expected = 1 if tgt_i in allow_single_line else 2
            if len(tgt_page.grid) < expected:
                failures.append(
                    f"[F4] 目标 p{tgt_i} 标题网格不完整（检出 {len(tgt_page.grid)} 个，期望 {expected}）"
                )
            elif tgt_page.grid[-1][1] != src_page.title_text:
                failures.append(
                    f"[F4] 目标 p{tgt_i} 主标题 {tgt_page.grid[-1][1]!r} "
                    f"≠ 原子页标题 {src_page.title_text!r}"
                )
            elif expected == 1:
                notes.append(f"[F4] 目标 p{tgt_i} 为无章页：标题网格只画主标题、无章节名行"
                             f"（baseline 已声明）")

        if tgt_i in allow_changed:
            exempt.append(tgt_i)
            print(f"    {tgt_i:>6} {src_i:>5} {len(tgt_page.shapes):>6}  baseline 豁免")
            continue

        page_failures, page_notes = verify_pair(src_page, tgt_page, args.shift_tolerance, bottom_limit)
        failures.extend(f"[目标 p{tgt_i} / 原 p{src_i}] {f}" for f in page_failures)
        notes.extend(f"[目标 p{tgt_i} / 原 p{src_i}] {n}" for n in page_notes)
        status = "PASS" if not page_failures else f"FAIL（{len(page_failures)} 项）"
        print(f"    {tgt_i:>6} {src_i:>5} {len(tgt_page.shapes):>6}  {status}")

    # ---- F1 page accounting ------------------------------------------------ #
    new_pages = [p.index for p in tgt_pages if p.index not in set(page_map)]
    removed = [p.index for p in src_pages if p.index not in set(page_map.values())]
    unexplained = [r for r in removed if r not in allow_removed]
    print("\n[F1] 页数账目")
    print(f"      新增外壳页 : {new_pages if new_pages else '无'}")
    print(f"      原稿被移除 : {removed if removed else '无'}")
    if unexplained:
        failures.append(f"[F1] 原稿 {len(unexplained)} 页被移除但未列入 baseline: {unexplained}")

    print("\n" + "-" * 78)
    if notes:
        print("允许的改动（逐条留痕）:")
        for n in notes:
            print("  · " + n)
    if exempt:
        print(f"baseline 豁免页: {sorted(exempt)}")
    for f in failures:
        print("  FAIL " + f)
    verdict = "PASS" if not failures else "FAIL"
    print("-" * 78)
    print(f"[{verdict}] 子页保真度：{'全部通过' if not failures else str(len(failures)) + ' 项未通过'}")

    if args.json_out:
        Path(args.json_out).parent.mkdir(parents=True, exist_ok=True)
        with open(args.json_out, "w", encoding="utf-8") as fh:
            json.dump({
                "verdict": verdict,
                "source": args.source, "target": args.target,
                "canvas_scale": {"sx": round(scale[0], 4), "sy": round(scale[1], 4)},
                "bottom_limit": bottom_limit,
                "source_pages": len(src_pages), "target_pages": len(tgt_pages),
                "page_map": page_map, "new_pages": new_pages, "removed_pages": removed,
                "exempt_pages": sorted(exempt), "notes": notes, "failures": failures,
            }, fh, ensure_ascii=False, indent=2)
        print(f"报告已写入: {args.json_out}")

    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
