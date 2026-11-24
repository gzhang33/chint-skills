# CHINT PM Reusable Skills 技能库 (`chint-skills`)

本项目为**正泰电气（CHINT）产品经理（PM）可复用业务技能与领域知识库**集中托管与备份仓库。

宗旨是为正泰海外市场、低压配电及主配电产品线的产品经理提供标准化、高精度、可被 AI Agent 直接调用的业务技能资产（包含样本翻译、产品选型、数据分析、品牌设计规范与竞品对齐等）。

---

## 📦 产品经理可复用技能清单

| 技能名称 | 目录路径 | 业务适用场景与核心能力 | 权威标准 / 业务系统依据 |
|:---|:---|:---|:---|
| **`chint-pptx`** | `skills/chint-pptx/` | **正泰企业级 PPTX 智能演示文稿生成**<br>按 2026 VI 规范生成可编辑的产品演示文稿。内容页收敛为表格契约（`ARCH_TABLE`）加三张原生图表（趋势 / 占比 / 雷达），封面与章节页继承模板版式保持原生可编辑。内置结构合规门禁、开源 OpenXML 校验、源页保真校验与渲染预览链路。 | CHINT 2026 VI 视觉规范指导手册<br>2026 年正泰 PPT 通用基础模板 |
| **`chint-catalog-edit`** | `skills/chint-catalog-edit/` | **正泰全品类低压样本册勘误与阈值门控（v1.1.0 · 三档门控）**<br>面向中英文 PDF / Word / Excel 样本册，提供固化三档阈值与叠加开关：**`L1`（默认，仅严格错误）** 专查单位互倒/交直流错标/技术矛盾、中文错别字语病、图号/页码交叉错印、同页冲突及英文严重错译与竞品代号（排除大小写、跨页统稿、行业习惯词及空格/`℃`/连字符/英美拼写噪声）；**`L2`（发版统稿）** 叠加跨页同物异名与符号/大小写统一；**`L3`（实质国标/IEC 合规）** 与 **`--with-iec`** 叠加 `chint-translation` 的实质条款与法定词偏差核查（永久剔除空格/全半角/`℃`/连字符/英美拼写）。通过 `chint-office-suite`（或同级内置引擎）提取并执行两步确认 PDF 批注交付。 | chint-office-extract/v1<br>chint-office-annotate/v1<br>IEC 60947-2:2024 / GB/T 14048.2—2020 |
| **`chint-translation`** | `skills/chint-translation/` | **B2B 工业品纯双标翻译与术语真源（v1.2.0 · 纯文本 + `1 + 1 + N` 隔离架构）**<br>专注 `ZH→EN`（`IEC 60947-2:2024` Ed. 6.0）与 `EN→ZH`（`GB/T 14048.2—2020` 法定词与条款号，零俗称括号），覆盖 ACB / MCCB 及附录 A–R（CBR / MRCD / CBI / ICB / 1 500 V PV DC / CBAR），支持正泰专属附件代号（`SHT` / `CEM` / `SPC` / `MOD` / `KL` / `DD` 等），内置纯净查词（`glossary_lookup.py`）与实质标准/错译自检（`lint_text.py`）、按需加载版次勘误层（`edition_divergences_and_errata.md`）与 `regions/` 区域扩展槽；全册样本勘误与 PDF 批注请走 `chint-catalog-edit`。 | IEC 60947-2:2024 (Ed. 6.0)<br>IEC 60947-1:2020<br>GB/T 14048.2—2020 |
| **`chint-office-suite`** | `skills/chint-office-suite/` | **正泰通用 Office 文档处理与 PDF 非破坏批注底座（v1.0.1 · 与业务技能完全解耦）**<br>面向 `.pdf` / `.docx` / `.xlsx` 样本与技术文档，提供 `--check-env` 运行时自检、大文档摘要与页码批建议（`--summary`）、统一结构化文本提取（`extract_doc.py` 自动标记低文本量纯视觉 PDF 页）、以及管道直入的统一黄色高亮与全量追加批注（`annotate_pdf.py` 支持逐处精标 `all` 与同页联动合并 `merged`，保留历史批注并仅另存唯一新 PDF 副本，零覆盖原件），内置 UTF-8 跨平台管道硬化与中国大陆镜像（清华源 / 阿里云源）依赖指引，并按文件类型路由协同官方 `pdf` / `docx` / `xlsx` 通用技能与 OCR 技能。 | chint-office-extract/v1<br>chint-office-annotate/v1<br>PyMuPDF / OpenXML / openpyxl |
| **`chint-pm-copywriter`** | `skills/chint-pm-copywriter/` | **B2B 工业品 PM 文案与汇报语法引擎**<br>向上汇报、QBR 复盘、PRD 价值主张与产品样本提炼。内置极简量化三要素、三段式负向建设性语法、黑白名单词典与出稿门禁，杜绝浮夸黑话与战役化暗喻。 | 正泰高管汇报标准<br>B2B 工业品 PM 务实文案规范 |
| **`chint-pm-fabe`** | `skills/chint-pm-fabe/` | **产品卖点 FAB 润色**<br>按 FAB 最佳实践将技术参数或结构设计润色为**结构化价值主张卡片式**（4字短标 + `Feature（特性）/ Advantage（优势）/ Benefit（利益）` 分层短点 + ≥3张卡总览表）或**一句式卖点**（特征 + 量化优势 + 客户利益）。F 段将白话升维为高阶工程术语，A 段集中展示参数与对比/后果量化，B 段收敛为成本、工时、停机、用量/占地、风险/资格五类客户价值，并静默规范单位（`kA` / `ms` / `μs`）与术语；专注文案润色，不输出待确认清单等额外审查项。 | ACB / MCCB / SSCB / ATS 技术参数表<br>IEC 60947 术语与单位规范 |
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

### 3. 团队新机双平台快速部署（macOS + Windows · 均支持单装独立运行，也可组合使用）

1. **按需单装或整套安装**（`chint-catalog-edit`、`chint-translation`、`chint-office-suite` 均已具备完整独立 SOP 与内置引擎，可单独安装运行；同装时自动协同零重复真源）：
   ```bash
   # 方式 A：单独安装并部署任意一个（以 chint-catalog-edit 为例）
   skills-manager-cli skills install https://github.com/gzhang33/chint-skills/tree/main/skills/chint-catalog-edit
   skills-manager-cli skills deploy chint-catalog-edit --agent antigravity

   # 方式 B：成套安装并部署三件套
   for s in chint-catalog-edit chint-translation chint-office-suite; do
     skills-manager-cli skills install "https://github.com/gzhang33/chint-skills/tree/main/skills/$s"
     skills-manager-cli skills deploy "$s" --agent antigravity
   done
   ```
2. **运行时自检**（macOS/Linux 用 `python3`，Windows 用 `python` 或 `py -3`）：
   ```bash
   python3 skills/chint-catalog-edit/scripts/audit_catalog.py --check-env
   # 若单独使用 chint-office-suite：
   python3 skills/chint-office-suite/scripts/extract_doc.py --check-env
   ```
3. **中国大陆 PyPI 镜像补装依赖**（处理 `.pdf` / `.xlsx` 时若缺失 `pymupdf` 或 `openpyxl`，优先清华源，失败切阿里云源）：
   ```bash
   # 清华源（首选，chint-catalog-edit 与 chint-office-suite 共用相同 requirements.txt）
   python3 -m pip install --user --timeout 30 -r skills/chint-catalog-edit/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
   # 阿里云源（备选，Windows 将 python3 替换为 python 或 py -3）
   python3 -m pip install --user --timeout 30 -r skills/chint-catalog-edit/requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
   ```

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

## 📌 知识库架构说明 (`chint-catalog-edit` · v1.1.0 独立/协同双模样本勘误与阈值门控)

- `SKILL.md` & `requirements.txt`：完全独立的三步阈值审校 + 确认后批注交接 SOP（`L1` 默认仅严格错误、`L2` 发版统稿、`L3` 实质国标/IEC 合规及 `--with-iec`），支持 `.pdf` / `.docx` / `.xlsx` / 纯文本直入与 `--check-env` 运行时自检。
- `scripts/audit_catalog.py`（**独立内置引擎 + 单向同级联动**）：优先委托同级 `chint-office-suite`（提取/批注）与 `chint-translation`（术语规则真源）；单装环境下自动启用内置 `.pdf`/`.docx`/`.xlsx` 提取器、与 `annotate_pdf.py` 同等全词边界/短代号大小写/跨行折词/旋转页保护的 PyMuPDF 批注器（`--write-pdf`）及对等校验的内置标准兜底表；全仓一致性由 `scripts/verify_doc_skills.py` 硬门禁锁死。
- `references/semantic_checklist.md` & `references/pdf_annotation_handoff.md`：纯语义/版面/视觉页核对清单与两步确认 PDF 批注流程。

---

## 📌 知识库架构说明 (`chint-translation` · v1.2.0 纯文本双标 `1 + 1 + N` 架构)

- `SKILL.md`（**三步翻译与术语真源工作流**）：双标法定词铁律（`IEC 60947-2:2024` ⟷ `GB/T 14048.2—2020`，零俗称括号）、相对技能根目录路径解析；专注翻译与术语校验，全册样本勘误与 PDF 批注统一路由至 `chint-catalog-edit`。
- `scripts/glossary_lookup.py`（**纯标准库 SSOT 词表与换算锁定器**）：反引号感知切表并精准识别缩写代号列，输出零括号纯中文目标词，区分 IEC 2024 跨版缺口（`gb_missing=True`）与 CHINT/行业扩展，支持分块、LaTeX 完整清洗与 `万次` 区间/去重换算。
- `scripts/lint_text.py`（**纯标准库实质翻译自检器**）：仅校验实质错译黑名单、竞品代号、技术矛盾（A 类配 `Isd` 未声明 `Icw`、60947-2 下标 `Type F/B+`）、已废止 Ed. 5 条款、法定中文偏差（豁免 `使用类别 AC-22` 等合法项）与未填槽位；已移除空格/全半角/`℃`/连字符/英美拼写提示。
- `references/iec_60947_2_standard.md` + `iec_annexes.md` + `audit_blacklist.md` + `edition_divergences_and_errata.md`（**分层渐进披露参考层**）：精简主表与附录 A–R、错译黑名单及按需下沉的版次勘误层。
- `references/departments/acb.md` / `mccb.md` / `_template.md`（**`N` 部门隔离词库**）：专责 ACB / MCCB 术语与正泰专属附件代号，零硬编码私人本地路径。
- `references/regions/_region_template.md`（**国家/区域合规隔离模板**）：预留独立 `regions/` 扩展位，仅加载具体国家覆写文件。

---

## 📌 知识库架构说明 (`chint-office-suite` · v1.0.1 通用 Office 底座)

- `SKILL.md` & `requirements.txt`：`.pdf` / `.docx` / `.xlsx` 路由门禁（Step 1）、独立提取（Branch A）/ 非破坏 PDF 批注（Branch B）分支、macOS/Windows 执行命令与清华/阿里云 PyPI 镜像补装指引。
- `scripts/extract_doc.py`：支持 `--check-env` 运行时自检、`--summary`、严格 `--pages` 校验、`.pdf` `<50` 字符视觉页识别、`.docx` 制表符/换行保真与文本框去重，以及 `.xlsx` 未缓存公式格警告（`uncached_formula_cells`）。
- `scripts/annotate_pdf.py`：通过 `--annotations -` 零磁盘管道消费 `chint-office-annotate/v1` JSON，采用词边界与短代号大小写保护、跨行词组多框归并及页边距便签限位，保留历史批注并仅另存唯一新 PDF 副本。

---

## 📌 贡献与维护规范

- 本仓库专注收录正泰**产品经理（PM）业务可复用**技能与知识库。
- 所有新增技能须遵循 `agentskills.io` 与 `writing-great-skills` 规范，且包含完整 `SKILL.md` 指南与数据校验。
