# Electrical Catalogue & GB/IEC Compliance Guide

Load this reference when auditing a CHINT electrical catalogue, datasheet, or manual — regardless of file format (`.pdf`/`.docx`/`.xlsx`/`.pptx`/JSON trigger `doc_type=catalogue` automatically at ≥2 distinct electrical signals in the first 400 text units, while `.md`/`.doc`/`.xls`/`.txt` always carry format-based `doc_type` and select this guide by subject) — or whenever `--with-iec` / `L3` standard compliance is requested.

## 1. Domain Rule Architecture & Calibration

- **Vocabulary vs Generic Detectors**: Product-line vocabulary (Chinese typo lists, same-page conflict groups, cross-page synonym groups, symbol/case notation) lives in [catalog_rules.json](../catalog_rules.json), while `audit_catalog.py` holds only generic algorithms (SI-unit casing such as `50KA`/`60HZ`, numeric-range sanity, `Ics ≤ Icu`, `In ≤ Inm`, `Ue ≤ Ui`, `Ui`/`Uimp` checks, bracket pairing, numbering sequences, page-ref bounds, duplicated words). Add new product-line terms to JSON rather than patching single-catalogue cases into Python so the engine stays reusable across lines.
- **Peer-Valid Legacy English (`L1` vs `L2`)**: Forms that peers legitimately use (`drawer`, `closing electromagnet`, `shunt opening release`, `shunt trip`, `separation position`) are downgraded via `severity_overrides` to `EN_TERM_CONSISTENCY` (`L2`) — canonical replacements are `Closing release (CEM)`, `Shunt release (SHT)`, `Earth current transformer (ECT)` (full blacklist lives in `audit_catalog.py` / `chint-translation`). Suppressing them at `L1` keeps the default pass focused on indisputable errors (`Earch`, `XF`/`MX` competitor codes, `Selectivity category A + Isd` without `Icw`) while still surfacing consistency drift during `L2` publish review.
- **Competitor Code Scope**: `COMPETITOR_CODE` targets CHINT catalogues mixing in Schneider/ABB accessory codes (`MX`, `XF`, `MN`, `SDE`, `MCH`, `KLC`). When auditing a competitor catalogue as external reference, pass `--external-reference` to disable `COMPETITOR_CODE` checks (`--dept mccb` skips only ACB-specific codes while common codes `MX`/`MN`/`SDE` still run); the engine also auto-suppresses `COMPETITOR_CODE` when the first 400 units carry zero CHINT identifiers and three or more peer brand mentions, preserving protection for CHINT catalogues that merely mention a peer once.
- **PDF Rating Tables (`P<n>:Table`)**: On `.pdf` inputs, `Page.find_tables()` runs only on pages matching rating tokens (`Icu`/`Ics`/`Inm`/`Icw`/`Ue`/`Ui`/`Uimp`/`额定`/`壳架`/`分断`), scanning a 120-page catalogue in ~3 s instead of ~50 s. Table findings use locator `P<n>:Table` and cannot be anchored for automated PDF highlighting, so flag them for manual layout edits.
- **Normative Traceability**: Standard attributions (GF 1001, GB/T 15834/15835, GB/T 2900.18, GB/T 14048.2—2020, IEC 60947-2:2024, IEC 62423, SI Brochure, ISO 80000-2) and corpus calibration evidence live in [sources.md](../sources.md). Never guess a clause or standard not listed there.

## 2. GB/IEC Compliance Overlay (`--with-iec` / `L3`)

- Pass `--with-iec --dept <acb|mccb|all>` on `L1` (strict errors + statutory checks) or `L2` (identical to `--profile L3`).
- When sibling `chint-translation` is installed, live IEC 60947-2:2024 / GB/T 14048.2—2020 SSOT rules load automatically and `<SKILL_DIR>/../chint-translation/scripts/glossary_lookup.py` can cross-check clause-level Chinese/English statutory terms (`使用类别 A` → `选择性类别 A`, `结构差异` → `结构段`, `闭合电磁铁` → `闭合脱扣器`, `万能式断路器` → `空气断路器（分类：万能式）`, `功率损耗` → `功耗`). When standalone, the parity-tested built-in SSOT fallback enforces identical checks.

## 3. Catalogue Semantic Verification Checklist

Sweep only the sections matching the active profile:

- **`L1` — Strict Errors & Layout Semantics (Default)**:
  - **Page / Box Header Mismatch**: Section headers copied from an unrelated frame or trip-unit chapter (e.g., an ETU screen page carrying a circuit-breaker frame header).
  - **Prose vs Table Contradictions**: Numeric steps, rated currents, or delay times in prose disagreeing with the adjacent rating table.
  - **Inverted Protection / Condition Bounds**: Safety or enclosure bounds stated backwards (`不超过 IP20` instead of `不低于 IP20` — route to Pending Verification List).
  - **Count & Header Integrity**: Stated counts disagreeing with the list below (`4 个主题菜单` with 5 items); duplicate adjacent table column headers where distinct states belong (two `绿色闪烁` columns); single-value ranges (`4000~4000`); unexplained shorthand (`无 bs 脱扣器`).
  - **Diagram vs Note Alignment**: Notes on dashed wiring, pushbuttons (`SB1/SB2`), or terminal legends contradicting the figure or sibling frame sections.
  - **Visual-Only Pages (`low_text_pages`)**: Inspect every listed page visually for cover copy, exploded-view callout numbers, and embedded diagram labels.
- **`L2` — Publish Consistency**: Verify cross-section naming, accessory terminology, symbol casing, and legend conventions align across the whole catalogue.
- **`L3` & `--with-iec` — Substantive GB/IEC Compliance**: Confirm selectivity categories, breaking-capacity relationships, and statutory terms match clause wording without violating verified ratings.
- **Pending Verification List Discipline**: Never guess or silently alter technical ratings. Isolate ambiguous specs, prose-vs-table conflicts, reversed safety bounds, undefined abbreviations, and statutory wording choices with exact page and line/table anchor.
