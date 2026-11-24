#!/usr/bin/env python3
"""Repository-level anti-drift, parity, contract, and eval smoke gate for CHINT document skills."""
from __future__ import annotations

import importlib.util
import json
import re
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO_ROOT / "skills"
TRN_DIR = SKILLS_DIR / "chint-translation"
CAT_DIR = SKILLS_DIR / "chint-catalog-edit"
OFF_DIR = SKILLS_DIR / "chint-office-suite"


def _load_mod(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, str(path))
    assert spec is not None and spec.loader is not None, f"Failed to load {path}"
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def gate_1_self_tests() -> None:
    scripts = [
        TRN_DIR / "scripts" / "glossary_lookup.py",
        TRN_DIR / "scripts" / "lint_text.py",
        CAT_DIR / "scripts" / "audit_catalog.py",
        OFF_DIR / "scripts" / "extract_doc.py",
        OFF_DIR / "scripts" / "annotate_pdf.py",
    ]
    for sp in scripts:
        res = subprocess.run([sys.executable, str(sp), "--self-test"], capture_output=True, text=True)
        assert res.returncode == 0, f"{sp.name} --self-test failed:\n{res.stdout}\n{res.stderr}"
    print("[PASS] Gate 1: All 5 script --self-test suites passed.")


def gate_2_ssot_parity() -> None:
    lint = _load_mod("_lint_text", TRN_DIR / "scripts" / "lint_text.py")
    cat = _load_mod("_audit_catalog", CAT_DIR / "scripts" / "audit_catalog.py")
    ssot_live, src, _ = cat.load_translation_ssot(TRN_DIR)
    assert src == "sibling:chint-translation"
    keys = (
        "BLACKLIST_COMMON",
        "BLACKLIST_ACB",
        "BLACKLIST_MCCB",
        "COMPETITOR_RULES_COMMON",
        "COMPETITOR_RULES_ACB",
        "STD_CONCEPT_ZH",
        "STD_STATUTORY_ZH",
        "ED5_GUARD_TAGS",
    )
    for k in keys:
        assert ssot_live[k] == cat.BUILTIN_SSOT_FALLBACK[k], f"SSOT drift on {k}"
    assert ssot_live["ED5_CLAUSE_RE"].pattern == cat.BUILTIN_SSOT_FALLBACK["ED5_CLAUSE_RE"].pattern

    sample_en = [("P1:L1", "Closed electromagnet (XF), Shunt Trip (MX), Earch current transformer, Cl. 4.3.5.")]
    sample_zh = [("P2:L1", "使用类别 A、使用类别 AC-22、热磁脱扣器、闭合电磁铁、漏电互感器。")]
    r_sib_en = cat.scan_units(sample_en, profile="L3", mode="en", with_iec=True, dept="acb", ssot=ssot_live)
    r_blt_en = cat.scan_units(sample_en, profile="L3", mode="en", with_iec=True, dept="acb", ssot=cat.BUILTIN_SSOT_FALLBACK)
    r_sib_zh = cat.scan_units(sample_zh, profile="L3", mode="zh", with_iec=True, dept="acb", ssot=ssot_live)
    r_blt_zh = cat.scan_units(sample_zh, profile="L3", mode="zh", with_iec=True, dept="acb", ssot=cat.BUILTIN_SSOT_FALLBACK)
    assert cat.strip_internal_fields(r_sib_en) == cat.strip_internal_fields(r_blt_en)
    assert cat.strip_internal_fields(r_sib_zh) == cat.strip_internal_fields(r_blt_zh)
    print("[PASS] Gate 2: 9-key SSOT and live-vs-builtin scan_units parity verified.")


def gate_3_office_parity() -> None:
    import fitz
    import openpyxl

    ext = _load_mod("_extract_doc", OFF_DIR / "scripts" / "extract_doc.py")
    ann = _load_mod("_annotate_pdf", OFF_DIR / "scripts" / "annotate_pdf.py")
    cat = _load_mod("_audit_catalog", CAT_DIR / "scripts" / "audit_catalog.py")

    with tempfile.TemporaryDirectory() as tmp:
        td = Path(tmp)
        pdf_p = td / "tricky.pdf"
        d = fitz.open()
        p = d.new_page()
        pre = p.add_rect_annot(fitz.Rect(20, 20, 60, 40))
        pre.set_info(title="Legacy Reviewer", content="Pre-existing")
        pre.update()
        p.insert_text((72, 100), "Column MN Omni autumn")
        p.insert_text((72, 125), "Rating 250A and 1250A")
        p.insert_text((72, 150), "Split line")
        p.insert_text((72, 165), "phrase; Split line")
        p.insert_text((72, 180), "phrase")
        p.insert_text((72, 210), "Frame 1000A, 1600A and 2000A")
        p2 = d.new_page()
        p2.set_rotation(90)
        p2.insert_text((72, 100), "Rotated Heading")
        d.save(str(pdf_p))
        d.close()

        items = [
            {"page": 1, "search": "MN", "match_mode": "all", "comment": "Code"},
            {"page": 1, "search": "250A", "match_mode": "all", "comment": "Spacing"},
            {"page": 1, "search": "Split line phrase", "match_mode": "all", "comment": "Wrapped"},
            {"page": 1, "searches": ["1000A", "1600A", "2000A"], "match_mode": "merged", "comment": "Merged"},
            {"page": 1, "search": "UNMATCHED_TOKEN", "comment": "Fallback"},
            {"page": 2, "search": "Rotated Heading", "match_mode": "first", "comment": "Rotated"},
        ]
        out_sib = td / "sib.pdf"
        out_blt = td / "blt.pdf"
        s_sib = ann.annotate_pdf(pdf_p, items, out_sib, default_author="Tester")
        s_blt = cat._annotate_pdf_builtin(pdf_p, items, out_blt, default_author="Tester")
        for k in ("matched_items", "highlight_annotations", "highlighted_rects", "sticky_fallback_count"):
            assert s_sib[k] == s_blt[k], (k, s_sib, s_blt)
        assert s_blt["matched_items"] == 5 and s_blt["sticky_fallback_count"] == 1, s_blt
        with fitz.open(str(pdf_p)) as sdoc, fitz.open(str(out_sib)) as ds, fitz.open(str(out_blt)) as db:
            assert len(list(sdoc[0].annots())) == 1 and len(list(sdoc[1].annots())) == 0
            for pno in (0, 1):
                va = [(a.type[1], len(a.vertices or [])) for a in ds[pno].annots()]
                vb = [(a.type[1], len(a.vertices or [])) for a in db[pno].annots()]
                assert va == vb, (pno, va, vb)

        e_pdf_sib = ext.extract_document(str(pdf_p))
        e_pdf_blt = cat._extract_office_builtin(str(pdf_p))
        assert e_pdf_sib["units"] == e_pdf_blt["units"]
        assert e_pdf_sib["low_text_pages"] == e_pdf_blt["low_text_pages"]

        docx_p = td / "s.docx"
        with zipfile.ZipFile(str(docx_p), "w") as zf:
            zf.writestr("word/header1.xml", '<w:hdr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:p><w:r><w:t>Hdr</w:t></w:r></w:p></w:hdr>')
            zf.writestr("word/document.xml", '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body><w:p><w:r><w:t>A</w:t><w:tab/><w:t>B</w:t></w:r></w:p></w:body></w:document>')
        e_doc_sib = ext.extract_document(str(docx_p))
        e_doc_blt = cat._extract_office_builtin(str(docx_p))
        assert e_doc_sib["units"] == e_doc_blt["units"]

        xlsx_p = td / "s.xlsx"
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Specs"
        ws["A1"] = "Rated"
        ws["B1"] = "=2+2"
        wb.save(str(xlsx_p))
        wb.close()
        e_xl_sib = ext.extract_document(str(xlsx_p))
        e_xl_blt = cat._extract_office_builtin(str(xlsx_p))
        assert e_xl_sib["units"] == e_xl_blt["units"]
        assert e_xl_sib["uncached_formula_cells"] == e_xl_blt["uncached_formula_cells"] == ["Specs!B1"]
    print("[PASS] Gate 3: Standalone vs sibling PDF annotation & Office extractor parity verified.")


def gate_4_glossary_contract() -> None:
    gl = _load_mod("_glossary_lookup", TRN_DIR / "scripts" / "glossary_lookup.py")
    for dept in ("acb", "mccb"):
        entries = gl.build_glossary(dept, None)
        unsplit = [e for e in entries if e["source_file"] != "zh-legacy-alias" and (len(gl.split_top_level(e["zh"], "/")) > 1 or len(gl.split_top_level(e["en"], "/")) > 1)]
        assert not unsplit, (dept, unsplit)
        clipped = [e for e in entries if e["basis"].endswith("...")]
        assert not clipped, (dept, clipped)
        bad_tex = [e for e in entries if any(b in e["basis"] or b in e["zh"] or b in e["en"] for b in ("pm 10text", "e pm", "\\text", "\\ge"))]
        assert not bad_tex, (dept, bad_tex)
        bad_target = [e for e in entries if "暂未收录" in e["zh"]]
        assert not bad_target, (dept, bad_target)

    acb_e = gl.build_glossary("acb", None)
    mccb_e = gl.build_glossary("mccb", None)
    for tok in ("ETU", "MCR", "ZSI", "ACB"):
        res = gl.lookup_terms([("L1", tok)], acb_e, "en2zh")
        assert res["match_count"] == 1, (tok, res)
    for tok in ("MCCB", "TM-D", "Icu1", "CBI"):
        res = gl.lookup_terms([("L1", tok)], mccb_e, "en2zh")
        assert res["match_count"] == 1, (tok, res)
    for e in acb_e + mccb_e:
        if "单极极限" in e["zh"]:
            assert e["gb_missing"] is True, e
        elif any(k in e["zh"] for k in ("无过电流保护要求", "基本配电型脱扣器", "热记忆", "区域选择性联锁")):
            assert e["gb_missing"] is False, e
    print("[PASS] Gate 4: Glossary zero-bracket target, 0 unsplit, 0 truncation, 0 LaTeX glitches, exact gb_missing.")


def gate_5_links_and_versions() -> None:
    link_re = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
    for sk_dir in (TRN_DIR, CAT_DIR, OFF_DIR):
        md_files = [sk_dir / "SKILL.md"] + sorted((sk_dir / "references").rglob("*.md") if (sk_dir / "references").exists() else [])
        for md in md_files:
            txt = md.read_text(encoding="utf-8")
            for raw_t in link_re.findall(txt):
                if raw_t.startswith(("http://", "https://", "file://", "#")):
                    continue
                rel = raw_t.split("#", 1)[0]
                if not rel:
                    continue
                target = (md.parent / rel).resolve()
                assert target.exists(), f"Broken link in {md}: {raw_t} -> {target}"

    expected = {
        TRN_DIR: "1.2.0",
        CAT_DIR: "1.1.0",
        OFF_DIR: "1.0.1",
    }
    for sk_dir, ver in expected.items():
        meta_txt = (sk_dir / "skill.meta.yaml").read_text(encoding="utf-8")
        m = re.search(r"^version:\s*(\S+)", meta_txt, re.MULTILINE)
        assert m and m.group(1) == ver, (sk_dir.name, meta_txt)
        ev_path = sk_dir / "evals" / "evals.json"
        if ev_path.exists():
            ev_obj = json.loads(ev_path.read_text(encoding="utf-8"))
            assert ev_obj.get("version") == ver, (sk_dir.name, ev_obj.get("version"))
    print("[PASS] Gate 5: All Markdown relative links valid and skill metadata versions synchronized.")


def _prompt_quote(prompt: str) -> str:
    m = re.search(r"「([\s\S]+?)」", prompt)
    if m:
        return m.group(1)
    m2 = re.search(r'"([\s\S]+?)"', prompt)
    if m2:
        return m2.group(1)
    m3 = re.search(r"'([\s\S]+?)'", prompt)
    if m3:
        return m3.group(1)
    return prompt


def gate_6_eval_smoke() -> None:
    import fitz

    gl = _load_mod("_glossary_lookup", TRN_DIR / "scripts" / "glossary_lookup.py")
    cat = _load_mod("_audit_catalog", CAT_DIR / "scripts" / "audit_catalog.py")
    ssot_live, _, _ = cat.load_translation_ssot(TRN_DIR)

    trn_evals = json.loads((TRN_DIR / "evals" / "evals.json").read_text(encoding="utf-8"))["evals"]
    acb_e = gl.build_glossary("acb", None)
    mccb_e = gl.build_glossary("mccb", None)

    e0_zh = _prompt_quote(trn_evals[0]["prompt"])
    t0 = {m["target"] for m in gl.lookup_terms([("P1:L1", e0_zh)], acb_e, "zh2en")["matches"]}
    assert {"Shunt release (SHT)", "Closing release (CEM)", "Ready-to-close contact (SPC)", "Key lock (KL)", "Withdrawable interphase barrier (DD)"} <= t0, t0

    e1_en = _prompt_quote(trn_evals[1]["prompt"])
    f1 = {f["match"] for f in cat.scan_units([("P1:L1", e1_en)], profile="L3", mode="en", dept="mccb", ssot=ssot_live)}
    assert {"Plastic case breaker", "Cl. 4.3.5", "MX"} <= f1 and any("Category" in x or "Isd" in x for x in f1), f1

    e2_en = _prompt_quote(trn_evals[2]["prompt"])
    r2 = gl.lookup_terms([("P1:L1", ln) for ln in e2_en.splitlines()], mccb_e, "en2zh")
    assert any(m["target"] == "塑料外壳式断路器" for m in r2["matches"])
    icu1_m = next(m for m in r2["matches"] if "单极极限" in m["target"])
    assert icu1_m["gb_missing"] is True and "暂未收录" not in icu1_m["target"]
    assert any(f["category"] == "TECH_HARD_ERROR" for f in cat.scan_units([("P1:L1", e2_en)], profile="L1", mode="en", dept="mccb", ssot=ssot_live))

    e3_zh = _prompt_quote(trn_evals[3]["prompt"])
    r3 = gl.lookup_terms([("P1:L1", ln) for ln in e3_zh.splitlines()], mccb_e, "zh2en")
    t3_blob = " | ".join(m["target"] for m in r3["matches"])
    assert {"Residual current protection", "Critical DC load current", "Back-up protection", "Take-over current"} <= {m["target"] for m in r3["matches"]}, t3_blob

    cat_evals = json.loads((CAT_DIR / "evals" / "evals.json").read_text(encoding="utf-8"))["evals"]
    c0_units = [("P36:L1", "瞬时电流 Ii 可设定范围：1.5In~50KA/65KA/75KA；□UVTZ 失压延时(详见 P036)；闭合电磁铁、万能式断路器。"), ("P44:L1", "额定绝缘电压 Ui(kV) 1000；额定冲击耐受电压 Uimp(V) 8；安装地点：海拨不超过2000m；环境温度-5℃~+40℃；功率损耗；涂润滑酯。")]
    c0_hits = {f["match"] for f in cat.scan_units(c0_units, profile="L1", mode="zh", ssot=cat.BUILTIN_SSOT_FALLBACK)}
    assert {"Ui(kV)", "Uimp(V)", "详见 P036", "海拨", "润滑酯"} <= c0_hits
    assert not (c0_hits & {"50KA", "2000m", "℃", "闭合电磁铁", "万能式断路器"})

    c1_zh = _prompt_quote(cat_evals[1]["prompt"])
    c1_hits = {f["match"] for f in cat.scan_units([("P3:L1", c1_zh)], profile="L1", with_iec=True, mode="zh", dept="acb", ssot=cat.BUILTIN_SSOT_FALLBACK)}
    assert {"万能式断路器", "使用类别 A", "闭合电磁铁", "结构差异"} <= c1_hits, c1_hits

    c2_en = _prompt_quote(cat_evals[2]["prompt"])
    c2_hits = {f["match"] for f in cat.scan_units([("P2:L1", c2_en)], profile="L1", mode="en", dept="acb", ssot=cat.BUILTIN_SSOT_FALLBACK)}
    assert {"Closed electromagnet", "XF", "Shunt Trip", "MX", "Earch current transformer"} <= c2_hits
    assert any("Isd" in m for m in c2_hits) and not (c2_hits & {"Molded", "color", "250A"})

    with tempfile.TemporaryDirectory() as tmp:
        c3_pdf = Path(tmp) / "c3.pdf"
        doc = fitz.open()
        doc.new_page()
        p2 = doc.new_page()
        p2.insert_text((50, 60), "Catalog Specification Table: Ui(kV) 1000, Uimp(V) 8, Altitude limit:")
        p2.insert_text((50, 90), "海拨超过 2000m，请注意核实。", fontname="china-s")
        doc.save(str(c3_pdf))
        doc.close()
        loaded = cat.load_units(str(c3_pdf), office_dir=None)
        assert loaded["low_text_pages"] == [1] and loaded["office_engine"] == "builtin-standalone"
        c3_hits = {f["match"] for f in cat.scan_units(loaded["units"], profile="L1", mode="zh", ssot=cat.BUILTIN_SSOT_FALLBACK)}
        assert {"Ui(kV)", "海拨"} <= c3_hits

    print("[PASS] Gate 6: All 8 evals.json deterministic smoke checks passed.")


def main() -> int:
    gate_1_self_tests()
    gate_2_ssot_parity()
    gate_3_office_parity()
    gate_4_glossary_contract()
    gate_5_links_and_versions()
    gate_6_eval_smoke()
    print("ALL 6 DOC-SKILL VERIFICATION GATES PASS.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
