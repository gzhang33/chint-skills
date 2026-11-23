#!/usr/bin/env python3
"""Non-destructive PDF highlighter & sticky-note annotator (chint-office-annotate/v1)."""
from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

SCHEMA_ID = "chint-office-annotate/v1"
YELLOW = (1.0, 0.92, 0.23)


def _collect_terms(item: dict) -> list[str]:
    raw: list[str] = []
    if item.get("search"):
        raw.append(str(item["search"]).strip())
    for s in item.get("searches") or []:
        st = str(s).strip()
        if st:
            raw.append(st)
    seen: set[str] = set()
    terms: list[str] = []
    for t in raw:
        if t and t not in seen:
            seen.add(t)
            terms.append(t)
    return terms


def _find_distinct_rects(page, terms: list[str]) -> list:
    seen: set[tuple[float, float, float, float]] = set()
    rects = []
    for t in terms:
        for r in page.search_for(t):
            key = (round(r.x0, 1), round(r.y0, 1), round(r.x1, 1), round(r.y1, 1))
            if key not in seen:
                seen.add(key)
                rects.append(r)
    return rects


def annotate_pdf(input_pdf: Path, items: list[dict], output_pdf: Path, default_author: str = "CHINT PM") -> dict:
    import fitz

    if output_pdf.resolve() == input_pdf.resolve():
        raise ValueError("Refusing to overwrite input PDF; choose a distinct output path.")

    doc = fitz.open(str(input_pdf))
    matched_items, highlights, rect_count, stickies = 0, 0, 0, 0
    page_stickies: dict[int, int] = {}
    fallback_items: list[dict] = []
    for idx, item in enumerate(items, 1):
        pno = int(item["page"])
        if pno < 1 or pno > len(doc):
            raise ValueError(f"Annotation #{idx} page {pno} out of range 1..{len(doc)}")
        page = doc[pno - 1]
        terms = _collect_terms(item)
        comment = str(item.get("comment", "")).strip()
        author = str(item.get("author") or default_author)
        mode = str(item.get("match_mode") or "all").lower()
        if mode not in {"all", "merged", "first"}:
            raise ValueError(f"Annotation #{idx} invalid match_mode: {mode}")

        matched_rects = _find_distinct_rects(page, terms)
        if matched_rects:
            matched_items += 1
            if mode == "merged":
                annot = page.add_highlight_annot(matched_rects)
                annot.set_colors(stroke=YELLOW)
                annot.set_info(title=author, content=comment)
                annot.update()
                highlights += 1
                rect_count += len(matched_rects)
            else:
                targets = [matched_rects[0]] if mode == "first" else matched_rects
                for rect in targets:
                    annot = page.add_highlight_annot(rect)
                    annot.set_colors(stroke=YELLOW)
                    annot.set_info(title=author, content=comment)
                    annot.update()
                    highlights += 1
                    rect_count += 1
        else:
            idx_on_page = page_stickies.get(pno, 0)
            page_stickies[pno] = idx_on_page + 1
            x = 24 + (idx_on_page // 10) * 28
            y = 24 + (idx_on_page % 10) * 22
            label = ""
            if len(terms) == 1:
                label = terms[0]
            elif terms:
                label = ", ".join(terms[:3]) + (" 等" if len(terms) > 3 else "")
            note_body = f"[{label}] {comment}" if label else comment
            annot = page.add_text_annot(fitz.Point(x, y), note_body)
            annot.set_colors(stroke=YELLOW)
            annot.set_info(title=author, content=note_body)
            annot.update()
            stickies += 1
            fallback_items.append({"page": pno, "label": label, "comment": comment})

    output_pdf.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(output_pdf))
    doc.close()
    return {
        "schema": SCHEMA_ID,
        "input": str(input_pdf),
        "output": str(output_pdf),
        "total": len(items),
        "matched_items": matched_items,
        "highlight_annotations": highlights,
        "highlighted_rects": rect_count,
        "sticky_fallback_count": stickies,
        "fallback_items": fallback_items,
    }


def run_self_test() -> int:
    import fitz

    with tempfile.TemporaryDirectory() as tmp:
        td = Path(tmp)
        src, dst = td / "orig.pdf", td / "orig_annotated.pdf"
        d = fitz.open()
        p = d.new_page()
        pre = p.add_rect_annot(fitz.Rect(20, 20, 60, 40))
        pre.set_info(title="Legacy Reviewer", content="Pre-existing square")
        pre.update()
        p.insert_text((72, 100), "Closed electromagnet XF; Closed electromagnet")
        p.insert_text((72, 140), "Frame 1000A, 1600A and 2000A")
        d.save(str(src))
        d.close()

        items = [
            {"page": 1, "search": "Closed electromagnet", "match_mode": "all", "comment": "替换为：Closing release (CEM)"},
            {"page": 1, "searches": ["1000A", "1600A", "2000A"], "match_mode": "merged", "comment": "替换为：数字与单位间加半角空格（本页 3 处）"},
            {"page": 1, "search": "UNMATCHED_SPLIT_RUN", "comment": "替换为：兜底便签"},
        ]
        summary = annotate_pdf(src, items, dst, default_author="CHINT Translation")
        assert summary["matched_items"] == 2 and summary["highlight_annotations"] == 3 and summary["highlighted_rects"] == 5 and summary["sticky_fallback_count"] == 1, summary
        assert len(summary["fallback_items"]) == 1 and summary["fallback_items"][0]["label"] == "UNMATCHED_SPLIT_RUN", summary
        with fitz.open(str(src)) as sdoc, fitz.open(str(dst)) as ddoc:
            assert len(list(sdoc[0].annots())) == 1, "Original PDF was modified!"
            annots = [(a.type[1], tuple(round(v, 1) for v in a.rect), len(a.vertices or []), a.colors.get("stroke"), a.info.get("title"), a.info.get("content")) for a in ddoc[0].annots()]
            assert len(annots) == 5, f"Expected 1 legacy + 4 new annots, got {len(annots)}: {annots}"
            assert annots[0][4] == "Legacy Reviewer", annots[0]
            assert annots[1][0] == "Highlight" and annots[2][0] == "Highlight" and annots[1][1] != annots[2][1], annots[1:3]
            assert annots[3][0] == "Highlight" and annots[3][2] == 12, annots[3]
            assert annots[4][0] == "Text" and "[UNMATCHED_SPLIT_RUN]" in (annots[4][5] or ""), annots[4]
    print("SELF-TEST PASS: annotate_pdf.py verified (legacy preserved, yellow all+merged highlights, sticky fallback, source untouched).")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Non-destructive PDF annotator")
    parser.add_argument("input_pdf", nargs="?", help="Source PDF (never modified)")
    parser.add_argument("--annotations", help="JSON file or '-' matching chint-office-annotate/v1")
    parser.add_argument("--output", help="Output PDF path (default: <stem>_annotated.pdf)")
    parser.add_argument("--author", default="CHINT PM", help="Default annotation author")
    parser.add_argument("--self-test", action="store_true", help="Run built-in verification suite")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()
    if not args.input_pdf or not args.annotations:
        parser.error("input_pdf and --annotations are required unless --self-test is set")

    inp = Path(args.input_pdf)
    out = Path(args.output) if args.output else inp.with_name(f"{inp.stem}_annotated.pdf")
    raw = sys.stdin.read() if args.annotations == "-" else Path(args.annotations).read_text(encoding="utf-8")
    payload = json.loads(raw)
    items = payload["annotations"] if isinstance(payload, dict) else payload
    print(json.dumps(annotate_pdf(inp, items, out, args.author), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
