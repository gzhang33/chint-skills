# CHINT PM Reusable Skills 技能库 (`chint-skills`)

本项目为**正泰电气（CHINT）产品经理（PM）可复用业务技能与领域知识库**集中托管与备份仓库。

宗旨是为正泰海外市场、低压配电及主配电产品线的产品经理提供标准化、高精度、可被 AI Agent 直接调用的业务技能资产（包含样本翻译、产品选型、数据分析、品牌设计规范与竞品对齐等）。

---

## 📦 产品经理可复用技能清单

| 技能名称 | 目录路径 | 业务适用场景与核心能力 | 权威标准 / 业务系统依据 |
|:---|:---|:---|:---|
| **`chint-pptx`** | `skills/chint-pptx/` | **正泰企业级 PPTX 智能演示文稿生成**<br>按 2026 VI 规范生成可编辑的产品演示文稿。内容页收敛为表格契约（`ARCH_TABLE`）加三张原生图表（趋势 / 占比 / 雷达），封面与章节页继承模板版式保持原生可编辑。内置结构合规门禁、开源 OpenXML 校验、源页保真校验与渲染预览链路。 | CHINT 2026 VI 视觉规范指导手册<br>2026 年正泰 PPT 通用基础模板 |
| **`chint-translation`** | `skills/chint-translation/` | **B2B 工业品翻译与本地化标准**<br>覆盖「三断一接」（ACB / MCCB / MCB / 接触器）、双电源（ATS）、电能质量（SVG / APF）、固态断路器、传感器与继电器。收录 8 大分域知识库（产品名称、电气参数、脱扣器与智能控制器、内外附件机构、安装接线与结构、环境与标准、样本高频句式、翻译禁忌词库）及结构化术语主数据。 | IEC 60947 / 60898 / 61000<br>GB/T 14048.2<br>UL 489 / 1066 / 1008 |
| **`chint-pm-copywriter`** | `skills/chint-pm-copywriter/` | **B2B 工业品 PM 文案与汇报语法引擎**<br>向上汇报、QBR 复盘、PRD 价值主张与产品样本提炼。内置极简量化三要素、三段式负向建设性语法、黑白名单词典与出稿门禁，杜绝浮夸黑话与战役化暗喻。 | 正泰高管汇报标准<br>B2B 工业品 PM 务实文案规范 |
| **`chint-brand-design`** | `skills/chint-brand-design/` | **正泰品牌资产与视觉规范系统**<br>为 PPTX、Web 前端、数据图表、HTML/PDF 报告提供自包含的品牌资产治理。内置正泰拓新体全套字体、2026 VI 配色矩阵与 Token 导出工具。具体 PPTX 生成请走 `chint-pptx`。 | CHINT 官方 2026 VI |
| **`chint-data-analysis`** | `skills/chint-data-analysis/` | **主配电销售数据分析**<br>销售透视、漏斗分析、产品线增长与自动化汇报生成，内置 DuckDB 本地数据仓库。 | 主配电产品线营销数据 |
| **`chint-data-review`** | `skills/chint-data-review/` | **市场数据稽核**<br>跨 Excel、白皮书与竞品数据集核对低压配电 / ACB 市场数字，每个引用数字须可回溯到源页。 | 带源页可追溯性的稽核清单 |
| **`chint-pm-rat`** | `skills/chint-pm-rat/` | **RAT 立项内容整理**<br>按立项表格栏目组织内容，只填产品经理范围（需求背景、产品定义、性能质量、应用场景与痛点、竞品、目标行业、销售通路）；技术 / 生产 / 财务可行性留白交其他部门。输出结构化 Markdown/表格，不绑定 PPT 模板。 | 配电产品线《立项资料编写经验分享》周会方法论（2026-08） |

---

## 🚀 快速安装与使用指南

### 1. 本地项目级安装（支持 Antigravity / Claude Code / Cursor / Copilot）
将技能目录复制到当前项目工作区的 `.agents/skills/` 目录下：

```bash
# 复制品牌设计技能到当前项目
cp -r skills/chint-brand-design /path/to/your-project/.agents/skills/

# 复制翻译技能到当前项目
cp -r skills/chint-translation /path/to/your-project/.agents/skills/

# 复制 PPTX 生成技能到当前项目
cp -r skills/chint-pptx /path/to/your-project/.agents/skills/
```

### 2. 用户级全局安装
将技能部署至 Antigravity / Claude Code 全局技能目录：

```bash
# 部署至 Antigravity 全局技能库
cp -r skills/chint-brand-design ~/.gemini/config/skills/
cp -r skills/chint-translation ~/.gemini/config/skills/
```

> 也可以用 `skills-manager-cli skills deploy` 统一部署，它会维护来源元数据、预设归属与跨 agent 的部署状态，比手工复制更可靠。

---

## 📌 知识库架构说明 (`chint-pptx`)

- `scripts/chint_pptx_engine.py`：演示文稿生成引擎，按 JSON payload 产出可编辑的表格页与原生图表页。
- `scripts/shell_rebuild_engine.py`：保留源内容页的外壳重排引擎，配套源稿保真校验。
- `core/`：测定、规划、渲染三个独立模块，引擎不再单文件承载全部逻辑。
- `spec/brand_tokens.json`：2026 VI 数值的唯一真源；`spec/2026VI.yaml` 存版式几何与测定阈值。
- `references/content_contract.md`：内容页版式契约（`ARCH_TABLE` 与三张原生图表）。
- `references/`：创建/编辑流程、质量与环境检查、源页保留 SOP、资源库指南等。

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

## 📌 知识库架构说明 (`chint-translation`)

- `references/01_universal_iec_parameters.md`：通用 IEC 电气参数定义（$U_e, U_i, U_{imp}, I_n, I_{cu}, I_{cs}, I_{cw}, I_{cm}$, Cat B 等）。
- `references/02_acb_trip_units_and_protection.md`：脱扣器型号与保护曲线（M/A/P/H 型、L/S/I/G/N 保护、ZSI、MCR、热记忆等）。
- `references/03_acb_accessories_and_mechanisms.md`：内外部附件与机构（SHT、UVR、CC/CEM、M/MOE、AX、AL、RTC、钥匙锁等）。
- `references/04_universal_wiring_and_contact_logic.md`：接线与触点逻辑的通用表述。
- `references/05_universal_safety_imperatives.md`：安全提示与警示语的标准译法。
- `references/06_universal_technical_headings_and_claims.md`：样本册标准栏目标题与产品亮点宣传统一表达。
- `references/07_universal_anti_chinglish.md`：中式英语防呆规则与常见错译拦截。
- `references/08_mccb_taxonomy_and_releases.md`：塑壳断路器分类与脱扣单元系列。
- `references/09_mcb_rcbo_curves_and_accessories.md`：微型断路器 / 漏电保护器的脱扣曲线与附件。
- `references/10_ats_classes_and_controllers.md`：双电源转换开关的类别与控制器。
- `references/11_power_quality_and_contactors.md`：电能质量装置（SVG / APF）与接触器术语。
- `references/acb_terminology_master.json`：结构化术语主数据，支持程序化检索。

---

## 📌 贡献与维护规范

- 本仓库专注收录正泰**产品经理（PM）业务可复用**技能与知识库。
- 所有新增技能须遵循 `agentskills.io` 与 `writing-great-skills` 规范，且包含完整 `SKILL.md` 指南与数据校验。
