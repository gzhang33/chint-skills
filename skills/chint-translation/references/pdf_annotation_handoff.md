# Confirmed PDF Annotation Handoff (`Branch B` Step 4)

> **Gate**: Read and execute this procedure **only after** the user explicitly confirms Step 3's chat errata checklist in a subsequent message.

## 1. Zero-Sidecar Staging Policy

- Keep the user's workspace free of extra `.json`, `.md`, or `.xlsx` sidecar files.
- If multiple passes (`extract_doc.py` → `lint_text.py` → `glossary_lookup.py`) need cached JSON, write extraction output only to an OS temporary path (`/tmp/...`) and delete it immediately after the turn, or stream via stdin/stdout pipes.

## 2. Build & Merge `chint-office-annotate/v1` Payload

1. Generate the deterministic mechanical annotation JSON to stdout (never to disk):
   - Default threshold (`--annotate-severity high`): keeps PDF focused strictly on substantive `HIGH` errors (`match_mode: "all"`, case-folded deduplication); `MEDIUM` spacing/orthography items remain in chat.
   - Pass `--annotate-severity all` **only** when the user explicitly asks to annotate spacing/orthography items too (emits page-level `match_mode: "merged"` highlights).
   - Command: `python3 "<TRANSLATION_SKILL_DIR>/scripts/lint_text.py" "<extract_or_tmp>" --dept <acb|mccb> --mode <en|zh> --emit-annotate - [--annotate-severity high|all] --author "CHINT Translation"`
2. Append any user-confirmed **semantic findings** from Step 3 directly in memory using schema `chint-office-annotate/v1`:
   - Required fields per item: `{"page": <1-based int>, "search": "<exact PDF phrase>", "comment": "替换为：<标准译文>", "match_mode": "all", "author": "CHINT Translation"}` (or `"searches": [...]` + `"match_mode": "merged"` for repeated same-page patterns).
3. **Copy-Paste Comment Rule**: Every `comment` inside the PDF must contain solely the actionable replacement text (`替换为：<标准译文>`). Keep IEC/GB clauses and rationales in chat.

## 3. Delegate Writing to `chint-office-suite` (`Branch B`)

1. Pipe the merged `chint-office-annotate/v1` JSON via stdin (`--annotations -`) into `chint-office-suite`'s `annotate_pdf.py` (`Branch B`), targeting a new copy (`<stem>_annotated.pdf` or user-specified output path, leaving source PDF untouched and pre-existing annotations intact).
2. *Done when*: New annotated PDF copy is written, source PDF is untouched, zero sidecar files remain in the workspace, and any `fallback_items` (unmatched split-run or visual-only notes) are reported back to the user in chat.