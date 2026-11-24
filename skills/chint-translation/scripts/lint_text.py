#!/usr/bin/env python3
"""Pure-stdlib IEC 60947-2:2024 & GB/T 14048.2—2020 substantive translation linter."""
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


BLACKLIST_COMMON = [
    (r"\bshunting release\b", "Shunt release (SHT)"),
    (r"\bshunt opening release\b", "Shunt release (SHT)"),
    (r"\bexcitation release\b", "Shunt release (SHT)"),
    (r"\bshunt trip\b", "Shunt release (SHT)"),
    (r"\black voltage\b", "Undervoltage release (UVT)"),
    (r"\bten thousand times\b", "plain integer operating cycles"),
    (r"\binstallation and debugging\b", "installation and commissioning"),
    (r"\bmatters need attention\b", "operating precautions"),
    (r"\bordering instructions?\b", "ordering information"),
    (r"\bwrong action\b", "false tripping"),
    (r"\berror work\b", "false tripping"),
    (r"\bno tolerance specified\b", "unspecified linear tolerance"),
    (r"\buse class(?:es)?\b", "selectivity category / utilization category"),
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
    (r"\bclosing magnet\b", "Closing release (CEM)"),
    (r"\bearch current transformer\b", "Earth current transformer (ECT)"),
    (r"\binterphased\b", "interphase barrier (DD / FD)"),
    (r"\binter phased\b", "interphase barrier (DD / FD)"),
    (r"\bphase space plate\b", "interphase barrier (DD / FD)"),
    (r"\bunder voltage delay release-zero\b", "Loss-of-voltage time-delay release (UVTZ)"),
    (r"\bclosing preparation contact\b", "Ready-to-close contact (SPC)"),
    (r"\bseparation position\b", "Disconnected position (Cl. 8.1.2)"),
    (r"\bconnection position\b", "Connected position"),
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
    (r"\bclosing magnet\b", "Closing release"),
]

STD_CONCEPT_ZH = [
    (r"相间对中性线", "相-中性线 (IEC 60947-2:2024 Cl. 5.3.6.2.3)"),
    (r"(?<![单两二三四多])极极限", "单极极限"),
    (r"隔离开关断路器", "隔离开关 (IEC 60947-3 / GB/T 14048.3)"),
    (r"使用类别\s*[AB](?![A-Za-z0-9\-])", "选择性类别 A / B (GB/T 14048.2—2020 Cl. 3.1 / 4.4)"),
    (r"抽出式断路器", "抽屉式断路器 (GB/T 14048.2—2020 Cl. 2.5 / 3.7)"),
    (r"结构差异", "结构段 (GB/T 14048.2—2020 Cl. 2.1.2 / 7.1.6)"),
    (r"合闸涌流脱扣器", "接通电流脱扣器 (GB/T 14048.2—2020 Cl. 2.10)"),
]

STD_STATUTORY_ZH = [
    (r"闭合电磁铁|合闸电磁铁|释能电磁铁", "闭合脱扣器 (GB/T 14048.2—2020 Cl. 2.23)"),
    (r"万能式断路器", "空气断路器（分类：万能式） (GB/T 14048.2—2020 Cl. 2.7 / 3.3)"),
    (r"(?<!塑料外壳式)塑壳断路器", "塑料外壳式断路器 (GB/T 14048.2—2020 Cl. 2.6 / 3.3)"),
    (r"功率损耗", "功耗 (GB/T 14048.2—2020 附录 G)"),
    (r"(?<![\"“])分离位置|“分离”\s*位置", "隔离位置 (GB/T 14048.2—2020 Cl. 7.1.2；Cl. 2.5 称抽出位置)"),
    (r"\bInm\b", "壳架等级（GB/T 14048.2—2020 Cl. 2.1.1 / IEC 3.1.1 未定义 Inm 符号）"),
    (r"漏电保护", "剩余电流保护 (GB/T 14048.2—2020 附录 B/R)"),
    (r"漏电互感器", "电流传感器（GB/T 14048.2—2020 附录 B/M；产品扩展可用「剩余电流互感器」）"),
]

ED5_CLAUSE_RE = re.compile(
    r"(?:Cl\.|Clause)\s*(?:2\.(?:[1-9]|1\d|2[0-3])(?:\.\d+)?|4\.3\.[1-6](?:\.\d+)?|4\.[6-8](?:\.\d+)?|7\.[12](?:\.\d+)?|8\.3\.[1-9](?:\.\d+)?|8\.[45](?:\.\d+)?)\b",
    re.IGNORECASE,
)
ED5_GUARD_TAGS = ("60947-1", "60947-3", "14048.2", "GB/T", "GB ")


def load_units(source: str) -> dict:
    raw = sys.stdin.read() if source == "-" else Path(source).read_text(encoding="utf-8", errors="replace")
    stripped = raw.lstrip()
    if stripped.startswith("{"):
        try:
            obj = json.loads(raw)
            if isinstance(obj, dict) and obj.get("schema") == "chint-office-extract/v1":
                units = [(str(u["location"]), str(u["text"])) for u in obj.get("units", [])]
                return {
                    "source": obj.get("source", source),
                    "total": obj.get("total_units", len(units)),
                    "scanned": obj.get("scanned_units", len(units)),
                    "low_text_pages": obj.get("low_text_pages", []),
                    "units": units,
                }
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
    "STD_CONCEPT_ERROR",
    "GB_STATUTORY_ZH",
    "UNRESOLVED_SLOT",
}


def _severity(cat: str) -> str:
    return "HIGH" if cat in HIGH_CATS else "MEDIUM"


def scan_units(units: list[tuple[str, str]], dept: str, mode: str) -> list[dict]:
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

    pf_context_re = re.compile(r"(?i)power\s+factor|\bcos\s*[φϕ]?|功率因数")
    cat_a_re = re.compile(r"(?:Selectivity[ \t]+category[ \t]*[:：]?[ \t]*A\b|选择性类别[ \t]*[:：]?[ \t]*A\b)(?![ \t]*[/、,])", re.IGNORECASE)
    cat_b_re = re.compile(r"(?:Selectivity[ \t]+category[ \t]*[:：]?[ \t]*B\b|选择性类别[ \t]*[:：]?[ \t]*B\b|\bCategory[ \t]+B\b)", re.IGNORECASE)
    model_hdr_re = re.compile(r"^\s*(?:NX[AMF]\d|NM\d|NA\d)")
    st_re = re.compile(r"\bIsd\b")
    icw_re = re.compile(r"\bIcw\b")

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
            raw_bl = list(BLACKLIST_COMMON)
            if dept in {"acb", "all"}:
                raw_bl.extend(BLACKLIST_ACB)
            if dept in {"mccb", "all"}:
                raw_bl.extend(BLACKLIST_MCCB)
            bl: list[tuple[str, str]] = []
            seen_bl_pats: set[str] = set()
            for pat, fix in raw_bl:
                if pat not in seen_bl_pats:
                    seen_bl_pats.add(pat)
                    bl.append((pat, fix))
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
            for m in ED5_CLAUSE_RE.finditer(line):
                window = line[max(0, m.start() - 80):min(len(line), m.end() + 40)]
                if not any(tag in window for tag in ED5_GUARD_TAGS):
                    add(loc, "OBSOLETE_CLAUSE_ED5", m.group(0), "Use IEC 60947-2:2024 Ed. 6.0 clause numbers", line)
        else:
            for pat, fix in STD_CONCEPT_ZH:
                for m in re.finditer(pat, line):
                    add(loc, "STD_CONCEPT_ERROR", m.group(0), fix, line)
            for pat, fix in STD_STATUTORY_ZH:
                for m in re.finditer(pat, line):
                    add(loc, "GB_STATUTORY_ZH", m.group(0), fix, line)

        for m in re.finditer(r"\{\{[^}]+\}\}", line):
            add(loc, "UNRESOLVED_SLOT", m.group(0), "Resolve value slot from datasheet or rewrite qualitatively", line)

    type_fb_re = re.compile(r"\bType[ \t]+(?:F|B\+)\b", re.IGNORECASE)
    for items in blocks.values():
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
                win_blob = "\n".join(win_lines)
                m_st = st_re.search(win_blob)
                if m_st and not icw_re.search(win_blob):
                    add(
                        loc,
                        "TECH_CONTRADICTION",
                        f"{m_a.group(0)} + {m_st.group(0)}",
                        "Category A with intentional short-time delay (Isd) requires a declared Icw verified by Test Sequence IV (or Selectivity category B + IEC Table 2 / GB 表 3 Icw) (IEC 60947-2:2024 Cl. 5.4 / GB/T 14048.2—2020 Cl. 4.4)",
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
        "### Translation Lint Summary",
        "| Total units | Scanned | HIGH hits | MEDIUM hits |",
        "| :--- | :--- | :--- | :--- |",
        f"| {loaded['total']} | {loaded['scanned']} | {len(high)} | {len(med)} |",
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
    else:
        lines.append("| — | — | None | — |")
    return "\n".join(lines)


def run_self_test() -> int:
    mccb_dirty = [("P1:L1", "NXM-250S Plastic case breaker (IEC 60947-2, Cl. 4.3.5). Shunt Trip (MX). Type F, 380/400/415V.")]
    mccb_res = scan_units(mccb_dirty, "mccb", "en")
    mccb_hits = {f["category"] for f in mccb_res}
    assert {"BLACKLIST_CHINGLISH_UL", "COMPETITOR_CODE", "OBSOLETE_CLAUSE_ED5", "TECH_CONTRADICTION"} <= mccb_hits, mccb_hits

    acb_dirty = [("P2:L1", "Closed electromagnet (XF), Shunt Trip (MX), Earch current transformer, Closing Preparation Contact (PF), hole opener.")]
    acb_res = scan_units(acb_dirty, "acb", "en")
    assert any(f["match"] == "Closed electromagnet" for f in acb_res), acb_res
    assert any(f["match"] == "XF" for f in acb_res), acb_res

    slot_res = scan_units([("P2:L3", "Supply voltage {{Uc: V}}.")], "acb", "en")
    assert len(slot_res) == 1 and slot_res[0]["category"] == "UNRESOLVED_SLOT", slot_res

    zh_dirty = [("P3:L1", "抽出式断路器（使用类别 A）与塑壳断路器、万能式断路器在 400V 下测量功率损耗与结构差异，含合闸涌流脱扣器与闭合电磁铁。")]
    zh_res = scan_units(zh_dirty, "acb", "zh")
    assert {"STD_CONCEPT_ERROR", "GB_STATUTORY_ZH"} <= {f["category"] for f in zh_res}, zh_res
    assert any(f["match"] == "闭合电磁铁" for f in zh_res), zh_res

    ac22_ok = scan_units([("P3:L2", "CBI 按使用类别 AC-22 与使用类别AC-22 额定电流使用。")], "all", "zh")
    assert len(ac22_ok) == 0, ac22_ok
    use_cat_a = scan_units([("P3:L3", "选择错写为使用类别 A。")], "all", "zh")
    assert len(use_cat_a) == 1 and use_cat_a[0]["category"] == "STD_CONCEPT_ERROR", use_cat_a
    rcd_res = scan_units([("P3:L4", "提供漏电保护与漏电互感器。")], "all", "zh")
    assert any("剩余电流保护" in f["fix"] for f in rcd_res) and any("电流传感器" in f["fix"] for f in rcd_res), rcd_res

    contra_en = [("P7:L1", "Selectivity category: A"), ("P7:L2", "Short-time pick-up Isd = 6 Ir")]
    contra_zh = [("P8:L1", "选择性类别：A，短时动作电流 Isd = 6 Ir")]
    multi_model_page = [
        ("P9:L1", "NXM-125 Selectivity category: A"),
        ("P9:L2", "NXM-630E Selectivity category: B"),
        ("P9:L3", "Short-time pick-up Isd = 6 Ir; Icw 15 kA"),
    ]
    cat_a_with_icw = [
        ("P10:L1", "Selectivity category: A"),
        ("P10:L2", "Short-time pick-up Isd = 6 Ir; Icw = 5 kA (Seq IV)"),
    ]
    assert any(f["category"] == "TECH_CONTRADICTION" for f in scan_units(contra_en, "mccb", "en"))
    assert any(f["category"] == "TECH_CONTRADICTION" for f in scan_units(contra_zh, "mccb", "zh"))
    assert not any(f["category"] == "TECH_CONTRADICTION" for f in scan_units(multi_model_page, "mccb", "en"))
    assert not any(f["category"] == "TECH_CONTRADICTION" for f in scan_units(cat_a_with_icw, "mccb", "en"))

    # Relaxed character/spacing/hyphen/UK-spelling rules must produce ZERO findings
    relaxed_en = [("P4:L1", "Molded case circuit breaker 250A, color gray, under-voltage, draw-out, ENERGISED, 20000 times, 100% Icu, Icu 36kA.")]
    assert len(scan_units(relaxed_en, "all", "en")) == 0, scan_units(relaxed_en, "all", "en")
    relaxed_zh = [("P5:L1", "GB/T 14048.2—2020 Cl. 2.5 抽屉式断路器 400V -5℃~+40℃。")]
    assert len(scan_units(relaxed_zh, "all", "zh")) == 0, scan_units(relaxed_zh, "all", "zh")

    # Plural ordering instructions, dept-aware closing magnet, and Ed. 5 vs Ed. 6.0 / GB clause checks
    plural_res = scan_units([("P11:L1", "Please see Ordering instructions.")], "all", "en")
    assert len(plural_res) == 1 and plural_res[0]["match"].lower() == "ordering instructions", plural_res

    cm_mccb = scan_units([("P12:L1", "Equipped with closing magnet.")], "mccb", "en")
    cm_acb = scan_units([("P12:L2", "Equipped with closing magnet.")], "acb", "en")
    cm_all = scan_units([("P12:L3", "Equipped with closing magnet.")], "all", "en")
    assert len(cm_mccb) == 1 and cm_mccb[0]["fix"] == "Closing release", cm_mccb
    assert len(cm_acb) == 1 and cm_acb[0]["fix"] == "Closing release (CEM)", cm_acb
    assert len(cm_all) == 1 and cm_all[0]["fix"] == "Closing release (CEM)", cm_all

    for ed5_cl in ("Cl. 2.15.1", "Cl. 4.7.1", "Cl. 7.1.2", "Cl. 8.4.1"):
        ed5_hits = scan_units([("P13:L1", f"Tested per IEC 60947-2 {ed5_cl}.")], "all", "en")
        assert len(ed5_hits) == 1 and ed5_hits[0]["category"] == "OBSOLETE_CLAUSE_ED5", (ed5_cl, ed5_hits)
    for ok_txt in (
        "Compliant with IEC 60947-2:2024 Cl. 3.5, Cl. 4.4, Cl. 5.4, Cl. 8.1.2, Cl. 8.3, Cl. 9.3.11.",
        "GB Cl. 4.3.6.2 applies.",
        "GB/T 14048.2—2020 规定了断路器的额定极限短路分断能力与短路特性，参见 Cl. 4.3.6.2。",
    ):
        ok_hits = scan_units([("P13:L2", ok_txt)], "all", "en")
        assert len(ok_hits) == 0, (ok_txt, ok_hits)

    print("SELF-TEST PASS: 7/7 suites passed (EN/ZH/multi-model/substantive-only/relaxed-ortho-spacing).")
    return 0


def main() -> int:
    _ensure_utf8_stdio()
    parser = argparse.ArgumentParser(description="Pure-stdlib substantive translation linter for chint-translation")
    parser.add_argument("source", nargs="?", help="Text file, chint-office-extract/v1 JSON, or '-' for stdin")
    parser.add_argument("--dept", choices=["acb", "mccb", "all"], default="all")
    parser.add_argument("--mode", choices=["en", "zh"], default="en")
    parser.add_argument("--json", action="store_true", help="Output structured JSON")
    parser.add_argument("--report-md", action="store_true", help="Output deduplicated Markdown report")
    parser.add_argument("--chunk-size", type=int, default=0, help="Split units into chunks of N non-empty lines")
    parser.add_argument("--chunk-index", type=int, default=0, help="Inspect 1-based chunk K only")
    parser.add_argument("--chunks-info", action="store_true", help="Print chunk manifest with per-chunk hit counts")
    parser.add_argument("--exit-zero", action="store_true", help="Exit 0 even when findings exist")
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
                "chunks": manifest_chunks,
            }
            print(json.dumps(manifest, ensure_ascii=False, indent=2) if args.json else f"Total units: {manifest['total_units']} | Chunks: {manifest['total_chunks']}")
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
        clean_findings = strip_internal_fields(findings)
        report = {
            "source": loaded["source"],
            "dept": args.dept,
            "mode": args.mode,
            "total_units": loaded["total"],
            "scanned_units": loaded["scanned"],
            "finding_count": len(clean_findings),
            "high_count": sum(1 for f in clean_findings if f["severity"] == "HIGH"),
            "medium_count": sum(1 for f in clean_findings if f["severity"] != "HIGH"),
            "findings": clean_findings,
        }
        if chunk_meta:
            report["chunk"] = chunk_meta

        if args.json:
            print(json.dumps(report, ensure_ascii=False, indent=2))
        elif args.report_md:
            print(format_report_md(loaded, clean_findings))
        else:
            print(f"Scanned {report['scanned_units']}/{report['total_units']} units | findings={report['finding_count']} (HIGH={report['high_count']}, MEDIUM={report['medium_count']})")
            for f in clean_findings:
                print(f"[{f['location']}] ({f['severity']}/{f['category']}) '{f['match']}' -> {f['fix']}")
        return 0 if args.exit_zero else (1 if clean_findings else 0)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
