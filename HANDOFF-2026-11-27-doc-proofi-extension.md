# HANDOFF — chint-catalog-edit → chint-doc-proofi 扩展（2026-11-27）

> 状态：**T1–T8 全部完成**（含 T5 领域规则渐进式披露重构）。执行结果与门禁状态见 §9–§11。
> 基准：`resources/chint-skills` 工作树当前状态（含本日已完成的审计修复，未提交）。
> 代码入口：`skills/chint-doc-proofi/scripts/audit_catalog.py`。

---

## 1. 一句话目标

把「正泰样本册勘误」扩展为「通用办公文档校对」，**并入同一个 skill 并重命名**为 `chint-doc-proofi`，
维持单目录可打包迁移、零本地共享模块、零新增重依赖。

## 2. 用户已确认的决策（不得再议）

| 决策点 | 结论 |
|:---|:---|
| 形态 | **就地扩展现有 skill 并重命名**，不新建兄弟 skill |
| 新名称 | **`chint-doc-proofi`**（原 `chint-catalog-edit` 被替换，不保留别名壳） |
| 新增格式 | **pptx、md/txt、doc/xls（旧版二进制）** |
| 旧版二进制策略 | **内置尽力提取**（OLE2 解析），不调用外部工具，不要求用户先转换 |
| 规则集 | **统一规则集**，不按文档类型分流 |
| 共享模块 | **禁止** `shared/` 等跨 skill 模块；单目录必须自包含 |
| 依赖 | 维持 `pymupdf` + `openpyxl`；pptx 用纯标准库 `zipfile`+`xml.etree`；OLE2 用纯标准库 |

## 3. 现状基线

### 3.1 已支持的格式
`.pdf` / `.docx` / `.xlsx` / `.xlsm` / `.txt`（含 JSON 结构化提取输入 `chint-office-extract/v1`）。
`.doc` / `.xls` 当前**直接抛错**要求转换。

### 3.2 目录体积
348 KB，其中 `scripts/` 296 KB、`references/` 28 KB、`evals/` 8 KB。单目录自包含，可整体迁移。

### 3.3 已知重复
与 `chint-office-suite` 约 18 KB 近似副本（10 个函数），与 `chint-translation` 3 个小函数。
**用户要求保留单装独立性，因此不合并**；待办见 §4 任务 T7（把漂移变成可检测）。

### 3.4 检测器现状（2026-11-27 四路审计后）
10/10 自测通过，6 道仓库门禁通过。真实语料：NXA 3 条、ABB Emax 5 条、施耐德 MVS 2 条、FQK 5 条。

## 4. 任务清单

按依赖顺序执行。每个任务独立可验证，前置条件不满足时停下报告。

### T1 — 重命名与引用同步
- `git mv skills/chint-catalog-edit skills/chint-doc-proofi`
- 同步修改：`SKILL.md` frontmatter `name:`、`skill.meta.yaml`、`evals/evals.json` 的 `skill_name` 与 prompt 文本、
  `scripts/verify_doc_skills.py` 的 `CAT_DIR`、仓库根 `README.md`、
  `/Users/gianni/Documents/chint/AGENTS.md` 技能路由表、`chint-translation/SKILL.md` 中的转介句。
- 验证：`rtk grep -rn "chint-catalog-edit" resources/chint-skills` 仅剩 `.git/` 历史；6 道门禁全过。

### T2 — pptx 支持（纯标准库）
- 新增 `_extract_pptx_builtin(path)`：`zipfile` 读 `ppt/slides/slideN.xml`，
  按 `<a:t>` 提取文本 run，按 `<a:p>` 聚合成段，`<a:br>` 转行。
- 定位格式：`S<slide>:T<shape-index>:P<para>`，保证能回溯到具体文本框。
- 需要处理：XML 实体反转义（`&amp;` → `&`）、`<a:tab>`、组合形状递归、备注页可选跳过。
- 验证：用 `Archives/产品介绍pptx/` 下真实文件，抽取文本非空、行数与 PowerPoint 目视一致。

### T3 — md / txt 强化
- 现有 `.txt` 分支已可用；补 `.md`：提取时**跳过代码块**（``` 围栏）与行内代码（反引号），
  避免把 URL、标识符当正文报错。
- 保留标题层级信息到定位（`M<line>` 即可，不解析结构）。
- 验证：`.md` 文件里的 ``` 围栏内 `海拨` 不报错；围栏外报错。

### T4 — .doc / .xls 内置尽力提取（OLE2）
- 新增 `_ole2.py` 风格的最小实现（**放在 `scripts/` 内，不建共享目录**）：
  - 解析 OLE2 复合文档头（512B header，`0xE11AB1A1` magic）、FAT/MiniFAT、目录项。
  - `.doc`：定位 `WordDocument` 流，读 FIB 取文本片段表（CLX），提取正文；必要时回退到裸片段扫描。
  - `.xls`：定位 `Workbook` 流，解析 BIFF8 记录（`LABELSST`/`NUMBER`/`RK`/`SST`），逐行输出。
- **硬性要求**：解析失败必须给出明确错误（`无法解析 .doc，建议转存 .docx`），
  不得静默返回空文本后报「0 错误」——这正是本轮已修掉的盲审问题。
- 定位格式：`.doc` 用 `D<段落序号>`，`.xls` 用 `X<sheet>:R<row>`。
- 验证：仓库内 2 个 `.doc` + 9 个 `.xls` 全部能提取出非空文本；无法解析的必须报错而非静默。

### T5 — 文档类型无关的规则复核
统一规则集意味着通用文档也会跑电气规则。需要确认**不产生致命噪声**：
- 对 3 类通用文档（会议纪要 md、产品介绍 pptx、报价 xlsx）各跑一次 L1，
  逐条核对命中是否为真问题（如标点/错字/重复词应真，IEC 术语应少）。
- 若噪声不可接受，**不改规则集**（用户已定统一），而是把电气类规则的命中降到 L2 级，
  并在报告里单列「领域规则」分节。此项产出报告由用户裁定，不自行改分级。

### T6 — 文档类型自动识别与报告标注
- `load_units` 返回值补 `doc_type`（`catalogue` / `office-generic` / `markdown` / `legacy-binary`）。
- 报告头部与 JSON 输出标注文档类型，便于用户判断该看哪些命中。

### T7 — 把跨 skill 漂移变成可检测（替代合并）
- 在 `scripts/verify_doc_skills.py` 增加 gate：对 10 个已知复制函数做 AST 归一化后比对哈希。
- 任一侧被单独修改即门禁失败，提示"同步另一侧或登记为有意分叉"。
- **不合并代码**，仅加检测。这是用户「保持单装独立」前提下的唯一可行方案。

### T8 — 文档与版本
- `SKILL.md` 重写描述（通用办公文档校对 + 样本册专精），三段式流程保持。
- `README.md` 技能表更新。
- 版本号升至 `2.0.0`（不兼容变更：目录名变更）。
- `references/semantic_checklist.md` 增补通用文档条目。

## 5. 约束与红线

1. **禁止新建跨 skill 共享模块**。所有代码在 `skills/chint-doc-proofi/` 内。
2. **禁止新增重依赖**。pptx 与 OLE2 必须纯标准库；`python-docx`/`python-pptx`/`olefile` 一律不引入。
3. **禁止静默失败**。任何格式解析不出文本时必须报错并给出可执行建议，不得输出「0 错误」。
4. **禁止覆盖原文件**。批注仍只写新副本；通用文档格式（pptx/xlsx/doc）**本轮不支持回写批注**，
   只出勘误表 —— 回写需要 Office 写库，与零依赖冲突。
5. 遵守仓库 `AGENTS.md` 事实红线：每个数字可溯源，缺来源留空进「待确认清单」。
6. 交付前跑 `python3 System/仓库脚本/scripts/check_repo_rules.py --quiet`，ERROR 必须为零
   （现有 17 条预存 ERROR 与本次无关，不计入）。

## 6. 进度表（执行方回写）

| 任务 | 状态 | 验证证据 | 备注 |
|:---|:---|:---|:---|
| T1 重命名 | 完成 | 目录与全部引用已改名；`rtk grep -rn "chint-catalog-edit"` 全仓仅剩本 HANDOFF 的历史叙述与 `.git/`；`AGENTS.md` 技能路由表与 `chint-translation/SKILL.md` 转介句均指向 `chint-doc-proofi`；门禁通过 | 未保留别名壳 |
| T2 pptx | 完成 | 自测 13/13（suite 11 覆盖数字序、grpSp 递归、a:br、实体反转义、备注页排除、盲审信号）；真实文件：`NXA系列产品培训_cn_v3.pptx` 23 页 1122 units，`虚拟工厂月报_模版.pptx` 9 页 812 units（第 8 页无文字进 low_text_pages），`正泰框架产品介绍.pptx` 127 页 2813 units | 纯 stdlib；定位 `S<slide>:T<shape>:P<para>`，不匹配 `^P\d+:`，按约定归入文档域 `__all__` 块 |
| T3 md/txt | 完成 | 自测 suite 12：围栏（``` 与 ~~~）与行内代码不参与扫描，`M<line>` 定位，全围栏文件 units=[] 且 low_text_pages 为空 | 仅 `.md` 走新逻辑，`.txt` 保持 `Line <n>` |
| T4 doc/xls | 完成 | 11 个真实文件（2 个 `.doc` + 9 个 `.xls`）在实测期全部提取非空；后续根仓 `1e234fe` 启用全量 LFS 指针后，未检出文件已加 Git LFS 指针识别，损坏文件退出码 2 并给出「无法解析 .doc…另存为 .docx」 | OLE2 内联在 audit_catalog.py，未新建 `_ole2.py`（`-I` 下脚本目录不在 sys.path） |
| T5 噪声复核 | 完成 | 真实语料 L1 实测：`虚拟工厂月报_模版.pptx`（office-generic，812 units）0 命中；`报价测算-刘洋 (3).xlsx`（office-generic，555 units）0 命中；`26年Q3制造部会议-框架.pptx`（office-generic，2243 units）2 命中且均为真错（第 10 页「业务业务」、第 17 页「研究与开发研究与开发」，已回读原 XML 确认）；`26年Q3制造部会议-塑壳.pptx`（1948 units）1 命中且为真错（第 12 页「终端终端」）；`NX…重点产品展示.pptx`（66 units）与 `NX…培训_cn_v3.pptx`（catalogue）0 命中；真实 `.md` 两份（179 / 22 units）0 命中 | 完成：采用渐进式披露，领域规则迁出 `SKILL.md`，按需路由至 `references/domains/electrical_catalogue.md` 与 `office_generic.md`，并移除原 `semantic_checklist.md` |
| T6 类型标注 | 完成 | `load_units` / `_extract_office_builtin` 均带 `doc_type`；`--summary`、`--json`、`--chunks-info` 与非 JSON 汇总行均已展示；实测 `NX…培训_cn_v3.pptx` = catalogue，`虚拟工厂月报_模版.pptx` = office-generic，`报价测算-刘洋 (3).xlsx` = office-generic，`.md` = markdown，`.doc`/`.xls` = legacy-binary | 按内容判定（前 400 units 内 ≥2 个不同电气信号），不看文件名 |
| T7 漂移门禁 | 完成 | 7/7 门禁通过；扰动 `_chars_in_rect` 后 gate 7 报错，还原后复绿 | gate 7 比对 4 对文件、35 个共有函数 |
| T8 文档版本 | 完成 | `SKILL.md` 重写（65 行）；`semantic_checklist.md` 增补第 5 节通用文档条目；`skill.meta.yaml` 与 `evals/evals.json` 升至 `2.0.0`，新增 eval 4–7；`README.md` 更新；`verify_doc_skills.py` Gate 5 期望值已提至 `2.0.0`，7/7 全绿 | 与 §9 一致；Gate 6 现已覆盖全部 12 条 eval（含 eval 4–7） |

## 7. 复现命令

```bash
cd /Users/gianni/Documents/chint
# 自测
uv run --quiet --with pymupdf --python 3.12 python3 -I \
  resources/chint-skills/skills/chint-doc-proofi/scripts/audit_catalog.py --self-test
# 七道门禁
cd resources/chint-skills && uv run --quiet --with pymupdf --with openpyxl --python 3.12 \
  python3 -I scripts/verify_doc_skills.py
```

## 8. 已知遗留（不在本轮范围）

- PDF 印刷页码与物理页序不一致，交叉引用检测只做提示不断言。
- `.xlsx`/pptx/doc/xls 不支持批注回写。
- 表格检查仅覆盖 `Ics > Icu`，`In ≤ Inm` 的表格版未实现。
- 仓库根 `CLAUDE.md` / `agent.md` 处于 git 删除状态（预存问题，非本 skill 职责）。

---

## 9. 执行结果（2026-11-27）

**已交付**

- 重命名 `chint-catalog-edit` → `chint-doc-proofi`，全部引用（README、AGENTS.md 路由表、`chint-translation` 转介句、门禁 `CAT_DIR`）同步，无别名壳。
- 新增三种提取路径，全部纯标准库：`.pptx`（`S<slide>:T<shape>:P<para>`）、`.md`（围栏与行内代码跳过，`M<line>`）、旧版 `.doc`/`.xls`（内联 OLE2，`D<n>` / `X<sheet>:R<row>`）。无法解析时退出码 2 并给出转存建议，不产生空文本「0 错误」。
- `doc_type` 五值分类（`catalogue` / `office-generic` / `markdown` / `legacy-binary` / `text`），在 `--summary`、`--json`、`--chunks-info` 与汇总行展示。
- 汇总行改为 `Scanned <scanned>/<total> containers, <N> text units`，容器数与文本单元数分列，消除 23 页 deck 显示为 23 行审校的误读。
- gate 7 跨 skill 漂移检测上线：AST 归一化哈希 + `DUP_PAIRS` 白名单（`in-sync` / `intentional-divergence:<reason>`），4 对文件、35 个共有函数纳入。
- 文档与版本：SKILL.md 重写、semantic_checklist 增补通用文档分节、`2.0.0` 版本同步、两份新 eval（pptx 定位、旧版二进制硬报错）。

**门禁状态**

- 7 道门禁全绿；自测 13/13；隔离副本（复制出仓后单独运行）自测同样 13/13。
- gate 5 的 `CAT_DIR` 期望值已提至 `2.0.0`，与 `skill.meta.yaml` / `evals.json` 一致。

**审查修复（skill-creator 最佳实践审查后）**

| 问题 | 处理 |
|:---|:---|
| `、灌` 规则在「润滑油、灌装」「注入、灌入容器」等正常中文上产生 L1 误报 | 收紧为 `灌(?<!入)(?:等)?容器`；真阳性「池、桶、槽、灌等容器」仍命中 |
| eval 2 声明 L1 却断言 L2 才有的术语命中，gate 6 用 L2 绕过矛盾 | eval 2 改为 L2，新增 c3 断言 L1 抑制方向；gate 6 改双向校验（L1 抑制 Closed electromagnet/Shunt Trip，保留 XF/MX/Earch） |
| 空 `.docx` / `.xlsx` 退出 0 报「0 错误」 | 纳入 blind-pass：`not units and format in {docx,xlsx,xlsm}` → 退出 2；错误消息按格式区分，不再对 docx 说「0 of 0 page(s)」 |
| `sources.md` 称「无 2900.18 backlink」「每条 fix 均引 GB/T 14048.2 条款」 | 两者均为假：补 GB/T 2900.18 行，改写为「多数引条款，`单极极限` 无条款、`隔离开关` 引 60947-3」 |
| `“黑色“` 引号规则错引 GB/T 15834 4.9（4.9 是括号） | 改为 4.8，并在 sources.md 补 4.8 行 |
| 《现代汉语词典》×3 与《通用规范汉字表》未在 sources.md 登记 | §1 补两行 |
| eval 6 无 fixture，路径 `/tmp/legacy/…` 不存在 | 新增 `evals/files/corrupt_ole2.doc` / `.xls`（200 字节错魔数），实测退出 2 并给出预期错误 |
| 无 md eval | 新增 eval 7「围栏与行内代码豁免」，实测围栏内 `海拨`/`63~32A` 与行内 `海拨` 均不报，正文报 1 条 |
| `0664` 子串抑制过宽 | 收紧为 `\b(?:VDE\s*)?0664` |
| 自测因本机 `~/.skills-manager` 旧版兄弟技能而失败 | 自测仅在兄弟技能位于同一 checkout 时做 parity 断言；同仓 parity 由 gate 2 负责 |

**未做 / 延后**

- 非 PDF 格式批注回写（需 Office 写库，违背零依赖约束）：`.pptx`/`.xlsx`/`.doc`/`.xls` 只出勘误表；`--write-pdf` 对非 PDF 输入直接报错，`--emit-annotate` 丢弃非 `P<n>:` 定位并给出 stderr 警告。
- T5 的「领域规则」独立分节：实测未达必要门槛，未实施。
- `.doc`/`.xls` 解析为尽力而为，复杂加密或异常分片可能提取不全；只承诺「解析失败必报错」，不承诺全量还原。
- **本机部署副本过期**：`~/.claude/skills/chint-catalog-edit`（旧名）与 `~/.skills-manager/skills/chint-translation`（`ED5_GUARD_TAGS` 少 2 项）均落后于仓库。`skills-manager-cli` 数据库 schema 版本 9 > 本机 CLI 支持的 8，无法直接重装，需升级 CLI 或手动替换后再 deploy。

---

## 10. 2026-11-28 二次核查修复增补

- **L2 规则修复**（`references/catalog_rules.json`）：修复 `cos φ` 自报误报（合法 `cos φ` / `cos ϕ` 不再触发，错写 `COSΦ`/`Cos φ`/`cos Φ` 照常命中）；修复汉字「一」作范围号规则写反（从 `(?<!\d)` 改为 `(?<=\d)`，命中 `16 一 63A`，不再误报 `第一 2 项`）。
- **竞品代号抑制收紧与开关化**（`audit_catalog.py` + `sources.md`）：新增 `--external-reference`；自动抑制改为需同时满足「前 400 units 无正泰标识且命中 ≥3 次同行品牌」才关闭 `COMPETITOR_CODE`，消除正泰样本提一句友商即静音整册的隐患，并同步 `sources.md`。
- **Git LFS 指针守卫**（`audit_catalog.py`）：对未检出的 Git LFS 指针文件直接报错退出码 2 并提示执行 `git lfs pull / checkout`，避免误报为文件损坏。
- **Gate 6 扩展**：`scripts/verify_doc_skills.py` 现覆盖 `chint-doc-proofi` 全部 8 条 eval（合计 12 条冒烟检查），T5 实测记录同步 `26年Q3制造部会议-塑壳.pptx`（1 命中「终端终端」）。

---

## 11. 领域规则渐进式披露重构（2026-11-28）

- **SKILL.md 瘦身**：抽离电气样本册与通用办公领域规则及语义核对细节，`SKILL.md` 仅保留领域无关三步工作流、输入定位契约、安全红线与按需路由指针。
- **领域参考分层（`references/domains/`）**：
  - `electrical_catalogue.md`：收拢 `catalog_rules.json` 与通用检测分工、同行历史译法 `L2` 降级、竞品代号 `--external-reference`、PDF 额定参数表门控、`--with-iec` / `L3` 合规叠加及样本册语义/版面清单，并修正移除对 `IEC 60050-441` 的不实提及。
  - `office_generic.md`：收拢非样本册文档域内命中甄别原则、`.pptx`/`.md`/`.doc`/`.xls` 提取与交付边界，以及通用办公语义清单（明确排除不适用的样本册版面规则）。
- **单源清理**：删除原 `references/semantic_checklist.md`，同步更新 `README.md`。
- **双路 `$skill-creator` 审查与闭环修补（结果：`PASS_WITH_FINDINGS` → 已全部清零）**：
  - 修复 `--report-md` 漏印 `doc_type=`/`office=`/`ssot=` 摘要行与 `chint-office-extract/v1` JSON 误判为 `text` 的脚本缺陷，并补齐 `--self-test` 回归断言（仅改动 `verify_doc_skills.py` Gate 7 已登记为 `intentional-divergence` 的函数，零影响同级函数对等）。
  - 区分主题域与容器格式：补充内联文本暂存 `/tmp` 规范、对齐 `Coverage Ledger` 6 列格式、在 `SKILL.md` `description` 补齐英文通用办公触发词。
  - 修正在 `electrical_catalogue.md` 与 `sources.md` 中关于 `--dept mccb` 误抑制竞品码的不实描述、补齐 `Shunt Trip` / `(CEM)`/`(SHT)`/`(ECT)` / `功率损耗 -> 功耗` / `Uimp` 词表、清理 `office_generic.md` 重复句及 `sources.md`/`pdf_annotation_handoff.md` 过期引用。
  - 对齐 `$skill-creator` `schemas.md` 将 `evals/evals.json` `assertions` 统一为 `expectations`，补齐 Eval 3（`standalone_sample.pdf`）、Eval 5（`product_brief.pptx`）、Eval 7（`notes.md`）真实夹具并修正 Eval 2 提示与预期对齐。
