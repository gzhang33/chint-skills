# CHINT Legacy PPTX Transformation & Modernization Guide (2026 VI Standard)

This guide defines the standardized engineering SOP for upgrading legacy CHINT PowerPoint presentations (pre-2026 templates, non-standard aspect ratios, inconsistent typography, raster charts) into pristine, corporate-compliant **2026 VI Standard presentations** powered by `chint_pptx_engine.py`.

---

## 1. Migration Overview & Strategic Principles

When modernizing a legacy CHINT presentation:
1. **Never patch broken layouts in place**: Legacy PPTX files often contain deeply nested groups, non-standard shape IDs, font DRM locks (`FuturaBT`), and corrupted namespaces (`ns0:`). Prefer the **Extract -> Synthesize -> Clean Assemble** pipeline over manual XML in-place patching.
2. **Standardize to 16:9 Widescreen**: Transform 4:3 or legacy 16:9 layouts into standard 13.333\" x 7.5\" canvases.
3. **100% 正泰拓新体 (CHINTinno)**: Upgrade all headline and body runs to official corporate typography.
4. **Vectorize Low-Res Visuals**: Replace legacy bitmap screenshots and static SmartArt with the **10 Rich Vector Chart archetypes** or structured card grids.

---

## 2. 5-Phase Migration Execution Pipeline

```
[Legacy .pptx] ──► [Phase 1: Extraction] ──► [Phase 2: Semantic Mapping]
                                                        │
[Verified 2026 VI Deck] ◄── [Phase 4: Assembly] ◄── [Phase 3: Synthesizing]
           │
[Phase 5: Dual-Gate QA]
```

### Phase 1: Content & Data Extraction
- Extract slide titles, subheads, paragraph bullets, table rows, and raw metrics from the source file.
- Identify core numerical series, trends, and category comparisons for chart conversion.

### Phase 2: Semantic Mapping to 34 Archetypes
Map each extracted slide to its optimal 2026 VI archetype (refer to [`layout_archetypes.md`](layout_archetypes.md)):
- **Problem vs. Solution**: Map to `ARCH_07_PROBLEM_SOLUTION_SWOT`.
- **KPI Metrics & Overviews**: Map to `ARCH_04_KPI_DASHBOARD` or `ARCH_18_KPI_METRIC_GRID`.
- **Product & Industry Matrices**: Map to `ARCH_09_SOLUTION_GRID` or `ARCH_16_HEATMAP`.
- **Milestones & Roadmaps**: Map to `ARCH_06_TIMELINE_ROADMAP` or `ARCH_30_MILESTONE_LIST_BADGE`.
- **Data & Trends**: Map to the appropriate vector chart archetype (`ARCH_16_WATERFALL`, `ARCH_16_SANKEY`, `ARCH_16_COMBO`, etc.).

### Phase 3: High-Density Payload Synthesis
- Convert raw bullet points into structured JSON payloads with bold leading keywords and quantitative support.
- Ensure **Zero Default Leakage**: Proactively populate all required fields for the chosen archetype.

### Phase 4: Autonomous Clean OpenXML Assembly
Execute the engine to assemble the clean presentation:
```bash
python3 scripts/chint_pptx_engine.py payload.json output_2026_vi.pptx
```

### Phase 5: Dual-Gate Quality Verification
1. **Gate 1**: Run `python3 scripts/inspect_pptx.py output_2026_vi.pptx` to verify 100% `正泰拓新体` usage, clean edit view, and valid OpenXML schemas.
2. **Gate 2**: Run macOS PowerPoint AppleScript live opening check to ensure 0 error dialogs and smooth rendering.

---

## 3. Legacy Visual Element Upgrade Matrix

| Legacy Element | Replacement in 2026 VI Standard | Recommended Archetype |
| :--- | :--- | :--- |
| **Static 4-Box List** | 4-Column Adaptive Card Grid | `ARCH_05_MULTI_COLUMN_CARDS` |
| **Traditional Pain Points List** | Red/Blue Contrast Matrix | `ARCH_07_PROBLEM_SOLUTION_SWOT` |
| **2x2 Quad Box** | 2x2 SWOT / TOWS Strategy Matrix | `ARCH_20_SWOT_TOWS_MATRIX` |
| **Before / After Table** | Clean Diff Comparison Cards | `ARCH_21_BEFORE_AFTER_DIFF` |
| **Stepped Arrow Timeline** | Horizontal Chevron Pipeline | `ARCH_25_PROCESS_STEP_HORIZONTAL` |
| **Bitmap Profit / Cost Chart** | High-Def Vector Waterfall Chart | `ARCH_16_WATERFALL` |
| **Bitmap Energy Flow Diagram** | High-Def Vector Sankey Diagram | `ARCH_16_SANKEY` |
| **Bitmap Funnel Graphic** | High-Def Vector Conversion Funnel | `ARCH_16_FUNNEL` |
| **Static KPI Number Callout** | Semi-Circular Target Gauge | `ARCH_16_GAUGE` |
| **Multi-Line Growth Chart** | 8-Stage Stacked Area Chart | `ARCH_16_STACKED_AREA` |
