#!/usr/bin/env python3
"""Non-destructive PDF highlighter & sticky-note annotator (chint-office-annotate/v1)."""
from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from pathlib import Path

SCHEMA_ID = "chint-office-annotate/v1"
YELLOW = (1.0, 0.92, 0.23)


def _import_fitz():
    try:
        import fitz
        return fitz
    except ImportError as exc:
        raise RuntimeError("Missing dependency 'pymupdf' (fitz) required for PDF annotation. Install with: pip install pymupdf") from exc


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


def _page_lines_chars(page) -> list[tuple[tuple[float, float, float, float], list[tuple[str, tuple[float, float, float, float]]]]]:
    lines: list[tuple[tuple[float, float, float, float], list[tuple[str, tuple[float, float, float, float]]]]] = []
    raw = page.get_text("rawdict")
    for blk in raw.get("blocks", []):
        if blk.get("type") != 0:
            continue
        for ln in blk.get("lines", []):
            chars: list[tuple[str, tuple[float, float, float, float]]] = []
            for sp in ln.get("spans", []):
                for ch in sp.get("chars", []):
                    c = ch.get("c", "")
                    bbox = ch.get("bbox")
                    if c and bbox:
                        chars.append((c, tuple(bbox)))
            if chars:
                lines.append((tuple(ln["bbox"]), chars))
    return lines


def _chars_in_rect(line_chars, rect) -> list[tuple[int, str, tuple[float, float, float, float]]]:
    hits = []
    for idx, (c, bbox) in enumerate(line_chars):
        cx = (bbox[0] + bbox[2]) * 0.5
        cy = (bbox[1] + bbox[3]) * 0.5
        if (rect.x0 - 1.2) <= cx <= (rect.x1 + 1.2) and (rect.y0 - 1.5) <= cy <= (rect.y1 + 1.5):
            hits.append((idx, c, bbox))
    return hits


def _matching_line(lines, rect):
    ry = (rect.y0 + rect.y1) * 0.5
    best = None
    best_dist = 1e9
    for lb, chars in lines:
        if (lb[0] - 2.0) <= rect.x1 and rect.x0 <= (lb[2] + 2.0) and (lb[1] - 2.0) <= ry <= (lb[3] + 2.0):
            dist = abs((lb[1] + lb[3]) * 0.5 - ry)
            if dist < best_dist:
                best = chars
                best_dist = dist
    return best


def _extract_group_text(lines, group_rects: list) -> tuple[str, bool]:
    """Return text inside rects plus word-boundary pass flag."""
    text_parts: list[str] = []
    first_left_bad = False
    last_right_bad = False
    for g_idx, rect in enumerate(group_rects):
        lchars = _matching_line(lines, rect)
        if not lchars:
            continue
        hits = _chars_in_rect(lchars, rect)
        if not hits:
            continue
        non_ws = [h for h in hits if not h[1].isspace()]
        if not non_ws:
            continue
        text_parts.append("".join(h[1] for h in hits))
        if g_idx == 0:
            first_i, _, first_bb = non_ws[0]
            if first_i > 0:
                prev_c, prev_bb = lchars[first_i - 1]
                if not prev_c.isspace() and prev_c.isascii() and prev_c.isalnum() and (first_bb[0] - prev_bb[2]) < 3.5:
                    first_left_bad = True
        if g_idx == len(group_rects) - 1:
            last_i, _, last_bb = non_ws[-1]
            if last_i + 1 < len(lchars):
                next_c, next_bb = lchars[last_i + 1]
                if not next_c.isspace() and next_c.isascii() and next_c.isalnum() and (next_bb[0] - last_bb[2]) < 3.5:
                    last_right_bad = True
    return "".join(text_parts), (first_left_bad or last_right_bad)


def _group_multiline_rects(raw_rects: list, lines, term: str) -> list[list]:
    """Group PyMuPDF rects belonging to one wrapped phrase into single occurrences."""
    target_norm = re.sub(r"\s+", "", term)
    if not raw_rects:
        return []
    groups: list[list] = []
    acc_rects: list = []
    acc_norm_len = 0
    for r in raw_rects:
        lchars = _matching_line(lines, r)
        seg = "".join(h[1] for h in _chars_in_rect(lchars, r)) if lchars else ""
        seg_norm_len = len(re.sub(r"\s+", "", seg))
        acc_rects.append(r)
        acc_norm_len += seg_norm_len if seg_norm_len > 0 else len(target_norm)
        if acc_norm_len >= len(target_norm):
            groups.append(acc_rects)
            acc_rects = []
            acc_norm_len = 0
    if acc_rects:
        groups.append(acc_rects)
    return groups


def _find_occurrence_groups(page, lines, terms: list[str], whole_word: bool | None, case_sensitive: bool | None) -> list[list]:
    seen: set[tuple[tuple[float, float, float, float], ...]] = set()
    accepted: list[list] = []
    for t in terms:
        ww = whole_word if whole_word is not None else bool(t and ((t[0].isascii() and t[0].isalnum()) or (t[-1].isascii() and t[-1].isalnum())))
        cs = case_sensitive if case_sensitive is not None else (len(t) <= 4 and any(c.isupper() for c in t) and t == t.upper())
        raw_rects = page.search_for(t)
        for grp in _group_multiline_rects(raw_rects, lines, t):
            g_text, touches_alnum = _extract_group_text(lines, grp)
            if g_text:
                if cs:
                    t_compact = re.sub(r"\s+", "", t)
                    g_compact = re.sub(r"\s+", "", g_text)
                    if t_compact not in g_compact:
                        continue
                if ww:
                    # Check edge boundary only on alphanumeric edges of the query term.
                    lchars_0 = _matching_line(lines, grp[0])
                    lchars_n = _matching_line(lines, grp[-1])
                    bad_edge = False
                    if t[0].isascii() and t[0].isalnum() and lchars_0:
                        hits0 = [h for h in _chars_in_rect(lchars_0, grp[0]) if not h[1].isspace()]
                        if hits0 and hits0[0][0] > 0:
                            pc, pbb = lchars_0[hits0[0][0] - 1]
                            if pc.isascii() and pc.isalnum() and (hits0[0][2][0] - pbb[2]) < 3.5:
                                bad_edge = True
                    if t[-1].isascii() and t[-1].isalnum() and lchars_n:
                        hitsn = [h for h in _chars_in_rect(lchars_n, grp[-1]) if not h[1].isspace()]
                        if hitsn and hitsn[-1][0] + 1 < len(lchars_n):
                            nc, nbb = lchars_n[hitsn[-1][0] + 1]
                            if nc.isascii() and nc.isalnum() and (nbb[0] - hitsn[-1][2][2]) < 3.5:
                                bad_edge = True
                    if bad_edge:
                        continue
            sig = tuple((round(r.x0, 1), round(r.y0, 1), round(r.x1, 1), round(r.y1, 1)) for r in grp)
            if sig not in seen:
                seen.add(sig)
                accepted.append(grp)
    return accepted


def annotate_pdf(input_pdf: Path, items: list[dict], output_pdf: Path, default_author: str = "CHINT PM") -> dict:
    fitz = _import_fitz()

    if not input_pdf.exists():
        raise FileNotFoundError(f"Input PDF not found: {input_pdf}")
    if output_pdf.resolve() == input_pdf.resolve():
        raise ValueError("Refusing to overwrite input PDF; choose a distinct output path.")

    doc = fitz.open(str(input_pdf))
    try:
        if doc.is_encrypted:
            raise ValueError(f"PDF '{input_pdf}' is encrypted/password-protected; decrypt before annotation.")
        matched_items, highlights, rect_count, stickies = 0, 0, 0, 0
        page_stickies: dict[int, int] = {}
        page_line_cache: dict[int, list] = {}
        fallback_items: list[dict] = []

        for idx, item in enumerate(items, 1):
            if not isinstance(item, dict) or "page" not in item:
                raise ValueError(f"Annotation #{idx} missing required 'page' field.")
            pno = int(item["page"])
            if pno < 1 or pno > len(doc):
                raise ValueError(f"Annotation #{idx} page {pno} out of range 1..{len(doc)}")
            page = doc[pno - 1]
            if pno not in page_line_cache:
                page_line_cache[pno] = _page_lines_chars(page)
            terms = _collect_terms(item)
            comment = str(item.get("comment", "")).strip()
            author = str(item.get("author") or default_author)
            mode = str(item.get("match_mode") or "all").lower()
            if mode not in {"all", "merged", "first"}:
                raise ValueError(f"Annotation #{idx} invalid match_mode: {mode}")
            ww = item.get("whole_word")
            cs = item.get("case_sensitive")

            occ_groups = _find_occurrence_groups(page, page_line_cache[pno], terms, ww, cs)
            if occ_groups:
                matched_items += 1
                if mode == "merged":
                    flat_rects = [r for grp in occ_groups for r in grp]
                    annot = page.add_highlight_annot(flat_rects)
                    annot.set_colors(stroke=YELLOW)
                    annot.set_info(title=author, content=comment)
                    annot.update()
                    highlights += 1
                    rect_count += len(flat_rects)
                else:
                    targets = [occ_groups[0]] if mode == "first" else occ_groups
                    for grp in targets:
                        annot = page.add_highlight_annot(grp)
                        annot.set_colors(stroke=YELLOW)
                        annot.set_info(title=author, content=comment)
                        annot.update()
                        highlights += 1
                        rect_count += len(grp)
            else:
                idx_on_page = page_stickies.get(pno, 0)
                page_stickies[pno] = idx_on_page + 1
                prect = page.rect
                rows_per_col = max(1, int((prect.height - 32) // 22))
                col = idx_on_page // rows_per_col
                row = idx_on_page % rows_per_col
                if col == 0:
                    x = prect.x0 + 16
                else:
                    x = max(prect.x0 + 16, prect.x1 - 34 - (col - 1) * 24)
                y = min(prect.y1 - 24, prect.y0 + 16 + row * 22)
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
    finally:
        doc.close()


def run_self_test() -> int:
    fitz = _import_fitz()

    with tempfile.TemporaryDirectory() as tmp:
        td = Path(tmp)
        src, dst = td / "orig.pdf", td / "orig_annotated.pdf"
        d = fitz.open()
        p = d.new_page()
        pre = p.add_rect_annot(fitz.Rect(20, 20, 60, 40))
        pre.set_info(title="Legacy Reviewer", content="Pre-existing square")
        pre.update()
        p.insert_text((72, 100), "Column MN Omni autumn")
        p.insert_text((72, 125), "Rating 250A and 1250A")
        p.insert_text((72, 150), "Split line")
        p.insert_text((72, 165), "phrase; Split line")
        p.insert_text((72, 180), "phrase")
        p.insert_text((72, 210), "Frame 1000A, 1600A and 2000A")
        p2 = d.new_page()
        p2.set_rotation(90)
        p2.insert_text((72, 100), "Rotated Heading")
        d.save(str(src))
        d.close()

        items = [
            {"page": 1, "search": "MN", "match_mode": "all", "comment": "Replace standalone code"},
            {"page": 1, "search": "250A", "match_mode": "all", "comment": "Exact token spacing"},
            {"page": 1, "search": "Split line phrase", "match_mode": "all", "comment": "Wrapped phrase"},
            {"page": 1, "searches": ["1000A", "1600A", "2000A"], "match_mode": "merged", "comment": "Merged spacing (3 items)"},
            {"page": 1, "search": "UNMATCHED_TOKEN", "comment": "Fallback sticky note"},
            {"page": 2, "search": "Rotated Heading", "match_mode": "first", "comment": "Rotated page check"},
        ]
        summary = annotate_pdf(src, items, dst, default_author="Office Reviewer")
        assert summary["matched_items"] == 5 and summary["sticky_fallback_count"] == 1, summary
        assert summary["highlight_annotations"] == 6 and summary["highlighted_rects"] == 10, summary
        with fitz.open(str(src)) as sdoc, fitz.open(str(dst)) as ddoc:
            assert len(list(sdoc[0].annots())) == 1, "Original PDF was modified!"
            p1_ann = [(a.type[1], len(a.vertices or []), a.colors.get("stroke"), a.info.get("title"), a.info.get("content")) for a in ddoc[0].annots()]
            assert len(p1_ann) == 7, f"Expected 1 legacy + 6 new annots on P1, got {len(p1_ann)}: {p1_ann}"
            assert p1_ann[0][3] == "Legacy Reviewer", p1_ann[0]
            assert p1_ann[1][0] == "Highlight" and p1_ann[1][1] == 4, f"MN must match only 1 rect: {p1_ann[1]}"
            assert p1_ann[2][0] == "Highlight" and p1_ann[2][1] == 4, f"250A must not match 1250A: {p1_ann[2]}"
            assert p1_ann[3][1] == 8 and p1_ann[4][1] == 8, f"Wrapped phrase must emit 2 2-quad highlights: {p1_ann[3:5]}"
            assert p1_ann[5][1] == 12, p1_ann[5]
            assert p1_ann[6][0] == "Text" and "[UNMATCHED_TOKEN]" in (p1_ann[6][4] or ""), p1_ann[6]
            assert len(list(ddoc[1].annots())) == 1, "Rotated page missing highlight!"
    print("SELF-TEST PASS: annotate_pdf.py verified (word-boundary/case guard, wrapped multi-line, legacy preserved, rotated page, sticky margin).")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Non-destructive PDF annotator")
    parser.add_argument("input_pdf", nargs="?", help="Source PDF (never modified)")
    parser.add_argument("--annotations", help="JSON file or '-' matching chint-office-annotate/v1")
    parser.add_argument("--output", help="Output PDF path (default: <stem>_annotated.pdf)")
    parser.add_argument("--author", default="CHINT PM", help="Default annotation author")
    parser.add_argument("--self-test", action="store_true", help="Run built-in verification suite")
    args = parser.parse_args()

    try:
        if args.self_test:
            return run_self_test()
        if not args.input_pdf or not args.annotations:
            parser.error("input_pdf and --annotations are required unless --self-test is set")

        inp = Path(args.input_pdf)
        out = Path(args.output) if args.output else inp.with_name(f"{inp.stem}_annotated.pdf")
        raw = sys.stdin.read() if args.annotations == "-" else Path(args.annotations).read_text(encoding="utf-8")
        payload = json.loads(raw)
        items = payload["annotations"] if isinstance(payload, dict) else payload
        if not isinstance(items, list):
            raise ValueError("Annotations payload must be a JSON list or an object with an 'annotations' list.")
        print(json.dumps(annotate_pdf(inp, items, out, args.author), ensure_ascii=False))
        return 0
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())