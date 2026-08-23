---
name: chint-brand-design
description: Official CHINT brand visual identity and design system skill. Use when designing, styling, or generating CHINT presentations (PPTX), Web UIs, CSS typography with CHINTinno font, data visualizations (Matplotlib, Seaborn, ECharts), reports, or marketing/product collateral under CHINT Electric Blue visual guidelines.
---

# CHINT Brand Identity & Visual Design Skill

Authoritative brand identity governance, template generation, and asset system for all CHINT digital deliverables, presentations (PPTX), web interfaces, data visualizations, and reporting materials, strictly aligned with the **2026 CHINT Corporate Visual Identity Standards**.

---

## Core Brand Foundations

### 1. Single Source of Truth: Tokens & Assets
- **Primary Brand Color**: `#1E50E6` (CHINT Electric Blue / 正泰极光蓝)
- **2026 Matrix Palette**: 7-step Primary Blue (`#1437AA` ~ `#D7F0FF`), 4-step Green Energy (`#14C832` ~ `#DCFF8C`), 4-step Smart Cyan (`#14C8B4` ~ `#C8FFDC`), 4-step Neutral Gray (`#5A5A5A` ~ `#F0F0F0`), Alert Red (`#D70A32`).
- **Gradient Banner**: `linear-gradient(90deg, #50C8FF 0%, #1E50C8 100%)` (Electric Cyan to Deep Blue)
- **Base Canvas / Background**: `#F6F6F6` (Crisp light gray canvas)
- **Surface / Card**: `#FFFFFF` with 1px border `#E2E8F0`
- **Text Hierarchy**: `#191919` (Titles/Headers) | `#333333` (Body text) | `#666666` (Captions/Footnotes)
- **Corporate Font**: `CHINTinno` (正泰拓新体) — weights `400` (Regular), `700` (Bold), `300` (Light)
- **CSS Fallback**: `'CHINTinno', 'Microsoft YaHei', 'PingFang SC', '微软雅黑', sans-serif`
- **Official 2026 Master PPTX**: Bundled at `assets/templates/chint_2026_template.pptx`

> All bundled font files, vector logos, 2026 master templates, CSS styles, and Python helpers reside in `assets/` and `scripts/`.

---

## 4-Step Standard Execution Workflow

### Step 1: Scenario Identification & Asset Loading
Identify the target output format and load the corresponding brand tokens or templates:
1. **PowerPoint Presentations (`.pptx`)**:
   - Generate directly from the 2026 master: `python3 scripts/generate_template.py --type pptx --title "..." --subtitle "..."`
   - Or load layout parameters via `scripts/chint_theme.py` (`get_pptx_config()`).
2. **Web / HTML / CSS**: Import `assets/styles/chint-fonts.css` and use `--font-chint: 'CHINTinno', 'Microsoft YaHei', 'PingFang SC', sans-serif;`.
3. **Data Visualizations (Matplotlib / Seaborn / ECharts)**: Call `apply_matplotlib_theme()` or load `get_chart_palette()`.
4. **Markdown / HTML / PDF Reports**: Generate standard HTML skeletons via `python3 scripts/generate_template.py --type html`.

> **Completion Criterion**: Appropriate brand tokens, templates, and font configurations are verified and loaded.

---

### Step 2: Visual Structure & Grid Enforcement
Enforce standard brand layout principles:
- **Presentation (16:9)**: Widescreen width `13.333 in` (960pt) and height `7.5 in` (540pt).
- **2026 Master Slide Layouts**: Cover Slide, 5-Card Table of Contents, Chapter Dividers, Standard Content/Chart page, Closing slide.
- **Card-Based Hierarchy**: Place foreground data and content inside `#FFFFFF` cards over the `#F6F6F6` background.
- **Zero-Emoji Policy**: Mandate vector icons (e.g. `lucide` / `lucide-react` / SVG) for UI actions and status indicators. Never use decorative emojis in enterprise deliverables.
- **Typographic Scale**: Slide titles `24pt - 28pt Bold`, card titles `15pt - 18pt Bold`, body text `12pt - 14pt Regular`.

> **Completion Criterion**: Layout adheres to the 16:9 grid, 2026 card structure, and typographic hierarchy.

---

### Step 3: Color Palette & Chart Styling
Apply official corporate colors strictly according to semantic meaning:
- **Hero & Primary Elements**: `#1E50E6` (Buttons, active tabs, main series).
- **Multi-Series Data Charts**: Use the 8-color corporate palette in order:
  `['#1E50E6', '#50C8FF', '#14C832', '#14C8B4', '#2378FF', '#5ADC19', '#F59E0B', '#D70A32']`
- **Semantic Indicators**: Growth/Success `#14C832` | Alert/Warning `#F59E0B` | Decline/Error `#D70A32`.

> **Completion Criterion**: Chart and UI colors match official hex values without unapproved arbitrary palettes.

---

### Step 4: Automated Brand Compliance Audit & Delivery
Verify all generated artifacts against the brand checklist or run the automated brand linter:
- Run automated audit: `python3 scripts/lint_brand.py <target_directory>`
- [ ] Font family explicitly set to `CHINTinno` with `Microsoft YaHei` second fallback.
- [ ] Primary accent matches `#1E50E6` (or gradient `#50C8FF` to `#1E50C8`).
- [ ] Contrast ratio meets WCAG 2.1 AA standards (dark text on light backgrounds).
- [ ] Clean vector logos referenced from `assets/logos/` when logo placement is required.
- [ ] Conversational delivery to user is strictly in **Chinese**, high-density, with zero raw code blocks.

> **Completion Criterion**: Artifacts pass all automated and manual verification points.

---

## Utility Tools & Scripts

- **`scripts/generate_template.py`**: Generates 2026 PPTX slide decks and HTML report skeletons (`--type [pptx|html|all] --outdir <path>`).
- **`scripts/lint_brand.py`**: Audits codebase/files for decorative emoji violations, non-brand blues, and typography fallback order.
- **`scripts/export_tokens.py`**: Exports design tokens to standalone `chint_tokens.json` and `chint_tokens.css`.
- **`scripts/chint_theme.py`**: Core Python API exposing colors, 2026 matrix, fonts, asset paths, and Matplotlib theme setups.

---

## References

- **Color Palette & 2026 Matrix**: [references/color_palette.md](references/color_palette.md)
- **Typography & Font Hierarchy**: [references/typography.md](references/typography.md)
- **PPTX 16:9 Layout & 2026 Guidelines**: [references/pptx_guidelines.md](references/pptx_guidelines.md)
- **Web Frontend & Chart Visualizations**: [references/web_and_charts.md](references/web_and_charts.md)
