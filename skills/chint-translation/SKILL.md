---
name: chint-translation
description: Translate and audit CHINT ACB/MCCB specs, catalogues, and long texts against IEC 60947-2:2024 (EN) and GB/T 14048.2-2020 (ZH). Use for ZH-EN translation, EN-ZH statutory back-translation, or exhaustive error checking.
---

# CHINT Circuit-Breaker Translation & Audit Standard (`chint-translation` v0.0.1)

- **Dual-Standard Statutory Anchors**: `ZH→EN` outputs one canonical **`IEC 60947-2:2024`** (Ed. 6.0) English term and Ed. 6.0 clause; `EN→ZH` outputs one statutory **`GB/T 14048.2—2020`** Chinese term and GB/T 2020 clause with explicit notes for IEC 2024-only additions ($I_{cu1}$, `CBI Class W`).
- **CHINT Accessory Ordering Codes**: Format product-accessory entries as **`Canonical IEC Term (CHINT Code)`** (e.g. `Closing release (CEM)`, `Shunt release (SHT)`, `Ready-to-close contact (SPC)`).
- **Standard Orthography**: Enforced single-source via [iec_60947_2_standard.md](references/iec_60947_2_standard.md) and [lint_text.py](scripts/lint_text.py) (`IEC 60947-2:2024` British spelling, ISO/IEC `-ize`, hyphenated `circuit-breaker`, unhyphenated `undervoltage` / `Coordination`).

## Step 1 — Lock Scope & Load Single Branch

1. Lock **Direction** (`ZH→EN` / `EN→ZH`), **Branch** (`Branch A: Fast Translation` / `Branch B: Long-Text & Catalogue Audit`), **Department** (`ACB` or `MCCB`), and **Jurisdiction** (default `IEC 60947-2:2024 ⟷ GB/T 14048.2—2020`).
2. Load only files matching the active branch:
   - **Standard Base**: [iec_60947_2_standard.md](references/iec_60947_2_standard.md).
   - **Single Department**: [acb.md](references/departments/acb.md) (`NXA`, `NA8`, `NA1`) OR [mccb.md](references/departments/mccb.md) (`NXM`, `NXS`, `NM8`, `NM5`). Consult §4 Blacklist only in `Branch B` or `EN→ZH` decoding.
   - **Regional Override (Isolated)**: [references/regions/_region_template.md](references/regions/_region_template.md) (or `references/regions/<country>.md`) loaded strictly when targeting another jurisdiction.
   - **Office Document Handoff**: Delegate `.pdf`, `.docx`, and `.xlsx` I/O to `chint-office-suite`: run `extract_doc.py --summary` for PDFs >20 pages, extract `chint-office-extract/v1` JSON via `extract_doc.py --json`, and hand errata back via `annotate_pdf.py` on a new PDF copy.
3. *Done when*: direction, branch, single department, and jurisdiction are locked and extracted JSON/plain text is staged.

## Step 2 — Deterministic Script Pass (Branch-Specific)

1. **`Branch A` (Fast Translation)**:
   - Run `python3 scripts/glossary_lookup.py <src_or_-> --dir <zh2en|en2zh> --dept <acb|mccb>` to lock every matched canonical term and `万次` cycle conversion directly from the reference tables.
   - Draft target text using locked terms and verified `{{param_name: unit}}` slots, then run `python3 scripts/lint_text.py - --dept <acb|mccb> --mode <en|zh>` until `finding_count == 0`.
2. **`Branch B` (Long-Text & Catalogue Audit)**:
   - Run `python3 scripts/lint_text.py <src_or_extract_json> --dept <acb|mccb> --mode <en|zh> --report-md [--emit-annotate <errata.json>]` for 100%-coverage deduplicated mechanical errata and optional `chint-office-annotate/v1` export.
   - For inputs exceeding 50 non-empty units, run `--chunk-size 50 --chunks-info` and inspect chunks `--chunk-index 1..N` sequentially with `glossary_lookup.py` to catch every semantic/technical defect without context overflow.
3. *Done when*: `Branch A` target hits `0` lint defects; `Branch B` covers all chunks `1..N` and preserves any `low_text_pages` (`<50`-char visual PDF pages).

## Step 3 — Semantic Verification & Deliverable Contract

1. Verify every unit and table cell for `kA rms` ($I_{cu}/I_{cs}/I_{cw}/I_{cu1}$) vs `kA peak` ($I_{cm}$), `Selectivity category A` vs `Isd`/`Icw` (`IEC 5.4` / `GB 4.4`), `frame size` (`IEC 3.1.1` / `GB 2.1.1`), asymmetric bounds (`≥` vs `>`), normative `shall`, and datasheet-verified values (isolate unverified/missing figures into Pending Verification List).
2. **Branch Outputs**:
   - **`Branch A`**: Clean Target Text (`0` lint hits, `0` unresolved `{{...}}`), Key Term Mapping Table, and Pending Verification List (if any).
   - **`Branch B`**: Errata Table (`Location | Quoted Source | Severity/Class | Statutory Fix | Basis`), Coverage Ledger (`Total units | Scanned | Visual-Only Pages (<50 chars) | Mechanical Hits | Semantic Hits`), Pending Verification List, and `chint-office-annotate/v1` JSON handoff to `chint-office-suite` (`annotate_pdf.py`) when PDF annotation is requested.
3. *Completion Gate*: Steps 1–3 satisfied; every matched term, chunk, and visual-only page accounted for; all numbers traceable to source data.
