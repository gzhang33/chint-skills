# CHINT PowerPoint (PPTX) Presentation Design Guidelines

This guide establishes the authoritative design principles and modular layout patterns for authoring professional, executive-ready CHINT presentations.

---

## 1. Design Philosophy: Brand Consistency with Content-Driven Freedom

- **Format & Brand Consistency**: Every presentation strictly preserves the official visual identity (16:9 widescreen canvas, CHINTinno typography, 2026 Electric Blue color matrix, clean light surfaces, and zero-emoji compliance).
- **Style & Layout Freedom**: There is **no rigid template restriction**. The number of slides, visual structures (cards, tables, timelines, architectures, metric grids), and narrative depth are dynamically tailored to the specific business objective.

---

## 2. Brand Non-Negotiables (Core Standards)

| Dimension | Standard Specification | Python / Design Parameter |
|:---|:---|:---|
| **Canvas Ratio** | 16:9 Widescreen | Width: `13.333 in` (960pt), Height: `7.500 in` (540pt) |
| **Typography** | `正泰拓新体` / `CHINTinno` | Fallback: `Microsoft YaHei` -> `PingFang SC` |
| **Canvas Tone** | Light Mode First | Background: `#F6F6F6` (Light Gray), Cards: `#FFFFFF` (White) |
| **Borders & Dividers** | 1px Clean Border | Border: `#E2E8F0` (RGB: 226, 232, 240) |
| **Primary Brand Blue** | CHINT Electric Blue | `#1E50E6` (RGB: 30, 80, 230) |
| **Banner Gradient** | Electric Cyan to Deep Blue | `linear-gradient(90deg, #50C8FF 0%, #1E50C8 100%)` |
| **Zero-Emoji Policy** | Strict Vector Iconography | Prohibit decorative emojis in UI/headers/cards |

---

## 3. Typographic Hierarchy

- **Deck Title (Cover)**: 32pt – 36pt Bold `#FFFFFF` (on dark/gradient cover) or `#191919` (on light cover)
- **Slide Header**: 22pt – 24pt Bold `#191919` (Top margin `0.3"`, Left `0.8"`)
- **Slide Subheader / Category Tag**: 12pt – 13pt Regular `#666666` or `#1E50E6`
- **Card Title / Section Header**: 15pt – 18pt Bold `#191919`
- **Body & Bullet Points**: 12pt – 14pt Regular `#333333` (Line spacing `1.3 - 1.4`)
- **Metric Big Numbers**: 28pt – 40pt Bold `#1E50E6` (or `#14C832` for positive, `#D70A32` for alert)
- **Footnotes & Captions**: 10pt – 11pt Regular `#94A3B8`

---

## 4. Modular Layout Patterns (Composable Building Blocks)

Combine these modular patterns freely based on your business narrative:

### Pattern A: Multi-Column Card Grid (2, 3, or 4 Columns)
Organize complex concepts, modules, or features into crisp white cards over the `#F6F6F6` canvas:
- **3-Column Width**: `width = 3.64"`, `height = 5.20"`, `lefts = [0.80", 4.84", 8.88"]`, `top = 1.40"`
- **2-Column Width**: `width = 5.65"`, `height = 5.20"`, `lefts = [0.80", 6.88"]`, `top = 1.40"`
- **Card Style**: Fill `#FFFFFF`, Border 1pt `#E2E8F0`, with a 3px vertical accent line (`#1E50E6` or `#14C8B4`) next to the card title.

### Pattern B: Structured Comparison & Parameter Table
For product spec comparisons, competitive teardowns, or pricing matrix:
- **Table Bounds**: `(left=0.80", top=1.45", width=11.73", height=5.20")`
- **Header Row**: Fill `#1E50E6`, Text `#FFFFFF` Bold 13pt `正泰拓新体`, center-aligned.
- **Alternating Rows**: `#FFFFFF` and `#F8FAFC`, Text `#333333` 11.5pt–12pt.
- **Row Borders**: Subtle `#E2E8F0` dividers.

### Pattern C: KPI Executive Metric Dashboard
For executive summaries, financial metrics, and operational performance:
- **4-Tile Row**: `(width=2.70", height=2.20", gap=0.30")`
- **Top Row KPI Tiles + Bottom Row Chart/Table**: High-density executive layout.
- **Big Stat Number**: 32pt–36pt Bold `#1E50E6`.
- **Growth Badge**: 11pt Bold `#14C832` inside a light green pill (`#DCFCE7`).

### Pattern D: Horizontal Timeline & Strategic Roadmap
For project phases, historical milestones, or migration paths:
- **Horizontal Progress Line**: Height 2px `#CBD5E1` connecting milestone cards.
- **Milestone Nodes**: Numbered circles (`01`, `02`, `03`, `04`) with `#1E50E6` active state.
- **Phase Cards**: Placed below each node with stage objectives and deliverables.

### Pattern E: Process Flow & System Architecture
For operational workflows, technical mechanisms, or value chains:
- **Step Boxes**: Horizontal interconnected cards with forward arrow indicators.
- **Key Inputs -> Core Mechanism -> Value Outputs**.

---

## 5. Clean, Zero-Template Python Code Blueprint

Create presentations dynamically from a blank canvas using `python-pptx` and brand tokens without relying on fixed template files:

```python
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

# 1. Initialize 16:9 Canvas
prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.500)
blank_layout = prs.slide_layouts[6]

# 2. Add Standard Content Slide with Brand Header
slide = prs.slides.add_slide(blank_layout)

# Base Canvas Fill
bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.500))
bg.fill.solid()
bg.fill.fore_color.rgb = RGBColor(246, 246, 246)  # #F6F6F6
bg.line.color.rgb = RGBColor(246, 246, 246)

# Top Brand Stripe (4px accent)
stripe = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(0.06))
stripe.fill.solid()
stripe.fill.fore_color.rgb = RGBColor(30, 80, 230)  # #1E50E6
stripe.line.color.rgb = RGBColor(30, 80, 230)

# Slide Header Box
title_box = slide.shapes.add_textbox(Inches(0.80), Inches(0.35), Inches(11.73), Inches(0.80))
tf = title_box.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "01 / 业务分析与战略全景"
p.font.name = "正泰拓新体"
p.font.size = Pt(22)
p.font.bold = True
p.font.color.rgb = RGBColor(25, 25, 25)

# 3. Add Freeform Business Cards (e.g. 3-column layout)
for idx, left_pos in enumerate([0.80, 4.84, 8.88]):
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left_pos), Inches(1.40), Inches(3.64), Inches(5.40))
    card.fill.solid()
    card.fill.fore_color.rgb = RGBColor(255, 255, 255)
    card.line.color.rgb = RGBColor(226, 232, 240)
```
