# Data Source Rules

## 统一规则

- 所有分析脚本经 `loader.resolve_default_input()` 取 `scripts/data/` 下最新 Excel，不再各自硬编码路径。
- `cli.py` 的 `--input` 默认 `None`；`gen_overseas_region_summary.py` 的 `EXCEL` 亦走 resolver。
- 优化类脚本（`optimize_excel*.py` / `verify_optimized.py`）的 `target_dir` 已改到 `scripts/data`。

## 年份口径

- 正确源 `主配电24-26年销售数据 -框架2026.04 净收入 v2.xlsm` 含 **2024 / 2025 / 2026** 三年。
- 合并文件（文件名含 "24-26年"）：`loader.find_prev_year_file` 检测到即返回**同一文件**，同比按年份列过滤 —— 无需多文件。
- 正确用法：`--year 2026 --prev-year 2025`（文件含 24/25/26）。

## 同比基期缺失崩溃（P0，未修）

- **现象**：`--prev-year <源文件不存在的年份>`（如源仅 2025 却传 `--prev-year 2024`）→ `analyzer.py` 第 4 步 `industry_region_china` 中 `df_prev = None` → `.groupby()` 抛 `AttributeError`，整流程崩溃。
- **规避**：确保 `--prev-year` 落在源文件覆盖年内；或先提示用户补全基期数据再跑。
- **修复建议（待用户授权）**：在 `analyzer.py` 对 `df_prev is None` 时优雅降级为"数据缺失"而非崩溃。

## 历史误用教训

- 曾误用 `25年框架虚拟工厂合并报表.xlsx`（仅含 2025 年）当源 → 全 `0` / 无同比。凡名称含"框架"但**非 `scripts/data` 指定源**的旧报表，勿用。

## 源文件安全编辑（P0）

- 源为约 80MB 的 `.xlsm`（解压 GB 级），含真实透视表 / 图表 / 公式链。
- **禁止 openpyxl 全量 `load`+`save`**（丢透视表 / 图表 / 公式链，破坏其他 sheet）。
- 改源用 `safe-xlsx-edit` 流式 XML 手术（`zipfile` 只读 + `lxml` `iterparse` 过滤 + `zip -r` 单成员回写）。
