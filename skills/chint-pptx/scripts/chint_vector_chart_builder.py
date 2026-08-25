#!/usr/bin/env python3
"""
CHINT Vector Chart Builder (2026 VI Standard Edition)

Generates high-definition, publication-quality vector charts for PPTX presentations.
Features:
- Full registration of 正泰拓新体 (CHINTinno) font family.
- Official 2026 VI brand color tokens (Electric Blue #1E50E6, Light Cyan #50C8FF, Growth Green #14C832, etc.).
- Multi-dimensional Radar Chart (竞品与技术雷达).
- Dual-Axis Combo Chart (营收与增速双轴组合图).
- Diverging Horizontal Bar Chart (双向对比与分岔柱图).
- Stepped Evolution Chart (阶梯演进与成熟度图).
- Heatmap / Capability Matrix (行业与能力矩阵热力图).
- Lossless in-memory BytesIO generation (DPI=300, transparent/light background).
"""

import os
import io
import math
from typing import Dict, Any, List, Optional, Tuple, Union

import matplotlib
matplotlib.use('Agg')  # Headless non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import matplotlib.patches as mpatches
from matplotlib.path import Path
import numpy as np

# 2026 VI Brand Colors (HEX for Matplotlib)
HEX_BLUE = "#1E50E6"          # Electric Blue Primary
HEX_CYAN = "#50C8FF"          # Light Cyan Accent
HEX_RED = "#D70A32"           # Alert Red
HEX_RED_BG = "#FFEBEB"        # Soft Red Alert BG
HEX_GREEN = "#14C832"         # Growth Green
HEX_GREEN_BG = "#E8F8EE"      # Soft Green BG
HEX_TEAL = "#14C8B4"          # Smart Teal
HEX_DEEP_BLUE = "#1437AA"     # Deep Corporate Blue
HEX_BLUE_BG = "#EBF3FF"       # Soft Blue Container
HEX_ICE_BLUE = "#D7F0FF"      # Ice Blue
HEX_ORANGE = "#F59E0B"        # Warning Orange
HEX_DARK = "#1E2024"          # Primary Dark Text
HEX_MUTED = "#5A5A5A"         # Slate Gray Text
HEX_LIGHT_BG = "#F6F8FA"      # Container Light Background
HEX_BORDER = "#D0D7DE"        # Card Border
HEX_WHITE = "#FFFFFF"         # Pure White

# 8-stage Palette
PALETTE = [
    HEX_BLUE,
    HEX_CYAN,
    HEX_GREEN,
    HEX_TEAL,
    "#2378FF",
    "#5ADC19",
    HEX_ORANGE,
    HEX_RED
]

# Configure Fonts
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), "assets")
FONTS_DIR = os.path.join(ASSETS_DIR, "fonts")

FONT_NAME = "CHINTinno"
FONT_PROP_BOLD = None
FONT_PROP_REG = None

import functools

def chart_guard(func):
    """Decorator ensuring that any matplotlib figures are cleanly closed on exception to prevent memory leaks."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:
            plt.close('all')
            raise
    return wrapper


def _init_fonts():
    global FONT_PROP_BOLD, FONT_PROP_REG, FONT_NAME
    bold_path = os.path.join(FONTS_DIR, "CHINTinno-Bold.ttf")
    reg_path = os.path.join(FONTS_DIR, "CHINTinno-Regular.ttf")
    
    found = False
    if os.path.exists(bold_path):
        fm.fontManager.addfont(bold_path)
        FONT_PROP_BOLD = fm.FontProperties(fname=bold_path)
        FONT_NAME = FONT_PROP_BOLD.get_name()
        found = True
    if os.path.exists(reg_path):
        fm.fontManager.addfont(reg_path)
        FONT_PROP_REG = fm.FontProperties(fname=reg_path)
        if not FONT_PROP_BOLD:
            FONT_NAME = FONT_PROP_REG.get_name()
        found = True
            
    if not found:
        import warnings
        warnings.warn(f"[CHINT-VI] CHINTinno font files not found at {FONTS_DIR}. Falling back to system sans-serif.")

    # Set default font family fallback
    plt.rcParams['font.sans-serif'] = [FONT_NAME, 'Noto Sans SC', 'PingFang SC', 'Microsoft YaHei', 'sans-serif']
    plt.rcParams['axes.unicode_minus'] = False

_init_fonts()


class ChintVectorChartBuilder:
    """Generates 2026 VI compliant vector charts rendered directly into memory."""

    @staticmethod
    def _save_to_bytes(fig) -> io.BytesIO:
        try:
            buf = io.BytesIO()
            fig.savefig(buf, format='png', dpi=300, bbox_inches='tight', transparent=False, facecolor=HEX_LIGHT_BG)
            buf.seek(0)
            return buf
        finally:
            plt.close(fig)

    @classmethod
    @chart_guard
    def render_radar_chart(cls, categories: List[str], series_data: List[Dict[str, Any]],
                           title: str = "", figsize: Tuple[float, float] = (7.0, 5.0)) -> io.BytesIO:
        """
        Render multi-axis Radar Chart (竞品与技术能力雷达对标图).
        """
        N = len(categories)
        if N < 3:
            categories = categories + [f"维度{i+1}" for i in range(3 - N)]
            N = 3

        angles = [n / float(N) * 2 * math.pi for n in range(N)]
        angles += angles[:1]

        fig, ax = plt.subplots(figsize=figsize, subplot_kw=dict(polar=True), facecolor=HEX_LIGHT_BG)
        ax.set_facecolor(HEX_WHITE)

        plt.xticks(angles[:-1], categories, fontproperties=FONT_PROP_BOLD or FONT_PROP_REG,
                   size=10.5, color=HEX_DARK)

        plt.yticks([20, 40, 60, 80, 100], [])
        ax.set_yticklabels([])
        plt.ylim(0, 105)

        ax.grid(color=HEX_BORDER, linestyle='--', linewidth=0.8, alpha=0.8)
        ax.spines['polar'].set_color(HEX_BORDER)
        ax.spines['polar'].set_linewidth(1.0)

        for i, s in enumerate(series_data):
            vals = list(s.get("values", []))
            if len(vals) < N:
                vals += [50] * (N - len(vals))
            else:
                vals = vals[:N]
            vals_closed = vals + vals[:1]
            
            color = s.get("color", PALETTE[i % len(PALETTE)])
            name = s.get("name", f"系列 {i+1}")
            
            ax.plot(angles, vals_closed, linewidth=2.4, linestyle='solid', label=name, color=color)
            ax.fill(angles, vals_closed, color=color, alpha=0.22)
            ax.scatter(angles[:-1], vals, s=40, color=color, zorder=5)

            # Vertex value data labels with badge protection
            for angle, val in zip(angles[:-1], vals):
                ax.annotate(f"{val:g}",
                            xy=(angle, val),
                            xytext=(0, 4), textcoords="offset points",
                            ha='center', va='bottom',
                            fontproperties=FONT_PROP_BOLD,
                            size=8.5, color=color,
                            bbox=dict(boxstyle="round,pad=0.15", fc=HEX_WHITE, ec=color, lw=0.6, alpha=0.9),
                            zorder=6)

        if title:
            ax.set_title(title, fontproperties=FONT_PROP_BOLD, size=13, color=HEX_BLUE, pad=20)

        legend = ax.legend(loc='upper right', bbox_to_anchor=(1.35, 1.1),
                           prop=FONT_PROP_BOLD or FONT_PROP_REG, frameon=True,
                           facecolor=HEX_WHITE, edgecolor=HEX_BORDER, fontsize=9.5)
        legend.get_frame().set_linewidth(0.8)

        return cls._save_to_bytes(fig)

    @classmethod
    @chart_guard
    def render_combo_chart(cls, categories: List[str], bar_series: Dict[str, Any],
                           line_series: Dict[str, Any], title: str = "",
                           figsize: Tuple[float, float] = (7.0, 5.0)) -> io.BytesIO:
        """
        Render Dual-Axis Combo Chart (主轴柱状图 + 次轴折线图).
        """
        fig, ax1 = plt.subplots(figsize=figsize, facecolor=HEX_LIGHT_BG)
        ax1.set_facecolor(HEX_WHITE)
        plt.subplots_adjust(top=0.82, bottom=0.15, left=0.12, right=0.88)

        x = np.arange(len(categories))
        width = 0.45

        bar_vals = bar_series.get("values", [])
        bar_color = bar_series.get("color", HEX_BLUE)
        bar_name = bar_series.get("name", "柱状系列")
        bar_unit = bar_series.get("unit", "")
        
        rects = ax1.bar(x, bar_vals, width, label=bar_name, color=bar_color, zorder=3, alpha=0.92,
                        edgecolor=HEX_BLUE_BG, linewidth=0.5)

        max_bar = max(bar_vals) if bar_vals else 100
        ax1.set_ylim(0, max_bar * 1.40)

        for rect in rects:
            height = rect.get_height()
            if height > max_bar * 0.20:
                ax1.annotate(f"{height:g}{bar_unit}",
                             xy=(rect.get_x() + rect.get_width() / 2, height / 2),
                             ha='center', va='center', fontproperties=FONT_PROP_BOLD,
                             size=10.0, color=HEX_WHITE, zorder=6)
            else:
                ax1.annotate(f"{height:g}{bar_unit}",
                             xy=(rect.get_x() + rect.get_width() / 2, height),
                             xytext=(0, 4), textcoords="offset points",
                             ha='center', va='bottom', fontproperties=FONT_PROP_BOLD,
                             size=9.5, color=HEX_DARK, zorder=6)

        ax1.set_ylabel(f"{bar_name} ({bar_unit})" if bar_unit else bar_name,
                       fontproperties=FONT_PROP_BOLD, color=HEX_DARK, size=10)
        ax1.set_xticks(x)
        ax1.set_xticklabels(categories, fontproperties=FONT_PROP_BOLD, size=10, color=HEX_DARK)
        ax1.tick_params(axis='y', labelcolor=HEX_MUTED)
        ax1.grid(axis='y', linestyle='--', alpha=0.6, color=HEX_BORDER, zorder=0)

        ax2 = ax1.twinx()
        line_vals = line_series.get("values", [])
        line_color = line_series.get("color", HEX_GREEN)
        line_name = line_series.get("name", "折线系列")
        line_unit = line_series.get("unit", "%")

        min_line = min(line_vals) if line_vals else 0
        max_line = max(line_vals) if line_vals else 100
        ax2.set_ylim(min(0, min_line * 1.25), max_line * 1.38)

        l_plot = ax2.plot(x, line_vals, color=line_color, marker='o', linewidth=2.8,
                          markersize=6, label=line_name, zorder=5)

        for i, val in enumerate(line_vals):
            ax2.annotate(f"{val:g}{line_unit}",
                         xy=(x[i], val),
                         xytext=(0, 8), textcoords="offset points",
                         ha='center', va='bottom', fontproperties=FONT_PROP_BOLD,
                         size=9.0, color=HEX_WHITE,
                         bbox=dict(boxstyle="round,pad=0.25", fc=line_color, ec="none", alpha=0.95),
                         zorder=7)

        ax2.set_ylabel(f"{line_name} ({line_unit})" if line_unit else line_name,
                       fontproperties=FONT_PROP_BOLD, color=HEX_GREEN, size=10)
        ax2.tick_params(axis='y', labelcolor=HEX_MUTED)
        ax2.grid(False)

        for ax in [ax1, ax2]:
            ax.spines['top'].set_visible(False)
            ax.spines['left'].set_color(HEX_BORDER)
            ax.spines['right'].set_color(HEX_BORDER)
            ax.spines['bottom'].set_color(HEX_BORDER)

        if title:
            fig.suptitle(title, fontproperties=FONT_PROP_BOLD, size=13, color=HEX_BLUE, y=0.96)

        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        leg = ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left',
                         bbox_to_anchor=(0.0, 1.15), ncol=2,
                         prop=FONT_PROP_BOLD or FONT_PROP_REG, frameon=True,
                         facecolor=HEX_WHITE, edgecolor=HEX_BORDER, fontsize=9.5)
        leg.get_frame().set_linewidth(0.8)

        return cls._save_to_bytes(fig)

    @classmethod
    @chart_guard
    def render_diverging_bar(cls, categories: List[str], values: List[float],
                             title: str = "", unit: str = "%",
                             figsize: Tuple[float, float] = (7.0, 5.0)) -> io.BytesIO:
        """
        Render Diverging Horizontal Bar Chart (正向增长 vs 承压衰退分岔对比柱图).
        """
        fig, ax = plt.subplots(figsize=figsize, facecolor=HEX_LIGHT_BG)
        ax.set_facecolor(HEX_WHITE)
        plt.subplots_adjust(top=0.86, bottom=0.12, left=0.22, right=0.92)

        y_pos = np.arange(len(categories))
        colors = [HEX_GREEN if v >= 0 else HEX_RED for v in values]

        min_v = min(values) if values else -10
        max_v = max(values) if values else 10
        pad_v = max(abs(min_v), abs(max_v)) * 0.35 + 4
        ax.set_xlim(min_v - pad_v, max_v + pad_v)

        bars = ax.barh(y_pos, values, align='center', color=colors, height=0.55,
                       edgecolor=HEX_BORDER, linewidth=0.6, zorder=3)

        ax.axvline(0, color=HEX_DARK, linewidth=1.2, zorder=4)

        for bar, val in zip(bars, values):
            offset = 1.0 if val >= 0 else -1.0
            ha = 'left' if val >= 0 else 'right'
            ax.annotate(f"{val:+g}{unit}",
                        xy=(val + offset, bar.get_y() + bar.get_height() / 2),
                        ha=ha, va='center', fontproperties=FONT_PROP_BOLD,
                        size=9.5, color=HEX_GREEN if val >= 0 else HEX_RED)

        ax.set_yticks(y_pos)
        ax.set_yticklabels(categories, fontproperties=FONT_PROP_BOLD, size=10, color=HEX_DARK)
        ax.invert_yaxis()
        ax.grid(axis='x', linestyle='--', alpha=0.5, color=HEX_BORDER, zorder=0)

        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['bottom'].set_color(HEX_BORDER)

        if title:
            fig.suptitle(title, fontproperties=FONT_PROP_BOLD, size=13, color=HEX_BLUE, y=0.96)

        return cls._save_to_bytes(fig)

    @classmethod
    @chart_guard
    def render_evolution_chart(cls, stages: List[str], values: List[float],
                               sub_labels: Optional[List[str]] = None,
                               title: str = "", unit: str = "分",
                               figsize: Tuple[float, float] = (7.0, 5.0)) -> io.BytesIO:
        """
        Render Stepped Evolution Chart (阶梯成熟度演进图).
        """
        fig, ax = plt.subplots(figsize=figsize, facecolor=HEX_LIGHT_BG)
        ax.set_facecolor(HEX_WHITE)

        x = np.arange(len(stages))
        gradient_colors = [
            HEX_ICE_BLUE,
            HEX_CYAN,
            "#2378FF",
            HEX_BLUE
        ]
        if len(stages) > len(gradient_colors):
            colors = [HEX_BLUE] * len(stages)
        else:
            colors = gradient_colors[:len(stages)]

        bars = ax.bar(x, values, width=0.52, color=colors, edgecolor=HEX_BORDER, linewidth=0.8, zorder=3)

        ax.plot(x, values, color=HEX_BLUE, linestyle='--', linewidth=2.0, marker='D', markersize=6, zorder=4)

        for i, (bar, val) in enumerate(zip(bars, values)):
            ax.annotate(f"{val:g}{unit}",
                        xy=(bar.get_x() + bar.get_width() / 2, val),
                        xytext=(0, 5), textcoords="offset points",
                        ha='center', va='bottom', fontproperties=FONT_PROP_BOLD,
                        size=10, color=HEX_BLUE)
            if sub_labels and i < len(sub_labels):
                ax.annotate(sub_labels[i],
                            xy=(bar.get_x() + bar.get_width() / 2, val / 2),
                            ha='center', va='center', fontproperties=FONT_PROP_BOLD,
                            size=9, color=HEX_DARK if i == 0 else HEX_WHITE)

        ax.set_xticks(x)
        ax.set_xticklabels(stages, fontproperties=FONT_PROP_BOLD, size=10, color=HEX_DARK)
        ax.grid(axis='y', linestyle='--', alpha=0.5, color=HEX_BORDER, zorder=0)

        for sp in ['top', 'right', 'left']:
            ax.spines[sp].set_visible(False)
        ax.spines['bottom'].set_color(HEX_BORDER)

        if title:
            ax.set_title(title, fontproperties=FONT_PROP_BOLD, size=13, color=HEX_BLUE, pad=15)

        return cls._save_to_bytes(fig)

    @classmethod
    @chart_guard
    def render_heatmap_matrix(cls, row_labels: List[str], col_labels: List[str],
                              data_matrix: List[List[Union[float, int, str]]],
                              title: str = "", figsize: Tuple[float, float] = (7.0, 5.0)) -> io.BytesIO:
        """
        Render Capability / Fit Heatmap Matrix (能力与行业适配热力矩阵).
        """
        fig, ax = plt.subplots(figsize=figsize, facecolor=HEX_LIGHT_BG)
        ax.set_facecolor(HEX_WHITE)
        plt.subplots_adjust(top=0.86, bottom=0.18, left=0.18, right=0.92)

        numeric_data = np.zeros((len(row_labels), len(col_labels)))
        for r in range(len(row_labels)):
            for c in range(len(col_labels)):
                val = data_matrix[r][c]
                if isinstance(val, (int, float)):
                    numeric_data[r, c] = val
                else:
                    numeric_data[r, c] = 80

        cmap = matplotlib.colors.LinearSegmentedColormap.from_list("chint_blue", [HEX_WHITE, HEX_BLUE_BG, HEX_CYAN, HEX_BLUE])
        im = ax.imshow(numeric_data, cmap=cmap, aspect='auto')

        ax.set_xticks(np.arange(len(col_labels)))
        ax.set_yticks(np.arange(len(row_labels)))
        ax.set_xticklabels(col_labels, fontproperties=FONT_PROP_BOLD, size=10, color=HEX_DARK)
        ax.set_yticklabels(row_labels, fontproperties=FONT_PROP_BOLD, size=10, color=HEX_DARK)

        plt.setp(ax.get_xticklabels(), rotation=20, ha="right", rotation_mode="anchor")

        vmin, vmax = np.min(numeric_data), np.max(numeric_data)
        val_range = vmax - vmin if vmax > vmin else 1.0

        for i in range(len(row_labels)):
            for j in range(len(col_labels)):
                val_raw = data_matrix[i][j]
                text_val = f"{val_raw:g}" if isinstance(val_raw, (int, float)) else str(val_raw)
                val_num = numeric_data[i, j]
                norm_val = (val_num - vmin) / val_range
                text_color = HEX_WHITE if norm_val > 0.55 else HEX_DARK
                ax.text(j, i, text_val, ha="center", va="center",
                        fontproperties=FONT_PROP_BOLD, size=9.5, color=text_color)

        for sp in ax.spines.values():
            sp.set_color(HEX_BORDER)
            sp.set_linewidth(1.0)

        if title:
            fig.suptitle(title, fontproperties=FONT_PROP_BOLD, size=13, color=HEX_BLUE, y=0.96)

        return cls._save_to_bytes(fig)

    @classmethod
    @chart_guard
    def render_waterfall_chart(cls, categories: List[str], values: List[float],
                               initial_value: Optional[float] = None,
                               title: str = "", unit: str = "万",
                               figsize: Tuple[float, float] = (7.0, 5.0)) -> io.BytesIO:
        """
        Render Waterfall Attribution Chart (归因瀑布与毛利/成本桥接图).
        - Initial/Final bars: HEX_DEEP_BLUE
        - Positive deltas: HEX_GREEN
        - Negative deltas: HEX_RED
        - Step connector lines between adjacent bars.
        """
        fig, ax = plt.subplots(figsize=figsize, facecolor=HEX_LIGHT_BG)
        ax.set_facecolor(HEX_WHITE)

        cats = list(categories)
        vals = list(values)

        # Prepare bars calculation
        if initial_value is not None and (not cats or cats[0] != "初始值"):
            cats = ["基准起步"] + cats
            vals = [initial_value] + vals

        # Compute running bottoms and heights
        running_total = 0.0
        bottoms = []
        heights = []
        colors = []
        totals = []

        is_final_included = len(cats) > len(vals) or (len(cats) >= 2 and cats[-1] in ("最终值", "合计", "净利润", "终值", "净增量"))
        
        for i, (cat, val) in enumerate(zip(cats, vals)):
            if i == 0:
                bottoms.append(0.0)
                heights.append(val)
                colors.append(HEX_DEEP_BLUE)
                running_total = val
            elif i == len(cats) - 1 and is_final_included:
                bottoms.append(0.0)
                heights.append(running_total)
                colors.append(HEX_DEEP_BLUE)
            else:
                if val >= 0:
                    bottoms.append(running_total)
                    heights.append(val)
                    colors.append(HEX_GREEN)
                    running_total += val
                else:
                    bottoms.append(running_total + val)
                    heights.append(abs(val))
                    colors.append(HEX_RED)
                    running_total += val
            totals.append(running_total)

        # If final bar was not explicitly supplied, append a final summary bar
        if not is_final_included:
            cats.append("最终合计")
            bottoms.append(0.0)
            heights.append(running_total)
            colors.append(HEX_DEEP_BLUE)
            vals.append(running_total)
            totals.append(running_total)

        x = np.arange(len(cats))
        bars = ax.bar(x, heights, bottom=bottoms, width=0.55, color=colors,
                      edgecolor=HEX_BORDER, linewidth=0.8, zorder=3)

        # Draw connecting dashed step lines
        for i in range(len(cats) - 1):
            conn_y = totals[i]
            x_start = x[i] + 0.275
            x_end = x[i + 1] - 0.275
            ax.plot([x_start, x_end], [conn_y, conn_y], color=HEX_MUTED, linestyle='--', linewidth=1.0, zorder=2)

        # Value annotations
        for i, (bar, cat, val, bot) in enumerate(zip(bars, cats, vals, bottoms)):
            display_val = f"{val:+g}{unit}" if (i > 0 and i < len(cats) - 1 and is_final_included) or (i > 0 and not is_final_included and i < len(cats) - 1) else f"{val:g}{unit}"
            if i == 0 or i == len(cats) - 1:
                display_val = f"{heights[i]:g}{unit}"
                
            top_y = bot + heights[i]
            ax.annotate(display_val,
                        xy=(bar.get_x() + bar.get_width() / 2, top_y),
                        xytext=(0, 4), textcoords="offset points",
                        ha='center', va='bottom', fontproperties=FONT_PROP_BOLD,
                        size=9.0, color=colors[i])

        ax.set_xticks(x)
        ax.set_xticklabels(cats, fontproperties=FONT_PROP_BOLD, size=9.5, color=HEX_DARK)
        plt.setp(ax.get_xticklabels(), rotation=15, ha="right", rotation_mode="anchor")

        ax.grid(axis='y', linestyle='--', alpha=0.5, color=HEX_BORDER, zorder=0)
        for sp in ['top', 'right', 'left']:
            ax.spines[sp].set_visible(False)
        ax.spines['bottom'].set_color(HEX_BORDER)

        if title:
            ax.set_title(title, fontproperties=FONT_PROP_BOLD, size=13, color=HEX_BLUE, pad=15)

        return cls._save_to_bytes(fig)

    @classmethod
    @chart_guard
    def render_sankey_chart(cls, flows: Optional[List[Dict[str, Any]]] = None,
                            nodes: Optional[List[Dict[str, Any]]] = None,
                            links: Optional[List[Dict[str, Any]]] = None,
                            title: str = "", unit: str = "万",
                            figsize: Tuple[float, float] = (7.0, 5.0)) -> io.BytesIO:
        """
        Render Value Flow Sankey Diagram (价值流向与供应链流转桑基图).
        Supports flexible flows: [{"source": "源", "target": "目标", "value": 100, "color": ...}]
        """
        fig, ax = plt.subplots(figsize=figsize, facecolor=HEX_LIGHT_BG)
        ax.set_facecolor(HEX_WHITE)

        if not flows and (not nodes or not links):
            flows = [
                {"source": "集中光伏", "target": "智能电网", "value": 120, "color": HEX_BLUE},
                {"source": "集中光伏", "target": "工商业储能", "value": 80, "color": HEX_CYAN},
                {"source": "工商业配电", "target": "智能电网", "value": 150, "color": "#2378FF"},
                {"source": "工商业配电", "target": "微电网自愈", "value": 90, "color": HEX_TEAL},
                {"source": "算力中心", "target": "2N高可用供电", "value": 110, "color": HEX_DEEP_BLUE}
            ]

        # Extract unique sources and targets
        if flows:
            sources = list(dict.fromkeys(f["source"] for f in flows))
            targets = list(dict.fromkeys(f["target"] for f in flows))
            
            src_totals = {s: sum(f["value"] for f in flows if f["source"] == s) for s in sources}
            tgt_totals = {t: sum(f["value"] for f in flows if f["target"] == t) for t in targets}
            max_total = max(sum(src_totals.values()), sum(tgt_totals.values()), 1.0)

            # Node geometries
            x_left = 0.15
            x_right = 0.85
            node_width = 0.05
            gap = 0.04

            # Layout left nodes
            avail_h = 0.82
            left_node_geoms = {}
            current_y = 0.90
            total_src_val = sum(src_totals.values()) or 1.0
            
            for s in sources:
                h = (src_totals[s] / total_src_val) * (avail_h - gap * (len(sources) - 1))
                h = max(h, 0.03)
                top_y = current_y
                bot_y = current_y - h
                left_node_geoms[s] = {"top": top_y, "bottom": bot_y, "height": h, "curr_y": top_y}
                current_y -= (h + gap)

            # Layout right nodes
            right_node_geoms = {}
            current_y = 0.90
            total_tgt_val = sum(tgt_totals.values()) or 1.0
            for t in targets:
                h = (tgt_totals[t] / total_tgt_val) * (avail_h - gap * (len(targets) - 1))
                h = max(h, 0.03)
                top_y = current_y
                bot_y = current_y - h
                right_node_geoms[t] = {"top": top_y, "bottom": bot_y, "height": h, "curr_y": top_y}
                current_y -= (h + gap)

            # Draw flows as Bezier ribbons
            for f in flows:
                s, t, v = f["source"], f["target"], f["value"]
                color = f.get("color", HEX_BLUE)
                
                # Height of flow on left and right
                flow_h_left = (v / total_src_val) * (avail_h - gap * (len(sources) - 1))
                flow_h_right = (v / total_tgt_val) * (avail_h - gap * (len(targets) - 1))
                
                y0_top = left_node_geoms[s]["curr_y"]
                y0_bot = y0_top - flow_h_left
                left_node_geoms[s]["curr_y"] = y0_bot

                y1_top = right_node_geoms[t]["curr_y"]
                y1_bot = y1_top - flow_h_right
                right_node_geoms[t]["curr_y"] = y1_bot

                # Bezier ribbon vertices
                verts = [
                    (x_left + node_width, y0_top),
                    (x_left + node_width + 0.35, y0_top),
                    (x_right - 0.35, y1_top),
                    (x_right, y1_top),
                    (x_right, y1_bot),
                    (x_right - 0.35, y1_bot),
                    (x_left + node_width + 0.35, y0_bot),
                    (x_left + node_width, y0_bot),
                    (x_left + node_width, y0_top),
                ]
                codes = [
                    Path.MOVETO,
                    Path.CURVE4,
                    Path.CURVE4,
                    Path.CURVE4,
                    Path.LINETO,
                    Path.CURVE4,
                    Path.CURVE4,
                    Path.CURVE4,
                    Path.CLOSEPOLY,
                ]
                path = Path(verts, codes)
                patch = mpatches.PathPatch(path, facecolor=color, edgecolor='none', alpha=0.35, zorder=2)
                ax.add_patch(patch)

            # Draw left node rects & labels
            for s, geom in left_node_geoms.items():
                rect = mpatches.Rectangle((x_left, geom["bottom"]), node_width, geom["height"],
                                          facecolor=HEX_DEEP_BLUE, edgecolor=HEX_BORDER, linewidth=0.8, zorder=3)
                ax.add_patch(rect)
                mid_y = (geom["top"] + geom["bottom"]) / 2
                ax.text(x_left - 0.02, mid_y, f"{s}\n{src_totals[s]:g}{unit}",
                        ha='right', va='center', fontproperties=FONT_PROP_BOLD, size=9.0, color=HEX_DARK)

            # Draw right node rects & labels
            for t, geom in right_node_geoms.items():
                rect = mpatches.Rectangle((x_right, geom["bottom"]), node_width, geom["height"],
                                          facecolor=HEX_BLUE, edgecolor=HEX_BORDER, linewidth=0.8, zorder=3)
                ax.add_patch(rect)
                mid_y = (geom["top"] + geom["bottom"]) / 2
                ax.text(x_right + node_width + 0.02, mid_y, f"{t}\n{tgt_totals[t]:g}{unit}",
                        ha='left', va='center', fontproperties=FONT_PROP_BOLD, size=9.0, color=HEX_DARK)

        ax.set_xlim(0, 1.0)
        ax.set_ylim(0, 1.0)
        ax.axis('off')

        if title:
            fig.suptitle(title, fontproperties=FONT_PROP_BOLD, size=13, color=HEX_BLUE, y=0.96)

        return cls._save_to_bytes(fig)

    @classmethod
    @chart_guard
    def render_funnel_chart(cls, stages: List[str], values: List[float],
                            conversion_rates: Optional[List[float]] = None,
                            title: str = "", unit: str = "万",
                            figsize: Tuple[float, float] = (7.0, 5.0)) -> io.BytesIO:
        """
        Render Funnel Conversion Chart (业务漏斗与转化留存图).
        - Centered symmetric horizontal trapezoids (bounded in center 40% width)
        - Left column dedicated for stage names (20% width)
        - Right column dedicated for conversion rate callouts (25% width)
        """
        fig, ax = plt.subplots(figsize=figsize, facecolor=HEX_LIGHT_BG)
        ax.set_facecolor(HEX_WHITE)
        plt.subplots_adjust(top=0.88, bottom=0.08, left=0.04, right=0.96)

        N = len(stages)
        max_val = max(values) if values else 1.0
        funnel_colors = [HEX_DEEP_BLUE, HEX_BLUE, "#2378FF", HEX_CYAN, HEX_TEAL, HEX_ICE_BLUE]
        
        # Geometry constants
        y_step = 1.0 / (N + 0.2)
        h_ratio = 0.85
        band_h = y_step * h_ratio
        
        for i in range(N):
            val = values[i]
            next_val = values[i + 1] if i + 1 < N else val * 0.7
            
            # Constrain funnel width to max 38% centered at x=0.45
            w_top = (val / max_val) * 0.38
            w_bot = (next_val / max_val) * 0.38
            
            y_top = 0.94 - i * y_step
            y_bot = y_top - band_h
            
            x_top_l = 0.45 - w_top / 2
            x_top_r = 0.45 + w_top / 2
            x_bot_l = 0.45 - w_bot / 2
            x_bot_r = 0.45 + w_bot / 2
            
            # Trapezoid polygon
            verts = [
                (x_top_l, y_top),
                (x_top_r, y_top),
                (x_bot_r, y_bot),
                (x_bot_l, y_bot),
                (x_top_l, y_top)
            ]
            codes = [Path.MOVETO, Path.LINETO, Path.LINETO, Path.LINETO, Path.CLOSEPOLY]
            color = funnel_colors[i % len(funnel_colors)]
            patch = mpatches.PathPatch(Path(verts, codes), facecolor=color, edgecolor=HEX_WHITE, linewidth=1.2, alpha=0.92, zorder=3)
            ax.add_patch(patch)
            
            # Text inside trapezoid
            mid_y = (y_top + y_bot) / 2
            ax.text(0.45, mid_y, f"{val:g}{unit}",
                    ha='center', va='center', fontproperties=FONT_PROP_BOLD,
                    size=9.5, color=HEX_WHITE if i < 3 else HEX_DARK, zorder=5)
            
            # Stage label in left column (strictly separate)
            ax.text(0.04, mid_y, stages[i],
                    ha='left', va='center', fontproperties=FONT_PROP_BOLD,
                    size=9.5, color=HEX_DARK, zorder=5)
            
            # Conversion rate badge in right column (strictly separate)
            if i > 0:
                rate = conversion_rates[i] if conversion_rates and i < len(conversion_rates) else (val / values[i - 1] * 100 if values[i - 1] else 0)
                rate_text = f"转化率 {rate:.1f}%"
                ax.annotate(rate_text,
                            xy=(x_top_r, mid_y),
                            xytext=(0.82, mid_y),
                            ha='center', va='center',
                            fontproperties=FONT_PROP_BOLD, size=8.5, color=HEX_BLUE,
                            bbox=dict(boxstyle="round,pad=0.25", fc=HEX_BLUE_BG, ec=HEX_CYAN, lw=0.8),
                            arrowprops=dict(arrowstyle="->", color=HEX_CYAN, lw=1.0),
                            zorder=6)

        ax.set_xlim(0, 1.0)
        ax.set_ylim(0, 1.0)
        ax.axis('off')

        if title:
            fig.suptitle(title, fontproperties=FONT_PROP_BOLD, size=13, color=HEX_BLUE, y=0.96)

        return cls._save_to_bytes(fig)

    @classmethod
    @chart_guard
    def render_gauge_kpi_chart(cls, current_val: float, target_val: float = 100.0,
                               min_val: float = 0.0, max_val: float = 100.0,
                               title: str = "", subtitle: str = "", unit: str = "%",
                               thresholds: Optional[List[Tuple[float, float, str]]] = None,
                               figsize: Tuple[float, float] = (7.0, 5.0)) -> io.BytesIO:
        """
        Render Gauge / Bullet KPI Chart (半环目标达成与安全阈值仪表盘).
        - 180° semi-circular arc with section colors (alert, caution, excellent)
        - Highlighted needle indicator
        - Large hero number callout positioned cleanly at origin
        """
        fig, ax = plt.subplots(figsize=figsize, subplot_kw=dict(polar=True), facecolor=HEX_LIGHT_BG)
        ax.set_facecolor(HEX_WHITE)
        plt.subplots_adjust(top=0.85, bottom=0.10)

        # Standard 180 degree gauge from pi to 0
        if not thresholds:
            thresholds = [
                (min_val, min_val + (max_val - min_val) * 0.6, HEX_BORDER),       # 起步区间
                (min_val + (max_val - min_val) * 0.6, min_val + (max_val - min_val) * 0.85, HEX_CYAN), # 良好区间
                (min_val + (max_val - min_val) * 0.85, max_val, HEX_GREEN)        # 卓越区间
            ]

        # Draw gauge background arcs
        val_range = max_val - min_val if max_val != min_val else 1.0
        for low, high, col in thresholds:
            theta_start = math.pi * (1.0 - (low - min_val) / val_range)
            theta_end = math.pi * (1.0 - (high - min_val) / val_range)
            thetas = np.linspace(theta_start, theta_end, 50)
            ax.fill_between(thetas, 0.70, 1.0, color=col, alpha=0.85, zorder=2)

        # Draw active progress arc
        clamped_val = max(min(current_val, max_val), min_val)
        curr_theta = math.pi * (1.0 - (clamped_val - min_val) / val_range)
        active_thetas = np.linspace(math.pi, curr_theta, 60)
        ax.fill_between(active_thetas, 0.72, 0.98, color=HEX_BLUE, alpha=0.95, zorder=4)

        # Draw Needle
        ax.plot([curr_theta, curr_theta], [0, 0.88], color=HEX_DARK, linewidth=3.0, zorder=6)
        ax.scatter([curr_theta], [0], color=HEX_DEEP_BLUE, s=120, zorder=7)

        # Ticks and Labels
        ax.set_thetamax(180)
        ax.set_thetamin(0)
        ax.set_theta_zero_location("E")
        ax.set_theta_direction(1)
        ax.grid(False)
        ax.set_yticklabels([])
        ax.set_xticklabels([])
        ax.spines['polar'].set_visible(False)

        # Central Hero Metric Text
        achieve_rate = (current_val / target_val * 100.0) if target_val else current_val
        ax.text(math.pi / 2, 0.40, f"{current_val:g}{unit}",
                ha='center', va='center', fontproperties=FONT_PROP_BOLD,
                size=22, color=HEX_BLUE, zorder=8)
        sub = subtitle or f"目标达成率 {achieve_rate:.1f}%"
        ax.text(math.pi / 2, 0.18, sub,
                ha='center', va='center', fontproperties=FONT_PROP_BOLD,
                size=9.5, color=HEX_MUTED, zorder=8)

        # Min/Max labels at outer arc ends
        ax.text(math.pi, 1.15, f"{min_val:g}{unit}", ha='center', va='center',
                fontproperties=FONT_PROP_BOLD, size=9.0, color=HEX_MUTED)
        ax.text(0, 1.15, f"{max_val:g}{unit}", ha='center', va='center',
                fontproperties=FONT_PROP_BOLD, size=9.0, color=HEX_MUTED)

        if title:
            fig.suptitle(title, fontproperties=FONT_PROP_BOLD, size=13, color=HEX_BLUE, y=0.96)

        return cls._save_to_bytes(fig)

    @classmethod
    @chart_guard
    def render_stacked_area_chart(cls, categories: List[str], series_data: List[Dict[str, Any]],
                                  title: str = "", unit: str = "亿",
                                  figsize: Tuple[float, float] = (7.0, 5.0)) -> io.BytesIO:
        """
        Render Multi-Dimensional Stacked Area Chart (多产品线规模演进堆叠面积图).
        - Smooth multi-series fill
        - 2026 VI color palette layering
        - Shows total line and series breakdown
        """
        fig, ax = plt.subplots(figsize=figsize, facecolor=HEX_LIGHT_BG)
        ax.set_facecolor(HEX_WHITE)
        plt.subplots_adjust(top=0.82, bottom=0.15, left=0.12, right=0.92)

        x = np.arange(len(categories))
        
        y_arrays = []
        labels = []
        colors = []
        
        for i, s in enumerate(series_data):
            labels.append(s.get("name", f"产品线 {i+1}"))
            colors.append(s.get("color", PALETTE[i % len(PALETTE)]))
            y_arrays.append(s.get("values", [10] * len(categories)))

        y_stack = np.vstack(y_arrays)
        
        # Render stackplot
        ax.stackplot(x, y_stack, labels=labels, colors=colors, alpha=0.85, edgecolor=HEX_WHITE, linewidth=1.0, zorder=3)

        # Top total curve
        totals = np.sum(y_stack, axis=0)
        max_tot = max(totals) if len(totals) > 0 else 100
        ax.set_ylim(0, max_tot * 1.30)
        ax.plot(x, totals, color=HEX_DARK, linestyle='--', linewidth=1.8, marker='o', markersize=5, label="总体规模", zorder=4)

        for i, tot in enumerate(totals):
            ax.annotate(f"{tot:g}{unit}",
                        xy=(x[i], tot),
                        xytext=(0, 5), textcoords="offset points",
                        ha='center', va='bottom', fontproperties=FONT_PROP_BOLD,
                        size=9.5, color=HEX_DARK)

        ax.set_xticks(x)
        ax.set_xticklabels(categories, fontproperties=FONT_PROP_BOLD, size=10, color=HEX_DARK)
        ax.set_ylabel(f"规模总量 ({unit})", fontproperties=FONT_PROP_BOLD, size=10, color=HEX_DARK)
        ax.grid(axis='y', linestyle='--', alpha=0.5, color=HEX_BORDER, zorder=0)

        for sp in ['top', 'right', 'left']:
            ax.spines[sp].set_visible(False)
        ax.spines['bottom'].set_color(HEX_BORDER)

        if title:
            fig.suptitle(title, fontproperties=FONT_PROP_BOLD, size=13, color=HEX_BLUE, y=0.96)

        leg = ax.legend(loc='upper left', bbox_to_anchor=(0.0, 1.14), ncol=3,
                        prop=FONT_PROP_BOLD or FONT_PROP_REG, frameon=True,
                        facecolor=HEX_WHITE, edgecolor=HEX_BORDER, fontsize=9.0)
        leg.get_frame().set_linewidth(0.8)

        return cls._save_to_bytes(fig)
