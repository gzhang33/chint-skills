---
name: chint-rat-one-pager
description: Use when 需要编写或生成立项资料 / 立项一页纸 PPT（RAT、IRT 立项评审、产品开发立项、项目立项汇报、新产品立项 pptx），或用户给出项目简报/调研材料并要求产出立项资料时。覆盖立项看板版式复刻与立项内容方法论（数字化、痛点对应、交叉验证、风险预案）。
---

# CHINT 立项资料一页纸生成（chint-rat-one-pager）

## Overview

产出一页纸立项看板 .pptx（16:9，12 分区，复刻 NXA 系列立项样板）+ 附录A 风险预案 + 附录B 销售预测交叉验证。

**核心分工**：版式由 `scripts/generate_one_pager.py` 保证，你只负责内容质量——把用户材料转化为合格的内容规格（spec JSON），并用校验器证明它合格。

## 文件

| 文件 | 用途 |
|---|---|
| `references/spec-schema.md` | spec JSON 每个槽位的定义与示例（**先读这个**） |
| `references/zone-spec.md` | 12 分区坐标/字号/样式规范 |
| `references/content-methodology.md` | 六条内容红线 + 领导常问六问自检 |
| `scripts/generate_one_pager.py` | spec.json → out.pptx |
| `scripts/validate_one_pager.py` | 校验器，PASS 才可交付 |
| `examples/nxm_spec.json` | 完整合格示例（含部分可行+预案+交叉验证） |

## 工作流（按序执行，不可跳步）

1. **读** `references/spec-schema.md`（含必填槽位清单）。
2. **填 spec**：从用户材料抽取内容逐槽位填写。每个槽位必填：
   - 数字拿不到 → 先向用户要一次；仍没有 → 填 `"待XX确认"` 占位，**禁止编造数字，禁止删槽位**。
   - 频率检查：痛点每条要有"要求值 vs 现有值"。
3. **条件规则**（可观察谓词，逐条判断）：
   - `technical_feasibility.verdict` ≠ `可行` → `risks` 必填（四要素：风险/影响/预案/资源诉求）+ `conditional_approval` 必填。
   - spec 含销售预测 → `cross_validation` 必填；行业数据拿不到 → steps 写可推算部分，`数据来源` 标 `"待补充（行业协会/盘厂调研）"`。
   - `verdict` 只允许 `可行` / `部分可行` / `不可行`，禁止"基本可行"等模糊词。
4. **生成**：`python3 scripts/generate_one_pager.py spec.json out.pptx`
5. **校验**：`python3 scripts/validate_one_pager.py out.pptx --spec spec.json` → 必须 `== PASS`；FAIL 逐条修复后重跑。PASS 后如仍有 WARN，逐条给出处理方式（占位并写入附录A / 待确认清单 / 解释口径），**禁止静默交付带 WARN 的文件**。
6. **目检**：`soffice --headless --convert-to pdf` + `pdftoppm -png -r 90` 渲染，检查文字溢出/重叠/截断。
7. **六问自检**：逐条回答 `content-methodology.md` 的领导常问六问；答不上的回改 spec。
8. **交付**：给可点击文件链接，并列出所有"待确认"占位字段清单。

## 交付前红线速查

| 红线 | 判据 |
|---|---|
| 数字化 | 痛点/收益/成本无数字 → 退回 |
| 痛点↔性能一一对应 | `客户痛点` 条数 ≤ `性能参数` 条数，逐条可对 |
| 交叉验证 | 有预测必须有附录B + 数据来源 |
| 风险附预案 | 非"可行"必须有附录A，预案含量化措施 |
| 可行性如实 | 不满足就写"部分可行"+暂不满足项 |
| 平台命名 | 只允许 昆仑/新锐/诺雅克 |

## Common Mistakes（来自基线测试的真实失败，勿重蹈）

| 错误 | 正确做法 |
|---|---|
| 无附录页，风险只在正文红字一句带过 | 附录A 四要素表格 + 有条件立项条件清单 |
| 无交叉验证，销售数字直接引用 | 附录B 独立推算链路；推不出时显式标来源待补 |
| 用微软雅黑代替 CHINTinno | 生成器已内置 CHINTinno，勿改字体 |
| 财务投入只写合计一句 | 保留五类费用投入表槽位，缺数据填"待财务提供" |
| 价格成本退化为键值对 | 保留规格×占比×口袋价×成本×毛利率表 + Total 行 |
| 毛利率与价格/成本口径不勾稽 | 检查 (面价−成本)/面价 与毛利率一致（±5pp），不一致就是数据源问题，要问 |
| 标题写"技术可行性与创新点"无结论 | verdict 写进标题条："技术可行性-部分可行" |

## Red Flags - STOP

- 想跳过校验器"我自己看过了就行" → 不允许，PASS 是交付门槛。
- 想绕过生成器手摆文本框"更灵活" → 不允许，版式走 generate_one_pager.py。
- 用户催时间，想砍附录页"先交主体" → 附录是红线，占位也要交。
- 发现 spec 槽位填不出而想删掉 → 占位并上报，不删。
