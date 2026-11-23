---
name: chint-office-suite
description: Extract structured text and visual-page maps from .pdf/.docx/.xlsx, write non-destructive PDF review annotations, or route generic office authoring — standalone or when another skill calls it.
---

# CHINT Office Suite (`chint-office-suite` v0.0.1)

## Step 1 — Format Gate & Routing

1. Inspect file extension and target deliverable:
   - **`.doc` / `.xls` legacy binaries**: Request conversion to `.docx` / `.xlsx` before parsing.
   - **Authoring / layout editing** (`.xlsx` formulas/pivot tables, `.docx` styling/redlines, `.pdf` splitting/merging/form filling): Route to installed general office skills (`pdf`, `docx`, `xlsx`).
   - **Scanned / image-only PDF pages**: Route `low_text_pages` from Branch A to `smart-ocr` or `tencentcloud-ocr` (or visual page inspection).
2. *Done when*: Format validated and active branch (`Branch A` extraction vs `Branch B` PDF annotation vs external office skill) selected.

## Branch A — Structured Extraction (`extract_doc.py`)

1. For PDFs exceeding 20 pages, inspect page map and recommended batch ranges first:
   - `python3 scripts/extract_doc.py <source_file> --summary [--json]`
2. Extract structured `chint-office-extract/v1` JSON (`P{n}:L{m}` for PDF, `document:P{n}` / `header1:P{n}` for Word, `Sheet!Cell` for Excel; flags PDF pages `<50` chars in `low_text_pages`):
   - `python3 scripts/extract_doc.py <source_file> [--pages <range>] --json`
3. *Done when*: Extraction payload emitted with `total_units`, `scanned_units`, and all `low_text_pages` explicitly surfaced; source file untouched.

## Branch B — Non-Destructive PDF Annotation (`annotate_pdf.py`)

1. Pipe `chint-office-annotate/v1` JSON (`page`, `search`/`searches`, `comment`, optional `match_mode`: `all` | `merged` | `first`, optional `author`) directly via stdin (`--annotations -`) to avoid stray sidecar files on disk.
2. Run: `python3 scripts/annotate_pdf.py <input.pdf> --annotations - [--output <out.pdf>] [--author <name>]`
   - Writes strictly to a single new PDF copy (`<stem>_annotated.pdf` by default), keeping `<input.pdf>` untouched and preserving all pre-existing annotations.
   - Applies unified yellow `Highlight` (`all` marks every occurrence; `merged` binds multiple hits into one linked sidebar annotation) and falls back to staggered yellow margin `Sticky Note` (`[label] comment`).
3. *Done when*: New annotated PDF written, source PDF untouched, zero stray sidecar files created, `matched_items + sticky_fallback_count == total`, and all `fallback_items` surfaced.