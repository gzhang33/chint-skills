"""
Command line tool to validate PowerPoint presentation (.pptx / .potx) XML files against XSD schemas.

Usage:
    python validate.py <path> [--original <original_file>] [--auto-repair] [-v]

The first argument can be either:
- An unpacked directory containing PPTX presentation XML files
- A packed PowerPoint file (.pptx / .potx) which will be unpacked to a temp directory
"""

import argparse
import sys
import tempfile
import zipfile
from pathlib import Path

from helpers import OOXML_FAMILY, rezip, safe_extract
from validators import PPTXSchemaValidator


def _fail(message: str):
    print(f"Error: {message}", file=sys.stderr)
    sys.exit(2)


def main():
    parser = argparse.ArgumentParser(description="Validate PPTX presentation OpenXML schemas")
    parser.add_argument(
        "path",
        help="Path to unpacked directory or PowerPoint file (.pptx / .potx)",
    )
    parser.add_argument(
        "--original",
        required=False,
        default=None,
        help="Path to original file (.pptx / .potx).",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose output",
    )
    parser.add_argument(
        "--auto-repair",
        action="store_true",
        help="Automatically repair common issues and write back if packed file.",
    )
    args = parser.parse_args()

    path = Path(args.path)
    if not path.exists():
        _fail(f"{path} does not exist")

    original_file = None
    if args.original:
        original_file = Path(args.original)
        if not original_file.is_file():
            _fail(f"{original_file} is not a file")
        if original_file.suffix.lower() not in (".pptx", ".potx"):
            _fail(f"{original_file} must be a .pptx or .potx file")

    packed_file = None
    temp_dir_ctx = None
    if path.is_file() and path.suffix.lower() in (".pptx", ".potx"):
        packed_file = path
        temp_dir_ctx = tempfile.TemporaryDirectory()
        unpacked_dir = Path(temp_dir_ctx.name)
        try:
            with zipfile.ZipFile(path, "r") as zf:
                safe_extract(zf, unpacked_dir)
        except (zipfile.BadZipFile, ValueError, OSError) as e:
            _fail(f"cannot unpack {path}: {e}")
    else:
        if not path.is_dir():
            _fail(f"{path} is not a directory or PowerPoint (.pptx/.potx) file")
        unpacked_dir = path

    validators = [
        PPTXSchemaValidator(unpacked_dir, original_file, verbose=args.verbose),
    ]

    if args.auto_repair:
        total_repairs = sum(v.repair() for v in validators)
        if total_repairs:
            print(f"Auto-repaired {total_repairs} issue(s)")
            if packed_file is not None:
                rezip(unpacked_dir, packed_file)
                print(f"Wrote repaired file to {packed_file}")

    success = all(v.validate() for v in validators)

    if temp_dir_ctx is not None:
        temp_dir_ctx.cleanup()

    if success:
        print("All validations PASSED!")

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
