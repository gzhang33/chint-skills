---
name: chint-data-visual
description: 未启用。原计划封装 CHINT 主配电 ACB 运营分析 PPT/HTML 报告生成，但其依赖的脚本与模板已从本机移除，无法运行。仅在用户明确要求恢复该流程、且已确认脚本落点后使用；否则改用 chint-data-review。
agent_created: true
---

# Chint Data Visual（未启用）

> ⚠️ **本技能当前不可用，且未从 `chint-data` 插件暴露。**
> 2026-11-03 核查：原脚本目录 `~/Documents/chint/excel 表格报告/scripts/` 已不存在；`cli.py`、`gen_overseas_region_summary.py`、`framework_reporting_template.pptx`、`scripts/data/` 在本机全树均无副本。仅 `analyzer.py` / `loader.py` / `pptx_generator.py` 残留在已归档的 `chint-data-analysis` 技能内。

## 何时仍会碰到

- 用户要求「生成 / 刷新框架断路器运营分析报告」「PPT 内容没更新」——先确认脚本是否已恢复；未恢复则告知流程不可用，不要按记忆生成路径或命令。
- 需要核对已有报告的数据口径时，改用 `chint-data-review`。

## 恢复前提（全部满足才可启用）

1. 分析脚本（`cli.py` / `analyzer.py` / `pptx_generator.py` / `loader.py`）与模板 `framework_reporting_template.pptx` 落在确定路径，且该路径已复核存在。
2. 源数据工作簿就位，且覆盖目标年与同比基期年。
3. 已实测跑通一次完整链路：选源 → 生成 → `verify_pptx.py` 校验。

满足后按上述实测路径重写本文件，并在 `plugins/chint-data/.claude-plugin/plugin.json` 与 README 重新登记。

## 已知约束（恢复时仍适用）

- 巨型 xlsm（80MB+）禁止 openpyxl 全量 `load` + `save`，会破坏透视表 / 图表 / 公式链；需流式 XML 手术。
- 模板是填空骨架：每次生成读模板 → 填数据 → 另存，模板本身不改。
- 「内容不更新」多半是未重跑，或源文件缺目标年 / 同比基期年（缺基期会让 `analyzer.py` 在 `groupby` 处崩）。
