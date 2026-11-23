---
name: chint-translation
description: IEC 60947-2:2024 (EN) and GB/T 14048.2-2020 (ZH) single-track translation and terminology audit for CHINT ACB & MCCB. Use when translating specs, catalogues, or manuals to English, back-translating to statutory Chinese, or auditing text/extracted documents for standard terms, CHINT accessory codes, and regional compliance.
---

# CHINT Circuit-Breaker Translation & Audit Standard (`chint-translation` v4.0.0)

## Dual-Standard Statutory Anchors & Orthography

- **Zero-Alias Statutory Terms**: `ZH→EN` outputs one canonical **`IEC 60947-2:2024`** (Ed. 6.0) English term and Ed. 6.0 clause; `EN→ZH` outputs one statutory **`GB/T 14048.2—2020`** Chinese term and GB/T 2020 clause with zero colloquial parenthetical aliases (explicitly flag IEC 2024-only additions such as $I_{cu1}$ or `CBI Class W`).
- **CHINT Accessory Ordering Codes**: Format product-accessory selection entries as **`Canonical IEC Term (CHINT Code)`** (e.g. `Closing release (CEM)`, `Shunt release (SHT)`, `Ready-to-close contact (SPC)`, `Motor-operator (MOD)`).
- **IEC 60947-2:2024 Orthography**: Use British nouns (`circuit-breaker`, `moulded`, `withdrawable`, `colour`, `aluminium`, `catalogue`, `behaviour`, `programme`, `analogue`, `signalling`), ISO/IEC Oxford `-ize` (`utilization`, `utilize`, `energize`, `energization`), standard hyphens (`lock-out`, `back-up`, `pick-up`, `time-delay`, `making-current release`, `let-through`, `cut-off`), and unhyphenated `undervoltage` and `Coordination`.

## Step 1 — Scope, Standards & Branch-Isolated Loading

1. Lock **Direction** (`ZH→EN` / `EN→ZH`), **Mode** (`Mode A: Translation` / `Mode B: Exhaustive Audit`), **Single Department** (`ACB` or `MCCB`), and **Target Jurisdiction** (default `IEC 60947-2:2024 ⟷ GB/T 14048.2—2020`; override only when user specifies another country/region).
2. Load only files matching your active branch:
   - **Standard Base (All Tasks)**: Read [iec_60947_2_standard.md](references/iec_60947_2_standard.md).
   - **Single Department (Exactly One)**: Read [acb.md](references/departments/acb.md) (`NXA`, `NA8`, `NA1`) OR [mccb.md](references/departments/mccb.md) (`NXM`, `NXS`, `NM8`, `NM5`). Read §1–§3 for positive terms; read §4 Blacklist only in `Mode B` or `EN→ZH` decoding.
   - **Regional Override (Optional, Isolated)**: Read [references/regions/_region_template.md](references/regions/_region_template.md) (or the specific `references/regions/<country>.md` when added) **only** when targeting a country outside default IEC/GB; otherwise leave unloaded.
   - **Office Document Inputs (`.pdf`, `.docx`, `.xlsx`)**: Delegate file extraction and non-destructive PDF annotation via the decoupled `chint-office-suite` handoff contract (Step 2 & Step 4); this skill handles pure text and structured extraction JSON only.
3. *Done when*: direction, mode, single department, and jurisdiction are locked with zero cross-department or unrequested regional files loaded.

## Step 2 — Mechanical Text Lint (Pure-Stdlib Sweep)

1. If the user supplies an Office file (`.pdf`, `.docx`, `.xlsx`), extract `chint-office-extract/v1` JSON via `chint-office-suite` (`extract_doc.py --json`) first and pipe it into [lint_text.py](scripts/lint_text.py); for plain text/markdown, pipe directly (`-`):
   - `python3 scripts/lint_text.py <text_or_extract_json_or_-> --dept <acb|mccb> --mode <en|zh> --json`
2. Record `total_units`, `scanned_units`, any preserved `low_text_pages` (`<50`-char visual PDF pages), and all hits (`Mode B` triages all hits; `Mode A` resolves drafted output to `0` hits).
3. *Done when*: 100% of units linted (`0` mechanical hits on `Mode A` target text; every visual-only page disclosed).

## Step 3 — Exhaustive Semantic & Value-Slot Verification

Inspect **every** unit, table, header, caption, and footnote sequentially without sampling:
1. **Statutory & CHINT Integrity**: Confirm dual-standard match (`IEC 2024` EN ⟷ `GB/T 2020` ZH), `kA rms` ($I_{cu}/I_{cs}/I_{cw}/I_{cu1}$) vs `kA peak` ($I_{cm}$), clause edition match, `Category A` vs `Isd`/`Icw` (`IEC 5.4` / `GB 4.4`), `frame size` (`IEC 3.1.1` / `GB 2.1.1`), `ground-fault` vs `earth fault`, `Annex B` (`Type AC/A/B`) vs `IEC 62423`, and `Cl. 6` / `GB 5.2` markings.
2. **Zero-Fabrication Value Slots**: Populate `{{param_name: unit}}` strictly from verified datasheets (named in department §1) or user source; isolate unverified/contradictory figures into Pending Verification List; scope family-wide claims (`100% of Ics`, rotatable terminals); preserve asymmetric bounds (`≥` vs `>`).
3. **Formatting**: Use normative `shall`, department §3.2 sentence frames, single half-width number-unit space (`250 A`, `415 V AC`, `-5 °C` to `+40 °C`), and plain integer `operating cycles` (`操作循环次数`) for `N 万次`.
4. *Done when*: every unit verified; every defect carries exact coordinate, quoted source, unique statutory fix, and clause/code basis.

## Step 4 — Deliverable Contract & PDF Annotation Handoff

- **Mode B (`Exhaustive Audit`)** emits three mandatory blocks:
  1. `Errata Table`: `Location | Quoted Source | Defect Class | Unique Statutory Replacement | Standard / CHINT Basis`
  2. `Coverage Ledger`: `Total units | Scanned | Unscanned Visual Pages (<50 chars) | Mechanical hits | Semantic hits`
  3. `Pending Verification List`: unverified ratings, missing mandatory parameters, and technical contradictions.
  - When the user requests annotated PDF output for branding execution, emit `chint-office-annotate/v1` JSON (`page`, `search`, `comment`) and hand off to `chint-office-suite` (`annotate_pdf.py`) to write a new annotated PDF copy.
- **Mode A (`Translation`)** emits clean target text (`0` lint defects, `0` unresolved `{{...}}`), Key Term Mapping Table, and Pending Verification List if needed.
- **Completion Gate**: Steps 1–4 satisfied; dual-standard statutory rules and department/region isolation honoured; zero fabricated ratings.
