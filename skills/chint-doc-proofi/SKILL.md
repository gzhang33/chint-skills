---
name: chint-doc-proofi
description: "Audit and proofread CHINT low-voltage catalogues and general office documents (PDF, Word .docx/.doc, Excel .xlsx/.xls, PowerPoint .pptx, Markdown, plain text) for 错别字 (typos), 勘误 (errata), 校对/审校 (proofreading), numbering defects, 术语一致性 (terminology drift) and 错漏/硬伤 (hard errors): produce a located errata table, then write non-destructive PDF 批注 only after explicit user confirmation. Use whenever the user asks to 校对/审校/勘误/查错/过一遍 a document, review a manual or catalogue, or mentions 错别字、错漏、硬伤、术语一致性、批注."
---

# CHINT Document Proofreading & Threshold Audit

Resolve `<SKILL_DIR>` from the directory containing this `SKILL.md` and run scripts via `python3 "<SKILL_DIR>/scripts/..."` on macOS/Linux (or `python` / `py -3` on Windows).

- **Standalone Dependencies**: Run `python3 "<SKILL_DIR>/scripts/audit_catalog.py" --check-env` before the first run. `.pdf` needs `pymupdf`, `.xlsx`/`.xlsm` need `openpyxl`; `.docx`, `.pptx`, `.md`, `.txt`, `.doc`, `.xls` are pure stdlib. Install via China mainland mirrors when missing: `python3 -m pip install --user --timeout 30 -r "<SKILL_DIR>/requirements.txt" -i https://pypi.tuna.tsinghua.edu.cn/simple` (fallback `-i https://mirrors.aliyun.com/pypi/simple/`).
- **Standalone & Sibling Synergy**: Runs 100% standalone. When sibling `chint-office-suite` is installed, `.pdf`/`.docx`/`.xlsx` extraction and PDF annotation delegate to it; when `chint-translation` is installed, the live IEC/GB terminology SSOT is loaded instead of the parity-tested built-in fallback. `.pptx`, `.md`, `.doc` and `.xls` always use the built-in extractors — the sibling extractor rejects `.doc`/`.xls` outright and knows nothing of pptx/md.
- **Data-Driven Rules**: Vocabulary (typo list, same-page conflict groups, cross-page synonym groups, symbol/case notation) lives in `references/catalog_rules.json`, not in Python. The script holds only generic detectors: SI-unit casing, numeric-range sanity, `Ics`/`Icu`, `In`/`Inm`, `Ue`/`Ui` relations, bracket pairing, figure/table numbering, page-reference bounds, duplicated words. Rule-to-standard traceability (GF 1001, GB/T 15834/15835, GB/T 2900.18, IEC 60050-441, IEC 60947-2:2024 / GB/T 14048.2—2020, IEC 62423) is documented in [references/sources.md](references/sources.md). Legacy English forms that peers also use (`drawer`, `closing electromagnet`, `shunt opening release`) are downgraded to `EN_TERM_CONSISTENCY` (L2) via `severity_overrides` — they are consistency issues, not hard errors. Add product-line terms to the JSON; never patch single-catalogue cases into the script.
- **One Rule Set, Several Document Types**: the same detectors run on a catalogue, a meeting deck and a quote sheet. `doc_type` (`catalogue` | `office-generic` | `markdown` | `legacy-binary` | `text`) is decided by content — ≥2 distinct electrical signals in the first 400 units make a `catalogue` — and tells you how to read the result: a typo or duplicated word is a defect in every document type, while a rating-table or IEC hit on `office-generic` deserves a second look before it goes in the errata table.

## Step 1 — Lock Profile & Stage Input

1. Lock **Profile** (`L1` default | `L2` | `L3`), optional **`--with-iec`** + **`--dept`** (`acb` | `mccb` | `all`), and **Language** (`auto` default | `zh` | `en`):
   - **`L1` (Default — Strict Errors Only)**: Technical hard errors (including inverted/equal numeric ranges, `Ics > Icu`, duplicated words, unbalanced brackets), logic contradictions, Chinese typos/grammar, cross-reference/numbering defects (figure/table duplicates, missing sequence numbers, out-of-range page references), same-page conflicting terms, and severe EN mistranslations/competitor codes/`{{...}}`. Legacy-but-peer-valid English forms (`drawer`, `closing electromagnet`) are NOT reported here — see `L2`.
   - **`L2` (Publish Consistency)**: `L1` plus cross-page term drift, peer-valid legacy English terminology (`EN_TERM_CONSISTENCY`), and symbol/case/notation inconsistencies (including SI-unit casing such as `50KA` / `60HZ`).
   - **`L3` (Substantive GB/IEC Compliance)**: identical behaviour to `L2 --with-iec` — same code path (`run_l2` plus the IEC concept/statutory checks), not a separate rule layer. Use either; `--with-iec` on `L1` gives strict-errors-only plus compliance.
   - **`--with-iec`**: Additive overlay applying substantive GB/IEC compliance onto `L1` or `L2`.
   - **Scope Guardrail**: Restrict findings strictly to the active profile; omit spacing, `℃`, punctuation, hyphenation, and UK/US spelling checks across all profiles.
2. **Input Routing**: Pass the document directly to `audit_catalog.py` (zero sidecar files in the workspace):

   | Input | Extraction | Locator shape |
   | :--- | :--- | :--- |
   | `.pdf` | sibling or built-in PyMuPDF | `P<page>:L<line>`; table findings `P<page>:Table` |
   | `.docx` | sibling or built-in OOXML | `<part>:P<para>` — e.g. `document:P12`, `header1:P3` |
   | `.xlsx` / `.xlsm` | sibling or openpyxl | `<sheet>!<col><row>` — e.g. `测算需求!B17` |
   | `.pptx` | built-in stdlib `zipfile` + ElementTree | `S<slide>:T<shape>:P<para>` — e.g. `S7:T2:P3` |
   | `.md` | built-in, fenced + inline code skipped | `M<line>` (source line number) |
   | `.txt` | built-in | `Line <n>` |
   | `.doc` | built-in OLE2 (CLX piece table) | `D<para>` |
   | `.xls` | built-in OLE2 / BIFF8 | `X<sheet>:R<row>` — e.g. `X内销工厂数据新增模板:R3` |
   | `chint-office-extract/v1` JSON | read as-is | as supplied in the file |

   - For PDFs > 20 pages, check `--summary` or use `--pages <range>` batches. `--pages` filters PDF pages only; every other format is scanned whole regardless of the flag.
   - pptx shape indexes count text-bearing shapes (`p:sp`, `p:graphicFrame`) in document order and walk group shapes recursively, so a locator points at a real text box, not a z-order guess. A slide with no extractable text lands in `low_text_pages` — an image-only deck is a coverage gap, not a clean pass.
   - `.doc`/`.xls` extraction is best-effort. When the OLE2 structure is unreadable the run exits `2` with `无法解析 .doc（…），建议用 Office 另存为 .docx 后重试` and never returns an empty text with "0 errors" — a silent empty pass would read as a clean bill of health for a file that was never audited. The same rule covers a parse that succeeds but yields no cell text (`.xls` raises `文件结构可解析但未提取到任何单元格文本…`) and an image-only `.pptx` (reported as `low_text_pages`, and the blind-pass guard exits `2` when every container is empty).
   - **No write-back for non-PDF formats**: `.pptx`, `.xlsx`/`.xlsm`, `.doc`, `.xls`, `.md` and `.txt` produce an errata table only. `--write-pdf` and `--emit-annotate` are PDF-only: findings whose locator is not `P<n>:…` are dropped with a stderr warning, and `--write-pdf` against a non-PDF input fails with exit `2`. Writing Office annotations would require an Office write library, which the zero-dependency rule excludes — hand the errata table to the document owner instead.
3. *Done when*: Active profile is locked and the input path (plus `--pages` batch if a large PDF) is ready.

## Step 2 — Deterministic Audit Pass

1. Run the audit engine directly on the source file (or extracted `/tmp` JSON):
   - `python3 "<SKILL_DIR>/scripts/audit_catalog.py" "<input_file>" --profile <L1|L2|L3> [--with-iec --dept <acb|mccb|all>] [--pages <range>] --mode <auto|zh|en> --report-md --exit-zero`
2. PDF rating tables are read with `Page.find_tables()` on pages whose text contains `Icu`/`Ics`/`Inm`/`Icw`/`Ue`/`Ui`/`额定`/`壳架`/`分断`. The gate matters: a 120-page catalogue has ~6 such pages, so this costs ~3 s instead of ~50 s. Table findings use location `P<n>:Table` and cannot be annotated in the PDF (no text to anchor to). Table extraction needs `pymupdf` and applies to `.pdf` only.
3. A single run always scans the whole document — cross-page detectors (term drift, caption duplicates, numbering gaps, same-page conflicts, bracket balance) need the full text. Use `--chunk-size 50 --chunk-index <k>` only to page through the *output* of a large file; the engine still scans everything and prints findings inside chunk `k`. Use `--chunks-info` to see the chunk map and `--summary` for a large PDF's page batches.
4. **Do not chunk as a substitute for a full run** — it costs a full re-extraction per chunk and used to drop cross-page findings.
5. When `--with-iec` or `L3` is active and sibling `chint-translation` is present, optionally run `<SKILL_DIR>/../chint-translation/scripts/glossary_lookup.py` for clause-level term verification.
6. Read the summary line before the findings: `[<profile>] Scanned <scanned>/<total> containers, <N> text units | doc_type=… | office=… | ssot=… | low_text_pages=… | findings=…`. `total` counts containers — PDF pages, pptx slides, `.docx`/`.doc` paragraphs, `.md`/`.txt` lines, `.xls` rows, and for `.xlsx` the sheet count (sibling extractor) or the extracted-cell count (builtin) — so it is not the audited text count. `<N>` is the text count. A 23-slide deck holding 1122 text units is normal; reading the two numbers as one is how under-coverage goes unnoticed. The same fields are available from `--summary` (text and JSON), the `--json` report, and the `--chunks-info --json` manifest.
7. *Done when*: One full pass is complete, every `low_text_pages` entry is listed, and `doc_type` has been read against the profile's noise expectation.

## Step 3 — Semantic Verification & Chat Deliverable

1. Read [references/semantic_checklist.md](references/semantic_checklist.md) and sweep ONLY the semantic checks matching the locked profile (`L1` / `L2` / `L3` / `--with-iec`). Sections 1–4 are catalogue-oriented; for `office-generic`, `markdown` and `legacy-binary` documents use section 5 as well.
   - Inspect every page/slide in `low_text_pages` visually and record its status in the Coverage Ledger.
   - Include ONLY findings active under the locked profile.
2. Output directly in chat (terse tables):
   - **Errata Table** (`页码 | 级别 | 维度 | 原文 | 替换为 | 依据`) — for non-PDF inputs the first column carries the native locator (`S7:T2:P3`, `X内销工厂数据新增模板:R3`, `M42`).
   - **Coverage Ledger** (`总单元 | 已扫描 | 视觉页 | 机械命中 | 语义命中`)
   - **Pending Verification List** (ambiguous specs, missing numbers, prose-vs-table conflicts — zero fabrication)
3. *Done when*: Every finding, chunk, and visual-only page is accounted for. **For PDF documents, end the turn cleanly here** without writing any PDF or calling `--write-pdf` / `--emit-annotate`, awaiting user confirmation in a subsequent message — even if the initial prompt already asked to annotate the PDF. **For every other format, end here too**: the errata table is the deliverable, because there is nothing to write back.

> **Confirmed PDF Annotation Handoff**: Only after user confirmation arrives in a subsequent message, read [references/pdf_annotation_handoff.md](references/pdf_annotation_handoff.md) and execute it. The confirmation is a separate message on purpose: a request to "annotate this PDF" states intent, not approval of findings the user has not seen yet, and annotations travel with the document after it leaves this chat.
