---
name: chint-data-review
description: Use when auditing CHINT low-voltage / ACB market figures across Excel, whitepapers, or competitor datasets and every cited number must trace to a source page.

---

# 法证级数据审查 (CHINT Data Review)

将正泰低压 / ACB 市场与产品数据审查流程固化为可复用 SOP。核心原则：任何对外引用的数字都必须能追溯到原始出处的具体页码，且发现的问题必须有优先级。

## 何时使用
- 审查市场容量、竞品参数、行业白皮书数字、销售数据。
- 用户要求「溯源」「核对」「核验」「审计」数据。
- 产出数据审查报告 / 口径说明。

## 审查流程（四步）
1. **建溯源矩阵**：列出所有关键数字（市场容量、增速、参数、份额），每行记录「数值 / 单位 / 口径 / 来源文件 / 页码」。
2. **链式交叉核对**：按 `Excel → PDF 白皮书 → 行业报告 → 竞品数据` 顺序，逐源比对同一指标；不一致项标记为待澄清。
3. **优先级标注**：对发现的问题打 P0 / P1 / P2（判定标准见 references/checklist.md）。
4. **引用与成稿**：每个数字按 `[文件, p.页码]` 格式标注（规则见 references/citation-format.md）；不确定事实标「待确认」或「建议向数据源方核实」，绝不编造。

## 硬性规则
- 引用统一 `[1, p.9]`，**禁止**出现 OCR 行号 `[1, L141-L160]`。
- 市场容量带单位（亿元）并标注口径（全口径 vs ACB 专属、装机 vs 销量）。
- 修改 / 修正必须显式 before / after 对比，不做隐含修正。
- 第三方数据准确性不担保，标「待确认」。

## 参考
- [checklist.md](references/checklist.md) — 审查清单 + P0/P1/P2 判定标准 + 交叉源矩阵模板；标注优先级前读。
- [citation-format.md](references/citation-format.md) — 引用格式规则与示例；成稿标注前读。
