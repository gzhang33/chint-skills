# Confirmed PDF Annotation Handoff (Step 4)

> **Gate**: Read and execute this procedure **only after** the user explicitly confirms Step 3's chat errata checklist in a subsequent message.

## 1. Zero-Sidecar Staging Policy

- Keep the user's workspace free of extra `.json`, `.md`, or `.xlsx` sidecar files.
- Any temporary extraction cache goes only to `/tmp` (or `%TEMP%` on Windows) and is deleted immediately on completion.

## 2. Prepare Confirmed Semantic Additions (`chint-office-annotate/v1`)

1. Format any user-confirmed **semantic findings** from Step 3 in memory using `chint-office-annotate/v1`:
   - `{"schema": "chint-office-annotate/v1", "annotations": [{"page": <1-based int>, "search": "<exact PDF phrase>", "comment": "替换为：<修正文本>", "match_mode": "all", "author": "CHINT Catalog Edit"}]}`
2. **Copy-Paste Comment Rule**: Every `comment` inside the PDF states solely the actionable fix (`替换为：<修正文本>` or `核实：<待核查项>`). Keep clause citations and long explanations in chat.

## 3. Write Non-Destructive Annotated PDF Copy

Run `audit_catalog.py` with `--write-pdf` (automatically delegates to sibling `chint-office-suite` when installed, or uses its built-in non-destructive PyMuPDF yellow-highlight + sticky-note writer when standalone):

- Command:
  `python3 "<SKILL_DIR>/scripts/audit_catalog.py" "<input.pdf>" --profile <L1|L2|L3> [--with-iec --dept <acb|mccb|all>] --mode <auto|zh|en> --annotate-severity <high|all> --write-pdf "<input.pdf>" [--output "<out.pdf>"] [--extra-annotations -]`
- Default `--annotate-severity high` keeps PDF annotations focused strictly on `HIGH` confirmed defects; pass `--annotate-severity all` when the user asks to annotate `MEDIUM` items too.
- Saves strictly to `<stem>_annotated.pdf` (or `--output`), preserving pre-existing annotations and leaving the source PDF untouched.
- *Done when*: Annotated PDF copy is written, source PDF is untouched, zero sidecar files remain in the workspace, and any `fallback_items` (unmatched split-run or visual-only notes) are reported back to the user in chat.
