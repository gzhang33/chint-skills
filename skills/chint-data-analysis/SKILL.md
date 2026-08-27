---
name: chint-data-analysis
description: Use when analyzing sales revenue, volume, series replacement rate, YoY trends, terminal customer industry attribution, or generating PPT reports for Low-Voltage Power Distribution products (ACB, MCCB, Power Quality, ATS, Virtual Factory) and related business teams.
---

# CHINT Power Distribution Data Analytics & Reporting Skill

Enterprise-grade multi-dimensional OLAP analytics and automated reporting engine for Low-Voltage Power Distribution Product Managers and business teams (ACB, MCCB, Power Quality, ATS, Virtual Factory).

---

## 4-Step Standard Workflow

### Step 1: Requirements Check & Clarification
Before executing any query, confirm the core analysis parameters:
1. **Category & Business Scope**:
   - Core Power Distribution categories: ACB (Air Circuit Breaker), MCCB (Molded Case Circuit Breaker), Power Quality, ATS, Virtual Factory
   - Additional scopes: International export (`intl`), All categories (`all`)
2. **Time Range**: Analysis year and month span (e.g. `2026 YTD Months 1-7` or `Month 7 single`).
3. **Analysis & Delivery Mode**:
   - Standard multi-dimensional aggregation / YoY trends (`--yoy`)
   - Product replacement rate analysis (must explicitly specify pairing, e.g. `-r "NXA:NA1"`)
   - Macro overview (`-q overview`)
   - Standard PPT report export (`pptx_generator.py`)
4. **Drill-down Dimension Isolation**:
   - Industry drill-down -> MUST lock `terminal_customer` (终端客户)
   - Channel drill-down -> MUST lock `customer_name` (客户名称)

> [!IMPORTANT]
> **Active Clarification Gate**: If a request lacks critical parameters (e.g. replacement rate requested without pairing, ambiguous months), ask for clarification before executing.
> 
> See business rules and metrics definitions in [business_rules.md](references/business_rules.md).
> 
> **Completion Criterion**: Confirmed category, time span, analysis mode, and comparison pairing.

---

### Step 2: Data Status & Ingestion
1. **Environment Verification**:
   - Ensure dependencies are installed: `pip install -r requirements.txt` (DuckDB, Pandas, PyArrow, python-pptx, openpyxl, matplotlib).
   - Ensure local DuckDB database (`data/database/<dept>.duckdb`) is active.
2. **Data Ingestion & Verification**:
   - Run ingestion via `etl/data_processor.py`.
   - Verify unmapped materials via `etl/mapping_manager.py`.

> **Completion Criterion**: Data is refreshed, validated, and reconciled in DuckDB semantic views.

---

### Step 3: Targeted Computation & Delivery
Execute analytics queries or presentation generation based on aligned parameters:

```bash
# 1. Industry dimension YoY trend analysis (lock terminal_customer)
python3 .agents/skills/chint-data-analysis/scripts/query_sales.py -g "终端客户" -y 2026 -m 1,2,3,4,5,6,7 --yoy -n 10

# 2. Automated PPT report generation
python3 backend/app/services/pptx_generator.py --category 框架 --year 2026 --months 1,2,3,4,5,6,7 --output reports/analysis_report.pptx
```

> See detailed CLI parameters and scenario recipes in [cli_reference.md](references/cli_reference.md).
> 
> **Completion Criterion**: Script runs successfully and outputs verified metrics or report files.

---

### Step 4: High-Density User Delivery SOP
In conversation responses, deliver results formatted strictly in **pure Chinese** without code blocks or bilingual noise:

1. **Executive Summary (速报)**: 3 core bullet points (revenue YoY, body unit volume YoY, key abnormal category/region).
2. **Structured Top 5-10 Table**: Dimension, Net Revenue, YoY %, Volume, Volume YoY %, Replacement Rate % (if applicable).
3. **Attribution & Recommendations (归因与建议)**: 1-2 focused follow-up actions and customer takeaways.

> [!WARNING]
> **Delivery Prohibitions**:
> - Never output raw code syntax or script implementations in chat conversations.
> - Do not include redundant bilingual translation brackets in Chinese outputs.
> - Limit tables to Top 5-10 unless full detail is explicitly requested.
> 
> **Completion Criterion**: Clean, high-density, accurate, and actionable Chinese summary.

---

## References

- **Executive Reporting Copywriting Standard**: [`chint-pm-copywriter`](../chint-pm-copywriter/SKILL.md)
- **Business Rules & Isolation Standards**: [references/business_rules.md](references/business_rules.md)
- **CLI Reference & Scenario Dictionary**: [references/cli_reference.md](references/cli_reference.md)
- **Multi-Dimensional Analysis Dimensions**: [references/dimensions.md](references/dimensions.md)
