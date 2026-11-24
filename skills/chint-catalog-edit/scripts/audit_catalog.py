#!/usr/bin/env python3
"""Pure-stdlib + optional Office-ready CHINT catalogue proofreading & PDF annotation engine.

Supports 100% standalone operation AND automatic sibling synergy:
- Prefers sibling `chint-office-suite` for Office extraction & PDF annotation when installed;
  otherwise runs built-in extractors (.pdf/.docx/.xlsx) and non-destructive PDF annotator.
- Prefers sibling `chint-translation` for IEC/GB rules & EN blacklist when installed;
  otherwise falls back to BUILTIN_SSOT_FALLBACK (parity-verified by --self-test).
"""
from __future__ import annotations

import argparse
import importlib.metadata
import importlib.util
import json
import platform
import re
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

LOW_TEXT_THRESHOLD = 50
YELLOW = (1.0, 0.92, 0.23)


def _ensure_utf8_stdio() -> None:
    """Force UTF-8 on stdio streams so piped JSON/text works on Windows cp936 consoles."""
    for stream in (sys.stdin, sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8")
            except (AttributeError, OSError, ValueError):
                pass


# ---------------------------------------------------------------------------
# Environment & Sibling Skill Resolution
# ---------------------------------------------------------------------------

def _probe_module(mod_name: str, dist_name: str) -> dict[str, object]:
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


def resolve_sibling_skill(skill_name: str, sentinel_rel: str, explicit_dir: str | None = None) -> Path | None:
    if explicit_dir is not None:
        cand = Path(explicit_dir).expanduser()
        return cand if (cand / sentinel_rel).is_file() else None
    skill_root = Path(__file__).resolve().parent.parent
    candidates = [
        skill_root.parent / skill_name,
        Path.home() / ".skills-manager" / "skills" / skill_name,
    ]
    for cand in candidates:
        if (cand / sentinel_rel).is_file():
            return cand
    return None


def resolve_translation_skill(explicit_dir: str | None = None) -> Path | None:
    return resolve_sibling_skill("chint-translation", "scripts/lint_text.py", explicit_dir)


def resolve_office_skill(explicit_dir: str | None = None) -> Path | None:
    return resolve_sibling_skill("chint-office-suite", "scripts/extract_doc.py", explicit_dir)


def check_env(office_dir: str | None = None, translation_dir: str | None = None) -> dict[str, object]:
    deps = {
        "pymupdf": _probe_module("fitz", "pymupdf"),
        "openpyxl": _probe_module("openpyxl", "openpyxl"),
    }
    off = resolve_office_skill(office_dir)
    trn = resolve_translation_skill(translation_dir)
    return {
        "python_version": platform.python_version(),
        "python_executable": sys.executable,
        "platform": sys.platform,
        "standalone_ready_for_text_and_docx": True,
        "standalone_ready_for_pdf_and_xlsx": all(bool(v["available"]) for v in deps.values()),
        "dependencies": deps,
        "siblings": {
            "chint-office-suite": str(off) if off else None,
            "chint-translation": str(trn) if trn else None,
        },
        "ready": all(bool(v["available"]) for v in deps.values()),
    }


# ---------------------------------------------------------------------------
# Built-in SSOT Fallback (parity-checked against chint-translation in --self-test)
# ---------------------------------------------------------------------------

BUILTIN_SSOT_FALLBACK: dict[str, object] = {
    "BLACKLIST_COMMON": [
        (r"\bshunting release\b", "Shunt release (SHT)"),
        (r"\bshunt opening release\b", "Shunt release (SHT)"),
        (r"\bexcitation release\b", "Shunt release (SHT)"),
        (r"\bshunt trip\b", "Shunt release (SHT)"),
        (r"\black voltage\b", "Undervoltage release (UVT)"),
        (r"\bclosing magnet\b", "Closing release (CEM)"),
        (r"\bten thousand times\b", "plain integer operating cycles"),
        (r"\binstallation and debugging\b", "installation and commissioning"),
        (r"\bmatters need attention\b", "operating precautions"),
        (r"\bordering instruction\b", "ordering information"),
        (r"\bwrong action\b", "false tripping"),
        (r"\berror work\b", "false tripping"),
        (r"\bno tolerance specified\b", "unspecified linear tolerance"),
        (r"\buse class(?:es)?\b", "selectivity category / utilization category"),
        (r"\bdrawer(?:\s+(?:type|box|seat|cradle|base))?\b", "Withdrawable / Withdrawable cradle (IEC Cl. 3.5)"),
    ],
    "BLACKLIST_ACB": [
        (r"\bclosed electromagnet\b", "Closing release (CEM)"),
        (r"\bclose electromagnet\b", "Closing release (CEM)"),
        (r"\bclosing electromagnet\b", "Closing release (CEM)"),
        (r"\bearch current transformer\b", "Earth current transformer (ECT)"),
        (r"\binterphased\b", "interphase barrier (DD / FD)"),
        (r"\binter phased\b", "interphase barrier (DD / FD)"),
        (r"\bphase space plate\b", "interphase barrier (DD / FD)"),
        (r"\bunder voltage delay release-zero\b", "Loss-of-voltage time-delay release (UVTZ)"),
        (r"\bclosing preparation contact\b", "Ready-to-close contact (SPC)"),
        (r"\bseparation position\b", "Disconnected position (Cl. 8.1.2)"),
        (r"\bconnection position\b", "Connected position (Cl. 8.1.2)"),
        (r"\bhole opener\b", "panel hole saw"),
        (r"\bface mask\b", "Door escutcheon"),
        (r"\bstorage hole\b", "Racking handle storage slot"),
        (r"\bbody key lock\b", "Key lock (KL)"),
        (r"\brefuses to open\b", "does not trip / cannot be opened"),
        (r"\bis forbidden to open\b", "cannot be opened"),
        (r"\birrelevant to\b", "independent of"),
        (r"\bpulse energization working mode\b", "pulse-energization duty"),
        (r"\buniversal circuit[- ]breaker\b", "Air circuit-breaker (ACB)"),
        (r"\bintelligent air circuit[- ]breaker\b", "Air circuit-breaker with electronic trip unit"),
        (r"\blvpcb\b", "Air circuit-breaker (ACB)"),
    ],
    "BLACKLIST_MCCB": [
        (r"\bplastic shell breaker\b", "Moulded-case circuit-breaker (MCCB)"),
        (r"\bplastic case breaker\b", "Moulded-case circuit-breaker (MCCB)"),
        (r"\bleakage plastic shell\b", "Circuit-breaker incorporating residual current protection (CBR)"),
        (r"\bearth leakage breaker\b", "Circuit-breaker incorporating residual current protection (CBR)"),
        (r"\belcb\b", "Circuit-breaker incorporating residual current protection (CBR)"),
        (r"\bmotor circuit protector\b", "Instantaneous trip circuit-breaker (ICB) (Annex O)"),
        (r"\bnon-automatic breaker\b", "CBI (Annex L) / switch-disconnector (IEC 60947-3)"),
        (r"\bdouble breaking point\b", "Rotary double-break contact system"),
        (r"\bback wiring\b", "Rear connection (HR / VR)"),
        (r"\binsert installation\b", "Plug-in base"),
        (r"\brotate handle\b", "Rotary handle"),
        (r"\bwire cover\b", "Terminal shield"),
        (r"\bmotor hand\b", "Motor-operator (MOD)"),
    ],
    "COMPETITOR_RULES_COMMON": [
        (r"(?<![A-Za-z0-9\-])MX(?![A-Za-z0-9\-])", "SHT (Shunt release)"),
        (r"(?<![A-Za-z0-9\-])MN(?![A-Za-z0-9\-])", "UVT (Undervoltage release)"),
        (r"(?<![A-Za-z0-9\-])SDE(?![A-Za-z0-9\-])", "AL (Alarm switch)"),
        (r"\(OF\)", "(AX) (Auxiliary contact)"),
        (r"\(YO\)", "(SHT) (Shunt release)"),
    ],
    "COMPETITOR_RULES_ACB": [
        (r"(?<![A-Za-z0-9\-])XF(?![A-Za-z0-9\-])", "CEM (Closing release)"),
        (r"\(PF\)|\bPF\s+contact\b", "SPC (Ready-to-close contact)"),
        (r"(?<![A-Za-z0-9\-])MCH(?![A-Za-z0-9\-])", "MOD (Motor-operator)"),
        (r"(?<![A-Za-z0-9\-])KLC(?![A-Za-z0-9\-])", "KL (Key lock)"),
    ],
    "STD_CONCEPT_ZH": [
        (r"相间对中性线", "相-中性线 (IEC 60947-2:2024 Cl. 5.3.6.2.3)"),
        (r"(?<![单两二三四多])极极限", "单极极限"),
        (r"隔离开关断路器", "隔离开关 (IEC 60947-3 / GB/T 14048.3)"),
        (r"使用类别\s*[AB]", "选择性类别 A / B (GB/T 14048.2—2020 Cl. 3.1 / 4.4)"),
        (r"抽出式断路器", "抽屉式断路器 (GB/T 14048.2—2020 Cl. 2.5 / 3.7)"),
        (r"结构差异", "结构段 (GB/T 14048.2—2020 Cl. 2.1.2 / 7.1.6)"),
        (r"合闸涌流脱扣器", "接通电流脱扣器 (GB/T 14048.2—2020 Cl. 2.10)"),
    ],
    "STD_STATUTORY_ZH": [
        (r"闭合电磁铁|合闸电磁铁|释能电磁铁", "闭合脱扣器 (GB/T 14048.2—2020 Cl. 2.23)"),
        (r"万能式断路器", "空气断路器（分类：万能式） (GB/T 14048.2—2020 Cl. 2.7 / 3.3)"),
        (r"(?<!塑料外壳式)塑壳断路器", "塑料外壳式断路器 (GB/T 14048.2—2020 Cl. 2.6 / 3.3)"),
        (r"功率损耗", "功耗 (GB/T 14048.2—2020 附录 G)"),
        (r"(?<![\"“])分离位置|“分离”\s*位置", "隔离位置 (GB/T 14048.2—2020 Cl. 7.1.2)"),
        (r"\bInm\b", "壳架等级（GB/T 14048.2—2020 Cl. 2.1.1 / IEC 3.1.1 未定义 Inm 符号）"),
        (r"漏电保护|漏电互感器", "剩余电流保护 / 剩余电流互感器 (GB/T 14048.2—2020 附录 B/M)"),
    ],
    "ED5_CLAUSE_RE": re.compile(
        r"(?:Cl\.|Clause)\s*(?:2\.1(?:\.\d+)?|4\.3\.[1-6](?:\.\d+)?|7\.2\.[1-8](?:\.\d+)?|8\.3\.[1-9](?:\.\d+)?)\b",
        re.IGNORECASE,
    ),
    "ED5_GUARD_TAGS": ("60947-1", "60947-3", "14048.2", "GB/T"),
}


def load_translation_ssot(translation_dir: Path | None) -> tuple[dict, str, str | None]:
    if translation_dir is not None:
        lint_path = translation_dir / "scripts" / "lint_text.py"
        if lint_path.is_file():
            spec = importlib.util.spec_from_file_location("_chint_translation_ssot", str(lint_path))
            if spec is not None and spec.loader is not None:
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                ssot = {
                    "BLACKLIST_COMMON": list(getattr(mod, "BLACKLIST_COMMON", [])),
                    "BLACKLIST_ACB": list(getattr(mod, "BLACKLIST_ACB", [])),
                    "BLACKLIST_MCCB": list(getattr(mod, "BLACKLIST_MCCB", [])),
                    "COMPETITOR_RULES_COMMON": list(getattr(mod, "COMPETITOR_RULES_COMMON", [])),
                    "COMPETITOR_RULES_ACB": list(getattr(mod, "COMPETITOR_RULES_ACB", [])),
                    "STD_CONCEPT_ZH": list(getattr(mod, "STD_CONCEPT_ZH", [])),
                    "STD_STATUTORY_ZH": list(getattr(mod, "STD_STATUTORY_ZH", [])),
                    "ED5_CLAUSE_RE": getattr(mod, "ED5_CLAUSE_RE", None),
                    "ED5_GUARD_TAGS": tuple(getattr(mod, "ED5_GUARD_TAGS", ())),
                }
                return ssot, "sibling:chint-translation", str(translation_dir)
    return dict(BUILTIN_SSOT_FALLBACK), "builtin-standalone", None


# ---------------------------------------------------------------------------
# Office Extraction & PDF Annotation (Sibling-First + Built-in Standalone)
# ---------------------------------------------------------------------------

def _import_fitz():
    try:
        import fitz
        return fitz
    except ImportError as exc:
        raise RuntimeError(
            "Missing dependency 'pymupdf' (fitz) required for .pdf processing. "
            "Install with: python3 -m pip install --user -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple"
        ) from exc


def _import_openpyxl():
    try:
        import openpyxl
        return openpyxl
    except ImportError as exc:
        raise RuntimeError(
            "Missing dependency 'openpyxl' required for .xlsx processing. "
            "Install with: python3 -m pip install --user -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple"
        ) from exc


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


def _extract_office_builtin(source: str, pages_filter: set[int] | None = None) -> dict:
    p = Path(source)
    if not p.exists():
        raise FileNotFoundError(f"Input not found: {source}")
    ext = p.suffix.lower()
    if ext in {".doc", ".xls"}:
        raise ValueError(f"Legacy binary format '{ext}' unsupported; convert to '.docx' or '.xlsx' first.")

    if ext == ".pdf":
        fitz = _import_fitz()
        doc = fitz.open(str(p))
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
            return {
                "schema": "chint-office-extract/v1",
                "source": str(p),
                "format": "pdf",
                "total_units": total,
                "scanned_units": scanned,
                "low_text_pages": low_pages,
                "uncached_formula_cells": [],
                "units": units,
            }
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
        return {
            "schema": "chint-office-extract/v1",
            "source": str(p),
            "format": "docx",
            "total_units": len(units),
            "scanned_units": len(units),
            "low_text_pages": [],
            "uncached_formula_cells": [],
            "units": units,
        }

    if ext in {".xlsx", ".xlsm"}:
        openpyxl = _import_openpyxl()
        wb = openpyxl.load_workbook(str(p), data_only=True, read_only=True)
        wb_f = openpyxl.load_workbook(str(p), data_only=False, read_only=True)
        units, uncached = [], []
        try:
            for sname in wb.sheetnames:
                ws, ws_f = wb[sname], wb_f[sname]
                for r_idx, (row, row_f) in enumerate(zip(ws.iter_rows(values_only=True), ws_f.iter_rows(values_only=True)), 1):
                    for c_idx, (val, raw_val) in enumerate(zip(row, row_f), 1):
                        col = openpyxl.utils.get_column_letter(c_idx)
                        coord = f"{sname}!{col}{r_idx}"
                        if val is not None and str(val).strip():
                            units.append({"location": coord, "text": str(val)})
                        elif val is None and isinstance(raw_val, str) and raw_val.startswith("="):
                            uncached.append(coord)
            sheet_cnt = len(wb.sheetnames)
        finally:
            wb.close()
            wb_f.close()
        if uncached:
            sample = ", ".join(uncached[:5]) + ("..." if len(uncached) > 5 else "")
            print(f"WARNING: {len(uncached)} uncached .xlsx formula cell(s) ({sample}).", file=sys.stderr)
        return {
            "schema": "chint-office-extract/v1",
            "source": str(p),
            "format": ext.lstrip("."),
            "total_units": sheet_cnt,
            "scanned_units": sheet_cnt,
            "low_text_pages": [],
            "uncached_formula_cells": uncached,
            "units": units,
        }

    lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
    units = [{"location": f"Line {i}", "text": l} for i, l in enumerate(lines, 1) if l.strip()]
    return {"schema": "chint-office-extract/v1", "source": str(p), "format": ext.lstrip(".") or "text", "total_units": len(lines), "scanned_units": len(lines), "low_text_pages": [], "uncached_formula_cells": [], "units": units}


def load_units(source: str, pages_spec: str | None = None, office_dir: Path | None = None) -> dict:
    pages_filter = parse_page_spec(pages_spec)
    if source != "-":
        p = Path(source)
        ext = p.suffix.lower()
        if ext in {".pdf", ".docx", ".xlsx", ".xlsm", ".doc", ".xls"}:
            if office_dir is not None and (office_dir / "scripts" / "extract_doc.py").is_file():
                spec = importlib.util.spec_from_file_location("_chint_office_extract", str(office_dir / "scripts" / "extract_doc.py"))
                if spec is not None and spec.loader is not None:
                    mod = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(mod)
                    obj = mod.extract_document(str(p), mod.parse_page_spec(pages_spec))
                    units = [(str(u["location"]), str(u["text"])) for u in obj.get("units", [])]
                    return {
                        "source": obj.get("source", source),
                        "format": obj.get("format", ext.lstrip(".")),
                        "office_engine": "sibling:chint-office-suite",
                        "total": obj.get("total_units", len(units)),
                        "scanned": obj.get("scanned_units", len(units)),
                        "low_text_pages": obj.get("low_text_pages", []),
                        "uncached_formula_cells": obj.get("uncached_formula_cells", []),
                        "units": units,
                    }
            obj = _extract_office_builtin(str(p), pages_filter)
            units = [(str(u["location"]), str(u["text"])) for u in obj.get("units", [])]
            return {
                "source": obj.get("source", source),
                "format": obj.get("format", ext.lstrip(".")),
                "office_engine": "builtin-standalone",
                "total": obj.get("total_units", len(units)),
                "scanned": obj.get("scanned_units", len(units)),
                "low_text_pages": obj.get("low_text_pages", []),
                "uncached_formula_cells": obj.get("uncached_formula_cells", []),
                "units": units,
            }

    raw = sys.stdin.read() if source == "-" else Path(source).read_text(encoding="utf-8", errors="replace")
    stripped = raw.lstrip()
    if stripped.startswith("{"):
        try:
            obj = json.loads(raw)
            if isinstance(obj, dict) and obj.get("schema") == "chint-office-extract/v1":
                units = [(str(u["location"]), str(u["text"])) for u in obj.get("units", [])]
                return {
                    "source": obj.get("source", source),
                    "format": obj.get("format", "extract-json"),
                    "office_engine": "pre-extracted-json",
                    "total": obj.get("total_units", len(units)),
                    "scanned": obj.get("scanned_units", len(units)),
                    "low_text_pages": obj.get("low_text_pages", []),
                    "uncached_formula_cells": obj.get("uncached_formula_cells", []),
                    "units": units,
                }
        except json.JSONDecodeError:
            pass
    lines = raw.splitlines()
    units = [(f"Line {i}", l) for i, l in enumerate(lines, 1) if l.strip()]
    return {
        "source": source,
        "format": "text",
        "office_engine": "builtin-standalone",
        "total": len(lines),
        "scanned": len(lines),
        "low_text_pages": [],
        "uncached_formula_cells": [],
        "units": units,
    }


def _collect_terms(item: dict) -> list[str]:
    raw: list[str] = []
    if item.get("search"):
        raw.append(str(item["search"]).strip())
    for s in item.get("searches") or []:
        st = str(s).strip()
        if st:
            raw.append(st)
    seen: set[str] = set()
    out: list[str] = []
    for t in raw:
        if t and t not in seen:
            seen.add(t)
            out.append(t)
    return out


def _annotate_pdf_builtin(input_pdf: Path, items: list[dict], output_pdf: Path, default_author: str = "CHINT Catalog Edit") -> dict:
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

            all_rects: list = []
            seen_sig: set[tuple[float, float, float, float]] = set()
            for t in terms:
                for r in page.search_for(t):
                    sig = (round(r.x0, 1), round(r.y0, 1), round(r.x1, 1), round(r.y1, 1))
                    if sig not in seen_sig:
                        seen_sig.add(sig)
                        all_rects.append(r)

            if all_rects:
                matched_items += 1
                if mode == "merged":
                    annot = page.add_highlight_annot(all_rects)
                    annot.set_colors(stroke=YELLOW)
                    annot.set_info(title=author, content=comment)
                    annot.update()
                    highlights += 1
                    rect_count += len(all_rects)
                else:
                    targets = [all_rects[0]] if mode == "first" else all_rects
                    for r in targets:
                        annot = page.add_highlight_annot([r])
                        annot.set_colors(stroke=YELLOW)
                        annot.set_info(title=author, content=comment)
                        annot.update()
                        highlights += 1
                        rect_count += 1
            else:
                idx_on_page = page_stickies.get(pno, 0)
                page_stickies[pno] = idx_on_page + 1
                prect = page.rect
                rows_per_col = max(1, int((prect.height - 32) // 22))
                col = idx_on_page // rows_per_col
                row = idx_on_page % rows_per_col
                x = prect.x0 + 16 if col == 0 else max(prect.x0 + 16, prect.x1 - 34 - (col - 1) * 24)
                y = min(prect.y1 - 24, prect.y0 + 16 + row * 22)
                label = terms[0] if len(terms) == 1 else (", ".join(terms[:3]) + (" 等" if len(terms) > 3 else "") if terms else "")
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
            "schema": "chint-office-annotate/v1",
            "office_engine": "builtin-standalone",
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


def write_annotated_pdf(
    input_pdf: Path,
    items: list[dict],
    output_pdf: Path,
    default_author: str = "CHINT Catalog Edit",
    office_dir: Path | None = None,
) -> dict:
    if office_dir is not None and (office_dir / "scripts" / "annotate_pdf.py").is_file():
        spec = importlib.util.spec_from_file_location("_chint_office_annotate", str(office_dir / "scripts" / "annotate_pdf.py"))
        if spec is not None and spec.loader is not None:
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            res = mod.annotate_pdf(input_pdf, items, output_pdf, default_author=default_author)
            res["office_engine"] = "sibling:chint-office-suite"
            return res
    return _annotate_pdf_builtin(input_pdf, items, output_pdf, default_author=default_author)


# ---------------------------------------------------------------------------
# L1 / L2 Catalogue Rules
# ---------------------------------------------------------------------------

ZH_TYPOS_GRAMMAR: list[tuple[str, str]] = [
    (r"海拨", "海拔"),
    (r"遥至", "摇至"),
    (r"引导起", "引起 / 导致"),
    (r"并虑到", "并考虑到"),
    (r"特殊申明", "特殊声明"),
    (r"轴侧图", "轴测图"),
    (r"润滑酯", "润滑脂"),
    (r"互感器互感器", "互感器"),
    (r"互感器电流互感器", "电流互感器 / 中性线互感器"),
    (r"欠电压\s*电压等级", "欠电压等级"),
    (r"当产品配置不配置", "当产品不配置"),
    (r"调整至为", "调整范围为 / 整定范围为"),
    (r"步调\s*\d+", "步长（参数调节步长）"),
    (r"居于垂直于水平", "明确安装方位（垂直位置 / 水平位置）"),
]

SAME_PAGE_CONFLICT_GROUPS: list[tuple[str, list[tuple[str, str]]]] = [
    ("防护罩名称同页不一致", [(r"透明保护罩", "透明保护罩"), (r"透明防护罩", "透明防护罩")]),
    ("分闸/分断按钮名称同页不一致", [(r"分断按钮", "分断按钮"), (r"分闸按钮", "分闸按钮")]),
]

CROSS_PAGE_SYNONYM_GROUPS: list[tuple[str, list[tuple[str, str]], str]] = [
    ("欠电压脱扣器简称混用", [(r"欠电压(?:延时|瞬时)?脱扣器", "欠电压脱扣器"), (r"欠压(?:延时|瞬时)?脱扣器|无欠压", "欠压脱扣器/无欠压")], "全册统一为「欠电压脱扣器 / 无欠电压」"),
    ("电动操作机构名称混用", [(r"电动储能机构", "电动储能机构"), (r"储能电动机", "储能电动机"), (r"储能电机", "储能电机"), (r"电动操作机构", "电动操作机构"), (r"电动机操作机构", "电动机操作机构")], "全册统一为「电动机操作机构」（或明确区分机构与电机）"),
    ("电子脱扣器/控制器名称混用", [(r"智能型控制器", "智能型控制器"), (r"智能控制器", "智能控制器"), (r"智能脱扣器", "智能脱扣器")], "全册统一控制器称谓（如「智能型控制器」或「电子脱扣器」）"),
    ("外接/外置互感器混用", [(r"外接互感器", "外接互感器"), (r"外置互感器", "外置互感器")], "全册统一为「外接互感器」或「外置互感器」"),
    ("联锁/连锁混用", [(r"联锁", "联锁"), (r"连锁", "连锁")], "全册统一为「联锁」"),
    ("连接/联结/联接混用", [(r"连接", "连接"), (r"联结", "联结"), (r"联接", "联接")], "全册统一为「连接」"),
    ("热磁式/热电磁式混用", [(r"热电磁式", "热电磁式"), (r"热磁式", "热磁式")], "全册统一为「热磁式」或「热电磁式」"),
    ("电气寿命/电寿命混用", [(r"电气寿命", "电气寿命"), (r"(?<!电)电寿命", "电寿命")], "全册统一为「电气寿命」"),
    ("防护罩/保护罩跨页混用", [(r"透明防护罩", "透明防护罩"), (r"透明保护罩", "透明保护罩")], "全册统一为「透明防护罩」"),
    ("默认/缺省混用", [(r"默认", "默认"), (r"缺省", "缺省")], "全册统一为「默认」"),
    ("通信/通讯混用", [(r"通信", "通信"), (r"通讯", "通讯")], "全册统一为「通信」"),
    ("其他/其它混用", [(r"其他", "其他"), (r"其它", "其它")], "全册统一为「其他」"),
    ("短路瞬时/瞬动混用", [(r"短路瞬时", "短路瞬时"), (r"短路瞬动", "短路瞬动")], "全册统一为「短路瞬时保护」"),
]

L2_CASE_NOTATION_RULES: list[tuple[str, str]] = [
    (r"(?<![A-Za-z0-9])\d+(?:\.\d+)?\s*KA\b", "kA（千安符号前缀 k 须小写）"),
    (r"\bSb\d+\b", "SB（按钮代号字母须全大写，如 SB1）"),
    (r"COSΦ|CosΦ", "cos φ（功率因数符号规范写法）"),
    (r"\bST~DP\b", "ST-DP（型号连字符误印为 ~）"),
    (r"\b[A-Z]{1,3}\d*\s*一[\u4e00-\u9fff]", "改用破折号「—」或冒号「：」（误用汉字「一」作分隔符）"),
    (r"\b\d+k\d+b\b", "改用标准中文表述（如「3 常开 3 常闭」，避免拼音简写）"),
    (r"部份", "部分（统一简体规范字形）"),
    (r"订做", "定制 / 定做（建议统一为「定制」）"),
]

HIGH_CATS = {
    "TECH_HARD_ERROR",
    "TYPO_GRAMMAR_ZH",
    "CROSSREF_NUMBERING",
    "SAME_PAGE_INCONSISTENCY",
    "EN_SEVERE_ERROR",
    "COMPETITOR_CODE",
    "STD_CONCEPT_ERROR",
    "OBSOLETE_CLAUSE_ED5",
    "UNRESOLVED_SLOT",
}


def detect_mode(units: list[tuple[str, str]]) -> str:
    sample = " ".join(txt for _, txt in units[:200])
    cjk = len(re.findall(r"[\u4e00-\u9fff]", sample))
    lat = len(re.findall(r"[A-Za-z]", sample))
    if cjk == 0 and lat > 0:
        return "en"
    if cjk >= max(2, int(0.15 * (cjk + lat))):
        return "zh"
    return "en"


def _page_key(loc: str) -> str:
    m = re.match(r"^(P\d+):", loc)
    return m.group(1) if m else "__all__"


def _severity(cat: str) -> str:
    return "HIGH" if cat in HIGH_CATS else "MEDIUM"


def scan_units(
    units: list[tuple[str, str]],
    profile: str = "L1",
    mode: str = "auto",
    with_iec: bool = False,
    dept: str = "all",
    ssot: dict | None = None,
) -> list[dict]:
    if mode == "auto":
        mode = detect_mode(units)
    if ssot is None:
        ssot, _, _ = load_translation_ssot(resolve_translation_skill())

    run_l2 = profile in {"L2", "L3"}
    run_iec_concept = with_iec or profile == "L3"
    run_iec_statutory = with_iec or profile == "L3"

    findings: list[dict] = []

    def add(loc: str, cat: str, matched: str, fix: str, line: str) -> None:
        findings.append({
            "location": loc,
            "severity": _severity(cat),
            "category": cat,
            "match": matched,
            "fix": fix,
            "excerpt": line[:120],
            "_full_line": line,
        })

    ed5_re = ssot.get("ED5_CLAUSE_RE")
    ed5_guards = ssot.get("ED5_GUARD_TAGS", ())
    pf_context_re = re.compile(r"(?i)power\s+factor|\bcos\s*[φϕ]?|功率因数")
    cat_a_re = re.compile(r"(?:Selectivity[ \t]+category[ \t]*[:：]?[ \t]*A\b|选择性类别[ \t]*[:：]?[ \t]*A\b)(?![ \t]*[/、,])", re.IGNORECASE)
    cat_b_re = re.compile(r"(?:Selectivity[ \t]+category[ \t]*[:：]?[ \t]*B\b|选择性类别[ \t]*[:：]?[ \t]*B\b|\bCategory[ \t]+B\b)", re.IGNORECASE)
    model_hdr_re = re.compile(r"^\s*(?:NX[AMF]\d|NM\d|NA\d|DW\d)")
    st_or_icw_re = re.compile(r"\b(?:Isd|Icw)\b")
    type_fb_re = re.compile(r"\bType[ \t]+(?:F|B\+)\b", re.IGNORECASE)
    fig_caption_re = re.compile(r"^(图\s*\d+(?:-\d+)?)\s*$")

    blocks: dict[str, list[tuple[str, str]]] = {}
    for loc, line in units:
        bkey = _page_key(loc) if re.match(r"^P\d+:", loc) else ("__all__" if len(units) <= 40 else loc)
        blocks.setdefault(bkey, []).append((loc, line))

    for loc, line in units:
        for pat, fix in ZH_TYPOS_GRAMMAR:
            for m in re.finditer(pat, line):
                add(loc, "TYPO_GRAMMAR_ZH", m.group(0), fix, line)

        for m in re.finditer(r"Ui\s*\(\s*kV\s*\)", line):
            add(loc, "TECH_HARD_ERROR", m.group(0), "Ui(V)（额定绝缘电压单位应为 V，与 Uimp(kV) 互倒）", line)
        for m in re.finditer(r"Uimp\s*\(\s*V\s*\)", line):
            add(loc, "TECH_HARD_ERROR", m.group(0), "Uimp(kV)（额定冲击耐受电压单位应为 kV，与 Ui(V) 互倒）", line)
        for m in re.finditer(r"直流\s*[（(][^）)]*AC\s*\d+\s*V[^）)]*[）)]", line):
            add(loc, "TECH_HARD_ERROR", m.group(0), "核改直流电压代号（直流括号内误写 AC 电压）", line)
        for m in re.finditer(r"交流\s*[（(][^）)]*DC\s*\d+\s*V[^）)]*[）)]", line):
            add(loc, "TECH_HARD_ERROR", m.group(0), "核改交流电压代号（交流括号内误写 DC 电压）", line)

        m_page = re.match(r"^P(\d+):", loc)
        if m_page:
            cur_p = int(m_page.group(1))
            for m_ref in re.finditer(r"详见\s*P0*(\d+)\b", line):
                if int(m_ref.group(1)) == cur_p:
                    add(loc, "CROSSREF_NUMBERING", m_ref.group(0), f"修正交叉引用页码（第 {cur_p} 页不应自引 P{cur_p:03d}）", line)
        for m in re.finditer(r"\)\s*\)", line):
            if line[:m.end()].count(")") > line[:m.end()].count("("):
                add(loc, "CROSSREF_NUMBERING", m.group(0), "删除多余右括号", line)
        for m in re.finditer(r"填写\s*\)\s*s\b", line):
            add(loc, "CROSSREF_NUMBERING", m.group(0), "删除括号外多余单位 s", line)
        for m in re.finditer(r"\{\{[^}]+\}\}", line):
            add(loc, "UNRESOLVED_SLOT", m.group(0), "补填数据表核实值或改为定性描述", line)

        if mode == "en":
            bl = list(ssot.get("BLACKLIST_COMMON", []))
            if dept in {"acb", "all"}:
                bl.extend(ssot.get("BLACKLIST_ACB", []))
            if dept in {"mccb", "all"}:
                bl.extend(ssot.get("BLACKLIST_MCCB", []))
            for pat, fix in bl:
                for m in re.finditer(pat, line, re.IGNORECASE):
                    add(loc, "EN_SEVERE_ERROR", m.group(0), fix, line)
            comp_rules = list(ssot.get("COMPETITOR_RULES_COMMON", []))
            if dept in {"acb", "all"}:
                comp_rules.extend(ssot.get("COMPETITOR_RULES_ACB", []))
            for c_pat, c_fix in comp_rules:
                for m in re.finditer(c_pat, line):
                    if "(PF)" in m.group(0).upper() and pf_context_re.search(line):
                        continue
                    add(loc, "COMPETITOR_CODE", m.group(0), c_fix, line)

        if run_l2:
            for pat, fix in L2_CASE_NOTATION_RULES:
                for m in re.finditer(pat, line):
                    add(loc, "SYMBOL_CASE_NOTATION", m.group(0), fix, line)

        if run_iec_concept:
            for pat, fix in ssot.get("STD_CONCEPT_ZH", []):
                for m in re.finditer(pat, line):
                    add(loc, "STD_CONCEPT_ERROR", m.group(0), fix, line)
            if mode == "en" and ed5_re is not None:
                for m in ed5_re.finditer(line):
                    window = line[max(0, m.start() - 35):min(len(line), m.end() + 35)]
                    if not any(tag in window for tag in ed5_guards):
                        add(loc, "OBSOLETE_CLAUSE_ED5", m.group(0), "按 IEC 60947-2:2024 第 6 版核改条款号", line)

        if run_iec_statutory:
            for pat, fix in ssot.get("STD_STATUTORY_ZH", []):
                for m in re.finditer(pat, line):
                    add(loc, "STD_STATUTORY_ZH", m.group(0), fix, line)

    for items in blocks.values():
        page_blob = "\n".join(txt for _, txt in items)

        for idx in range(len(items) - 1):
            loc1, t1 = items[idx]
            _, t2 = items[idx + 1]
            pair_txt = t1 + " " + t2
            m_acdc = re.search(r"(直流\s*[（(][^）)]*)\s+(AC\s*\d+\s*V[^）)]*[）)])", pair_txt)
            if re.search(r"直流\s*[（(][^）)]*$", t1) and re.search(r"^\s*AC\s*\d+\s*V[^）)]*[）)]", t2):
                matched_frag = f"{m_acdc.group(1)} {m_acdc.group(2)}" if m_acdc else f"{t1.strip()} {t2.strip()}"
                add(loc1, "TECH_HARD_ERROR", matched_frag, "直流电压括号内误写 AC 电压（应为 DC）", pair_txt)

        for idx, (loc, txt) in enumerate(items):
            if re.search(r"整定电流\s*范围\s*[（(]\s*Ir\s*[）)]", txt):
                fwd_blob = "\n".join(t for _, t in items[idx:min(len(items), idx + 14)])
                if re.search(r"\bIsd\b", fwd_blob) and not re.search(r"\b1\.05\s*Ir\b", fwd_blob):
                    add(loc, "TECH_HARD_ERROR", "整定电流范围 (Ir)", "整定电流范围 (Isd)（短路短延时表头误写为 Ir）", txt)
            elif re.search(r"整定电流", txt) and idx + 1 < len(items) and re.search(r"^\s*范围\s*[（(]\s*Ir\s*[）)]", items[idx + 1][1]):
                fwd_blob = "\n".join(t for _, t in items[idx:min(len(items), idx + 15)])
                if re.search(r"\bIsd\b", fwd_blob) and not re.search(r"\b1\.05\s*Ir\b", fwd_blob):
                    add(loc, "TECH_HARD_ERROR", "整定电流范围 (Ir)", "整定电流范围 (Isd)（短路短延时表头误写为 Ir）", txt)

        for idx, (loc, txt) in enumerate(items):
            m_a = cat_a_re.search(txt)
            if m_a:
                win_lines = []
                if idx > 0 and not cat_b_re.search(items[idx - 1][1]):
                    win_lines.append(items[idx - 1][1])
                win_lines.append(txt)
                for fwd in range(idx + 1, min(len(items), idx + 4)):
                    ntxt = items[fwd][1]
                    if cat_b_re.search(ntxt) or model_hdr_re.search(ntxt):
                        break
                    win_lines.append(ntxt)
                m_st = st_or_icw_re.search("\n".join(win_lines))
                if m_st:
                    add(loc, "TECH_HARD_ERROR", f"{m_a.group(0)} + {m_st.group(0)}", "选择性类别 A 禁止配 Isd/Icw（须改 B 类并声明 Icw）", txt)

            m_fb = type_fb_re.search(txt)
            if m_fb:
                lo, hi = max(0, idx - 2), min(len(items), idx + 3)
                local_blob = "\n".join(t for _, t in items[lo:hi])
                if re.search(r"60947-2", local_blob) and not re.search(r"62423|0664", local_blob):
                    add(loc, "TECH_HARD_ERROR", f"{m_fb.group(0)} + IEC 60947-2", "IEC 60947-2 附录 B 仅覆盖 AC/A/B 型；Type F/B+ 须引 IEC 62423", txt)

        fig_hits: dict[str, list[str]] = {}
        for loc, txt in items:
            s_txt = txt.strip()
            m_fig = fig_caption_re.match(s_txt)
            if m_fig:
                norm = re.sub(r"\s+", "", m_fig.group(1))
                fig_hits.setdefault(norm, []).append(loc)
            elif re.match(r"^图\s*\d+(?:-\d+)?\s+(?:DW|NX|NA)", s_txt):
                m_head = re.match(r"^(图\s*\d+(?:-\d+)?)", s_txt)
                if m_head:
                    norm = re.sub(r"\s+", "", m_head.group(1))
                    fig_hits.setdefault(norm, []).append(loc)
        for norm, locs in fig_hits.items():
            if len(locs) >= 2:
                add(locs[1], "CROSSREF_NUMBERING", norm, f"同页图号重复（{norm} 出现 {len(locs)} 次），核对顺延编号", page_blob[:120])

        for desc, variants in SAME_PAGE_CONFLICT_GROUPS:
            present: list[tuple[str, str]] = []
            for pat, label in variants:
                for loc, txt in items:
                    if re.search(pat, txt):
                        present.append((label, loc))
                        break
            if len(present) >= 2:
                labels = " / ".join(p[0] for p in present)
                add(present[1][1], "SAME_PAGE_INCONSISTENCY", labels, f"{desc}（同页出现 {labels}）", page_blob[:120])

    if run_l2:
        for desc, variants, fix in CROSS_PAGE_SYNONYM_GROUPS:
            found_variants: list[tuple[str, list[str]]] = []
            for pat, label in variants:
                locs_for_var: list[str] = []
                for loc, txt in units:
                    if re.search(pat, txt):
                        locs_for_var.append(loc)
                if locs_for_var:
                    found_variants.append((label, locs_for_var))
            if len(found_variants) >= 2:
                summary_parts = [f"{lbl}({len(ls)}处)" for lbl, ls in found_variants]
                first_loc = found_variants[0][1][0]
                add(first_loc, "CROSS_PAGE_TERM_DRIFT", " vs ".join(summary_parts), f"{desc}：{fix}", " | ".join(summary_parts))

    return findings


def strip_internal_fields(findings: list[dict]) -> list[dict]:
    return [{k: v for k, v in f.items() if not k.startswith("_")} for f in findings]


def build_chunks(units: list[tuple[str, str]], chunk_size: int) -> list[list[tuple[str, str]]]:
    if chunk_size <= 0 or not units:
        return [units] if units else []
    return [units[i:i + chunk_size] for i in range(0, len(units), chunk_size)]


def build_summary(loaded: dict, batch_size: int = 20) -> dict:
    batches: list[str] = []
    if loaded.get("format") == "pdf" and loaded.get("total", 0) > 0:
        total_p = int(loaded["total"])
        for start in range(1, total_p + 1, batch_size):
            batches.append(f"{start}-{min(start + batch_size - 1, total_p)}")
    return {
        "source": loaded.get("source", ""),
        "format": loaded.get("format", ""),
        "office_engine": loaded.get("office_engine", ""),
        "total_units": loaded.get("total", 0),
        "scanned_units": loaded.get("scanned", 0),
        "text_unit_count": len(loaded.get("units", [])),
        "low_text_pages": loaded.get("low_text_pages", []),
        "uncached_formula_cells": loaded.get("uncached_formula_cells", []),
        "recommended_page_batches": batches,
    }


def format_report_md(loaded: dict, findings: list[dict], profile: str, with_iec: bool) -> str:
    high = [f for f in findings if f["severity"] == "HIGH"]
    med = [f for f in findings if f["severity"] != "HIGH"]
    mode_tag = f"{profile}{'+IEC' if with_iec else ''}"
    lines = [
        f"### Coverage Ledger (`{mode_tag}`)",
        "| Total units | Scanned | Visual Pages (<50 chars) | HIGH hits | MEDIUM hits |",
        "| :--- | :--- | :--- | :--- | :--- |",
        f"| {loaded['total']} | {loaded['scanned']} | {loaded['low_text_pages']} | {len(high)} | {len(med)} |",
        "",
        "### HIGH-Severity Findings (Verbatim, up to 60 rows)",
        "| Location | Category | Quoted Match | Suggested Fix |",
        "| :--- | :--- | :--- | :--- |",
    ]
    if high:
        for f in high[:60]:
            m_clean = f["match"].replace("|", "\\|")
            fix_clean = f["fix"].replace("|", "\\|")
            lines.append(f"| `{f['location']}` | `{f['category']}` | `{m_clean}` | {fix_clean} |")
        if len(high) > 60:
            lines.append(f"\n> Truncated HIGH rows: showing 60 of {len(high)} findings; inspect with `--chunk-size` / `--chunk-index`.")
    else:
        lines.append("| — | — | None | — |")

    lines.extend([
        "",
        "### MEDIUM-Severity Findings (Aggregated by Pattern)",
        "| Category | Match | Fix | Count | Sample Locations (max 5) |",
        "| :--- | :--- | :--- | :--- | :--- |",
    ])
    if med:
        grouped: dict[tuple[str, str, str], list[str]] = {}
        for f in med:
            grouped.setdefault((f["category"], f["match"], f["fix"]), []).append(f["location"])
        ordered = sorted(grouped.items(), key=lambda kv: (-len(kv[1]), kv[0][0], kv[0][1]))
        for (cat, match, fix), locs in ordered:
            sample = ", ".join(dict.fromkeys(locs[:5]))
            m_clean = match.replace("|", "\\|")
            fix_clean = fix.replace("|", "\\|")
            lines.append(f"| `{cat}` | `{m_clean}` | {fix_clean} | {len(locs)} | `{sample}` |")
    else:
        lines.append("| — | None | — | 0 | — |")
    return "\n".join(lines)


CLAUSE_PAREN_RE = re.compile(r"\s*\((?:IEC|GB/T|Cl\.|Annex|ISO/IEC)[^)]*\)\s*$", re.IGNORECASE)


def _strip_clause_notes(text: str) -> str:
    cur = text.strip()
    while True:
        nxt = CLAUSE_PAREN_RE.sub("", cur).strip()
        if nxt == cur:
            return cur
        cur = nxt


def clean_pdf_replacement(match: str, category: str, fix: str) -> str:
    if category == "UNRESOLVED_SLOT":
        return "补填数据表核实值"
    if category == "COMPETITOR_CODE":
        if "contact" in match.lower():
            m_code = re.match(r"([A-Z]{2,4})\b", fix)
            if m_code:
                return f"{m_code.group(1)} contact"
        m_code = re.match(r"\(?([A-Z]{2,4})\)?", fix)
        if m_code:
            code = m_code.group(1)
            return f"({code})" if match.startswith("(") and match.endswith(")") else code
        return fix
    if category == "EN_SEVERE_ERROR" and fix == "plain integer operating cycles":
        return "<整数> operating cycles"
    return _strip_clause_notes(fix)


def _coalesce_high_compounds(findings: list[dict]) -> list[dict]:
    by_loc: dict[str, list[int]] = {}
    for idx, f in enumerate(findings):
        if f["severity"] == "HIGH":
            by_loc.setdefault(f["location"], []).append(idx)

    absorbed: set[int] = set()
    overrides: dict[int, str] = {}
    for idxs in by_loc.values():
        bl_idxs = [i for i in idxs if findings[i]["category"] == "EN_SEVERE_ERROR"]
        comp_idxs = [i for i in idxs if findings[i]["category"] == "COMPETITOR_CODE"]
        if not bl_idxs or not comp_idxs:
            continue
        for bi in bl_idxs:
            bf = findings[bi]
            m_bl_code = re.search(r"\(([A-Z]{2,4})\)", bf["fix"])
            if not m_bl_code:
                continue
            bl_code = m_bl_code.group(1)
            full_line = bf.get("_full_line") or bf.get("excerpt", "")
            for ci in comp_idxs:
                if ci in absorbed:
                    continue
                cf = findings[ci]
                m_c_code = re.match(r"\(?([A-Z]{2,4})\)?", cf["fix"])
                if not m_c_code or m_c_code.group(1) != bl_code:
                    continue
                cm = cf["match"]
                pat = rf"{re.escape(bf['match'])}\s*{re.escape(cm)}" if (cm.startswith("(") and cm.endswith(")")) else rf"{re.escape(bf['match'])}\s*\(\s*{re.escape(cm)}\s*\)"
                m_compound = re.search(pat, full_line)
                if m_compound:
                    overrides[bi] = m_compound.group(0)
                    absorbed.add(ci)
                    break

    out: list[dict] = []
    for idx, f in enumerate(findings):
        if idx in absorbed:
            continue
        if idx in overrides:
            nf = dict(f)
            nf["match"] = overrides[idx]
            out.append(nf)
        else:
            out.append(f)
    return out


def build_annotate_payload(findings: list[dict], author: str = "CHINT Catalog Edit", min_severity: str = "high") -> dict:
    findings = _coalesce_high_compounds(findings)
    high_seen: set[tuple[int, str, str]] = set()
    med_groups: dict[tuple[int, str, str], list[dict]] = {}
    items: list[dict] = []
    skipped_non_pdf = 0

    for f in findings:
        m = re.match(r"^P(\d+):", f["location"])
        if not m:
            if f["severity"] == "HIGH" or min_severity == "all":
                skipped_non_pdf += 1
            continue
        pno = int(m.group(1))
        if f["severity"] == "HIGH":
            search_str = f["match"].split(" + ")[0] if f["category"] == "TECH_HARD_ERROR" else f["match"]
            key = (pno, search_str.lower(), f["fix"])
            if key in high_seen:
                continue
            high_seen.add(key)
            rep = clean_pdf_replacement(search_str, f["category"], f["fix"])
            items.append({
                "page": pno,
                "search": search_str,
                "match_mode": "all",
                "comment": f"替换为：{rep}",
                "author": author,
            })
        elif min_severity == "all":
            gkey = (pno, f["category"], f["fix"])
            med_groups.setdefault(gkey, []).append(f)

    if skipped_non_pdf:
        print(f"WARNING: skipped {skipped_non_pdf} non-PDF finding(s) lacking 'P{{n}}:' coordinates.", file=sys.stderr)

    for (pno, cat, fix), grp in med_groups.items():
        unique_matches = list(dict.fromkeys(f["match"] for f in grp))
        count = len(grp)
        rep = clean_pdf_replacement(unique_matches[0], cat, fix)
        comment = f"替换为：{rep}" if count == 1 else f"替换为：{rep}（本页共 {count} 处）"
        entry: dict = {"page": pno, "match_mode": "merged", "comment": comment, "author": author}
        if len(unique_matches) == 1:
            entry["search"] = unique_matches[0]
        else:
            entry["searches"] = unique_matches
        items.append(entry)

    items.sort(key=lambda x: (x["page"], 0 if x["match_mode"] == "all" else 1))
    return {"schema": "chint-office-annotate/v1", "annotations": items}


def emit_annotate_payload(findings: list[dict], out_target: str | Path, author: str = "CHINT Catalog Edit", min_severity: str = "high", extra_items: list[dict] | None = None) -> int:
    payload = build_annotate_payload(findings, author=author, min_severity=min_severity)
    if extra_items:
        payload["annotations"].extend(extra_items)
        payload["annotations"].sort(key=lambda x: (int(x["page"]), 0 if str(x.get("match_mode", "all")) == "all" else 1))
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    if str(out_target) == "-":
        sys.stdout.write(text + "\n")
        sys.stdout.flush()
    else:
        p = Path(out_target)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
    return len(payload["annotations"])


def run_self_test() -> int:
    import tempfile

    # 1. Parity anti-drift check whenever sibling chint-translation is present
    trn_dir = resolve_translation_skill()
    ssot_live, ssot_src, _ = load_translation_ssot(trn_dir)
    if trn_dir is not None:
        assert ssot_src == "sibling:chint-translation"
        for key in ("BLACKLIST_COMMON", "BLACKLIST_ACB", "BLACKLIST_MCCB", "COMPETITOR_RULES_COMMON", "COMPETITOR_RULES_ACB", "STD_CONCEPT_ZH", "STD_STATUTORY_ZH", "ED5_GUARD_TAGS"):
            assert ssot_live[key] == BUILTIN_SSOT_FALLBACK[key], f"SSOT drift detected on {key}!"
        assert ssot_live["ED5_CLAUSE_RE"].pattern == BUILTIN_SSOT_FALLBACK["ED5_CLAUSE_RE"].pattern

    # 2. Pure solo-mode test (office_dir=None, translation_dir=None) on synthetic PDF & DOCX
    fitz = _import_fitz()
    ssot_solo, solo_src, solo_path = load_translation_ssot(None)
    assert solo_src == "builtin-standalone" and solo_path is None

    with tempfile.TemporaryDirectory() as td:
        tdir = Path(td)
        pdf_p = tdir / "solo_sample.pdf"
        doc = fitz.open()
        doc.new_page()  # P1 visual-only (<50 chars)
        p2 = doc.new_page()
        p2.insert_text((50, 60), "Ui(kV) 1000, Uimp(V) 8, 50KA, 2000m.")
        p2.insert_text((50, 90), "Closed electromagnet (XF) and Shunt Trip (MX).")
        doc.save(str(pdf_p))
        doc.close()

        loaded_pdf = load_units(str(pdf_p), office_dir=None)
        assert loaded_pdf["office_engine"] == "builtin-standalone"
        assert loaded_pdf["low_text_pages"] == [1], loaded_pdf
        res_solo_en = scan_units(loaded_pdf["units"], profile="L1", mode="en", dept="acb", ssot=ssot_solo)
        matches_en = {f["match"] for f in res_solo_en}
        assert {"Ui(kV)", "Uimp(V)", "Closed electromagnet", "Shunt Trip", "XF", "MX"} <= matches_en, matches_en
        assert not any(m in matches_en for m in ("50KA", "2000m"))

        # Built-in non-destructive PDF annotation writer in solo mode
        ann_payload = build_annotate_payload(res_solo_en)
        out_pdf = tdir / "solo_sample_annotated.pdf"
        ann_sum = write_annotated_pdf(pdf_p, ann_payload["annotations"], out_pdf, office_dir=None)
        assert ann_sum["office_engine"] == "builtin-standalone" and ann_sum["matched_items"] >= 2, ann_sum
        with fitz.open(str(pdf_p)) as sdoc, fitz.open(str(out_pdf)) as ddoc:
            assert len(list(sdoc[1].annots())) == 0, "Source PDF must remain untouched!"
            assert len(list(ddoc[1].annots())) >= 2, "Output PDF missing highlight annotations!"

        # Built-in DOCX extraction in solo mode
        docx_p = tdir / "solo_sample.docx"
        with zipfile.ZipFile(str(docx_p), "w") as zf:
            zf.writestr("word/document.xml", '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body><w:p><w:r><w:t>海拨不超过2000m，涂润滑酯。</w:t></w:r></w:p></w:body></w:document>')
        loaded_docx = load_units(str(docx_p), office_dir=None)
        assert loaded_docx["office_engine"] == "builtin-standalone"
        res_docx = scan_units(loaded_docx["units"], profile="L1", mode="zh", ssot=ssot_solo)
        assert {"海拨", "润滑酯"} <= {f["match"] for f in res_docx}, res_docx

    # 3. Profile threshold calibration tests (L1 / L2 / L1+IEC / EN no-ortho)
    zh_units = [
        ("P36:L1", "瞬时电流 Ii 可设定范围：1.5In~50KA/65KA/75KA"),
        ("P36:L2", "□UVTZ 失压延时(详见 P036)"),
        ("P36:L3", "万能式断路器、闭合电磁铁、功率损耗、Inm=2000A、海拔不超过2000m、-5℃~+40℃。"),
        ("P44:L1", "额定绝缘电压 Ui(kV) 1000；额定冲击耐受电压 Uimp(V) 8；安装地点：海拨不超过2000m；涂润滑酯。"),
        ("P34:L1", "输入交流(AC220V)或直流(DC110V、"),
        ("P34:L2", "AC220V)电源。"),
        ("P32:L1", "6.10 透明保护罩（仅 NA1-2000X 抽屉式可提供），参见图：透明防护罩。"),
        ("P48:L1", "图 3"),
        ("P48:L2", "图 3"),
        ("P9:L1", "Sb1 分励按钮、其它、部分部份、订做。"),
    ]
    res_l1 = scan_units(zh_units, profile="L1", mode="zh", ssot=ssot_solo)
    for must_have in ("海拨", "润滑酯", "Ui(kV)", "Uimp(V)", "详见 P036", "图3"):
        assert any(must_have in f["match"] for f in res_l1), (must_have, res_l1)
    for must_suppress in ("50KA", "Sb1", "2000m", "℃", "万能式断路器", "闭合电磁铁", "功率损耗", "Inm", "部份", "订做", "其它"):
        assert not any(must_suppress in f["match"] for f in res_l1), (must_suppress, res_l1)

    res_l2 = scan_units(zh_units, profile="L2", mode="zh", ssot=ssot_solo)
    assert any("50KA" in f["match"] for f in res_l2) and any("Sb1" in f["match"] for f in res_l2)
    assert not any("2000m" in f["match"] or "℃" in f["match"] for f in res_l2)

    iec_units = [("P3:L1", "万能式断路器，使用类别 A，闭合电磁铁，结构差异，2000m，-5℃。")]
    res_iec = scan_units(iec_units, profile="L1", mode="zh", with_iec=True, dept="acb", ssot=ssot_solo)
    assert {"STD_CONCEPT_ERROR", "STD_STATUTORY_ZH"} <= {f["category"] for f in res_iec}
    assert not any("2000m" in f["match"] or "℃" in f["match"] for f in res_iec)

    print("SELF-TEST PASS: 6/6 suites passed (anti-drift/solo-PDF-write/solo-DOCX/L1-strict/L2-drift/L1+IEC).")
    return 0


def main() -> int:
    _ensure_utf8_stdio()
    parser = argparse.ArgumentParser(description="Standalone + sibling-aware CHINT catalogue audit & PDF annotation engine")
    parser.add_argument("source", nargs="?", help=".pdf/.docx/.xlsx/.txt, chint-office-extract/v1 JSON, or '-'")
    parser.add_argument("--profile", choices=["L1", "L2", "L3"], default="L1", help="Threshold profile (default: L1 strict errors only)")
    parser.add_argument("--with-iec", action="store_true", help="Overlay substantive GB/T 14048.2 & IEC 60947-2 checks onto L1/L2")
    parser.add_argument("--dept", choices=["acb", "mccb", "all"], default="all", help="Product department scope (default: all)")
    parser.add_argument("--mode", choices=["auto", "zh", "en"], default="auto", help="Language mode (default: auto)")
    parser.add_argument("--pages", help="PDF page range, e.g. 1-20 or 1,3,5")
    parser.add_argument("--summary", action="store_true", help="Print compact document metadata & page batches without auditing")
    parser.add_argument("--office-dir", help="Optional path to sibling chint-office-suite (or /nonexistent to force built-in)")
    parser.add_argument("--translation-dir", help="Optional path to sibling chint-translation (or /nonexistent to force built-in)")
    parser.add_argument("--check-env", action="store_true", help="Check Python, optional pymupdf/openpyxl, and sibling skill availability")
    parser.add_argument("--json", action="store_true", help="Output structured JSON")
    parser.add_argument("--report-md", action="store_true", help="Output deduplicated Markdown report")
    parser.add_argument("--emit-annotate", help="Write chint-office-annotate/v1 JSON to '-' or file path")
    parser.add_argument("--write-pdf", help="Write non-destructive annotated copy of this PDF (uses sibling or built-in PyMuPDF)")
    parser.add_argument("--output", help="Output PDF path for --write-pdf (default: <stem>_annotated.pdf)")
    parser.add_argument("--extra-annotations", help="Optional extra chint-office-annotate/v1 JSON file or '-' merged into --write-pdf / --emit-annotate")
    parser.add_argument("--annotate-severity", choices=["high", "all"], default="high", help="Minimum severity for PDF annotations (default: high)")
    parser.add_argument("--author", default="CHINT Catalog Edit", help="Annotation author")
    parser.add_argument("--chunk-size", type=int, default=0, help="Split units into chunks of N non-empty lines")
    parser.add_argument("--chunk-index", type=int, default=0, help="Inspect 1-based chunk K only")
    parser.add_argument("--chunks-info", action="store_true", help="Print chunk manifest with per-chunk hit counts")
    parser.add_argument("--exit-zero", action="store_true", help="Exit 0 even when findings exist")
    parser.add_argument("--self-test", action="store_true", help="Run built-in verification suite")
    args = parser.parse_args()

    try:
        if args.self_test:
            return run_self_test()
        if args.check_env:
            info = check_env(args.office_dir, args.translation_dir)
            print(json.dumps(info, ensure_ascii=False, indent=2))
            return 0 if info["ready"] else 1
        if not args.source:
            parser.error("source is required unless --self-test or --check-env is set")

        off_dir = resolve_office_skill(args.office_dir)
        trn_dir = resolve_translation_skill(args.translation_dir)
        loaded = load_units(args.source, pages_spec=args.pages, office_dir=off_dir)
        if args.summary:
            summary = build_summary(loaded)
            print(json.dumps(summary, ensure_ascii=False, indent=2) if args.json else f"{summary['format']} ({summary['office_engine']}) | total={summary['total_units']} | scanned={summary['scanned_units']} | low_text_pages={summary['low_text_pages']} | batches={summary['recommended_page_batches']}")
            return 0

        units = loaded["units"]
        eff_mode = detect_mode(units) if args.mode == "auto" else args.mode
        ssot, ssot_source, ssot_path = load_translation_ssot(trn_dir)

        if args.chunks_info:
            csize = args.chunk_size if args.chunk_size > 0 else 50
            chunks = build_chunks(units, csize)
            manifest_chunks = []
            for idx, ch in enumerate(chunks, 1):
                cf = scan_units(ch, profile=args.profile, mode=eff_mode, with_iec=args.with_iec, dept=args.dept, ssot=ssot)
                manifest_chunks.append({
                    "index": idx,
                    "start_location": ch[0][0],
                    "end_location": ch[-1][0],
                    "unit_count": len(ch),
                    "high_hits": sum(1 for f in cf if f["severity"] == "HIGH"),
                    "medium_hits": sum(1 for f in cf if f["severity"] != "HIGH"),
                })
            manifest = {
                "source": loaded["source"],
                "profile": args.profile,
                "with_iec": args.with_iec,
                "mode": eff_mode,
                "office_engine": loaded["office_engine"],
                "ssot_source": ssot_source,
                "ssot_path": ssot_path,
                "total_units": len(units),
                "chunk_size": csize,
                "total_chunks": len(chunks),
                "low_text_pages": loaded["low_text_pages"],
                "chunks": manifest_chunks,
            }
            if args.json:
                print(json.dumps(manifest, ensure_ascii=False, indent=2))
            else:
                print(f"Total units: {manifest['total_units']} | Chunks: {manifest['total_chunks']} (size={csize}) | profile={args.profile} | ssot={ssot_source} | office={loaded['office_engine']} | low_text_pages={manifest['low_text_pages']}")
                for c in manifest_chunks:
                    print(f"  Chunk {c['index']}: {c['start_location']}..{c['end_location']} ({c['unit_count']} units) | HIGH={c['high_hits']} MEDIUM={c['medium_hits']}")
            return 0

        active_units = units
        chunk_meta = None
        if args.chunk_index > 0:
            csize = args.chunk_size if args.chunk_size > 0 else 50
            chunks = build_chunks(units, csize)
            if args.chunk_index > len(chunks):
                raise ValueError(f"--chunk-index {args.chunk_index} out of range 1..{len(chunks)}")
            active_units = chunks[args.chunk_index - 1]
            chunk_meta = {"index": args.chunk_index, "total_chunks": len(chunks), "unit_count": len(active_units)}

        findings = scan_units(active_units, profile=args.profile, mode=eff_mode, with_iec=args.with_iec, dept=args.dept, ssot=ssot)

        extra_items: list[dict] = []
        if args.extra_annotations:
            raw_extra = sys.stdin.read() if args.extra_annotations == "-" else Path(args.extra_annotations).read_text(encoding="utf-8")
            extra_obj = json.loads(raw_extra)
            extra_list = extra_obj["annotations"] if isinstance(extra_obj, dict) else extra_obj
            if not isinstance(extra_list, list):
                raise ValueError("--extra-annotations must be a JSON list or an object with 'annotations'.")
            extra_items = extra_list

        if args.write_pdf:
            inp_pdf = Path(args.write_pdf)
            out_pdf = Path(args.output) if args.output else inp_pdf.with_name(f"{inp_pdf.stem}_annotated.pdf")
            payload = build_annotate_payload(findings, author=args.author, min_severity=args.annotate_severity)
            all_items = payload["annotations"] + extra_items
            all_items.sort(key=lambda x: (int(x["page"]), 0 if str(x.get("match_mode", "all")) == "all" else 1))
            summary = write_annotated_pdf(inp_pdf, all_items, out_pdf, default_author=args.author, office_dir=off_dir)
            print(json.dumps(summary, ensure_ascii=False, indent=2))
            return 0

        if args.emit_annotate:
            emit_annotate_payload(findings, args.emit_annotate, author=args.author, min_severity=args.annotate_severity, extra_items=extra_items)
            if args.emit_annotate == "-":
                return 0

        clean_findings = strip_internal_fields(findings)
        report = {
            "source": loaded["source"],
            "format": loaded["format"],
            "office_engine": loaded["office_engine"],
            "profile": args.profile,
            "with_iec": args.with_iec,
            "dept": args.dept,
            "mode": eff_mode,
            "ssot_source": ssot_source,
            "ssot_path": ssot_path,
            "total_units": loaded["total"],
            "scanned_units": loaded["scanned"],
            "low_text_pages": loaded["low_text_pages"],
            "finding_count": len(clean_findings),
            "high_count": sum(1 for f in clean_findings if f["severity"] == "HIGH"),
            "medium_count": sum(1 for f in clean_findings if f["severity"] != "HIGH"),
            "findings": clean_findings,
        }
        if chunk_meta:
            report["chunk"] = chunk_meta
            report["units"] = [{"location": loc, "text": txt} for loc, txt in active_units]

        if args.json:
            print(json.dumps(report, ensure_ascii=False, indent=2))
        elif args.report_md:
            print(format_report_md(loaded, clean_findings, args.profile, args.with_iec))
        else:
            print(f"[{args.profile}{'+IEC' if args.with_iec else ''}] Scanned {report['scanned_units']}/{report['total_units']} units | office={report['office_engine']} | ssot={ssot_source} | low_text_pages={report['low_text_pages']} | findings={report['finding_count']} (HIGH={report['high_count']}, MEDIUM={report['medium_count']})")
            if chunk_meta:
                print(f"--- Chunk {chunk_meta['index']}/{chunk_meta['total_chunks']} ({chunk_meta['unit_count']} units) ---")
                for loc, txt in active_units:
                    print(f"[{loc}] {txt}")
                print("--- Findings ---")
            for f in clean_findings:
                print(f"[{f['location']}] ({f['severity']}/{f['category']}) '{f['match']}' -> {f['fix']}")
        return 0 if args.exit_zero else (1 if clean_findings else 0)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
