# General Office, Markdown & Legacy Binary Guide

Load this reference when auditing non-catalogue documents (`doc_type` = `office-generic` | `markdown` | `legacy-binary` | `text`) — meeting notes, internal notices, product intro decks, quote sheets, Markdown files, or legacy `.doc`/`.xls` files. If a `.md`/`.doc`/`.xls`/`.txt` file is actually an electrical catalogue or manual, load [electrical_catalogue.md](electrical_catalogue.md) for domain rules and keep §2 below for container locator caveats.

## 1. Unified Engine & Domain-Hit Triage

- **Why the Same Engine Runs**: Universal defects (Chinese typos like `海拨`/`润滑酯`, duplicated words, inverted/equal numeric ranges, unbalanced brackets, duplicate or skipped numbering, out-of-range cross-references) break accuracy in any office document. Running one rule set avoids splitting maintenance across separate detectors.
- **Triage Incidental Electrical Hits**: Because product-line and electrical rules also run here, inspect any rating-table or IEC/electrical terminology hit against the document's purpose before placing it in the final errata table:
  - Keep true generic typos, logic/numbering defects, and clear unit mistakes (`63~32A`, `断路器断路器`, `Ui(kV) 1000` when stating electrical ratings).
  - Verify whether incidental electrical vocabulary on a meeting deck, business quote sheet, or administrative notice is genuine product-domain copy needing correction or out-of-context noise, and triage transparently rather than deleting hits silently.

## 2. Format Extraction & Delivery Boundaries

- **PowerPoint (`.pptx`)**: Extracted via pure-stdlib `zipfile` + ElementTree. Locators `S<slide>:T<shape>:P<para>` index text-bearing shapes (`p:sp`, `p:graphicFrame`) in document order and walk group shapes (`grpSp`) recursively so locators map to real text boxes; speaker notes are excluded by default. Slides with no extractable text enter `low_text_pages` (treat image-only slides as visual inspection gaps, not clean passes).
- **Markdown (`.md`)**: Fenced code blocks (` ``` ` / `~~~`) and inline backtick spans are stripped before scanning so shell commands, URLs, and code identifiers do not trigger prose errors. Locators use source line numbers (`M<line>`).
- **Legacy Binary (`.doc` / `.xls`)**: Extracted via pure-stdlib OLE2 best-effort parsing (`D<para>` for Word paragraphs; `X<sheet>:R<row>` for Excel rows). Because `.doc` streams carry no page breaks and merged `.xls` cells collapse onto one row, always quote the surrounding sentence or full row text in the errata table. Complex encryption or broken OLE2 streams exit `2` with `.docx`/`.xlsx` re-save guidance (`SKILL.md` enforces honest unaudited reporting).
- **Non-PDF Delivery**: Deliver the errata table directly to the document owner (`--write-pdf` / `--emit-annotate` in `SKILL.md` apply to `.pdf` only).

## 3. Generic Office Semantic Verification Checklist

Sweep only items matching the active profile:

- **Count & Header Integrity**: Stated item counts matching actual lists ("三项要求" followed by 4 bullets); table captions matching header columns; summary-slide totals matching detail slides.
- **Numbering & Sequencing**: Skipped agenda or step numbers, duplicate section headings, prose ordering ("第一步/第二步") contradicting actual body order, figure/table callouts never defined.
- **Prose vs Table / Prose vs Slide Contradictions**: Dates, quantities, or KPIs in prose disagreeing with an accompanying table cell or chart claim.
- **Stated vs Actual Lists**: Declared vendor/owner counts disagreeing with listed rows, blank owners in assigned columns, or agenda topics missing corresponding slides/sections.
- **Internal Identifier Consistency (`L2`)**: Product codes, part numbers, department names, or project tags spelled inconsistently across slides, sheets, or sections.
- **Visual Slides (`low_text_pages`)**: Inspect image-only slides or embedded screenshots visually for legible defects and log them in the Coverage Ledger.
- **Pending Verification List**: Isolate contradictory metrics, missing owners/dates, or unclear phrasing without guessing values.

### Layout Checks Excluded Here

Skip catalogue-specific layout assumptions unless clearly relevant:
- Running per-section frame/box headers (flag a slide title only when it contradicts its own slide content).
- Exploded-view callout legends (verify illustrative slide diagrams visually rather than cross-checking part tables).
- Incidental electrical rating vocabulary on non-technical quote sheets or administrative memos.
