"""CHINT Brand Design Script Package."""
from .chint_theme import (
    CHINT_COLORS,
    CHINT_CHART_PALETTE,
    CHINT_FONTS,
    CHINT_2026_MATRIX,
    get_brand_colors,
    get_chart_palette,
    get_font_family,
    get_font_file,
    get_logo_path,
    apply_matplotlib_theme,
    get_pptx_config,
    get_2026_color_matrix,
    get_template_path,
    hex_to_rgb,
)
from .generate_template import generate_pptx_deck, generate_html_template
from .lint_brand import lint_path, lint_file

__all__ = [
    "CHINT_COLORS",
    "CHINT_CHART_PALETTE",
    "CHINT_FONTS",
    "CHINT_2026_MATRIX",
    "get_brand_colors",
    "get_chart_palette",
    "get_font_family",
    "get_font_file",
    "get_logo_path",
    "apply_matplotlib_theme",
    "get_pptx_config",
    "get_2026_color_matrix",
    "get_template_path",
    "hex_to_rgb",
    "generate_pptx_deck",
    "generate_html_template",
    "lint_path",
    "lint_file",
]

