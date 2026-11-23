---
name: chint-office-suite
description: Extract structured text and visual-page maps from .pdf/.docx/.xlsx files, or write non-destructive PDF review annotations. Use for catalogue I/O, when another skill needs office extraction/annotation, or to route generic office authoring.
---

# CHINT Office Suite (`chint-office-suite` v0.0.1)

## Step 1 — Format Gate & Office Skill Routing

1. Inspect file extension and target deliverable:
   - **`.doc` / `.xls` legacy binaries**: Request conversion to `.docx` / `.xlsx` before parsing.
   - **Authoring / layout editing** (`.xlsx` formulas/pivot tables, `.docx` styling/redlines, `.pdf` splitting/merging/form filling): Route to installed general office skills (`pdf`, `docx`, `xlsx`).
   - **Scanned / image-only PDF pages**: Route `low_text_pages` from Step 2 to `smart-ocr` or `tencentcloud-ocr` (or visual page inspection).
2. *Done when*: Format validated and authoring vs extraction route selected.

## Step 2 — Structured Extraction (`extract_doc.py`)

1. For PDFs exceeding 20 pages, inspect page map and recommended batch ranges first:
   - `python3 scripts/extract_doc.py <source_file> --summary [--json]`
2. Extract structured `chint-office-extract/v1` JSON (`P{n}:L{m}` for PDF, `document:P{n}` / `header1:P{n}` for Word, `Sheet!Cell` for Excel; flags PDF pages `<50` chars in `low_text_pages`):
   - `python3 scripts/extract_doc.py <source_file> [--pages <range>] --json`
3. *Done when*: Extraction JSON returned with `total_units`, `scanned_units`, `low_text_pages`, and `units`.

## Step 3 — Non-Destructive PDF Annotation (`annotate_pdf.py`)

1. Consume a `chint-office-annotate/v1` JSON list or `{"annotations": [...]}` (`page`, `search` or `searches`, `comment`, optional `match_mode`: `all` | `merged` | `first`, optional `author`). Pipe JSON directly via `--annotations -` to avoid extra files on disk.
2. Run: `python3 scripts/annotate_pdf.py <input.pdf> --annotations - [--output <out.pdf>] [--author <name>]`
   - Writes strictly to a single new PDF copy (`<stem>_annotated.pdf` by default), preserving `<input.pdf>` untouched and keeping all pre-existing annotations.
   - Applies unified yellow `Highlight` (`all` marks every occurrence on the page; `merged` binds multiple hits into one linked sidebar annotation) and falls back to staggered yellow margin `Sticky Note` preserving `[label] comment` (`sticky_fallback_count` & `fallback_items` tracked).
3. *Done when*: New annotated PDF copy written, source PDF untouched, and `matched_items + sticky_fallback_count == total`.

## Step 4 — Completion Gate

- Original file untouched; zero stray sidecar files created when piped; any `low_text_pages` and `fallback_items` explicitly surfaced; `chint-office-extract/v1` / `chint-office-annotate/v1` schemas preserved verbatim.
