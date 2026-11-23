#!/usr/bin/env python3
"""Non-destructive PDF highlighter & sticky-note annotator (chint-office-annotate/v1)."""
from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

SCHEMA_ID = "chint-office-annotate/v1"


def annotate_pdf(input_pdf: Path, items: list[dict], output_pdf: Path, default_author: str = "CHINT PM") -> dict:
    import fitz

    if output_pdf.resolve() == input_pdf.resolve():
        raise ValueError("Refusing to overwrite input PDF; choose a distinct output path.")

    doc = fitz.open(str(input_pdf))
    highlights, stickies = 0, 0
    page_stickies: dict[int, int] = {}
    for idx, item in enumerate(items, 1):
        pno = int(item["page"])
        if pno < 1 or pno > len(doc):
            raise ValueError(f"Annotation #{idx} page {pno} out of range 1..{len(doc)}")
        page = doc[pno - 1]
        query = str(item.get("search", "")).strip()
        comment = str(item.get("comment", "")).strip()
        author = str(item.get("author") or default_author)
        rects = page.search_for(query) if query else []
        if rects:
            annot = page.add_highlight_annot(rects[0])
            note_body = comment
            highlights += 1
        else:
            idx_on_page = page_stickies.get(pno, 0)
            page_stickies[pno] = idx_on_page + 1
            x = 24 + (idx_on_page // 10) * 28
            y = 24 + (idx_on_page % 10) * 22
            note_body = f"[{query}] {comment}" if query else comment
            annot = page.add_text_annot(fitz.Point(x, y), note_body)
            stickies += 1
        annot.set_info(title=author, content=note_body)
        annot.update()

    output_pdf.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(output_pdf))
    doc.close()
    return {"schema": SCHEMA_ID, "input": str(input_pdf), "output": str(output_pdf), "total": len(items), "highlight_count": highlights, "sticky_fallback_count": stickies}


def run_self_test() -> int:
    import fitz

    with tempfile.TemporaryDirectory() as tmp:
        td = Path(tmp)
        src, dst = td / "orig.pdf", td / "orig_annotated.pdf"
        d = fitz.open()
        p = d.new_page()
        p.insert_text((72, 100), "Closed electromagnet XF")
        d.save(str(src))
        d.close()

        items = [
            {"page": 1, "search": "Closed electromagnet", "comment": "Replace with Closing release (CEM)"},
            {"page": 1, "search": "UNMATCHED_SPLIT_RUN", "comment": "Fallback sticky note"},
        ]
        summary = annotate_pdf(src, items, dst)
        assert summary["highlight_count"] == 1 and summary["sticky_fallback_count"] == 1, summary
        with fitz.open(str(src)) as sdoc, fitz.open(str(dst)) as ddoc:
            assert len(list(sdoc[0].annots())) == 0, "Original PDF was modified!"
            annots = list(ddoc[0].annots())
            assert len(annots) == 2, "Annotated PDF missing annotations!"
            assert "[UNMATCHED_SPLIT_RUN]" in (annots[1].info.get("content") or ""), annots[1].info
    print("SELF-TEST PASS: annotate_pdf.py verified (highlight + sticky fallback + content intact, original untouched).")
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
