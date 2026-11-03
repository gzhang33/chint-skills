# Preserve Source Pages: Contract and Limits

Use this workflow only when the user explicitly asks to keep source content pages unchanged. A supplied PowerPoint file alone does not select it. For edits to the narrative, body content, layout, or page order, use `create_edit_workflow.md`.

## Source and output

- Keep the source presentation unchanged and save a separate output file.
- Preserve source content pages, data, chart series, tables, wording, images, ordering, and geometry.
- Replace or add only the CHINT cover, contents page, chapter dividers, closing page, and the approved interior shell elements.
- Use the clean chapter artwork. Keep the template cover and closing artwork's existing logo and copyright marks.
- Badge placement and font normalization follow the CHINT assets section of [quality_and_environment.md](quality_and_environment.md); do not restate the rule here.
- If a content object cannot be safely preserved, leave the source presentation unchanged and report the specific blocker.

## Configuration and mapping

The configuration is checked by `scripts/shell_rebuild_engine.py`. Map retained content pages into a chapter, `intro`, or `standalone_pages`, and keep them in source order. The analyzer classifies replaceable shell pages; config does not override that classification. Confirm only when the source leaves a consequential page role or chapter boundary ambiguous.

Do not silently delete source pages, move content, adjust table columns, restyle charts, or rewrite claims. Remove a page only when the user asked for it or its content is clearly a replaceable cover, contents, or divider page. Do not create user-confirmed fact changes in a preserve-pages task.

Use the minimum config example in `preserve_source_pages_runbook.md` and the schema enforced by the engine. Keep source and output paths distinct. Assets resolve from the skill directory.

## Verification

- Run `scripts/inspect_pptx.py` on the result for CHINT font coverage, interior badge presence, and package structure.
- Run `scripts/verify_preserve_source.py --source <source.pptx> --target <output.pptx> --baseline <output.pptx.baseline.json>`. Require `[PASS]` before describing source pages as preserved.
- Run `scripts/office/validate.py <output.pptx> --original <source.pptx>` to compare OpenXML findings against the source.
- Render and inspect every output slide. Open and save a representative file in PowerPoint and WPS with 正泰拓新体 installed.

The source-fidelity gate checks page mapping, shape identity, native chart categories, series, values, number formats, axis titles, and embedded workbook cells, along with its documented geometry invariants. It does not prove that raster content was interpreted correctly or that a restructured deck retained meaning.
