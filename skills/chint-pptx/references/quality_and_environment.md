# Runtime and Presentation Quality

## Runtime

Use one Python executable for generation and every check in the same run. It must be Python 3.11 or newer and have the packages listed in `requirements.txt`. Run `python3 scripts/check_environment.py` before a deck task. If the interpreter or a required package is missing, select a compatible environment and rerun the check; do not switch interpreters between generation and validation. Run the font check described under [Font installation](#font-installation) and stop there if it fails.

The engine, renderer, and validators resolve assets relative to their own files. Run project commands from the skill root so relative input paths have one clear base. Every workflow — creation, restructure, edit, and shell rebuild — writes outside the skill folder: to a task-provided path when there is one, otherwise to a `CHINT-PPTX` directory under the operating system's Documents folder, or to `CHINT_PPTX_OUTPUT_DIR` when that variable is set. On Windows this resolves the real Documents location, including a redirected one. The quality-check script reports the interpreter and missing packages.

## Font installation

The three files under `assets/fonts/` (`CHINTinno-Regular.ttf`, `CHINTinno-Bold.ttf`, `CHINTinno-Light.ttf`) must be installed for the current user before any deck is generated or edited, and on any machine that will open the result. `scripts/check_environment.py` verifies that each one is registered with macOS CoreText or the Windows font registry and names the missing files.

When fonts are missing, stop and ask the user to install them. On approval, `python3 scripts/check_environment.py --open-font-installer` opens Font Book on macOS or the Windows font preview so the user can complete a current-user installation. Restart Office, rerun the check, and resume only when it passes. Never install silently, request administrator access, or embed the fonts in the deck.

## Editable content and evidence checks

- Check the original source and final deck side by side. Carry native text, table cells, chart values, units, notes, and links forward when the requested edit leaves them in scope.
- For a local edit, list stable targets with `scripts/inspect_pptx.py --edit-targets` and apply a JSON manifest through `scripts/chint_pptx_engine.py --edit-config`. The engine patches only selected text shapes or table cells, verifies the source hash and target text, and copies all other package parts unchanged. Unsupported chart or complex-object edits fail before output is written.
- Pass the source deck as the validator baseline for a local edit. Inspect the rendered changed slides and confirm source pages remain unchanged outside the approved text/style/geometry operations.
- Prefer PowerPoint native charts for supported data charts. Inspect category labels, each series, chart units, and any underlying data workbook. Complex image graphics do not preserve an editable chart's data.
- The retained chart layouts (`ARCH_16_CHART_BAR_TREND`, `ARCH_17_CHART_PIE_DONUT`, `ARCH_16_RADAR`) all produce native editable charts. The engine has no raster chart path.
- Preserve unreadable or unsupported embedded objects as source objects. Do not derive product facts from raster images.
- Inspect every editable run in shapes and tables for 正泰拓新体. Inspect native chart labels, categories, values, legend, and units separately. A font name in the presentation theme alone does not prove coverage.
- The local `scripts/verify_content.py` command compares source and target product-model and numeric evidence when restructuring or editing source content. It reports unmatched items for review; it cannot prove that a rewritten claim keeps its original meaning.
- For a preserve-content shell rebuild, run `scripts/verify_preserve_source.py` with the source, target, and generated baseline. This gate checks source-page preservation only. It is not evidence for a restructure or content edit.

## File and render checks

Run the package validator on every final deck. Pass the original deck to `scripts/office/validate.py --original` for template-derived output so inherited template findings remain distinguishable.

Extract the final slide text and inspect for lost content, wrong order, empty titles, and instructional placeholders such as “单击添加” or “TODO”. Run `scripts/render_preview.py` with an output directory under the user's output folder to render a PDF, every slide as an image, and a contact sheet. Inspect each slide at full resolution. Check text fit, overlaps, logo placement, page edges, tables, chart labels, color contrast, and content density. Correct the source payload or generation code, then regenerate and inspect the final render.

Open representative new, restructured, and edited samples in Microsoft PowerPoint and WPS Presentation. Confirm that both open and save the file without repair prompts, fonts are present on the receiving device, native charts remain editable, and page layout remains intact. Record the tested operating system and application versions. Do not claim Windows save compatibility from checks performed only on macOS. Automated OpenXML checks do not replace these application checks.

When a user reports that a deck cannot open, edit, or save on macOS or Windows, read [delivery_editability_checklist.md](delivery_editability_checklist.md). Use its platform-specific troubleshooting only for the reported failure; do not treat local security or file-system changes as a routine delivery step.

## CHINT assets

- Cover and closing backgrounds already include their official-position brand marks. Keep those marks in place.
- Omit the upper-right badge on chapter dividers. Reuse an upper-right CHINT badge inherited from the slide layout or master on other inner pages; add a slide-level badge only when no visible inherited mark exists or slide artwork covers it. `scripts/inspect_pptx.py` counts effective marks across slide, layout, and master layers.
- The font files are covered under [Font installation](#font-installation). Do not embed them by default.
- `assets/media/chapter_26_bg_clean.jpg` is a legacy flat-bitmap divider kept for the shell
  rebuild path only. The creation engine builds chapter pages on the `节标题` layout, so the
  band, gradient and accent line stay native; do not paste the bitmap over it.
- `spec/brand_tokens.json` is the only VI color and font-token source.
