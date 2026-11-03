#!/usr/bin/env python3
"""Brand token loader for CHINT creation and shell-rendering engines.

Reads ``<skill root>/spec/brand_tokens.json`` (the same snapshot the Mode B engine
uses). The skill root is resolved relative to this file:

    <skill root>/scripts/_brand_tokens.py  ->  parents[1] is <skill root>

Snapshot missing / invalid JSON / theme table missing / required keys missing ->
print the expected absolute path (and missing key names) to stderr, then
``sys.exit(2)``. No silent fallback of any kind.

Exposes:
    THEME_KEYS -- the 9 required theme key names
    TOKENS     -- dict of raw string values from the snapshot theme table
"""

import json
import os
import pathlib
import sys

THEME_KEYS = ("font", "blue", "navy", "cyan", "ice", "white",
              "muted", "light_bg", "card_border")


def _spec_path() -> pathlib.Path:
    """Resolve the brand snapshot path. Environment override first, then skill-root-relative."""
    override = os.getenv("CHINT_PPTX_BRAND_TOKENS")
    if override:
        return pathlib.Path(override)
    # __file__ = <skill root>/scripts/_brand_tokens.py
    skill_root = pathlib.Path(__file__).resolve().parents[1]
    return skill_root / "spec" / "brand_tokens.json"


def _load() -> dict:
    spec_path = _spec_path()
    if not spec_path.exists():
        print(f"[FAIL] 品牌 token 快照缺失: {spec_path}", file=sys.stderr)
        sys.exit(2)
    try:
        spec = json.loads(spec_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"[FAIL] 品牌 token 快照不是合法 JSON: {spec_path}\n       {exc}",
              file=sys.stderr)
        sys.exit(2)
    theme = spec.get("theme")
    if not isinstance(theme, dict):
        print(f"[FAIL] 品牌 token 快照缺少 theme 表: {spec_path}", file=sys.stderr)
        sys.exit(2)
    missing = [k for k in THEME_KEYS if k not in theme]
    if missing:
        print(f"[FAIL] 品牌 token 快照 theme 缺少必需键: {', '.join(missing)}\n"
              f"       路径: {spec_path}", file=sys.stderr)
        sys.exit(2)
    return {k: theme[k] for k in THEME_KEYS}


TOKENS = _load()
