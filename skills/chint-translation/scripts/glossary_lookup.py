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
DEPT_DIR = SKILL_ROOT / "references" / "departments"

GENERIC_EN_STOP = {
    "base", "fixed", "type", "class", "status", "tests", "mode", "unit",
    "duty", "items", "aux", "releases", "environment", "type tests",
}
SHORT_ALLOW = {"Ue", "Ui", "In", "Ir", "Ii", "Ig", "Is", "IB", "KL", "DD", "FD", "EB", "AX", "AL", "MI", "RU"}


def clean_md(text: str) -> str:
    s = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    s = s.replace("**", "").replace("`", "")
    s = re.sub(r"\*([^*]+)\*", r"\1", s)
    def _latex(m: re.Match[str]) -> str:
        inner = m.group(1)
        inner = inner.replace(r"\Delta ", "Δ").replace(r"\Delta", "Δ")
        inner = re.sub(r"_\{([^}]+)\}", r"\1", inner)
        inner = re.sub(r"\^\{([^}]+)\}", r"\1", inner)
        return re.sub(r"[{}\\]", "", inner)
    s = re.sub(r"\$([^$]+)\$", _latex, s)
    return re.sub(r"\s+", " ", s).strip()


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
    # Remove trailing editorial notes like *(国标 2020 暂未收录...)*
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
            skip_section = any(k in s for k in ("Blacklist", "Guardrails", "Custom Extensions"))
            continue
        if s.startswith("### "):
            flush_reset()
            continue
        if skip_section:
            continue
        if not s.startswith("|"):
            flush_reset()
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
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
            elif "code" in h:
                code_col = idx
            elif "symbol" in h:
                if code_col is None:
                    code_col = idx
            elif "clause" in h or "2024" in h:
                clause_col = idx
            elif "note" in h or "meaning" in h or "rule" in h or "function" in h:
                note_col = idx

        if zh_col is None or en_col is None or zh_col >= len(cells) or en_col >= len(cells):
            continue

        zh_raw, en_raw = cells[zh_col], cells[en_col]
        code_raw = cells[code_col] if code_col is not None and code_col < len(cells) else ""
        clause_raw = cells[clause_col] if clause_col is not None and clause_col < len(cells) else ""
        note_raw = cells[note_col] if note_col is not None and note_col < len(cells) else ""

        zh_full = clean_md(zh_raw)
        en_full = clean_md(en_raw)
        if not zh_full or not en_full or zh_full == "—":
            continue

        row_blob = " | ".join([zh_raw, en_raw, clause_raw, note_raw])
        gb_gap = "暂未收录" in row_blob
        basis_parts = [p for p in [clean_md(clause_raw), clean_md(note_raw)] if p and p != "—"]
        basis = "; ".join(basis_parts)[:140]
        if gb_gap and "GB/T 14048.2—2020 暂未收录" not in basis:
            basis = f"GB/T 14048.2—2020 暂未收录; {basis}".strip("; ")

        # Handle paired top-level slash cells cleanly when counts match (e.g. "抽屉式 / 固定式" <-> "Withdrawable / Fixed")
        zh_slash = split_top_level(zh_full, seps="/")
        en_slash = split_top_level(en_full, seps="/")
        code_clean = clean_md(code_raw)
        if len(zh_slash) > 1 and len(zh_slash) == len(en_slash):
            pairs = [(z, e) for z, e in zip(zh_slash, en_slash)]
        else:
            pairs = [(zh_full, en_full)]

        for z_txt, e_txt in pairs:
            zh_keys = split_keys(z_txt, is_zh=True)
            en_keys = split_keys(e_txt, is_zh=False)
            if code_clean and code_clean not in {"—", "-"}:
                for ck in split_keys(code_clean, is_zh=False):
                    if len(ck) >= 2 and ck not in GENERIC_EN_STOP:
                        en_keys.append(ck)
            entries.append({
                "role": role,
                "source_file": md_path.name,
                "zh": z_txt,
                "en": e_txt,
                "code": code_clean if code_clean not in {"—", "-"} else "",
                "gb_missing": gb_gap,
                "basis": basis,
                "zh_keys": list(dict.fromkeys(zh_keys)),
                "en_keys": list(dict.fromkeys(en_keys)),
            })
    return entries


def build_glossary(dept: str, region_path: str | None) -> list[dict]:
    entries: list[dict] = []
    if dept in {"acb", "all"}:
        entries.extend(extract_rows_from_md(DEPT_DIR / "acb.md", "dept:acb"))
    if dept in {"mccb", "all"}:
        entries.extend(extract_rows_from_md(DEPT_DIR / "mccb.md", "dept:mccb"))
    entries.extend(extract_rows_from_md(STD_FILE, "standard"))
    if region_path:
        entries.extend(extract_rows_from_md(Path(region_path), "region"))
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


def lookup_terms(units: list[tuple[str, str]], entries: list[dict], direction: str) -> dict:
    full_text = "\n".join(t for _, t in units)
    matched: list[dict] = []
    seen_targets: set[tuple[str, str]] = set()

    if direction == "zh2en":
        candidates: list[tuple[str, dict]] = []
        for e in entries:
            for k in e["zh_keys"]:
                candidates.append((k, e))
        candidates.sort(key=lambda x: (-len(x[0]), 0 if x[1]["role"].startswith("dept") else 1))
        for key, e in candidates:
            pat = re.escape(key)
            m = re.search(pat, full_text, re.IGNORECASE)
            if m:
                sig = (key, e["en"])
                if sig in seen_targets:
                    continue
                seen_targets.add(sig)
                locs = [loc for loc, txt in units if re.search(pat, txt, re.IGNORECASE)][:3]
                matched.append({
                    "matched_source": m.group(0),
                    "target": e["en"],
                    "statutory_zh": e["zh"],
                    "code": e["code"],
                    "basis": e["basis"],
                    "source_file": e["source_file"],
                    "locations": locs,
                })
        # Deterministic N 万次 -> operating cycles numeric conversion hints
        wan_seen: set[str] = set()
        for loc, txt in units:
            for m in re.finditer(r"(\d+(?:\.\d+)?)\s*万\s*次", txt):
                raw_expr = m.group(0)
                if raw_expr in wan_seen:
                    continue
                wan_seen.add(raw_expr)
                val = int(round(float(m.group(1)) * 10000))
                matched.append({
                    "matched_source": raw_expr,
                    "target": f"{val:,} operating cycles",
                    "statutory_zh": "操作循环次数",
                    "code": "",
                    "basis": "IEC 60947-2:2024 Cl. 8.2.4.2, Table 7 / GB/T 14048.2—2020 Cl. 7.2.4.2",
                    "source_file": "numeric-rule",
                    "locations": [loc],
                })
    else:
        candidates = []
        for e in entries:
            for k in e["en_keys"]:
                candidates.append((k, e))
        candidates.sort(key=lambda x: (-len(x[0]), 0 if x[1]["role"].startswith("dept") else 1))
        for key, e in candidates:
            pat = rf"(?<![A-Za-z0-9]){re.escape(key)}(?![A-Za-z0-9])"
            m = re.search(pat, full_text, re.IGNORECASE)
            if m:
                sig = (e["zh"], e["en"])
                if sig in seen_targets:
                    continue
                seen_targets.add(sig)
                locs = [loc for loc, txt in units if re.search(pat, txt, re.IGNORECASE)][:3]
                basis = e["basis"]
                if e["gb_missing"] and "GB/T 14048.2—2020 暂未收录" not in basis:
                    basis = f"GB/T 14048.2—2020 暂未收录; {basis}".strip("; ")
                matched.append({
                    "matched_source": m.group(0),
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
    zh_sample = [("P1:L1", "分励脱扣器、闭合脱扣器、抽屉式断路器与合闸准备就绪触点，机械操作 2 万次。")]
    r_zh = lookup_terms(zh_sample, acb_entries, "zh2en")
    targets_zh = " | ".join(m["target"] for m in r_zh["matches"])
    assert "Shunt release (SHT)" in targets_zh, targets_zh
    assert "Closing release (CEM)" in targets_zh, targets_zh
    assert "withdrawable circuit-breaker" in targets_zh.lower(), targets_zh
    assert "Ready-to-close contact (SPC)" in targets_zh, targets_zh
    assert "20,000 operating cycles" in targets_zh, targets_zh

    mccb_entries = build_glossary("mccb", None)
    en_sample = [("P2:L1", "Moulded-case circuit-breaker (MCCB) Icu1 18 kA rms; power loss 42 W.")]
    r_en = lookup_terms(en_sample, mccb_entries, "en2zh")
    targets_en = " | ".join(f"{m['target']} [{m['basis']}]" for m in r_en["matches"])
    assert "塑料外壳式断路器" in targets_en, targets_en
    assert "功耗" in targets_en, targets_en
    assert "GB/T 14048.2—2020 暂未收录" in targets_en, targets_en

    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as tf:
        json.dump({"schema": "chint-office-extract/v1", "source": "cat.pdf", "total_units": 1, "scanned_units": 1, "low_text_pages": [], "units": [{"location": "P1:L1", "text": "分励脱扣器"}]}, tf)
        tpath = Path(tf.name)
    try:
        _, units = load_text_units(str(tpath))
        r_pipe = lookup_terms(units, acb_entries, "zh2en")
        assert any("Shunt release (SHT)" in m["target"] for m in r_pipe["matches"]), r_pipe
    finally:
        tpath.unlink(missing_ok=True)

    print("SELF-TEST PASS: glossary_lookup.py verified (zh2en ACB + 2万次, en2zh MCCB + Icu1 gap, extract JSON pipe).")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="SSOT Markdown glossary lookup for chint-translation")
    parser.add_argument("source", nargs="?", help="Text file, chint-office-extract/v1 JSON, or '-'")
    parser.add_argument("--dir", choices=["zh2en", "en2zh"], default="zh2en")
    parser.add_argument("--dept", choices=["acb", "mccb", "all"], default="all")
    parser.add_argument("--region", help="Optional isolated region override Markdown path")
    parser.add_argument("--json", action="store_true", help="Emit JSON output")
    parser.add_argument("--self-test", action="store_true", help="Run built-in verification suite")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()
    if not args.source:
        parser.error("source is required unless --self-test is set")

    src_name, units = load_text_units(args.source)
    entries = build_glossary(args.dept, args.region)
    res = lookup_terms(units, entries, args.dir)
    res["source"] = src_name
    res["dept"] = args.dept

    if args.json:
        print(json.dumps(res, ensure_ascii=False, indent=2))
    else:
        print(f"| Source Match | Canonical Target | Clause / Standard Basis | Origin | Locations |")
        print(f"| :--- | :--- | :--- | :--- | :--- |")
        for m in res["matches"]:
            locs = ", ".join(m["locations"])
            print(f"| `{m['matched_source']}` | **{m['target']}** | {m['basis']} | `{m['source_file']}` | `{locs}` |")
    return 0


if __name__ == "__main__":
    sys.exit(main())
