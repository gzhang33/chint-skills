# Document Semantic Verification Checklist (`semantic_checklist.md`)

> **Scope**: Sections 1–4 assume a printed product catalogue. For `doc_type=office-generic` / `markdown` / `legacy-binary` (meeting notes, notifications, product intro decks, quote sheets), run section 5 instead of the layout-dependent items in section 1. Apply ONLY the sections matching the active profile (`L1` default, `L2`, `L3`, or `--with-iec`). Mechanical rules live in `scripts/audit_catalog.py` (generic detectors: SI-unit casing, numeric-range sanity, `Ics`/`Icu` relations, bracket pairing, figure/table numbering, page-reference bounds, duplicated words) and `references/catalog_rules.json` (catalogue vocabulary: typos, same-page conflicts, cross-page synonym groups, case/notation). This checklist covers **semantic, layout, and cross-table defects** that regex cannot detect.

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

## 5. Generic Office Documents (`office-generic` / `markdown` / `legacy-binary`)

Meeting notes, notifications, product intro decks, quote sheets. The same `L1`/`L2` engine runs here, so expect domain-rule hits that do not belong to the file — read them with the `doc_type` expectation, do not delete them silently.

**Still applies** (mechanical rules already catch most of these; verify the semantic layer on top):

- **Count & Header Integrity**: "三项要求" followed by four items; a table caption naming columns that differ from the header row; a summary slide whose stated totals disagree with the detail slides.
- **Numbering & Sequencing**: skipped agenda/step numbers, duplicated section numbers, "第一步/第二步" ordering that contradicts the body order, figure/table numbers referenced but never defined.
- **Prose vs Table / Prose vs Slide Contradictions**: body text "12 月 1 日截止" against a table cell "12 月 5 日"; a bullet claiming a figure the chart does not show.
- **Stated vs Actual Lists**: "共 5 家供应商" where the list holds 4; a named-owner column with a blank owner; an agenda item with no matching section.
- **Internal Identifier Consistency**: product/part codes, department names, project codes spelled two ways in the same document (the `L2` term-drift detectors cover the generic case).
- **Legacy `.doc`/`.xls` Caveats**: OLE2 extraction is best-effort — a run that exits `2` means the file was never audited, so report the parse error and the `.docx`/`.xlsx` conversion suggestion, never "0 errors". `.xls` locators (`X<sheet>:R<row>`) carry the workbook's own sheet name (`X内销工厂数据新增模板:R120`) and a 1-based row; always quote the row's text as well, since hidden rows shift nothing but merged cells collapse into one line. `.doc` locators (`D<n>`) are paragraph indices in extracted order with no page number — quote the surrounding sentence.

**Does not apply** (layout assumptions a catalogue has and these files do not):

- **Page / Box Header Mismatch** — a deck or a memo has no running box header copied per section; flag it only if a slide title visibly disagrees with its own content.
- **Exploded-View Callouts & Diagram-vs-Note Alignment** — illustrative diagrams in decks carry no numbered callout legend to cross-check; a `low_text_pages` slide with a diagram is verified as an image, not against a parts list.
- **Electrical ratings table cross-checks** (`Ics`/`Icu`, `Ue`/`Ui`) — they fire only when the file actually states those symbols; on a quote sheet the electrical vocabulary is incidental.
