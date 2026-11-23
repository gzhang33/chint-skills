#!/usr/bin/env python3
"""Generic CHINT office document text & visual-page extractor (.pdf, .docx, .xlsx, .md/.txt)."""
from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

SCHEMA_ID = "chint-office-extract/v1"
LOW_TEXT_THRESHOLD = 50


def parse_page_spec(spec: str | None) -> set[int] | None:
    if not spec:
        return None
    pages: set[int] = set()
    for part in spec.split(","):
        part = part.strip()
        if "-" in part:
            lo, hi = part.split("-", 1)
            pages.update(range(int(lo), int(hi) + 1))
        elif part:
            pages.add(int(part))
    return pages


def extract_document(source: str, pages_filter: set[int] | None = None) -> dict:
    if source == "-":
        lines = sys.stdin.read().splitlines()
        units = [{"location": f"Line {i}", "text": l} for i, l in enumerate(lines, 1) if l.strip()]
        return {"schema": SCHEMA_ID, "source": "-", "format": "stdin", "total_units": len(lines), "scanned_units": len(lines), "low_text_pages": [], "units": units}

    p = Path(source)
    if not p.exists():
        raise FileNotFoundError(f"Input not found: {source}")
    ext = p.suffix.lower()

    if ext in {".doc", ".xls"}:
        raise ValueError(f"Legacy binary format '{ext}' unsupported; convert to '.docx' or '.xlsx' first.")

    if ext == ".pdf":
        import fitz
        doc = fitz.open(str(p))
        total, scanned = len(doc), 0
        units, low_pages = [], []
        for idx, page in enumerate(doc, 1):
            if pages_filter and idx not in pages_filter:
                continue
            scanned += 1
            txt = page.get_text("text")
            if len(re.sub(r"\s+", "", txt)) < LOW_TEXT_THRESHOLD:
                low_pages.append(idx)
            for lno, line in enumerate(txt.splitlines(), 1):
                if line.strip():
                    units.append({"location": f"P{idx}:L{lno}", "text": line})
        return {"schema": SCHEMA_ID, "source": str(p), "format": "pdf", "total_units": total, "scanned_units": scanned, "low_text_pages": low_pages, "units": units}

    if ext == ".docx":
        units = []
        ns = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
        with zipfile.ZipFile(str(p)) as zf:
            xml_names = [n for n in zf.namelist() if re.match(r"word/(document|header\d+|footer\d+)\.xml$", n)]
            for name in sorted(xml_names):
                root = ET.fromstring(zf.read(name))
                for p_idx, para in enumerate(root.iter(f"{ns}p"), 1):
                    txt = "".join(t.text or "" for t in para.iter(f"{ns}t"))
                    if txt.strip():
                        units.append({"location": f"{Path(name).stem}:P{p_idx}", "text": txt})
        return {"schema": SCHEMA_ID, "source": str(p), "format": "docx", "total_units": len(units), "scanned_units": len(units), "low_text_pages": [], "units": units}

    if ext in {".xlsx", ".xlsm"}:
        import openpyxl
        wb = openpyxl.load_workbook(str(p), data_only=True, read_only=True)
        units = []
        for sname in wb.sheetnames:
            ws = wb[sname]
            for r_idx, row in enumerate(ws.iter_rows(values_only=True), 1):
                for c_idx, val in enumerate(row, 1):
                    if val is not None and str(val).strip():
                        col = openpyxl.utils.get_column_letter(c_idx)
                        units.append({"location": f"{sname}!{col}{r_idx}", "text": str(val)})
        return {"schema": SCHEMA_ID, "source": str(p), "format": ext.lstrip("."), "total_units": len(wb.sheetnames), "scanned_units": len(wb.sheetnames), "low_text_pages": [], "units": units}

    lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
    units = [{"location": f"Line {i}", "text": l} for i, l in enumerate(lines, 1) if l.strip()]
    return {"schema": SCHEMA_ID, "source": str(p), "format": ext.lstrip(".") or "text", "total_units": len(lines), "scanned_units": len(lines), "low_text_pages": [], "units": units}


def build_summary(result: dict, batch_size: int = 20) -> dict:
    batches: list[str] = []
    if result.get("format") == "pdf" and result.get("total_units", 0) > 0:
        total_p = int(result["total_units"])
        for start in range(1, total_p + 1, batch_size):
            end = min(start + batch_size - 1, total_p)
            batches.append(f"{start}-{end}")
    return {
        "schema": SCHEMA_ID,
        "source": result.get("source", ""),
        "format": result.get("format", ""),
        "total_units": result.get("total_units", 0),
        "scanned_units": result.get("scanned_units", 0),
        "text_unit_count": len(result.get("units", [])),
        "low_text_pages": result.get("low_text_pages", []),
        "recommended_page_batches": batches,
    }


def run_self_test() -> int:
    import fitz
    import openpyxl

    with tempfile.TemporaryDirectory() as tmp:
        td = Path(tmp)
        pdf_p = td / "sample.pdf"
        doc = fitz.open()
        p1 = doc.new_page()
        p1.insert_text((50, 50), "Rated operational voltage Ue 415 V AC; test body exceeding fifty characters here.")
        doc.new_page()  # blank page 2 (<50 chars)
        doc.save(str(pdf_p))
        doc.close()

        res_pdf = extract_document(str(pdf_p))
        assert res_pdf["schema"] == SCHEMA_ID
        assert res_pdf["total_units"] == 2 and res_pdf["scanned_units"] == 2
        assert res_pdf["low_text_pages"] == [2], res_pdf
        assert res_pdf["units"][0]["location"] == "P1:L1"
        sum_pdf = build_summary(res_pdf)
        assert sum_pdf["text_unit_count"] == 1 and sum_pdf["recommended_page_batches"] == ["1-2"]
        sum_45 = build_summary({"format": "pdf", "total_units": 45, "scanned_units": 45, "units": []})
        assert sum_45["recommended_page_batches"] == ["1-20", "21-40", "41-45"], sum_45

        docx_p = td / "sample.docx"
        with zipfile.ZipFile(str(docx_p), "w") as zf:
            zf.writestr("word/document.xml", '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body><w:p><w:r><w:t>NXA Air Circuit-Breaker</w:t></w:r></w:p></w:body></w:document>')
        res_docx = extract_document(str(docx_p))
        assert res_docx["units"][0]["text"] == "NXA Air Circuit-Breaker"

        xlsx_p = td / "sample.xlsx"
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Specs"
        ws["B2"] = "Frame size 250 A"
        wb.save(str(xlsx_p))
        res_xlsx = extract_document(str(xlsx_p))
        assert res_xlsx["units"][0] == {"location": "Specs!B2", "text": "Frame size 250 A"}

    print("SELF-TEST PASS: extract_doc.py verified (.pdf + low_text_pages + --summary, .docx, .xlsx, schema).")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Generic CHINT office document extractor")
    parser.add_argument("source", nargs="?", help="Input (.pdf/.docx/.xlsx/.md/.txt) or '-'")
    parser.add_argument("--pages", help="PDF page range, e.g. 1-20 or 1,3,5")
    parser.add_argument("--json", action="store_true", help="Emit chint-office-extract/v1 JSON")
    parser.add_argument("--summary", action="store_true", help="Emit compact metadata, low_text_pages, and recommended batches without raw text")
    parser.add_argument("--self-test", action="store_true", help="Run built-in verification suite")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()
    if not args.source:
        parser.error("source is required unless --self-test is set")

    result = extract_document(args.source, parse_page_spec(args.pages))
    if args.summary:
        summary = build_summary(result)
        if args.json:
            print(json.dumps(summary, ensure_ascii=False, indent=2))
        else:
            print(f"{summary['format']} | total={summary['total_units']} | scanned={summary['scanned_units']} | text_units={summary['text_unit_count']} | low_text_pages={summary['low_text_pages']} | batches={summary['recommended_page_batches']}")
        return 0
    if args.json:
        print(json.dumps(result, ensure_ascii=False))
    else:
        print(f"{result['format']} | units={len(result['units'])} | scanned={result['scanned_units']}/{result['total_units']} | low_text_pages={result['low_text_pages']}")
        for u in result["units"][:25]:
            print(f"[{u['location']}] {u['text']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
