---
name: chint-translation
description: IEC 60947-2:2024 single-track ZH↔EN translation and exhaustive catalogue audit for CHINT ACB & MCCB. Use when translating catalogues, datasheets, or manuals to English, back-translating to Chinese, or auditing drafts for IEC terminology, CHINT accessory codes, and parameter defects.
---

# CHINT Low-Voltage Translation & Audit Standard (`chint-translation` v3.1.0)

## Single-Track Standard & Orthography

- **One Canonical Output Per Concept**: Produce one unique `IEC 60947-2:2024` (Ed. 6.0) English term (for `ZH→EN`) or one `GB/T 14048.2` Chinese term (for `EN→ZH`) across catalogues, datasheets, tenders, and manuals alike.
- **CHINT Exclusive Codes**: Format accessories carrying official CHINT codes as **`Canonical IEC Term (CHINT Code)`** — e.g. `Closing release (CEM)`, `Shunt release (SHT)`, `Ready-to-close contact (SPC)`, `Motor-operator (MOD)`.
- **IEC 60947-2:2024 Orthography**: Use British nouns (`circuit-breaker`, `moulded`, `withdrawable`, `colour`, `aluminium`, `catalogue`, `behaviour`, `programme`, `analogue`, `signalling`), ISO/IEC Oxford `-ize` (`utilization`, `utilize`, `energize`, `energization`), standard hyphens (`lock-out`, `back-up`, `pick-up`, `time-delay`, `making-current release`, `let-through`, `cut-off`), and unhyphenated `undervoltage` and `Coordination`.

## Step 1 — Scope, Direction & Branch-Isolated Loading

1. Lock **Direction** (`ZH→EN` or `EN→ZH`), **Mode** (`Mode A: Direct Translation` or `Mode B: Exhaustive Audit`), and **Single Department** (`ACB` or `MCCB`).
2. Load only the files required by your active branch (`1 + 1 + N` strict isolation):
   - **Standard Base (All Tasks)**: Read [iec_60947_2_standard.md](references/iec_60947_2_standard.md).
   - **Single Department (Load Exactly One)**: Read [acb.md](references/departments/acb.md) for ACB (`NXA`, `NA8`, `NA1`) OR [mccb.md](references/departments/mccb.md) for MCCB (`NXM`, `NXS`, `NM8`, `NM5`). Read §1–§3 for positive terminology; consult §4 Audit Blacklist only in `Mode B` or when decoding legacy `EN→ZH` drafts.
   - **New Department Only**: Read [_template.md](references/departments/_template.md) exclusively when scaffolding a separate product line.
   - **Local Datasheet Anchor**: Inspect local files named in department §1 only to resolve exact SKU codes or `{{...}}` value slots.
3. *Done when*: direction, mode, and single department are locked with zero cross-department files loaded.

## Step 2 — Mechanical-First Sweep (Deterministic Recall)

Run [audit_catalogue.py](scripts/audit_catalogue.py) across 100% of the source file (`.pdf`, `.docx`, `.xlsx`, `.md`, `.txt`) or piped text (`-`) to guarantee exhaustive pattern detection:
- **Mode B (`Exhaustive Audit`)**: Run `python3 scripts/audit_catalogue.py <source> --dept <acb|mccb> --mode <en|zh> --json` **before** semantic reading. Record `total_units`, `scanned_units`, every PDF page in `low_text_pages` (`<50` chars, image/vector-only), and every finding (`ORTHOGRAPHY_US_HYPHEN`, `BLACKLIST_CHINGLISH_UL`, `COMPETITOR_CODE`, `OBSOLETE_CLAUSE_ED5`, `UNIT_SPACING_PUNCT`).
- **Mode A (`Direct Translation`)**: Pipe drafted target text into `python3 scripts/audit_catalogue.py - --dept <acb|mccb> --mode <en|zh>` and resolve all hits to `0`.
- *Done when*: scanner completed across 100% of input scope, every `<50`-char PDF page is recorded in `Unscanned Visual Pages`, and mechanical hits are triaged (`Mode B`) or zeroed (`Mode A`).

## Step 3 — Exhaustive Semantic & Technical Sweep

Inspect **every** page, table, header, diagram caption, and footnote sequentially without sampling:
1. **Single-Track Terminology & CHINT Coding**: Verify every term matches `iec_60947_2_standard.md` + active `departments/<dept>.md` §2–§3; flag any §4 blacklist match, legacy Chinglish phrasing, competitor code, or missing CHINT code.
2. **IEC 60947-2:2024 Technical Integrity**: Check `kA rms` ($I_{cu}/I_{cs}/I_{cw}/I_{cu1}$) vs `kA peak` ($I_{cm}$), Ed. 6.0 clause accuracy, `Category A` vs `Isd`/`Icw` (`Cl. 5.4`), `frame size` (`Cl. 3.1.1`) vs `Inm` (`GB/T 14048.2`), `ground-fault` (G-stage) vs `earth fault` (Annex B), `Icu1` phase-to-neutral meaning (`Cl. 5.3.6.2.3`), `Annex B` waveforms (`Type AC/A/B` only) vs `IEC 62423`, and `Cl. 6` markings.
3. **Zero-Fabrication Value-Slot Rule**: Populate `{{param_name: unit}}` strictly from the exact model's datasheet or user source; flag unverified ratings, missing mandatory fields, or technical contradictions cleanly in the Pending Verification List; scope family-wide claims (`100% of Ics`, rotatable terminals) to verified models; preserve asymmetric bounds (`≥` vs `>`).
4. **Native Engineering Style & Formatting**: Apply normative `shall` for requirements, §3.2 native sentence frames, exactly one half-width space between number and unit (`250 A`, `415 V AC`, `-5 °C` to `+40 °C`), and plain integer `operating cycles` for `N 万次` (`Table 7`).
- *Done when*: every page, table, caption, and footnote has been audited, and every defect carries an exact location, quoted source, unique canonical fix, and IEC/CHINT basis.

## Step 4 — Deliverable Contract & Completion Gate

- **Mode B (`Exhaustive Audit` — errata ready for branding execution without modifying source PDF/docx layout)** outputs three mandatory blocks:
  1. `Errata Table`: `Location (Page/Table/Row) | Quoted Source | Defect Class | Unique Canonical Replacement | IEC / CHINT Basis`
  2. `Coverage Ledger`: `Total pages/sections | Scanned | Unscanned Visual Pages (<50 chars) | Mechanical hits | Semantic hits`
  3. `Pending Verification List`: unverified ratings, missing mandatory parameters, and technical contradictions.
- **Mode A (`Direct Translation`)** outputs: (1) clean single-track target text (`0` scanner defects, `0` unresolved `{{...}}` slots), (2) Key Term & CHINT Code Mapping Table, and (3) Pending Verification List where source omits mandatory specs.
- **Completion Gate**: Steps 1–4 executed in order; deterministic scanner run recorded; 100% coverage ledger accounted for; zero fabricated parameters; department isolation intact.
