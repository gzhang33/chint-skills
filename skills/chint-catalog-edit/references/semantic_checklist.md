# Catalogue Semantic Verification Checklist (`semantic_checklist.md`)

> **Scope**: Apply ONLY the sections matching the active profile (`L1` default, `L2`, `L3`, or `--with-iec`). Mechanical regex rules live solely in `scripts/audit_catalog.py` (and sibling `chint-translation/scripts/lint_text.py` for IEC/GB SSOT); this checklist covers **semantic, layout, and cross-table defects** that regex cannot detect.

## 1. `L1` — Strict Errors & Semantic Defects (Default)

- **Page / Box Header Mismatch**: Page title or frame header copied from an unrelated section (e.g., an ETU user-interface page carrying a breaker frame header).
- **Prose vs Table Contradictions**: Numeric steps, ratings, or delay values in body text disagreeing with the adjacent parameter table.
- **Inverted Protection / Condition Bounds**: Safety or enclosure conditions stated backwards (e.g., `不超过 IP20` instead of `不低于 IP20` — route to Pending Verification List).
- **Count & Header Integrity**:
  - Stated item count disagreeing with the actual list below (e.g., `4 个主题菜单` followed by 5 menu names).
  - Adjacent table columns sharing identical headers where distinct states belong (e.g., two columns both headed `绿色闪烁`).
  - Single-value range artifacts (`(4000~4000)`) or unexplained shorthand (`无 bs 脱扣器`).
- **Diagram vs Note Alignment**: Notes describing line styles or pushbutton codes (`虚线部分`、`SB1/SB2`) that contradict the actual wiring diagram or other frame sections.
- **Visual-Only Pages (`low_text_pages`)**: Inspect every low-text page visually to verify cover text, exploded-view callout numbers, and embedded diagram labels.

## 2. `L2` — Publish Consistency (Manual Profile)

Add on top of `L1`:
- **Cross-Section Naming Alignment**: Ensure product/accessory terminology, symbol casing, and legend conventions remain uniform across product-line sections when preparing a release.

## 3. `L3` & `--with-iec` — Substantive GB/T & IEC Compliance

Add on top of the active base profile:
- **Standard Clause & Concept Verification**: Verify that technical claims, selectivity categories, and statutory Chinese/English terms align with `chint-translation/scripts/glossary_lookup.py` and IEC 60947-2:2024 / GB/T 14048.2—2020.

## 4. Pending Verification List Discipline

Never guess or silently alter technical facts. Move any item requiring PM/R&D confirmation (ambiguous numbers, conflicting tables, reversed safety bounds, undefined abbreviations, or statutory wording policy choices) into the Pending Verification List with exact page and line/table anchor.
