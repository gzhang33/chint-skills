# CHINT PowerPoint (PPTX) Presentation Design Guidelines

This guide specifies layout, typography, palette, and component positioning standards for dynamically generating professional, executive-ready CHINT PowerPoint presentations using `python-pptx` and the **2026 Official Master Layouts (`chint_2026_template.pptx`)**.

---

## 1. Canvas Dimensions & Grid System

All CHINT presentations MUST use the widescreen **16:9 aspect ratio**:

| Dimension Parameter | Inches | Centimeters | Points (pt) | EMUs |
|:---|:---|:---|:---|:---|
| **Slide Width** | `13.333 in` | `33.867 cm` | `960 pt` | `12,192,000` |
| **Slide Height** | `7.500 in` | `19.050 cm` | `540 pt` | `6,858,000` |

---

## 2. 2026 Master Slide Layouts & Dynamic Slide Construction

When generating presentations for business topics, **always construct slides dynamically** using the corresponding master layout indices from `chint_2026_template.pptx`:

```python
from pptx import Presentation

# 1. Load the master container
prs = Presentation(get_template_path("chint_2026_template.pptx"))

# 2. Clear template starter slides to begin with a clean slate
while len(prs.slides) > 0:
    rId = prs.slides._sldIdLst[0].rId
    prs.part.drop_rel(rId)
    del prs.slides._sldIdLst[0]

# 3. Add custom slides dynamically
slide_cover = prs.slides.add_slide(prs.slide_layouts[1])    # Layout 1: Cover
slide_toc   = prs.slides.add_slide(prs.slide_layouts[2])    # Layout 2: 5-Card Agenda
slide_break = prs.slides.add_slide(prs.slide_layouts[3])    # Layout 3: Section Divider
slide_body  = prs.slides.add_slide(prs.slide_layouts[8])    # Layout 8: 2_Title (Content)
slide_end   = prs.slides.add_slide(prs.slide_layouts[7])    # Layout 7: Closing
```

### Layout Index Mapping:
- **`slide_layouts[1]` (标题幻灯片)**: Official Cover with high-res Aurora Blue artwork background, 拓新体 Title (32pt Bold) & Subtitle (14pt).
- **`slide_layouts[2]` (目录)**: Standard Table of Contents with 5 card slots and numbered badges (`01`~`05`).
- **`slide_layouts[3]` (节标题)**: High-contrast chapter transition page.
- **`slide_layouts[8]` (2_Title / 正文与图表)**: Clean white canvas with official top title bar, logo, and wide working area (`left=0.8"`, `top=1.2"`, `width=11.7"`, `height=5.7"`).
- **`slide_layouts[7]` (末尾幻灯片)**: Official Closing Slide with artwork background and centered appreciation title.

> **Crucial Rule**: Never output internal design guideline slides (e.g. "色彩的使用") or unedited template placeholders in actual business presentation deliverables. All slides must contain real, structured domain content.

---

## 3. High-Density Card & Table Design Patterns

Organize content using high visual contrast cards and tables on top of the content slides:

### Pattern A: 3-Column Card Layout (for Features, Architecture, Modules)
- **Card 1**: `(left=0.8", top=1.3", width=3.64", height=5.4")`
- **Card 2**: `(left=4.84", top=1.3", width=3.64", height=5.4")`
- **Card 3**: `(left=8.88", top=1.3", width=3.64", height=5.4")`
- **Card Fill**: `#FFFFFF`, Border: 1pt solid `#E2E8F0`
- **Card Header**: 15pt Bold `#191919` with a 3px left accent line `#1E50E6`.

### Pattern B: 2-Column Comparison Layout (for Strategy vs Execution, Old vs New)
- **Left Column**: `(left=0.8", top=1.3", width=5.65", height=5.4")`
- **Right Column**: `(left=6.88", top=1.3", width=5.65", height=5.4")`

### Pattern C: Technical Specification / Comparison Table
- **Table Position**: `(left=0.8", top=1.4", width=11.73", height=5.2")`
- **Header Row**: Fill `#1E50E6`, Text `#FFFFFF` Bold 13pt `正泰拓新体`.
- **Alternating Rows**: `#FFFFFF` / `#F8FAFC`, Text `#333333` 12pt.
- **Grid Borders**: `#E2E8F0`.

### Pattern D: 4-Metric KPI Summary Card
- **4 Cards Grid**: `width=2.70"`, `gap=0.3"`, `height=2.2"`
- **Big Number**: 32pt Bold `#1E50E6` (or `#14C832` for growth, `#D70A32` for alerts).
- **Metric Label**: 13pt Regular `#666666`.
- **Badge Pill**: 11pt Bold `#14C832` with `#DCFCE7` background.

---

## 4. Typography Hierarchy

- **Presentation Title**: `正泰拓新体` / `CHINTinno` 32pt - 36pt Bold `#FFFFFF` (Cover)
- **Slide Header**: `正泰拓新体` 22pt - 24pt Bold `#191919`
- **Card Title / Section Subhead**: `正泰拓新体` 15pt - 16pt Bold `#191919`
- **Body & Paragraphs**: `正泰拓新体` 12pt - 14pt Regular `#333333` (line spacing 1.3)
- **Table Header & Captions**: `正泰拓新体` 12pt - 13pt Bold `#FFFFFF` / `#666666`
