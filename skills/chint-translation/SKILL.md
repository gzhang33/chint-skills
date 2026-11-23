---
name: chint-translation
description: Translate CHINT ACB/MCCB specs (ZH→EN IEC 60947-2:2024, EN→ZH GB/T 14048.2-2020) or audit long texts and PDF catalogues for statutory errata.
---

# CHINT Circuit-Breaker Translation & Audit Standard (`chint-translation` v0.0.1)

- **Dual-Standard Statutory Anchors**: `ZH→EN` outputs one canonical **`IEC 60947-2:2024`** (Ed. 6.0) English term and clause; `EN→ZH` outputs one statutory **`GB/T 14048.2—2020`** Chinese term and clause, noting IEC 2024-only additions ($I_{cu1}$, `CBI Class W`).
- **CHINT Accessory Ordering Codes**: Format accessories as **`Canonical IEC Term (CHINT Code)`** (e.g. `Closing release (CEM)`, `Shunt release (SHT)`, `Ready-to-close contact (SPC)`).
- **Single-Source Orthography**: Enforced via [iec_60947_2_standard.md](references/iec_60947_2_standard.md) and [lint_text.py](scripts/lint_text.py).

## Step 1 — Lock Scope & Load Single Branch

1. Lock **Direction** (`ZH→EN` / `EN→ZH`), **Branch** (`Branch A: Fast Translation` / `Branch B: Long-Text & Catalogue Audit`), **Department** (`ACB` or `MCCB`), and **Jurisdiction** (default `IEC 60947-2:2024 ⟷ GB/T 14048.2—2020`).
2. Load only files matching the active branch:
   - **Standard Base**: [iec_60947_2_standard.md](references/iec_60947_2_standard.md).
   - **Single Department**: [acb.md](references/departments/acb.md) (`NXA`, `NA8`, `NA1`) OR [mccb.md](references/departments/mccb.md) (`NXM`, `NXS`, `NM8`, `NM5`). Consult §4 Blacklist only in `Branch B` or `EN→ZH` decoding.
   - **Regional Override (Isolated)**: [references/regions/_region_template.md](references/regions/_region_template.md) (or `references/regions/<country>.md`) loaded strictly when targeting another jurisdiction.
   - **Office Handoff**: Delegate `.pdf`, `.docx`, and `.xlsx` extraction and PDF annotation to `chint-office-suite`.
3. *Done when*: Scope is locked and extracted text or `chint-office-extract/v1` JSON is staged.

## Step 2 — Deterministic Script Pass (Branch-Specific)

1. **`Branch A` (Fast Translation)**:
   - Run `python3 scripts/glossary_lookup.py <src_or_-> --dir <zh2en|en2zh> --dept <acb|mccb>` to lock matched terms and `万次` cycle conversions.
   - Draft target text with verified `{{param_name: unit}}` slots, then run `python3 scripts/lint_text.py - --dept <acb|mccb> --mode <en|zh>` until `finding_count == 0`.
2. **`Branch B` (Long-Text & Catalogue Audit)**:
   - Run `python3 scripts/lint_text.py <src_or_extract_json> --dept <acb|mccb> --mode <en|zh> --report-md` for deduplicated mechanical errata.
   - For inputs exceeding 50 non-empty units, run `--chunk-size 50 --chunks-info` and inspect chunks `--chunk-index 1..N` sequentially with `glossary_lookup.py` to catch every semantic/technical defect.
3. *Done when*: `Branch A` hits `0` lint defects; `Branch B` inspects all chunks `1..N` and preserves `low_text_pages`.

## Step 3 — Semantic Verification & Chat Deliverable

1. Verify every unit and rating for `kA rms` ($I_{cu}/I_{cs}/I_{cw}/I_{cu1}$) vs `kA peak` ($I_{cm}$), `Selectivity category A` vs `Isd`/`Icw` (`IEC 5.4` / `GB 4.4`), `frame size` (`IEC 3.1.1` / `GB 2.1.1`), asymmetric bounds (`≥` vs `>`), normative `shall`, and datasheet-verified values (isolate missing/unverified figures into Pending Verification List).
2. **Deliver by Branch**:
   - **`Branch A`**: Clean Target Text (`0` lint hits, `0` unresolved `{{...}}`), Key Term Mapping Table, and Pending Verification List (if any).
   - **`Branch B`**: Present terse table rows only directly in chat — Errata Table (`页码 | 级别 | 原文 | 替换为 | IEC/GB 依据`), Coverage Ledger (`总单元 | 已扫描 | 扫描/视觉页 | 机械命中 | 语义命中`), and Pending Verification List. For PDF catalogues, stop here and await user confirmation before writing any PDF file.
3. *Done when*: Every matched term, chunk, and visual-only page is accounted for with all numbers traced to source data.

## Step 4 — Confirmed PDF Annotation Handoff (Branch B PDFs Only)

1. Run only after the user confirms Step 3's chat checklist: merge confirmed mechanical hits (`lint_text.py --emit-annotate -`, defaulting to `--annotate-severity high` so style/spacing noise stays in chat unless `--annotate-severity all` is explicitly requested) with confirmed semantic fixes.
2. Keep rule explanations and IEC/GB citations in chat; write copy-paste `替换为：<标准译文>` text only in each PDF comment, and pipe JSON directly via stdin (`--annotations -`) to `chint-office-suite/scripts/annotate_pdf.py --author "CHINT Translation"`.
3. *Done when*: A single new `<stem>_annotated.pdf` is written (source PDF untouched, pre-existing annotations preserved, zero stray sidecar files created on disk) and all `fallback_items` are surfaced.