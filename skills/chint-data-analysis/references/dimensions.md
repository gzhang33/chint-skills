# Multi-Dimensional Data Analytics Reference (多维数据分析参考指南)

This document provides technical reference and definition details for the 5 key analysis dimensions executed by the `chint-data-analysis` engine.

---

## 1. Five Core Analysis Dimensions (5 大核心分析维度)

### Dimension 1: Global Executive Overview (全局大盘与品牌拆解)
- **Primary KPIs**:
  - Global Net Income (`net_income` in 万元)
  - Gross Profit (`gross_profit` in 万元)
  - Invoice Quantity (`invoice_qty` in 台/万台)
  - Average Unit Sales Price (`avg_unit_price` in 元/台)
  - Gross Margin Rate (`gross_margin_rate` in %)
  - YoY Variations (`yoy_pct` for income, quantity, profit)
- **Brand Breakdown**:
  - CHINT Brand (`正泰`) vs Noark Brand (`诺雅克`).

### Dimension 2: Domestic Product Line & Series (中国区产品线与型号结构)
- **Series Level**: Next-series (正泰拓新系列), World-series, Craft-series, Traditional series.
- **Model Level**: Breakdown of top revenue & volume generating breaker models.
- **Metrics**: YTD Sales, YTD Qty, YoY Growth %, Share of Total CN Sales %.

### Dimension 3: International Product Portfolio (国际区产品系列)
- **Overseas Product Series**: Export product lines tailored for European, Asia-Pacific, Latin American, and Middle Eastern markets.
- **Metrics**: Export Revenue, Qty, YoY Growth %.

### Dimension 4: Domestic Industry Teams & Regional Big Areas (中国区行业团队与七大区)
- **Industry Customer Segments**:
  - Panel Builders (盘柜厂)
  - OEM Equipment Manufacturing (OEM)
  - Real Estate & Building (建筑地产)
  - Power Grid & Energy (电力电网)
  - Industrial Automation (工业自动化)
- **Regional Big Areas**:
  - East China (华东大区), North China (华北), South China (华南), Central China (华中), West China (西南/西北), Northeast (东北).

### Dimension 5: Gross Margin & Cost Analysis (毛利与成本结构)
- **Gross Profit Margin (%)**: Calculated at series and product tier level.
- **Unit Cost Trend**: Cost variance per unit across current year vs prior year.

---

## 2. Command Line CLI Options Reference

完整的命令行运行参数、筛选机制与场景调用模板，请直接参考单一大纲：
👉 **[CLI 调用命令与场景字典参考 (cli_reference.md)](cli_reference.md)**

---

## 3. Completion Criteria

When executing a full dataset analysis run, the process completes successfully when:
1. All 5 analytical dimensions complete calculation without missing value errors (`NaN`/`Inf` sanitized).
2. `reports/full_analysis_data.json` is generated with valid JSON syntax.
3. `reports/full_analysis_report.md` is rendered with clear markdown formatting.
4. The stdout summary displays clean execution metrics.
