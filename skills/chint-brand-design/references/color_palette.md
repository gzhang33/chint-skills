# CHINT Brand Color Palette & Theme Tokens

This document specifies the authoritative color standards for all CHINT branded artifacts, presentations, web interfaces, and data visualizations.

---

## 1. Primary Brand Colors

| Color Token | Hex Code | RGB | HSL | Semantic Meaning & Application |
|:---|:---|:---|:---|:---|
| `--chint-primary` | `#1E50E6` | `(30, 80, 230)` | `(225°, 82%, 51%)` | **CHINT Electric Blue** — Primary buttons, active tabs, header icons, key chart series. |
| `--chint-primary-hover` | `#1E62DE` | `(30, 98, 222)` | `(219°, 76%, 49%)` | Interactive hover state for primary elements. |
| `--chint-primary-dark` | `#1E50C8` | `(30, 80, 200)` | `(222°, 74%, 45%)` | Deep blue banner gradient end, pressed states, card active borders. |
| `--chint-primary-light` | `#50C8FF` | `(80, 200, 255)` | `(199°, 100%, 66%)` | Electric Cyan — Banner gradient start, glowing accents, badge highlights. |
| `--chint-primary-classic` | `#0070C0` | `(0, 112, 192)` | `(205°, 100%, 38%)` | Classic CHINT corporate industrial blue. |

### Banner & Header Gradient
```css
--chint-gradient-banner: linear-gradient(90deg, #50C8FF 0%, #1E50C8 100%);
```
- **Usage**: Presentation cover slide banners, top app navigation bars, header accent stripes (height: 4px–6px).

---

## 2. Neutrals & Surface Colors (Light Mode First)

All CHINT digital applications and documentation default to a clean, crisp Light Mode.

| Token Name | Hex Code | RGB | Purpose & Application |
|:---|:---|:---|:---|
| `--chint-background` | `#F6F6F6` | `(246, 246, 246)` | Main window / body background, canvas fill. |
| `--chint-surface` | `#FFFFFF` | `(255, 255, 255)` | Content cards, data tables, modals, input containers. |
| `--chint-bg-subtle` | `#F3F6FE` | `(243, 246, 254)` | Table alternating rows, hover background, callout containers. |
| `--chint-border` | `#E2E8F0` | `(226, 232, 240)` | Card borders, grid lines, dividers. |
| `--chint-border-light`| `#CBD5E1` | `(203, 213, 225)` | Form input borders, active focus indicators. |

---

## 3. Typography Neutrals & Text Hierarchy

| Token Name | Hex Code | Purpose |
|:---|:---|:---|
| `--chint-text-dark` | `#191919` | Top-level slide titles, primary page headings (H1/H2), key metric numbers. |
| `--chint-text-soft` | `#333333` | Standard body paragraphs, table cell data, bullet points. |
| `--chint-text-muted`| `#666666` | Secondary annotations, captions, footnotes, column metadata. |
| `--chint-text-faint`| `#94A3B8` | Input placeholder text, disabled actions, timestamp stamps. |

---

## 4. Semantic Status Colors

| State | Hex Code | RGB | Badge Background | Use Case |
|:---|:---|:---|:---|:---|
| **Success** | `#16A34A` | `(22, 163, 74)` | `#DCFCE7` | YoY positive growth, target achieved, online status. |
| **Warning** | `#D97706` | `(217, 119, 6)` | `#FEF3C7` | Replacement transition, risk alert, pending review. |
| **Error / Alert**| `#DC2626` | `(220, 38, 38)` | `#FEE2E2` | YoY decline, critical failure, unmapped model error. |
| **Info** | `#0284C7` | `(2, 132, 199)` | `#E0F2FE` | Informational callouts, notice banners. |

---

## 5. Multi-Series Data Visualization Palette

When plotting charts with multiple product series (e.g. NXA vs NA1 vs NA8, ACB vs MCCB):

1. **Series 1 (Core / Hero)**: `#1E50E6` (CHINT Electric Blue)
2. **Series 2 (Growth / Focus)**: `#50C8FF` (Electric Cyan)
3. **Series 3 (Secondary)**: `#1E50C8` (Deep Blue)
4. **Series 4 (Classic / Baseline)**: `#0070C0` (Corporate Blue)
5. **Series 5 (Accent Amber)**: `#F59E0B` (Amber Orange)
6. **Series 6 (Accent Green)**: `#10B981` (Emerald Green)
7. **Series 7 (Accent Indigo)**: `#6366F1` (Indigo Purple)
8. **Series 8 (Accent Pink)**: `#EC4899` (Magenta Rose)

---

## 6. Prohibited Anti-Patterns

- ❌ **No Random Rainbow Palettes**: Never use saturated random rainbow colors in business reports.
- ❌ **No Unreadable Low-Contrast Combinations**: Avoid yellow text on white backgrounds or dark blue text on black backgrounds.
- ❌ **No Clashing Gradients**: Only use the official `#50C8FF` to `#1E50C8` gradient. Do not mix purple-to-yellow or red-to-green gradients.
