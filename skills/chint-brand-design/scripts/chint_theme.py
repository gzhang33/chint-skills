#!/usr/bin/env python3
"""
CHINT Brand Theme & Visual Asset Manager
Location: skills/chint-brand-design/scripts/chint_theme.py

Single Source of Truth for CHINT Brand Visual Standards:
- Typography: CHINTinno (正泰拓新体) Regular, Bold, Light
- Color System: Electric Blue (#1E50E6), Cyan Accent (#50C8FF), Deep Blue (#1E50C8)
- Chart Palette: 8-series high contrast corporate palette
- Presets for Matplotlib, python-pptx, CSS tokens, and ECharts
"""

import os
from typing import Dict, List, Optional, Tuple

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_ROOT = os.path.dirname(CURRENT_DIR)
ASSETS_DIR = os.path.join(SKILL_ROOT, "assets")

CHINT_COLORS: Dict[str, str] = {
    # Primary Brand Colors
    "primary": "#1E50E6",          # CHINT Electric Blue (主品牌极光蓝)
    "primary_hover": "#1E62DE",    # Interactive hover
    "primary_dark": "#1E50C8",     # Deep blue for accents and banner gradients
    "primary_light": "#50C8FF",    # Cyan blue accent / gradient start
    "primary_classic": "#0070C0",  # Classic corporate blue
    
    # Gradients
    "gradient_from": "#50C8FF",
    "gradient_to": "#1E50C8",
    "gradient_banner": "linear-gradient(90deg, #50C8FF 0%, #1E50C8 100%)",

    # Neutral / Backgrounds (Light Theme)
    "background": "#F6F6F6",       # App / Canvas base background
    "surface": "#FFFFFF",          # Card, modal, sheet surface
    "bg_subtle": "#F3F6FE",        # Light blue tint for highlights / table zebra
    "border": "#E2E8F0",           # Standard card / divider border
    "border_light": "#CBD5E1",     # Input border

    # Typography Colors
    "text_dark": "#191919",        # Primary headers & high-contrast titles
    "text_main": "#191919",        # Body text main
    "text_soft": "#333333",        # Secondary body text
    "text_muted": "#666666",       # Captions, footnotes, disabled states
    "text_faint": "#94A3B8",       # Placeholder text
    "btn_text": "#FFFFFF",         # Primary button label text

    # Semantic Status Colors
    "status_success": "#16A34A",   # Verified / Growth / On-target
    "status_warning": "#D97706",   # Alert / Caution / Replacement in progress
    "status_error": "#DC2626",     # Decline / Critical / Failure
    "status_info": "#0284C7",      # Informational notices
}

# Multi-series data visualization palette
CHINT_CHART_PALETTE: List[str] = [
    "#1E50E6",  # CHINT Electric Blue
    "#50C8FF",  # Electric Cyan
    "#1E50C8",  # Deep Accent Blue
    "#0070C0",  # Classic Corporate Blue
    "#F59E0B",  # Amber Accent
    "#10B981",  # Emerald Green
    "#6366F1",  # Indigo Accent
    "#EC4899",  # Magenta Accent
]

CHINT_FONTS: Dict[str, str] = {
    "brand_family": "CHINTinno",
    "cjk_family": "正泰拓新体",
    "css_font_family": "'CHINTinno', 'PingFang SC', 'Microsoft YaHei', '微软雅黑', sans-serif",
    "matplotlib_font_family": "CHINTinno",
    "pptx_font_family": "CHINTinno",
}


def hex_to_rgb(hex_str: str) -> Tuple[int, int, int]:
    """Converts hex color string to RGB tuple (e.g. '#1E50E6' -> (30, 80, 230))."""
    hex_str = hex_str.lstrip("#")
    return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))  # type: ignore


def get_brand_colors() -> Dict[str, str]:
    """Returns the full brand color dictionary."""
    return dict(CHINT_COLORS)


def get_chart_palette() -> List[str]:
    """Returns the official 8-color chart palette."""
    return list(CHINT_CHART_PALETTE)


def get_font_family(mode: str = "css") -> str:
    """Returns the font-family string according to target platform ('css', 'matplotlib', 'pptx')."""
    if mode == "css":
        return CHINT_FONTS["css_font_family"]
    elif mode == "matplotlib":
        return CHINT_FONTS["matplotlib_font_family"]
    elif mode == "pptx":
        return CHINT_FONTS["pptx_font_family"]
    return CHINT_FONTS["brand_family"]


def get_font_file(weight: str = "regular") -> Optional[str]:
    """Returns the local absolute path to the bundled TTF font file."""
    filename_map = {
        "regular": "CHINTinno-Regular.ttf",
        "bold": "CHINTinno-Bold.ttf",
        "light": "CHINTinno-Light.ttf",
    }
    fname = filename_map.get(weight.lower(), "CHINTinno-Regular.ttf")
    path = os.path.join(ASSETS_DIR, "fonts", fname)
    if os.path.exists(path):
        return path
    
    # Fallback to system fonts directory if available on macOS
    sys_path = os.path.expanduser(f"~/Library/Fonts/{fname}")
    if os.path.exists(sys_path):
        return sys_path
    return None


def get_logo_path(asset_type: str = "svg") -> Optional[str]:
    """Returns the path to the specified logo format ('svg', 'png', 'logo2', 'favicon')."""
    asset_map = {
        "svg": "chint_logo.svg",
        "png": "chint_logo.png",
        "logo2": "chint_logo2.png",
        "favicon": "chint_favicon.ico",
    }
    fname = asset_map.get(asset_type.lower(), "chint_logo.svg")
    path = os.path.join(ASSETS_DIR, "logos", fname)
    return path if os.path.exists(path) else None


def apply_matplotlib_theme(plt=None):
    """
    Applies CHINT brand styling to Matplotlib global rcParams.
    If plt is None, attempts to import matplotlib.pyplot automatically.
    """
    try:
        if plt is None:
            import matplotlib.pyplot as plt
        import matplotlib.font_manager as fm

        # Register bundled font file if available
        font_ttf = get_font_file("regular")
        if font_ttf and os.path.exists(font_ttf):
            try:
                fm.fontManager.addfont(font_ttf)
            except Exception:
                pass

        plt.rcParams["font.family"] = ["CHINTinno", "PingFang SC", "Microsoft YaHei", "sans-serif"]
        plt.rcParams["axes.unicode_minus"] = False
        plt.rcParams["figure.facecolor"] = CHINT_COLORS["surface"]
        plt.rcParams["axes.facecolor"] = CHINT_COLORS["surface"]
        plt.rcParams["axes.edgecolor"] = CHINT_COLORS["border"]
        plt.rcParams["axes.labelcolor"] = CHINT_COLORS["text_dark"]
        plt.rcParams["xtick.color"] = CHINT_COLORS["text_soft"]
        plt.rcParams["ytick.color"] = CHINT_COLORS["text_soft"]
        plt.rcParams["text.color"] = CHINT_COLORS["text_dark"]
        plt.rcParams["grid.color"] = CHINT_COLORS["border"]
        plt.rcParams["grid.linestyle"] = "--"
        plt.rcParams["grid.alpha"] = 0.6
        plt.rcParams["axes.prop_cycle"] = plt.cycler(color=CHINT_CHART_PALETTE)
        return True
    except ImportError:
        return False


def get_pptx_config() -> dict:
    """Returns standardized PPTX visual design parameters."""
    return {
        "slide_width_inches": 13.333,
        "slide_height_inches": 7.5,
        "font_name": "CHINTinno",
        "font_fallback": "微软雅黑",
        "colors_rgb": {
            "primary": hex_to_rgb(CHINT_COLORS["primary"]),
            "primary_dark": hex_to_rgb(CHINT_COLORS["primary_dark"]),
            "primary_light": hex_to_rgb(CHINT_COLORS["primary_light"]),
            "background": hex_to_rgb(CHINT_COLORS["background"]),
            "surface": hex_to_rgb(CHINT_COLORS["surface"]),
            "text_dark": hex_to_rgb(CHINT_COLORS["text_dark"]),
            "text_soft": hex_to_rgb(CHINT_COLORS["text_soft"]),
            "text_muted": hex_to_rgb(CHINT_COLORS["text_muted"]),
            "border": hex_to_rgb(CHINT_COLORS["border"]),
            "white": (255, 255, 255),
        },
        "banner_height_inches": 0.95,
        "margin_left_inches": 0.8,
        "margin_right_inches": 0.8,
        "title_font_pt": 24,
        "subtitle_font_pt": 14,
        "body_font_pt": 13,
        "card_header_pt": 15,
        "logo_path": get_logo_path("png"),
    }
