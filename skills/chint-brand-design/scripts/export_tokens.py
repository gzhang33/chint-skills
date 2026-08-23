#!/usr/bin/env python3
"""
CHINT Brand Tokens Exporter
Exports CHINT design tokens to JSON, CSS Custom Properties, or Tailwind Theme extension format.
"""

import json
import os
import sys

try:
    from .chint_theme import CHINT_COLORS, CHINT_CHART_PALETTE, CHINT_FONTS
except ImportError:
    from chint_theme import CHINT_COLORS, CHINT_CHART_PALETTE, CHINT_FONTS


def export_json(filepath: str):
    """Exports brand tokens to JSON."""
    data = {
        "colors": CHINT_COLORS,
        "chart_palette": CHINT_CHART_PALETTE,
        "fonts": CHINT_FONTS,
    }
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Exported JSON tokens to: {filepath}")


def export_css(filepath: str):
    """Exports CSS variables."""
    lines = [
        "/**",
        " * CHINT Brand Design Tokens (CSS Variables)",
        " * Generated automatically by chint-brand-design skill",
        " */",
        ":root {",
    ]
    for k, v in CHINT_COLORS.items():
        css_var_name = f"--chint-{k.replace('_', '-')}"
        lines.append(f"  {css_var_name}: {v};")
    
    lines.append(f"  --font-chint: {CHINT_FONTS['css_font_family']};")
    lines.append("}")
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"Exported CSS variables to: {filepath}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Export CHINT Brand Tokens")
    parser.add_argument("--format", choices=["json", "css", "all"], default="all")
    parser.add_argument("--outdir", default=".")
    args = parser.parse_args()

    os.makedirs(args.outdir, exist_ok=True)
    if args.format in ("json", "all"):
        export_json(os.path.join(args.outdir, "chint_tokens.json"))
    if args.format in ("css", "all"):
        export_css(os.path.join(args.outdir, "chint_tokens.css"))
