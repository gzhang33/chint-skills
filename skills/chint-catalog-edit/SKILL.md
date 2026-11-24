---
name: chint-catalog-edit
description: "Audit CHINT low-voltage product catalogues (ZH/EN PDF, Word, Excel, text) for hard errors, typos, numbering defects, optional IEC/GB compliance, and non-destructive PDF review annotations."
---

# CHINT Catalogue Proofreading & Threshold Audit

Resolve `<SKILL_DIR>` from the directory containing this `SKILL.md` and run scripts via `python3 "<SKILL_DIR>/scripts/..."` on macOS/Linux (or `python` / `py -3` on Windows).

- **Standalone Dependencies (`.pdf` / `.xlsx`)**: Run `python3 "<SKILL_DIR>/scripts/audit_catalog.py" --check-env` when processing `.pdf` or `.xlsx` (`.docx` and text use Python stdlib). If `pymupdf` or `openpyxl` is missing, install via China mainland mirrors: `python3 -m pip install --user --timeout 30 -r "<SKILL_DIR>/requirements.txt" -i https://pypi.tuna.tsinghua.edu.cn/simple` (fallback: `-i https://mirrors.aliyun.com/pypi/simple/`).
- **Standalone & Sibling Synergy**: Runs 100% standalone. When sibling `chint-office-suite` or `chint-translation` is installed, `audit_catalog.py` automatically delegates Office I/O and loads the live IEC/GB terminology SSOT; otherwise it uses its built-in extractors, PDF annotator, and parity-tested fallback SSOT.

## Step 1 — Lock Profile & Stage Input

1. Lock **Profile** (`L1` default | `L2` | `L3`), optional **`--with-iec`** + **`--dept`** (`acb` | `mccb` | `all`), and **Language** (`auto` default | `zh` | `en`):
   - **`L1` (Default — Strict Errors Only)**: Technical hard errors, logic contradictions, Chinese typos/grammar, cross-reference/numbering defects, same-page conflicting terms, and severe EN mistranslations/competitor codes/`{{...}}`.
   - **`L2` (Publish Consistency)**: `L1` plus cross-page term drift and symbol/case/notation inconsistencies.
   - **`L3` (Substantive GB/IEC Compliance)**: `L2` plus substantive standard concept errors and statutory Chinese deviations.
   - **`--with-iec`**: Additive overlay applying substantive GB/IEC compliance onto `L1` or `L2`.
   - **Scope Guardrail**: Restrict findings strictly to the active profile; omit spacing, `℃`, punctuation, hyphenation, and UK/US spelling checks across all profiles.
2. **Input Routing**: Pass `.pdf`, `.docx`, `.xlsx`, `.txt`/`.md`, or `chint-office-extract/v1` JSON directly to `audit_catalog.py` (for PDFs > 20 pages, check `--summary` or use `--pages <range>` batches; zero extra sidecar files in the workspace).
3. *Done when*: Active profile is locked and input path (plus `--pages` batch if large PDF) is ready.

## Step 2 — Deterministic Audit Pass

1. Run the catalogue audit engine directly on the source file (or extracted `/tmp` JSON):
   - `python3 "<SKILL_DIR>/scripts/audit_catalog.py" "<input_file>" --profile <L1|L2|L3> [--with-iec --dept <acb|mccb|all>] [--pages <range>] --mode <auto|zh|en> --report-md --exit-zero`
2. For inputs exceeding 50 non-empty text units, inspect `--chunk-size 50 --chunks-info` and scan chunks `1..N` sequentially (`--chunk-size 50 --chunk-index <k> --exit-zero`, omitting `--report-md`) so every page is inspected.
3. When `--with-iec` or `L3` is active and sibling `chint-translation` is present, optionally run `<SKILL_DIR>/../chint-translation/scripts/glossary_lookup.py` for clause-level term verification.
4. *Done when*: Every chunk `1..N` is scanned and all `low_text_pages` are listed.

## Step 3 — Semantic Verification & Chat Deliverable

1. Read [references/semantic_checklist.md](references/semantic_checklist.md) and sweep ONLY the semantic checks matching the locked profile (`L1` / `L2` / `L3` / `--with-iec`):
   - Inspect every page in `low_text_pages` visually and record its status in the Coverage Ledger.
   - Include ONLY findings active under the locked profile.
2. Output directly in chat (terse tables):
   - **Errata Table** (`页码 | 级别 | 维度 | 原文 | 替换为 | 依据`)
   - **Coverage Ledger** (`总单元 | 已扫描 | 视觉页 | 机械命中 | 语义命中`)
   - **Pending Verification List** (ambiguous specs, missing numbers, prose-vs-table conflicts — zero fabrication)
3. *Done when*: Every finding, chunk, and visual-only page is accounted for — **and for PDF catalogues, end the turn cleanly here without writing any PDF or calling `--write-pdf` / `--emit-annotate`, awaiting user confirmation in a subsequent message (even if the initial prompt asked to annotate the PDF).**

> **Confirmed PDF Annotation Handoff**: Only after user confirmation arrives in a subsequent message, read [references/pdf_annotation_handoff.md](references/pdf_annotation_handoff.md) and execute it.
