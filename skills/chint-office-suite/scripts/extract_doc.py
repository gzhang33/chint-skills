#!/usr/bin/env python3
"""Generic CHINT office document text & visual-page extractor (.pdf, .docx, .xlsx, .md/.txt)."""
from __future__ import annotations

import argparse
import importlib.metadata
import importlib.util
import json
import platform
import re
import sys
import tempfile
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

SCHEMA_ID = "chint-office-extract/v1"
LOW_TEXT_THRESHOLD = 50


def _ensure_utf8_stdio() -> None:
    """Force UTF-8 on stdio streams so piped JSON/text works on Windows cp936 consoles."""
    for stream in (sys.stdin, sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8")
            except (AttributeError, OSError, ValueError):
                pass


def _probe_module(mod_name: str, dist_name: str) -> dict[str, object]:
    """Check whether a third-party module is importable and report its version."""
    if importlib.util.find_spec(mod_name) is None:
        return {"available": False, "version": None}
    try:
        mod = __import__(mod_name)
        ver = getattr(mod, "__version__", None)
        if mod_name == "fitz" and hasattr(mod, "VersionBind"):
            ver = str(mod.VersionBind)
        elif not isinstance(ver, str) or len(ver) > 40:
            ver = None
        if not ver:
            try:
                ver = importlib.metadata.version(dist_name)
            except importlib.metadata.PackageNotFoundError:
                ver = None
        return {"available": True, "version": str(ver) if ver else None}
    except Exception:
        return {"available": False, "version": None}


def check_env() -> dict[str, object]:
    """Return runtime Python and optional office dependency availability."""
    deps = {
        "pymupdf": _probe_module("fitz", "pymupdf"),
        "openpyxl": _probe_module("openpyxl", "openpyxl"),
    }
    return {
        "python_version": platform.python_version(),
        "python_executable": sys.executable,
        "platform": sys.platform,
        "dependencies": deps,
        "ready": all(bool(v["available"]) for v in deps.values()),
    }


def _import_fitz():
    try:
        import fitz
        return fitz
    except ImportError as exc:
        raise RuntimeError("Missing dependency 'pymupdf' (fitz) required for .pdf extraction. Install with: pip install pymupdf") from exc


def _import_openpyxl():
    try:
        import openpyxl
        return openpyxl
    except ImportError as exc:
        raise RuntimeError("Missing dependency 'openpyxl' required for .xlsx extraction. Install with: pip install openpyxl") from exc


def parse_page_spec(spec: str | None) -> set[int] | None:
    if spec is None:
        return None
    cleaned = spec.strip()
    if not cleaned:
        raise ValueError("Empty --pages specification; provide e.g. '1-20' or '1,3,5'.")
    pages: set[int] = set()
    for part in cleaned.split(","):
        part = part.strip()
        if not part:
            raise ValueError(f"Invalid empty segment in --pages '{spec}'.")
        if "-" in part:
            m = re.fullmatch(r"(\d+)-(\d+)", part)
            if not m:
                raise ValueError(f"Invalid page range '{part}' in --pages '{spec}'; expected positive integers like '1-20'.")
            lo, hi = int(m.group(1)), int(m.group(2))
            if lo < 1 or hi < lo:
                raise ValueError(f"Invalid page range '{part}' in --pages '{spec}'; start must be >= 1 and <= end.")
            pages.update(range(lo, hi + 1))
        else:
            if not re.fullmatch(r"\d+", part) or int(part) < 1:
                raise ValueError(f"Invalid page number '{part}' in --pages '{spec}'; expected integer >= 1.")
            pages.add(int(part))
    if not pages:
        raise ValueError(f"Empty page selection from --pages '{spec}'.")
    return pages


def _docx_xml_sort_key(name: str) -> tuple[int, int, str]:
    stem = Path(name).stem
    if stem.startswith("header"):
        return (0, int(re.sub(r"\D+", "", stem) or 0), stem)
    if stem == "document":
        return (1, 0, stem)
    if stem == "footnotes":
        return (2, 0, stem)
    if stem == "endnotes":
        return (3, 0, stem)
    if stem == "comments":
        return (4, 0, stem)
    if stem.startswith("footer"):
        return (5, int(re.sub(r"\D+", "", stem) or 0), stem)
    return (6, 0, stem)


def _docx_para_text(elem: ET.Element, ns: str) -> str:
    parts: list[str] = []

    def _walk(node: ET.Element) -> None:
        tag = node.tag
        if tag == f"{ns}txbxContent":
            return
        if tag == f"{ns}t":
            if node.text:
                parts.append(node.text)
            return
        if tag == f"{ns}tab":
            parts.append("\t")
            return
        if tag in (f"{ns}br", f"{ns}cr"):
            parts.append("\n")
            return
        for child in node:
            _walk(child)

    for child in elem:
        _walk(child)
    return "".join(parts)


def extract_document(source: str, pages_filter: set[int] | None = None) -> dict:
    if source == "-":
        lines = sys.stdin.read().splitlines()
        units = [{"location": f"Line {i}", "text": l} for i, l in enumerate(lines, 1) if l.strip()]
        return {"schema": SCHEMA_ID, "source": "-", "format": "stdin", "total_units": len(lines), "scanned_units": len(lines), "low_text_pages": [], "uncached_formula_cells": [], "units": units}

    p = Path(source)
    if not p.exists():
        raise FileNotFoundError(f"Input not found: {source}")
    ext = p.suffix.lower()

    if ext in {".doc", ".xls"}:
        raise ValueError(f"Legacy binary format '{ext}' unsupported; convert to '.docx' or '.xlsx' first.")

    if ext == ".pdf":
        fitz = _import_fitz()
        try:
            doc = fitz.open(str(p))
        except Exception as exc:
            raise RuntimeError(f"Failed to open PDF '{source}': {exc}") from exc
        try:
            if doc.is_encrypted:
                raise ValueError(f"PDF '{source}' is encrypted/password-protected; decrypt before extraction.")
            total, scanned = len(doc), 0
            if pages_filter is not None:
                invalid = sorted(n for n in pages_filter if n > total)
                if invalid:
                    raise ValueError(f"--pages exceeds PDF page count ({total}): {invalid[:5]}")
            units, low_pages = [], []
            for idx, page in enumerate(doc, 1):
                if pages_filter is not None and idx not in pages_filter:
                    continue
                scanned += 1
                txt = page.get_text("text")
                if len(re.sub(r"\s+", "", txt)) < LOW_TEXT_THRESHOLD:
                    low_pages.append(idx)
                for lno, line in enumerate(txt.splitlines(), 1):
                    if line.strip():
                        units.append({"location": f"P{idx}:L{lno}", "text": line})
            return {"schema": SCHEMA_ID, "source": str(p), "format": "pdf", "total_units": total, "scanned_units": scanned, "low_text_pages": low_pages, "uncached_formula_cells": [], "units": units}
        finally:
            doc.close()

    if ext == ".docx":
        units = []
        ns = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
        with zipfile.ZipFile(str(p)) as zf:
            xml_names = [
                n for n in zf.namelist()
                if re.match(r"word/(header\d+|document|footnotes|endnotes|comments|footer\d+)\.xml$", n)
            ]
            for name in sorted(xml_names, key=_docx_xml_sort_key):
                root = ET.fromstring(zf.read(name))
                stem = Path(name).stem
                for p_idx, para in enumerate(root.iter(f"{ns}p"), 1):
                    txt = _docx_para_text(para, ns)
                    if txt.strip():
                        units.append({"location": f"{stem}:P{p_idx}", "text": txt})
        return {"schema": SCHEMA_ID, "source": str(p), "format": "docx", "total_units": len(units), "scanned_units": len(units), "low_text_pages": [], "uncached_formula_cells": [], "units": units}

    if ext in {".xlsx", ".xlsm"}:
        openpyxl = _import_openpyxl()
        wb = openpyxl.load_workbook(str(p), data_only=True, read_only=True)
        wb_f = openpyxl.load_workbook(str(p), data_only=False, read_only=True)
        units = []
        uncached_formulas: list[str] = []
        try:
            for sname in wb.sheetnames:
                ws = wb[sname]
                ws_f = wb_f[sname]
                for r_idx, (row, row_f) in enumerate(zip(ws.iter_rows(values_only=True), ws_f.iter_rows(values_only=True)), 1):
                    for c_idx, (val, raw_val) in enumerate(zip(row, row_f), 1):
                        col = openpyxl.utils.get_column_letter(c_idx)
                        coord = f"{sname}!{col}{r_idx}"
                        if val is not None and str(val).strip():
                            units.append({"location": coord, "text": str(val)})
                        elif val is None and isinstance(raw_val, str) and raw_val.startswith("="):
                            uncached_formulas.append(coord)
            sheet_cnt = len(wb.sheetnames)
        finally:
            wb.close()
            wb_f.close()
        if uncached_formulas:
            sample = ", ".join(uncached_formulas[:5]) + ("..." if len(uncached_formulas) > 5 else "")
            print(f"WARNING: {len(uncached_formulas)} uncached .xlsx formula cell(s) have empty cached values ({sample}); open/save in Excel to populate cache.", file=sys.stderr)
        return {"schema": SCHEMA_ID, "source": str(p), "format": ext.lstrip("."), "total_units": sheet_cnt, "scanned_units": sheet_cnt, "low_text_pages": [], "uncached_formula_cells": uncached_formulas, "units": units}

    lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
    units = [{"location": f"Line {i}", "text": l} for i, l in enumerate(lines, 1) if l.strip()]
    return {"schema": SCHEMA_ID, "source": str(p), "format": ext.lstrip(".") or "text", "total_units": len(lines), "scanned_units": len(lines), "low_text_pages": [], "uncached_formula_cells": [], "units": units}


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
        "uncached_formula_cells": result.get("uncached_formula_cells", []),
        "recommended_page_batches": batches,
    }


def run_self_test() -> int:
    fitz = _import_fitz()
    openpyxl = _import_openpyxl()

    for bad_spec in ("5-2", "abc", "0", "-3", "1-"):
        try:
            parse_page_spec(bad_spec)
            raise AssertionError(f"Expected ValueError for --pages '{bad_spec}'")
        except ValueError:
            pass
    assert parse_page_spec("1-3,5") == {1, 2, 3, 5}

    with tempfile.TemporaryDirectory() as tmp:
        td = Path(tmp)
        pdf_p = td / "sample.pdf"
        doc = fitz.open()
        p1 = doc.new_page()
        p1.insert_text((50, 50), "Section 1: Overview specification body exceeding fifty characters here.")
        doc.new_page()  # blank page 2 (<50 chars)
        doc.save(str(pdf_p))
        doc.close()

        res_pdf = extract_document(str(pdf_p), pages_filter=parse_page_spec("1-2"))
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
            zf.writestr("word/header1.xml", '<w:hdr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:p><w:r><w:t>DocHeader</w:t></w:r></w:p></w:hdr>')
            zf.writestr(
                "word/document.xml",
                '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body>'
                '<w:p><w:r><w:t>250</w:t><w:tab/><w:t>A</w:t><w:br/><w:t>415 V</w:t></w:r></w:p>'
                '<w:p><w:r><w:pict><w:txbxContent><w:p><w:r><w:t>InnerTextbox</w:t></w:r></w:p></w:txbxContent></w:pict></w:r></w:p>'
                '</w:body></w:document>',
            )
            zf.writestr("word/footer1.xml", '<w:ftr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:p><w:r><w:t>DocFooter</w:t></w:r></w:p></w:ftr>')
        res_docx = extract_document(str(docx_p))
        docx_texts = [u["text"] for u in res_docx["units"]]
        assert res_docx["units"][0]["location"] == "header1:P1" and res_docx["units"][-1]["location"] == "footer1:P1", res_docx
        assert "250\tA\n415 V" in docx_texts, docx_texts
        assert docx_texts.count("InnerTextbox") == 1, docx_texts

        xlsx_p = td / "sample.xlsx"
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Specs"
        ws["A1"] = "Parameter A"
        ws["B1"] = "=10*2"  # uncached formula created programmatically
        wb.save(str(xlsx_p))
        wb.close()
        res_xlsx = extract_document(str(xlsx_p))
        assert res_xlsx["units"][0] == {"location": "Specs!A1", "text": "Parameter A"}, res_xlsx
        assert res_xlsx["uncached_formula_cells"] == ["Specs!B1"], res_xlsx

    env_info = check_env()
    assert isinstance(env_info.get("python_version"), str) and env_info["python_version"], env_info
    assert set(env_info.get("dependencies", {})) == {"pymupdf", "openpyxl"}, env_info
    assert env_info["ready"] is True, env_info

    print("SELF-TEST PASS: extract_doc.py verified (.pdf + strict --pages + low_text_pages, .docx separators/txbx, .xlsx uncached formulas, --check-env).")
    return 0


def main() -> int:
    _ensure_utf8_stdio()
    parser = argparse.ArgumentParser(description="Generic CHINT office document extractor")
    parser.add_argument("source", nargs="?", help="Input (.pdf/.docx/.xlsx/.md/.txt) or '-'")
    parser.add_argument("--pages", help="PDF page range, e.g. 1-20 or 1,3,5")
    parser.add_argument("--json", action="store_true", help="Emit chint-office-extract/v1 JSON")
    parser.add_argument("--summary", action="store_true", help="Emit compact metadata, low_text_pages, and recommended batches without raw text")
    parser.add_argument("--check-env", action="store_true", help="Check Python and pymupdf/openpyxl runtime availability as JSON")
    parser.add_argument("--self-test", action="store_true", help="Run built-in verification suite")
    args = parser.parse_args()

    try:
        if args.self_test:
            return run_self_test()
        if args.check_env:
            info = check_env()
            print(json.dumps(info, ensure_ascii=False, indent=2))
            return 0 if info["ready"] else 1
        if not args.source:
            parser.error("source is required unless --self-test or --check-env is set")

        result = extract_document(args.source, parse_page_spec(args.pages))
        if args.summary:
            summary = build_summary(result)
            if args.json:
                print(json.dumps(summary, ensure_ascii=False, indent=2))
            else:
                print(f"{summary['format']} | total={summary['total_units']} | scanned={summary['scanned_units']} | text_units={summary['text_unit_count']} | low_text_pages={summary['low_text_pages']} | uncached_formulas={len(summary['uncached_formula_cells'])} | batches={summary['recommended_page_batches']}")
            return 0
        if args.json:
            print(json.dumps(result, ensure_ascii=False))
        else:
            print(f"{result['format']} | units={len(result['units'])} | scanned={result['scanned_units']}/{result['total_units']} | low_text_pages={result['low_text_pages']} | uncached_formulas={len(result['uncached_formula_cells'])}")
            for u in result["units"][:25]:
                print(f"[{u['location']}] {u['text']}")
        return 0
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())