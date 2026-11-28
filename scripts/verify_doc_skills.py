#!/usr/bin/env python3
"""Repository-level anti-drift, parity, contract, eval smoke, and cross-skill duplicate-drift gate for CHINT document skills."""
from __future__ import annotations

import ast
import hashlib
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
CAT_DIR = SKILLS_DIR / "chint-doc-proofi"
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
        clipped = [e for e in entries if e["basis"].endswith("...") and "依据摘录已截断" not in e["basis"]]
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
        CAT_DIR: "2.0.0",
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
    c2_l1 = {f["match"] for f in cat.scan_units([("P2:L1", c2_en)], profile="L1", mode="en", dept="acb", ssot=cat.BUILTIN_SSOT_FALLBACK)}
    c2_l2 = {f["match"] for f in cat.scan_units([("P2:L1", c2_en)], profile="L2", mode="en", dept="acb", ssot=cat.BUILTIN_SSOT_FALLBACK)}
    # Eval 2 asserts L2 (peer-valid legacy terms are EN_TERM_CONSISTENCY, suppressed at L1),
    # so both directions are checked: L2 reports them, L1 suppresses only the two terms that
    # are in `severity_overrides` while keeping the competitor codes and the `Earch`
    # misspelling, which is a severe error rather than a peer-valid legacy form.
    assert {"Closed electromagnet", "XF", "Shunt Trip", "MX", "Earch current transformer"} <= c2_l2
    assert {"XF", "MX", "Earch current transformer"} <= c2_l1
    assert not (c2_l1 & {"Closed electromagnet", "Shunt Trip"})
    assert any("Isd" in m for m in c2_l1) and not (c2_l1 & {"Molded", "color", "250A"})

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

        # Eval 4: generic-layer-blind-sample (L1 generic defects + L2 SI casing + clean negatives)
        c4_l1_units = [
            ("P5:L1", "额定电流范围 63~32A；区间 4000~4000；Ics=65kA，Icu=50kA；断路器断路器；多出括号 ) 收尾。"),
            ("P5:L2", "图 3-2 外形"),
            ("P9:L1", "图 3-2 外形"),
        ]
        c4_l1 = cat.scan_units(c4_l1_units, profile="L1", mode="zh", ssot=cat.BUILTIN_SSOT_FALLBACK, total_pages=10)
        c4_l1_cats = {f["category"] for f in c4_l1}
        assert {"NUMERIC_RANGE", "TECH_HARD_ERROR", "DUPLICATE_WORD", "CROSSREF_NUMBERING", "BRACKET_UNBALANCED"} <= c4_l1_cats, c4_l1
        c4_l2 = cat.scan_units([
            ("P6:L1", "瞬时电流 50KA、频率 60HZ、正常区间 16~63A、功率因数 cos φ = 0.85、第一 2 项、一般 10 分钟。"),
        ], profile="L2", mode="zh", ssot=cat.BUILTIN_SSOT_FALLBACK, total_pages=10)
        c4_l2_matches = [f["match"] for f in c4_l2]
        assert any("50KA" in m for m in c4_l2_matches) and any("60HZ" in m for m in c4_l2_matches), c4_l2
        assert not any("16~63" in m or "cos φ" in m or "一" in m for m in c4_l2_matches), c4_l2

        # Eval 5: pptx-slide-locator-errata (S7/S12 locators via pure stdlib zip)
        c5_pptx = Path(tmp) / "c5.pptx"
        def _sld(text: str) -> str:
            return (
                '<p:sld xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"'
                ' xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">'
                f'<p:cSld><p:spTree><p:sp><p:txBody><a:bodyPr/><a:p><a:r><a:t>{text}</a:t></a:r></a:p></p:txBody></p:sp></p:spTree></p:cSld></p:sld>'
            )
        with zipfile.ZipFile(str(c5_pptx), "w") as zf:
            for s_idx in range(1, 13):
                body = "额定电流调节范围 63~32A" if s_idx == 7 else ("安装地点：海拨不超过 2000m" if s_idx == 12 else f"正常页 {s_idx}")
                zf.writestr(f"ppt/slides/slide{s_idx}.xml", _sld(body))
        c5_loaded = cat.load_units(str(c5_pptx), office_dir=None)
        c5_hits = cat.scan_units(c5_loaded["units"], profile="L1", mode="zh", ssot=cat.BUILTIN_SSOT_FALLBACK)
        assert any(f["location"].startswith("S7:") and "63~32" in f["match"] for f in c5_hits), c5_hits
        assert any(f["location"].startswith("S12:") and "海拨" in f["match"] for f in c5_hits), c5_hits

        # Eval 6: legacy-binary-unparseable-hard-error (real corrupt fixtures exit 2)
        for rel_f, expect_ext in (("evals/files/corrupt_ole2.doc", ".docx"), ("evals/files/corrupt_ole2.xls", ".xlsx")):
            r6 = subprocess.run(
                [sys.executable, "-I", str(CAT_DIR / "scripts" / "audit_catalog.py"), str(CAT_DIR / rel_f), "--profile", "L1"],
                capture_output=True, text=True,
            )
            assert r6.returncode == 2 and "无法解析" in r6.stderr and expect_ext in r6.stderr, (rel_f, r6.returncode, r6.stderr)

        # Eval 7: markdown-fenced-code-exemption (prose only, M<line> locators)
        c7_md = Path(tmp) / "notes.md"
        c7_md.write_text(
            "## 结论\n\n现场纪要里写成了「海拨 2000m」，需要改。\n\n```bash\n# 海拨 不应该在这里报错\necho 63~32A\n```\n\n行内代码 `海拨` 也不该算正文。\n",
            encoding="utf-8",
        )
        c7_loaded = cat.load_units(str(c7_md), office_dir=None)
        c7_hits = cat.scan_units(c7_loaded["units"], profile="L1", mode="zh", ssot=cat.BUILTIN_SSOT_FALLBACK)
        assert len(c7_hits) == 1 and c7_hits[0]["location"].startswith("M") and c7_hits[0]["match"] == "海拨", c7_hits

    assert len(cat_evals) >= 8, len(cat_evals)
    print("[PASS] Gate 6: All 12 evals.json deterministic smoke checks passed.")


# --- Gate 7 registry: deliberately duplicated cross-skill helpers -------------
# Skills must stay standalone and independently packageable, so shared helpers are
# copied, never imported from a shared module. The copies are compared per top-level
# function by docstring-stripped AST hash. "in-sync" is documentary (any shared
# function not marked intentional-divergence must hash-match anyway);
# "intentional-divergence:<reason>" is the explicit waiver and its reason is mandatory.
# The keys are the compared file pairs and double as the pair list for the gate.
# Paths are repo-relative and start with their skill directory: a skill pair that
# contributes more than one script (doc-proofi <-> office-suite) needs file-level
# keys, otherwise a registry entry could not say which side it belongs to.
DUP_PAIRS: dict[tuple[str, str], dict[str, str]] = {
    (
        "skills/chint-doc-proofi/scripts/audit_catalog.py",
        "skills/chint-office-suite/scripts/extract_doc.py",
    ): {
        "_docx_para_text": "in-sync",
        "_docx_xml_sort_key": "in-sync",
        "_ensure_utf8_stdio": "in-sync",
        "_import_fitz": "intentional-divergence: each skill ships its own dependency install hint; doc-proofi points at its bundled requirements.txt, office-suite at plain pip",
        "_import_openpyxl": "intentional-divergence: each skill ships its own dependency install hint; doc-proofi points at its bundled requirements.txt, office-suite at plain pip",
        "_probe_module": "in-sync",
        "build_summary": "intentional-divergence: different result contract; extract_doc emits chint-office-extract/v1 (schema, total_units, no office_engine), audit_catalog emits its loaded-dict summary (total, scanned, office_engine)",
        "check_env": "intentional-divergence: extract_doc probes dependencies only; audit_catalog also resolves sibling skill directories and reports standalone readiness",
        "main": "intentional-divergence: distinct CLI contracts (audit / annotate / emit vs extraction only)",
        "parse_page_spec": "in-sync",
        "run_self_test": "intentional-divergence: per-skill self-test suites cover different behaviours",
    },
    (
        "skills/chint-doc-proofi/scripts/audit_catalog.py",
        "skills/chint-office-suite/scripts/annotate_pdf.py",
    ): {
        "_chars_in_rect": "in-sync",
        "_collect_terms": "in-sync",
        "_ensure_utf8_stdio": "in-sync",
        "_extract_group_text": "in-sync",
        "_find_occurrence_groups": "in-sync",
        "_group_multiline_rects": "in-sync",
        "_import_fitz": "intentional-divergence: install hint names the caller's job (PDF annotation vs .pdf processing)",
        "_matching_line": "in-sync",
        "_page_lines_chars": "in-sync",
        "main": "intentional-divergence: distinct CLI contracts (audit / annotate / emit vs annotation only)",
        "run_self_test": "intentional-divergence: per-skill self-test suites cover different behaviours",
    },
    (
        "skills/chint-doc-proofi/scripts/audit_catalog.py",
        "skills/chint-translation/scripts/lint_text.py",
    ): {
        "_ensure_utf8_stdio": "in-sync",
        "_severity": "in-sync",
        "build_chunks": "in-sync",
        "format_report_md": "intentional-divergence: catalogue report carries coverage ledger, profile tag and aggregated MEDIUM section; translation lint report does not",
        "load_units": "intentional-divergence: lint_text reads text/JSON only; audit_catalog also extracts pdf/docx/xlsx/doc/xls and attaches tables",
        "main": "intentional-divergence: distinct CLI contracts (audit / annotate / emit vs translation lint only)",
        "run_self_test": "intentional-divergence: per-skill self-test suites cover different behaviours",
        "scan_units": "intentional-divergence: catalogue rule engine (L1-L3 profiles, IEC overlay, tables, document-scope detection) vs translation lint rule engine",
        "strip_internal_fields": "in-sync",
    },
    (
        "skills/chint-doc-proofi/scripts/audit_catalog.py",
        "skills/chint-translation/scripts/glossary_lookup.py",
    ): {
        "_ensure_utf8_stdio": "in-sync",
        "build_chunks": "in-sync",
        "main": "intentional-divergence: distinct CLI contracts (audit / annotate / emit vs glossary lookup only)",
        "run_self_test": "intentional-divergence: per-skill self-test suites cover different behaviours",
    },
}


def _strip_docstring_and_hash(node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    if node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Constant) and isinstance(node.body[0].value.value, str):
        node.body = node.body[1:]
    node.body = node.body or [ast.Pass()]
    return hashlib.sha256(ast.dump(node, annotate_fields=True, include_attributes=False).encode()).hexdigest()


def _function_hashes(path: Path) -> dict[str, str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    return {
        node.name: _strip_docstring_and_hash(node)
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }


def gate_7_cross_skill_duplicate_drift() -> None:
    for (rel_a, rel_b), registered in DUP_PAIRS.items():
        path_a, path_b = REPO_ROOT / rel_a, REPO_ROOT / rel_b
        hashes_a, hashes_b = _function_hashes(path_a), _function_hashes(path_b)

        for fn, status in registered.items():
            assert status.startswith("intentional-divergence:") or status == "in-sync", (
                f"Gate 7: invalid registry status {status!r} for '{fn}' ({path_b.name})."
            )
            if status.startswith("intentional-divergence:"):
                assert status.split(":", 1)[1].strip(), (
                    f"Gate 7: '{fn}' ({path_b.name}) is registered as intentional-divergence with an empty reason."
                )
            missing_from = [p.name for p, h in ((path_a, hashes_a), (path_b, hashes_b)) if fn not in h]
            assert not missing_from, (
                f"Gate 7 stale registry entry: '{fn}' is registered for {path_a.name} <-> {path_b.name} "
                f"but no longer exists in {', '.join(missing_from)}. Remove or correct the DUP_PAIRS entry."
            )

        verdicts: list[str] = []
        for fn in sorted(set(hashes_a) & set(hashes_b)):
            matches = hashes_a[fn] == hashes_b[fn]
            if not registered.get(fn, "").startswith("intentional-divergence:"):
                assert matches, (
                    f"Gate 7 duplicate drift: '{fn}' differs between {rel_a} and {rel_b}. "
                    f"同步另一侧或登记为有意分叉 — sync the other side, or register "
                    f"'{fn}': 'intentional-divergence:<reason>' in DUP_PAIRS."
                )
            verdicts.append(f"{fn}={'in-sync' if matches else 'intentional-divergence'}")
        print(f"  Gate 7: {path_a.name} <-> {path_b.name} -> {len(verdicts)} shared: {', '.join(verdicts)}")
    print("[PASS] Gate 7: All cross-skill duplicated helpers hash-match or are registered as intentional divergence.")


def main() -> int:
    gate_1_self_tests()
    gate_2_ssot_parity()
    gate_3_office_parity()
    gate_4_glossary_contract()
    gate_5_links_and_versions()
    gate_6_eval_smoke()
    gate_7_cross_skill_duplicate_drift()
    print("ALL 7 DOC-SKILL VERIFICATION GATES PASS.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
