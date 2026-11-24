---
name: chint-office-suite
description: "Extract structured text and visual-page maps from .pdf/.docx/.xlsx, write non-destructive PDF review annotations, or route generic office authoring — standalone or when another skill calls it."
---

# CHINT Office Suite

Resolve `<OFFICE_SKILL_DIR>` from the directory containing this `SKILL.md` and run every script via `python3 "<OFFICE_SKILL_DIR>/scripts/..."` (never assume workspace CWD matches the skill directory). Prerequisites: `pymupdf` (`fitz`) for `.pdf` and `openpyxl` for `.xlsx`.

## Step 1 — Format Gate & Routing

1. Inspect file extension and target deliverable:
   - **`.doc` / `.xls` legacy binaries**: Request conversion to `.docx` / `.xlsx` before parsing.
   - **Authoring / layout editing** (`.xlsx` formulas/pivot tables, `.docx` styling/redlines, `.pdf` splitting/merging/form filling): Route to `pdf`, `docx`, or `xlsx` skill if installed; otherwise report the missing capability.
   - **Extraction vs PDF annotation**: Choose `Branch A` for reading/extracting text, or `Branch B` for writing PDF review annotations.
2. *Done when*: Format validated and active branch selected.

## Branch A — Structured Extraction (`extract_doc.py`)

1. For PDFs exceeding 20 pages, inspect page map and recommended batch ranges first:
   - `python3 "<OFFICE_SKILL_DIR>/scripts/extract_doc.py" "<source_file>" --summary [--json]`
2. Extract structured `chint-office-extract/v1` JSON (`P{n}:L{m}` for PDF, `document:P{n}` / `header1:P{n}` for Word, `Sheet!Cell` for Excel; flags `<50`-char PDF pages in `low_text_pages` and uncached Excel formulas in `uncached_formula_cells`):
   - `python3 "<OFFICE_SKILL_DIR>/scripts/extract_doc.py" "<source_file>" [--pages <range>] --json`
   - Route any `low_text_pages` to `smart-ocr` or `tencentcloud-ocr` if installed, else fall back to visual page inspection.
3. *Done when*: All recommended batches `1..M` (if PDF > 20 pages) are extracted, `total_units`/`scanned_units` accounted for, and every `low_text_pages` / `uncached_formula_cells` entry is surfaced.

## Branch B — Non-Destructive PDF Annotation (`annotate_pdf.py`)

1. Pipe `chint-office-annotate/v1` JSON (`page`, `search`/`searches`, `comment`, optional `match_mode`: `all` | `merged` | `first`, optional `whole_word`/`case_sensitive`, optional `author`) directly via stdin (`--annotations -`) so no sidecar file lands in the user's directory.
2. Run: `python3 "<OFFICE_SKILL_DIR>/scripts/annotate_pdf.py" "<input.pdf>" --annotations - [--output "<out.pdf>"] [--author "<name>"]`
   - Saves strictly to a single new PDF copy (`<stem>_annotated.pdf` by default), preserving pre-existing annotations.
   - Applies unified yellow `Highlight` with token-boundary and wrapped-phrase protection (`all` highlights every occurrence; `merged` binds hits into one linked sidebar item) and falls back to margin `Sticky Note` (`[label] comment`).
3. *Done when*: New annotated PDF copy written, source PDF untouched, `matched_items + sticky_fallback_count == total`, and all `fallback_items` surfaced.