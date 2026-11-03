#!/usr/bin/env python3
"""Render a PPTX to PDF, full-slide JPEGs, and a contact sheet for visual review."""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import fitz
from PIL import Image, ImageOps, ImageDraw

SKILL_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_ROOT))
from core.output_paths import ensure_output_path


def find_soffice():
    configured = os.environ.get("CHINT_PPTX_SOFFICE")
    candidates = [configured, shutil.which("soffice"), shutil.which("libreoffice"),
                  "/Applications/LibreOffice.app/Contents/MacOS/soffice",
                  "/usr/bin/soffice", r"C:\Program Files\LibreOffice\program\soffice.exe"]
    return next((str(value) for value in candidates if value and Path(value).is_file()), None)


def render(pptx: Path, output_dir: Path) -> int:
    try:
        output_dir = ensure_output_path(output_dir)
    except ValueError as exc:
        print(f"[FAIL] {exc}", file=sys.stderr)
        return 2
    if not pptx.is_file() or pptx.suffix.lower() not in (".pptx", ".potx"):
        print("[FAIL] Input must be an existing .pptx or .potx file.", file=sys.stderr)
        return 2
    soffice = find_soffice()
    if not soffice:
        print("[FAIL] LibreOffice soffice was not found. Set CHINT_PPTX_SOFFICE to its executable.", file=sys.stderr)
        return 2
    output_dir.mkdir(parents=True, exist_ok=True)
    pdf = output_dir / f"{pptx.stem}.pdf"
    with tempfile.TemporaryDirectory(prefix="chint-pptx-lo-") as profile:
        profile_url = Path(profile).resolve().as_uri()
        command = [soffice, f"-env:UserInstallation={profile_url}", "--headless", "--convert-to", "pdf", "--outdir", str(output_dir), str(pptx)]
        try:
            result = subprocess.run(command, capture_output=True, text=True, timeout=240, check=False)
        except (OSError, subprocess.TimeoutExpired) as exc:
            print(f"[FAIL] LibreOffice could not render the deck: {exc}", file=sys.stderr)
            return 2
    if result.returncode or not pdf.is_file():
        print("[FAIL] LibreOffice PDF export failed.", file=sys.stderr)
        if result.stderr.strip():
            print(result.stderr.strip(), file=sys.stderr)
        return 1

    deck = fitz.open(pdf)
    previews = []
    for number, page in enumerate(deck, 1):
        pixmap = page.get_pixmap(matrix=fitz.Matrix(1.4, 1.4), alpha=False)
        target = output_dir / f"{pptx.stem}-slide-{number:03d}.jpg"
        pixmap.save(target, jpg_quality=90)
        previews.append(target)

    thumb_width, columns, padding = 420, 3, 18
    thumbs = []
    for path in previews:
        with Image.open(path) as image:
            thumb_height = round(image.height * thumb_width / image.width)
            thumbs.append(ImageOps.contain(image.convert("RGB"), (thumb_width, thumb_height)))
    row_heights = [max(image.height for image in thumbs[start:start + columns])
                   for start in range(0, len(thumbs), columns)]
    sheet = Image.new("RGB", (padding + columns * (thumb_width + padding),
                               padding + sum(h + padding for h in row_heights)), "#e9eef7")
    draw = ImageDraw.Draw(sheet)
    for index, image in enumerate(thumbs):
        row, col = divmod(index, columns)
        x, y = padding + col * (thumb_width + padding), padding + sum(h + padding for h in row_heights[:row])
        sheet.paste(image, (x, y + 28))
        draw.text((x, y + 5), f"Slide {index + 1}", fill="#1437aa")
    contact_sheet = output_dir / f"{pptx.stem}-contact-sheet.jpg"
    sheet.save(contact_sheet, quality=90)
    print(f"[PASS] Rendered {len(previews)} slides.")
    print(f"PDF: {pdf}")
    print(f"Contact sheet: {contact_sheet}")
    print(f"Full-resolution slides: {output_dir}")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pptx", help="source presentation to render")
    parser.add_argument("--output-dir", required=True, help="directory for the PDF and slide previews")
    args = parser.parse_args(argv)
    return render(Path(args.pptx).resolve(), Path(args.output_dir))


if __name__ == "__main__":
    raise SystemExit(main())
