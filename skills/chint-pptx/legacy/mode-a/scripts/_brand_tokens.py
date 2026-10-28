"""Compatibility entry point; active implementation lives under scripts/."""
from __future__ import annotations
import importlib.util
import pathlib
import sys

_ACTIVE = pathlib.Path(__file__).resolve().parents[3] / "scripts" / "_brand_tokens.py"
if str(_ACTIVE.parent) in sys.path:
    sys.path.remove(str(_ACTIVE.parent))
sys.path.insert(0, str(_ACTIVE.parent))
_spec = importlib.util.spec_from_file_location("_chint_active__brand_tokens", _ACTIVE)
_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_module)

TOKENS = _module.TOKENS
THEME_KEYS = _module.THEME_KEYS
