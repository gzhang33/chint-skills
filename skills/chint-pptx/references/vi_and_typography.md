# CHINT 2026 Visual System and Typography

Use this file as rationale and role guidance. Keep all executable brand colors and the font family in `spec/brand_tokens.json`; do not duplicate their values here.

## Theme roles

| Token | Use |
|---|---|
| `theme.blue` | Main brand emphasis, core data, and actions |
| `theme.cyan` | Secondary accents, flow markers, and highlights |
| `theme.navy` | Body-slide and contents titles |
| `theme.ice` | Text on dark brand backgrounds |
| `theme.white` | Text or surfaces on dark backgrounds |
| `theme.muted` | Supporting text, captions, and footer details |
| `theme.light_bg` | Subtle card and table surfaces |
| `theme.card_border` | Neutral card and table borders |
| `theme.font` | 正泰拓新体 / CHINTinno editable text |

Use the existing brand color hierarchy consistently. Change token values only in the JSON source after the brand owner approves the change.

## Editable text and charts

Use 正泰拓新体 for editable slide text, including the Latin, East Asian, and complex-script font records. The receiver must have the bundled CHINTinno font installed. Font embedding is off by default.

Use native PowerPoint charts for supported data comparisons and trends. Use native shapes for processes, matrices, and other diagrams that users should edit. Use a raster graphic for complex visualizations only when a native editable version is not reasonably available; retain the chart data as inspectable source information.

## Layout hierarchy

- **Cover:** one product or presentation title, an optional source-backed subtitle, and the included CHINT cover artwork.
- **Chapter divider:** one section title; retain the cleaned artwork from `assets/media/chapter_26_bg_clean.jpg`.
- **Body:** one clear headline, supporting evidence, and an editable visual that matches the content.
- **Closing:** keep the template's existing THANKS artwork and mark. Add contact details only when supplied by the user.

Keep regular body copy left aligned, use clear hierarchy, and preserve enough margin for long Chinese or English labels. Judge text fit from PowerPoint and WPS output with the required font installed.

## Multi-series palette

The creation engine's `CHART_PALETTE` defines series order. The first two series use `theme.blue` and `theme.cyan`; semantic warning and status colors are independent meanings, not replacement brand tokens. Do not infer a value's positive or negative meaning from its label color.
