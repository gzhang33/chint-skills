# Preserve-Content Shell Rebuild

This runbook handles the case where the user explicitly keeps source content pages intact while applying the CHINT presentation shell.

## Inspect the source

Read slide text, order, dimensions, notes, links, tables, chart data, embedded objects, and visible artwork from the original file. Classify actual shell pages separately from content pages. Treat raster graphics as unreadable source objects; do not reconstruct product data from their pixels.

Infer chapter groupings from source headings and existing divider pages. Keep source order. Continue when boundaries are clear. Ask only when more than one plausible grouping would materially change the contents page or divider placement.

Map retained source content pages into chapters, the intro, or standalone pages. The analyzer identifies replaceable shell pages. Keep retained content in source order. Keep output path distinct from input and save a name derived from the source file, such as `source_CHINT.pptx`, in the user's output directory.

## Prepare and run the configuration

Read `preserve_source_pages_sop.md` for the configuration invariants. The engine uses the supplied source deck as its canvas; it does not substitute `assets/templates/26年模板拓新体.pptx`. New shell artwork uses media under `assets/media/`, including `chapter_26_bg_clean.jpg` for dividers.

The minimum JSON contract requires an existing `source` deck, a `blank_layout` name available in that deck, and a non-empty `chapters` list. Each chapter needs `num`, `name`, and `pages`; page numbers refer to the source deck and start at one. Every source page must appear exactly once: retained pages go in `intro`, `standalone_pages`, or `chapters`; replaceable shell pages go in `remove_source_pages`. Keep retained pages in source order.

The analyzer's shell-page classification determines which source pages are replaced; config does not override that classification. Review the result against the source and ask when a page's role is ambiguous.

```json
{
  "source": "/path/to/source.pptx",
  "blank_layout": "仅标题",
  "remove_source_pages": [1, 2, 3, 6],
  "chapters": [
    {"num": "01", "name": "填写原稿章节标题", "pages": [4, 5]}
  ]
}
```

The page numbers and chapter in this example illustrate the shape only; replace them with the source-backed page map. Set `blank_layout` to an exact layout name from the supplied source deck; the engine checks this before analysis or writing scratch files. `source` and `output` must resolve to different files. When omitted, `output` defaults to `<system Documents>/CHINT-PPTX/<source>_2026VI.pptx`; `CHINT_PPTX_OUTPUT_DIR` can override that directory. Never write a deck or report inside the skill folder.

Optional config belongs only where needed: `intro` can map one lead page and needs a `label`; `standalone_pages` needs a reason and is limited to source pages before the first chapter; `title_grid.promote_heading_pages` declares headings to promote; `footer.skip_pages` and `no_shift_pages` declare verified page exceptions. The bundled backgrounds and badge resolve from the skill directory without an `assets` block. For other supported options, read `scripts/shell_rebuild_engine.py` `validate_config`.

Write the validated configuration and scratch reports outside the skill folder. Run the engine from the skill root so its relative inputs resolve consistently:

```bash
python3 scripts/shell_rebuild_engine.py <config-path> --json <user-output-dir>/run_report.json
```

Use the same Python 3.11-or-newer interpreter that passed `scripts/check_environment.py`. Keep the generated `.baseline.json` beside the output; it records engine-authorized shell changes.

## Review and deliver

Require `[PASS]` from both the outer-shell inspection and source-fidelity verification. Run the OpenXML validator with the source file as its baseline. Inspect every rendered page for a displaced title, overlapped content, incomplete contents list, incorrect page number, extra logo, placeholder text, missing font, and truncation.

If a gate fails, fix the configuration or engine. Never turn a failed result into a pass by adding broad page exceptions. Do not claim semantic accuracy from shape-preservation results. Use `scripts/verify_content.py` and page-by-page source review for a restructure or an edit.

When the gates pass, provide a short Chinese delivery note with the new `.pptx` link, the requested changes, and the verification performed. Preserve the original source file.
