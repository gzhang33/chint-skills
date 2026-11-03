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

For a fresh device, install the packages in `requirements.txt`, then follow the Font installation section of [quality_and_environment.md](quality_and_environment.md) before using the presentation engine.

Two maintenance scripts are not in the list above because they run on demand rather than every check: `scripts/generate_contract_sample.py` regenerates a watermarked sample deck covering every archetype and is the regression check to run after changing the engine or the compliance gate; `scripts/measure_form.py` is a thin CLI over the analyzer that prints measured layout geometry for a source deck.
