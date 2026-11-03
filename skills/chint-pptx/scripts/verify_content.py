#!/usr/bin/env python3
"""Compare source and target product identifiers and numeric evidence in PPTX files."""
from __future__ import annotations

import argparse
import collections
import json
import re
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_ROOT))
from core.output_paths import ensure_output_path

from pptx import Presentation


NUMBER = re.compile(r"(?<![A-Za-z0-9])[-+]?\d[\d,]*(?:\.\d+)?")
WITH_UNIT = re.compile(
    r"(?<![A-Za-z0-9])[-+]?\d[\d,]*(?:\.\d+)?\s*"
    r"(?:万元|亿元|MVA|kVA|kHz|kV|KV|kA|KA|kW|KW|MW|Hz|ms|mm|cm|°C|℃|"
    r"%|‰|V|A|W|s|m|h|dB|台|个|套|万|亿|元|天|级|分)(?![A-Za-z])", re.IGNORECASE)
MODEL = re.compile(
    r"(?<![A-Za-z0-9])(?:NX[A-Z0-9]{1,8}|NM[A-Z0-9]{1,8}|NA\d[A-Z0-9-]{0,6}|"
    r"[A-Z]{1,5}\d[A-Z0-9-]{1,12})(?![A-Za-z0-9])", re.IGNORECASE)


def walk_shapes(shapes):
    for shape in shapes:
        yield shape
        if getattr(shape, "shape_type", None) == 6:
            yield from walk_shapes(shape.shapes)


def slide_strings(slide):
    for shape in walk_shapes(slide.shapes):
        if getattr(shape, "has_text_frame", False):
            yield shape.text_frame.text
        if getattr(shape, "has_table", False):
            for row in shape.table.rows:
                yield " | ".join(cell.text for cell in row.cells)
        if getattr(shape, "has_chart", False):
            chart = shape.chart
            if chart.has_title:
                yield chart.chart_title.text_frame.text
            for plot in chart.plots:
                for category in plot.categories:
                    yield str(category.label)


def facts(path: Path):
    deck = Presentation(str(path))
    numeric = set()
    models = set()
    table_rows = set()
    chart_series = set()
    images = 0

    for slide_number, slide in enumerate(deck.slides, 1):
        strings = list(slide_strings(slide))
        all_text = "\n".join(strings)
        for match in WITH_UNIT.finditer(all_text):
            text = re.sub(r"\s+", "", match.group(0)).replace(",", "")
            numeric.add(text.casefold())
        # Unitless decimals often hold chart values or electrical measurements.
        for match in NUMBER.finditer(all_text):
            token = match.group(0).replace(",", "")
            if "." in token:
                numeric.add(token.casefold())
        models.update(m.group(0).upper() for m in MODEL.finditer(all_text))

        for shape in walk_shapes(slide.shapes):
            if shape.shape_type == 13:
                images += 1
            if getattr(shape, "has_table", False):
                for row in shape.table.rows:
                    cells = " | ".join(cell.text.strip() for cell in row.cells)
                    row_numbers = tuple(sorted({
                        m.group(0).replace(",", "").casefold()
                        for m in NUMBER.finditer(cells)
                    }))
                    row_models = tuple(sorted({m.group(0).upper() for m in MODEL.finditer(cells)}))
                    if row_numbers or row_models:
                        table_rows.add((row_numbers, row_models))
            if getattr(shape, "has_chart", False):
                for series in shape.chart.series:
                    values = tuple(sorted(str(v).replace(",", "") for v in series.values))
                    if values:
                        chart_series.add((series.name.strip(), values))

    return {
        "slides": len(deck.slides),
        "numeric_evidence": numeric,
        "product_identifiers": models,
        "table_fact_rows": table_rows,
        "chart_series": chart_series,
        "image_shapes": images,
    }


def _added_and_removed(source, target):
    return sorted(source - target), sorted(target - source)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, help="unchanged source .pptx")
    parser.add_argument("--target", required=True, help="edited or restructured output .pptx")
    parser.add_argument("--manifest", help="JSON review manifest with approved_fact_changes")
    parser.add_argument("--json", dest="json_path", help="write the comparison report to JSON")
    args = parser.parse_args(argv)
    if args.json_path:
        try:
            args.json_path = str(ensure_output_path(args.json_path))
        except ValueError as exc:
            parser.error(str(exc))

    source_path, target_path = Path(args.source), Path(args.target)
    if not source_path.is_file() or not target_path.is_file():
        parser.error("both --source and --target must name existing .pptx files")
    if source_path.resolve() == target_path.resolve():
        parser.error("source and target must be different files")

    approval = {"numeric_evidence": [], "product_identifiers": []}
    if args.manifest:
        manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
        entries = manifest.get("approved_fact_changes", [])
        if not isinstance(entries, list):
            parser.error("manifest approved_fact_changes must be an array")
        for entry in entries:
            if not isinstance(entry, dict) or not all(entry.get(key) for key in ("source", "replacement", "user_basis")):
                parser.error("each approved_fact_changes entry needs source, replacement, and user_basis")
            for key, pattern in (("numeric_evidence", NUMBER), ("product_identifiers", MODEL)):
                old = pattern.findall(entry["source"])
                new = pattern.findall(entry["replacement"])
                if old:
                    approval[key].extend(x.replace(",", "").casefold() for x in old)
                if new:
                    approval[key].extend(x.replace(",", "").casefold() for x in new)

    before, after = facts(source_path), facts(target_path)
    report = {"source": str(source_path.resolve()), "target": str(target_path.resolve()),
              "source_pages": before["slides"], "target_pages": after["slides"],
              "manual_semantic_review_required": True,
              "uninspectable_image_shapes_in_target": after["image_shapes"], "checks": {}}
    failed = False
    for key in ("numeric_evidence", "product_identifiers", "table_fact_rows", "chart_series"):
        removed, added = _added_and_removed(before[key], after[key])
        if key in ("numeric_evidence", "product_identifiers"):
            approved = set(approval[key])
            removed = [value for value in removed if str(value).casefold() not in approved]
            added = [value for value in added if str(value).casefold() not in approved]
        report["checks"][key] = {"missing_from_target": [list(x) if isinstance(x, tuple) else x for x in removed],
                                 "unmatched_in_target": [list(x) if isinstance(x, tuple) else x for x in added]}
        if removed:
            failed = True

    report["checks"]["chart_series"]["note"] = "Unmatched series need source review; image charts are not data-editable."
    report["checks"]["semantic_review"] = "Read every rewritten claim and confirm its source, product, conditions, and conclusion."
    print(json.dumps(report, ensure_ascii=False, indent=2, default=str))
    if args.json_path:
        report_path = Path(args.json_path)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2, default=str) + "\n",
                               encoding="utf-8")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
