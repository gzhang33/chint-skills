# CHINT PowerPoint (PPTX) Presentation Design Guidelines

This guide specifies layout, typography, palette, and component positioning standards for creating professional CHINT PowerPoint presentations using `python-pptx`, the **2026 Official Master Template (`chint_2026_template.pptx`)**, or manual authoring.

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

## 2. 2026 Official Master Layouts (`chint_2026_template.pptx`)

The bundled 2026 official presentation template contains the following standard layout slides:

1. **Cover Slide (标题幻灯片)**:
   - High-resolution Aurora Blue corporate brand artwork.
   - Title Placeholder: `(left=3.95", top=5.06", width=8.72", height=0.67")`, Font: `正泰拓新体` / `CHINTinno`, Size: `28pt - 36pt` Bold `#FFFFFF`.
   - Subtitle Placeholder: `(left=3.95", top=5.96", width=6.63", height=0.35")`, Font: `正泰拓新体`, Size: `14pt` `#D7F0FF`.

2. **Table of Contents (目录页)**:
   - 5 structured rounded rectangle cards `(left=5.02", top=1.30" ~ 5.26", width=6.56", height=0.76")`.
   - Number Badge (`01`, `02`, `03`, `04`, `05`) in Electric Blue `#1E50E6`.
   - Section Title Box with forward-indicator chevrons.

3. **Section Divider (节标题页)**:
   - Centered aurora graphic background with high-contrast chapter title placeholder `(left=3.18", top=2.86", width=6.98", height=0.84")`.

4. **Standard Content Slide (标题和副标题正文页)**:
   - Top Header Title Placeholder `(left=0.54", top=0.21", width=12.21", height=0.79")`.
   - Subtitle / Content Placeholder `(left=0.54", top=1.42", width=12.21", height=0.44")`.
   - Usable body working area: Width `12.2 in`, Height `5.2 in`.

5. **Color Matrix Specification Slide (色彩规范页)**:
   - Comprehensive reference of the 7-step Primary Blue, 4-step Green Energy, 4-step Smart Cyan, 4-step Neutral Gray, and Warning Red.

6. **Ending Slide (末尾幻灯片)**:
   - Official closing artwork with centered `感谢观看` / `Empower the World` brand title.

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
- **Metric Value (Big Number)**: Font size `32pt - 40pt`, Bold, Color `#1E50E6` (or `#14C832` for positive growth, `#D70A32` for negative).
- **Metric Label**: Font size `13pt - 14pt`, Regular, Color `#666666`.
- **YoY Tag**: Font size `12pt`, Bold, with colored background pill (e.g. green pill `#DCFCE7` with `#14C832` text).

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
