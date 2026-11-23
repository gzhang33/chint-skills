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


HIGH_CATS = {
    "BLACKLIST_CHINGLISH_UL",
    "COMPETITOR_CODE",
    "TECH_CONTRADICTION",
    "OBSOLETE_CLAUSE_ED5",
    "GB_STATUTORY_ZH",
}


def _severity(cat: str) -> str:
    return "HIGH" if cat in HIGH_CATS else "MEDIUM"


def scan_units(units: list[tuple[str, str]], dept: str, mode: str) -> list[dict]:
    findings: list[dict] = []

    def add(loc: str, cat: str, matched: str, fix: str, line: str):
        findings.append({
            "location": loc,
            "severity": _severity(cat),
            "category": cat,
            "match": matched,
            "fix": fix,
            "excerpt": line[:120],
        })

    ed5_re = re.compile(r"(?:Cl\.|Clause)\s*(?:2\.1(?:\.\d+)?|4\.3\.[1-6](?:\.\d+)?|7\.2\.[1-8](?:\.\d+)?|8\.3\.[1-9](?:\.\d+)?)\b", re.IGNORECASE)
    comp_re = re.compile(r"\b(?:MX|MN|XF|SDE|PF|MCH|KLC)\b|\(OF\)")
    unit_gap_re = re.compile(r"(?<![A-Za-z0-9\-/_])\d+(?:\.\d+)?(?:kA|mA|kV|mV|ms|Hz|kHz|mm²|mm|kW|VA|kVA|N·m|°C|A|V|s)\b(?![A-Za-z0-9\-])")
    cat_a_re = re.compile(r"(?:Selectivity\s+category\s*[:：]?\s*A\b|选择性类别\s*[:：]?\s*A\b)(?!\s*[/、,])", re.IGNORECASE)
    st_or_icw_re = re.compile(r"\b(?:Isd|Icw)\b")
    zh_bad = [
        (r"相间对中性线", "相-中性线交流电压下的额定单极极限短路分断能力 (IEC 60947-2:2024 Cl. 5.3.6.2.3)"),
        (r"(?<!单)极极限", "单极极限短路分断能力"),
        (r"隔离开关断路器", "隔离开关 (IEC 60947-3 / GB/T 14048.3)"),
        (r"使用类别\s*[AB]", "选择性类别 A / B (GB/T 14048.2—2020 Cl. 3.1 / 4.4)"),
        (r"抽出式断路器", "抽屉式断路器 (GB/T 14048.2—2020 Cl. 2.5 / 3.7)"),
        (r"(?<!塑料外壳式)塑壳断路器", "塑料外壳式断路器 (GB/T 14048.2—2020 Cl. 2.6 / 3.3)"),
        (r"万能式断路器", "空气断路器（分类：万能式） (GB/T 14048.2—2020 Cl. 2.7 / 3.3)"),
        (r"功率损耗", "功耗 (GB/T 14048.2—2020 附录 G)"),
        (r"结构差异", "结构段 (GB/T 14048.2—2020 Cl. 2.1.2 / 7.1.6)"),
        (r"合闸涌流脱扣器", "接通电流脱扣器 (GB/T 14048.2—2020 Cl. 2.10)"),
    ]

    blocks: dict[str, list[tuple[str, str]]] = {}
    for loc, line in units:
        m_page = re.match(r"^(P\d+):", loc)
        if m_page:
            bkey = m_page.group(1)
        elif len(units) <= 40:
            bkey = "__all__"
        else:
            bkey = loc
        blocks.setdefault(bkey, []).append((loc, line))

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

    for items in blocks.values():
        joined = "\n".join(txt for _, txt in items)
        m_a = cat_a_re.search(joined)
        m_st = st_or_icw_re.search(joined)
        if m_a and m_st:
            hit_loc = next((loc for loc, txt in items if cat_a_re.search(txt)), items[0][0])
            hit_line = next((txt for loc, txt in items if loc == hit_loc), items[0][1])
            add(
                hit_loc,
                "TECH_CONTRADICTION",
                f"{m_a.group(0)} + {m_st.group(0)}",
                "Category A forbids Isd/Icw; use Selectivity category B + declared Icw (IEC 60947-2:2024 Cl. 5.4 / GB/T 14048.2—2020 Cl. 4.4)",
                hit_line,
            )
    return findings


def build_chunks(units: list[tuple[str, str]], chunk_size: int) -> list[list[tuple[str, str]]]:
    if chunk_size <= 0 or not units:
        return [units] if units else []
    return [units[i:i + chunk_size] for i in range(0, len(units), chunk_size)]


def format_report_md(loaded: dict, findings: list[dict]) -> str:
    high = [f for f in findings if f["severity"] == "HIGH"]
    med = [f for f in findings if f["severity"] != "HIGH"]
    lines = [
        "### Coverage Ledger",
        "| Total units | Scanned | Unscanned Visual Pages (<50 chars) | HIGH hits | MEDIUM hits |",
        "| :--- | :--- | :--- | :--- | :--- |",
        f"| {loaded['total']} | {loaded['scanned']} | {loaded['low_text_pages']} | {len(high)} | {len(med)} |",
        "",
        "### HIGH-Severity Findings (Verbatim, up to 60 rows)",
        "| Location | Category | Quoted Match | Unique Statutory Fix |",
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


def emit_annotate_payload(findings: list[dict], out_path: Path) -> int:
    seen: set[tuple[int, str]] = set()
    items: list[dict] = []
    for f in findings:
        m = re.match(r"^P(\d+):", f["location"])
        if not m:
            continue
        pno = int(m.group(1))
        key = (pno, f["match"])
        if key in seen:
            continue
        seen.add(key)
        items.append({
            "page": pno,
            "search": f["match"],
            "comment": f"[{f['severity']}/{f['category']}] {f['fix']}",
        })
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps({"schema": "chint-office-annotate/v1", "annotations": items}, ensure_ascii=False, indent=2), encoding="utf-8")
    return len(items)


def run_self_test() -> int:
    import tempfile

    mccb_dirty = [("P1:L1", "NXM-250S Molded Case Circuit Breaker (IEC 60947-2, Cl. 4.3.5). Frame size: 250A. Icu: 36kA at 415V. Ics: 100% Icu. Mechanical durability: 20000 times. Short-time pickup Isd.")]
    mccb_hits = {f["category"] for f in scan_units(mccb_dirty, "mccb", "en")}
    assert {"ORTHOGRAPHY_US_HYPHEN", "OBSOLETE_CLAUSE_ED5", "UNIT_SPACING_PUNCT", "BLACKLIST_CHINGLISH_UL"} <= mccb_hits, mccb_hits

    acb_dirty = [("P2:L1", "Closed electromagnet (XF), Shunt Trip (MX), Earch current transformer, Closing Preparation Contact (PF), hole opener on drawer seat.")]
    acb_hits = {f["category"] for f in scan_units(acb_dirty, "acb", "en")}
    assert {"BLACKLIST_CHINGLISH_UL", "COMPETITOR_CODE"} <= acb_hits, acb_hits

    zh_dirty = [("P3:L1", "抽出式断路器（使用类别 A）与塑壳断路器、万能式断路器在 400V 下测量功率损耗与结构差异，含合闸涌流脱扣器。")]
    zh_res = scan_units(zh_dirty, "acb", "zh")
    zh_hits = {f["category"] for f in zh_res}
    assert {"GB_STATUTORY_ZH", "UNIT_SPACING_PUNCT"} <= zh_hits, zh_hits
    assert any(f["match"] == "塑壳断路器" for f in zh_res), zh_res
    assert any(f["match"] == "万能式断路器" for f in zh_res), zh_res

    contra_en = [("P7:L1", "Selectivity category: A"), ("P7:L2", "Short-time pick-up Isd = 6 Ir")]
    contra_zh = [("P8:L1", "选择性类别：A，短时动作电流 Isd = 6 Ir")]
    assert any(f["category"] == "TECH_CONTRADICTION" and f["severity"] == "HIGH" for f in scan_units(contra_en, "mccb", "en"))
    assert any(f["category"] == "TECH_CONTRADICTION" and f["severity"] == "HIGH" for f in scan_units(contra_zh, "mccb", "zh"))

    clean_en = [("P4:L1", "Moulded-case circuit-breaker (MCCB) 250 A, 415 V AC, Icu 36 kA rms, Icm 75.6 kA peak, utilization category AC-22, 20,000 operating cycles per Cl. 8.2.4.2.")]
    assert len(scan_units(clean_en, "all", "en")) == 0

    clean_zh = [("P5:L1", "GB/T 14048.2—2020 Cl. 2.5 抽屉式断路器、Cl. 2.6 塑料外壳式断路器、Cl. 2.10 接通电流脱扣器、Cl. 4.3.5、Cl. 7.2.4.2 操作性能能力及附录 G 功耗；电压 400 V，温度 -5 °C 至 +40 °C。")]
    assert len(scan_units(clean_zh, "all", "zh")) == 0

    fp_guard = [("P6:L1", "TABLE OF CONTENTS: NXM-250S 3P 4P AC-22 IP40 CD-1 2A Cl. 7.2.1 per IEC 60947-1. Selectivity category: A/B.")]
    assert len(scan_units(fp_guard, "all", "en")) == 0

    with tempfile.TemporaryDirectory() as td:
        tdir = Path(td)
        ext_json = tdir / "extract.json"
        ann_json = tdir / "ann.json"
        ext_json.write_text(json.dumps({
            "schema": "chint-office-extract/v1",
            "source": "x.pdf",
            "total_units": 3,
            "scanned_units": 3,
            "low_text_pages": [2],
            "units": [{"location": "P1:L1", "text": "Frame size: 250A"}, {"location": "P1:L2", "text": "Shunt Trip"}],
        }), encoding="utf-8")
        loaded = load_units(str(ext_json))
        assert loaded["low_text_pages"] == [2]
        findings = scan_units(loaded["units"], "mccb", "en")
        assert len(findings) == 2
        md = format_report_md(loaded, findings)
        assert "Coverage Ledger" in md and "MEDIUM-Severity Findings" in md
        written = emit_annotate_payload(findings, ann_json)
        assert written == 2
        ann_obj = json.loads(ann_json.read_text(encoding="utf-8"))
        assert ann_obj["schema"] == "chint-office-annotate/v1" and len(ann_obj["annotations"]) == 2
        chunks = build_chunks(loaded["units"], 1)
        assert len(chunks) == 2

    print("SELF-TEST PASS: 9/9 suites passed (EN/ZH/TECH_CONTRADICTION/clean/FP-guard/report-md/annotate/chunking).")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Pure-stdlib text linter for chint-translation")
    parser.add_argument("source", nargs="?", help="Text file, chint-office-extract/v1 JSON, or '-' for stdin")
    parser.add_argument("--dept", choices=["acb", "mccb", "all"], default="all")
    parser.add_argument("--mode", choices=["en", "zh"], default="en")
    parser.add_argument("--json", action="store_true", help="Output structured JSON")
    parser.add_argument("--report-md", action="store_true", help="Output deduplicated context-safe Markdown report")
    parser.add_argument("--emit-annotate", help="Write deduplicated chint-office-annotate/v1 JSON to file")
    parser.add_argument("--chunk-size", type=int, default=0, help="Split units into chunks of N non-empty lines")
    parser.add_argument("--chunk-index", type=int, default=0, help="Inspect 1-based chunk K only")
    parser.add_argument("--chunks-info", action="store_true", help="Print chunk manifest with per-chunk hit counts")
    parser.add_argument("--self-test", action="store_true", help="Run built-in verification suite")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()
    if not args.source:
        parser.error("source is required unless --self-test is set")

    loaded = load_units(args.source)
    units = loaded["units"]

    if args.chunks_info:
        csize = args.chunk_size if args.chunk_size > 0 else 50
        chunks = build_chunks(units, csize)
        manifest_chunks = []
        for idx, ch in enumerate(chunks, 1):
            cf = scan_units(ch, args.dept, args.mode)
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
            "total_units": len(units),
            "chunk_size": csize,
            "total_chunks": len(chunks),
            "low_text_pages": loaded["low_text_pages"],
            "chunks": manifest_chunks,
        }
        if args.json:
            print(json.dumps(manifest, ensure_ascii=False, indent=2))
        else:
            print(f"Total non-empty units: {manifest['total_units']} | Chunks: {manifest['total_chunks']} (size={csize}) | low_text_pages={manifest['low_text_pages']}")
            for c in manifest_chunks:
                print(f"  Chunk {c['index']}: {c['start_location']}..{c['end_location']} ({c['unit_count']} units) | HIGH={c['high_hits']} MEDIUM={c['medium_hits']}")
        return 0

    active_units = units
    chunk_meta = None
    if args.chunk_index > 0:
        csize = args.chunk_size if args.chunk_size > 0 else 50
        chunks = build_chunks(units, csize)
        if args.chunk_index > len(chunks):
            parser.error(f"--chunk-index {args.chunk_index} out of range 1..{len(chunks)}")
        active_units = chunks[args.chunk_index - 1]
        chunk_meta = {"index": args.chunk_index, "total_chunks": len(chunks), "unit_count": len(active_units)}

    findings = scan_units(active_units, args.dept, args.mode)
    if args.emit_annotate:
        emit_annotate_payload(findings, Path(args.emit_annotate))

    report = {
        "source": loaded["source"],
        "dept": args.dept,
        "mode": args.mode,
        "total_units": loaded["total"],
        "scanned_units": loaded["scanned"],
        "low_text_pages": loaded["low_text_pages"],
        "finding_count": len(findings),
        "high_count": sum(1 for f in findings if f["severity"] == "HIGH"),
        "medium_count": sum(1 for f in findings if f["severity"] != "HIGH"),
        "findings": findings,
    }
    if chunk_meta:
        report["chunk"] = chunk_meta
        report["units"] = [{"location": loc, "text": txt} for loc, txt in active_units]

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    elif args.report_md:
        print(format_report_md(loaded, findings))
    else:
        print(f"Scanned {report['scanned_units']}/{report['total_units']} units | low_text_pages={report['low_text_pages']} | findings={report['finding_count']} (HIGH={report['high_count']}, MEDIUM={report['medium_count']})")
        if chunk_meta:
            print(f"--- Chunk {chunk_meta['index']}/{chunk_meta['total_chunks']} ({chunk_meta['unit_count']} units) ---")
            for loc, txt in active_units:
                print(f"[{loc}] {txt}")
            print("--- Findings ---")
        for f in findings:
            print(f"[{f['location']}] ({f['severity']}/{f['category']}) '{f['match']}' -> {f['fix']}")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
