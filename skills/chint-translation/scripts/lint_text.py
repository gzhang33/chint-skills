#!/usr/bin/env python3
"""Pure-stdlib IEC 60947-2:2024 & GB/T 14048.2-2020 text/extract-JSON linter for chint-translation."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


def _ensure_utf8_stdio() -> None:
    """Force UTF-8 on stdio streams so piped JSON/text works on Windows cp936 consoles."""
    for stream in (sys.stdin, sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8")
            except (AttributeError, OSError, ValueError):
                pass


ORTHO_RULES = [
    (r"\bmolded\b", "moulded (IEC UK spelling)"),
    (r"\bcolors?\b", "colour(s) (IEC UK spelling)"),
    (r"\baluminum\b", "aluminium (IEC UK spelling)"),
    (r"\bcatalogs?\b", "catalogue(s) (IEC UK spelling)"),
    (r"\bcircuit breakers?\b", "circuit-breaker(s) (Cl. 3.1 hyphenated)"),
    (r"\blockout\b", "lock-out (Cl. 3.10 hyphenated)"),
    (r"\bbackup\b", "back-up (Annex A hyphenated)"),
    (r"\bpickup\b", "pick-up (Cl. 3.17 hyphenated)"),
    (r"\bunder[- ]voltage\b", "undervoltage (unhyphenated per IEC 60947-2)"),
    (r"\benergis\w*\b", "energiz* (ISO/IEC Oxford -ize)"),
    (r"\butilisation\b", "utilization (Annex L.4.1 ISO/IEC -ize)"),
    (r"\bearth-fault\b", "ground-fault (G-stage) / earth fault (Annex B)"),
    (r"\bdurability\b", "operational performance / operating cycles / endurance (Cl. 8.2.4.2)"),
    (r"\bdiscrimination\b", "selectivity (Annex A / Cl. 5.4)"),
    (r"\bdraw-out\b", "withdrawable (IEC Cl. 3.5)"),
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
    (r"\bdrawer(?:\s+(?:type|box|seat|cradle|base))?\b", "Withdrawable / Withdrawable cradle (IEC Cl. 3.5)"),
]

COMPETITOR_RULES_COMMON = [
    (r"(?<![A-Za-z0-9\-])MX(?![A-Za-z0-9\-])", "SHT (Shunt release)"),
    (r"(?<![A-Za-z0-9\-])MN(?![A-Za-z0-9\-])", "UVT (Undervoltage release)"),
    (r"(?<![A-Za-z0-9\-])SDE(?![A-Za-z0-9\-])", "AL (Alarm switch)"),
    (r"\(OF\)", "(AX) (Auxiliary contact)"),
    (r"\(YO\)", "(SHT) (Shunt release)"),
]

COMPETITOR_RULES_ACB = [
    (r"(?<![A-Za-z0-9\-])XF(?![A-Za-z0-9\-])", "CEM (Closing release)"),
    (r"\(PF\)|\bPF\s+contact\b", "SPC (Ready-to-close contact)"),
    (r"(?<![A-Za-z0-9\-])MCH(?![A-Za-z0-9\-])", "MOD (Motor-operator)"),
    (r"(?<![A-Za-z0-9\-])KLC(?![A-Za-z0-9\-])", "KL (Key lock)"),
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
    "UNRESOLVED_SLOT",
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
            "_full_line": line,
        })

    ed5_re = re.compile(r"(?:Cl\.|Clause)\s*(?:2\.1(?:\.\d+)?|4\.3\.[1-6](?:\.\d+)?|7\.2\.[1-8](?:\.\d+)?|8\.3\.[1-9](?:\.\d+)?)\b", re.IGNORECASE)
    unit_gap_re = re.compile(r"(?<![A-Za-z0-9\-_])\d+(?:\.\d+)?(?:kA|mA|kV|mV|ms|Hz|kHz|mm²|mm|kW|VA|kVA|N·m|°C|A|V|s)(?![A-Za-z0-9\-])")
    prefix_guard_re = re.compile(r"(?i)(?:Fig\.?|Figure|Table|Grade|Class|Type|Series|Cat\.?)\s+$")
    decade_re = re.compile(r"^(?:19|20)\d0s$")
    pf_context_re = re.compile(r"(?i)power\s+factor|\bcos\s*[φϕ]?|功率因数")
    cat_a_re = re.compile(r"(?:Selectivity[ \t]+category[ \t]*[:：]?[ \t]*A\b|选择性类别[ \t]*[:：]?[ \t]*A\b)(?![ \t]*[/、,])", re.IGNORECASE)
    cat_b_re = re.compile(r"(?:Selectivity[ \t]+category[ \t]*[:：]?[ \t]*B\b|选择性类别[ \t]*[:：]?[ \t]*B\b|\bCategory[ \t]+B\b)", re.IGNORECASE)
    model_hdr_re = re.compile(r"^\s*(?:NX[AMF]\d|NM\d|NA\d)")
    st_or_icw_re = re.compile(r"\b(?:Isd|Icw)\b")
    zh_bad = [
        (r"相间对中性线", "相-中性线 (IEC 60947-2:2024 Cl. 5.3.6.2.3)"),
        (r"(?<![单两二三四多])极极限", "单极极限"),
        (r"隔离开关断路器", "隔离开关 (IEC 60947-3 / GB/T 14048.3)"),
        (r"使用类别\s*[AB]", "选择性类别 A / B (GB/T 14048.2—2020 Cl. 3.1 / 4.4)"),
        (r"抽出式断路器", "抽屉式断路器 (GB/T 14048.2—2020 Cl. 2.5 / 3.7)"),
        (r"(?<!塑料外壳式)塑壳断路器", "塑料外壳式断路器 (GB/T 14048.2—2020 Cl. 2.6 / 3.3)"),
        (r"万能式断路器", "空气断路器（分类：万能式） (GB/T 14048.2—2020 Cl. 2.7 / 3.3)"),
        (r"功率损耗", "功耗 (GB/T 14048.2—2020 附录 G)"),
        (r"结构差异", "结构段 (GB/T 14048.2—2020 Cl. 2.1.2 / 7.1.6)"),
        (r"合闸涌流脱扣器", "接通电流脱扣器 (GB/T 14048.2—2020 Cl. 2.10)"),
        (r"闭合电磁铁", "闭合脱扣器 (GB/T 14048.2—2020 Cl. 2.23)"),
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
            comp_rules = list(COMPETITOR_RULES_COMMON)
            if dept in {"acb", "all"}:
                comp_rules.extend(COMPETITOR_RULES_ACB)
            for c_pat, c_fix in comp_rules:
                for m in re.finditer(c_pat, line):
                    if "(PF)" in m.group(0).upper() and pf_context_re.search(line):
                        continue
                    add(loc, "COMPETITOR_CODE", m.group(0), c_fix, line)
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
                window = line[max(0, m.start() - 35):min(len(line), m.end() + 35)]
                if not any(tag in window for tag in ("60947-1", "60947-3", "14048.2", "GB/T")):
                    add(loc, "OBSOLETE_CLAUSE_ED5", m.group(0), "Use IEC 60947-2:2024 Ed. 6.0 clause numbers", line)
        else:
            for pat, fix in zh_bad:
                for m in re.finditer(pat, line):
                    add(loc, "GB_STATUTORY_ZH", m.group(0), fix, line)

        for m in unit_gap_re.finditer(line):
            tok = m.group(0)
            if decade_re.match(tok):
                continue
            if prefix_guard_re.search(line[:m.start()]):
                continue
            if tok in {"2A", "3A"} and ("CD-1" in line or "控制器" in line or "型" in line or line.strip() in {"2A", "3A"}):
                continue
            add(loc, "UNIT_SPACING_PUNCT", tok, "Insert single half-width space between number and unit", line)
        if "℃" in line:
            add(loc, "UNIT_SPACING_PUNCT", "℃", "Replace full-width '℃' with ' °C'", line)
        for m in re.finditer(r"\{\{[^}]+\}\}", line):
            add(loc, "UNRESOLVED_SLOT", m.group(0), "Resolve value slot from datasheet or rewrite qualitatively", line)

    type_fb_re = re.compile(r"\bType[ \t]+(?:F|B\+)\b", re.IGNORECASE)
    for items in blocks.values():
        for idx, (loc, txt) in enumerate(items):
            m_a = cat_a_re.search(txt)
            if m_a:
                # Tight local window: check immediate previous line and next up to 3 lines,
                # stopping at Category B or a new model row to prevent multi-model false positives.
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
                    add(
                        loc,
                        "TECH_CONTRADICTION",
                        f"{m_a.group(0)} + {m_st.group(0)}",
                        "Category A forbids Isd/Icw; use Selectivity category B + declared Icw (IEC 60947-2:2024 Cl. 5.4 / GB/T 14048.2—2020 Cl. 4.4)",
                        txt,
                    )

            m_fb = type_fb_re.search(txt)
            if m_fb:
                lo, hi = max(0, idx - 2), min(len(items), idx + 3)
                local_blob = "\n".join(t for _, t in items[lo:hi])
                if re.search(r"60947-2", local_blob) and not re.search(r"62423|0664", local_blob):
                    add(
                        loc,
                        "TECH_CONTRADICTION",
                        f"{m_fb.group(0)} + IEC 60947-2",
                        "IEC 60947-2 Annex B covers Type AC/A/B only; cite IEC 62423 / VDE 0664-400 for Type F / B+",
                        txt,
                    )
    return findings


def strip_internal_fields(findings: list[dict]) -> list[dict]:
    return [{k: v for k, v in f.items() if not k.startswith("_")} for f in findings]


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


CLAUSE_PAREN_RE = re.compile(r"\s*\((?:IEC|GB/T|Cl\.|Annex|ISO/IEC|unhyphenated|explicit)[^)]*\)\s*$", re.IGNORECASE)
UNIT_SPACING_FIX = "Insert single half-width space between number and unit"
ASCII_PUNCT_FIX = "Use half-width ASCII punctuation in English prose"


def _strip_clause_notes(text: str) -> str:
    cur = text.strip()
    while True:
        nxt = CLAUSE_PAREN_RE.sub("", cur).strip()
        if nxt == cur:
            return cur
        cur = nxt


def _format_unit_gap(tok: str) -> str:
    return re.sub(r"^(\d+(?:\.\d+)?)(.+)$", r"\1 \2", tok)


def clean_pdf_replacement(match: str, category: str, fix: str) -> str:
    if category == "TECH_CONTRADICTION":
        if "62423" in fix:
            return "IEC 62423 / VDE 0664-400（IEC 60947-2 附录 B 仅覆盖 AC/A/B 型）"
        return "Selectivity category B（含 Isd/Icw 时须声明为 B 类）"
    if category == "OBSOLETE_CLAUSE_ED5":
        return "按 IEC 60947-2:2024 第 6 版核改条款号"
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
    if category == "BLACKLIST_CHINGLISH_UL":
        if fix == "operating cycles":
            m_times = re.fullmatch(r"(\d[\d,]*)\s+times", match, re.IGNORECASE)
            if m_times:
                val = int(m_times.group(1).replace(",", ""))
                return f"{val:,} operating cycles"
        if fix == "plain integer operating cycles":
            return "<整数> operating cycles"
        if fix.startswith("CBI (Annex L)"):
            return "CBI / switch-disconnector"
    if category == "UNIT_SPACING_PUNCT":
        if fix == UNIT_SPACING_FIX:
            return _format_unit_gap(match)
        if fix == ASCII_PUNCT_FIX:
            return "半角英文标点"
        if "℃" in fix:
            return " °C"
        if fix.startswith("100% of Icu"):
            return "100% of Icu"
        if "kA rms" in fix:
            return re.sub(r"(\d)kA\b", r"\1 kA", match) + " rms"
        if "kA peak" in fix:
            return re.sub(r"(\d)kA\b", r"\1 kA", match) + " peak"
    if category == "ORTHOGRAPHY_US_HYPHEN":
        if "energiz*" in fix:
            if match.isupper():
                return re.sub(r"ENERGIS", "ENERGIZ", match)
            return re.sub(r"(?i)energis", lambda m: "Energiz" if m.group(0)[0].isupper() else "energiz", match)
        base = _strip_clause_notes(fix)
        if "(s)" in base:
            base = base.replace("(s)", "s" if match.lower().endswith("s") else "")
        if match[:1].isupper() and base[:1].islower():
            base = base[0].upper() + base[1:]
        return base
    return _strip_clause_notes(fix)


def _coalesce_high_compounds(findings: list[dict]) -> list[dict]:
    """Merge adjacent `BLACKLIST_CHINGLISH_UL + (COMPETITOR_CODE)` compounds sharing the same CHINT code."""
    by_loc: dict[str, list[int]] = {}
    for idx, f in enumerate(findings):
        if f["severity"] == "HIGH":
            by_loc.setdefault(f["location"], []).append(idx)

    absorbed: set[int] = set()
    overrides: dict[int, str] = {}
    for idxs in by_loc.values():
        bl_idxs = [i for i in idxs if findings[i]["category"] == "BLACKLIST_CHINGLISH_UL"]
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
                if cm.startswith("(") and cm.endswith(")"):
                    pat = rf"{re.escape(bf['match'])}\s*{re.escape(cm)}"
                else:
                    pat = rf"{re.escape(bf['match'])}\s*\(\s*{re.escape(cm)}\s*\)"
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


def build_annotate_payload(findings: list[dict], author: str = "CHINT Translation", min_severity: str = "high") -> dict:
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
            search_str = f["match"].split(" + ")[0] if f["category"] == "TECH_CONTRADICTION" else f["match"]
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
        print(f"WARNING: --emit-annotate skipped {skipped_non_pdf} non-PDF finding(s) lacking 'P{{n}}:' coordinates.", file=sys.stderr)

    for (pno, cat, fix), grp in med_groups.items():
        unique_matches = list(dict.fromkeys(f["match"] for f in grp))
        count = len(grp)
        if cat == "UNIT_SPACING_PUNCT" and fix == UNIT_SPACING_FIX:
            ex_tokens = [_format_unit_gap(tok) for tok in unique_matches[:3]]
            ex_str = "、".join(ex_tokens) + (" 等" if len(unique_matches) > 3 else "")
            comment = f"替换为：数字与单位间加半角空格（本页 {count} 处，如 {ex_str}）"
        elif cat == "UNIT_SPACING_PUNCT" and fix == ASCII_PUNCT_FIX:
            comment = f"替换为：半角英文标点（本页 {count} 处）"
        else:
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


def emit_annotate_payload(findings: list[dict], out_target: str | Path, author: str = "CHINT Translation", min_severity: str = "high") -> int:
    payload = build_annotate_payload(findings, author=author, min_severity=min_severity)
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

    mccb_dirty = [("P1:L1", "NXM-250S Molded Case Circuit Breaker (IEC 60947-2, Cl. 4.3.5). Frame size: 250A. Icu: 36kA at 415V. Ics: 100% Icu. Mechanical durability: 20000 times. Short-time pickup Isd. Drawer type, Type F, 50/60Hz, 380/400/415V, 10mm². Under voltage ENERGISED.")]
    mccb_res = scan_units(mccb_dirty, "mccb", "en")
    mccb_hits = {f["category"] for f in mccb_res}
    assert {"ORTHOGRAPHY_US_HYPHEN", "OBSOLETE_CLAUSE_ED5", "UNIT_SPACING_PUNCT", "BLACKLIST_CHINGLISH_UL", "TECH_CONTRADICTION"} <= mccb_hits, mccb_hits
    assert any(f["match"].lower() == "under voltage" for f in mccb_res), mccb_res
    assert clean_pdf_replacement("ENERGISED", "ORTHOGRAPHY_US_HYPHEN", "energiz* (ISO/IEC Oxford -ize)") == "ENERGIZED"
    assert clean_pdf_replacement("Cl. 4.3.5", "OBSOLETE_CLAUSE_ED5", "Use IEC 60947-2:2024 Ed. 6.0 clause numbers") == "按 IEC 60947-2:2024 第 6 版核改条款号"

    acb_dirty = [("P2:L1", "Closed electromagnet (XF), Shunt Trip (MX), Earch current transformer, Closing Preparation Contact (PF), hole opener on drawer seat; standalone MN, (YO), and standalone (PF).")]
    acb_res = scan_units(acb_dirty, "acb", "en")
    acb_ann = build_annotate_payload(acb_res)["annotations"]
    ann_map = {a["search"]: a["comment"] for a in acb_ann}
    assert ann_map.get("Closed electromagnet (XF)") == "替换为：Closing release (CEM)", ann_map
    assert ann_map.get("Shunt Trip (MX)") == "替换为：Shunt release (SHT)", ann_map
    assert ann_map.get("Closing Preparation Contact (PF)") == "替换为：Ready-to-close contact (SPC)", ann_map
    assert ann_map.get("MN") == "替换为：UVT", ann_map
    assert ann_map.get("(YO)") == "替换为：(SHT)", ann_map
    assert ann_map.get("(PF)") == "替换为：(SPC)", ann_map

    long_prefix = "A" * 130 + " Closed electromagnet (XF)"
    long_ann = build_annotate_payload(scan_units([("P2:L9", long_prefix)], "acb", "en"))["annotations"]
    assert len(long_ann) == 1 and long_ann[0]["search"] == "Closed electromagnet (XF)", long_ann

    times_ann = build_annotate_payload(scan_units([("P2:L2", "Mechanical durability: 10000 times.")], "acb", "en"))["annotations"]
    assert times_ann[0]["comment"] == "替换为：10,000 operating cycles", times_ann

    slot_res = scan_units([("P2:L3", "Supply voltage {{Uc: V}}.")], "acb", "en")
    assert len(slot_res) == 1 and slot_res[0]["severity"] == "HIGH" and slot_res[0]["category"] == "UNRESOLVED_SLOT", slot_res

    zh_dirty = [("P3:L1", "抽出式断路器（使用类别 A）与塑壳断路器、万能式断路器在 400V 下测量功率损耗与结构差异，含合闸涌流脱扣器与闭合电磁铁。")]
    zh_res = scan_units(zh_dirty, "acb", "zh")
    zh_hits = {f["category"] for f in zh_res}
    assert {"GB_STATUTORY_ZH", "UNIT_SPACING_PUNCT"} <= zh_hits, zh_hits
    assert any(f["match"] == "塑壳断路器" for f in zh_res), zh_res
    assert any(f["match"] == "万能式断路器" for f in zh_res), zh_res
    assert any(f["match"] == "闭合电磁铁" for f in zh_res), zh_res

    contra_en = [("P7:L1", "Selectivity category: A"), ("P7:L2", "Short-time pick-up Isd = 6 Ir")]
    contra_zh = [("P8:L1", "选择性类别：A，短时动作电流 Isd = 6 Ir")]
    multi_model_page = [
        ("P9:L1", "NXM-125 Selectivity category: A"),
        ("P9:L2", "NXM-630E Selectivity category: B"),
        ("P9:L3", "Short-time pick-up Isd = 6 Ir; Icw 15 kA"),
    ]
    assert any(f["category"] == "TECH_CONTRADICTION" and f["severity"] == "HIGH" for f in scan_units(contra_en, "mccb", "en"))
    assert any(f["category"] == "TECH_CONTRADICTION" and f["severity"] == "HIGH" for f in scan_units(contra_zh, "mccb", "zh"))
    assert not any(f["category"] == "TECH_CONTRADICTION" for f in scan_units(multi_model_page, "mccb", "en")), scan_units(multi_model_page, "mccb", "en")

    clean_en = [("P4:L1", "Moulded-case circuit-breaker (MCCB) 250 A, 415 V AC, Icu 36 kA rms, Icm 75.6 kA peak, utilization category AC-22, 20,000 operating cycles per Cl. 8.2.4.2.")]
    assert len(scan_units(clean_en, "all", "en")) == 0

    clean_zh = [("P5:L1", "GB/T 14048.2—2020 Cl. 2.5 抽屉式断路器、Cl. 2.6 塑料外壳式断路器、Cl. 2.10 接通电流脱扣器、Cl. 4.3.5、Cl. 7.2.4.2 操作性能能力及附录 G 功耗；三极极限短路分断能力；电压 400 V，温度 -5 °C 至 +40 °C。")]
    assert len(scan_units(clean_zh, "all", "zh")) == 0

    fp_guard = [("P6:L1", "TABLE OF CONTENTS: NXM-250S MX-100 XF-20 MN-400 Fig. 1A Table 2A 1990s 3P 4P AC-22 IP40 CD-1 2A Cl. 7.2.1 per IEC 60947-1; GB/T 14048.2—2020 Cl. 4.3.5. Selectivity category: A/B. Power factor (PF) = 0.95.")]
    assert len(scan_units(fp_guard, "all", "en")) == 0, scan_units(fp_guard, "all", "en")

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
        assert written == 1, written
        ann_obj = json.loads(ann_json.read_text(encoding="utf-8"))
        assert ann_obj["schema"] == "chint-office-annotate/v1" and len(ann_obj["annotations"]) == 1
        assert ann_obj["annotations"][0]["match_mode"] == "all" and ann_obj["annotations"][0]["comment"] == "替换为：Shunt release (SHT)", ann_obj
        all_obj = build_annotate_payload(findings, min_severity="all")
        high_ann = [a for a in all_obj["annotations"] if a["match_mode"] == "all"]
        med_ann = [a for a in all_obj["annotations"] if a["match_mode"] == "merged"]
        assert len(high_ann) == 1 and len(med_ann) == 1 and med_ann[0]["search"] == "250A", all_obj
        case_dedup = build_annotate_payload([
            {"location": "P1:L1", "severity": "HIGH", "category": "BLACKLIST_CHINGLISH_UL", "match": "Closed electromagnet", "fix": "Closing release (CEM)", "excerpt": ""},
            {"location": "P1:L2", "severity": "HIGH", "category": "BLACKLIST_CHINGLISH_UL", "match": "closed electromagnet", "fix": "Closing release (CEM)", "excerpt": ""},
        ])["annotations"]
        assert len(case_dedup) == 1, case_dedup
        merged_check = build_annotate_payload([
            {"location": "P1:L1", "severity": "MEDIUM", "category": "UNIT_SPACING_PUNCT", "match": "250A", "fix": UNIT_SPACING_FIX, "excerpt": ""},
            {"location": "P1:L2", "severity": "MEDIUM", "category": "UNIT_SPACING_PUNCT", "match": "400V", "fix": UNIT_SPACING_FIX, "excerpt": ""},
        ], min_severity="all")["annotations"]
        assert len(merged_check) == 1 and merged_check[0]["searches"] == ["250A", "400V"] and "250 A、400 V" in merged_check[0]["comment"], merged_check
        assert all("_full_line" not in item for item in strip_internal_fields(findings))
        chunks = build_chunks(loaded["units"], 1)
        assert len(chunks) == 2

    drawout_res = scan_units([("P1:L5", "Draw-out circuit-breaker type.")], "acb", "en")
    assert any(f["match"].lower() == "draw-out" and f["severity"] == "MEDIUM" for f in drawout_res), drawout_res
    assert build_annotate_payload(drawout_res, min_severity="high")["annotations"] == [], drawout_res
    assert len(build_annotate_payload(drawout_res, min_severity="all")["annotations"]) >= 1, drawout_res

    print("SELF-TEST PASS: 11/11 suites passed (EN/ZH/multi-model/long-line/FP-guard/ENERGISED/draw-out-MEDIUM/report-md/compound-annotate/chunking).")
    return 0


def main() -> int:
    _ensure_utf8_stdio()
    parser = argparse.ArgumentParser(description="Pure-stdlib text linter for chint-translation")
    parser.add_argument("source", nargs="?", help="Text file, chint-office-extract/v1 JSON, or '-' for stdin")
    parser.add_argument("--dept", choices=["acb", "mccb", "all"], default="all")
    parser.add_argument("--mode", choices=["en", "zh"], default="en")
    parser.add_argument("--json", action="store_true", help="Output structured JSON")
    parser.add_argument("--report-md", action="store_true", help="Output deduplicated context-safe Markdown report")
    parser.add_argument("--emit-annotate", help="Write chint-office-annotate/v1 JSON to '-' (stdout pipe, zero disk file) or file path")
    parser.add_argument("--annotate-severity", choices=["high", "all"], default="high", help="Minimum severity included in --emit-annotate (default: high; use 'all' to include merged MEDIUM style/spacing rules)")
    parser.add_argument("--author", default="CHINT Translation", help="Annotation author when emitting chint-office-annotate/v1")
    parser.add_argument("--chunk-size", type=int, default=0, help="Split units into chunks of N non-empty lines")
    parser.add_argument("--chunk-index", type=int, default=0, help="Inspect 1-based chunk K only")
    parser.add_argument("--chunks-info", action="store_true", help="Print chunk manifest with per-chunk hit counts")
    parser.add_argument("--exit-zero", action="store_true", help="Exit 0 even when findings exist (useful in Branch B pipelines)")
    parser.add_argument("--self-test", action="store_true", help="Run built-in verification suite")
    args = parser.parse_args()

    try:
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
                raise ValueError(f"--chunk-index {args.chunk_index} out of range 1..{len(chunks)}")
            active_units = chunks[args.chunk_index - 1]
            chunk_meta = {"index": args.chunk_index, "total_chunks": len(chunks), "unit_count": len(active_units)}

        findings = scan_units(active_units, args.dept, args.mode)
        if args.emit_annotate:
            emit_annotate_payload(findings, args.emit_annotate, author=args.author, min_severity=args.annotate_severity)
            if args.emit_annotate == "-":
                return 0

        clean_findings = strip_internal_fields(findings)
        report = {
            "source": loaded["source"],
            "dept": args.dept,
            "mode": args.mode,
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
            print(format_report_md(loaded, clean_findings))
        else:
            print(f"Scanned {report['scanned_units']}/{report['total_units']} units | low_text_pages={report['low_text_pages']} | findings={report['finding_count']} (HIGH={report['high_count']}, MEDIUM={report['medium_count']})")
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