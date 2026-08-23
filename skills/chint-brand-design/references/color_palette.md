# CHINT Brand Color Palette & Theme Tokens

This document specifies the authoritative color standards for all CHINT branded artifacts, presentations, web interfaces, and data visualizations, fully aligned with the **2026 CHINT Corporate Visual Identity Standards**.

---

## 1. Primary Brand Colors

| Color Token | Hex Code | RGB | Semantic Meaning & Application |
|:---|:---|:---|:---|
| `--chint-primary` | `#1E50E6` | `(30, 80, 230)` | **CHINT Electric Blue** — Primary buttons, active tabs, header icons, key chart series. |
| `--chint-primary-hover` | `#1E62DE` | `(30, 98, 222)` | Interactive hover state for primary elements. |
| `--chint-primary-dark` | `#1E50C8` | `(30, 80, 200)` | Deep blue banner gradient end, pressed states, card active borders. |
| `--chint-primary-light` | `#50C8FF` | `(80, 200, 255)` | Electric Cyan — Banner gradient start, glowing accents, badge highlights. |
| `--chint-primary-classic` | `#0070C0` | `(0, 112, 192)` | Classic CHINT corporate industrial blue. |

### Banner & Header Gradient
```css
--chint-gradient-banner: linear-gradient(90deg, #50C8FF 0%, #1E50C8 100%);
```
- **Usage**: Presentation cover slide banners, top app navigation bars, header accent stripes (height: 4px–6px).

---

## 2. 2026 Official Presentation Color Specification Matrix

As defined in the official 2026 CHINT Corporate Master (`26年模板拓新体(1).pptx` Slide 5):

### 2.1 主色系（7 阶主蓝）
| 阶梯 | 描述 | Hex Code | RGB |
|:---|:---|:---|:---|
| 阶 1 | 深邃蓝 | `#1437AA` | `(20, 55, 170)` |
| 阶 2 | 极光蓝（主品牌色） | `#1E50E6` | `(30, 80, 230)` |
| 阶 3 | 明亮蓝 | `#2378FF` | `(35, 120, 255)` |
| 阶 4 | 天空蓝 | `#3CA0FF` | `(60, 160, 255)` |
| 阶 5 | 极光青蓝 | `#50C8FF` | `(80, 200, 255)` |
| 阶 6 | 淡青蓝 | `#A0E6FF` | `(160, 230, 255)` |
| 阶 7 | 冰蓝底色 | `#D7F0FF` | `(215, 240, 255)` |

### 2.2 辅助色系 1：绿色能源（4 阶绿能）
| 阶梯 | 描述 | Hex Code | RGB |
|:---|:---|:---|:---|
| 阶 1 | 绿能深绿 | `#14C832` | `(20, 200, 50)` |
| 阶 2 | 绿能草绿 | `#5ADC19` | `(90, 220, 25)` |
| 阶 3 | 绿能鲜绿 | `#A0F000` | `(160, 240, 0)` |
| 阶 4 | 绿能浅绿 | `#DCFF8C` | `(220, 255, 140)` |

### 2.3 辅助色系 2：智慧低碳（4 阶青绿）
| 阶梯 | 描述 | Hex Code | RGB |
|:---|:---|:---|:---|
| 阶 1 | 低碳青绿 | `#14C8B4` | `(20, 200, 180)` |
| 阶 2 | 低碳明青 | `#2DEEC8` | `(45, 238, 200)` |
| 阶 3 | 低碳水绿 | `#73FFD2` | `(115, 255, 210)` |
| 阶 4 | 低碳淡青 | `#C8FFDC` | `(200, 255, 220)` |

### 2.4 辅助色系 3：中性灰（4 阶）
| 阶梯 | 描述 | Hex Code | RGB |
|:---|:---|:---|:---|
| 阶 1 | 中性深灰 | `#5A5A5A` | `(90, 90, 90)` |
| 阶 2 | 中性中灰 | `#828282` | `(130, 130, 130)` |
| 阶 3 | 中性浅灰 | `#D2D2D2` | `(210, 210, 210)` |
| 阶 4 | 中性背景灰 | `#F0F0F0` | `(240, 240, 240)` |

### 2.5 警示与强调红
| 描述 | Hex Code | RGB | 用途 |
|:---|:---|:---|:---|
| 警示强调红 | `#D70A32` | `(215, 10, 50)` | 关键警示批注、下滑预警、核心强调指标 |

---

## 3. Neutrals & Surface Colors (Light Mode First)

All CHINT digital applications and documentation default to a clean, crisp Light Mode.

| Token Name | Hex Code | RGB | Purpose & Application |
|:---|:---|:---|:---|
| `--chint-background` | `#F6F6F6` | `(246, 246, 246)` | Main window / body background, canvas fill. |
| `--chint-surface` | `#FFFFFF` | `(255, 255, 255)` | Content cards, data tables, modals, input containers. |
| `--chint-bg-subtle` | `#F3F6FE` | `(243, 246, 254)` | Table alternating rows, hover background, callout containers. |
| `--chint-border` | `#E2E8F0` | `(226, 232, 240)` | Card borders, grid lines, dividers. |
| `--chint-border-light`| `#CBD5E1` | `(203, 213, 225)` | Form input borders, active focus indicators. |

---

## 4. Typography Neutrals & Text Hierarchy

| Token Name | Hex Code | Purpose |
|:---|:---|:---|
| `--chint-text-dark` | `#191919` | Top-level slide titles, primary page headings (H1/H2), key metric numbers. |
| `--chint-text-soft` | `#333333` | Standard body paragraphs, table cell data, bullet points. |
| `--chint-text-muted`| `#666666` | Secondary annotations, captions, footnotes, column metadata. |
| `--chint-text-faint`| `#94A3B8` | Input placeholder text, disabled actions, timestamp stamps. |

---

## 5. Semantic Status Colors

| State | Hex Code | RGB | Badge Background | Use Case |
|:---|:---|:---|:---|:---|
| **Success** | `#14C832` | `(20, 200, 50)` | `#DCFCE7` | YoY positive growth, target achieved, online status. |
| **Warning** | `#F59E0B` | `(245, 158, 11)` | `#FEF3C7` | Replacement transition, risk alert, pending review. |
| **Error / Alert**| `#D70A32` | `(215, 10, 50)` | `#FEE2E2` | YoY decline, critical failure, unmapped model error. |
| **Info** | `#1E50E6` | `(30, 80, 230)` | `#E0F2FE` | Informational callouts, notice banners. |

---

## 6. Multi-Series Data Visualization Palette

When plotting charts with multiple product series (e.g. NXA vs NA1 vs NA8, ACB vs MCCB):

1. **Series 1 (Core / Hero)**: `#1E50E6` (CHINT Electric Blue)
2. **Series 2 (Growth / Focus)**: `#50C8FF` (Electric Cyan)
3. **Series 3 (Green Energy)**: `#14C832` (Energy Green)
4. **Series 4 (Low-Carbon)**: `#14C8B4` (Smart Cyan)
5. **Series 5 (Bright Blue)**: `#2378FF` (Bright Blue)
6. **Series 6 (Grass Green)**: `#5ADC19` (Grass Green)
7. **Series 7 (Amber Accent)**: `#F59E0B` (Amber Orange)
8. **Series 8 (Alert Red)**: `#D70A32` (Accent Red)

---

## 7. Prohibited Anti-Patterns

- **No Random Rainbow Palettes**: Never use saturated random rainbow colors in business reports.
- **No Unreadable Low-Contrast Combinations**: Avoid yellow text on white backgrounds or dark blue text on black backgrounds.
- **No Clashing Gradients**: Only use the official `#50C8FF` to `#1E50C8` gradient. Do not mix purple-to-yellow or red-to-green gradients.
