---
name: chint-pptx
description: Author enterprise CHINT PowerPoint (PPTX) decks with 2026 VI guidelines, CHINTinno (正泰拓新体) typography, clean OpenXML architecture, and adaptive 34-layout archetype selection. Use when creating CHINT presentations, pitch decks, business reviews, technical solution slides, or translating user requirements into tailored slides with the grill-me alignment SOP.
---

# CHINT Enterprise PPTX Generation Skill (`chint-pptx`)

Generate professional, corporate-compliant CHINT PowerPoint presentations tailored for Low-Voltage Electrical Apparatus (低压电器) Product Managers, enforcing the **2026 VI Design Standard**, **正泰拓新体 (CHINTinno)** typography, 16:9 widescreen grids (13.333" x 7.5"), clean OpenXML assembly, and an **adaptive layout selection engine** supporting all **34 slide layout archetypes**.

---

## Operational SOP Workflow

```
[Phase 1: Alignment] ──► [Phase 2: Adaptive Multi-Scenario Selection] ──► [Phase 3: Synthesizing]
                                                                                   │
[Phase 5: Dual-Gate Automated QA] ◄── [Phase 4: Clean OpenXML Engine] ◄────────────┘
```

### Phase 1: Grill-Me Requirement Alignment (`ask_question`)
Align with the Product Manager using the interactive `ask_question` modal (refer to [`references/grill_me_alignment_sop.md`](references/grill_me_alignment_sop.md)):
1. **Audience & Goal**: Establish whether the deck is for executive review, client sales pitch, strategy alignment, or technical solution release.
2. **Dynamic Pacing**: Match slide count to input content density (5–8p Concise, 10–14p Standard, 15–20p Deep-dive).
3. **Visual Theme**: Apply official CHINT 2026 VI Electric Blue (`#1E50E6`) palette.
- **Completion Criterion**: Target audience, slide count tier, and narrative arc confirmed by user.

### Phase 2: Dynamic Multi-Scenario Adaptive Layout Selection
The Agent MUST dynamically evaluate the semantic intent and information structure of each slide topic to select the most appropriate layout archetype among all 34 supported archetypes (refer to [`references/layout_archetypes.md`](references/layout_archetypes.md)):

* **Master & Frames**: `ARCH_01_COVER`, `ARCH_02_TOC`, `ARCH_03_CHAPTER`, `ARCH_11_CLOSING`, `ARCH_15_CONTACT_US`
* **KPI & Charts**: `ARCH_04_KPI_DASHBOARD`, `ARCH_16_CHART_BAR_TREND`, `ARCH_17_CHART_PIE_DONUT`, `ARCH_18_KPI_METRIC_GRID`, `ARCH_19_HERO_METRIC_SPLIT`
* **Strategy & Diagnostics**: `ARCH_05_MULTI_COLUMN_CARDS`, `ARCH_07_PROBLEM_SOLUTION_SWOT`, `ARCH_20_SWOT_TOWS_MATRIX`, `ARCH_21_BEFORE_AFTER_DIFF`, `ARCH_22_PROBLEM_IMPROVE_SPLIT`, `ARCH_23_RISK_MATRIX_RESPONSE`, `ARCH_24_MISSION_VISION_VALUES`
* **Process, Funnels & Ladders**: `ARCH_25_PROCESS_STEP_HORIZONTAL`, `ARCH_26_FUNNEL_CONVERSION`, `ARCH_27_STEP_LADDER_MATURITY`, `ARCH_28_WATERFALL_DIAMOND`
* **Schedules & Milestones**: `ARCH_06_TIMELINE_ROADMAP`, `ARCH_29_GANTT_SCHEDULE_TABLE`, `ARCH_30_MILESTONE_LIST_BADGE`
* **Platform & Ecosystem**: `ARCH_08_PLATFORM_ARCHITECTURE`, `ARCH_31_THREE_PILLARS_PLATFORM`, `ARCH_32_ECOSYSTEM_CIRCULAR`, `ARCH_14_CONCENTRIC_HUB`
* **Solutions, Cases & Endorsement**: `ARCH_09_SOLUTION_GRID`, `ARCH_10_CASE_STUDY`, `ARCH_33_HONOR_CERTIFICATION`, `ARCH_34_PARTNER_LOGO_WALL`, `ARCH_12_TEAM_PROFILE`, `ARCH_13_GLOBAL_FOOTPRINT`

- **Completion Criterion**: Every slide explicitly mapped to the optimal archetype ID (`ARCH_01` to `ARCH_34`) based on content semantics.

### Phase 3: Content Synthesizing & Proactive Field Population Protocol
- **Proactive Field Population Rule (Zero Default Leakage)**: The Agent MUST proactively synthesize and populate 100% of all required fields in the payload JSON for the chosen archetype. The Agent MUST NOT rely on engine default fallbacks or pass empty lists (`[]`).
  - `ARCH_01_COVER`: Provide `title`, `subtitle`, `date`, `author`.
  - `ARCH_02_TOC`: Provide `items`: `[{"title": "...", "bullets": [...]}]`.
  - `ARCH_03_CHAPTER`: Provide `title` / `headline`, `subtitle` / `category`.
  - `ARCH_04_KPI_DASHBOARD`: Provide `title`, `category`, `kpi_cards`: `[{"number": "...", "label": "...", "details": [...]}]`.
  - `ARCH_05_MULTI_COLUMN_CARDS`: Provide `title`, `category`, `columns`: `[{"header": "...", "bullets": [...]}]`.
  - `ARCH_06_TIMELINE_ROADMAP`: Provide `title`, `category`, `stages`: `[{"phase": "...", "title": "...", "desc": "..."}]`.
  - `ARCH_07_PROBLEM_SOLUTION_SWOT`: Provide `title`, `category`, `pain_header`, `pain_points`: `[...]`, `solution_header`, `solutions`: `[...]`.
  - `ARCH_08_PLATFORM_ARCHITECTURE`: Provide `title`, `category`, `layers`: `[{"layer_name": "...", "headline": "...", "modules": [...]}]`.
  - `ARCH_09_SOLUTION_GRID`: Provide `title`, `category`, `modules`: `[{"title": "...", "desc": "..."}]` (6 items).
  - `ARCH_10_CASE_STUDY`: Provide `title`, `category`, `client_name`, `hero_metric`, `hero_desc`, `bullets`: `[...]`.
  - `ARCH_11_CLOSING`: Provide `tagline`, `team`, `call_to_action`.
  - `ARCH_12_TEAM_PROFILE`: Provide `title`, `category`, `members`: `[{"name": "...", "title": "...", "role": "...", "credentials": [...]}]`.
  - `ARCH_13_GLOBAL_FOOTPRINT`: Provide `title`, `category`, `coverage_title`, `stats`: `[...]`, `network_title`, `offices`: `[...]`.
  - `ARCH_14_CONCENTRIC_HUB`: Provide `title`, `category`, `center_label`, `nodes`: `[{"title": "...", "desc": "..."}]` (up to 5 items).
  - `ARCH_16_RICH_CHART` (Vector Charts):
    - `ARCH_16_RADAR`: Provide `categories`, `series`: `[{"name", "values", "color"}]`, `insights`.
    - `ARCH_16_COMBO`: Provide `categories`, `bar_series`, `line_series`, `insights`.
    - `ARCH_16_DIVERGING`: Provide `categories`, `values`, `unit`, `insights`.
    - `ARCH_16_HEATMAP`: Provide `row_labels`, `col_labels`, `data_matrix`, `insights`.
    - `ARCH_16_EVOLUTION`: Provide `stages`, `values`, `sub_labels`, `insights`.
    - `ARCH_16_WATERFALL`: Provide `categories`, `values`, `unit`, `insights`.
    - `ARCH_16_SANKEY`: Provide `flows`: `[{"source", "target", "value", "color"}]`, `unit`, `insights`.
    - `ARCH_16_FUNNEL`: Provide `stages`, `values`, `conversion_rates`, `unit`, `insights`.
    - `ARCH_16_GAUGE`: Provide `current_val`, `target_val`, `min_val`, `max_val`, `subtitle`, `unit`, `insights`.
    - `ARCH_16_STACKED_AREA`: Provide `categories`, `series`: `[{"name", "values", "color"}]`, `unit`, `insights`.
- **High Information Density & Positive Phrasing**: Structure raw content into bold leading keywords followed by metric-backed bullet points.
- **2026 VI Grid Standards**: Enforce 0.8" side margins, color tokens (`#1E50E6`, `#50C8FF`, `#D70A32`, `#1E2024`, `#5A5A5A`, `#F6F8FA`), and clean hierarchy (refer to [`references/vi_and_typography.md`](references/vi_and_typography.md)).
- **Completion Criterion**: Clean presentation JSON payload constructed with 100% explicitly populated fields and zero fallback dependencies.

### Phase 4: Autonomous Clean OpenXML Assembly Engine
Execute the Python generation engine autonomously in the background to produce standard, uncorrupted OpenXML `.pptx` presentations:

```bash
python3 scripts/chint_pptx_engine.py <path_to_payload.json> <output_path.pptx>
```

#### OpenXML Engineering Safeguards:
1. **Pristine PresentationML Assembly**: Direct shape construction avoiding XML re-serialization through `xml.etree.ElementTree` (which causes `ns0:` namespace prefix corruption).
2. **Zero Font DRM Restrictions**: Guarantee no `p:embeddedFontLst`, `embedTrueTypeFonts`, or restricted font locks (`FuturaBT Book`) are serialized.
3. **Clean Edit View Properties**: Enforce default normal edit view (`viewProps.xml` without `lastView="sldMasterView"`).
4. **16:9 Widescreen Canvas**: Enforce `13.333" x 7.5"` slide dimensions.
- **Completion Criterion**: Engine exits with exit code 0 and creates the target `.pptx` file.

### Phase 5: Dual-Gate Automated QA & Clickable Delivery
1. **Gate 1: Automated Inspection & Validation Suite**:
   ```bash
   python3 scripts/inspect_pptx.py <output_path.pptx>
   ```
   * Verifies 16:9 aspect ratio and dimensions.
   * Confirms `正泰拓新体` typography and brand color tokens.
   * Checks package hygiene (0 font DRM locks, normal edit view).
   * Runs OpenXML schema and relationship integrity validation via `scripts/office/validate.py`.

2. **Gate 2: Microsoft PowerPoint Live UI Automation Test**:
   * Live macOS AppleScript test with Microsoft PowerPoint to verify `CLEAN_OPEN` with 0 repair dialogs or warnings.

3. **Clickable Delivery**:
   * Present a concise executive summary in Chinese to the PM with direct clickable links: `[文稿名称.pptx](file:///absolute/path/to/output_path.pptx)`.
- **Completion Criterion**: `inspect_pptx.py` confirms 100% schema compliance and `正泰拓新体` coverage, PowerPoint live automation returns `CLEAN_OPEN`, and clickable link returned in chat.

---

## Disclosed References & Assets Index

- **Bundled Fonts**: `assets/fonts/CHINTinno-Bold.ttf`, `CHINTinno-Regular.ttf`, `CHINTinno-Light.ttf`
- **Official 2026 VI Media Assets**: `assets/media/` (`cover_26_bg.png`, `toc_26_bg.png`, `chapter_26_bg.png`, `closing_26_bg.png`, `chint_badge.png`, 3D panoramic cityscapes)
- **Base Templates**: `assets/templates/26年模板拓新体.pptx`, `assets/templates/chint_archetypes_master.pptx`
- **Visual VI Reference**: [`references/vi_and_typography.md`](references/vi_and_typography.md)
- **Layout Archetypes Reference**: [`references/layout_archetypes.md`](references/layout_archetypes.md)
- **Legacy PPTX Modernization Guide**: [`references/legacy_pptx_migration_guide.md`](references/legacy_pptx_migration_guide.md)
- **Asset Library Guide**: [`references/asset_library_guide.md`](references/asset_library_guide.md)
- **Grill-Me Alignment SOP**: [`references/grill_me_alignment_sop.md`](references/grill_me_alignment_sop.md)
- **Generation Engine**: [`scripts/chint_pptx_engine.py`](scripts/chint_pptx_engine.py)
- **Quality Inspector**: [`scripts/inspect_pptx.py`](scripts/inspect_pptx.py)
- **OpenXML Validation Suite**: [`scripts/office/validate.py`](scripts/office/validate.py)
