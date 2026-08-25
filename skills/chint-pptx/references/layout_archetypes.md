# CHINT 34-Slide Layout Archetype Specifications & Universal Decision Matrix (2026 VI Standard Edition)

This catalog defines all **34 enterprise slide layout archetypes** supported by the `chint-pptx` generation engine (`chint_pptx_engine.py`), aligned with the **26年模板拓新体.pptx** 109-page master presentation.

---

## 1. Universal Semantic Selection Matrix (34 版式全局选型矩阵)

The Agent evaluates the semantic nature, business intent, and data structure of each slide topic to select the optimal archetype from 7 major functional scenarios:

| 场景分类 | 语义意图与业务场景 | 核心触发关键词 | 推荐版式 ID | 视觉形态特征 | 必需 Payload Checklist |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **母版框架** | 演示文稿封面 | 标题, 汇报, 发布会, 演讲, 规划 | `ARCH_01_COVER` | 3D 莫比乌斯环 + 双层悬浮信息卡 | `title`, `subtitle`, `date`, `author` |
| **母版框架** | 议程大纲与目录 | 目录, 议程, 大纲, CONTENTS | `ARCH_02_TOC` | 35% 电蓝饰带 + 7.76" 拓新胶囊容器 | `items`: `[{"title": "...", "bullets": [...]}]` |
| **母版框架** | 篇章切页与过渡 | 章节, 阶段过渡, 分篇, 导引 | `ARCH_03_CHAPTER` | 官方光效居中横幅 + 亮青装饰底线 | `title`/`headline`, `subtitle`/`category` |
| **母版框架** | 封底致谢与标语 | 致谢, 问答, 谢谢, THANKS | `ARCH_11_CLOSING` | 3D 莫比乌斯环 + THANKS 蓝带 | `tagline`, `team`, `call_to_action` |
| **母版框架** | 联系方式与办事处 | 联系我们, 商务, 咨询, 网点 | `ARCH_15_CONTACT_US` | 4 通道联络卡片 + 区域办事处列表 | `title`, `category`, `channels`, `offices` |
| **KPI 图表** | 核心指标经营看板 | KPI, 指标, 数据, 经营, 看板 | `ARCH_04_KPI_DASHBOARD` | 2–4 栏自适应卡片 + 顶部蓝带大数字 | `title`, `category`, `kpi_cards`: `[{"number", "label", "details"}]` |
| **KPI 图表** | 柱状/折线数据对比 | 趋势, 柱状图, 折线图, 增长, 对比 | `ARCH_16_CHART_BAR_TREND` | 左侧叙事洞察卡 + 右侧原生柱状图 | `title`, `category`, `categories`, `series` |
| **KPI 图表** | 结构拆解/饼图环形 | 占比, 结构, 环形图, 构成, 份额 | `ARCH_17_CHART_PIE_DONUT` | 左侧 360° 环形图 + 右侧 2–6 栏自适应卡 | `title`, `category`, `center_metric`, `slices` |
| **KPI 图表** | 竞品与技术对标雷达 | 雷达图, 维度对标, 竞品对比, 能力 | `ARCH_16_RADAR` | 2026 VI 矢量雷达图 + 右侧战略洞察卡 | `title`, `category`, `categories`, `series`, `insights` |
| **KPI 图表** | 营收与增速双轴组合 | 双轴图, 组合图, 柱折图, 复合增长 | `ARCH_16_COMBO` | 主轴柱状+次轴折线双轴图 + 战略洞察卡 | `title`, `category`, `categories`, `bar_series`, `line_series`, `insights` |
| **KPI 图表** | 赛道渗透双向对比柱 | 分岔柱图, 对比, 增长 vs 承压 | `ARCH_16_DIVERGING` | 正负分岔水平柱图 + 战略洞察卡 | `title`, `category`, `categories`, `values`, `insights` |
| **KPI 图表** | 产品与行业适配热力 | 热力图, 矩阵, 适配度, 行业成熟度 | `ARCH_16_HEATMAP` | 2026 VI 渐变蓝热力矩阵 + 战略洞察卡 | `title`, `category`, `row_labels`, `col_labels`, `data_matrix`, `insights` |
| **KPI 图表** | 利润与成本归因瀑布 | 瀑布图, 归因, 毛利桥接, 增减拆解 | `ARCH_16_WATERFALL` | 正负阶梯色块 + 连线对齐 + 战略洞察卡 | `title`, `category`, `categories`, `values`, `insights` |
| **KPI 图表** | 供应链与价值流桑基 | 桑基图, 流向, 能源流转, 路径分布 | `ARCH_16_SANKEY` | 平滑贝塞尔曲线流向带 + 战略洞察卡 | `title`, `category`, `flows`, `insights` |
| **KPI 图表** | 业务转化与履约漏斗 | 漏斗图, 转化率, 商机流转, 阶段留存 | `ARCH_16_FUNNEL` | 对称梯形渐变色块 + 转化率气泡 + 洞察卡 | `title`, `category`, `stages`, `values`, `insights` |
| **KPI 图表** | 目标达成半环仪表盘 | 仪表盘, 达成率, OEE, 阈值, 靶心图 | `ARCH_16_GAUGE` | 180° 半环刻度 + 极客蓝指针 + 卓越区间 | `title`, `category`, `current_val`, `target_val`, `insights` |
| **KPI 图表** | 多维度规模堆叠面积 | 堆叠面积图, 业务结构演进, 规模预测 | `ARCH_16_STACKED_AREA` | 品牌 8 阶平滑堆叠面 + 总值趋势线 + 洞察卡 | `title`, `category`, `categories`, `series`, `insights` |
| **KPI 图表** | 4–5 栏紧凑指标网格 | 网格, 指标矩阵, YoY, 达成率 | `ARCH_18_KPI_METRIC_GRID` | 4–5 栏自适应大数字卡 + 涨跌幅标签 | `title`, `category`, `metrics`: `[{"number", "label", "trend", "desc"}]` |
| **KPI 图表** | 超级单指标发布 | 9000W, 里程碑, 超级指标, 突破 | `ARCH_19_HERO_METRIC_SPLIT` | 左侧 42pt 超大数字蓝卡 + 右侧叙事 | `title`, `category`, `hero_number`, `hero_unit`, `bullets` |
| **战略诊断** | 平行概念/定位解析 | 定位, 职责, 多维度, 概念, 支柱 | `ARCH_05_MULTI_COLUMN_CARDS` | 2–4 栏平行卡片 + 浅蓝顶帽标头 | `title`, `category`, `columns`: `[{"header", "bullets"}]` |
| **战略诊断** | 痛点挑战 vs 解决方案 | 痛点, 挑战 vs 方案, 举措, 应对 | `ARCH_07_PROBLEM_SOLUTION_SWOT` | 左右分栏：红框痛点 (#FFEBEB) vs 蓝框方案 | `title`, `category`, `pain_points`, `solutions` |
| **战略诊断** | SWOT 经典战略矩阵 | SWOT, TOWS, 态势分析, 四象限 | `ARCH_20_SWOT_TOWS_MATRIX` | 2×2 四象限矩阵 (S:蓝, W:红, O:绿, T:灰) | `title`, `category`, `strengths`, `weaknesses`, `opportunities`, `threats` |
| **战略诊断** | 升级前后对比表 | 前后对比, Before/After, 传统 vs 新 | `ARCH_21_BEFORE_AFTER_DIFF` | 左侧传统模式 (✕) vs 右侧正泰方案 (✔) | `title`, `category`, `before_items`, `after_items` |
| **战略诊断** | 不足与改善行动 | 短板, 缺陷 vs 改善计划, 行动 | `ARCH_22_PROBLEM_IMPROVE_SPLIT` | 左侧浅红短板卡 vs 右侧浅蓝改善卡 | `title`, `category`, `problems`, `improvements` |
| **战略诊断** | 三维风险评估预案 | 风险, 防控, 评估, 高/中/低 | `ARCH_23_RISK_MATRIX_RESPONSE` | 3 栏风险卡 + 风险等级标签 + 应对预案 | `title`, `category`, `risks`: `[{"level", "title", "desc", "response"}]` |
| **战略诊断** | 文化使命愿景基石 | 使命, 愿景, 价值观, 文化基石 | `ARCH_24_MISSION_VISION_VALUES` | 3 联文化卡片 + 英文 Tag + 金句引言 | `title`, `category`, `pillars`: `[{"en_title", "cn_title", "slogan", "details"}]` |
| **流程流水** | 3–5 步横向流水线 | 步骤, 流程, 阶段, 管道, 步骤123 | `ARCH_25_PROCESS_STEP_HORIZONTAL` | STEP 数字胶囊 + 亮青流转 chevron 箭头 | `title`, `category`, `steps`: `[{"phase", "title", "desc"}]` |
| **流程流水** | 4 阶段营销转化漏斗 | 漏斗, 转化率, 触达, 留存, 签约 | `ARCH_26_FUNNEL_CONVERSION` | 4 阶段倒梯形/阶梯递减渐变蓝块 | `title`, `category`, `stages`: `[{"stage", "value", "desc"}]` |
| **流程流水** | 4 阶技术成熟度阶梯 | 阶梯, 成熟度, 演进, 2.0 -> 5.0 | `ARCH_27_STEP_LADDER_MATURITY` | 4 阶递增台阶 + V2.0~V5.0 蓝色顶帽 | `title`, `category`, `steps`: `[{"ver", "title", "desc"}]` |
| **流程流水** | IPD 双钻研发门禁 | IPD, 门禁, G1-G5, 研发流程 | `ARCH_28_WATERFALL_DIAMOND` | 5 阶段门禁菱形节点 + 下方判定要点 | `title`, `category`, `gates`: `[{"gate", "title"}]` |
| **排期里程** | 推进路线与里程碑 | 路线图, 时间轴, 里程碑, 推进 | `ARCH_06_TIMELINE_ROADMAP` | 4 阶段中心主轴 + 亮青轨道圆点 | `title`, `category`, `stages`: `[{"phase", "title", "desc"}]` |
| **排期里程** | 规范项目甘特表格 | 甘特图, 排期表, 进度表, Q1-Q4 | `ARCH_29_GANTT_SCHEDULE_TABLE` | 标准排期表格 + 蓝底表头 + 状态指示符 | `title`, `category`, `tasks`: `[["任务", "负责人", "Q1", ...]]` |
| **排期里程** | 年份药丸大事记 | 大事记, 年份, 发展历程, 纪事 | `ARCH_30_MILESTONE_LIST_BADGE` | 左侧 24pt 年份药丸胶囊 + 右侧卡片 | `title`, `category`, `milestones`: `[{"year", "title", "desc"}]` |
| **架构生态** | 4 层分层技术架构 | 架构, 分层, 底座, 协议层, 应用层 | `ARCH_08_PLATFORM_ARCHITECTURE` | 4 层堆叠卡 + 深蓝底座层 + 模块管道 | `title`, `category`, `layers`: `[{"layer_name", "headline", "modules"}]` |
| **架构生态** | 三支柱与平台底座 | 支柱, 底座, 三大支撑, 平台 | `ARCH_31_THREE_PILLARS_PLATFORM` | 顶部 3 支柱卡片 + 底部企业深蓝底座 | `title`, `category`, `pillars`, `base_title`, `base_desc` |
| **架构生态** | 4 方协同环形生态 | 生态, 拓扑, 协同, 4方, 合作伙伴 | `ARCH_32_ECOSYSTEM_CIRCULAR` | 中心电蓝中枢 + 亮青轨道 + 4 节点卡片 | `title`, `category`, `hub_label`, `nodes` |
| **架构生态** | 同心圆战略飞轮 | 闭环, 飞轮, 枢纽, 同心圆, 赋能 | `ARCH_14_CONCENTRIC_HUB` | 同心圆环 + 中心核心球 + 5 轨道节点 | `title`, `category`, `center_label`, `nodes` |
| **方案背书** | 2×3 六宫格方案矩阵 | 场景, 解决方案包, 方案矩阵, 6宫格 | `ARCH_09_SOLUTION_GRID` | 2×3 浅蓝卡片 + 电蓝标题 | `title`, `category`, `modules`: `[{"title", "desc"}]` (6项) |
| **方案背书** | 标杆工程/客户案例 | 标杆, 案例, 示范工程, 落地实践 | `ARCH_10_CASE_STUDY` | 左侧深蓝成效大卡 + 右侧项目价值要点 | `title`, `category`, `client_name`, `hero_metric`, `bullets` |
| **方案背书** | 权威认证与荣誉徽章 | 认证, 荣誉, 证书, 专利, 背书 | `ARCH_33_HONOR_CERTIFICATION` | 4 栏荣誉卡 + 认证徽章 + 绿色成就指标 | `title`, `category`, `honors`: `[{"badge", "title", "org", "metric"}]` |
| **方案背书** | 合作伙伴 Logo 墙 | Logo墙, 合作伙伴, 客户墙, 厂商 | `ARCH_34_PARTNER_LOGO_WALL` | 2×2 / 2×4 对称网格卡 + 合作领域标签 | `title`, `category`, `partners`: `[{"category", "title", "desc"}]` |
| **组织能力** | 核心团队/专家履历 | 团队, 专家, 讲师, 负责人, 资历 | `ARCH_12_TEAM_PROFILE` | 3–4 栏专家卡片 + 角色胶囊 + 资质要点 | `title`, `category`, `members`: `[{"name", "title", "role", "credentials"}]` |
| **组织能力** | 全球业务网络/大区 | 全球化, 布局, 海外, 大区, 办事处 | `ARCH_13_GLOBAL_FOOTPRINT` | 左侧企业深蓝大盘统计 + 右侧区域网络 | `title`, `category`, `coverage_title`, `stats`, `offices` |

---

## 2. Archetype Disambiguation & Decision Rules (选型排他与最佳适配规则)

1. **红蓝痛点对标 vs 多列平行卡片**：
   - 若内容具有明确的**矛盾对立性**（如“现有挑战 vs 应对方案”、“竞品缺陷 vs 我方优势”、“问题 vs 举措”），**必须**选 `ARCH_07_PROBLEM_SOLUTION_SWOT`，严禁退化为普通的 `ARCH_05`。
2. **分层架构 vs 方案矩阵**：
   - 纵向具有**上下依赖/层叠调用关系**（如底座层 -> 核心层 -> 应用层），选 `ARCH_08_PLATFORM_ARCHITECTURE`。
   - 横向为**平级细分行业场景**（如数据中心、新能源、轨道交通等），选 `ARCH_09_SOLUTION_GRID`。
3. **指标看板 vs 标杆案例**：
   - 泛业务或产品线的**宏观量化数据汇总**，选 `ARCH_04_KPI_DASHBOARD`（3个卡片各自独立）。
   - 针对**单一客户或具体示范项目**的深度剖析，选 `ARCH_10_CASE_STUDY`（左侧单一大指标，右侧背景/方案/价值）。
4. **时间轴演进 vs 同心圆闭环 vs 阶段阶梯**：
   - 具有**单向时间推移与阶段递进关系**，选 `ARCH_06_TIMELINE_ROADMAP`。
   - 具有**技术版本演进与台阶递进**，选 `ARCH_27_STEP_LADDER_MATURITY`。
   - 具有**持续自循环、飞轮赋能或多要素协同**特征，选 `ARCH_14_CONCENTRIC_HUB`。
5. **10 大数据量化与高清矢量图表精准选型决策**：
   - **利润/成本构成拆解、毛利桥接、YoY 增减归因**：选 `ARCH_16_WATERFALL`（瀑布图，展示起步基准、各驱动增减因素与期末净值）。
   - **能源潮流流向、电力供应链流转、端到端消纳路径**：选 `ARCH_16_SANKEY`（桑基图，展示多源节点至目标节点的贝塞尔平滑流向带与权重）。
   - **招投标阶段履约、线索-商机-签约转化留存**：选 `ARCH_16_FUNNEL`（漏斗图，对称多阶梯形色块 + 阶段转化率标注）。
   - **战略 KPI 达成率、智能制造 OEE、供电安全阈值**：选 `ARCH_16_GAUGE`（半环仪表盘，三段式健康度色带 + 超大英雄数字）。
   - **多业务线历史规模与未来结构变迁 (时间轴)**：选 `ARCH_16_STACKED_AREA`（堆叠面积图，8阶品牌色叠加 + 顶部总量虚线）。
   - **多维度竞品能力与技术指标对标 (3~6维)**：选 `ARCH_16_RADAR`（雷达图，极坐标多边形与对标基线）。
   - **营收绝对值与同比增速复合看板**：选 `ARCH_16_COMBO`（双轴组合图，主轴柱图 + 次轴折线）。
   - **多行业赛道增速正负分化对比 (增长 vs 承压)**：选 `ARCH_16_DIVERGING`（分岔水平柱图，以 0 为中心对称展开）。
   - **产品系列与垂直行业适配度及成熟度矩阵**：选 `ARCH_16_HEATMAP`（热力矩阵图，2026 VI 蓝色阶梯度与数值标注）。
   - **业务板块占比与份额构成 (2~6 切片)**：选 `ARCH_17_CHART_PIE_DONUT`（360° 环形切片 + 右侧自适应说明卡）。

