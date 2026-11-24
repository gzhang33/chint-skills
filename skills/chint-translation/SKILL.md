---
name: chint-translation
description: "Translate CHINT ACB/MCCB specs (ZH→EN IEC 60947-2:2024, EN→ZH GB/T 14048.2—2020) or audit long texts and PDF/Word/Excel catalogues for statutory errata."
---

# CHINT Circuit-Breaker Translation & Audit Standard

Resolve `<SKILL_DIR>` from the directory containing this `SKILL.md` and run scripts via `python3 "<SKILL_DIR>/scripts/..."`.

- **Dual-Standard Statutory Anchors**: `ZH→EN` outputs one canonical **`IEC 60947-2:2024`** (Ed. 6.0) English term and clause; `EN→ZH` outputs one statutory **`GB/T 14048.2—2020`** Chinese term and clause, noting IEC 2024-only additions ($I_{cu1}$, `CBI Class W`).
- **CHINT Accessory Ordering Codes**: Format accessories as **`Canonical IEC Term (CHINT Code)`** (e.g. `Closing release (CEM)`, `Shunt release (SHT)`, `Ready-to-close contact (SPC)`).

## Step 1 — Lock Scope & Load Active References

1. Lock **Direction** (`ZH→EN` / `EN→ZH`), **Branch** (`Branch A: Fast Translation` / `Branch B: Long-Text & Catalogue Audit`), **Department** (`ACB` or `MCCB`), and **Jurisdiction** (default `IEC 60947-2:2024 ⟷ GB/T 14048.2—2020`).
2. Load only files matching the active task:
   - **Core Base**: [iec_60947_2_standard.md](references/iec_60947_2_standard.md).
   - **Annexes (`CBR`/`MRCD`/`CBI`/`ICB`/`PV`/`CBAR`/`IT`/`Al`/EMC only)**: [iec_annexes.md](references/iec_annexes.md).
   - **Single Department**: [acb.md](references/departments/acb.md) (`NXA`, `NA8`, `NA1`) OR [mccb.md](references/departments/mccb.md) (`NXM`, `NXS`, `NM8`, `NM5`).
   - **Audit Blacklist (`Branch B` or `EN→ZH` legacy decoding only)**: [audit_blacklist.md](references/audit_blacklist.md).
   - **Regional Override (Isolated)**: Load concrete `references/regions/<country>.md` only when targeting another jurisdiction.
   - **Office Handoff**: Delegate `.pdf`, `.docx`, and `.xlsx` extraction and PDF annotation to `chint-office-suite`. Stream extracted `chint-office-extract/v1` JSON via stdin or an OS `/tmp` file deleted on completion (zero sidecars in the user's directory).
3. *Done when*: Scope is locked and plain text or `chint-office-extract/v1` JSON is staged.

## Step 2 — Deterministic Script Pass (Branch-Specific)

1. **`Branch A` (Fast Translation)**:
   - Run `python3 "<SKILL_DIR>/scripts/glossary_lookup.py" <src_or_-> --dir <zh2en|en2zh> --dept <acb|mccb> [--region <path>]` to lock matched terms and `万次` cycle conversions.
   - Draft target text with verified `{{param_name: unit}}` slots, then run `python3 "<SKILL_DIR>/scripts/lint_text.py" - --dept <acb|mccb> --mode <en|zh> --json` until `finding_count == 0` (`exit 1` denotes findings present).
2. **`Branch B` (Long-Text & Catalogue Audit)**:
   - Run `python3 "<SKILL_DIR>/scripts/lint_text.py" <src_or_extract_json> --dept <acb|mccb> --mode <en|zh> --report-md --exit-zero` for deduplicated mechanical errata.
   - For inputs exceeding 50 non-empty units, run `--chunk-size 50 --chunks-info`, then inspect every chunk `1..N` sequentially with both `lint_text.py ... --chunk-size 50 --chunk-index <k> --exit-zero` (omitting `--report-md`) and `glossary_lookup.py ... --dir <...> --dept <...> --chunk-size 50 --chunk-index <k>`.
3. *Done when*: `Branch A` hits `finding_count == 0`; `Branch B` inspects all chunks `1..N` and preserves `low_text_pages`.

## Step 3 — Semantic Verification & Chat Deliverable

1. Verify every unit and rating for `kA rms` ($I_{cu}/I_{cs}/I_{cw}/I_{cu1}$) vs `kA peak` ($I_{cm}$), `Selectivity category A` vs `Isd`/`Icw` (`IEC 5.4` / `GB 4.4`), `frame size` (`IEC 3.1.1` / `GB 2.1.1`), asymmetric bounds (`≥` vs `>`), normative `shall`, and datasheet-verified values (isolate missing/unverified figures into Pending Verification List).
2. **Deliver by Branch**:
   - **`Branch A`**: Clean Target Text (`finding_count == 0`, zero unresolved `{{...}}`), Key Term Mapping Table, and Pending Verification List (if any).
   - **`Branch B`**: Present terse table rows directly in chat — Errata Table (`页码 | 级别 | 原文 | 替换为 | IEC/GB 依据`), Coverage Ledger (`总单元 | 已扫描 | 扫描/视觉页 | 机械命中 | 语义命中`), and Pending Verification List.
3. *Done when*: Every matched term, chunk, and visual-only page is accounted for with all numbers traced to source data — **and for PDF catalogues, the chat checklist above has been output and this turn ends cleanly without writing any PDF or invoking `--emit-annotate`, awaiting a new user message confirming the checklist (even if the initial prompt asked to annotate the PDF).**

> **Confirmed PDF Annotation Handoff**: Only after user confirmation arrives in a subsequent message, read [references/pdf_annotation_handoff.md](references/pdf_annotation_handoff.md) and execute it.