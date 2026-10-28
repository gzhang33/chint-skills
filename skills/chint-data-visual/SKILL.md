---
name: chint-data-visual
description: This skill should be used when generating, refreshing, or debugging
  CHINT (正泰电器) 主配电 / 框架断路器 (ACB) 运营分析 PPT or HTML reports from sales data Excel
  workbooks. It encodes the data-source resolution rule (auto-pick the latest
  scripts/data/*.xlsm), the framework_reporting_template.pptx fill contract
  (data tables vs. Action Tracker tables), the 7-dimension analyzer, the
  year-base YoY pitfall (missing prev-year crashes analyzer.py), and the
  safe-editing rule for the ~80MB source workbook. Trigger on requests like
  '生成框架断路器运营分析报告', '刷新 PPT 用最新销售数据', '为什么 PPT 内容没更新', or any task touching
  framework_reporting_template.pptx / cli.py / pptx_generator.py /
  gen_overseas_region_summary.py / loader.py.
version: 1.0.0
agent_created: true
disabled: true
---

# Chint Data Visual

> ⚠️ 状态：项目级草稿，`disabled: true`。底层分析脚本（cli.py / analyzer.py / pptx_generator.py 等）尚未完善，暂不启用。待脚本稳定后，将 `disabled` 改为 `false` 即可激活。

## Overview

封装 CHINT 主配电（框架断路器 ACB）运营数据分析 → PPT / HTML 报告的完整、可复现工作流。脚本位于 `~/Documents/chint/excel 表格报告/scripts/`，数据源统一在 `scripts/data/` 下最新 Excel。本 skill 使 WorkBuddy 以正泰 PM 视角，正确生成汇报材料，并规避已知的数据源 / 同比 / 模板契约陷阱。

依赖运行于 managed venv：`/Users/gianni/.workbuddy/binaries/python/envs/default/bin/python`（已装 python-pptx / pandas / openpyxl / plotly）。下文命令中的 `python` 均指该解释器。

## When To Use

- 用户要求生成或刷新 CHINT 主配电运营分析 PPT / HTML 报告。
- 用户要求生成海外五大区单页汇总 PPT。
- 用户报告"PPT 内容没更新 / 数据不刷新"，需诊断模板契约或数据源问题。
- 任务涉及 `framework_reporting_template.pptx`、`cli.py`、`pptx_generator.py`、`gen_overseas_region_summary.py`、`loader.py`、`analyzer.py`。

## Core Workflow

### 1. 数据源（自动选用，勿硬编码路径）

- `loader.resolve_default_input()` 扫描 `scripts/data/` 下 `*.xlsx/*.xlsm/*.xls`，按 `st_mtime` 降序取最新，跳过 `~$` 锁文件与 `*_optimized` 中间产物。
- `cli.py` 的 `--input` 默认 `None`；未指定即自动选用上述文件。
- 当前正确数据源：`主配电24-26年销售数据 -框架2026.04 净收入 v2.xlsm`（含 2024 / 2025 / 2026 三年）。

### 2. 生成 PPT 报告

```bash
cd ~/Documents/chint/excel\ 表格报告/scripts
python cli.py \
  --year 2026 --prev-year 2025 --months 1,2,3 \
  --export-pptx "../reports/框架运营分析_YYYYMMDD.pptx"
```

- `--year` 目标年、`--prev-year` 同比基期（二者都必须存在于源文件，否则见 Pitfalls）。
- 不传 `--input` 即自动选 `scripts/data` 最新文件。

### 3. 生成 HTML 报告

同上加 `--output ../reports/报告.html`、省略 `--export-pptx`，生成 7 维分析综合 HTML。

### 4. 海外五大区单页汇总

```bash
python gen_overseas_region_summary.py
```

自动用 resolver 选源，生成 `reports/海外五大区_YYYY年M月汇总_单页.pptx`（1 页：净收入 + 销量 + 同比，涨红跌绿）。

## Template Fill Contract

详见 `references/template_contract.md`。要点：

- 模板 `templates/framework_reporting_template.pptx` 是**填空骨架**：每次生成 = 读模板 → 填数据 → 另存新文件；模板本身永不被改。"内容不更新"通常不是脚本坏，而是未重跑或源缺目标年。
- 每页由「**数据表**（脚本填充）+ **Action Tracker 表**（手工维护，永不覆盖）」两组构成。
- 标题绑定健壮（`slide.shapes.title`）；数据表绑定脆弱（精确形状名 + run 数 + 首列行标签）。

## Data Source Rules

详见 `references/data_source.md`。要点：

- 源文件为 24-26 三年合并文件时，`loader.find_prev_year_file` 返回自身，同比按年份列过滤，无需多文件。
- **同比基期缺失 → `analyzer.py` 第 4 步 `df_prev=None` 后 `groupby` 崩溃**（未修；缺失基期时勿跑，或提示用户补全上一年数据）。

## Pitfalls (P0 / P1)

- **P0 数据源年份不全**：`--year 2026` 但源仅含 2025 → 数据表全 `0` / `数据缺失`（假"不更新"）。务必让 `--year` / `--prev-year` 均在源文件覆盖年内。
- **P0 巨型 xlsm 安全编辑**：源文件约 80MB+（解压 GB 级），**禁止 openpyxl 全量 `load`+`save`**（破坏透视表 / 图表 / 公式链）。需改源用 `safe-xlsx-edit` 流式 XML 手术。
- **P1 Action Tracker 不改写**：5 个 Action Tracker 表（表格 7 / 7 / 7 / 8 / 10）代码从不引用，重跑后保持模板原样——这是预期行为，非 bug。
- **P1 模板表头写死年份**：slide6 等表头文案"2026年 / 26年1-3月毛利率"是烤死的，脚本只填数值单元格不重写表头；换年需改模板。
- **P2 `backend/main.py`**：Web 后端上传目录仍指向旧 `框架模型/data`，未统一；独立部署勿混淆。

## Verification

生成后用 `scripts/verify_pptx.py` 核对：

```bash
python scripts/verify_pptx.py 生成.pptx 模板.pptx
```

检查：数据表（表格 8 / 1 / 4 / 9）是否已变更填充、5 个 Action Tracker 是否逐字节保留、图表系列数是否合理。

## Key Paths

- 脚本目录：`~/Documents/chint/excel 表格报告/scripts/`
- 数据源：`~/Documents/chint/excel 表格报告/scripts/data/`（最新 `.xlsm`）
- 模板：`scripts/templates/framework_reporting_template.pptx`
- 死文件（已被取代）：`scripts/templates/reporting_template.pptx`（可 `git rm`）
