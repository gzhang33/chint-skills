---
name: chint-translation
description: "Translate CHINT ACB/MCCB specs (ZH→EN IEC 60947-2:2024, EN→ZH GB/T 14048.2—2020), verify dual-standard terminology SSOT, or supply IEC/GB rules when chint-doc-proofi runs standard checks."
---

# CHINT Circuit-Breaker Translation & Terminology Standard

Resolve `<SKILL_DIR>` from the directory containing this `SKILL.md` and run scripts via `python3 "<SKILL_DIR>/scripts/..."` on macOS/Linux (or `python` / `py -3` on Windows).

- **Dual-Standard Statutory Anchors**: `ZH→EN` outputs one canonical **`IEC 60947-2:2024`** (Ed. 6.0) English term and clause; `EN→ZH` outputs one statutory **`GB/T 14048.2—2020`** Chinese term and clause, noting IEC 2024-only additions ($I_{cu1}$, `CBI Class W`).
- **CHINT Accessory Ordering Codes**: Format accessories as **`Canonical IEC Term (CHINT Code)`** (e.g. `Closing release (CEM)`, `Shunt release (SHT)`, `Ready-to-close contact (SPC)`).
- **Catalogue Proofreading & PDF Annotation**: For full PDF/Word/Excel catalogue error audits, threshold gating (`L1`/`L2`/`L3`), or PDF review annotations, route to `chint-doc-proofi` (and `chint-office-suite`).

## Step 1 — Lock Scope & Load Active References

1. Lock **Direction** (`ZH→EN` / `EN→ZH`), **Department** (`ACB` or `MCCB`), and **Jurisdiction** (default `IEC 60947-2:2024 ⟷ GB/T 14048.2—2020`).
2. Load only files matching the active task:
   - **Core Base**: [iec_60947_2_standard.md](references/iec_60947_2_standard.md).
   - **Annexes (`CBR`/`MRCD`/`CBI`/`ICB`/`PV`/`CBAR`/`IT`/`Al`/EMC only)**: [iec_annexes.md](references/iec_annexes.md).
   - **Single Department**: [acb.md](references/departments/acb.md) (`NXA`, `NA8`, `NA1`) OR [mccb.md](references/departments/mccb.md) (`NXM`, `NXS`, `NM8`, `NM8N`, `NM5`).
   - **Legacy Decoding & Redlines (`EN` audit / legacy decoding / `EN→ZH` statutory redlines)**: [audit_blacklist.md](references/audit_blacklist.md).
   - **Edition Divergences & Print Errata (standard-audit / `GB`-vs-`IEC` disputes only)**: [edition_divergences_and_errata.md](references/edition_divergences_and_errata.md).
   - **Regional Override (Isolated)**: Load concrete `references/regions/<country>.md` only when targeting another jurisdiction.
3. *Done when*: Scope is locked and source text is ready.

## Step 2 — Deterministic Script Pass

1. Run `python3 "<SKILL_DIR>/scripts/glossary_lookup.py" <src_or_-> --dir <zh2en|en2zh> --dept <acb|mccb> [--region <path>]` to lock matched terms and `万次` cycle conversions.
2. Draft target text with verified `{{param_name: unit}}` slots, then run `python3 "<SKILL_DIR>/scripts/lint_text.py" - --dept <acb|mccb> --mode <en|zh> --json` until `finding_count == 0` (`exit 1` denotes substantive standard, mistranslation, competitor-code, contradiction, or unresolved-slot findings).
3. *Done when*: `lint_text.py` returns `finding_count == 0`.

## Step 3 — Semantic Verification & Deliverable

1. Verify `kA` without appending `rms` ($I_{cu}/I_{cs}/I_{cw}/I_{cu1}/I_s$) vs `kA peak` ($I_{cm}$), Celsius symbol `℃` (never `°C`), `Selectivity category A` vs `Isd`/`Icw` (`IEC 5.4` / `GB 4.4`), `frame size` (`IEC 3.1.1` / `GB 2.1.1`), asymmetric bounds (`≥` vs `>`), normative `shall`, and datasheet-verified values (isolate missing/unverified figures into Pending Verification List).
2. Deliver directly in chat:
   - **Clean Target Text** (`finding_count == 0`, zero unresolved `{{...}}`)
   - **Key Term Mapping Table**
   - **Pending Verification List** (if any missing or contradictory source ratings exist)
3. *Done when*: Every statutory term maps to a verified clause, every CHINT/industry extension is labelled, and zero ratings are fabricated.

## Term Bank Maintenance (maintainers only)

The four reference tables are generated from **`翻译术语对照表_v*.xlsx`** (main repo, `resources/agent database/`). Edit the workbook, not the tables.

- `python3 "<SKILL_DIR>/scripts/sync_terms.py" --check` — read-only; reports `MATCH` / `DIFF` / `NOT_INSTRUMENTED` per section.
- `--coverage` — which reference rows have no workbook entry yet.
- `--write` — rewrite the marked blocks; never touches text outside them.
- `--instrument` — one-off, wraps an unmarked table body in `<!-- AUTO:BEGIN <loc> -->` / `<!-- AUTO:END <loc> -->`.

Only the first three columns of each table are generated. Every later column (clause notes, value slots, functions, key-clause rules) is human-maintained and preserved by Chinese-term key. The hidden `目标位置` column in the workbook selects the target section; unknown values abort the run. Workbook lookup order: `--xlsx`, `$CHINT_TERM_XLSX`, repository-relative path.

