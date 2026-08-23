"""
ingest_engine.py — 统一数据摄入、清洗与 DuckDB 年月分区幂等更新引擎 (Skill SSOT)

核心特性：
1. 56 列标准标题与物理列标准化映射（隔离 net_revenue 净收入 与 net_amount 净额，杜绝静默取最大值）。
2. 智能本体 (本体 vs 附件) 与核心指标 (net_revenue, invoice_qty_benti) 规范化。
3. 严格接入 data_quality 契约校验与勾稽核对（净收入 - 产品成本 ≈ 毛利额），失败直接阻断。
4. 年月分区幂等覆盖 (Partition-level Upsert) 与全量覆盖重置。
5. 注册统一语义视图 (v_sales_detailed, v_sales_all, v_chint_cn_sales_xxx, v_chint_intl_sales)，解耦 market_channel 与 region。
6. 提供全自动多维对账核算小结与 dry-run 预览探查能力。
"""
from __future__ import annotations
import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Set
import pandas as pd
import numpy as np
import duckdb

try:
    from config_loader import STANDARD_56_COLUMN_MAP, SKILL_DUCKDB_PATH
    from data_quality import validate_dataframe
except ImportError:
    from .config_loader import STANDARD_56_COLUMN_MAP, SKILL_DUCKDB_PATH
    from .data_quality import validate_dataframe

# ── 1. 属性判定关键词表（本体 vs 附件） ─────────────────────────────────────
NON_BENTI_KEYWORDS = [
    "附件", "辅助触头", "分励脱扣器", "欠压脱扣器", "闭合电磁铁", "电动操作机构",
    "抽屉架", "控制器", "互感器", "接线板", "门框", "相间隔板", "二次接线插头",
    "手柄", "联锁", "机构", "罩壳", "零配件", "铜排", "螺栓", "母排", "安装板",
    "脱扣器", "欠压", "分励", "电操", "电磁铁", "指示灯", "插座", "线圈"
]


def classify_property_type(material_desc: Any, default_val: Any = None) -> str:
    """判定二元属性（本体 vs 附件）"""
    if default_val and str(default_val).strip() in ("本体", "附件"):
        return str(default_val).strip()
    if not material_desc or pd.isna(material_desc):
        return "本体"
    desc_str = str(material_desc)
    for kw in NON_BENTI_KEYWORDS:
        if kw in desc_str:
            return "附件"
    return "本体"


def clean_material_description(desc: Any) -> str:
    """清洗物料描述"""
    if not desc or pd.isna(desc):
        return "未归属物料"
    clean_str = re.sub(r'[\s_]+', ' ', str(desc)).strip()
    return clean_str


def normalize_year_month(val: Any) -> int:
    """提取纯整数年份或月份"""
    if val is None or pd.isna(val):
        return 0
    s = str(val).strip()
    match = re.search(r'\d+', s)
    if match:
        return int(match.group(0))
    return 0


def read_and_clean_dataframe(
    file_path: Path | str,
    sheet_name: Optional[str] = None,
    revenue_col: Optional[str] = None,
    run_validation: bool = True
) -> pd.DataFrame:
    """
    通用 Excel/CSV 读取与清洗转换函数
    自动识别多 Sheet、标准化 56 列标题、推导本体属性与统一数值指标，严格执行数据质量契约校验。
    """
    path_obj = Path(file_path).resolve()
    if not path_obj.exists():
        raise FileNotFoundError(f"数据集文件未找到: {file_path}")

    dfs = []
    if path_obj.suffix.lower() in ('.xlsx', '.xls', '.xlsm'):
        try:
            xl = pd.ExcelFile(path_obj, engine="calamine")
        except Exception:
            xl = pd.ExcelFile(path_obj)
        
        all_sheets = xl.sheet_names
        target_sheets = []
        
        if sheet_name:
            if sheet_name in all_sheets:
                target_sheets = [sheet_name]
            else:
                raise ValueError(f"指定的 Sheet '{sheet_name}' 不存在于 Excel 中！可用页: {all_sheets}")
        else:
            # 自动探测核心数据 Sheet
            for s in all_sheets:
                if any(kw in s for kw in ["中国区", "中国数据", "中国", "海外区", "海外数据", "海外", "国际数据", "国际区", "国际", "销售数据", "明细", "Data", "Sheet1"]):
                    target_sheets.append(s)
            if not target_sheets:
                target_sheets = [all_sheets[0]]
        
        for s in target_sheets:
            df_sub = xl.parse(sheet_name=s)
            if not df_sub.empty:
                # 若无 report_source，根据 sheet 补充默认来源
                if "报表来源" not in df_sub.columns and "report_source" not in df_sub.columns:
                    if "海外" in s or "国际" in s:
                        df_sub["report_source"] = "海外区"
                    else:
                        df_sub["report_source"] = "中国区"
                dfs.append(df_sub)
    elif path_obj.suffix.lower() == '.csv':
        try:
            df_csv = pd.read_csv(path_obj, encoding='utf-8')
        except UnicodeDecodeError:
            df_csv = pd.read_csv(path_obj, encoding='gbk')
        dfs.append(df_csv)
    else:
        raise ValueError(f"不支持的数据格式: {path_obj.suffix}")

    if not dfs:
        raise ValueError("未能从文件中解析出任何有效数据行！")

    df = pd.concat(dfs, ignore_index=True)

    # 1. 规范化列名与收入列消歧
    rev_col_clean = revenue_col.strip() if revenue_col else None
    new_cols = []
    for col in df.columns:
        col_clean = str(col).strip()
        if rev_col_clean and col_clean == rev_col_clean:
            mapped_col = "net_revenue"
        else:
            mapped_col = STANDARD_56_COLUMN_MAP.get(col_clean, col_clean)
        new_cols.append(mapped_col)
    
    df.columns = new_cols

    # 同名列安全合并（杜绝盲目取最大值，优先取第一个有效值）
    if df.columns.duplicated().any():
        dedup_cols = {}
        for c in df.columns.unique():
            sub = df[c]
            if isinstance(sub, pd.DataFrame):
                if c in ("net_revenue", "net_amount", "product_cost", "gross_profit", "raw_sales_qty", "invoice_qty_benti"):
                    sub_num = sub.apply(pd.to_numeric, errors='coerce')
                    merged_series = sub_num.bfill(axis=1).iloc[:, 0].fillna(0.0)
                else:
                    merged_series = sub.fillna("").astype(str).replace("", np.nan).bfill(axis=1).iloc[:, 0].fillna("")
                dedup_cols[c] = merged_series
            else:
                dedup_cols[c] = sub
        df = pd.DataFrame(dedup_cols, index=df.index)

    # 2. 补齐核心字段
    if "year" in df.columns:
        df["year"] = df["year"].apply(normalize_year_month)
    else:
        df["year"] = 2026

    if "month" in df.columns:
        df["month"] = df["month"].apply(normalize_year_month)
    else:
        df["month"] = 1

    # 过滤无效年月行 (如空行或汇总统计行)
    df = df[df["year"] > 2000].copy()

    # 季度
    if "quarter" not in df.columns:
        df["quarter"] = df["month"].apply(
            lambda m: "Q1" if m in (1, 2, 3) else ("Q2" if m in (4, 5, 6) else ("Q3" if m in (7, 8, 9) else "Q4"))
        )

    # 物料描述清洗与本体分类
    if "material_desc_raw" in df.columns:
        df["material_desc_clean"] = df["material_desc_raw"].apply(clean_material_description)
    elif "material_desc_clean" not in df.columns:
        df["material_desc_clean"] = "常规物料"

    raw_prop = df.get("property_type", None)
    df["property_type"] = df.apply(
        lambda r: classify_property_type(r.get("material_desc_clean", ""), r.get("property_type", None)),
        axis=1
    )

    # 3. 规范数值指标 (双物理列隔离保留：net_revenue 净收入 与 net_amount 净额)
    has_net_rev = "net_revenue" in df.columns
    has_net_amt = "net_amount" in df.columns

    if has_net_rev:
        df["net_revenue"] = pd.to_numeric(df["net_revenue"], errors='coerce').fillna(0.0)
    elif has_net_amt:
        print("⚠️ [Warning] 数据源未包含'净收入（不含税）'列，已回退采用'净额（不含税）'作为 net_revenue。")
        df["net_revenue"] = pd.to_numeric(df["net_amount"], errors='coerce').fillna(0.0)
    else:
        df["net_revenue"] = 0.0

    if has_net_amt:
        df["net_amount"] = pd.to_numeric(df["net_amount"], errors='coerce').fillna(0.0)
    else:
        df["net_amount"] = df["net_revenue"]

    df["net_income_wanyu"] = df["net_revenue"] / 10000.0
    df["net_amount_wanyu"] = df["net_amount"] / 10000.0

    # 发票数量与本体台数
    if "raw_sales_qty" in df.columns:
        df["raw_sales_qty"] = pd.to_numeric(df["raw_sales_qty"], errors='coerce').fillna(0.0)
        df["invoice_qty"] = df["raw_sales_qty"]
    elif "invoice_qty" in df.columns:
        df["invoice_qty"] = pd.to_numeric(df["invoice_qty"], errors='coerce').fillna(0.0)
        df["raw_sales_qty"] = df["invoice_qty"]
    else:
        df["invoice_qty"] = 0.0
        df["raw_sales_qty"] = 0.0

    df["invoice_qty_benti"] = df.apply(
        lambda r: r["invoice_qty"] if str(r.get("property_type", "本体")) == "本体" else 0.0,
        axis=1
    )

    # 成本与毛利 (单位均为“元”，wanyu 字段为万元)
    if "product_cost" in df.columns:
        df["product_cost"] = pd.to_numeric(df["product_cost"], errors='coerce').fillna(0.0)
        df["cost_wanyu"] = df["product_cost"] / 10000.0
    elif "cost_wanyu" in df.columns:
        df["cost_wanyu"] = pd.to_numeric(df["cost_wanyu"], errors='coerce').fillna(0.0)
        df["product_cost"] = df["cost_wanyu"] * 10000.0
    else:
        df["cost_wanyu"] = 0.0
        df["product_cost"] = 0.0

    if "gross_profit" in df.columns:
        df["gross_profit"] = pd.to_numeric(df["gross_profit"], errors='coerce').fillna(0.0)
        df["gross_profit_wanyu"] = df["gross_profit"] / 10000.0
    elif "gross_profit_wanyu" in df.columns:
        df["gross_profit_wanyu"] = pd.to_numeric(df["gross_profit_wanyu"], errors='coerce').fillna(0.0)
        df["gross_profit"] = df["gross_profit_wanyu"] * 10000.0
    else:
        df["gross_profit"] = df["net_revenue"] - df["product_cost"]
        df["gross_profit_wanyu"] = df["gross_profit"] / 10000.0

    # 基础维度列安全填充
    str_cols = [
        "report_source", "market_channel", "brand_sector", "product_category", "product_series",
        "product_subclass", "product_model", "product_manager", "province",
        "region", "country", "sales_team", "terminal_customer", "customer_name",
        "biz_type", "biz_category", "material_code", "material_desc_raw", "material_desc_clean",
        "frame_current", "breaking_capacity", "operation_method", "pole_count", "n_pole_type", "tripping_curve"
    ]
    for c in str_cols:
        if c not in df.columns:
            df[c] = ""
        else:
            df[c] = df[c].fillna("").astype(str).str.strip()

    # 规范化省份字段：严格剥离海外业务的“海外”伪省份占位符
    if "province" in df.columns:
        is_overseas_mask = (
            df["report_source"].astype(str).str.contains("海外|国际|外贸", na=False) |
            (df["province"].astype(str).str.strip() == "海外")
        )
        df.loc[is_overseas_mask, "province"] = ""

    # 规范化 market_channel
    def derive_market_channel(row):
        rep = str(row.get("report_source", "")).strip()
        ch = str(row.get("market_channel", "")).strip()
        if ch in ("中国区", "国内", "中国"):
            return "中国区"
        if ch in ("海外区", "国际", "海外", "外贸"):
            return "海外区"
        if "国际" in rep or "海外" in rep or "外贸" in rep:
            return "海外区"
        return "中国区"

    df["market_channel"] = df.apply(derive_market_channel, axis=1)

    # 规范化 product_category (如 '框架类' -> '框架', '塑壳类' -> '塑壳')，同时兼容系列识别
    def standardize_cat(row):
        cat = str(row.get("product_category", "")).strip()
        series = str(row.get("product_series", "")).strip().upper()
        if cat in ("框架类", "框架", "ACB", "万能式断路器"):
            return "框架"
        if cat in ("塑壳类", "塑壳", "MCCB", "塑料外壳式断路器"):
            return "塑壳"
        if cat in ("微断类", "微断", "MCB", "终端类", "终端配电类"):
            return "微断"
        if cat in ("电能质量", "电能质量类", "PQ"):
            return "电能质量"
        if cat in ("双电源", "双电源类", "ATSE", "ATS"):
            return "双电源"
        # 若 category 为空或为通用词，基于产品系列识别
        if series in ("NXA", "NA1", "NDW1", "NDW2", "NA8G"):
            return "框架"
        if series in ("NXM", "NM1", "NM8", "NM8N", "NM8M", "NXMLE", "NM1LE", "M"):
            return "塑壳"
        if series in ("NXB", "DZ47", "DZ158", "NB1", "Ex9B"):
            return "微断"
        if series in ("NXZ", "NZ7", "NH40"):
            return "双电源"
        return cat if cat and cat not in ("低压", "低压电器") else "框架"

    df["product_category"] = df.apply(standardize_cat, axis=1)

    # 4. 执行数据质量契约校验
    if run_validation:
        validate_dataframe(df)

    return df


def inspect_and_preview_file(
    file_path: Path | str,
    sheet_name: Optional[str] = None,
    revenue_col: Optional[str] = None
) -> Dict[str, Any]:
    """
    Dry-Run 探查预览：
    解析 Excel/CSV 文件结构、Sheet 清单、列映射矩阵与潜在口径冲突，而不写入 DuckDB。
    """
    path_obj = Path(file_path).resolve()
    if not path_obj.exists():
        raise FileNotFoundError(f"文件未找到: {file_path}")

    sheets_info = []
    if path_obj.suffix.lower() in ('.xlsx', '.xls', '.xlsm'):
        try:
            xl = pd.ExcelFile(path_obj, engine="calamine")
        except Exception:
            xl = pd.ExcelFile(path_obj)
        for s in xl.sheet_names:
            df_peek = xl.parse(sheet_name=s, nrows=5)
            sheets_info.append({
                "sheet_name": s,
                "raw_columns": [str(c).strip() for c in df_peek.columns],
                "sample_rows_count": len(df_peek)
            })
    else:
        df_peek = pd.read_csv(path_obj, nrows=5)
        sheets_info.append({
            "sheet_name": "CSV_DATA",
            "raw_columns": [str(c).strip() for c in df_peek.columns],
            "sample_rows_count": len(df_peek)
        })

    # 读取并清洗预览数据
    df_clean = read_and_clean_dataframe(file_path, sheet_name=sheet_name, revenue_col=revenue_col, run_validation=False)

    # 列映射矩阵分析
    all_raw_cols = []
    for s_info in sheets_info:
        all_raw_cols.extend(s_info["raw_columns"])
    all_raw_cols = list(dict.fromkeys(all_raw_cols))

    mapping_matrix = []
    revenue_candidates = []
    for c in all_raw_cols:
        target_f = STANDARD_56_COLUMN_MAP.get(c, "(透传原始物理列)")
        if c in ("净收入（不含税）", "净额（不含税）", "销售净收入", "净额", "净收入", "开票金额"):
            revenue_candidates.append((c, target_f))
        mapping_matrix.append({
            "raw_column": c,
            "mapped_target": target_f
        })

    return {
        "file_name": path_obj.name,
        "file_size_mb": round(path_obj.stat().st_size / (1024 * 1024), 2),
        "sheets": sheets_info,
        "total_parsed_rows": len(df_clean),
        "mapping_matrix": mapping_matrix,
        "revenue_candidates": revenue_candidates,
        "sample_data": df_clean.head(3).to_dict(orient="records")
    }


def get_reconciliation_summary(con: duckdb.DuckDBPyConnection) -> Dict[str, Any]:
    """计算并生成中国区/海外区 × 本体/附件的结构化勾稽对账小结"""
    # 1. 市场渠道与属性交叉统计
    cross_records = con.execute("""
        SELECT 
            market_channel,
            property_type,
            COUNT(*) AS row_cnt,
            COALESCE(SUM(raw_sales_qty), 0) AS total_qty,
            COALESCE(SUM(invoice_qty_benti), 0) AS benti_qty,
            COALESCE(SUM(net_revenue), 0) / 10000.0 AS net_revenue_wanyu,
            COALESCE(SUM(product_cost), 0) / 10000.0 AS cost_wanyu,
            COALESCE(SUM(gross_profit), 0) / 10000.0 AS profit_wanyu
        FROM v_sales_detailed
        GROUP BY market_channel, property_type
        ORDER BY market_channel DESC, property_type ASC
    """).fetchall()

    cross_summary = []
    for r in cross_records:
        cross_summary.append({
            "market_channel": r[0],
            "property_type": r[1],
            "row_cnt": r[2],
            "total_qty": round(float(r[3]), 2),
            "benti_qty": round(float(r[4]), 2),
            "net_revenue_wanyu": round(float(r[5]), 2),
            "cost_wanyu": round(float(r[6]), 2),
            "profit_wanyu": round(float(r[7]), 2)
        })

    # 2. 渠道大盘总计
    channel_records = con.execute("""
        SELECT 
            market_channel,
            COUNT(*) AS row_cnt,
            COALESCE(SUM(raw_sales_qty), 0) AS total_qty,
            COALESCE(SUM(invoice_qty_benti), 0) AS benti_qty,
            COALESCE(SUM(net_revenue), 0) / 10000.0 AS net_revenue_wanyu,
            COALESCE(SUM(gross_profit), 0) / 10000.0 AS profit_wanyu
        FROM v_sales_detailed
        GROUP BY market_channel
        ORDER BY market_channel DESC
    """).fetchall()

    channel_summary = []
    for r in channel_records:
        channel_summary.append({
            "market_channel": r[0],
            "row_cnt": r[1],
            "total_qty": round(float(r[2]), 2),
            "benti_qty": round(float(r[3]), 2),
            "net_revenue_wanyu": round(float(r[4]), 2),
            "profit_wanyu": round(float(r[5]), 2)
        })

    # 3. 全局总计
    total_row = con.execute("""
        SELECT 
            COUNT(*) AS total_rows,
            COALESCE(SUM(raw_sales_qty), 0) AS total_qty,
            COALESCE(SUM(invoice_qty_benti), 0) AS benti_qty,
            COALESCE(SUM(net_revenue), 0) / 10000.0 AS net_revenue_wanyu,
            COALESCE(SUM(gross_profit), 0) / 10000.0 AS profit_wanyu
        FROM v_sales_detailed
    """).fetchone()

    total_summary = {
        "total_rows": total_row[0] if total_row else 0,
        "total_qty": round(float(total_row[1]), 2) if total_row else 0.0,
        "benti_qty": round(float(total_row[2]), 2) if total_row else 0.0,
        "net_revenue_wanyu": round(float(total_row[3]), 2) if total_row else 0.0,
        "profit_wanyu": round(float(total_row[4]), 2) if total_row else 0.0
    }

    return {
        "cross_summary": cross_summary,
        "channel_summary": channel_summary,
        "total_summary": total_summary
    }


def upsert_to_duckdb(
    df: pd.DataFrame,
    duckdb_path: Path | str = SKILL_DUCKDB_PATH,
    overwrite: bool = False
) -> Dict[str, Any]:
    """
    将清洗后的 DataFrame 写入 DuckDB。
    支持年月分区幂等覆盖 (Partition Upsert) 与全量替换 (Overwrite)。
    返回写入元数据总结字典。
    """
    db_path = Path(duckdb_path).resolve()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    if db_path.exists() and db_path.stat().st_size == 0:
        db_path.unlink()

    con = duckdb.connect(str(db_path))
    try:
        # 获取待导入数据的唯一 (year, month) 集合
        incoming_partitions: List[Tuple[int, int]] = (
            df[["year", "month"]].drop_duplicates().sort_values(["year", "month"]).values.tolist()
        )
        
        tables = [t[0] for t in con.execute("SHOW TABLES").fetchall()]
        table_exists = "sales_data" in tables

        rows_written = len(df)
        replaced_partitions = []

        con.register("df_incoming", df)

        if overwrite or not table_exists:
            # 全量覆写或初次建表
            con.execute("BEGIN TRANSACTION")
            try:
                con.execute("DROP TABLE IF EXISTS sales_data")
                con.execute("CREATE TABLE sales_data AS SELECT * FROM df_incoming")
                con.execute("COMMIT")
            except Exception as e:
                con.execute("ROLLBACK")
                raise e
            mode = "overwrite" if overwrite else "initial_create"
        else:
            # 增量模式：按年月分区幂等覆盖
            con.execute("BEGIN TRANSACTION")
            try:
                for yr, mn in incoming_partitions:
                    con.execute("DELETE FROM sales_data WHERE year = ? AND month = ?", [yr, mn])
                    replaced_partitions.append(f"{yr}年{mn}月")
                con.execute("INSERT INTO sales_data SELECT * FROM df_incoming")
                con.execute("COMMIT")
            except Exception as e:
                con.execute("ROLLBACK")
                raise e
            mode = "incremental_upsert"

        con.unregister("df_incoming")

        # 注入统一语义视图
        apply_skill_semantic_views(con)

        # 汇总信息与对账核算
        total_rows = con.execute("SELECT COUNT(*) FROM sales_data").fetchone()[0]
        db_years = sorted([r[0] for r in con.execute("SELECT DISTINCT year FROM sales_data WHERE year > 0").fetchall()])
        db_months = sorted([r[0] for r in con.execute("SELECT DISTINCT month FROM sales_data WHERE month > 0").fetchall()])

        reconcile_data = get_reconciliation_summary(con)

        return {
            "status": "success",
            "mode": mode,
            "incoming_rows": rows_written,
            "total_rows_in_db": total_rows,
            "incoming_partitions": [f"{y}年{m}月" for y, m in incoming_partitions],
            "replaced_partitions": replaced_partitions,
            "db_years": db_years,
            "db_months": db_months,
            "duckdb_path": str(db_path),
            "reconciliation": reconcile_data
        }
    finally:
        con.close()


def apply_skill_semantic_views(con: duckdb.DuckDBPyConnection):
    """在 DuckDB 中构建统一的 SQL 语义视图层（严格规范 market_channel 与 region 语义）"""
    # 动态检查 sales_data 字段
    cols = [c[0] for c in con.execute("DESCRIBE sales_data;").fetchall()]
    net_amt_expr = "net_amount" if "net_amount" in cols else "net_revenue AS net_amount"
    biz_cat_expr = "biz_category" if "biz_category" in cols else "'' AS biz_category"
    ind_cat_expr = "product_industry_category" if "product_industry_category" in cols else "'' AS product_industry_category"

    # 透传用户自定义/非标准原始列
    standard_projected = {
        "market_channel", "year", "month", "quarter", "region", "province", "country",
        "sales_team", "sales_team_rev", "biz_type", "biz_category", "product_industry_category",
        "product_category", "product_series", "product_subclass", "product_model",
        "report_source", "brand_sector", "property_type", "material_code", "material_desc_raw",
        "material_desc_clean", "terminal_customer", "customer_name", "net_revenue",
        "net_amount", "net_income_wanyu", "raw_sales_qty", "invoice_qty", "invoice_qty_benti",
        "product_cost", "cost_wanyu", "gross_profit", "gross_profit_wanyu"
    }
    extra_cols = [f'"{c}"' for c in cols if c not in standard_projected]
    extra_cols_sql = (",\n        " + ",\n        ".join(extra_cols)) if extra_cols else ""

    con.execute(f"""
    -- 兼容视图
    CREATE OR REPLACE VIEW china_data AS 
    SELECT * FROM sales_data 
    WHERE market_channel = '中国区' OR report_source LIKE '%中国%' OR report_source = '中国区';

    CREATE OR REPLACE VIEW overseas_data AS 
    SELECT * FROM sales_data 
    WHERE market_channel = '海外区' OR report_source LIKE '%国际%' OR report_source LIKE '%海外%';

    -- 全局多维销售分析统一明细视图
    CREATE OR REPLACE VIEW v_sales_detailed AS
    SELECT
        COALESCE(NULLIF(market_channel, ''), CASE 
            WHEN report_source LIKE '%国际%' OR report_source LIKE '%海外%' THEN '海外区'
            ELSE '中国区'
        END) AS market_channel,
        year,
        month,
        COALESCE(quarter, CASE WHEN month BETWEEN 1 AND 3 THEN 'Q1' WHEN month BETWEEN 4 AND 6 THEN 'Q2' WHEN month BETWEEN 7 AND 9 THEN 'Q3' ELSE 'Q4' END) AS quarter,
        region,
        province,
        country,
        sales_team,
        sales_team AS sales_team_rev,
        CASE WHEN report_source LIKE '%海外%' OR market_channel = '海外区' THEN '海外业务' ELSE '渠道业务' END AS biz_type,
        {biz_cat_expr},
        {ind_cat_expr},
        product_category,
        product_series,
        product_subclass,
        COALESCE(NULLIF(product_model, ''), '常规型号') AS product_model,
        report_source,
        brand_sector,
        property_type,
        material_code,
        material_desc_raw,
        material_desc_clean,
        terminal_customer,
        customer_name,
        net_revenue,
        {net_amt_expr},
        net_income_wanyu,
        raw_sales_qty,
        invoice_qty,
        invoice_qty_benti,
        product_cost,
        cost_wanyu,
        gross_profit,
        gross_profit_wanyu{extra_cols_sql}
    FROM sales_data;

    CREATE OR REPLACE VIEW v_sales_all AS SELECT * FROM v_sales_detailed;
    CREATE OR REPLACE VIEW v_chint_cn_sales_all AS SELECT * FROM v_sales_detailed WHERE market_channel = '中国区';
    CREATE OR REPLACE VIEW v_chint_intl_sales AS SELECT * FROM v_sales_detailed WHERE market_channel = '海外区';
    CREATE OR REPLACE VIEW v_chint_cn_sales_acb AS SELECT * FROM v_sales_detailed WHERE market_channel = '中国区' AND product_category IN ('框架', 'ACB', '框架类', '万能式断路器');
    CREATE OR REPLACE VIEW v_chint_cn_sales_mccb AS SELECT * FROM v_sales_detailed WHERE market_channel = '中国区' AND product_category IN ('塑壳', 'MCCB', '塑壳类', '塑料外壳式断路器');
    CREATE OR REPLACE VIEW v_chint_cn_sales_mcb AS SELECT * FROM v_sales_detailed WHERE market_channel = '中国区' AND product_category IN ('微断', 'MCB', 'VF', '虚拟工厂', '微断类', '终端类');
    CREATE OR REPLACE VIEW v_chint_cn_sales_pq AS SELECT * FROM v_sales_detailed WHERE market_channel = '中国区' AND product_category IN ('电能质量', 'PQ', '电能质量类');
    CREATE OR REPLACE VIEW v_chint_cn_sales_atse AS SELECT * FROM v_sales_detailed WHERE market_channel = '中国区' AND product_category IN ('双电源', 'ATSE', 'ATS', '双电源类');
    CREATE OR REPLACE VIEW v_sales_acb AS SELECT * FROM v_sales_detailed WHERE product_category IN ('框架', 'ACB', '框架类', '万能式断路器');
    CREATE OR REPLACE VIEW v_sales_mccb AS SELECT * FROM v_sales_detailed WHERE product_category IN ('塑壳', 'MCCB', '塑壳类', '塑料外壳式断路器');
    CREATE OR REPLACE VIEW v_sales_mcb AS SELECT * FROM v_sales_detailed WHERE product_category IN ('微断', 'MCB', 'VF', '虚拟工厂', '微断类', '终端类');
    CREATE OR REPLACE VIEW v_sales_pq AS SELECT * FROM v_sales_detailed WHERE product_category IN ('电能质量', 'PQ', '电能质量类');
    CREATE OR REPLACE VIEW v_sales_atse AS SELECT * FROM v_sales_detailed WHERE product_category IN ('双电源', 'ATSE', 'ATS', '双电源类');
    """)
