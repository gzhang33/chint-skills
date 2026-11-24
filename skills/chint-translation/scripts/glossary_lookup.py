#!/usr/bin/env python3
"""Pure-stdlib SSOT glossary & conversion lookup engine for chint-translation."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
STD_FILE = SKILL_ROOT / "references" / "iec_60947_2_standard.md"
ANNEX_FILE = SKILL_ROOT / "references" / "iec_annexes.md"
DEPT_DIR = SKILL_ROOT / "references" / "departments"


def _ensure_utf8_stdio() -> None:
    """Force UTF-8 on stdio streams so piped JSON/text works on Windows cp936 consoles."""
    for stream in (sys.stdin, sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8")
            except (AttributeError, OSError, ValueError):
                pass

GENERIC_EN_STOP = {
    "base", "fixed", "type", "class", "status", "tests", "mode", "unit",
    "duty", "items", "aux", "releases", "environment", "type tests",
}
SHORT_ALLOW = {"Ue", "Ui", "In", "Ir", "Ii", "Ig", "Is", "IB", "KL", "DD", "FD", "EB", "AX", "AL", "MI", "RU"}

ZH_LEGACY_ALIASES: dict[str, list[dict[str, str]]] = {
    "acb": [
        {"zh": "闭合电磁铁", "en": "Closing release (CEM)", "code": "CEM", "basis": "IEC 60947-2:2024 Cl. 3.19 / GB/T 14048.2—2020 Cl. 2.23; legacy ZH alias"},
        {"zh": "合闸电磁铁", "en": "Closing release (CEM)", "code": "CEM", "basis": "IEC 60947-2:2024 Cl. 3.19 / GB/T 14048.2—2020 Cl. 2.23; legacy ZH alias"},
        {"zh": "合闸线圈", "en": "Closing release (CEM)", "code": "CEM", "basis": "IEC 60947-2:2024 Cl. 3.19 / GB/T 14048.2—2020 Cl. 2.23; legacy ZH alias"},
        {"zh": "分励线圈", "en": "Shunt release (SHT)", "code": "SHT", "basis": "IEC 60947-2:2024 Cl. 5.7.1, 8.2.1.2.3 / GB/T 14048.2—2020 Cl. 4.7.1, 7.2.1.2.3; legacy ZH alias"},
        {"zh": "欠压脱扣器", "en": "Undervoltage release (UVT)", "code": "UVT", "basis": "IEC 60947-2:2024 Cl. 5.7.1, 8.2.1.2.2 / GB/T 14048.2—2020 Cl. 4.7.1, 7.2.1.2.2; legacy ZH alias"},
        {"zh": "开孔器", "en": "panel hole saw", "code": "", "basis": "audit_blacklist.md; legacy ZH alias"},
        {"zh": "飞弧距离", "en": "Arcing distance", "code": "", "basis": "Industry term (ref. IEC 60947-2:2024 Table 4 item 3.7 / GB/T 14048.2—2020 表 13 3.7); acb.md §3.1"},
        {"zh": "抽屉盒", "en": "Withdrawable cradle", "code": "", "basis": "IEC 60947-2:2024 Cl. 3.5; audit_blacklist.md"},
        {"zh": "分离位置", "en": "Disconnected position", "code": "", "basis": "IEC 60947-2:2024 Cl. 8.1.2; GB statutory: 隔离位置 (7.1.2) / 抽出位置 (2.5); audit_blacklist.md"},
        {"zh": "连接位置", "en": "Connected position", "code": "", "basis": "Industry term (IEC 8.1.2 only defines disconnected position); audit_blacklist.md"},
    ],
    "mccb": [
        {"zh": "漏电断路器", "en": "Circuit-breaker incorporating residual current protection (CBR)", "code": "CBR", "basis": "IEC 60947-2:2024 Annex B / GB/T 14048.2—2020 附录 B; audit_blacklist.md"},
        {"zh": "分励线圈", "en": "Shunt release (SHT)", "code": "SHT", "basis": "IEC 60947-2:2024 Cl. 5.7.1, 8.2.1.2.3 / GB/T 14048.2—2020 Cl. 4.7.1, 7.2.1.2.3; legacy ZH alias"},
        {"zh": "欠压脱扣器", "en": "Undervoltage release (UVT)", "code": "UVT", "basis": "IEC 60947-2:2024 Cl. 5.7.1, 8.2.1.2.2 / GB/T 14048.2—2020 Cl. 4.7.1, 7.2.1.2.2; legacy ZH alias"},
        {"zh": "热磁式过电流脱扣器", "en": "Thermal-magnetic overcurrent release (TM)", "code": "TM", "basis": "GB/T 14048.2—2020 Cl. 7.1.6 b), 8.3.3.2.3 b) (statutory: 热磁脱扣器); legacy ZH alias"},
        {"zh": "板后接线", "en": "Rear connection (HR / VR)", "code": "HR / VR", "basis": "mccb.md §3; audit_blacklist.md"},
    ],
    "common": [
        {"zh": "闭合电磁铁", "en": "Closing release", "code": "", "basis": "IEC 60947-2:2024 Cl. 3.19 / GB/T 14048.2—2020 Cl. 2.23; legacy ZH alias"},
        {"zh": "合闸电磁铁", "en": "Closing release", "code": "", "basis": "IEC 60947-2:2024 Cl. 3.19 / GB/T 14048.2—2020 Cl. 2.23; legacy ZH alias"},
        {"zh": "合闸线圈", "en": "Closing release", "code": "", "basis": "IEC 60947-2:2024 Cl. 3.19 / GB/T 14048.2—2020 Cl. 2.23; legacy ZH alias"},
        {"zh": "抽出式断路器", "en": "withdrawable circuit-breaker", "code": "", "basis": "IEC 60947-2:2024 Cl. 3.5; GB statutory: 抽屉式断路器"},
        {"zh": "塑壳断路器", "en": "moulded-case circuit-breaker", "code": "", "basis": "GB/T 14048.2—2020 Cl. 2.6; GB statutory: 塑料外壳式断路器"},
        {"zh": "万能式断路器", "en": "air circuit-breaker", "code": "", "basis": "GB/T 14048.2—2020 Cl. 2.7, 3.3"},
        {"zh": "功率损耗", "en": "power loss", "code": "", "basis": "IEC 60947-2:2024 Annex G; GB statutory: 功耗"},
        {"zh": "合闸涌流脱扣器", "en": "making-current release", "code": "", "basis": "IEC 60947-2:2024 Cl. 3.6; GB statutory: 接通电流脱扣器"},
        {"zh": "结构差异", "en": "construction break", "code": "", "basis": "IEC 60947-2:2024 Cl. 3.1.2; GB statutory: 结构段"},
        {"zh": "机械寿命", "en": "operational performance without current", "code": "", "basis": "IEC 60947-2:2024 Cl. 8.2.4.2; Annex B: operational performance capability; Annex M: mechanical & electrical endurance; Annex R: mechanical endurance"},
        {"zh": "电寿命", "en": "operational performance with current", "code": "", "basis": "IEC 60947-2:2024 Cl. 8.2.4.2; Annex B: operational performance capability; Annex M: mechanical & electrical endurance; Annex R: mechanical endurance"},
        {"zh": "电气寿命", "en": "operational performance with current", "code": "", "basis": "IEC 60947-2:2024 Cl. 8.2.4.2; Annex B: operational performance capability; Annex M: mechanical & electrical endurance; Annex R: mechanical endurance"},
        {"zh": "安装调试", "en": "installation and commissioning", "code": "", "basis": "audit_blacklist.md"},
        {"zh": "注意事项", "en": "operating precautions", "code": "", "basis": "audit_blacklist.md"},
        {"zh": "订货须知", "en": "ordering information", "code": "", "basis": "audit_blacklist.md"},
        {"zh": "误动作", "en": "false tripping", "code": "", "basis": "audit_blacklist.md"},
        {"zh": "未注公差", "en": "unspecified linear tolerance", "code": "", "basis": "audit_blacklist.md"},
        {"zh": "安装面", "en": "mounting surface", "code": "", "basis": "General engineering legacy ZH alias"},
        {"zh": "剩余电流保护", "en": "Residual current protection", "code": "", "basis": "IEC 60947-2:2024 Annex B, M / GB/T 14048.2—2020 附录 B, M"},
        {"zh": "临界直流负载电流", "en": "Critical DC load current", "code": "", "basis": "IEC 60947-2:2024 Cl. 9.3.10 / GB/T 14048.2—2020 Cl. 8.3.9"},
    ],
}


def clean_md(text: str) -> str:
    s = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    s = s.replace("**", "").replace("`", "").replace("\\|", "|")
    s = re.sub(r"\*([^*]+)\*", r"\1", s)
    def _latex(m: re.Match[str]) -> str:
        inner = m.group(1)
        inner = re.sub(r"\\Delta\s*", "Δ", inner)
        inner = re.sub(r"\\geq?\b", "≥", inner)
        inner = re.sub(r"\\leq?\b", "≤", inner)
        inner = re.sub(r"\\pm\b", "±", inner)
        inner = re.sub(r"\\times\b", "×", inner)
        inner = re.sub(r"\\circ\b", "°", inner)
        inner = inner.replace(r"\,", " ")
        inner = re.sub(r"\\(?:text|mathrm)\{([^}]+)\}", r"\1", inner)
        inner = re.sub(r"_\{([^}]+)\}", r"\1", inner)
        inner = re.sub(r"\^\{([^}]+)\}", r"\1", inner)
        return re.sub(r"[{}\\]", "", inner)
    s = re.sub(r"\$([^$]+)\$", _latex, s)
    return re.sub(r"\s+", " ", s).strip()


def _strip_gb_gap_note(text: str) -> str:
    cleaned = re.sub(r"\s*[（(][^）)]*暂未收录[^）)]*[)）]", "", text)
    return re.sub(r"\s+", " ", cleaned).strip()


def _split_md_row(line: str) -> list[str]:
    """Split a Markdown pipe-table row respecting inline code backticks and backslash escapes."""
    s = line.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|") and not s.endswith(r"\|"):
        s = s[:-1]
    cells: list[str] = []
    buf: list[str] = []
    in_code = False
    i = 0
    while i < len(s):
        ch = s[i]
        if ch == "\\" and i + 1 < len(s) and s[i + 1] in {"|", "`"}:
            buf.append(s[i : i + 2])
            i += 2
            continue
        if ch == "`":
            in_code = not in_code
            buf.append(ch)
        elif ch == "|" and not in_code:
            cells.append("".join(buf).strip())
            buf = []
        else:
            buf.append(ch)
        i += 1
    cells.append("".join(buf).strip())
    return cells


def split_top_level(text: str, seps: str = "/;；") -> list[str]:
    parts: list[str] = []
    buf: list[str] = []
    depth = 0
    for ch in text:
        if ch in "(（[":
            depth += 1
        elif ch in ")）]" and depth > 0:
            depth -= 1
        if depth == 0 and ch in seps:
            piece = "".join(buf).strip(" ;；，,")
            if piece:
                parts.append(piece)
            buf = []
        else:
            buf.append(ch)
    tail = "".join(buf).strip(" ;；，,")
    if tail:
        parts.append(tail)
    return parts


def split_keys(text: str, is_zh: bool) -> list[str]:
    cleaned = clean_md(text)
    if not cleaned or cleaned in {"—", "-", "N/A"}:
        return []
    cleaned = re.sub(r"[（(][^）)]*暂未收录[^）)]*[)）]", "", cleaned).strip()
    parts = split_top_level(cleaned, seps="/;；")
    keys: list[str] = []
    for p in parts:
        keys.append(p)
        bare = re.sub(r"\s*[（(][^）)]+[)）]", "", p).strip()
        if bare and bare != p:
            keys.append(bare)
        if is_zh and "：" in p:
            head = p.split("：", 1)[0].strip()
            if len(head) >= 2:
                keys.append(head)
        elif not is_zh:
            for abbr in re.findall(r"(?<=\()([A-Z]{3,6})(?:s(?=\)))?(?=[\s);,)])", p):
                keys.append(abbr)
    out: list[str] = []
    for k in keys:
        if k in {"—", "-", "N/A"}:
            continue
        if is_zh:
            if len(k) >= 2 and re.search(r"[\u4e00-\u9fff]", k):
                out.append(k)
        else:
            if k.lower() in GENERIC_EN_STOP:
                continue
            if len(k) >= 3 or k in SHORT_ALLOW:
                out.append(k)
    return list(dict.fromkeys(out))


def extract_rows_from_md(md_path: Path, role: str) -> list[dict]:
    entries: list[dict] = []
    if not md_path.exists():
        return entries
    lines = md_path.read_text(encoding="utf-8").splitlines()
    skip_section = False
    headers: list[str] = []
    in_table = False

    def flush_reset():
        nonlocal headers, in_table
        headers = []
        in_table = False

    for line in lines:
        s = line.strip()
        if s.startswith("## "):
            flush_reset()
            skip_section = any(k in s for k in ("Blacklist", "Guardrails"))
            continue
        if s.startswith("### "):
            flush_reset()
            continue
        if skip_section:
            continue
        if not s.startswith("|"):
            flush_reset()
            continue
        cells = _split_md_row(s)
        if all(re.fullmatch(r":?-{2,}:?", c.replace(" ", "")) for c in cells if c):
            continue
        if not in_table:
            headers = [clean_md(c).lower() for c in cells]
            in_table = True
            continue
        if len(cells) < 2 or all(c in {"—", "-", ""} for c in cells):
            continue

        zh_col = en_col = code_col = clause_col = note_col = None
        for idx, h in enumerate(headers):
            if "chinese" in h:
                zh_col = idx
            elif "english" in h:
                en_col = idx
            elif "code" in h or ("symbol" in h and "note" not in h):
                if code_col is None:
                    code_col = idx
            elif "note" in h or "meaning" in h or "rule" in h or "function" in h:
                note_col = idx
            elif "clause" in h or "2024" in h:
                clause_col = idx
            elif "slot" in h:
                note_col = idx

        if zh_col is None or en_col is None or zh_col >= len(cells) or en_col >= len(cells):
            continue

        zh_raw, en_raw = cells[zh_col], cells[en_col]
        code_raw = cells[code_col] if code_col is not None and code_col < len(cells) else ""
        clause_raw = cells[clause_col] if clause_col is not None and clause_col < len(cells) else ""
        note_raw = cells[note_col] if note_col is not None and note_col < len(cells) else ""

        zh_full = clean_md(zh_raw)
        en_full = clean_md(en_raw)
        if not zh_full or not en_full or zh_full in {"—", "-"} or en_full in {"—", "-"}:
            continue
        if zh_full.startswith("(") or zh_full.startswith("（"):
            continue

        base_basis_parts = [p for p in [clean_md(clause_raw), clean_md(note_raw)] if p and p != "—"]
        base_basis = "; ".join(base_basis_parts)
        if len(base_basis) > 260:
            base_basis = base_basis[:257].rstrip(" ;,") + "..."

        zh_slash = split_top_level(zh_full, seps="/")
        en_slash = split_top_level(en_full, seps="/")
        code_clean = clean_md(code_raw)
        if len(code_clean) > 28 and "/" not in code_clean:
            code_clean = ""
        code_slash = split_top_level(code_clean, seps="/") if code_clean and code_clean not in {"—", "-"} else []
        if len(zh_slash) > 1 and len(zh_slash) == len(en_slash):
            pairs = [(z, e) for z, e in zip(zh_slash, en_slash)]
        else:
            pairs = [(zh_full, en_full)]

        for idx, (z_txt, e_txt) in enumerate(pairs):
            pair_code = code_slash[idx] if len(pairs) > 1 and len(code_slash) == len(pairs) else code_clean
            if pair_code in {"—", "-"}:
                pair_code = ""
            pair_gb_gap = ("暂未收录" in z_txt) or ("暂未收录" in e_txt)
            clean_z = _strip_gb_gap_note(z_txt)
            clean_e = _strip_gb_gap_note(e_txt)
            pair_basis = base_basis
            if pair_gb_gap and "暂未收录" not in pair_basis:
                pair_basis = f"GB/T 14048.2—2020 暂未收录（IEC 2024 新增）; {pair_basis}".strip("; ")
            zh_keys = split_keys(clean_z, is_zh=True)
            en_keys = split_keys(clean_e, is_zh=False)
            if pair_code:
                for ck in split_keys(pair_code, is_zh=False):
                    if re.fullmatch(r"[A-Za-z][A-Za-z0-9Δ_-]{1,7}", ck) and ck.lower() not in GENERIC_EN_STOP:
                        en_keys.append(ck)
            entries.append({
                "role": role,
                "source_file": md_path.name,
                "zh": clean_z,
                "en": clean_e,
                "code": pair_code,
                "gb_missing": pair_gb_gap,
                "basis": pair_basis,
                "zh_keys": list(dict.fromkeys(zh_keys)),
                "en_keys": list(dict.fromkeys(en_keys)),
            })
    return entries


def _alias_entries(scope: str, role: str) -> list[dict]:
    out: list[dict] = []
    for item in ZH_LEGACY_ALIASES.get(scope, []):
        out.append({
            "role": role,
            "source_file": "zh-legacy-alias",
            "zh": item["zh"],
            "en": item["en"],
            "code": item["code"],
            "gb_missing": False,
            "basis": item["basis"],
            "zh_keys": [item["zh"]],
            "en_keys": [],
        })
    return out


def build_glossary(dept: str, region_path: str | None) -> list[dict]:
    entries: list[dict] = []
    if dept in {"acb", "all"}:
        entries.extend(extract_rows_from_md(DEPT_DIR / "acb.md", "dept:acb"))
    if dept in {"mccb", "all"}:
        entries.extend(extract_rows_from_md(DEPT_DIR / "mccb.md", "dept:mccb"))
    entries.extend(extract_rows_from_md(STD_FILE, "standard"))
    if ANNEX_FILE.exists():
        entries.extend(extract_rows_from_md(ANNEX_FILE, "standard"))
    if region_path:
        rp = Path(region_path)
        if not rp.exists():
            raise FileNotFoundError(f"Region override file not found: {region_path}")
        entries.extend(extract_rows_from_md(rp, "region"))
    if dept in {"acb", "all"}:
        entries.extend(_alias_entries("acb", "alias:dept"))
    if dept in {"mccb", "all"}:
        entries.extend(_alias_entries("mccb", "alias:dept"))
    entries.extend(_alias_entries("common", "alias:common"))
    return entries


def load_text_units(source: str) -> tuple[str, list[tuple[str, str]]]:
    raw = sys.stdin.read() if source == "-" else Path(source).read_text(encoding="utf-8", errors="replace")
    stripped = raw.lstrip()
    if stripped.startswith("{"):
        try:
            obj = json.loads(raw)
            if isinstance(obj, dict) and obj.get("schema") == "chint-office-extract/v1":
                units = [(str(u["location"]), str(u["text"])) for u in obj.get("units", [])]
                return str(obj.get("source", source)), units
        except json.JSONDecodeError:
            pass
    lines = raw.splitlines()
    return source, [(f"Line {i}", l) for i, l in enumerate(lines, 1) if l.strip()]


def build_chunks(units: list[tuple[str, str]], chunk_size: int) -> list[list[tuple[str, str]]]:
    if chunk_size <= 0 or not units:
        return [units] if units else []
    return [units[i:i + chunk_size] for i in range(0, len(units), chunk_size)]


def _role_prio(role: str) -> int:
    if role == "region" or role.startswith("dept"):
        return 0
    if role == "standard":
        return 1
    if role == "alias:dept":
        return 2
    return 3


def _span_covered(start: int, end: int, covered: list[tuple[int, int]]) -> bool:
    return any(cs <= start and end <= ce for cs, ce in covered)


def lookup_terms(units: list[tuple[str, str]], entries: list[dict], direction: str) -> dict:
    full_text = "\n".join(t for _, t in units)
    matched: list[dict] = []
    seen_targets: set[tuple[str, str]] = set()
    covered_spans: list[tuple[int, int]] = []

    if direction == "zh2en":
        candidates: list[tuple[str, dict]] = []
        for e in entries:
            for k in e["zh_keys"]:
                candidates.append((k, e))
        candidates.sort(key=lambda x: (-len(x[0]), _role_prio(x[1]["role"])))
        seen_keys: set[str] = set()
        for key, e in candidates:
            if key in seen_keys:
                continue
            pat = re.escape(key)
            hits = [m for m in re.finditer(pat, full_text, re.IGNORECASE) if not _span_covered(m.start(), m.end(), covered_spans)]
            if hits:
                sig = (key, e["en"])
                if sig in seen_targets:
                    continue
                seen_keys.add(key)
                seen_targets.add(sig)
                for h in hits:
                    covered_spans.append((h.start(), h.end()))
                locs = [loc for loc, txt in units if re.search(pat, txt, re.IGNORECASE)][:3]
                matched.append({
                    "matched_source": hits[0].group(0),
                    "target": e["en"],
                    "statutory_zh": e["zh"],
                    "code": e["code"],
                    "basis": e["basis"],
                    "source_file": e["source_file"],
                    "locations": locs,
                })

        wan_covered: list[tuple[int, int]] = []
        range_pat = re.compile(r"(\d+(?:\.\d+)?)\s*万?\s*[~～\-–]\s*(\d+(?:\.\d+)?)\s*万\s*次")
        range_seen: dict[tuple[int, int], tuple[str, list[str]]] = {}
        for loc, txt in units:
            for m in range_pat.finditer(txt):
                v1 = int(round(float(m.group(1)) * 10000))
                v2 = int(round(float(m.group(2)) * 10000))
                rk = (v1, v2)
                if rk not in range_seen:
                    range_seen[rk] = (m.group(0), [loc])
                elif len(range_seen[rk][1]) < 3 and loc not in range_seen[rk][1]:
                    range_seen[rk][1].append(loc)
        for (v1, v2), (raw_expr, locs) in range_seen.items():
            matched.append({
                "matched_source": raw_expr,
                "target": f"{v1:,} to {v2:,} operating cycles",
                "statutory_zh": "操作循环次数",
                "code": "",
                "basis": "IEC 60947-2:2024 Cl. 8.2.4.2, Table 7 / GB/T 14048.2—2020 Cl. 7.2.4.2, 表 8",
                "source_file": "numeric-rule",
                "locations": locs,
            })

        single_pat = re.compile(r"(\d+(?:\.\d+)?)\s*万\s*次")
        wan_seen: dict[int, tuple[str, list[str]]] = {}
        for loc, txt in units:
            rcov = [(m.start(), m.end()) for m in range_pat.finditer(txt)]
            for m in single_pat.finditer(txt):
                if _span_covered(m.start(), m.end(), rcov):
                    continue
                val = int(round(float(m.group(1)) * 10000))
                if val not in wan_seen:
                    wan_seen[val] = (m.group(0), [loc])
                elif len(wan_seen[val][1]) < 3 and loc not in wan_seen[val][1]:
                    wan_seen[val][1].append(loc)
        for val, (raw_expr, locs) in wan_seen.items():
            matched.append({
                "matched_source": raw_expr,
                "target": f"{val:,} operating cycles",
                "statutory_zh": "操作循环次数",
                "code": "",
                "basis": "IEC 60947-2:2024 Cl. 8.2.4.2, Table 7 / GB/T 14048.2—2020 Cl. 7.2.4.2, 表 8",
                "source_file": "numeric-rule",
                "locations": locs,
            })
    else:
        candidates = []
        for e in entries:
            for k in e["en_keys"]:
                candidates.append((k, e))
        candidates.sort(key=lambda x: (-len(x[0]), _role_prio(x[1]["role"])))
        seen_en_keys: set[str] = set()
        for key, e in candidates:
            k_low = key.lower()
            if k_low in seen_en_keys:
                continue
            pat = rf"(?<![A-Za-z0-9]){re.escape(key)}(?![A-Za-z0-9])"
            hits = [m for m in re.finditer(pat, full_text, re.IGNORECASE) if not _span_covered(m.start(), m.end(), covered_spans)]
            if hits:
                sig = (e["zh"], e["en"])
                if sig in seen_targets:
                    continue
                seen_en_keys.add(k_low)
                seen_targets.add(sig)
                for h in hits:
                    covered_spans.append((h.start(), h.end()))
                locs = [loc for loc, txt in units if re.search(pat, txt, re.IGNORECASE)][:3]
                basis = e["basis"]
                if e["gb_missing"] and "GB/T 14048.2—2020 暂未收录" not in basis:
                    basis = f"GB/T 14048.2—2020 暂未收录; {basis}".strip("; ")
                matched.append({
                    "matched_source": hits[0].group(0),
                    "target": e["zh"],
                    "canonical_en": e["en"],
                    "gb_missing": e["gb_missing"],
                    "basis": basis,
                    "source_file": e["source_file"],
                    "locations": locs,
                })

    return {"direction": direction, "match_count": len(matched), "matches": matched}


def run_self_test() -> int:
    import tempfile

    acb_entries = build_glossary("acb", None)
    assert all(len(e["code"]) <= 28 or "/" in e["code"] for e in acb_entries), [e for e in acb_entries if len(e["code"]) > 28]
    ax_entry = next(e for e in acb_entries if e["code"] == "AX")
    assert "O/I" in ax_entry["basis"], ax_entry
    assert lookup_terms([("P0:L1", "Series fuse per line pole.")], acb_entries, "en2zh")["match_count"] == 0

    zh_sample = [("P1:L1", "分励脱扣器、闭合电磁铁、抽屉式断路器、开孔器与合闸准备就绪触点，机械操作 2万次，电寿命 1万~2万次。"), ("P1:L2", "另测 2 万次。")]
    r_zh = lookup_terms(zh_sample, acb_entries, "zh2en")
    targets_zh = " | ".join(m["target"] for m in r_zh["matches"])
    sources_zh = [m["matched_source"] for m in r_zh["matches"]]
    assert "Shunt release (SHT)" in targets_zh, targets_zh
    assert "Closing release (CEM)" in targets_zh, targets_zh
    assert "panel hole saw" in targets_zh, targets_zh
    assert "withdrawable air circuit-breaker" in targets_zh.lower(), targets_zh
    assert "断路器" not in sources_zh, sources_zh
    assert "Ready-to-close contact (SPC)" in targets_zh, targets_zh
    assert "20,000 operating cycles" in targets_zh, targets_zh
    assert "10,000 to 20,000 operating cycles" in targets_zh, targets_zh
    two_wan = [m for m in r_zh["matches"] if m["target"] == "20,000 operating cycles"]
    assert len(two_wan) == 1 and two_wan[0]["locations"] == ["P1:L1", "P1:L2"], two_wan
    assert "Withdrawable interphase barrier (DD)" not in targets_zh, targets_zh
    shunt_matches = [m for m in r_zh["matches"] if m["matched_source"] == "分励脱扣器"]
    assert len(shunt_matches) == 1 and shunt_matches[0]["target"] == "Shunt release (SHT)", shunt_matches

    assert "≥ ± 10 K" == clean_md(r"$\ge \pm 10\text{ K}$"), clean_md(r"$\ge \pm 10\text{ K}$")

    mccb_entries = build_glossary("mccb", None)
    en_sample = [("P2:L1", "Moulded-case circuit-breaker (MCCB) Icu1 18 kA rms; ultimate short-circuit breaking capacity; power loss 42 W.")]
    r_en = lookup_terms(en_sample, mccb_entries, "en2zh")
    targets_en = " | ".join(f"{m['target']} [{m['basis']}]" for m in r_en["matches"])
    assert "塑料外壳式断路器" in targets_en, targets_en
    assert "功耗" in targets_en, targets_en
    icu1_hit = next(m for m in r_en["matches"] if "单极极限" in m["target"])
    assert icu1_hit["target"] == "相-中性线交流电压下的额定单极极限短路分断能力", icu1_hit
    assert "暂未收录" not in icu1_hit["target"] and "暂未收录" in icu1_hit["basis"] and icu1_hit["gb_missing"] is True, icu1_hit
    ult_hit = next(m for m in r_en["matches"] if m["target"] == "极限短路分断能力")
    assert ult_hit["gb_missing"] is False, ult_hit

    cbi_hit = lookup_terms([("P2:L2", "CBI and Circuit-breakers not fulfilling the requirements for overcurrent protection (CBIs)")], mccb_entries, "en2zh")
    assert cbi_hit["match_count"] == 1 and cbi_hit["matches"][0]["gb_missing"] is False, cbi_hit
    annex_abbr = lookup_terms([("P2:L4", "CBR, CBI, MRCD, ICB, CBAR and PLC")], mccb_entries, "en2zh")
    assert {m["matched_source"].upper() for m in annex_abbr["matches"]} == {"CBR", "CBI", "MRCD", "ICB", "CBAR", "PLC"}, annex_abbr

    ext_hit = lookup_terms([("P2:L3", "Basic distribution trip unit and Thermal memory")], acb_entries, "en2zh")
    ext_map = {m["matched_source"]: m for m in ext_hit["matches"]}
    assert ext_map["Basic distribution trip unit"]["target"] == "基本配电型脱扣器" and ext_map["Basic distribution trip unit"]["gb_missing"] is False, ext_map
    assert "CHINT" in ext_map["Basic distribution trip unit"]["basis"], ext_map["Basic distribution trip unit"]
    assert ext_map["Thermal memory"]["target"] == "热记忆" and ext_map["Thermal memory"]["gb_missing"] is False, ext_map
    assert "Industry" in ext_map["Thermal memory"]["basis"], ext_map["Thermal memory"]

    r_codes = lookup_terms([("P3:L1", "UVT, PSU, ETU, MCR, ZSI and ACB")], acb_entries, "en2zh")
    code_map = {m["matched_source"].upper(): m["target"] for m in r_codes["matches"]}
    assert code_map.get("UVT") == "欠电压脱扣器", r_codes
    assert code_map.get("PSU") == "电源模块", r_codes
    assert code_map.get("ETU") == "电子脱扣器", r_codes
    assert code_map.get("MCR") == "接通电流脱扣器", r_codes
    assert code_map.get("ZSI") == "区域选择性联锁", r_codes
    assert code_map.get("ACB") == "空气断路器（分类：万能式）", r_codes

    r_mccb_codes = lookup_terms([("P3:L2", "MCCB with TM-D release")], mccb_entries, "en2zh")
    mc_map = {m["matched_source"].upper(): m["target"] for m in r_mccb_codes["matches"]}
    assert mc_map.get("MCCB") == "塑料外壳式断路器", r_mccb_codes
    assert mc_map.get("TM-D") == "热磁脱扣器", r_mccb_codes

    try:
        build_glossary("acb", "/nonexistent_region_path_xyz.md")
        raise AssertionError("Expected FileNotFoundError for missing --region")
    except FileNotFoundError:
        pass

    region_tpl_entries = extract_rows_from_md(SKILL_ROOT / "references" / "regions" / "_region_template.md", "region")
    assert len(region_tpl_entries) >= 1, region_tpl_entries

    chunks = build_chunks([("P1:L1", "a"), ("P1:L2", "b"), ("P1:L3", "c")], 2)
    assert len(chunks) == 2 and len(chunks[1]) == 1

    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as tf:
        json.dump({"schema": "chint-office-extract/v1", "source": "cat.pdf", "total_units": 1, "scanned_units": 1, "low_text_pages": [], "units": [{"location": "P1:L1", "text": "分励脱扣器"}]}, tf)
        tpath = Path(tf.name)
    try:
        _, units = load_text_units(str(tpath))
        r_pipe = lookup_terms(units, acb_entries, "zh2en")
        assert any("Shunt release (SHT)" in m["target"] for m in r_pipe["matches"]), r_pipe
    finally:
        tpath.unlink(missing_ok=True)

    print("SELF-TEST PASS: glossary_lookup.py verified (clean table cols, span dedup, range 万次, chunking, missing --region error).")
    return 0


def main() -> int:
    _ensure_utf8_stdio()
    parser = argparse.ArgumentParser(description="SSOT Markdown glossary lookup for chint-translation")
    parser.add_argument("source", nargs="?", help="Text file, chint-office-extract/v1 JSON, or '-'")
    parser.add_argument("--dir", choices=["zh2en", "en2zh"], default="zh2en")
    parser.add_argument("--dept", choices=["acb", "mccb", "all"], default="all")
    parser.add_argument("--region", help="Optional isolated region override Markdown path")
    parser.add_argument("--chunk-size", type=int, default=0, help="Split units into chunks of N non-empty lines")
    parser.add_argument("--chunk-index", type=int, default=0, help="Inspect 1-based chunk K only")
    parser.add_argument("--json", action="store_true", help="Emit JSON output")
    parser.add_argument("--self-test", action="store_true", help="Run built-in verification suite")
    args = parser.parse_args()

    try:
        if args.self_test:
            return run_self_test()
        if not args.source:
            parser.error("source is required unless --self-test is set")

        src_name, units = load_text_units(args.source)
        active_units = units
        chunk_meta = None
        if args.chunk_index > 0:
            csize = args.chunk_size if args.chunk_size > 0 else 50
            chunks = build_chunks(units, csize)
            if args.chunk_index > len(chunks):
                raise ValueError(f"--chunk-index {args.chunk_index} out of range 1..{len(chunks)}")
            active_units = chunks[args.chunk_index - 1]
            chunk_meta = {"index": args.chunk_index, "total_chunks": len(chunks), "unit_count": len(active_units)}

        entries = build_glossary(args.dept, args.region)
        res = lookup_terms(active_units, entries, args.dir)
        res["source"] = src_name
        res["dept"] = args.dept
        if chunk_meta:
            res["chunk"] = chunk_meta

        if args.json:
            print(json.dumps(res, ensure_ascii=False, indent=2))
        else:
            print("| Source Match | Canonical Target | Clause / Standard Basis | Origin | Locations |")
            print("| :--- | :--- | :--- | :--- | :--- |")
            for m in res["matches"]:
                locs = ", ".join(m["locations"])
                print(f"| `{m['matched_source']}` | **{m['target']}** | {m['basis']} | `{m['source_file']}` | `{locs}` |")
        return 0
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())