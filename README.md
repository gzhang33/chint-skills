# CHINT PM Reusable Skills 技能库 (`chint-skills`)

正泰电器（CHINT）产品经理（PM）可复用业务技能库，同时作为 Claude Code / Cowork 的插件市场（marketplace）发布。

8 个技能按用途分入 4 个插件，安装一个插件即获得该组全部技能。

---

## 🧩 插件分组

| 插件 | 包含技能 | 适用场景 |
|:---|:---|:---|
| **`chint-deck`** | `chint-pptx`、`chint-pm-rat`、`archify` | 产品 PPT 生成与改造、立项内容整理、架构/工作流/时序图 |
| **`chint-copy`** | `chint-pm-copywriter`、`chint-translation` | PM 文案与高管汇报语法、低压电器中英技术翻译 |
| **`chint-data`** | `chint-data-review` | 市场数据口径法证审查与逐项溯源 |
| **`chint-ops`** | `chint-brand-design` | 品牌 VI 规范与设计 Token |

---

## 🚀 安装

### Claude Code 插件方式（推荐）

```bash
claude plugin marketplace add gzhang33/chint-skills
claude plugin install chint-deck@chint-skills
```

`chint-copy` / `chint-data` / `chint-ops` 按需替换最后一条命令。

### 其他 Agent（项目级 / 全局目录）

```bash
# 项目级：复制到工作区 .agents/skills/
cp -r skills/chint-pptx /path/to/your-project/.agents/skills/

# 全局：复制到各 agent 的技能目录
cp -r skills/chint-pptx ~/.claude/skills/
```

---

## 📦 技能清单

| 技能 | 目录 | 核心能力 |
|:---|:---|:---|
| **`chint-pptx`** | `skills/chint-pptx/` | 基于 2026 版模版与 CHINTinno 字体的可编辑 PPT 生成/改造，含源页保真门禁与环境自检。 |
| **`chint-pm-rat`** | `skills/chint-pm-rat/` | 立项资料（RAT）产品经理范围内容整理，输出结构化内容，不绑定版式。模板填充链路归档于 `archive/`。 |
| **`archify`** | `skills/archify/` | 架构 / 工作流 / 时序 / 数据流 / 生命周期图，自包含 HTML+SVG，正泰 VI 配色。 |
| **`chint-pm-copywriter`** | `skills/chint-pm-copywriter/` | B2B 工业品 PM 文案与高管汇报语法：量化三要素、三段式建设性语法、出稿门禁。 |
| **`chint-translation`** | `skills/chint-translation/` | 低压电器「三断一接」、ATS、电能质量、固态开关的中英技术翻译与防呆词库。 |
| **`chint-data-review`** | `skills/chint-data-review/` | 跨 Excel / 白皮书 / 竞品数据的法证级口径核对，逐项可追溯到页码。 |
| **`chint-data-visual`** | `skills/chint-data-visual/` | **未启用，未从插件暴露**：依赖脚本与模板已从本机移除，技能只保留恢复前提说明。 |
| **`chint-brand-design`** | `skills/chint-brand-design/` | 2026 VI Token、CHINTinno 字体、配色与版式规范；品牌校验脚本。仅提供品牌指引，不生成 PPT。 |

---

## 📌 目录结构

```text
chint-skills/
├── .claude-plugin/marketplace.json   # 插件市场清单
├── plugins/<plugin>/
│   ├── .claude-plugin/plugin.json    # 插件清单（显式声明 skills）
│   └── skills/<skill> -> ../../../skills/<skill>   # 符号链接，单一真源
└── skills/<skill>/                    # 技能实体，SKILL.md + references/ + scripts/ + assets/
```

技能实体只在 `skills/` 维护一份；`plugins/` 下的符号链接由插件清单显式列出。安装时 Claude Code 会把链接解引用为实体目录。

---

## 📌 贡献与维护规范

- 本仓库专注收录正泰**产品经理（PM）业务可复用**技能与知识库。
- 新增技能须遵循 `skill-creator` 最佳实践：描述精确可判别、正文精简、细节下沉 `references/`、脚本可执行。
- 新增技能后必须：在 `plugins/<组>/skills/` 建符号链接 → 在对应 `plugin.json` 的 `skills` 数组登记 → 更新本 README 与 `marketplace.json`。
- 提交前对每个插件执行 `claude plugin validate plugins/<plugin>`。
