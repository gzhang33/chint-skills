# CHINT PM Reusable Skills 技能库 (`chint-skills`)

本项目为**正泰电气（CHINT）产品经理（PM）可复用业务技能与领域知识库**集中托管与备份仓库。

宗旨是为正泰海外市场、低压配电及主配电产品线的产品经理提供标准化、高精度、可被 AI Agent 直接调用的业务技能资产（包含样本翻译、产品选型、数据分析、品牌设计规范与竞品对齐等）。

---

## 📦 产品经理可复用技能清单

| 技能名称 | 目录路径 | 业务适用场景与核心能力 | 权威标准 / 业务系统依据 |
|:---|:---|:---|:---|
| **`chint-brand-design`** | `skills/chint-brand-design/` | **正泰品牌资产与视觉规范系统**<br>专为正泰数字化产出（PPTX 汇报、Web 前端界面、数据图表、HTML/PDF 报告）提供全套自包含的品牌资产治理技能。内置正泰拓新体（CHINTinno）全套字体、极光蓝（`#1E50E6`）配色系统、16:9 版式网格、ECharts/Matplotlib 预设及 Token 导出工具。 | CHINT 官方品牌视觉识别系统（VI） |
| **`chint-pptx`** | `skills/chint-pptx/` | **正泰企业级 PPTX 智能演示文稿生成技能**<br>专为低压电气产品经理（PM）打造的符合 2026 VI 规范的 PPTX 生成技能。内置正泰拓新体（CHINTinno）全套 TrueType 字体包、34 种全场景版式原型库（ARCH_01 ~ ARCH_34）、12 组核心排版引擎、10 种矢量图表构建器、python-pptx 自动化生成引擎及 `/grill-me` 互动需求对齐 SOP。 | CHINT 2026 VI 视觉规范指导手册<br>2026年正泰PPT通用基础模版 |
| **`chint-acb-translation`** | `skills/chint-acb-translation/` | **正泰万能式断路器（ACB）海外样本与技术翻译**<br>专为正泰海外市场 PM 打造的万能式断路器（NXA/NA8/NA1/Noark UL）高精度翻译知识库。收录 8 大分域知识库（产品名称、电气参数、脱扣器与智能控制器、内外部附件机构、安装接线与结构、环境与标准、样本高频句式、翻译禁忌词库）及 88 组全量结构化元数据 JSON。 | IEC 60947-2 (2024)<br>GB/T 14048.2 (2020)<br>UL 1066 / IEEE C37.13 |
| **`chint-data-analysis`** | `skills/chint-data-analysis/` | **正泰主配电销售数据与业务智能分析**<br>专为 PM 业务分析打造的主配电产品销售数据透视、漏斗分析、产品线增长及自动化汇报生成技能。 | 正泰主配电产品线营销数据 |
| **`chint-pm-copywriter`** | `skills/chint-pm-copywriter/` | **B2B 工业品产品经理通用文案与汇报语法引擎**<br>专为工业制造与配电产品经理打造的向上汇报、QBR复盘、PRD价值主张与产品样本提炼技能。内置极简量化三要素、三段式负向建设性语法、黑白名单词典与5项出稿门禁，坚决杜绝浮夸黑话与战役化暗喻。 | 正泰高管汇报标准<br>B2B 工业品 PM 务实文案规范 |
| **`archify`** | `skills/archify/` | **正泰数字化系统架构与工作流高保真交互图谱**<br>专为系统架构、工业工作流、调用时序、数据管道与生命周期状态图打造的高保真编译渲染技能。默认适配正泰 VI 配色体系（正泰蓝 `#1E50E6`、诺雅克绿 `#5CB531` 及工业数字化标准语义色谱），支持中英文混排与自包含可交互 HTML/SVG 导出。 | 正泰 2026 VI 视觉规范指导手册<br>Archify 开源编译器体系 |
| **`chint-RAT`** | `skills/chint-RAT/` | **立项资料一页纸 PPT 生成**<br>复刻 NXA 系列立项样板版式（16:9 单页 12 分区看板 + 承接单位/团队/P1-P4 计划/财务三表），内置 python-pptx 生成引擎与校验器（分区齐全、平台命名、痛点量化、口径勾稽、字体 VI 门禁），配套立项内容方法论：数字化表述、痛点与产品定义一一对应、销售预测交叉验证、风险预案四要素、领导常问六问自检；技术 verdict 支持"部分可行"红标并自动追加风险预案/交叉验证附录页。 | NXA 系列电炉行业专供产品开发立项样板<br>配电产品线《立项资料编写经验分享》周会方法论（2026-08） |

---

## 🚀 快速安装与使用指南

### 1. 本地项目级安装（支持 Antigravity / Claude Code / Cursor / Copilot）
将技能目录复制到当前项目工作区的 `.agents/skills/` 目录下：

```bash
# 复制品牌设计技能到当前项目
cp -r skills/chint-brand-design /path/to/your-project/.agents/skills/

# 复制断路器翻译技能到当前项目
cp -r skills/chint-acb-translation /path/to/your-project/.agents/skills/

# 复制正泰系统架构与工作流交互图谱技能到当前项目
cp -r skills/archify /path/to/your-project/.agents/skills/
```

### 2. 用户级全局安装
将技能部署至 Antigravity / Claude Code 全局技能目录：

```bash
# 部署至 Antigravity 全局技能库
cp -r skills/chint-brand-design ~/.gemini/config/skills/
cp -r skills/chint-acb-translation ~/.gemini/config/skills/
cp -r skills/archify ~/.gemini/config/skills/
```

---

## 📌 知识库架构说明 (`archify`)

- `bin/archify.mjs`：原生 Node.js CLI 编译器与校验入口，支持 `render`, `compare`, `deliver`, `validate`, `doctor` 命令。
- `assets/template.html`：正泰企业级轻量 HTML 渲染母版，内置 `#1E50E6` 正泰蓝、`#5CB531` 诺雅克绿调色盘与 `CHINTinno` 字体栈。
- `schemas/`：包含 5 大图表类型（`architecture`, `workflow`, `sequence`, `dataflow`, `lifecycle`）的 JSON Schema 定义。
- `renderers/`：自包含的图表生成与布局引擎（含自动路由、正泰语义色谱注入与无障碍文本计算）。
- `delta/architecture-delta.mjs`：架构版本快照（Before / Delta / After）差异比对与交互审查器。
- `references/`：包含品牌标识、场景配方与设计模式参考文档。

---

## 📌 知识库架构说明 (`chint-brand-design`)

- `assets/fonts/`：内置正泰拓新体（CHINTinno）全套字体（Regular/Bold/Light），支持跨环境即开即用。
- `assets/logos/`：内置正泰品牌 SVG / PNG 矢量与光栅 Logo 图标资产。
- `assets/styles/chint-fonts.css`：单点事实来源的 `@font-face` 声明与全局 CSS Custom Properties。
- `references/color_palette.md`：极光蓝 `#1E50E6`、天青渐变 `#50C8FF` -> `#1E50C8`、灰阶及图表调色盘规范。
- `references/typography.md`：正泰拓新体层级排版、字号比例与跨平台渲染回退规范。
- `references/pptx_guidelines.md`：16:9 宽屏版式、母版网格与 `python-pptx` 自动化生成代码模版。
- `references/web_and_charts.md`：前端极简 UI 规范、Zero-Emoji 规则与 Matplotlib / ECharts 图表样式注入。
- `scripts/chint_theme.py`：Python 品牌主题管理模块，提供图表样式、PPTX 参数与色彩工具。
- `scripts/export_tokens.py`：支持一键导出 JSON / CSS Token 文件。

---

## 📌 知识库架构说明 (`chint-acb-translation`)

- `references/01_产品名称与系列.md`：收录万能式断路器定义、ACB/LVPCB/ICCB分类、NXA/NA8/Noark系列代号等。
- `references/02_电气性能与参数.md`：收录 $U_e, U_i, U_{imp}, I_n, I_{cu}, I_{cs}=100\%I_{cu}, I_{cw}, I_{cm}$, Cat B, 零飞弧等。
- `references/03_脱扣器与智能控制器.md`：收录 M/A/P/H 型、2.0N~4.0N、L/S/I/G/N 保护、ZSI、MCR、Override、热记忆等。
- `references/04_内部与外部附件机构.md`：收录 SHT、UVR、CC/CEM、M/MOE、AX、AL、RTC、钥匙锁、VBP挂锁罩、钢缆联锁等。
- `references/05_安装接线与结构尺寸.md`：收录 水平/垂直/前接线/90°旋转端子、加长排、抽屉座(Cradle)、三位置指示、Door Flange等。
- `references/06_环境条件与标准认证.md`：收录 IEC 60947-2、GB/T 14048.2、UL 1066、-45℃~+70℃超宽温、高海拔降容、EMC、CB/CE/Marine 认证等。
- `references/07_样本高频句式与栏目.md`：收录 样本册标准栏目标题与产品亮点英文宣传统一表达。
- `references/08_翻译禁忌与防呆词库.md`：硬性拦截如 Universal Breaker ❌, Closed electromagnet ❌, Excitation release ❌, Drawer box ❌ 等错译。
- `references/acb_terminology_master.json`：包含 88 组带 10 维元数据的完整结构化数据包，支持程序化向量或 RAG 检索。

---

## 📌 贡献与维护规范

- 本仓库专注收录正泰**产品经理（PM）业务可复用**技能与知识库。
- 所有新增技能须遵循 `agentskills.io` 与 `writing-great-skills` 规范，且包含完整 `SKILL.md` 指南与数据校验。
