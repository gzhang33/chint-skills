"""Compatibility entry point; active implementation lives under scripts/."""
from __future__ import annotations
import importlib.util
import pathlib
import sys

_ACTIVE = pathlib.Path(__file__).resolve().parents[3] / "scripts" / "chint_vector_chart_builder.py"
if str(_ACTIVE.parent) in sys.path:
    sys.path.remove(str(_ACTIVE.parent))
sys.path.insert(0, str(_ACTIVE.parent))
_spec = importlib.util.spec_from_file_location("_chint_active_chint_vector_chart_builder", _ACTIVE)
_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_module)

for _key in dir(_module):
    if not _key.startswith("__"):
        globals()[_key] = getattr(_module, _key)
