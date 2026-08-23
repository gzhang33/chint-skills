# CHINT AI Agent Skills 技能库 (`chint-skills`)

本项目为**正泰电气（CHINT）AI Agent 专属技能与领域知识库**集中备份与分发仓库，旨在为各类智能体（Antigravity、Claude Code、Cursor、Copilot 等）提供结构化、高精度、符合国际标准与正泰产品业务规范的技能资产。

---

## 📦 核心技能清单

| 技能名称 | 目录路径 | 适用场景与核心能力 | 依据标准 / 业务系统 |
|:---|:---|:---|:---|
| **`chint-acb-translation`** | `skills/chint-acb-translation/` | **正泰万能式断路器（ACB）海外样本与技术翻译**<br>包含 8 大分域知识库（产品名称、电气参数、脱扣器与智能控制器、内外部附件机构、安装接线与结构、环境与标准、样本高频句式、翻译禁忌词库）及 88 组全量元数据 JSON。 | IEC 60947-2 (2024)<br>GB/T 14048.2 (2020)<br>UL 1066 / IEEE C37.13 |
| **`chint-data-analysis`** | `skills/chint-data-analysis/` | **正泰主配电销售数据与业务智能分析**<br>支持多维数据透视、销售漏斗分析、行业竞品对比及自动化报表生成。 | 正泰营销与主配电产品线 |
| **`chint-feishu-drive-sync`** | `skills/chint-feishu-drive-sync/` | **正泰飞书云盘自动同步与资产分发**<br>自动化大文件、样本 PDF 与工程数据云端同步。 | 飞书开放平台开放接口 |
| **`chint-git-lfs-sync`** | `skills/chint-git-lfs-sync/` | **大型二进制工程文件 Git LFS 同步管理**<br>解决大型 CAD、PDF 样本与 PPT 资源版本管理。 | Git LFS 规范 |

---

## 🚀 快速安装与使用指南

### 1. 本地项目安装（项目级）
将对应技能目录复制到本地项目工作区的 `.agents/skills/` 目录下：

```bash
# 复制断路器翻译技能到当前项目
cp -r skills/chint-acb-translation /path/to/your-project/.agents/skills/
```

### 2. 全局安装（用户级）
将技能部署至 Antigravity / Claude Code 全局技能目录：

```bash
# 部署至 Antigravity 全局目录
cp -r skills/chint-acb-translation ~/.gemini/config/skills/
```

---

## 🛠️ 知识库分域说明 (`chint-acb-translation`)

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

## 📌 版本与维护规范

- 统一遵循 [agents.md](https://agents.md) 及 `agentskills.io` 开放标准规范。
- 所有技能更新必须经过测试验证后方可提交主分支。
