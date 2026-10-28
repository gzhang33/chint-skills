---
name: chint-pptx
description: "Create, restructure, or improve CHINT electrical-distribution product presentations with the existing CHINT 2026 template and source-backed content. Use this domain skill instead of generic deck generators for CHINT product presentations."
---

# CHINT Product Presentation Skill

Build editable Chinese-first presentations for product managers in CHINT's electrical-distribution team. Use the included 2026 template, CHINT brand assets, and CHINTinno fonts. Keep product facts anchored to the user's source material.

## Route each request

For native CHINT PowerPoint work, this skill takes precedence over generic PPT or presentation workflows. Reuse the most specific existing CHINT generator below; do not create a parallel generation script.

Use the most specific existing CHINT generator: sales or product analytics reports go to `chint-data-analysis`; RAT one-page forms go to `chint-pm-RAT`; Top3 chart-logo updates go to `ppt-chart-top3-logo-inserter`. Use this skill for CHINT product presentations. Use `chint-brand-design` for brand guidance, not as a second PPTX generator.

| User request | Workflow |
|---|---|
| Create a deck from a brief, product materials, or an outline | Read [references/create_edit_workflow.md](references/create_edit_workflow.md). Build a concise narrative and use the active [layout archetype guide](references/layout_archetypes.md) to compose the pages. |
| Restructure an existing deck or rebuild its narrative and page order | Read [references/create_edit_workflow.md](references/create_edit_workflow.md). Inspect the source, map its facts and objects, then reorganize pages to fit the requested outcome. |
| Improve an existing deck while retaining its structure | Read [references/create_edit_workflow.md](references/create_edit_workflow.md). Inspect targets and use the existing `--edit-config` mode for supported text, table-cell, style, and geometry edits. |
| Change the visual shell while preserving every source content page | Read [references/preserve_source_pages_sop.md](references/preserve_source_pages_sop.md) and [references/preserve_source_pages_runbook.md](references/preserve_source_pages_runbook.md). Run the source-fidelity gate. |

Use the existing creation engine for new and restructured decks. Do not create a task-specific PPTX generator script:

```bash
python3 scripts/chint_pptx_engine.py --config <payload.json> --output <absolute-output-path>
```

The legacy positional form remains supported. For environment setup, validation, rendering, and PowerPoint/WPS checks, read [references/quality_and_environment.md](references/quality_and_environment.md).

For supported local edits, use `scripts/inspect_pptx.py <source.pptx> --edit-targets` and the engine's `--edit-config` mode. Keep the source deck unchanged. Do not add a parallel generator when an existing route lacks a requested operation; report the gap.

## Content rules

- Adapt framing, evidence, detail, and recommendations to the audience and stated purpose. Do not force every deck into a preset business narrative.
- Treat product names, electrical ratings, standards, certification, performance, prices, dates, and quantitative claims as source-backed facts. Never fill gaps with plausible specifications or sample metrics.
- Keep source facts attached to their product, condition, unit, time range, and comparison basis. Distinguish source statements, transparent calculations, and unanswered questions.
- When a source is incomplete, omit unsupported claims or ask only for missing information that blocks the requested conclusion.
- Preserve unrequested content and source assets during local optimization. A full restructure may change story, sectioning, page order, and slide boundaries while carrying source facts forward.

## Brand and editing rules

- New and fully restructured decks use `assets/templates/26年模板拓新体.pptx` as their canvas. A local optimization keeps the source canvas.
- Use template positions for the cover and closing marks. Keep one CHINT mark in the upper-right on contents and body slides; omit it on chapter dividers.
- Keep the contents page to one page. Reuse the template's native contents layout and adapt row spacing and title sizes to the entry count; shorten section titles when they cannot fit legibly. The engine accepts up to 12 entries on that page.
- Use 正泰拓新体 for editable presentation text, including tables, grouped shapes, charts, and chart labels. The receiving computer must have the CHINT fonts installed.
- Before creating, restructuring, or editing a deck, run `scripts/check_environment.py`. If it reports missing installed CHINT fonts, stop and ask the user to install all three fonts from `assets/fonts`. After approval, `python3 scripts/check_environment.py --open-font-installer` opens Font Book on macOS or Windows font previews; the user completes the install. Restart Office, rerun the check, and resume only when it passes. Do not install silently, request administrator access, or embed fonts automatically.
- Prefer native PowerPoint text, shapes, tables, and supported data charts. Keep product photography and complex graphics as images only when a native editable representation would materially reduce clarity; disclose that limitation.
- Never flatten an editable chart merely to simplify generation. Preserve chart series, category labels, units, and source data.
- Keep the uploaded file unchanged. Save generated payloads, decks, previews, reports, and scratch files outside this skill folder. Use a task-provided output location when available; otherwise use the operating system's Documents folder under `CHINT-PPTX`, or `CHINT_PPTX_OUTPUT_DIR` when configured. Pass an absolute output path when creating or restructuring decks; local edit mode uses this default when `--output` is omitted. Return a clickable link to the saved deck.

## Resources

- [references/create_edit_workflow.md](references/create_edit_workflow.md): creation, restructuring, scoped edits, and fact protection.
- [references/quality_and_environment.md](references/quality_and_environment.md): runtime, editable-content, structural, visual, and PowerPoint/WPS checks.
- [references/layout_archetypes.md](references/layout_archetypes.md): available layout vocabulary for the payload-driven generation engine.
- [references/vi_and_typography.md](references/vi_and_typography.md): rationale and token names. Numeric brand values live in `spec/brand_tokens.json`.
- [references/preserve_source_pages_sop.md](references/preserve_source_pages_sop.md): strict source-page preservation contract; use only for explicit preserve-content requests.
- [references/asset_library_guide.md](references/asset_library_guide.md): read only when selecting map, icon, or media assets.
- [references/maintenance_and_environment.md](references/maintenance_and_environment.md): read only when maintaining or synchronizing this skill.
- [references/delivery_editability_checklist.md](references/delivery_editability_checklist.md): read only when a user reports an opening, editing, or saving problem on macOS or Windows.
