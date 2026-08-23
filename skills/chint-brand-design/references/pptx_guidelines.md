# CHINT PowerPoint (PPTX) Presentation Design Guidelines

This guide specifies layout, typography, palette, and component positioning standards for creating professional CHINT PowerPoint presentations using `python-pptx` or manual authoring.

---

## 1. Canvas Dimensions & Grid System

All CHINT presentations MUST use the widescreen **16:9 aspect ratio**:

| Dimension Parameter | Inches | Centimeters | Points (pt) | EMUs |
|:---|:---|:---|:---|:---|
| **Slide Width** | `13.333 in` | `33.867 cm` | `960 pt` | `12,192,000` |
| **Slide Height** | `7.500 in` | `19.050 cm` | `540 pt` | `6,858,000` |

### python-pptx Initialization:
```python
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
```

---

## 2. Standard Layout Master & Margins

### Top Navigation / Title Banner:
- **Banner Height**: `0.90 in` to `1.00 in`
- **Banner Background**: Gradient `#50C8FF` -> `#1E50C8` or Solid Electric Blue `#1E50E6` (with white text `#FFFFFF`), OR clean white header on `#F6F6F6` background (with `#191919` text and `#1E50E6` left accent bar).
- **CHINT Logo Placement**: Top-left `(left=0.8", top=0.3", height=0.4")` or top-right.
- **Slide Title**: Left `0.8 in`, Top `0.25 in`, Font size `24pt`, Bold, Font `CHINTinno`.

### Content Working Area:
- **Left Margin**: `0.80 in`
- **Right Margin**: `0.80 in`
- **Top Margin (below banner)**: `1.25 in`
- **Bottom Margin**: `0.60 in`
- **Usable Content Width**: `11.733 in`
- **Usable Content Height**: `5.65 in`

---

## 3. Card-Based Layout Patterns

Presentations should organize information into clean white surface cards over the light gray canvas background (`#F6F6F6`):

```
+-------------------------------------------------------------------+
|  [CHINT LOGO]   Slide Title (CHINTinno 24pt Bold)                 | Top Banner (0.95")
+-------------------------------------------------------------------+
|                                                                   |
|   +-----------------------+   +-------------------------------+   |
|   | Card 1: Metric KPI    |   | Card 2: Chart / Breakdown     |   | Content Area
|   | Background: #FFFFFF   |   | Background: #FFFFFF           |   | (Left 0.8", Right 0.8")
|   | Border: #E2E8F0       |   | Border: #E2E8F0               |   |
|   |                       |   |                               |   |
|   +-----------------------+   +-------------------------------+   |
|                                                                   |
+-------------------------------------------------------------------+
| CHINT Electric Power Distribution | Confidential         Page 03  | Footer (0.4")
+-------------------------------------------------------------------+
```

---

## 4. Standard Component Specifications

### 1. KPI Metric Cards
- **Card Background**: `#FFFFFF`, Border `#E2E8F0` (width 1pt), Corner radius subtle.
- **Metric Value (Big Number)**: Font size `32pt - 40pt`, Bold, Color `#1E50E6` (or `#16A34A` for positive growth, `#DC2626` for negative).
- **Metric Label**: Font size `13pt - 14pt`, Regular, Color `#666666`.
- **YoY Tag**: Font size `12pt`, Bold, with colored background pill (e.g. green pill `#DCFCE7` with `#16A34A` text).

### 2. Structured Data Tables
- **Header Row**: Background `#1E50E6` (text `#FFFFFF` Bold 13pt) OR `#F3F6FE` (text `#191919` Bold 13pt).
- **Data Rows**: Text `#333333` Regular 12pt, vertical alignment centered.
- **Alternating Rows**: Even rows `#FFFFFF`, Odd rows `#F9FBFF`.
- **Grid Lines**: Border `#E2E8F0` (0.5pt).

### 3. Bullet Points & Paragraphs
- **Font**: `CHINTinno` Regular 13pt - 14pt.
- **Color**: `#333333`.
- **Line Spacing**: `1.3 - 1.4`.
- **Bullet Style**: Clean square or circular bullets in brand blue `#1E50E6`.

---

## 5. End-to-End `python-pptx` Code Blueprint

```python
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

# 1. Initialize 16:9 Presentation
prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
blank_slide_layout = prs.slide_layouts[6]
slide = prs.slides.add_slide(blank_slide_layout)

# 2. Add Background Canvas
bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
bg.fill.solid()
bg.fill.fore_color.rgb = RGBColor(246, 246, 246)  # #F6F6F6
bg.line.color.rgb = RGBColor(246, 246, 246)

# 3. Add Top Header Bar
header = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(0.95))
header.fill.solid()
header.fill.fore_color.rgb = RGBColor(30, 80, 230)  # #1E50E6
header.line.color.rgb = RGBColor(30, 80, 230)

# 4. Add Title Text
title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.2), Inches(10.0), Inches(0.6))
tf = title_box.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "CHINT Power Distribution Sales Overview"
p.font.name = "CHINTinno"
p.font.size = Pt(24)
p.font.bold = True
p.font.color.rgb = RGBColor(255, 255, 255)

# 5. Add White Content Card
card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.3), Inches(5.6), Inches(5.4))
card.fill.solid()
card.fill.fore_color.rgb = RGBColor(255, 255, 255)
card.line.color.rgb = RGBColor(226, 232, 240)  # #E2E8F0
```
