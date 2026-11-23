#!/usr/bin/env python3
"""Deterministic IEC 60947-2:2024 catalogue & translation scanner for chint-translation."""
from __future__ import annotations

import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

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


def extract_units(source: str, pages_filter: set[int] | None) -> dict:
    """Return dict with units [(loc, text)], total_units, low_text_pages."""
    if source == "-":
        lines = sys.stdin.read().splitlines()
        return {"units": [(f"Line {i}", l) for i, l in enumerate(lines, 1)], "total": len(lines), "scanned": len(lines), "low_text_pages": []}

    p = Path(source)
    if not p.exists():
        raise FileNotFoundError(f"Input not found: {source}")
    ext = p.suffix.lower()

    if ext == ".pdf":
        import fitz
        doc = fitz.open(str(p))
        total = len(doc)
        units, low_pages, scanned = [], [], 0
        for idx, page in enumerate(doc, 1):
            if pages_filter and idx not in pages_filter:
                continue
            scanned += 1
            txt = page.get_text("text")
            if len(re.sub(r"\s+", "", txt)) < LOW_TEXT_THRESHOLD:
                low_pages.append(idx)
            for lno, line in enumerate(txt.splitlines(), 1):
                if line.strip():
                    units.append((f"P{idx}:L{lno}", line))
        return {"units": units, "total": total, "scanned": scanned, "low_text_pages": low_pages}

    if ext == ".docx":
        units = []
        with zipfile.ZipFile(str(p)) as zf:
            xml_names = [n for n in zf.namelist() if re.match(r"word/(document|header\d+|footer\d+)\.xml$", n)]
            for name in sorted(xml_names):
                root = ET.fromstring(zf.read(name))
                for p_idx, para in enumerate(root.iter("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p"), 1):
                    txt = "".join(t.text or "" for t in para.iter("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t"))
                    if txt.strip():
                        units.append((f"{Path(name).stem}:P{p_idx}", txt))
        return {"units": units, "total": len(units), "scanned": len(units), "low_text_pages": []}

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
                        units.append((f"{sname}!{col}{r_idx}", str(val)))
        return {"units": units, "total": len(wb.sheetnames), "scanned": len(wb.sheetnames), "low_text_pages": []}

    lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
    return {"units": [(f"Line {i}", l) for i, l in enumerate(lines, 1)], "total": len(lines), "scanned": len(lines), "low_text_pages": []}


ORTHO_RULES = [
    (r"\bmolded\b", "moulded (IEC UK spelling)"),
    (r"\bcolors?\b", "colour(s) (IEC UK spelling)"),
    (r"\baluminum\b", "aluminium (IEC UK spelling)"),
    (r"\bcatalogs?\b", "catalogue(s) (IEC UK spelling)"),
    (r"\bcircuit breakers?\b", "circuit-breaker(s) (Cl. 3.1 hyphenated)"),
    (r"\blockout\b", "lock-out (Cl. 3.10 hyphenated)"),
    (r"\bbackup\b", "back-up (Annex A hyphenated)"),
    (r"\bpickup\b", "pick-up (Cl. 3.17 hyphenated)"),
    (r"\bunder-voltage\b", "undervoltage (unhyphenated per IEC 60947-2)"),
    (r"\benergis\w*\b", "energiz* (ISO/IEC Oxford -ize)"),
    (r"\butilisation\b", "utilization (Annex L.4.1 ISO/IEC -ize)"),
    (r"\bearth-fault\b", "ground-fault (G-stage) / earth fault (Annex B)"),
    (r"\bdurability\b", "operational performance / operating cycles / endurance (Cl. 8.2.4.2)"),
    (r"\bdiscrimination\b", "selectivity (Annex A / Cl. 5.4)"),
]

BLACKLIST_COMMON = [
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
    (r"(?<![A-Za-z])\d[\d,]*\s+times\b", "operating cycles"),
]

BLACKLIST_ACB = [
    (r"\bclosed electromagnet\b", "Closing release (CEM)"),
    (r"\bclose electromagnet\b", "Closing release (CEM)"),
    (r"\bclosing electromagnet\b", "Closing release (CEM)"),
    (r"\bearch current transformer\b", "Earth current transformer (ECT)"),
    (r"\binterphased\b", "interphase barrier (DD / FD)"),
    (r"\binter phased\b", "interphase barrier (DD / FD)"),
    (r"\bphase space plate\b", "interphase barrier (DD / FD)"),
    (r"\bunder voltage delay release-zero\b", "Loss-of-voltage time-delay release (UVTZ)"),
    (r"\bclosing preparation contact\b", "Ready-to-close contact (SPC)"),
    (r"\bdrawer\s+(?:type|box|seat)\b", "Withdrawable / Withdrawable cradle"),
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
]

BLACKLIST_MCCB = [
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
]


def scan_units(units: list[tuple[str, str]], dept: str, mode: str) -> list[dict]:
    findings: list[dict] = []

    def add(loc: str, cat: str, matched: str, fix: str, line: str):
        findings.append({"location": loc, "category": cat, "match": matched, "fix": fix, "excerpt": line[:120]})

    ed5_re = re.compile(r"(?:Cl\.|Clause)\s*(?:2\.1(?:\.\d+)?|4\.3\.[1-6](?:\.\d+)?|7\.2\.[1-8](?:\.\d+)?|8\.3\.[1-9](?:\.\d+)?)\b", re.IGNORECASE)
    comp_re = re.compile(r"\b(?:MX|MN|XF|SDE|PF|MCH|KLC)\b|\(OF\)")
    unit_gap_re = re.compile(r"(?<![A-Za-z0-9\-/_])\d+(?:\.\d+)?(?:kA|mA|kV|mV|ms|Hz|kHz|mm²|mm|kW|VA|kVA|N·m|°C|A|V|s)\b(?![A-Za-z0-9\-])")
    zh_bad = [(r"相间对中性线", "相-中性线交流电压下的额定单极极限短路分断能力 (Cl. 5.3.6.2.3)"), (r"(?<!单)极极限", "单极极限短路分断能力"), (r"隔离开关断路器", "隔离开关（开关-隔离器）(IEC 60947-3)"), (r"使用类别\s*[AB]", "选择性类别 A / B (Cl. 4.1)")]

    for loc, line in units:
        if mode == "en":
            for pat, fix in ORTHO_RULES:
                for m in re.finditer(pat, line, re.IGNORECASE):
                    add(loc, "ORTHOGRAPHY_US_HYPHEN", m.group(0), fix, line)
            bl = list(BLACKLIST_COMMON)
            if dept in {"acb", "all"}:
                bl.extend(BLACKLIST_ACB)
            if dept in {"mccb", "all"}:
                bl.extend(BLACKLIST_MCCB)
            for pat, fix in bl:
                for m in re.finditer(pat, line, re.IGNORECASE):
                    add(loc, "BLACKLIST_CHINGLISH_UL", m.group(0), fix, line)
            if dept in {"acb", "all"}:
                for m in comp_re.finditer(line):
                    add(loc, "COMPETITOR_CODE", m.group(0), "CHINT code (SHT/UVT/CEM/AX/AL/SPC/MOD/KL)", line)
            if re.search(r"[A-Za-z]", line):
                for m in re.finditer(r"[；：（），。～]", line):
                    add(loc, "UNIT_SPACING_PUNCT", m.group(0), "Use half-width ASCII punctuation in English prose", line)
            for m in re.finditer(r"100\s*%\s*Icu\b", line):
                add(loc, "UNIT_SPACING_PUNCT", m.group(0), "100% of Icu (explicit model & Ue scope required)", line)
            for m in re.finditer(r"\b(?:Icu1?|Ics|Icw)\b(?:(?!(?:Icm|Icu1?|Ics|Icw)\b|[,;\n]).){0,25}?\b\d+(?:\.\d+)?\s*kA\b(?!\s*rms)", line):
                add(loc, "UNIT_SPACING_PUNCT", m.group(0), "Qualify AC breaking/withstand kA with 'kA rms'", line)
            for m in re.finditer(r"\bIcm\b(?:(?!(?:Icm|Icu1?|Ics|Icw)\b|[,;\n]).){0,25}?\b\d+(?:\.\d+)?\s*kA\b(?!\s*peak)", line):
                add(loc, "UNIT_SPACING_PUNCT", m.group(0), "Qualify making capacity kA with 'kA peak'", line)
        else:
            for pat, fix in zh_bad:
                for m in re.finditer(pat, line):
                    add(loc, "UNIT_SPACING_PUNCT", m.group(0), fix, line)

        for m in ed5_re.finditer(line):
            prefix = line[max(0, m.start() - 25):m.start()]
            if "60947-1" not in prefix and "60947-3" not in prefix:
                add(loc, "OBSOLETE_CLAUSE_ED5", m.group(0), "Use IEC 60947-2:2024 Ed. 6.0 clause numbers", line)
        for m in unit_gap_re.finditer(line):
            tok = m.group(0)
            if tok in {"2A", "3A"} and ("CD-1" in line or "控制器" in line or "型" in line or line.strip() in {"2A", "3A"}):
                continue
            add(loc, "UNIT_SPACING_PUNCT", tok, "Insert single half-width space between number and unit", line)
        if "℃" in line:
            add(loc, "UNIT_SPACING_PUNCT", "℃", "Replace full-width '℃' with ' °C'", line)
        for m in re.finditer(r"\{\{[^}]+\}\}", line):
            add(loc, "UNIT_SPACING_PUNCT", m.group(0), "Resolve value slot from datasheet or rewrite qualitatively", line)
    return findings


def run_self_test() -> int:
    mccb_dirty = [
        ("P1:L1", "NXM-250S Molded Case Circuit Breaker (IEC 60947-2, Cl. 4.3.5). Frame size: 250A."),
        ("P1:L2", "Ui: 800V. Uimp: 8kV. Icu: 36kA at 415V. Ics: 100% Icu."),
        ("P1:L3", "Mechanical durability: 20000 times. Short-time pickup Isd."),
        ("P1:L4", "This circuit breaker fits 250 A feed; ambient -5℃ to +40℃."),
    ]
    mccb_hits = {f["category"] for f in scan_units(mccb_dirty, "mccb", "en")}
    assert {"ORTHOGRAPHY_US_HYPHEN", "OBSOLETE_CLAUSE_ED5", "UNIT_SPACING_PUNCT", "BLACKLIST_CHINGLISH_UL"} <= mccb_hits, mccb_hits

    acb_dirty = [
        ("P2:L1", "Closed electromagnet (XF) and Shunt Trip (MX) on drawer seat."),
        ("P2:L2", "Earch current transformer with Closing Preparation Contact (PF) and hole opener."),
    ]
    acb_hits = {f["category"] for f in scan_units(acb_dirty, "acb", "en")}
    assert {"BLACKLIST_CHINGLISH_UL", "COMPETITOR_CODE"} <= acb_hits, acb_hits

    clean_iec = [
        ("P3:L1", "Air circuit-breaker (ACB) with Closing release (CEM) and Shunt release (SHT)."),
        ("P3:L2", "Moulded-case circuit-breaker (MCCB) rated 250 A, 415 V AC, Icu 36 kA rms, Icm 75.6 kA peak."),
        ("P3:L3", "Category B selectivity limit current Is, back-up protection, utilization category AC-22 per Cl. 8.2.8."),
        ("P3:L4", "Pulse-energization duty t1 >= 200 ms; ambient -5 °C to +40 °C; 20,000 operating cycles per Table 7."),
    ]
    clean_hits = scan_units(clean_iec, "all", "en")
    assert len(clean_hits) == 0, f"Unexpected hits on clean IEC prose: {clean_hits}"

    fp_guard = [("P4:L1", "TABLE OF CONTENTS: NXM-250S 3P 4P AC-22 IP40 Is per IEC 60947-1 Cl. 7.2.1 and Cl. 8.2.4.2.")]
    fp_hits = scan_units(fp_guard, "all", "en")
    assert len(fp_hits) == 0, f"False-positive guard failed: {fp_hits}"

    print("SELF-TEST PASS: 4/4 suites passed (MCCB dirty, ACB dirty, clean IEC 0-hit, FP-guard 0-hit).")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Deterministic IEC 60947-2:2024 catalogue scanner")
    parser.add_argument("source", nargs="?", help="File path (.pdf/.docx/.xlsx/.md/.txt) or '-' for stdin")
    parser.add_argument("--dept", choices=["acb", "mccb", "all"], default="all")
    parser.add_argument("--mode", choices=["en", "zh"], default="en")
    parser.add_argument("--pages", help="PDF page range e.g. 1-20 or 1,3,5")
    parser.add_argument("--json", action="store_true", help="Output structured JSON")
    parser.add_argument("--self-test", action="store_true", help="Run built-in verification suite")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()
    if not args.source:
        parser.error("source is required unless --self-test is set")

    extracted = extract_units(args.source, parse_page_spec(args.pages))
    findings = scan_units(extracted["units"], args.dept, args.mode)
    report = {
        "source": args.source,
        "dept": args.dept,
        "mode": args.mode,
        "total_units": extracted["total"],
        "scanned_units": extracted["scanned"],
        "low_text_pages": extracted["low_text_pages"],
        "finding_count": len(findings),
        "findings": findings,
    }
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"Scanned {report['scanned_units']}/{report['total_units']} units | low_text_pages={report['low_text_pages']} | findings={report['finding_count']}")
        for f in findings:
            print(f"[{f['location']}] ({f['category']}) '{f['match']}' -> {f['fix']}")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
