# CHINT Typography & Font Hierarchy Standards

The official corporate font for CHINT is **正泰拓新体 (CHINTinno)**. It must be used consistently across presentations, UI layouts, charts, and branded publications.

---

## 1. Font Specifications & Weights

The CHINTinno font family is bundled in three standard weights:

| Weight Name | Weight Value | TTF Filename | PostScript Name | Primary Use Case |
|:---|:---|:---|:---|:---|
| **Regular** | `400` | `CHINTinno-Regular.ttf` | `CHINTinno` | Body paragraphs, table contents, UI labels, chart axis tick labels. |
| **Bold** | `700` | `CHINTinno-Bold.ttf` | `CHINTinnoBold` | Slide titles, page headers (H1/H2), hero metric numbers, button text. |
| **Light** | `300` | `CHINTinno-Light.ttf` | `CHINTinnoLight` | Large hero quote subtitles, decorative numeric backdrops, light captions. |

---

## 2. Cross-Platform Font Family Fallback Stack

Always declare the standard fallback stack to ensure consistent font rendering across macOS, Windows, Linux, and web browsers:

### Web / CSS Stack:
```css
font-family: 'CHINTinno', 'Microsoft YaHei', 'PingFang SC', '微软雅黑', sans-serif;
```

### Python (Matplotlib / Seaborn) Font Stack:
```python
plt.rcParams['font.family'] = ['CHINTinno', 'Microsoft YaHei', 'PingFang SC', 'sans-serif']
```

### Presentation (python-pptx) Font Assignment:
```python
# Primary run font
font.name = "CHINTinno"
# When CHINTinno is not installed locally on end-user machine, PowerPoint will fall back cleanly to system defaults.
```

---

## 3. Typographic Scale & Hierarchy

Use the following typographic scale to maintain visual hierarchy:

| Level | Size (Web px / rem) | Size (PPT pt) | Weight | Line Height | Application |
|:---|:---|:---|:---|:---|:---|
| **Display / Hero** | `36px` / `2.25rem` | `32pt - 36pt` | Bold (700) | `1.2` | Cover slide title, big KPI summary cards |
| **H1 (Section / Slide)**| `24px` / `1.5rem` | `24pt - 28pt` | Bold (700) | `1.3` | PPT slide main header, page top title |
| **H2 (Card / Subsection)**| `18px` / `1.125rem` | `18pt - 20pt` | Bold (700) | `1.4` | Dashboard card titles, modal headers |
| **H3 (Group / Subheader)**| `16px` / `1.0rem` | `15pt - 16pt` | Regular (400) / Bold | `1.4` | Table column headers, section subheaders |
| **Body (Main)** | `14px` / `0.875rem` | `13pt - 14pt` | Regular (400) | `1.5` | Standard paragraphs, table data cells |
| **Caption / Footnote** | `12px` / `0.75rem` | `10pt - 11pt` | Regular (400) | `1.4` | Chart legends, source notes, timestamps |

---

## 4. Web CSS `@font-face` Integration

Include `assets/styles/chint-fonts.css` or define the `@font-face` rules:

```css
@font-face {
  font-family: 'CHINTinno';
  src: local('CHINTinno'),
       local('CHINTinno-Regular'),
       local('CHINTinno Regular'),
       url('/assets/fonts/CHINTinno-Regular.ttf') format('truetype');
  font-weight: 400;
  font-style: normal;
  font-display: swap;
}

@font-face {
  font-family: 'CHINTinno';
  src: local('CHINTinno-Bold'),
       local('CHINTinno Bold'),
       url('/assets/fonts/CHINTinno-Bold.ttf') format('truetype');
  font-weight: 700;
  font-style: normal;
  font-display: swap;
}

@font-face {
  font-family: 'CHINTinno';
  src: local('CHINTinno-Light'),
       local('CHINTinno Light'),
       url('/assets/fonts/CHINTinno-Light.ttf') format('truetype');
  font-weight: 300;
  font-style: normal;
  font-display: swap;
}
```

---

## 5. Typographic Rules & Best Practices

1. **Numeric Formatting**: Use standard half-width English digits `0-9` with thousand separators (e.g., `¥12,450,000` or `1,820 台`).
2. **Title Casing & Punctuation**: Keep slide and section headings concise. Do not end headers with periods (`。`).
3. **High Contrast**: Ensure text contrast ratio exceeds WCAG 2.1 AA level (minimum 4.5:1 for body text, 3:1 for large titles).
