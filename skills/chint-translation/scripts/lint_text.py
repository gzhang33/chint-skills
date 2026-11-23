#!/usr/bin/env python3
"""Pure-stdlib IEC 60947-2:2024 & GB/T 14048.2-2020 text/extract-JSON linter for chint-translation."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

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


def load_units(source: str) -> dict:
    raw = sys.stdin.read() if source == "-" else Path(source).read_text(encoding="utf-8", errors="replace")
    stripped = raw.lstrip()
    if stripped.startswith("{"):
        try:
            obj = json.loads(raw)
            if isinstance(obj, dict) and obj.get("schema") == "chint-office-extract/v1":
                units = [(str(u["location"]), str(u["text"])) for u in obj.get("units", [])]
                return {"source": obj.get("source", source), "total": obj.get("total_units", len(units)), "scanned": obj.get("scanned_units", len(units)), "low_text_pages": obj.get("low_text_pages", []), "units": units}
        except json.JSONDecodeError:
            pass
    lines = raw.splitlines()
    units = [(f"Line {i}", l) for i, l in enumerate(lines, 1) if l.strip()]
    return {"source": source, "total": len(lines), "scanned": len(lines), "low_text_pages": [], "units": units}


def scan_units(units: list[tuple[str, str]], dept: str, mode: str) -> list[dict]:
    findings: list[dict] = []

    def add(loc: str, cat: str, matched: str, fix: str, line: str):
        findings.append({"location": loc, "category": cat, "match": matched, "fix": fix, "excerpt": line[:120]})

    ed5_re = re.compile(r"(?:Cl\.|Clause)\s*(?:2\.1(?:\.\d+)?|4\.3\.[1-6](?:\.\d+)?|7\.2\.[1-8](?:\.\d+)?|8\.3\.[1-9](?:\.\d+)?)\b", re.IGNORECASE)
    comp_re = re.compile(r"\b(?:MX|MN|XF|SDE|PF|MCH|KLC)\b|\(OF\)")
    unit_gap_re = re.compile(r"(?<![A-Za-z0-9\-/_])\d+(?:\.\d+)?(?:kA|mA|kV|mV|ms|Hz|kHz|mm²|mm|kW|VA|kVA|N·m|°C|A|V|s)\b(?![A-Za-z0-9\-])")
    zh_bad = [
        (r"相间对中性线", "相-中性线交流电压下的额定单极极限短路分断能力 (IEC 60947-2:2024 Cl. 5.3.6.2.3)"),
        (r"(?<!单)极极限", "单极极限短路分断能力"),
        (r"隔离开关断路器", "隔离开关 (IEC 60947-3 / GB/T 14048.3)"),
        (r"使用类别\s*[AB]", "选择性类别 A / B (GB/T 14048.2—2020 Cl. 3.1 / 4.4)"),
        (r"抽出式断路器", "抽屉式断路器 (GB/T 14048.2—2020 Cl. 2.5 / 3.7)"),
        (r"功率损耗", "功耗 (GB/T 14048.2—2020 附录 G)"),
        (r"结构差异", "结构段 (GB/T 14048.2—2020 Cl. 2.1.2 / 7.1.6)"),
        (r"合闸涌流脱扣器", "接通电流脱扣器 (GB/T 14048.2—2020 Cl. 2.10)"),
    ]

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
            for m in ed5_re.finditer(line):
                window = line[max(0, m.start() - 25):min(len(line), m.end() + 25)]
                if "60947-1" not in window and "60947-3" not in window:
                    add(loc, "OBSOLETE_CLAUSE_ED5", m.group(0), "Use IEC 60947-2:2024 Ed. 6.0 clause numbers", line)
        else:
            for pat, fix in zh_bad:
                for m in re.finditer(pat, line):
                    add(loc, "GB_STATUTORY_ZH", m.group(0), fix, line)

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
    import tempfile

    mccb_dirty = [("P1:L1", "NXM-250S Molded Case Circuit Breaker (IEC 60947-2, Cl. 4.3.5). Frame size: 250A. Icu: 36kA at 415V. Ics: 100% Icu. Mechanical durability: 20000 times. Short-time pickup Isd.")]
    mccb_hits = {f["category"] for f in scan_units(mccb_dirty, "mccb", "en")}
    assert {"ORTHOGRAPHY_US_HYPHEN", "OBSOLETE_CLAUSE_ED5", "UNIT_SPACING_PUNCT", "BLACKLIST_CHINGLISH_UL"} <= mccb_hits, mccb_hits

    acb_dirty = [("P2:L1", "Closed electromagnet (XF), Shunt Trip (MX), Earch current transformer, Closing Preparation Contact (PF), hole opener on drawer seat.")]
    acb_hits = {f["category"] for f in scan_units(acb_dirty, "acb", "en")}
    assert {"BLACKLIST_CHINGLISH_UL", "COMPETITOR_CODE"} <= acb_hits, acb_hits

    zh_dirty = [("P3:L1", "抽出式断路器（使用类别 A）在 400V 下测量功率损耗与结构差异，含合闸涌流脱扣器。")]
    zh_hits = {f["category"] for f in scan_units(zh_dirty, "acb", "zh")}
    assert {"GB_STATUTORY_ZH", "UNIT_SPACING_PUNCT"} <= zh_hits, zh_hits

    clean_en = [("P4:L1", "Moulded-case circuit-breaker (MCCB) 250 A, 415 V AC, Icu 36 kA rms, Icm 75.6 kA peak, utilization category AC-22, 20,000 operating cycles per Cl. 8.2.4.2.")]
    assert len(scan_units(clean_en, "all", "en")) == 0

    clean_zh = [("P5:L1", "GB/T 14048.2—2020 Cl. 2.5 抽屉式断路器、Cl. 2.10 接通电流脱扣器、Cl. 4.3.5、Cl. 7.2.4.2 操作性能能力及附录 G 功耗；电压 400 V，温度 -5 °C 至 +40 °C。")]
    assert len(scan_units(clean_zh, "all", "zh")) == 0

    fp_guard = [("P6:L1", "TABLE OF CONTENTS: NXM-250S 3P 4P AC-22 IP40 CD-1 2A Cl. 7.2.1 per IEC 60947-1.")]
    assert len(scan_units(fp_guard, "all", "en")) == 0

    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as tf:
        json.dump({"schema": "chint-office-extract/v1", "source": "x.pdf", "total_units": 3, "scanned_units": 3, "low_text_pages": [2], "units": [{"location": "P1:L1", "text": "Frame size: 250A"}]}, tf)
        tpath = Path(tf.name)
    try:
        loaded = load_units(str(tpath))
        assert loaded["low_text_pages"] == [2] and len(scan_units(loaded["units"], "mccb", "en")) == 1
    finally:
        tpath.unlink(missing_ok=True)

    print("SELF-TEST PASS: 7/7 suites passed (EN MCCB/ACB, ZH GB/T, clean EN/ZH 0-hit, FP-guard, extract JSON pipe).")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Pure-stdlib text linter for chint-translation")
    parser.add_argument("source", nargs="?", help="Text file, chint-office-extract/v1 JSON, or '-' for stdin")
    parser.add_argument("--dept", choices=["acb", "mccb", "all"], default="all")
    parser.add_argument("--mode", choices=["en", "zh"], default="en")
    parser.add_argument("--json", action="store_true", help="Output structured JSON")
    parser.add_argument("--self-test", action="store_true", help="Run built-in verification suite")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()
    if not args.source:
        parser.error("source is required unless --self-test is set")

    loaded = load_units(args.source)
    findings = scan_units(loaded["units"], args.dept, args.mode)
    report = {
        "source": loaded["source"],
        "dept": args.dept,
        "mode": args.mode,
        "total_units": loaded["total"],
        "scanned_units": loaded["scanned"],
        "low_text_pages": loaded["low_text_pages"],
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
