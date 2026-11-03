"""Shared output-location policy for generated CHINT presentation artifacts."""
from __future__ import annotations

import os
from pathlib import Path


def skill_root() -> Path:
    return Path(__file__).resolve().parents[1]


def ensure_output_path(value: str | os.PathLike[str]) -> Path:
    """Resolve an output path and reject writes anywhere inside this skill."""
    candidate = Path(value).expanduser()
    if not candidate.is_absolute():
        candidate = Path.cwd() / candidate
    candidate = candidate.resolve(strict=False)
    root = skill_root().resolve(strict=False)
    try:
        candidate.relative_to(root)
    except ValueError:
        return candidate
    raise ValueError(f"Generated files must be saved outside the skill folder: {candidate}")


def _documents_directory() -> Path:
    if os.name == "nt":
        try:
            import ctypes

            folder = ctypes.create_unicode_buffer(260)
            result = ctypes.windll.shell32.SHGetFolderPathW(None, 5, None, 0, folder)
            if result == 0 and folder.value:
                return Path(folder.value)
        except (AttributeError, OSError):
            pass

    configured = os.environ.get("XDG_DOCUMENTS_DIR")
    if configured:
        return Path(os.path.expandvars(os.path.expanduser(configured)))
    return Path.home() / "Documents"


def default_output_dir() -> Path:
    """Use an explicit user override or the platform's Documents/CHINT-PPTX folder."""
    configured = os.environ.get("CHINT_PPTX_OUTPUT_DIR")
    base = Path(configured).expanduser() if configured else _documents_directory() / "CHINT-PPTX"
    return ensure_output_path(base)
