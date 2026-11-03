# Create, Restructure, and Improve a Presentation

## Read the request and sources

Identify the intended audience, decision or communication outcome, source files, and any required presentation length. Treat these as inputs, not a fixed deck type. Read relevant product sheets, specifications, analysis, and existing slides before drafting claims.

Build a short fact inventory before layout work. Include product/model identifiers, ratings, units, applicable conditions, standards, dates, cited comparisons, and quantitative evidence. Track where each fact came from. Separate confirmed facts, calculations with visible methods, and missing evidence. Never reuse the generator's old sample data as a business claim.

If required input is missing, continue with the parts supported by evidence. Ask one focused question only when the gap changes the recommendation, product selection, safety claim, or numeric conclusion.

## Create from a brief

Draft the story for the particular request. Give each slide one job, then pick its form from what the reader has to do with the information — scan a list of values, or read a change over time. Only the archetypes in [content_contract.md](content_contract.md) exist; there is no process, roadmap, architecture, or case-study layout to select, so a request shaped like one of those becomes a table page whose columns carry the sequence or the comparison.

Create a cover, one contents page, chapter dividers where useful, editable body pages, and a closing page from the CHINT template. Cover, chapter divider and closing are built on their template layouts (`标题幻灯片`, `节标题`, `末尾幻灯片`), so their artwork stays native; contents reuses the template's original contents page. Adapt contents row spacing and title font sizes to the entry count; shorten or group section names when they cannot fit legibly. The engine rejects lists past `TOC_MAX_ENTRIES` instead of creating a second contents page. Use native PowerPoint charts for supported chart types and supply the complete categories, series, and units.

The current JSON engine accepts an object with a `slides` array. Each slide supplies an explicit `archetype` and required source-backed fields for that layout. Read [content_contract.md](content_contract.md) for the supported archetypes and payload fields. The engine rejects unknown archetypes and missing required data rather than filling in sample facts.

The archetype catalog summarizes payload fields; `scripts/chint_pptx_engine.py` `_validate_slide_payload` is the authoritative required-field check. Cover `date` and `author` are optional and render when supplied. `ARCH_11_CLOSING` takes no payload fields: its layout already carries the KV, THANKS, the group mark and the copyright line, and the engine draws nothing on top. A radar chart needs the category count the engine validates and one finite numeric value per category and series. Every retained chart (bar-trend, donut, radar) is a native editable PowerPoint chart; there is no raster chart path.

## Restructure an existing deck

Keep an untouched source copy. Extract editable text, table cells, native chart categories and values, notes, links, and slide order before redesigning. Identify embedded objects or complex visuals whose contents cannot be recovered reliably; retain those source objects unless the user provides editable source data.

Map source facts to their destination slides before changing page order. Keep model-rating-unit relationships, qualifiers, and comparison periods intact. Cite added conclusions to supplied material; label calculations with their basis. Do not infer numeric chart values from an image. The engine does not import arbitrary source-slide objects, so plan around that limitation rather than assuming a page survives the rebuild; when source pages and their objects must remain unchanged, use the preserve-content shell workflow.

Rebuild the deck from the source-backed payload on the included CHINT template. The engine carries forward only what the payload describes; report any source objects it could not carry. Apply the shared CHINT font, colors, page furniture, and interior logo. Save to a new output file.

## Improve an existing deck

Keep its page order and message unless the user asked to change them. Correct copy, text fit, typography, color, paragraph alignment, and supported text-box or table geometry. Keep chart data, chart labels, and complex objects unchanged; report requested edits outside the supported scope.

Scope edits to the user's request. Do not restate current metrics, product claims, or recommendations from memory. If a correction changes a source fact, record the specific user-provided source for that correction in the review manifest.

For local edits, use the existing edit mode in `scripts/chint_pptx_engine.py`; do not create a task-specific generator script or edit OOXML by hand. First run `scripts/inspect_pptx.py <source.pptx> --edit-targets` and use its source hash, slide part, shape ID, name, and text as edit-manifest guards.

The edit manifest supports unique text replacements across adjacent runs within one paragraph, full-target replacements across paragraphs, table-cell text, text style changes, paragraph alignment, and text-shape or table geometry. Partial replacements cannot cross an existing paragraph or line break; line breaks in their `to` value stay within that paragraph. For a full-target replacement, `\n` creates paragraphs and `\v` creates an in-paragraph line break. Empty `from` is allowed only when the target text is empty, so existing blank text shapes and cells can be filled. Full-target replacements preserve paragraph properties when possible; fields, hyperlinks, and custom paragraph markup are rejected. The engine edits only supported text shapes and tables; chart data and complex objects remain untouched. It rejects grouped shapes, merged cells, ambiguous matches, and unsupported object types. For overflow corrections, adjust font size or box geometry from the rendered preview, then render and inspect again. Do not claim an unsupported edit succeeded; report the limitation.

Run the manifest through the existing engine. Output location, Windows Documents resolution, and the `CHINT_PPTX_OUTPUT_DIR` override are defined once in [quality_and_environment.md](quality_and_environment.md) Runtime; with no override the edited deck lands there under `<source-name>_edited.pptx`. Close an existing destination deck in PowerPoint before replacing it; a locked destination fails safely and leaves the source untouched.

```bash
python3 scripts/chint_pptx_engine.py --edit-config <edit-manifest.json>
```

The manifest contains `source`, `source_sha256`, and an `edits` array; `output` is optional. Copy the source hash and each target's `slide`, `slide_part`, `shape_id`, `shape_name`, and `target_type` from the inventory. For text shapes, use the inventory's `text` as `expected_text`; for a table-cell edit, use that cell's text. Each edit may include `replace_text` with exact `from`/`to` strings, `cell` with zero-based `row`/`column`, `style`, or `geometry_in` in inches. A partial `from` must occur exactly once inside one paragraph; a full-target `from` must equal `expected_text` and may span paragraphs. `style` accepts `font_family`, `font_size_pt`, six-digit RGB `font_color`, `alignment`, `bold`, and `italic`. Geometry must stay within slide bounds. The engine rejects stale hashes, mismatched target text, ambiguous matches, and unsupported objects before writing output.

Do not overwrite the source deck. If a requested change needs chart-data editing, SmartArt/OLE changes, or grouped-shape edits, stop and explain the missing capability rather than creating a parallel generator.

## Preserve-content shell rebuild

Use the analyzer and shell engine only when the user asks to keep all content pages unchanged. Follow `preserve_source_pages_sop.md` and `preserve_source_pages_runbook.md`. Report content preservation only after the source-fidelity gate passes; that gate does not validate a full restructure or a content edit.
