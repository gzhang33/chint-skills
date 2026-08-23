---
name: chint-brand-design
description: Design CHINT brand deliverables under official 2026 VI standards. Use when creating or styling CHINT presentations (PPTX), web interfaces (CSS), charts (Matplotlib, ECharts), reports, or when applying CHINTinno font, Electric Blue (#1E50E6), or brand color tokens.
---

# CHINT Brand Identity & Visual Design Skill

Authoritative brand identity governance, design system tokens, and modular layout guidelines for all CHINT digital deliverables, presentations (PPTX), web interfaces, data visualizations, and reporting materials, strictly aligned with the **2026 CHINT Corporate Visual Identity Standards**.

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

> All bundled font files, vector logos, CSS styles, and Python helpers reside in `assets/` and `scripts/`.

---

## 4-Step Standard Execution Workflow

### Step 1: Scenario Identification & Brand Token Loading
Identify the target deliverable medium and load the corresponding brand tokens:
1. **PowerPoint Presentations (`.pptx`)**:
   - Initialize 16:9 canvas (`13.333" x 7.500"`) using `python-pptx` and import official brand tokens from `scripts/chint_theme.py` (`CHINT_COLORS`, `CHINT_FONTS`).
   - Consult [pptx_guidelines.md](references/pptx_guidelines.md) to choose modular layout patterns (multi-column cards, comparison tables, KPI dashboards, timelines, or process flows) tailored to the specific business narrative.
2. **Web / HTML / CSS**:
   - Link `assets/styles/chint-fonts.css` and use `--font-chint: 'CHINTinno', 'Microsoft YaHei', 'PingFang SC', '微软雅黑', sans-serif;`.
   - Consult [web_and_charts.md](references/web_and_charts.md) for shared CSS custom properties and UI density patterns.
3. **Data Visualizations (Matplotlib / Seaborn / ECharts)**:
   - Call `apply_matplotlib_theme()` or load `get_chart_palette()`. Consult [web_and_charts.md](references/web_and_charts.md).
4. **Markdown / HTML / PDF Reports**:
   - Structure with crisp light mode cards, standard typography, and clean vector status indicators.

> **Completion Criterion**: Target medium is identified and official brand tokens (`CHINT_COLORS`, `CHINT_FONTS`) or CSS variables are imported and verified.

---

### Step 2: Visual Structure & Modular Layout Composition
Apply composable modular layout patterns according to content density:
- **Presentation Canvas (16:9)**: Set width `13.333 in` (960pt) and height `7.5 in` (540pt).
- **Surface Hierarchy**: Place foreground data and content inside `#FFFFFF` cards over the `#F6F6F6` background.
- **Zero-Emoji Policy**: Mandate vector iconography (e.g. `lucide` / `lucide-react` / SVG) for all UI actions, badges, and status indicators. Never use non-professional decorative emojis in enterprise deliverables.
- **Typographic Scale**: Slide titles `22pt - 24pt Bold`, card titles `15pt - 18pt Bold`, body text `12pt - 14pt Regular`. Consult [typography.md](references/typography.md).

> **Completion Criterion**: Layout strictly adheres to 16:9 widescreen dimensions, white card surface hierarchy, typographic scale, and zero-emoji compliance.

---

### Step 3: Color Palette & Chart Styling
Apply official corporate colors strictly according to semantic meaning:
- **Hero & Primary Elements**: `#1E50E6` (Buttons, active tabs, main series).
- **Multi-Series Data Charts**: Use the 8-color corporate palette in order:
  `['#1E50E6', '#50C8FF', '#14C832', '#14C8B4', '#2378FF', '#5ADC19', '#F59E0B', '#D70A32']`
- **Semantic Indicators**: Growth/Success `#14C832` | Alert/Warning `#F59E0B` | Decline/Error `#D70A32` | Info `#1E50E6`.
- Consult [color_palette.md](references/color_palette.md) for the complete 2026 multi-series step matrix.

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

> **Completion Criterion**: `python3 scripts/lint_brand.py .` executes with 0 violations and user-facing delivery is strictly in Chinese with zero raw code blocks.

---

## Utility Tools & Scripts

- **`scripts/lint_brand.py`**: Audits codebase/files for decorative emoji violations, non-brand blues, and typography fallback order.
- **`scripts/export_tokens.py`**: Exports design tokens and 2026 matrix to standalone `chint_tokens.json` and `chint_tokens.css`.
- **`scripts/chint_theme.py`**: Core Python API exposing colors, 2026 matrix, fonts, asset paths, and Matplotlib theme setups.

---

## Progressive Disclosure References

- **[references/color_palette.md](references/color_palette.md)**: Consult when needing exact hex/RGB values for the 2026 7-step Blue, 4-step Green Energy, 4-step Smart Cyan, 4-step Neutral Gray, and semantic status badges.
- **[references/typography.md](references/typography.md)**: Consult when configuring font faces, typographic hierarchies, or cross-platform font fallbacks.
- **[references/pptx_guidelines.md](references/pptx_guidelines.md)**: Consult when authoring PowerPoint presentations for modular card grids, parameter tables, KPI dashboards, timelines, and process flows.
- **[references/web_and_charts.md](references/web_and_charts.md)**: Consult when building Web frontends, CSS custom properties, ECharts JSON themes, or Matplotlib figures.
