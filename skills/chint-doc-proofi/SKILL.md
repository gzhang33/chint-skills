---
name: chint-doc-proofi
description: "Audit and proofread CHINT low-voltage catalogues and general office documents (PDF, Word .docx/.doc, Excel .xlsx/.xls, PowerPoint .pptx, Markdown, plain text) for 错别字 (typos), 勘误 (errata), 校对/审校 (proofreading), numbering defects, 术语一致性 (terminology drift) and 错漏/硬伤 (hard errors): produce a located errata table, then write non-destructive PDF 批注 only after explicit user confirmation. Use whenever the user asks to 校对/审校/勘误/查错/过一遍 a document, proofread or review a manual, catalogue, slide deck, spreadsheet, or report, or mentions typos, numbering errors, 错别字、错漏、硬伤、术语一致性、批注."
---

# CHINT Document Proofreading & Threshold Audit

Resolve `<SKILL_DIR>` from the directory containing this `SKILL.md` and run scripts via `python3 "<SKILL_DIR>/scripts/..."` on macOS/Linux (or `python` / `py -3` on Windows).

- **Dependencies & Runtime**: Run `python3 "<SKILL_DIR>/scripts/audit_catalog.py" --check-env` before the first run. `.pdf` needs `pymupdf`, `.xlsx`/`.xlsm` need `openpyxl`; all other formats are pure stdlib. If missing, install via China mainland mirrors: `python3 -m pip install --user --timeout 30 -r "<SKILL_DIR>/requirements.txt" -i https://pypi.tuna.tsinghua.edu.cn/simple` (fallback `-i https://mirrors.aliyun.com/pypi/simple/`).
- **Standalone & Sibling Synergy**: Works 100% standalone. When sibling `chint-office-suite` is installed, `.pdf`/`.docx`/`.xlsx` extraction and PDF annotation delegate to it; when `chint-translation` is installed, its live IEC/GB terminology SSOT overrides the parity-tested built-in fallback. `.pptx`, `.md`, `.doc`, and `.xls` always run via built-in extractors.
- **Unified Engine, Domain Disclosure**: One deterministic detector set scans every document, classifying `doc_type` (`catalogue` | `office-generic` | `markdown` | `legacy-binary` | `text`) by content so domain rules load on demand instead of crowding general checks.

## Step 1 — Lock Profile, Input & Domain Guide

1. Lock **Profile** (`L1` default | `L2` | `L3`), optional **`--with-iec`** + **`--dept`** (`acb` | `mccb` | `all`), and **Language** (`auto` default | `zh` | `en`):
   - **`L1` (Default — Strict Errors Only)**: Objective hard errors (inverted/equal numeric ranges, internal parameter contradictions, duplicated words, unbalanced brackets, numbering duplicates/gaps, out-of-range page refs), Chinese typos/grammar, same-page conflicting terms, severe mistranslations, unresolved `{{...}}`, plus domain hard errors defined in the active domain guide.
   - **`L2` (Publish Consistency)**: `L1` plus cross-page term drift, peer-valid legacy consistency items, and symbol/case/notation normalization.
   - **`L3` (Substantive Compliance)**: Identical code path to `L2 --with-iec` (adds domain statutory/standard compliance checks); pass `--with-iec` on `L1` for strict errors plus compliance.
   - **Scope Guardrail**: Restrict findings strictly to the active profile; omit spacing, `℃`, punctuation-style, hyphenation, and UK/US spelling checks across all profiles.
2. **Input Routing & Universal Boundaries**:

   | Input | Extraction | Locator shape |
   | :--- | :--- | :--- |
   | `.pdf` | sibling or built-in PyMuPDF | `P<page>:L<line>`; tables `P<page>:Table` |
   | `.docx` | sibling or built-in OOXML | `<part>:P<para>` (e.g. `document:P12`, `header1:P3`) |
   | `.xlsx` / `.xlsm` | sibling or openpyxl | `<sheet>!<col><row>` (e.g. `测算需求!B17`) |
   | `.pptx` | built-in stdlib | `S<slide>:T<shape>:P<para>` (e.g. `S7:T2:P3`) |
   | `.md` | built-in (code spans/blocks skipped) | `M<line>` (source line number) |
   | `.txt` | built-in | `Line <n>` |
   | `.doc` / `.xls` | built-in OLE2 (best-effort) | `D<para>` / `X<sheet>:R<row>` |
   | `chint-office-extract/v1` JSON | read as-is | as supplied |

   - **Never report "0 errors" when unaudited**: Exit code `2` signals an unreadable binary, Git LFS pointer, or zero-text blind pass — report the error and suggested fix honestly because the file was never checked.
   - **Non-PDF outputs end at the errata table**: Writing annotations inside Office files requires external write libraries excluded by zero-dependency design (`--write-pdf` and `--emit-annotate` work only on `.pdf`).
3. **Domain Guide Routing** — match on **subject domain**, not container format alone (`markdown`, `legacy-binary`, `text` reflect file format rather than topic):
   - Electrical catalogue, datasheet, or technical manual (even in `.md`, `.doc`, or pasted text), or statutory compliance (`--with-iec` / `L3`) → read [references/domains/electrical_catalogue.md](references/domains/electrical_catalogue.md).
   - Non-catalogue general office doc, presentation, spreadsheet, Markdown, or legacy binary (`office-generic` | `markdown` | `legacy-binary` | `text`) → read [references/domains/office_generic.md](references/domains/office_generic.md) (also load its §2 for `.pptx`/`.md`/`.doc`/`.xls` locator caveats even on technical files).
   - Standard citations or extending [references/catalog_rules.json](references/catalog_rules.json) → read [references/sources.md](references/sources.md).
4. *Done when*: Active profile, input path (`--pages <range>` only for batching PDFs > 20 pages after inspecting `--summary`), and domain guide are selected.

## Step 2 — Deterministic Audit Pass

1. Run the audit script directly on the source file (zero workspace sidecar files):
   - `python3 "<SKILL_DIR>/scripts/audit_catalog.py" "<input_file>" --profile <L1|L2|L3> [--with-iec --dept <acb|mccb|all>] [--pages <range>] --mode <auto|zh|en> --report-md --exit-zero`
   - For pasted inline snippets with no file path, stage a clean temporary file in `/tmp` — `/tmp/<name>.md` for Markdown, or `/tmp/<name>.json` as `chint-office-extract/v1` with `P<page>:L<line>` locators when page numbers are stated (avoid bare stdin `-` on paged/Markdown inputs, which falls back to `Line <n>`) — run `audit_catalog.py`, and delete the `/tmp` file immediately after.
2. Scan the full document in one pass so cross-page detectors see complete context. Use `--summary` for large PDF page batches and `--chunks-info` / `--chunk-size 50 --chunk-index <k>` only to paginate large outputs, never as a scan substitute.
3. Read the summary line printed above `--report-md` (`[<profile>] Scanned <scanned>/<total> containers, <N> text units | doc_type=… | office=… | ssot=… | low_text_pages=… | findings=…`): `total` counts containers while `<N>` is audited text units; confirm or switch guides between `electrical_catalogue.md` and `office_generic.md` only when `doc_type` toggles `catalogue` vs `office-generic`, and note every `low_text_pages` item for visual inspection.
4. *Done when*: Full pass completes (or exits `2` cleanly), `doc_type` is confirmed, and every `low_text_pages` entry is logged.

## Step 3 — Semantic Verification & Chat Deliverable

1. If Step 2 exits `2`, stop cleanly and report the unaudited error and recovery guidance — do not emit an empty Errata Table.
2. Otherwise apply only the semantic checks matching the active profile from the loaded domain guide, and inspect every `low_text_pages` page/slide visually.
3. Output directly in chat (terse Markdown tables):
   - **Errata Table** (`页码 | 级别 | 维度 | 原文 | 替换为 | 依据` — first column uses native locator for non-PDF)
   - **Coverage Ledger** (`总容器(页/片/表) | 已扫描 | 文本单元 | 视觉页 | 机械命中 | 语义命中`)
   - **Pending Verification List** (ambiguous numbers, prose-vs-table conflicts, unverified specs — never guess or fabricate)
4. *Done when*: Every finding, visual page, and pending item is accounted for. **End the turn here**: for PDFs, await explicit user confirmation in a subsequent message before writing annotations (requests to "annotate" state intent, not approval of findings before review); for all other formats, this errata table completes delivery.

## Step 4 — Confirmed PDF Annotation Handoff

Only after explicit user confirmation arrives in a subsequent message on a `.pdf`, read [references/pdf_annotation_handoff.md](references/pdf_annotation_handoff.md) and execute it.
