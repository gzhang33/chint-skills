---
name: chint-office-suite
description: CHINT office document I/O and non-destructive PDF annotation hub (.pdf, .docx, .xlsx). Use when extracting structured text or visual-only page maps from catalogues/specs, writing highlight and sticky-note annotations onto new PDF copies, or routing generic Word/Excel/PDF authoring to installed office skills.
---

# CHINT Office Suite (`chint-office-suite` v1.0.0)

Generic, domain-neutral document parsing, office-skill routing, and non-destructive PDF annotation layer designed for seamless composition with any CHINT business skill.

## Step 1 — Format Gate & Office Skill Routing

1. Inspect input file extension and target deliverable:
   - **`.doc` / `.xls` legacy binaries**: Stop cleanly and ask the user or LibreOffice workflow to convert to `.docx` / `.xlsx` before parsing.
   - **Document creation or layout editing** (`.xlsx` formulas/pivot tables, `.docx` styling/redlines, `.pdf` splitting/merging/form filling): Route to the installed general office skills (`pdf`, `docx`, `xlsx`).
   - **Scanned / image-only PDF pages**: Route `low_text_pages` reported in Step 2 to `smart-ocr` or `tencentcloud-ocr` (or visual page inspection).
2. *Done when*: Format validated (zero legacy `.doc`/`.xls` blind reads) and authoring vs extraction route selected.

## Step 2 — Structured Extraction (`extract_doc.py`)

Run [extract_doc.py](scripts/extract_doc.py) to emit structured `chint-office-extract/v1` JSON for downstream business skills:
- Command: `python3 scripts/extract_doc.py <source_file> [--pages <range>] --json`
- Guarantees:
  - Emits exact coordinates (`P{n}:L{m}` for PDF, `document:P{n}` / `header1:P{n}` for Word, `Sheet!Cell` for Excel).
  - Detects and records every PDF page with `<50` non-whitespace characters in `low_text_pages` so visual/vector pages are never misreported as empty or defect-free.
- *Done when*: Extraction JSON returned with `total_units`, `scanned_units`, `low_text_pages`, and `units`.

## Step 3 — Non-Destructive PDF Annotation (`annotate_pdf.py`)

When an upstream business skill returns errata or review comments for PDF branding execution:
1. Build an input payload matching `chint-office-annotate/v1`: JSON list (or `{"annotations": [...]}`) where each item specifies `page` (1-based int), `search` (verbatim source text), `comment` (replacement/review note), and optional `author`.
2. Run: `python3 scripts/annotate_pdf.py <input.pdf> --annotations <errata.json_or_-> [--output <out.pdf>]`
3. Safety & recall guarantees:
   - Writes strictly to a new output file (`<stem>_annotated.pdf` by default) and rejects overwriting `<input.pdf>`.
   - Places a Highlight annotation on every matched phrase; falls back automatically to a top-margin Sticky Note when broken PDF text runs prevent highlight bounding boxes (`sticky_fallback_count` tracked).
- *Done when*: Annotated PDF copy generated, `input.pdf` untouched, and `highlight_count + sticky_fallback_count == total` confirmed.

## Step 4 — Completion Gate

- Original file byte-identical / untouched.
- Any `low_text_pages` from Step 2 explicitly handed off alongside extracted text (zero silent gaps).
- Output schemas (`chint-office-extract/v1` / `chint-office-annotate/v1`) honoured verbatim for downstream skill integration.
