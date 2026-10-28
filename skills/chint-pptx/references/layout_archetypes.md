# CHINT 34-Slide Layout Archetype Catalog and Universal Decision Matrix

This catalog defines the 34 layouts supported by `chint-pptx/scripts/chint_pptx_engine.py` and aligned with the `26年模板拓新体.pptx` template.

## 1. Universal semantic selection matrix

Choose an archetype from the topic's meaning, business purpose, and data structure. Trigger keywords below are literal terms found in common Chinese requests; payload requirements are ultimately validated by the engine.

| Scenario | Intent and use case | Trigger keywords | Layout ID | Visual structure | Payload fields |
|---|---|---|---|---|---|
| Master shell | Presentation cover | “标题”, “汇报”, “发布会”, “演讲”, “规划” | `ARCH_01_COVER` | 3D Möbius ring with layered floating information cards | `title`; optional `subtitle`, `date`, `author` |
| Master shell | Agenda and contents | “目录”, “议程”, “大纲”, `CONTENTS` | `ARCH_02_TOC` | Native single-page contents artwork from the 2026 VI template | `items`: strings or objects with a `title` |
| Master shell | Chapter transition | “章节”, “阶段过渡”, “分篇”, “导引” | `ARCH_03_CHAPTER` | Centered official light-effect banner with a cyan accent rule | `title` or `headline`; `subtitle` or `category` |
| Master shell | Closing and thanks | “致谢”, “问答”, “谢谢”, `THANKS` | `ARCH_11_CLOSING` | 3D Möbius ring and blue THANKS banner | Optional `tagline`, `team`, `call_to_action`, `contact` |
| Master shell | Contact details and offices | “联系我们”, “商务”, “咨询”, “网点” | `ARCH_15_CONTACT_US` | Four contact cards and a regional office list | `title`, `channels`, `offices` |
| KPI and charts | KPI dashboard | `KPI`, “指标”, “数据”, “经营”, “看板” | `ARCH_04_KPI_DASHBOARD` | Two to four adaptive cards with large values and a blue header | `title`, `kpi_cards`; optional `details` |
| KPI and charts | Bar and line comparison | “趋势”, “柱状图”, “折线图”, “增长”, “对比” | `ARCH_16_CHART_BAR_TREND` | Narrative insight card beside an editable native chart | `title`, `categories`, `series`, `summary_bullets` |
| KPI and charts | Composition and donut chart | “占比”, “结构”, “环形图”, “构成”, “份额” | `ARCH_17_CHART_PIE_DONUT` | Donut chart beside two to six adaptive explanation cards | `title`, `center_metric`, `center_label`, `slices` |
| KPI and charts | Competitor or technology radar | “雷达图”, “维度对标”, “竞品对比”, “能力” | `ARCH_16_RADAR` | Editable native radar chart with a strategic insight card | `title`, 3–6 `categories`, `series`; non-full-width layouts also require `insights` |
| KPI and charts | Revenue and growth dual axis | “双轴图”, “组合图”, “柱折图”, “复合增长” | `ARCH_16_COMBO` | Primary-axis columns, secondary-axis line, and insight card | `title`, `categories`, `bar_series`, `line_series`; non-full-width layouts also require `insights` |
| KPI and charts | Diverging comparison | “分岔柱图”, “增长 vs 承压” | `ARCH_16_DIVERGING` | Horizontal positive and negative bars around zero | `title`, `categories`, `values`, `unit`; non-full-width layouts also require `insights` |
| KPI and charts | Product and industry fit matrix | “热力图”, “矩阵”, “适配度”, “行业成熟度” | `ARCH_16_HEATMAP` | Gradient-blue heatmap with a strategic insight card | `title`, `row_labels`, `col_labels`, `data_matrix`; non-full-width layouts also require `insights` |
| KPI and charts | Profit and cost attribution | “瀑布图”, “归因”, “毛利桥接”, “增减拆解” | `ARCH_16_WATERFALL` | Positive and negative steps with connector alignment | `title`, `categories`, `values`, `unit`; non-full-width layouts also require `insights` |
| KPI and charts | Supply-chain or value-flow analysis | “桑基图”, “流向”, “能源流转”, “路径分布” | `ARCH_16_SANKEY` | Smooth Bézier flow bands between weighted nodes | `title`, `flows`; non-full-width layouts also require `insights` |
| KPI and charts | Conversion and fulfillment funnel | “漏斗图”, “转化率”, “商机流转”, “阶段留存” | `ARCH_16_FUNNEL` | Symmetric tapered stages with conversion callouts | `title`, `stages`, `values`, `unit`; non-full-width layouts also require `insights` |
| KPI and charts | Target attainment gauge | “仪表盘”, “达成率”, `OEE`, “阈值” | `ARCH_16_GAUGE` | 180-degree gauge with a blue pointer and target bands | `title`, `current_val`, `target_val`, `min_val`, `max_val`, `unit`; non-full-width layouts also require `insights` |
| KPI and charts | Stacked scale over time | “堆叠面积图”, “业务结构演进”, “规模预测” | `ARCH_16_STACKED_AREA` | Stacked brand-color series with a total trend line | `title`, `categories`, `series`, `unit`; non-full-width layouts also require `insights` |
| KPI and charts | Compact KPI grid | “网格”, “指标矩阵”, `YoY`, “达成率” | `ARCH_18_KPI_METRIC_GRID` | Four or five adaptive metric cards with trend labels | `title`, `category`, `metrics` |
| KPI and charts | Single hero metric | “9000W”, “里程碑”, “超级指标”, “突破” | `ARCH_19_HERO_METRIC_SPLIT` | Oversized metric card beside supporting narrative | `title`, `hero_label`, `hero_number`, `hero_unit`, `hero_desc`, `bullets` |
| Strategic diagnosis | Parallel concepts or positioning | “定位”, “职责”, “多维度”, “概念”, “支柱” | `ARCH_05_MULTI_COLUMN_CARDS` | Two to four parallel cards with pale-blue headers | `title`, `category`, `columns` |
| Strategic diagnosis | Problems and solutions | “痛点”, “挑战 vs 方案”, “举措”, “应对” | `ARCH_07_PROBLEM_SOLUTION_SWOT` | Red problem panel beside blue solution panel | `title`, `pain_points`, `solutions`, `pain_summary`, `solution_summary` |
| Strategic diagnosis | SWOT or TOWS matrix | `SWOT`, `TOWS`, “态势分析”, “四象限” | `ARCH_20_SWOT_TOWS_MATRIX` | 2×2 matrix with blue, red, green, and gray quadrants | `title`, `category`, `strengths`, `weaknesses`, `opportunities`, `threats` |
| Strategic diagnosis | Before and after comparison | “前后对比”, `Before/After`, “传统 vs 新” | `ARCH_21_BEFORE_AFTER_DIFF` | Conventional approach beside the CHINT solution | `title`, `before_items`, `after_items`, `before_summary`, `after_summary` |
| Strategic diagnosis | Gaps and improvement actions | “短板”, “缺陷 vs 改善计划”, “行动” | `ARCH_22_PROBLEM_IMPROVE_SPLIT` | Pale-red gap panel beside a pale-blue action panel | `title`, `problems`, `improvements`, `problem_summary`, `improve_summary` |
| Strategic diagnosis | Risk assessment and response | “风险”, “防控”, “评估”, “高/中/低” | `ARCH_23_RISK_MATRIX_RESPONSE` | Risk cards, severity labels, and response plans | `title`, `risks` |
| Strategic diagnosis | Mission, vision, and values | “使命”, “愿景”, “价值观”, “文化基石” | `ARCH_24_MISSION_VISION_VALUES` | Three culture cards, English tags, and a quotation | `title`, `pillars` |
| Process and flow | Three to five process steps | “步骤”, “流程”, “阶段”, “管道” | `ARCH_25_PROCESS_STEP_HORIZONTAL` | Numbered steps connected by cyan chevrons | `title`, `steps` |
| Process and flow | Marketing conversion funnel | “漏斗”, “转化率”, “触达”, “留存”, “签约” | `ARCH_26_FUNNEL_CONVERSION` | Stacked tapered stages with decreasing values | `title`, `category`, `stages` |
| Process and flow | Technology maturity ladder | “阶梯”, “成熟度”, “演进”, “版本升级” | `ARCH_27_STEP_LADDER_MATURITY` | Ascending steps with version markers | `title`, `category`, `steps` |
| Process and flow | IPD double-diamond gates | `IPD`, “门禁”, “研发流程” | `ARCH_28_WATERFALL_DIAMOND` | Stage gates with decision points below | `title`, `category`, `gates` |
| Roadmap and milestones | Roadmap and milestones | “路线图”, “时间轴”, “里程碑”, “推进” | `ARCH_06_TIMELINE_ROADMAP` | Centered timeline with cyan markers | `title`, `category`, `stages` |
| Roadmap and milestones | Project Gantt schedule | “甘特图”, “排期表”, “进度表”, `Q1-Q4` | `ARCH_29_GANTT_SCHEDULE_TABLE` | Schedule table with blue header and status indicators | `title`, `category`, `tasks` |
| Roadmap and milestones | Year-by-year milestones | “大事记”, “年份”, “发展历程”, “纪事” | `ARCH_30_MILESTONE_LIST_BADGE` | Year badges beside milestone cards | `title`, `category`, `milestones` |
| Architecture and ecosystem | Four-layer technology architecture | “架构”, “分层”, “底座”, “协议层”, “应用层” | `ARCH_08_PLATFORM_ARCHITECTURE` | Four stacked layers with a dark-blue foundation | `title`, `category`, `layers` |
| Architecture and ecosystem | Three pillars and platform base | “支柱”, “底座”, “三大支撑”, “平台” | `ARCH_31_THREE_PILLARS_PLATFORM` | Three pillar cards above a blue platform base | `title`, `category`, `pillars`, `base_title`, `base_desc` |
| Architecture and ecosystem | Four-party collaboration | “生态”, “拓扑”, “协同”, “4方”, “合作伙伴” | `ARCH_32_ECOSYSTEM_CIRCULAR` | Central blue hub, cyan orbit, and four nodes | `title`, `category`, `hub_label`, `nodes` |
| Architecture and ecosystem | Concentric strategy flywheel | “闭环”, “飞轮”, “枢纽”, “同心圆”, “赋能” | `ARCH_14_CONCENTRIC_HUB` | Concentric rings with a central hub and five orbiting nodes | `title`, `category`, `center_label`, `nodes` |
| Solutions and proof points | Six-part solution matrix | “场景”, “解决方案包”, “方案矩阵”, “6宫格” | `ARCH_09_SOLUTION_GRID` | 2×3 pale-blue cards with electric-blue titles | `title`, `category`, six `modules` |
| Solutions and proof points | Customer or reference project | “标杆”, “案例”, “示范工程”, “落地实践” | `ARCH_10_CASE_STUDY` | Large outcome metric beside context, solution, and value | `title`, `client_name`, `hero_metric`, `hero_desc`, `bullets` |
| Solutions and proof points | Certifications and honors | “认证”, “荣誉”, “证书”, “专利”, “背书” | `ARCH_33_HONOR_CERTIFICATION` | Four honor cards with badges and achievement metrics | `title`, `category`, `honors` |
| Solutions and proof points | Partner logo wall | “Logo墙”, “合作伙伴”, “客户墙”, “厂商” | `ARCH_34_PARTNER_LOGO_WALL` | Symmetric 2×2 or 2×4 logo cards with capability labels | `title`, `category`, `partners` |
| Organization and capability | Core team and expert profiles | “团队”, “专家”, “讲师”, “负责人”, “资历” | `ARCH_12_TEAM_PROFILE` | Three or four profile cards with roles and credentials | `title`, `category`, `members` |
| Organization and capability | Global network and regions | “全球化”, “布局”, “海外”, “大区”, “办事处” | `ARCH_13_GLOBAL_FOOTPRINT` | Large network metrics beside regional coverage | `title`, `coverage_title`, `stats`, `offices`, `network_title` |

Fields such as `date`, `author`, closing copy, and insights are never invented when absent. Only `ARCH_16_CHART_BAR_TREND` and `ARCH_16_RADAR` use editable native charts; other `ARCH_16` chart layouts render raster images and report that limitation. The authoritative required-field validation is `_validate_slide_payload` in `scripts/chint_pptx_engine.py`.

## 2. Archetype disambiguation and decision rules

1. **Problem-solution contrast versus parallel cards**
   - When the content has a clear conflict or contrast, such as “现有挑战 vs 应对方案”, “竞品缺陷 vs 我方优势”, or “问题 vs 举措”, select `ARCH_07_PROBLEM_SOLUTION_SWOT`. Do not downgrade it to ordinary `ARCH_05` cards.
2. **Layered architecture versus solution matrix**
   - Use `ARCH_08_PLATFORM_ARCHITECTURE` for vertical dependencies or call layers, such as base → core → application.
   - Use `ARCH_09_SOLUTION_GRID` for peer industry scenarios, such as data centers, new energy, or rail transit.
3. **KPI dashboard versus reference case**
   - Use `ARCH_04_KPI_DASHBOARD` for broad quantitative summaries of a business or product line.
   - Use `ARCH_10_CASE_STUDY` for an in-depth review of one customer or project, with one lead metric and supporting context, solution, and value.
4. **Timeline versus circular loop versus maturity ladder**
   - Use `ARCH_06_TIMELINE_ROADMAP` for one-way progression over time.
   - Use `ARCH_27_STEP_LADDER_MATURITY` for version or technology maturity progression.
   - Use `ARCH_14_CONCENTRIC_HUB` for continuous cycles, flywheels, or collaboration among multiple elements.
5. **Quantitative chart selection**
   - Profit or cost composition, gross-margin bridges, and year-over-year attribution: use `ARCH_16_WATERFALL` to show the baseline, drivers, and ending value.
   - Energy or supply-chain flows: use `ARCH_16_SANKEY` to show weighted paths from source nodes to destinations.
   - Tender fulfillment or lead-to-contract conversion: use `ARCH_16_FUNNEL` for stages and conversion rates.
   - Strategic KPI attainment, manufacturing OEE, or power-supply thresholds: use `ARCH_16_GAUGE` for a half-ring gauge and status bands.
   - Historical scale and future mix across business lines: use `ARCH_16_STACKED_AREA` for time-based stacked series.
   - Competitor capabilities across three to six dimensions: use `ARCH_16_RADAR` for polygon comparisons and a baseline.
   - Revenue and year-over-year growth: use `ARCH_16_COMBO` for a dual-axis column and line chart.
   - Positive and negative growth across industries: use `ARCH_16_DIVERGING` for bars centered on zero.
   - Product fit across industries or maturity dimensions: use `ARCH_16_HEATMAP` for a labeled matrix.
   - Business mix across two to six categories: use `ARCH_17_CHART_PIE_DONUT` for a donut with adaptive explanation cards.
