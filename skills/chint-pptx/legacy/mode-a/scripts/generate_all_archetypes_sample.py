"""Compatibility entry point; active implementation lives under scripts/."""
from __future__ import annotations
import importlib.util
import pathlib
import sys

_ACTIVE = pathlib.Path(__file__).resolve().parents[3] / "samples" / "legacy" / "generate_all_archetypes_sample.py"
if str(_ACTIVE.parent) in sys.path:
    sys.path.remove(str(_ACTIVE.parent))
sys.path.insert(0, str(_ACTIVE.parent))
_spec = importlib.util.spec_from_file_location("_chint_active_generate_all_archetypes_sample", _ACTIVE)
_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_module)

if __name__ == "__main__":
    import runpy
    runpy.run_path(str(_ACTIVE), run_name="__main__")
