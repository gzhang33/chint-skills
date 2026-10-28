# Skill Maintenance and Synchronization

Read this guide only for skill-library maintenance or synchronization. For deck runtime, output paths, and quality checks, use `quality_and_environment.md`.

## Synchronization

Run `scripts/verify_skill_sync.py` to check the managed skill-library copy and deployment links. Preserve the existing links; edit the library directory rather than replacing a link with a separate copy. The checker excludes `__pycache__`, `.pyc`, `.pyo`, and `.DS_Store` from directory comparisons. The parent `skills/.gitignore` also excludes these generated artifacts from Git. The checker supports explicit endpoints with `--endpoint` and `CHINT_PPTX_SYNC_ENDPOINTS`; use `--strict-missing` when every configured endpoint is required.

## Temporary work

Keep intermediate analysis and render files in a scratch or dedicated validation directory. Save generated decks, previews, and reports outside the skill folder. Deliver only requested PPTX files and audit outputs. Use `scripts/cleanup_scratch.py` to preview or remove expired CHINT scratch files; it skips symbolic links and protected system locations.

## Maintenance checks

From the skill root, run:

```bash
python3 scripts/check_environment.py
python3 scripts/check_brand_tokens.py
python3 scripts/lint_docs.py
python3 scripts/verify_skill_sync.py
```

For a fresh device, install the packages in `requirements.txt`. If the font check fails, ask the user before opening the native installer with `python3 scripts/check_environment.py --open-font-installer`; the user completes the current-user installation. Restart Office and rerun `scripts/check_environment.py` before using the presentation engine.
