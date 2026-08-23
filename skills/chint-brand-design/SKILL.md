---
name: chint-brand-design
description: Official CHINT brand visual identity and design system skill. Use when designing, styling, or generating CHINT presentations (PPTX), Web UIs, CSS typography with CHINTinno font, data visualizations (Matplotlib, Seaborn, ECharts), reports, or marketing/product collateral under CHINT Electric Blue visual guidelines.
---

# CHINT Brand Identity & Visual Design Skill

Authoritative brand identity governance and asset system for all CHINT digital deliverables, presentations (PPTX), web interfaces, data visualizations, and reporting materials.

---

## Core Brand Foundations

### 1. Single Source of Truth: Tokens & Assets
- **Primary Brand Color**: `#1E50E6` (CHINT Electric Blue / 正泰极光蓝)
- **Gradient Banner**: `linear-gradient(90deg, #50C8FF 0%, #1E50C8 100%)` (Electric Cyan to Deep Blue)
- **Base Canvas / Background**: `#F6F6F6` (Crisp light gray canvas)
- **Surface / Card**: `#FFFFFF` with 1px border `#E2E8F0`
- **Text Hierarchy**: `#191919` (Titles/Headers) | `#333333` (Body text) | `#666666` (Captions/Footnotes)
- **Corporate Font**: `CHINTinno` (正泰拓新体) — weights `400` (Regular), `700` (Bold), `300` (Light)
- **CSS Fallback**: `'CHINTinno', 'PingFang SC', 'Microsoft YaHei', '微软雅黑', sans-serif`

> All bundled font files, vector logos, CSS styles, and Python helpers reside in `assets/` and `scripts/`.

---

## 4-Step Standard Execution Workflow

### Step 1: Scenario Identification & Asset Loading
Identify the target output format and load the corresponding brand tokens:
1. **PowerPoint Presentations (`.pptx`)**: Load layout parameters and colors via `scripts/chint_theme.py` (`get_pptx_config()`).
2. **Web / HTML / CSS**: Import `assets/styles/chint-fonts.css` and set `--font-chint: 'CHINTinno'`.
3. **Data Visualizations (Matplotlib / Seaborn / ECharts)**: Call `apply_matplotlib_theme()` or load `get_chart_palette()`.
4. **Markdown / HTML / PDF Reports**: Structure with corporate header banners, card containers, and standard table styling.

> **Completion Criterion**: Appropriate brand tokens and font configurations are verified and loaded.

---

### Step 2: Visual Structure & Grid Enforcement
Enforce standard brand layout principles:
- **Presentation (16:9)**: Set width `13.333 in` (960pt) and height `7.5 in` (540pt). Top banner height `0.95 in`. Margins `0.80 in`.
- **Card-Based Hierarchy**: Place foreground data and content inside `#FFFFFF` cards over the `#F6F6F6` background.
- **Zero-Emoji Policy**: Mandate vector icons (e.g. `lucide` / `lucide-react`) for UI actions and status indicators. Never use decorative emojis in enterprise deliverables.
- **Typographic Scale**: Slide titles `24pt - 28pt Bold`, card titles `18pt - 20pt Bold`, body text `13pt - 14pt Regular`.

> **Completion Criterion**: Layout adheres to the 16:9 grid, card structure, and typographic hierarchy.

---

### Step 3: Color Palette & Chart Styling
Apply official corporate colors strictly according to semantic meaning:
- **Hero & Primary Elements**: `#1E50E6` (Buttons, active tabs, main series).
- **Multi-Series Data Charts**: Use the 8-color corporate palette in order:
  `['#1E50E6', '#50C8FF', '#1E50C8', '#0070C0', '#F59E0B', '#10B981', '#6366F1', '#EC4899']`
- **Semantic Indicators**: Growth/Success `#16A34A` | Alert/Warning `#D97706` | Decline/Error `#DC2626`.

> **Completion Criterion**: Chart and UI colors match official hex values without unapproved arbitrary palettes.

---

### Step 4: Verification & Artifact Delivery
Verify all generated artifacts against the brand checklist:
- [ ] Font family explicitly set to `CHINTinno` with valid fallback stack.
- [ ] Primary accent matches `#1E50E6` (or gradient `#50C8FF` to `#1E50C8`).
- [ ] Contrast ratio meets WCAG 2.1 AA standards (dark text on light backgrounds).
- [ ] Clean vector logos referenced from `assets/logos/` when logo placement is required.
- [ ] Conversational delivery to user is strictly in **Chinese**, high-density, with zero raw code blocks.

> **Completion Criterion**: Artifacts pass all 5 verification points.

---

## References

- **Color Palette & Hex Values**: [references/color_palette.md](references/color_palette.md)
- **Typography & Font Hierarchy**: [references/typography.md](references/typography.md)
- **PPTX 16:9 Layout & python-pptx Blueprints**: [references/pptx_guidelines.md](references/pptx_guidelines.md)
- **Web Frontend & Chart Visualizations**: [references/web_and_charts.md](references/web_and_charts.md)
