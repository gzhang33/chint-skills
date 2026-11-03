#!/usr/bin/env python3
"""
query_sales.py — 断路器产品经理（ACB/MCCB/MCB/PQ/ATSE/VF）通用多维 OLAP 数据分析模型与速查引擎 (Skill & Project SSOT)

功能特性：
1. 100% 独立便携与自包含：优先读取 Skill 内部 data/sales.duckdb，自动兼容项目数仓。
2. 56 列标准标题全量动态解析与自由组合分组 (-g)，支持动态原始列透明透传（如 '通用/专业'）。
3. 全 56 列通用筛选引擎 (-f)：支持多值逗号匹配 (省份=江苏,浙江)、否定 (!=)、范围 (>=, <=, >, <) 与跨列全局模糊匹配。
4. 专用月份切片 (-m / --months) 与年份过滤 (-y)。
5. 全面支持多维同比 (YoY) 跌幅/增长趋势分析 (--yoy)。
6. 严格按用户指定新老产品配对计算【台数替换率】(-r / --replace-rate "新产品:老产品")，严禁隐式默认计算。
7. 显式打印当前统计口径标签（如【口径: 本体 · 净收入不含税 · 2026年Q1-Q2】），消除口径认知偏差。
8. 严格防御 SQL 注入与单引号转义。
"""

import sys
import os
import argparse
import re
from pathlib import Path
from typing import List, Tuple, Dict, Any, Optional
import duckdb
import pandas as pd

CURRENT_DIR = Path(__file__).resolve().parent

def find_repo_root(start: Path) -> Path:
    cur = start
    for _ in range(6):
        if (cur / "etl").exists() and (cur / "config.py").exists():
            return cur
        if cur.parent == cur:
            break
        cur = cur.parent
    return start.parent

REPO_ROOT = find_repo_root(CURRENT_DIR)
SKILL_DIR = CURRENT_DIR.parent if (CURRENT_DIR.parent / "scripts").exists() and (CURRENT_DIR.parent / "resources").exists() else REPO_ROOT / ".agents" / "skills" / "chint-data-analysis"

SKILL_DATA_DIR = SKILL_DIR / "data"

# 数据仓库不随技能分发，位置由 config_loader 统一解析（$CHINT_SALES_DUCKDB →
# 工作区 Areas/data-analytics/data/ → 技能内部 data/）。
try:
    from config_loader import get_skill_duckdb_path as _resolve_duckdb
except ImportError:
    try:
        from .config_loader import get_skill_duckdb_path as _resolve_duckdb
    except ImportError:
        _resolve_duckdb = None

# 56 列全量标准 Excel 标题到数据库物理字段映射字典
STANDARD_56_COLUMN_MAP: Dict[str, str] = {
    # 基础与地域维度
    "报表来源": "report_source", "数据来源": "report_source", "来源": "report_source",
    "市场": "market_channel", "市场通道": "market_channel", "渠道": "market_channel",
    "产业": "brand_sector", "品牌": "brand_sector",
    "产业分类": "product_industry_category", "产品产业分类": "product_industry_category", # 产业分类（如'低压'）独立映射，绝不污染 product_category
    "业务分类": "biz_category", # 业务分类独立映射，不污染 product_subclass
    "通用/专业": "biz_category", "通用专业": "biz_category", "专业/通用": "biz_category",
    "洲区": "region", "大洲": "region", "国家": "country", "国家名称": "country",
    "省份": "province", "省份名称": "province", "区域": "region", "大区": "region",
    "年份": "year", "月份": "month", "季度": "quarter",
    
    # 产品与物料维度 (涵盖 ACB, MCCB, MCB, PQ, ATSE, 虚拟工厂)
    "物料编码": "material_code", "物料号": "material_code", "物料代码": "material_code",
    "物料描述": "material_desc_raw", "物料名称": "material_desc_raw",
    "修正物料组描述": "material_desc_clean",
    "新政策大类": "product_subclass", "物料组描述": "product_subclass", "物料组": "product_subclass",
    "产品系列": "product_series", "修正产品系列": "product_series", "系列": "product_series", "系列名称": "product_series",
    "产品平台": "product_platform", "平台": "product_platform",
    "产品大类": "product_category", "product_category": "product_category", "产品分类": "product_category",
    "产品经理": "product_manager", "PM": "product_manager",
    "型号": "product_model", "产品型号": "product_model", "规格型号": "product_model",
    "属性": "property_type", "物料属性": "property_type", "产品属性": "property_type",
    "壳架电流": "frame_current", "壳架等级": "frame_current", "分断能力": "breaking_capacity",
    "操作方式": "operation_method", "安装方式": "operation_method",
    "极数": "pole_count", "N极方式": "n_pole_type", "脱扣曲线": "tripping_curve",
    
    # 组织、销售与客户维度 (严格隔离行业与渠道)
    "销售组织": "sales_org", "组织": "sales_org",
    "销售团队": "sales_team", "销售团队修订": "sales_team", "销售团队分类": "sales_team", "团队": "sales_team",
    "业务类型": "biz_type",
    "终端客户": "terminal_customer", "最终用户": "terminal_customer", "行业客户": "terminal_customer", "终端用户名称": "terminal_customer",
    "客户名称": "customer_name", "客户": "customer_name", "买方名称": "customer_name", "经销商": "customer_name", "代理商": "customer_name",
    "大客户": "key_account", "KA": "key_account", "行业": "industry", "行业分类": "industry_category",
    
    # 数值指标 (双物理列隔离保留：net_revenue 与 net_amount)
    "发票数量": "raw_sales_qty", "发票数量(台)": "raw_sales_qty", "销售数量": "raw_sales_qty", "开票数量": "raw_sales_qty", "数量": "raw_sales_qty", "发票台数": "raw_sales_qty",
    "本体台数": "invoice_qty_benti", "本体台数(台)": "invoice_qty_benti", "发票数量_本体": "invoice_qty_benti", "本体数量": "invoice_qty_benti",
    "净额（不含税）": "net_amount", "净额（不含税）(元)": "net_amount", "净额": "net_amount", "开票金额": "net_amount",
    "净收入（不含税）": "net_revenue", "净收入（不含税）(元)": "net_revenue", "净收入": "net_revenue",
    "销售净收入": "net_revenue", "销售净收入(元)": "net_revenue", "销售收入": "net_revenue",
    "产品成本（不含税）": "product_cost", "产品成本（不含税）(元)": "product_cost", "产品成本": "product_cost", "成本": "product_cost",
    "毛利额（不含税）": "gross_profit", "毛利额（不含税）(元)": "gross_profit", "毛利额": "gross_profit", "毛利": "gross_profit"
}


def get_skill_database_connection(custom_path: Optional[str] = None, category: Optional[str] = None) -> duckdb.DuckDBPyConnection:
    """获取 DuckDB 数据库只读连接（自定路径 → 统一解析位置 → 仓库内常见落点 → 技能内任意 .duckdb）"""
    if custom_path:
        p = Path(custom_path).resolve()
        if p.exists():
            return duckdb.connect(str(p), read_only=True)

    cat_code = (category or "acb").lower()
    search_paths = []
    if _resolve_duckdb is not None:
        try:
            search_paths.append(_resolve_duckdb())
        except FileNotFoundError:
            pass
    search_paths += [
        SKILL_DATA_DIR / "sales.duckdb",
        REPO_ROOT / "data" / "database" / f"{cat_code}.duckdb",
        REPO_ROOT / "data" / "database" / "chint_analytics.duckdb",
        REPO_ROOT / "data" / "database" / "acb.duckdb",
        REPO_ROOT / "data" / "database" / "mccb.duckdb",
    ]

    for p in search_paths:
        if p.exists():
            return duckdb.connect(str(p), read_only=True)

    # 检索 Skill 内部所有 .duckdb
    candidates = list(SKILL_DATA_DIR.glob("*.duckdb"))
    if candidates:
        return duckdb.connect(str(candidates[0]), read_only=True)

    print("❌ [Error] 未找到可用 DuckDB 数据库文件。已查找：")
    for p in search_paths:
        print(f"   - {p}")
    print("💡 提示: 销售数据仓库不随技能分发。设置 CHINT_SALES_DUCKDB 指向数据库文件，")
    print("   或把数据文件放到工作区 Areas/data-analytics/data/sales.duckdb，")
    print("   或先运行 ingest_user_data.py 从 Excel 生成：")
    print("   python3 scripts/ingest_user_data.py --file /path/to/data.xlsx")
    sys.exit(1)


def resolve_column_expr(title: str, table_cols: List[str]) -> str:
    """将 Excel 中文标题动态解析为 DuckDB SQL 列名或派生计算表达式"""
    clean_title = title.strip()
    
    # 市场渠道 / 渠道
    if clean_title in ("市场", "市场通道", "渠道", "market_channel"):
        if "market_channel" in table_cols:
            return "market_channel"

    # 季度派生
    if clean_title in ("季度", "quarter"):
        if "quarter" in table_cols:
            return "quarter"
        if "month" in table_cols:
            return "CASE WHEN month IN (1,2,3) THEN 'Q1' WHEN month IN (4,5,6) THEN 'Q2' WHEN month IN (7,8,9) THEN 'Q3' ELSE 'Q4' END"

    # 映射表解析
    mapped_col = STANDARD_56_COLUMN_MAP.get(clean_title, clean_title)
    
    # 列存在性校验（直接匹配）
    if mapped_col in table_cols:
        return mapped_col
    
    # 大小写不敏感匹配
    lower_map = {c.lower(): c for c in table_cols}
    if mapped_col.lower() in lower_map:
        return lower_map[mapped_col.lower()]
    if clean_title.lower() in lower_map:
        return lower_map[clean_title.lower()]
    
    # 常用业务字段备选降级 (保留合理降级，绝不将 region 降级为 province)
    if mapped_col in ("terminal_customer", "customer_name") and "sales_team" in table_cols:
        return "sales_team"
    if mapped_col == "product_model" and "product_subclass" in table_cols:
        return "product_subclass"

    # 若底层表包含该原始列名（如'通用/专业'），直接使用双引号透传
    if clean_title in table_cols:
        return f'"{clean_title}"'

    return mapped_col


def build_property_clause(prop_mode: str) -> Tuple[str, str]:
    """根据属性模式构建过滤条件与数量字段"""
    if prop_mode in ("benti", "本体"):
        return "property_type = '本体'", "invoice_qty_benti"
    elif prop_mode in ("non_benti", "非本体", "附件"):
        return "property_type != '本体'", "raw_sales_qty"
    elif prop_mode in ("all", "全量", "全部"):
        return "", "raw_sales_qty"
    else:
        return "property_type = '本体'", "invoice_qty_benti"


def parse_filter_to_sql_conditions(filter_str: str, table_cols: List[str]) -> List[str]:
    """
    通用 56 列通用筛选器解析引擎：
    支持：
      1. 多值逗号枚举: 省份=江苏,浙江,广东 -> province IN ('江苏', '浙江', '广东')
      2. 否定与精确匹配: 属性=本体, 产品系列!=NXA
      3. 数值与大小比较: 月份>=3, 净收入（不含税）>100000
      4. 跨列全局模糊匹配: 未带操作符时自动匹配系列/物料/客户/省份
    """
    if not filter_str:
        return []

    raw_tokens = []
    for part in filter_str.replace("；", ";").split(";"):
        part = part.strip()
        if part:
            raw_tokens.append(part)

    sql_conditions = []
    operators = [">=", "<=", "!=", ">", "<", "="]

    for token in raw_tokens:
        matched_op = None
        for op in operators:
            if op in token:
                matched_op = op
                break

        if not matched_op:
            # 跨列模糊搜索
            safe_kw = token.replace("'", "''")
            search_clause = (
                f"(CAST(product_series AS VARCHAR) ILIKE '%{safe_kw}%' "
                f"OR CAST(material_desc_clean AS VARCHAR) ILIKE '%{safe_kw}%' "
                f"OR CAST(product_category AS VARCHAR) ILIKE '%{safe_kw}%' "
                f"OR CAST(sales_team AS VARCHAR) ILIKE '%{safe_kw}%' "
                f"OR CAST(province AS VARCHAR) ILIKE '%{safe_kw}%' "
                f"OR CAST(terminal_customer AS VARCHAR) ILIKE '%{safe_kw}%' "
                f"OR CAST(customer_name AS VARCHAR) ILIKE '%{safe_kw}%')"
            )
            sql_conditions.append(search_clause)
            continue

        raw_col, raw_val = token.split(matched_op, 1)
        col_name = raw_col.strip()
        val_str = raw_val.strip()
        col_expr = resolve_column_expr(col_name, table_cols)

        is_num_col = col_name in ("月份", "month", "年份", "year", "发票数量", "净额（不含税）", "净收入（不含税）", "成本", "毛利")

        # 1. 包含逗号的多值枚举匹配 (如 "省份=江苏,浙江,广东")
        if "," in val_str and matched_op in ("=", "!="):
            val_items = [v.strip().replace("'", "''") for v in val_str.split(",") if v.strip()]
            if val_items:
                if is_num_col or all(v.isdigit() for v in val_items):
                    in_list = ", ".join(val_items)
                    expr = f"CAST({col_expr} AS NUMERIC) {'NOT IN' if matched_op == '!=' else 'IN'} ({in_list})"
                else:
                    in_list = ", ".join([f"'{v}'" for v in val_items])
                    expr = f"CAST({col_expr} AS VARCHAR) {'NOT IN' if matched_op == '!=' else 'IN'} ({in_list})"
                sql_conditions.append(expr)
            continue

        # 2. 单值比较匹配
        safe_val = val_str.replace("'", "''")
        if matched_op == "=":
            if is_num_col or safe_val.isdigit():
                sql_conditions.append(f"CAST({col_expr} AS VARCHAR) = '{safe_val}'")
            else:
                sql_conditions.append(f"CAST({col_expr} AS VARCHAR) ILIKE '%{safe_val}%'")
        elif matched_op == "!=":
            if is_num_col or safe_val.isdigit():
                sql_conditions.append(f"CAST({col_expr} AS VARCHAR) != '{safe_val}'")
            else:
                sql_conditions.append(f"NOT (CAST({col_expr} AS VARCHAR) ILIKE '%{safe_val}%')")
        elif matched_op in (">=", "<=", ">", "<"):
            sql_conditions.append(f"TRY_CAST({col_expr} AS NUMERIC) {matched_op} {safe_val}")

    return sql_conditions


def query_dynamic(
    conn: duckdb.DuckDBPyConnection,
    group_by_str: str,
    category: str = "all",
    year: int = 2026,
    months: Optional[List[int]] = None,
    prop_mode: str = "benti",
    filter_str: Optional[str] = None,
    top: int = 10,
    yoy: bool = False,
    show_all: bool = False
) -> str:
    """通用多维 OLAP 分析执行器"""
    group_titles = [g.strip() for g in group_by_str.split(",") if g.strip()]
    if not group_titles:
        group_titles = ["产品系列"]

    cat_lower = category.lower()
    is_intl = cat_lower in ("intl", "overseas", "海外", "海外区")
    
    tables = [t[0] for t in conn.execute("SHOW TABLES").fetchall()]
    if is_intl:
        view_name = "v_chint_intl_sales" if "v_chint_intl_sales" in tables else "overseas_data"
    elif cat_lower in ("china", "cn", "国内", "中国区"):
        view_name = "v_chint_cn_sales_all" if "v_chint_cn_sales_all" in tables else "china_data"
    elif cat_lower in ("acb", "mccb", "pq", "atse", "vf", "mcb"):
        if f"v_sales_{cat_lower}" in tables:
            view_name = f"v_sales_{cat_lower}"
        elif f"v_chint_cn_sales_{cat_lower}" in tables:
            view_name = f"v_chint_cn_sales_{cat_lower}"
        else:
            view_name = "v_sales_detailed" if "v_sales_detailed" in tables else "sales_data"
    else:
        view_name = "v_sales_detailed" if "v_sales_detailed" in tables else ("v_sales_all" if "v_sales_all" in tables else "sales_data")

    table_cols = [c[0] for c in conn.execute(f"DESCRIBE {view_name};").fetchall()]

    db_cols = []
    seen_exprs = set()
    for title in group_titles:
        expr = resolve_column_expr(title, table_cols)
        # 校验字段合法性
        raw_field = expr.strip('"')
        if expr not in seen_exprs:
            if raw_field not in table_cols and not expr.startswith("CASE"):
                print(f"❌ [Error] 无法识别分组字段 '{title}'！")
                print(f"💡 当前视图 ({view_name}) 支持的字段清单:\n   {', '.join(table_cols)}")
                sys.exit(1)
            db_cols.append((expr, title))
            seen_exprs.add(expr)

    group_select = ", ".join([f'{expr} AS "{title}"' for expr, title in db_cols])
    group_by_indexes = ", ".join([str(i + 1) for i in range(len(db_cols))])

    prop_clause, qty_col = build_property_clause(prop_mode)

    where_conditions = []
    if prop_clause and "property_type" in table_cols:
        where_conditions.append(prop_clause)

    # 针对分组维度自动剔除空字符串与'海外'伪省份，防止空分组
    for t in group_titles:
        expr = resolve_column_expr(t, table_cols)
        raw_field = expr.strip('"')
        if raw_field in table_cols:
            if t in ("省份", "province"):
                where_conditions.append(f"({expr} IS NOT NULL AND TRIM(CAST({expr} AS VARCHAR)) != '' AND CAST({expr} AS VARCHAR) != '海外')")
            else:
                where_conditions.append(f"({expr} IS NOT NULL AND TRIM(CAST({expr} AS VARCHAR)) != '')")

    if months and "month" in table_cols:
        months_clean = [int(m) for m in months if str(m).isdigit() and 1 <= int(m) <= 12]
        if months_clean:
            where_conditions.append(f"month IN ({', '.join(str(m) for m in months_clean)})")

    if cat_lower not in ("all", "全部", "全品类", "intl", "overseas", "海外", "海外区", "china", "cn", "国内", "中国区") and "product_category" in table_cols:
        cat_upper = category.upper()
        if cat_upper in ("ACB", "框架", "框架类", "万能式断路器"):
            cat_list = "'ACB', '框架', '框架类', '万能式断路器'"
        elif cat_upper in ("MCCB", "塑壳", "塑壳类", "塑料外壳式断路器"):
            cat_list = "'MCCB', '塑壳', '塑壳类', '塑料外壳式断路器'"
        elif cat_upper in ("MCB", "微断", "微断类", "终端类", "终端配电类"):
            cat_list = "'MCB', '微断', '微断类', '终端类', '终端配电类'"
        elif cat_upper in ("PQ", "电能质量", "电能质量类"):
            cat_list = "'PQ', '电能质量', '电能质量类'"
        elif cat_upper in ("ATS", "ATSE", "双电源", "双电源类"):
            cat_list = "'ATS', 'ATSE', '双电源', '双电源类'"
        elif cat_upper in ("VF", "虚拟工厂", "其它低压类", "其他低压类"):
            cat_list = "'VF', '虚拟工厂', '其它低压类', '其他低压类'"
        else:
            cat_list = f"'{category}', '{cat_upper}'"
        where_conditions.append(f"product_category IN ({cat_list})")

    if filter_str:
        custom_conds = parse_filter_to_sql_conditions(filter_str, table_cols)
        where_conditions.extend(custom_conds)

    prev_year = year - 1
    limit_clause = "" if show_all else f"LIMIT {top}"

    order_by_clause = f'ORDER BY "{year}年销售额(万元)" DESC' if yoy else 'ORDER BY "销售净收入(万元)" DESC'
    if group_titles and group_titles[0] in ("月份", "month", "季度", "quarter", "年份", "year"):
        order_by_clause = f'ORDER BY "{group_titles[0]}" ASC'

    month_desc = f" (1-{max(months)}月 YTD)" if months and len(months) > 1 and min(months) == 1 else (f" ({','.join(str(m) for m in months)}月)" if months else "")

    if yoy:
        year_cond = f"year IN ({year}, {prev_year})"
        all_where = [year_cond] + where_conditions
        where_sql = "WHERE " + " AND ".join(all_where)

        sql = f"""
        SELECT 
            {group_select},
            ROUND(SUM(CASE WHEN year = {year} THEN net_revenue ELSE 0 END) / 10000.0, 2) AS "{year}年销售额(万元)",
            ROUND(SUM(CASE WHEN year = {prev_year} THEN net_revenue ELSE 0 END) / 10000.0, 2) AS "{prev_year}年销售额(万元)",
            ROUND((SUM(CASE WHEN year = {year} THEN net_revenue ELSE 0 END) - SUM(CASE WHEN year = {prev_year} THEN net_revenue ELSE 0 END)) / 10000.0, 2) AS "销售额增减(万元)",
            ROUND(
                (SUM(CASE WHEN year = {year} THEN net_revenue ELSE 0 END) - SUM(CASE WHEN year = {prev_year} THEN net_revenue ELSE 0 END))
                / NULLIF(SUM(CASE WHEN year = {prev_year} THEN net_revenue ELSE 0 END), 0) * 100.0, 2
            ) AS "销售额同比(%)",
            ROUND(SUM(CASE WHEN year = {year} THEN {qty_col} ELSE 0 END), 0) AS "{year}年发票台数(台)",
            ROUND(SUM(CASE WHEN year = {prev_year} THEN {qty_col} ELSE 0 END), 0) AS "{prev_year}年发票台数(台)",
            ROUND(
                (SUM(CASE WHEN year = {year} THEN {qty_col} ELSE 0 END) - SUM(CASE WHEN year = {prev_year} THEN {qty_col} ELSE 0 END))
                / NULLIF(SUM(CASE WHEN year = {prev_year} THEN {qty_col} ELSE 0 END), 0) * 100.0, 2
            ) AS "台数同比(%)",
            ROUND(SUM(CASE WHEN year = {year} THEN gross_profit ELSE 0 END) / NULLIF(SUM(CASE WHEN year = {year} THEN net_revenue ELSE 0 END), 0) * 100.0, 2) AS "{year}年毛利率(%)"
        FROM {view_name}
        {where_sql}
        GROUP BY {group_by_indexes}
        {order_by_clause}
        {limit_clause};
        """
    else:
        year_cond = f"year = {year}"
        all_where = [year_cond] + where_conditions
        where_sql = "WHERE " + " AND ".join(all_where)

        sql = f"""
        SELECT 
            {group_select},
            ROUND(SUM(net_revenue) / 10000.0, 2) AS "销售净收入(万元)",
            ROUND(SUM({qty_col}), 0) AS "发票数量(台)",
            ROUND(SUM(gross_profit) / 10000.0, 2) AS "毛利额(万元)",
            ROUND(SUM(gross_profit) / NULLIF(SUM(net_revenue), 0) * 100.0, 2) AS "毛利率(%)"
        FROM {view_name}
        {where_sql}
        GROUP BY {group_by_indexes}
        {order_by_clause}
        {limit_clause};
        """

    df = conn.execute(sql).fetchdf()

    title_suffix = f"{year}年 vs {prev_year}年 YoY 趋势对比" if yoy else f"{year}年"
    scope_tag = "海外区" if is_intl else ("全品类" if category.lower() in ("all", "全部") else category.upper())
    prop_tag = "本体" if prop_mode == "benti" else ("非本体/附件" if prop_mode == "non_benti" else "全部(含附件)")
    rev_tag = "净收入(不含税)"

    lines = [
        f"═══ 📊 CHINT 多维 OLAP 分析 [{', '.join(group_titles)}] ═══",
        f"【统计口径: {prop_tag} · {rev_tag} · 品类: {scope_tag} · 期间: {title_suffix}{month_desc}】",
        ""
    ]
    if df.empty:
        lines.append("⚠️ 未查到符合条件的数据记录（请检查年份、月份或过滤条件）。")
    else:
        lines.append(df.to_string(index=False))

    return "\n".join(lines)


def query_replace_rate(
    conn: duckdb.DuckDBPyConnection,
    pair_str: str,
    group_by_str: Optional[str] = "省份",
    category: str = "all",
    year: int = 2026,
    months: Optional[List[int]] = None,
    prop_mode: str = "benti",
    filter_str: Optional[str] = None,
    top: int = 10,
    show_all: bool = False
) -> str:
    """
    新老产品台数替换率专用分析引擎：
    严格根据用户指定的 GroupA 与 GroupB 计算：
    台数替换率 (%) = GroupA 发票台数 / (GroupA 发票台数 + GroupB 发票台数) * 100%
    """
    if not pair_str or ":" not in str(pair_str):
        print(f"❌ [Error] 替换率计算必须显式指定新老产品配对！")
        print("💡 正确格式为 '新产品:老产品'，例如:")
        print("   -r 'NXA:NA1'")
        print("   -r '昆仑:1系列'")
        print("   -r 'NXM:NM1'")
        sys.exit(1)

    raw_a, raw_b = pair_str.split(":", 1)
    group_a_items = [v.strip().replace("'", "''") for v in raw_a.split(",") if v.strip()]
    group_b_items = [v.strip().replace("'", "''") for v in raw_b.split(",") if v.strip()]

    if not group_a_items or not group_b_items:
        print("❌ [Error] 新产品组或老产品组不能为空！请提供有效的产品配对 (例如 -r 'NXA:NA1')。")
        sys.exit(1)

    group_a_label = raw_a.strip()
    group_b_label = raw_b.strip()

    group_titles = [g.strip() for g in (group_by_str or "省份").split(",") if g.strip()]
    cat_lower = category.lower()
    is_intl = cat_lower in ("intl", "overseas", "海外", "海外区")
    
    tables = [t[0] for t in conn.execute("SHOW TABLES").fetchall()]
    if is_intl:
        view_name = "v_chint_intl_sales" if "v_chint_intl_sales" in tables else "overseas_data"
    elif cat_lower in ("china", "cn", "国内", "中国区"):
        view_name = "v_chint_cn_sales_all" if "v_chint_cn_sales_all" in tables else "china_data"
    elif cat_lower in ("acb", "mccb", "pq", "atse", "vf", "mcb"):
        if f"v_sales_{cat_lower}" in tables:
            view_name = f"v_sales_{cat_lower}"
        elif f"v_chint_cn_sales_{cat_lower}" in tables:
            view_name = f"v_chint_cn_sales_{cat_lower}"
        else:
            view_name = "v_sales_detailed" if "v_sales_detailed" in tables else "sales_data"
    else:
        view_name = "v_sales_detailed" if "v_sales_detailed" in tables else ("v_sales_all" if "v_sales_all" in tables else "sales_data")

    table_cols = [c[0] for c in conn.execute(f"DESCRIBE {view_name};").fetchall()]

    db_cols = []
    seen_exprs = set()
    for title in group_titles:
        expr = resolve_column_expr(title, table_cols)
        if expr not in seen_exprs:
            db_cols.append((expr, title))
            seen_exprs.add(expr)

    group_select = ", ".join([f'{expr} AS "{title}"' for expr, title in db_cols])
    group_by_indexes = ", ".join([str(i + 1) for i in range(len(db_cols))])

    prop_clause, qty_col = build_property_clause(prop_mode)

    where_conditions = [f"year = {year}"]
    if prop_clause and "property_type" in table_cols:
        where_conditions.append(prop_clause)

    for t in group_titles:
        expr = resolve_column_expr(t, table_cols)
        raw_field = expr.strip('"')
        if raw_field in table_cols:
            if t in ("省份", "province"):
                where_conditions.append(f"({expr} IS NOT NULL AND TRIM(CAST({expr} AS VARCHAR)) != '' AND CAST({expr} AS VARCHAR) != '海外')")
            else:
                where_conditions.append(f"({expr} IS NOT NULL AND TRIM(CAST({expr} AS VARCHAR)) != '')")

    if months and "month" in table_cols:
        months_clean = [int(m) for m in months if str(m).isdigit() and 1 <= int(m) <= 12]
        if months_clean:
            where_conditions.append(f"month IN ({', '.join(str(m) for m in months_clean)})")

    if cat_lower not in ("all", "全部", "全品类", "intl", "overseas", "海外", "海外区", "china", "cn", "国内", "中国区") and "product_category" in table_cols:
        cat_upper = category.upper()
        if cat_upper in ("ACB", "框架", "框架类", "万能式断路器"):
            cat_list = "'ACB', '框架', '框架类', '万能式断路器'"
        elif cat_upper in ("MCCB", "塑壳", "塑壳类", "塑料外壳式断路器"):
            cat_list = "'MCCB', '塑壳', '塑壳类', '塑料外壳式断路器'"
        elif cat_upper in ("MCB", "微断", "微断类", "终端类", "终端配电类"):
            cat_list = "'MCB', '微断', '微断类', '终端类', '终端配电类'"
        elif cat_upper in ("PQ", "电能质量", "电能质量类"):
            cat_list = "'PQ', '电能质量', '电能质量类'"
        elif cat_upper in ("ATS", "ATSE", "双电源", "双电源类"):
            cat_list = "'ATS', 'ATSE', '双电源', '双电源类'"
        elif cat_upper in ("VF", "虚拟工厂", "其它低压类", "其他低压类"):
            cat_list = "'VF', '虚拟工厂', '其它低压类', '其他低压类'"
        else:
            cat_list = f"'{category}', '{cat_upper}'"
        where_conditions.append(f"product_category IN ({cat_list})")

    if filter_str:
        custom_conds = parse_filter_to_sql_conditions(filter_str, table_cols)
        where_conditions.extend(custom_conds)

    # 匹配条件 (同时支持产品系列、型号与物料描述包含)
    pm_expr = resolve_column_expr("产品型号", table_cols)
    ps_expr = resolve_column_expr("产品系列", table_cols)

    cond_a_parts = []
    for it in group_a_items:
        cond_a_parts.append(f"({ps_expr} = '{it}' OR {pm_expr} = '{it}' OR CAST(material_desc_clean AS VARCHAR) ILIKE '%{it}%')")
    match_a = " OR ".join(cond_a_parts)

    cond_b_parts = []
    for it in group_b_items:
        cond_b_parts.append(f"({ps_expr} = '{it}' OR {pm_expr} = '{it}' OR CAST(material_desc_clean AS VARCHAR) ILIKE '%{it}%')")
    match_b = " OR ".join(cond_b_parts)

    # 仅统计涉及 A 与 B 的数据行
    where_conditions.append(f"(({match_a}) OR ({match_b}))")
    where_sql = "WHERE " + " AND ".join(where_conditions)

    limit_clause = "" if show_all else f"LIMIT {top}"
    order_by_clause = f'ORDER BY "{group_a_label}台数(台)" DESC'

    sql = f"""
    SELECT 
        {group_select},
        ROUND(SUM(CASE WHEN ({match_a}) THEN {qty_col} ELSE 0 END), 0) AS "{group_a_label}台数(台)",
        ROUND(SUM(CASE WHEN ({match_b}) THEN {qty_col} ELSE 0 END), 0) AS "{group_b_label}台数(台)",
        ROUND(
            SUM(CASE WHEN ({match_a}) THEN {qty_col} ELSE 0 END)
            / NULLIF(SUM(CASE WHEN ({match_a}) OR ({match_b}) THEN {qty_col} ELSE 0 END), 0) * 100.0, 2
        ) AS "替换率(%)"
    FROM {view_name}
    {where_sql}
    GROUP BY {group_by_indexes}
    {order_by_clause}
    {limit_clause};
    """

    df = conn.execute(sql).fetchdf()

    month_desc = f" (1-{max(months)}月 YTD)" if months and len(months) > 1 and min(months) == 1 else (f" ({','.join(str(m) for m in months)}月)" if months else "")
    scope_tag = "海外区" if is_intl else ("全品类" if category.lower() in ("all", "全部") else category.upper())
    prop_tag = "本体" if prop_mode == "benti" else ("非本体/附件" if prop_mode == "non_benti" else "全部(含附件)")

    lines = [
        f"═══ 🔄 CHINT 新老产品台数替换率分析 [{', '.join(group_titles)}] ═══",
        f"【统计口径: {prop_tag} · 替换配对: {group_a_label} 替换 {group_b_label} · 品类: {scope_tag} · 期间: {year}年{month_desc}】",
        ""
    ]
    if df.empty:
        lines.append(f"⚠️ 未查到关于「{group_a_label}」与「{group_b_label}」的相关销售记录。")
    else:
        lines.append(df.to_string(index=False))

    return "\n".join(lines)


def query_overview(
    conn: duckdb.DuckDBPyConnection,
    category: str = "all",
    year: int = 2026,
    months: Optional[List[int]] = None,
    prop_mode: str = "benti"
) -> str:
    """大盘全景概览"""
    tables = [t[0] for t in conn.execute("SHOW TABLES").fetchall()]
    view_name = "v_sales_detailed" if "v_sales_detailed" in tables else (tables[0] if tables else "sales_data")

    prop_clause, qty_col = build_property_clause(prop_mode)
    where_parts = []
    if prop_clause and "property_type" in [c[0] for c in conn.execute(f"DESCRIBE {view_name}").fetchall()]:
        where_parts.append(prop_clause)
    if months:
        where_parts.append(f"month IN ({', '.join(str(m) for m in months)})")
    if category.lower() not in ("all", "全部", "全品类"):
        cat_upper = category.upper()
        if cat_upper in ("ACB", "框架", "框架类", "万能式断路器"):
            cat_list = "'ACB', '框架', '框架类', '万能式断路器'"
        elif cat_upper in ("MCCB", "塑壳", "塑壳类", "塑料外壳式断路器"):
            cat_list = "'MCCB', '塑壳', '塑壳类', '塑料外壳式断路器'"
        elif cat_upper in ("MCB", "微断", "微断类", "终端类", "终端配电类"):
            cat_list = "'MCB', '微断', '微断类', '终端类', '终端配电类'"
        elif cat_upper in ("PQ", "电能质量", "电能质量类"):
            cat_list = "'PQ', '电能质量', '电能质量类'"
        elif cat_upper in ("ATS", "ATSE", "双电源", "双电源类"):
            cat_list = "'ATS', 'ATSE', '双电源', '双电源类'"
        elif cat_upper in ("VF", "虚拟工厂", "其它低压类", "其他低压类"):
            cat_list = "'VF', '虚拟工厂', '其它低压类', '其他低压类'"
        else:
            cat_list = f"'{category}', '{cat_upper}'"
        where_parts.append(f"product_category IN ({cat_list})")

    where_curr = " AND ".join([f"year = {year}"] + where_parts)
    where_prev = " AND ".join([f"year = {year - 1}"] + where_parts)

    q_curr = f"SELECT SUM(net_revenue), SUM({qty_col}), SUM(gross_profit) FROM {view_name} WHERE {where_curr};"
    q_prev = f"SELECT SUM(net_revenue), SUM({qty_col}), SUM(gross_profit) FROM {view_name} WHERE {where_prev};"

    r_curr = conn.execute(q_curr).fetchone()
    r_prev = conn.execute(q_prev).fetchone()

    sales_curr = (r_curr[0] or 0.0) if r_curr else 0.0
    sales_prev = (r_prev[0] or 0.0) if r_prev else 0.0
    qty_curr = (r_curr[1] or 0.0) if r_curr else 0.0
    qty_prev = (r_prev[1] or 0.0) if r_prev else 0.0
    gp_curr = (r_curr[2] or 0.0) if r_curr else 0.0

    yoy_sales = ((sales_curr - sales_prev) / sales_prev * 100.0) if sales_prev > 0 else 0.0
    yoy_qty = ((qty_curr - qty_prev) / qty_prev * 100.0) if qty_prev > 0 else 0.0
    gp_rate = (gp_curr / sales_curr * 100.0) if sales_curr > 0 else 0.0

    month_str = f"1-{max(months)}月 YTD" if months and min(months) == 1 else (f"{','.join(str(m) for m in months)}月" if months else "全年")
    prop_desc = "本体" if prop_mode == "benti" else ("附件" if prop_mode == "non_benti" else "全部(含附件)")

    lines = [
        f"═══ 🌟 CHINT 配电设备销售大盘概览 ═══",
        f"【统计口径: {prop_desc} · 净收入不含税 · 品类: {category.upper()} · 期间: {year}年 · {month_str}】",
        f"• 净收入（不含税）: {sales_curr / 10000.0:,.2f} 万元 (同比: {yoy_sales:+.2f}%)",
        f"• 发票数量: {qty_curr:,.0f} 台 ({prop_desc}, 同比: {yoy_qty:+.2f}%)",
        f"• 整体毛利率: {gp_rate:.2f}%",
        f"",
        f"【品牌构成】"
    ]

    q_brand = f"""
    SELECT 
        CASE WHEN report_source LIKE '%诺雅克%' THEN '诺雅克' ELSE '正泰' END AS brand,
        ROUND(SUM(net_revenue) / 10000.0, 2) AS sales_wanyu,
        ROUND(SUM({qty_col}), 0) AS qty_tai
    FROM {view_name}
    WHERE {where_curr}
    GROUP BY 1;
    """
    for bname, bsales, bqty in conn.execute(q_brand).fetchall():
        bsales = bsales or 0.0
        bqty = bqty or 0.0
        bshare = (bsales / (sales_curr / 10000.0) * 100.0) if sales_curr > 0 else 0.0
        lines.append(f"  ├─ {bname}品牌: {bsales:,.2f} 万元 (占比 {bshare:.1f}%, 发票台数 {bqty:,.0f} 台)")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="CHINT 断路器产品经理通用多维 OLAP 分析引擎 (SSOT)"
    )
    parser.add_argument("--group-by", "-g", default=None, help="自由分组维度（支持 56 列标准标题，如 '终端客户', '客户名称', '产品系列,省份', '市场', '通用/专业'）")
    parser.add_argument("--category", "-c", default="all", help="品类: acb, mccb, mcb, intl, all (默认 all)")
    parser.add_argument("--query-type", "-q", default="overview", choices=["overview", "series", "region", "customer", "industry"], help="快捷预设查询")
    parser.add_argument("--property", "-p", default="benti", choices=["benti", "non_benti", "all"], help="属性口径: benti(默认本体台数), non_benti(非本体/附件), all(全量)")
    parser.add_argument("--year", "-y", type=int, default=2026, help="分析目标年份 (默认 2026)")
    parser.add_argument("--months", "-m", default=None, help="月份范围切片 (例如 '1,2,3,4,5,6,7' 或 '7')")
    parser.add_argument("--filter", "-f", default=None, help="56 列全能条件过滤 (例如 '省份=江苏,浙江' 或 '属性=本体;产品大类=ACB')")
    parser.add_argument("--replace-rate", "-r", default=None, help="新老产品台数替换率分析（必须显式指定配对 '新产品:老产品'，例如 -r 'NXA:NA1' 或 -r '昆仑:1系列'）")
    parser.add_argument("--top", "-n", type=int, default=10, help="返回前 N 条记录 (默认 10)")
    parser.add_argument("--all", "-a", action="store_true", help="返回全量记录（不受 -n 限制）")
    parser.add_argument("--yoy", action="store_true", help="开启多维同比 (YoY) 跌幅/增长趋势对比")
    parser.add_argument("--db-path", default=None, help="自定义 DuckDB 文件路径")

    args = parser.parse_args()

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    month_list = None
    if args.months:
        month_list = [int(m.strip()) for m in str(args.months).split(",") if m.strip().isdigit()]

    conn = get_skill_database_connection(args.db_path, category=args.category)
    try:
        # 1. 替换率分析优先级最高
        if args.replace_rate is not None:
            print(query_replace_rate(
                conn=conn,
                pair_str=args.replace_rate,
                group_by_str=args.group_by or "省份",
                category=args.category,
                year=args.year,
                months=month_list,
                prop_mode=args.property,
                filter_str=args.filter,
                top=args.top,
                show_all=args.all
            ))
        elif args.group_by:
            print(query_dynamic(
                conn=conn,
                group_by_str=args.group_by,
                category=args.category,
                year=args.year,
                months=month_list,
                prop_mode=args.property,
                filter_str=args.filter,
                top=args.top,
                yoy=args.yoy,
                show_all=args.all
            ))
        elif args.filter and not args.group_by:
            print(query_dynamic(
                conn=conn,
                group_by_str="产品大类,产品系列",
                category=args.category,
                year=args.year,
                months=month_list,
                prop_mode=args.property,
                filter_str=args.filter,
                top=args.top,
                yoy=args.yoy,
                show_all=args.all
            ))
        elif args.query_type == "overview":
            print(query_overview(
                conn=conn,
                category=args.category,
                year=args.year,
                months=month_list,
                prop_mode=args.property
            ))
        elif args.query_type == "series":
            print(query_dynamic(
                conn=conn,
                group_by_str="产品系列",
                category=args.category,
                year=args.year,
                months=month_list,
                prop_mode=args.property,
                filter_str=args.filter,
                top=args.top,
                yoy=args.yoy,
                show_all=args.all
            ))
        elif args.query_type == "region":
            print(query_dynamic(
                conn=conn,
                group_by_str="省份",
                category=args.category,
                year=args.year,
                months=month_list,
                prop_mode=args.property,
                filter_str=args.filter,
                top=args.top,
                yoy=args.yoy,
                show_all=args.all
            ))
        elif args.query_type == "industry":
            print(query_dynamic(
                conn=conn,
                group_by_str="终端客户",
                category=args.category,
                year=args.year,
                months=month_list,
                prop_mode=args.property,
                filter_str=args.filter,
                top=args.top,
                yoy=args.yoy,
                show_all=args.all
            ))
        elif args.query_type == "customer":
            print(query_dynamic(
                conn=conn,
                group_by_str="客户名称",
                category=args.category,
                year=args.year,
                months=month_list,
                prop_mode=args.property,
                filter_str=args.filter,
                top=args.top,
                yoy=args.yoy,
                show_all=args.all
            ))
    finally:
        conn.close()


if __name__ == "__main__":
    main()
