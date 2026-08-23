"""
etl/query_engine.py — 统一 DuckDB 数据分析查询引擎与共享层 (Single Source of Truth)

集中管理：
1. 12+ 业务分析维度映射字典 (DIM_COL_MAP)
2. 核心财务与实物算子映射字典 (METRIC_MAP)
3. 语义隔离视图选择器 (resolve_view_name)
4. 多维透视 SQL 生成器 (build_pivot_sql)
5. 全量大屏 6 大面板 SQL 聚合引擎 (build_full_dashboard_sqls)
"""

import os
import re
import sys
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union
import duckdb

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))




# ── 1. 维度字段集中映射字典 (涵盖 6 大动态映射派生列及全量 49 物理原始字段) ─────────────
DIM_COL_MAP: Dict[str, str] = {
    "market_channel": "COALESCE(NULLIF(TRIM(market_channel), ''), CASE WHEN report_source LIKE '%中国区%' THEN '中国区' ELSE '海外区' END)",
    "market": "COALESCE(NULLIF(TRIM(market_channel), ''), CASE WHEN report_source LIKE '%中国区%' THEN '中国区' ELSE '海外区' END)",
    "product_series": "COALESCE(NULLIF(TRIM(product_series), ''), '其他')",
    "product_series_raw": "COALESCE(NULLIF(TRIM(product_series), ''), '其他')",
    "series_name": "COALESCE(NULLIF(TRIM(product_series), ''), '其他')",
    "sales_team": "COALESCE(NULLIF(TRIM(sales_team_rev), ''), NULLIF(TRIM(sales_team), ''), '其他')",
    "sales_team_raw": "COALESCE(NULLIF(TRIM(sales_team), ''), '其他')",
    "sales_team_rev": "COALESCE(NULLIF(TRIM(sales_team_rev), ''), NULLIF(TRIM(sales_team), ''), '其他')",
    "industry": "COALESCE(NULLIF(TRIM(brand_sector), ''), '正泰电器')",
    "brand_sector": "COALESCE(NULLIF(TRIM(brand_sector), ''), '正泰电器')",
    "product_manager": "COALESCE(NULLIF(TRIM(sales_team), ''), '其他')",
    "province": "COALESCE(NULLIF(TRIM(province), ''), '其他')",
    "region": "COALESCE(NULLIF(TRIM(region_rev), ''), '其他')",
    "region_rev": "COALESCE(NULLIF(TRIM(region_rev), ''), '其他')",
    "terminal_customer": "COALESCE(NULLIF(TRIM(terminal_customer), ''), '通用客户')",
    "customer_name": "COALESCE(NULLIF(TRIM(customer_name), ''), '通用客户')",
    "customer_nature": "COALESCE(NULLIF(TRIM(customer_nature), ''), '未分类')",
    "customer_no": "COALESCE(NULLIF(TRIM(customer_no), ''), '未提供')",
    "outlet_customer_no": "COALESCE(NULLIF(TRIM(outlet_customer_no), ''), '未提供')",
    "outlet_customer_name": "COALESCE(NULLIF(TRIM(outlet_customer_name), ''), '未提供')",
    "country": "COALESCE(NULLIF(TRIM(country), ''), '中国')",
    "country_name": "COALESCE(NULLIF(TRIM(country_name), ''), NULLIF(TRIM(country), ''), '中国')",
    "continent": "COALESCE(NULLIF(TRIM(continent), ''), '中国区')",
    "report_source": "COALESCE(NULLIF(TRIM(report_source), ''), '中国区')",
    "report_source_rev": "CASE WHEN report_source LIKE '%中国区%' OR report_source IN ('中国区-正泰', '中国区-诺雅克', '中国区') THEN '中国区' WHEN report_source = '国际' OR report_source LIKE '%国际%' OR report_source LIKE '%海外%' OR report_source = '海外区' THEN '国际' ELSE '中国区' END",
    "property_type": "COALESCE(NULLIF(TRIM(property_type), ''), '本体')",
    "property_type_rev": "COALESCE(NULLIF(TRIM(property_type), ''), '本体')",
    "product_model": "COALESCE(NULLIF(TRIM(product_model), ''), '常规型号')",
    "product_model_rev": "COALESCE(NULLIF(TRIM(product_model), ''), '常规型号')",
    "material_code": "COALESCE(NULLIF(TRIM(material_code), ''), NULLIF(TRIM(material_desc), ''), '未知型号')",
    "material_desc": "COALESCE(NULLIF(TRIM(material_desc), ''), NULLIF(TRIM(material_code), ''), '未知描述')",
    "material_desc_rev": "REPLACE(COALESCE(CAST(material_desc AS VARCHAR), ''), '~', '~~')",
    "material_group_code": "COALESCE(NULLIF(TRIM(material_group_code), ''), '未分类')",
    "material_group_desc": "COALESCE(NULLIF(TRIM(material_group_desc), ''), '未分类')",
    "material_group_desc_rev": "COALESCE(NULLIF(TRIM(material_group_desc_rev), ''), NULLIF(TRIM(product_model), ''), NULLIF(TRIM(material_group_desc), ''), '常规型号')",
    "project_no": "COALESCE(NULLIF(TRIM(project_no), ''), '未立项')",
    "project_name": "COALESCE(NULLIF(TRIM(project_name), ''), '非项目')",
    "sales_org": "COALESCE(NULLIF(TRIM(sales_org), ''), '通用销售部')",
    "sales_org_code": "COALESCE(NULLIF(TRIM(sales_org_code), ''), '未分类')",
    "mfg_unit": "COALESCE(NULLIF(TRIM(mfg_unit), ''), '本部')",
    "mfg_unit_code": "COALESCE(NULLIF(TRIM(mfg_unit_code), ''), '未分类')",
    "biz_category": "COALESCE(NULLIF(TRIM(biz_category), ''), '渠道业务')",
    "biz_type": "COALESCE(NULLIF(TRIM(biz_type_rev), ''), '渠道业务')",
    "biz_type_rev": "COALESCE(NULLIF(TRIM(biz_type_rev), ''), '渠道业务')",
    "new_policy_category": "COALESCE(NULLIF(TRIM(new_policy_category), ''), '常规')",
    "internal_customer_flag": "COALESCE(NULLIF(TRIM(internal_customer_flag), ''), '否')",
    "general_or_specialized": "COALESCE(NULLIF(TRIM(general_or_specialized), ''), '通用')",
    "product_platform": "COALESCE(NULLIF(TRIM(product_platform), ''), '其它')",
    "product_manager_team": "COALESCE(NULLIF(TRIM(product_manager_team), ''), '产品部')",
    "product_industry_category": "COALESCE(NULLIF(TRIM(product_industry_category), ''), '低压配电')",
    "currency": "COALESCE(NULLIF(TRIM(currency), ''), 'CNY')",
    "exchange_rate": "COALESCE(exchange_rate, 1.0)",
    "revenue_local_currency": "COALESCE(revenue_local_currency, net_revenue, 0)",
    "cost_local_currency": "COALESCE(cost_local_currency, product_cost, 0)",
    "billing_price_amount": "COALESCE(billing_price_amount, 0)",
    "settlement_price_amount": "COALESCE(settlement_price_amount, 0)",
    "net_amount": "COALESCE(net_amount, 0)",
    "discount_amount": "COALESCE(discount_amount, 0)",
    "expense_amount": "COALESCE(expense_amount, 0)",
    "pocket_price": "COALESCE(pocket_price, 0)",
    "revenue": "COALESCE(net_revenue, 0)",
    "net_revenue": "COALESCE(net_revenue, 0)",
    "qty": "COALESCE(invoice_qty, 0)",
    "sales_qty": "COALESCE(invoice_qty, 0)",
    "invoice_qty": "COALESCE(invoice_qty, 0)",
    "invoice_qty_benti": "COALESCE(invoice_qty_benti, invoice_qty, 0)",
    "cost": "COALESCE(product_cost, 0)",
    "product_cost": "COALESCE(product_cost, 0)",
    "total_cost": "COALESCE(total_cost, product_cost, 0)",
    "gross_profit": "COALESCE(gross_profit, 0)",
    "gross_margin_rate": "ROUND(COALESCE(gross_margin_rate, 0), 2)",
    "replace_rate": "0",
    "kunlun_replace_rate": "0",
    "yoy_growth_rate": "0",
    "product_category": "COALESCE(NULLIF(TRIM(product_category), ''), '低压配电')",
    "frame_current": "COALESCE(frame_current, '通用壳架')",
    "breaking_capacity": "COALESCE(breaking_capacity, '标准分断')",
    "operation_method": "COALESCE(operation_method, '标准操作')",
    "installation_type": "COALESCE(operation_method, '抽屉式')",
    "pole_count": "COALESCE(pole_count, '未指定极数')",
    "n_pole_type": "COALESCE(n_pole_type, '无')",
    "biz_type": "biz_type",
    "business_type": "biz_type",
    "is_overseas_str": "COALESCE(market_channel, '中国区')",
    "year": "CAST(year AS VARCHAR)",
    "quarter": "CASE WHEN CAST(month AS INTEGER) BETWEEN 1 AND 3 THEN 'Q1' WHEN CAST(month AS INTEGER) BETWEEN 4 AND 6 THEN 'Q2' WHEN CAST(month AS INTEGER) BETWEEN 7 AND 9 THEN 'Q3' ELSE 'Q4' END",
    "quarter_rev": "COALESCE(quarter_rev, quarter, CASE WHEN CAST(month AS INTEGER) BETWEEN 1 AND 3 THEN 'Q1' WHEN CAST(month AS INTEGER) BETWEEN 4 AND 6 THEN 'Q2' WHEN CAST(month AS INTEGER) BETWEEN 7 AND 9 THEN 'Q3' ELSE 'Q4' END)",
    "month": "CAST(month AS VARCHAR)",
    "acb_frame_current": "COALESCE(frame_current, '2000A壳架')",
    "acb_installation_type": "COALESCE(operation_method, '抽屉式')",
    "mccb_breaking_capacity": "COALESCE(breaking_capacity, 'S型标准')",
    "mccb_frame_size": "COALESCE(frame_current, '250A壳架')",
    "mcb_pole_count": "COALESCE(pole_count, '3P')",
    "n_pole_connection": "COALESCE(n_pole_type, '无N极')",
}

# 汉语列名向内部维度 Key 的容错映射 (供 CLI 与自然语言交互)
CHINESE_COL_ALIAS: Dict[str, str] = {
    "报表来源": "report_source",
    "数据来源": "report_source",
    "市场": "report_source",
    "市场通道": "report_source",
    "国内国际": "report_source",
    "中国海外": "report_source",
    "区域范围": "report_source",
    "sales_team_cls": "sales_team",
    "产品系列": "product_series",
    "销售团队": "sales_team",
    "销售团队分类": "sales_team",
    "销售团队映射": "sales_team",
    "行业团队": "sales_team",
    "业务类型": "biz_type",
    "型号": "product_model",
    "壳架电流": "frame_current",
    "壳架": "frame_current",
    "壳架代号": "frame_current",
    "分断能力": "breaking_capacity",
    "分断代号": "breaking_capacity",
    "分断": "breaking_capacity",
    "安装方式": "operation_method",
    "操作方式": "operation_method",
    "极数": "pole_count",
    "N极连接方式": "n_pole_type",
    "N极连接": "n_pole_type",
    "省份": "province",
    "区域": "region",
    "大区": "region",
    "洲区": "continent",
    "终端客户": "terminal_customer",
    "客户名称": "customer_name",
    "客户性质": "customer_nature",
    "客户号": "customer_no",
    "网点客户号": "outlet_customer_no",
    "网点客户名称": "outlet_customer_name",
    "物料编码": "material_code",
    "物料描述": "material_desc",
    "物料组编码": "material_group_code",
    "物料组描述": "material_group_desc",
    "项目编号": "project_no",
    "项目名称": "project_name",
    "销售组织": "sales_org",
    "销售组织编码": "sales_org_code",
    "生产制造单位": "mfg_unit",
    "生产制造单位编码": "mfg_unit_code",
    "新政策大类": "new_policy_category",
    "产业": "brand_sector",
    "品牌板块": "brand_sector",
    "品牌": "brand_sector",
    "industry": "brand_sector",
    "brand_sector": "brand_sector",
    "业务分类": "biz_category",
    "发票数量": "invoice_qty",
    "开单价金额": "billing_price_amount",
    "开单价金额（含税）": "billing_price_amount",
    "结算价金额": "settlement_price_amount",
    "结算价金额（含税）": "settlement_price_amount",
    "净额": "net_amount",
    "净额（不含税）": "net_amount",
    "折让": "discount_amount",
    "折让（不含税）": "discount_amount",
    "费用": "expense_amount",
    "费用（不含税）": "expense_amount",
    "净收入（不含税）": "revenue",
    "口袋价": "pocket_price",
    "口袋价（含税）": "pocket_price",
    "产品成本（不含税）": "cost",
    "总成本": "total_cost",
    "总成本（不含税）": "total_cost",
    "毛利额（不含税）": "gross_profit",
    "本位币种": "currency",
    "汇率": "exchange_rate",
    "汇率(本币)": "exchange_rate",
    "收入（本币）": "revenue_local_currency",
    "成本（本币）": "cost_local_currency",
    "产品产业分类": "product_industry_category",
    "通用/专业": "general_or_specialized",
    "产品平台": "product_platform",
    "产品管理团队": "product_manager_team",
    "产品大类": "product_category",
    "内配客户标记": "internal_customer_flag",
    "国家": "country",
    "国家名称": "country",
    "年份": "year",
    "月份": "month",
    "季度": "quarter",
    "属性": "property_type",
    "产品经理": "product_manager",
    "产品型号": "product_model",
    "ACB壳架电流": "acb_frame_current",
    "ACB安装方式": "acb_installation_type",
    "分段代号": "mccb_breaking_capacity",
    "MCCB分断能力": "mccb_breaking_capacity",
    "壳架等级": "mccb_frame_size",
    "MCB极数": "mcb_pole_count",
    "替换率": "replace_rate",
    "昆仑替换率": "replace_rate",
    "replace_rate": "replace_rate",
    "kunlun_replace_rate": "replace_rate",
    "同比增长率": "yoy_growth_rate",
    "毛利率": "gross_margin_rate",
}


# ── 2. 算子/指标集中映射字典 ─────────────────────────────────
METRIC_MAP: Dict[str, Tuple[str, str]] = {
    "revenue": ("revenue", "ROUND(SUM(net_revenue), 2)"),
    "net_revenue": ("revenue", "ROUND(SUM(net_revenue), 2)"),
    "total_net_revenue": ("revenue", "ROUND(SUM(net_revenue), 2)"),
    "qty": ("qty", "ROUND(SUM(invoice_qty), 0)"),
    "invoice_qty": ("qty", "ROUND(SUM(invoice_qty), 0)"),
    "quantity": ("qty", "ROUND(SUM(invoice_qty), 0)"),
    "total_qty": ("qty", "ROUND(SUM(invoice_qty), 0)"),
    "benti_qty": ("benti_qty", "ROUND(SUM(invoice_qty_benti), 0)"),
    "invoice_qty_benti": ("benti_qty", "ROUND(SUM(invoice_qty_benti), 0)"),
    "cost": ("cost", "ROUND(SUM(product_cost), 2)"),
    "product_cost": ("cost", "ROUND(SUM(product_cost), 2)"),
    "gross_profit": ("gross_profit", "ROUND(SUM(gross_profit), 2)"),
    "gross_margin": ("gross_margin_rate", "ROUND(SUM(gross_profit) / NULLIF(SUM(net_revenue), 0) * 100.0, 2)"),
    "gross_margin_rate": ("gross_margin_rate", "ROUND(SUM(gross_profit) / NULLIF(SUM(net_revenue), 0) * 100.0, 2)"),
    "margin": ("gross_margin_rate", "ROUND(SUM(gross_profit) / NULLIF(SUM(net_revenue), 0) * 100.0, 2)"),
    "margin_rate": ("gross_margin_rate", "ROUND(SUM(gross_profit) / NULLIF(SUM(net_revenue), 0) * 100.0, 2)"),
}



# ── 3. 视图查找与路由 ───────────────────────────────────────
def resolve_view_name(product_class: Optional[str], year: Optional[Union[int, str]] = 2026, con: Any = None) -> str:
    """自动解析路由 DuckDB 语义视图名称 (全球全量无损视图: 中国区 + 海外区)"""
    cat = (product_class or "acb").lower()
    if cat in ("intl", "overseas", "foreign", "海外", "国际"):
        return "v_chint_intl_sales"
    elif cat in ("acb", "mccb", "pq", "atse", "vf", "mcb"):
        view_name = f"v_sales_{cat if cat != 'mcb' else 'vf'}"
        if con is not None:
            try:
                year_clause = f"WHERE year = {int(year)}" if (year is not None and str(year).lower() != "all") else ""
                cnt = con.execute(f"SELECT COUNT(*) FROM {view_name} {year_clause}").fetchone()[0]
                if cnt == 0:
                    return "v_sales_all"
            except Exception:
                pass
        return view_name
    return "v_sales_all"


def resolve_max_month_condition(
    year: Optional[Union[int, str]] = 2026,
    quarter: Optional[str] = "all",
    view_name: str = "v_sales_all",
    con: Any = None
) -> Tuple[int, str]:
    """
    计算动态同比月份对齐条件 (Apple-to-Apple 同月份区间对比)
    返回: (max_month, m_cond_sql)
    示例: (6, "AND month <= 6")
    """
    max_month = 12
    q_lower = (quarter or "all").lower()
    if q_lower == "q1":
        max_month = 3
    elif q_lower == "q2":
        max_month = 6
    elif q_lower == "q3":
        max_month = 9
    elif q_lower == "q4":
        max_month = 12
    elif con and year is not None and str(year).lower() != "all":
        try:
            res = con.execute(f"SELECT COALESCE(MAX(month), 12) FROM {view_name} WHERE year = {int(year)}").fetchone()
            if res and res[0]:
                max_month = int(res[0])
        except Exception:
            max_month = 12
    else:
        max_month = 12

    m_cond = f"AND month <= {max_month}" if max_month < 12 else ""
    return max_month, m_cond


def build_yoy_metric_selects(
    metrics: List[str],
    target_year: int,
    prev_year: int,
    m_cond: str = "",
    qty_col: str = "invoice_qty_benti"
) -> List[str]:
    """
    统一生成带有同区间 (m_cond) 约束的绝对值与同比 (YoY) SQL 表达式列表
    """
    metric_selects = []
    for m in metrics:
        if m in ("revenue", "total_net_revenue", "销售净收入"):
            metric_selects.append(
                f'ROUND(SUM(CASE WHEN year = {target_year} {m_cond} THEN net_revenue ELSE 0 END), 2) AS "销售净收入 (元)"'
            )
            metric_selects.append(
                f'ROUND((SUM(CASE WHEN year = {target_year} {m_cond} THEN net_revenue ELSE 0 END) - SUM(CASE WHEN year = {prev_year} {m_cond} THEN net_revenue ELSE 0 END)) / NULLIF(ABS(SUM(CASE WHEN year = {prev_year} {m_cond} THEN net_revenue ELSE 0 END)), 0) * 100.0, 2) AS "销售净收入 同比 (%)"'
            )
        elif m in ("qty", "quantity", "benti_qty", "本体发票台数"):
            metric_selects.append(
                f'ROUND(SUM(CASE WHEN year = {target_year} {m_cond} THEN {qty_col} ELSE 0 END), 0) AS "本体发票台数 (台)"'
            )
            metric_selects.append(
                f'ROUND((SUM(CASE WHEN year = {target_year} {m_cond} THEN {qty_col} ELSE 0 END) - SUM(CASE WHEN year = {prev_year} {m_cond} THEN {qty_col} ELSE 0 END)) / NULLIF(ABS(SUM(CASE WHEN year = {prev_year} {m_cond} THEN {qty_col} ELSE 0 END)), 0) * 100.0, 2) AS "本体发票台数 同比 (%)"'
            )
        elif m in ("cost", "产品成本"):
            metric_selects.append(
                f'ROUND(SUM(CASE WHEN year = {target_year} {m_cond} THEN product_cost ELSE 0 END), 2) AS "产品成本 (元)"'
            )
            metric_selects.append(
                f'ROUND((SUM(CASE WHEN year = {target_year} {m_cond} THEN product_cost ELSE 0 END) - SUM(CASE WHEN year = {prev_year} {m_cond} THEN product_cost ELSE 0 END)) / NULLIF(ABS(SUM(CASE WHEN year = {prev_year} {m_cond} THEN product_cost ELSE 0 END)), 0) * 100.0, 2) AS "产品成本 同比 (%)"'
            )
        elif m in ("gross_profit", "毛利额"):
            metric_selects.append(
                f'ROUND(SUM(CASE WHEN year = {target_year} {m_cond} THEN gross_profit ELSE 0 END), 2) AS "毛利额 (元)"'
            )
            metric_selects.append(
                f'ROUND((SUM(CASE WHEN year = {target_year} {m_cond} THEN gross_profit ELSE 0 END) - SUM(CASE WHEN year = {prev_year} {m_cond} THEN gross_profit ELSE 0 END)) / NULLIF(ABS(SUM(CASE WHEN year = {prev_year} {m_cond} THEN gross_profit ELSE 0 END)), 0) * 100.0, 2) AS "毛利额 同比 (%)"'
            )
        elif m in ("gross_margin_rate", "毛利率"):
            metric_selects.append(
                f'ROUND(SUM(CASE WHEN year = {target_year} {m_cond} THEN gross_profit ELSE 0 END) / NULLIF(SUM(CASE WHEN year = {target_year} {m_cond} THEN net_revenue ELSE 0 END), 0) * 100.0, 2) AS "毛利率 (%)"'
            )
            metric_selects.append(
                f'ROUND(COALESCE(SUM(CASE WHEN year = {target_year} {m_cond} THEN gross_profit ELSE 0 END) / NULLIF(SUM(CASE WHEN year = {target_year} {m_cond} THEN net_revenue ELSE 0 END), 0) * 100.0, 0.0) - COALESCE(SUM(CASE WHEN year = {prev_year} {m_cond} THEN gross_profit ELSE 0 END) / NULLIF(SUM(CASE WHEN year = {prev_year} {m_cond} THEN net_revenue ELSE 0 END), 0) * 100.0, 0.0), 2) AS "毛利率 同比 (pp)"'
            )

    if not metric_selects:
        metric_selects.append(
            f'ROUND(SUM(CASE WHEN year = {target_year} {m_cond} THEN net_revenue ELSE 0 END), 2) AS "销售净收入 (元)"'
        )
        metric_selects.append(
            f'ROUND((SUM(CASE WHEN year = {target_year} {m_cond} THEN net_revenue ELSE 0 END) - SUM(CASE WHEN year = {prev_year} {m_cond} THEN net_revenue ELSE 0 END)) / NULLIF(ABS(SUM(CASE WHEN year = {prev_year} {m_cond} THEN net_revenue ELSE 0 END)), 0) * 100.0, 2) AS "销售净收入 同比 (%)"'
        )
    return metric_selects


# ── 4. 多维透视与明细钻取 SQL 翻译引擎 (应用层 A 方案) ────────────
MAX_PIVOT_COLS = 500


def sanitize_identifier(field_name: str) -> str:
    """
    标识符转义与安全校验函数
    双引号包裹有效标识符字符（支持中文、英文字母、数字、#、·、¥、各种常用符号及 Unicode 文本），
    严禁 SQL 注入危险字符（单引号、分号、双引号、注释符、空字节），校验非空防注入。
    """
    if not isinstance(field_name, str):
        raise ValueError(f"Identifier must be a string, got {type(field_name)}")

    clean_name = field_name.strip()
    if clean_name.startswith('"') and clean_name.endswith('"') and len(clean_name) >= 2:
        clean_name = clean_name[1:-1].strip()

    if not clean_name:
        raise ValueError("Invalid identifier: empty string")

    # 严禁危险的 SQL 注入字符与控制字符
    if re.search(r'["\';\x00]|\-\-|\/\*', clean_name):
        raise ValueError(f"Invalid identifier '{field_name}': contains illegal or dangerous characters")

    # 允许包含所有常见合法标点与符号（含 #, ·, [, ], ¥, $, @, ~, *, ?, !, =, <, >, \, ^, 中文标点等）
    if not re.match(r'^[\u4e00-\u9fa5a-zA-Z0-9_\s\-\(\)\%\/\.\+\&\,\#\·\[\]\¥\$\*\?\!\=\<\>\\\^\~\@\:\（\）\【\】\、\：\；\。\℃\±\≤\≥]+$', clean_name):
        raise ValueError(f"Invalid identifier '{field_name}': contains unsupported characters")

    return f'"{clean_name}"'


DIM_LABEL_MAP: Dict[str, str] = {
    "market_channel": "报表来源",
    "market": "报表来源",
    "product_model": "产品型号",
    "product_series": "产品系列",
    "series_name": "产品系列",
    "revenue": "销售净收入 (元)",
    "net_revenue": "销售净收入 (元)",
    "qty": "总台数 (台)",
    "total_qty": "总台数 (台)",
    "benti_qty": "本体台数 (台)",
    "sales_qty": "销售台数 (台)",
    "raw_sales_qty": "原始开票数 (台)",
    "invoice_qty": "发票数量",
    "invoice_qty_benti": "本体台数 (台)",
    "cost": "产品成本 (元)",
    "product_cost": "产品成本 (元)",
    "gross_profit": "毛利额 (元)",
    "replace_rate": "替换率",
    "kunlun_replace_rate": "替换率",
    "yoy_growth_rate": "同比增长率",
    "gross_margin_rate": "毛利率",
    "sales_team": "销售团队",
    "sales_team_rev": "销售团队",
    "industry": "产业",
    "brand_sector": "产业",
    "product_manager": "产品经理",
    "province": "省份",
    "region": "区域",
    "terminal_customer": "终端客户",
    "customer_name": "客户名称",
    "customer_nature": "客户性质",
    "customer_no": "客户号",
    "outlet_customer_name": "网点客户名称",
    "country": "国家",
    "continent": "洲区",
    "report_source": "报表来源",
    "property_type": "属性",
    "is_overseas_str": "区域类型",
    "year": "年份",
    "quarter": "季度",
    "month": "月份",
    "material_code": "物料编码",
    "material_desc": "物料描述",
    "material_group_code": "物料组编码",
    "material_group_desc": "物料组描述",
    "material_group_desc_rev": "物料组描述",
    "biz_type": "业务分类",
    "biz_type_rev": "业务分类",
    "biz_category": "业务分类",
    "report_source_rev": "报表来源",
    "region_rev": "区域",
    "project_no": "项目编号",
    "project_name": "项目名称",
    "sales_org": "销售组织",
    "mfg_unit": "生产制造单位",
    "biz_category": "业务分类",
    "billing_price_amount": "开单价金额",
    "settlement_price_amount": "结算价金额",
    "net_amount": "净额",
    "discount_amount": "折让",
    "expense_amount": "费用",
    "pocket_price": "口袋价",
    "currency": "本位币种",
    "product_platform": "产品平台",
    "product_manager_team": "产品管理团队",
    "product_category": "产品大类",
    "internal_customer_flag": "内配客户标记",
    "biz_type": "业务类型",
    "business_type": "业务类型",
    "acb_frame_current": "壳架电流",
    "acb_installation_type": "安装方式",
    "mccb_breaking_capacity": "分断能力",
    "mccb_frame_size": "壳架等级",
    "mcb_pole_count": "极数",
    "n_pole_connection": "N极连接方式",
    "frame_current": "壳架电流",
    "breaking_capacity": "分断能力",
    "operation_method": "安装方式",
    "installation_type": "安装方式",
    "pole_count": "极数",
    "n_pole_type": "N极连接方式",
}


class PivotSQLTranslator:
    """
    PivotSQLTranslator — 纯 Python DuckDB 数据透视 SQL 翻译器 (应用层 A 方案)
    支持：
    - 安全标识符转义 (sanitize_identifier) 防 SQL 注入
    - 多行维度 + ROLLUP 动态层级小计/总计 (`_grouping_id`)
    - 多列维度交叉透视 (CASE WHEN 动态列展开，最大限制 500 列)
    - 窗口函数占比 (percent_of_total, percent_of_row, percent_of_col, percent_of_parent_row, difference_from_total, rank)
    - 列树 (column_tree) 数据元信息输出
    """

    def __init__(
        self,
        row_dims: Optional[List[str]] = None,
        col_dims: Optional[Union[str, List[str]]] = None,
        col_dim: Optional[str] = None,
        metrics: Optional[List[Union[str, dict, Any]]] = None,
        year: Optional[int] = 2026,
        product_class: Optional[str] = "acb",
        property_type: Optional[str] = "all",
        quarter: Optional[str] = "all",
        include_subtotals: bool = True,
        limit: int = 500,
        con: Any = None,
        filters: Optional[Dict[str, Any]] = None,
        date_hierarchy: bool = False,
        numeric_grouping: Optional[Dict[str, Dict[str, Any]]] = None,
        top_n: Optional[Dict[str, Any]] = None,
    ):
        self.raw_row_dims = row_dims or []
        self.date_hierarchy = date_hierarchy
        # 数值分组配置: {dim_id: {'step': float, 'start': float|None, 'end': float|None}}
        # 对齐 Excel 透视表 "右键数值列 → 创建组 → 步长分组" 能力
        self.numeric_grouping: Dict[str, Dict[str, Any]] = numeric_grouping or {}
        # Top N 值筛选配置 (对齐 Excel 透视表 "值筛选 → 前 10 项/后 10 项")
        # 格式: {'enabled': bool, 'count': int, 'direction': 'top'|'bottom', 'metric': str}
        # 仅作用于行维度明细行 (_grouping_id === 0)，不影响小计与总计行
        self.top_n: Optional[Dict[str, Any]] = top_n
        # 维度 Key -> 数值分组 SQL 表达式 的运行时缓存 (translate 阶段填充)
        self._numeric_group_exprs: Dict[str, str] = {}
        # 维度 Key -> 分组后展示标签 的运行时缓存 (translate 阶段填充)
        self._numeric_group_labels: Dict[str, str] = {}

        # 兼容多列 col_dims 与单列 col_dim
        if col_dims is not None:
            if isinstance(col_dims, str):
                self.raw_col_dims = [col_dims] if col_dims else []
            else:
                self.raw_col_dims = [cd for cd in col_dims if cd]
        elif col_dim:
            self.raw_col_dims = [col_dim]
        else:
            self.raw_col_dims = []

        self.metrics_raw = metrics or ["revenue", "qty"]
        self.year = year
        self.product_class = product_class or "acb"
        self.property_type = property_type or "all"
        self.quarter = quarter or "all"
        self.include_subtotals = include_subtotals
        self.limit = limit
        self.con = con
        self.filters = filters or {}

        if self.top_n is None and self.filters:
            raw_top_n = self.filters.get("__top_n__") or self.filters.get("top_n") or self.filters.get("topN")
            if isinstance(raw_top_n, list) and len(raw_top_n) > 0:
                first_val = raw_top_n[0]
                if isinstance(first_val, str):
                    try:
                        self.top_n = json.loads(first_val)
                    except Exception:
                        pass
                elif isinstance(first_val, dict):
                    self.top_n = first_val
            elif isinstance(raw_top_n, dict):
                self.top_n = raw_top_n
            elif isinstance(raw_top_n, str):
                try:
                    self.top_n = json.loads(raw_top_n)
                except Exception:
                    pass

        self.column_tree: List[Dict[str, Any]] = []
        self.grouping_meta: Dict[str, Any] = {}
        self.sql: str = ""
        self.view_name: str = ""
        self.available_cols: set = set()

    def _normalize_dim_key(self, dim: str) -> str:
        """把中文/别名维度 key 统一转换成内部规范 Key"""
        return CHINESE_COL_ALIAS.get(dim, dim)

    def _has_yoy_metric(self) -> bool:
        """检查当前查询是否包含同比增长率衍生指标（兼容字典、Pydantic 对象及字符串）"""
        for m in (self.metrics_raw or []):
            if isinstance(m, dict):
                f = str(m.get("field") or m.get("id") or m.get("alias") or m.get("label") or "")
            elif hasattr(m, "field") or hasattr(m, "id"):
                f = str(getattr(m, "field", None) or getattr(m, "id", None) or getattr(m, "alias", None) or getattr(m, "label", None) or "")
            else:
                f = str(m)
            f_l = f.lower()
            if "yoy" in f_l or "同比" in f:
                return True
        return False

    def _has_mom_metric(self) -> bool:
        """检查当前查询是否包含环比增长率衍生指标（兼容字典、Pydantic 对象及字符串）"""
        for m in (self.metrics_raw or []):
            if isinstance(m, dict):
                f = str(m.get("field") or m.get("id") or m.get("alias") or m.get("label") or "")
            elif hasattr(m, "field") or hasattr(m, "id"):
                f = str(getattr(m, "field", None) or getattr(m, "id", None) or getattr(m, "alias", None) or getattr(m, "label", None) or "")
            else:
                f = str(m)
            f_l = f.lower()
            if "mom" in f_l or "环比" in f:
                return True
        return False

    def _get_default_year(self) -> int:
        """获取默认分析年份：优先读取传入年份，次之从数据库动态获取 MAX(year)，兜底为当前自然年"""
        if self.year is not None and str(self.year).isdigit():
            return int(self.year)
        if self.con is not None:
            try:
                res = self.con.execute("SELECT MAX(year) FROM sales_data WHERE year IS NOT NULL").fetchone()
                if res and res[0] is not None:
                    return int(res[0])
            except Exception:
                pass
        import datetime
        return datetime.datetime.now().year

    def _resolve_mom_period(self) -> Tuple[int, int, int, int]:
        """解析环比的目标年、目标月、基期年、基期月（支持智能跨年回溯 1月 vs 上年12月）"""
        target_year = self._get_default_year()
        month_filter = self.filters.get("month") or self.filters.get("selectedMonth") or self.filters.get("selected_month")
        target_month = None
        if month_filter is not None:
            if isinstance(month_filter, (list, tuple, set)):
                valid_m = [int(m) for m in month_filter if str(m).isdigit()]
                if valid_m:
                    target_month = max(valid_m)
            elif str(month_filter).isdigit():
                target_month = int(month_filter)

        if target_month is None:
            import datetime
            target_month = self._get_max_available_month(target_year) or datetime.datetime.now().month

        if target_month == 1:
            prev_year = target_year - 1
            prev_month = 12
        else:
            prev_year = target_year
            prev_month = target_month - 1

        return target_year, target_month, prev_year, prev_month

    def _get_max_available_month(self, target_year: int) -> Optional[int]:
        """获取目标年份在当前品类数据库中的最大有效数据月份 (如 2026 年实际有 1-7 月时返回 7)"""
        if self.con is not None:
            try:
                view_name = resolve_view_name(self.product_class, target_year, self.con)
                res = self.con.execute(
                    f"SELECT MAX(month) FROM {view_name} WHERE year = {target_year} AND month IS NOT NULL"
                ).fetchone()
                if res and res[0] is not None:
                    return int(res[0])
            except Exception:
                pass
        return None

    # 日期层次分组支持的日期维度集合 (年/季度/月/发票日期)
    DATE_DIM_KEYS = {"year", "quarter", "month", "invoice_date"}
    # 日期层次完整顺序: 年 -> 季度 -> 月
    DATE_HIERARCHY_ORDER = ["year", "quarter", "month"]

    def build_date_hierarchy_sql(self, date_column: str) -> List[str]:
        """
        构建日期层次分组的 SQL 表达式列表 (年/季度/月三个层次)。
        使用 DuckDB EXTRACT 函数从日期列提取层次值，对齐 Excel 透视表
        "右键日期列 → 创建组 → 年/季度/月" 的自动层次展开能力。

        Args:
            date_column: 日期列名 (如 'invoice_date' 或 'month')

        Returns:
            长度为 3 的 SQL 表达式列表，依次对应年/季度/月:
            - EXTRACT(YEAR FROM {date_column})::INTEGER AS year
            - EXTRACT(QUARTER FROM {date_column})::INTEGER AS quarter
            - EXTRACT(MONTH FROM {date_column})::INTEGER AS month
        """
        safe_col = sanitize_identifier(date_column)
        return [
            f"EXTRACT(YEAR FROM {safe_col})::INTEGER AS year",
            f"EXTRACT(QUARTER FROM {safe_col})::INTEGER AS quarter",
            f"EXTRACT(MONTH FROM {safe_col})::INTEGER AS month",
        ]

    def _expand_date_hierarchy(self, dims: List[str]) -> List[str]:
        """
        检测维度列表中的日期类型维度，并自动展开为完整的年→季度→月层次结构。

        展开规则 (对齐 Excel 透视表日期分组):
        - 含 'month' 或 'invoice_date' -> ['year', 'quarter', 'month']
        - 含 'quarter' (不含 month) -> ['year', 'quarter']
        - 含 'year' (不含 quarter/month) -> ['year']
        - 非日期维度保持原位

        当 self.date_hierarchy=False 时，直接返回原维度列表不做展开。

        Args:
            dims: 已规范化的维度 Key 列表

        Returns:
            展开后的维度 Key 列表 (日期维度被替换为完整层次)
        """
        if not self.date_hierarchy or not dims:
            return list(dims)

        norm_dims = [self._normalize_dim_key(d) for d in dims]
        date_dims_present = {d for d in norm_dims if d in self.DATE_DIM_KEYS}
        if not date_dims_present:
            return list(dims)

        # 确定日期层次展开的终止层级
        if "month" in date_dims_present or "invoice_date" in date_dims_present:
            hierarchy = list(self.DATE_HIERARCHY_ORDER)  # year, quarter, month
        elif "quarter" in date_dims_present:
            hierarchy = ["year", "quarter"]
        else:  # only year
            hierarchy = ["year"]

        # 用完整层次替换原列表中的日期维度 (保持非日期维度的相对顺序)
        expanded: List[str] = []
        hierarchy_inserted = False
        for d in dims:
            norm_d = self._normalize_dim_key(d)
            if norm_d in self.DATE_DIM_KEYS:
                if not hierarchy_inserted:
                    expanded.extend(hierarchy)
                    hierarchy_inserted = True
                # 跳过原日期维度 (已被层次替换)
            else:
                expanded.append(d)

        # 若原列表仅含日期维度且已被全部替换
        if not hierarchy_inserted:
            expanded.extend(hierarchy)

        return expanded

    def build_numeric_grouping_sql(
        self,
        column: str,
        step: float,
        start: Optional[float] = None,
        end: Optional[float] = None,
    ) -> str:
        """
        构建数值步长分组的 SQL CASE WHEN 表达式 (对齐 Excel 透视表
        "右键数值列 → 创建组 → 步长分组" 能力)。

        将连续数值列按固定步长切分为离散区间标签，例如 step=100 时生成：
            CASE WHEN col < 100 THEN '0-100'
                 WHEN col < 200 THEN '100-200'
                 ...
                 ELSE '900+' END

        Args:
            column: 数值列的 SQL 表达式 (已转义或为聚合表达式)
            step: 分组步长 (必须 > 0)
            start: 可选起始值；未提供时从数据 MIN 推断 (需运行期子查询)
            end: 可选结束值；未提供时从数据 MAX 推断 (需运行期子查询)

        Returns:
            DuckDB CASE WHEN 表达式字符串，输出区间标签 (VARCHAR)
        """
        if step is None or float(step) <= 0:
            raise ValueError(f"Numeric grouping step must be positive, got {step}")

        step_f = float(step)
        start_f = float(start) if start is not None else None
        end_f = float(end) if end is not None else None

        # 区间边界对齐到步长网格 (Excel 行为：起始值即第一组下界)
        if start_f is None or end_f is None:
            # 运行期推断：用子查询获取 MIN/MAX，再对齐到步长网格
            min_expr = f"(SELECT MIN({column}) FROM {self.view_name})"
            max_expr = f"(SELECT MAX({column}) FROM {self.view_name})"
            if start_f is None:
                start_f_sql = f"FLOOR(({min_expr}) / {step_f}) * {step_f}"
            else:
                start_f_sql = str(start_f)
            if end_f is None:
                end_f_sql = f"CEIL(({max_expr}) / {step_f}) * {step_f}"
            else:
                end_f_sql = str(end_f)
            # 区间数量动态：用 GREATEST 保证至少 1 组
            n_buckets_sql = f"GREATEST(CAST(CEIL(({end_f_sql} - {start_f_sql}) / {step_f}) AS INTEGER), 1)"
        else:
            start_f_sql = str(start_f)
            end_f_sql = str(end_f)
            n_buckets = max(int((end_f - start_f) / step_f), 1)
            n_buckets_sql = str(n_buckets)

        # 使用 DuckDB generate_series + 区间匹配生成 CASE WHEN
        # 对每个 bucket i (0-based)：下界 = start + i*step，上界 = start + (i+1)*step
        # 标签格式: "{lo}-{hi}"，最后一组为 "{lo}+"
        # 采用静态展开 (start/end 已知) 或动态子查询展开 (运行期推断)
        if start_f is not None and end_f is not None:
            # 静态展开：直接生成 CASE WHEN 链
            case_parts: List[str] = [f"WHEN {column} IS NULL THEN NULL"]
            if start_f != 0:
                case_parts.append(f"WHEN {column} < {start_f} THEN '<{self._fmt_bucket_label(start_f, start_f, is_last=False).split('-')[0]}'")
            else:
                case_parts.append(f"WHEN {column} < 0 THEN '<0'")
            # 浮点步长对齐：用 round 避免 0.1+0.1 != 0.2 累积误差
            n = max(int(round((end_f - start_f) / step_f)), 1)
            for i in range(n):
                lo = round(start_f + i * step_f, 10)
                hi = round(start_f + (i + 1) * step_f, 10)
                case_parts.append(f"WHEN {column} < {hi} THEN '{self._fmt_bucket_label(lo, hi)}'")
            # 兜底：超出 end 的归入最后一组 (含上界及以上)
            case_parts.append(f"ELSE '{self._fmt_bucket_label(end_f, end_f, is_last=True)}'")
            return "CASE " + " ".join(case_parts) + " END"
        else:
            # 动态展开：运行期用 generate_series 构造区间，再 JOIN 匹配
            # 表达式: 通过子查询为每行计算所属 bucket 索引，再格式化标签
            # bucket_idx = FLOOR((col - start) / step)
            # lo = start + bucket_idx * step, hi = lo + step
            # 标签 = lo || '-' || hi (最后一组用 lo || '+')
            # 为保持与静态分支一致的标签格式，使用 CASE 表达式
            bucket_idx = f"FLOOR(({column} - ({start_f_sql})) / {step_f})::INTEGER"
            lo_expr = f"({start_f_sql}) + {bucket_idx} * {step_f}"
            hi_expr = f"({lo_expr}) + {step_f}"
            # 格式化：去掉浮点尾随 .0 (显式包裹括号保证 BIGINT 转换优先级)
            fmt_lo = f"CASE WHEN ({lo_expr}) = FLOOR({lo_expr}) THEN CAST(({lo_expr})::BIGINT AS VARCHAR) ELSE CAST(ROUND({lo_expr}, 4) AS VARCHAR) END"
            fmt_hi = f"CASE WHEN ({hi_expr}) = FLOOR({hi_expr}) THEN CAST(({hi_expr})::BIGINT AS VARCHAR) ELSE CAST(ROUND({hi_expr}, 4) AS VARCHAR) END"
            # 最后一组 (bucket_idx == n_buckets - 1) 用 "+" 后缀
            is_last = f"({bucket_idx} >= ({n_buckets_sql}) - 1)"
            return (
                f"CASE WHEN {column} IS NULL THEN NULL "
                f"WHEN {is_last} THEN {fmt_lo} || '+' "
                f"ELSE {fmt_lo} || '-' || {fmt_hi} END"
            )

    @staticmethod
    def _fmt_bucket_label(lo: float, hi: float, is_last: bool = False) -> str:
        """格式化区间标签：整数去 .0，最后一组用 '+' 后缀"""
        def _fmt(v: float) -> str:
            if v == int(v):
                return str(int(v))
            return f"{round(v, 4)}"
        if is_last:
            return f"{_fmt(lo)}+"
        return f"{_fmt(lo)}-{_fmt(hi)}"

    def _apply_numeric_grouping(
        self,
        dims: List[str],
        grouping_config: Dict[str, Dict[str, Any]],
    ) -> List[str]:
        """
        遍历维度列表，对配置了数值分组的维度预生成分组 SQL 表达式并缓存，
        返回更新后的维度 Key 列表 (Key 本身不变，分组表达式通过
        self._numeric_group_exprs 在 _get_dim_expr 阶段注入)。

        约定：
        - 分组配置的 Key 为已规范化的维度 Key (如 'revenue', 'frame_current')
        - 仅当维度对应的底层列可被识别为数值列时才生效；否则跳过分组
        - 分组后的展示标签自动追加 "区间" 后缀 (如 "销售额区间")

        Args:
            dims: 已规范化的维度 Key 列表
            grouping_config: {dim_id: {'step': float, 'start': float|None, 'end': float|None}}

        Returns:
            更新后的维度 Key 列表 (顺序与输入一致，分组维度 Key 保持原值)
        """
        if not grouping_config or not dims:
            return list(dims)

        for d in dims:
            norm_d = self._normalize_dim_key(d)
            cfg = grouping_config.get(norm_d) or grouping_config.get(d)
            if not cfg:
                continue
            step = cfg.get("step")
            if step is None:
                continue
            # 解析底层列表达式：优先用 DIM_COL_MAP 中的真实列引用，
            # 否则回退到维度 Key 本身 (作为列名)
            base_expr = DIM_COL_MAP.get(norm_d)
            if base_expr:
                # 从 COALESCE(...) 等表达式中提取首个列标识符作为分组依据
                # 避免对 COALESCE 结果分组导致标签混乱
                m = re.match(r'COALESCE\(\s*([a-zA-Z_][a-zA-Z0-9_]*)', base_expr)
                col_ref = m.group(1) if m else base_expr
            else:
                col_ref = norm_d
            # Schema 安全探测：若视图列集合已知且分组依据列不存在，则跳过分组
            # (回退到 _get_dim_expr 的原始 schema 探测逻辑，避免 Binder 错误)
            if self.available_cols and col_ref not in self.available_cols:
                continue
            # 安全转义列引用
            try:
                safe_col = sanitize_identifier(col_ref)
            except ValueError:
                continue
            try:
                group_sql = self.build_numeric_grouping_sql(
                    column=safe_col,
                    step=float(step),
                    start=cfg.get("start"),
                    end=cfg.get("end"),
                )
            except ValueError:
                # 步长非法则跳过该维度的分组
                continue
            self._numeric_group_exprs[norm_d] = group_sql
            # 分组后展示标签：原标签 + "区间"
            base_label = DIM_LABEL_MAP.get(norm_d, norm_d)
            self._numeric_group_labels[norm_d] = f"{base_label}区间"

        return list(dims)

    def _get_dim_expr(self, dim: str, is_intl: bool = False) -> str:
        """获取维度的 DuckDB SQL 计算表达式 (具备 Schema 安全探测)"""
        norm_dim = self._normalize_dim_key(dim)
        # 数值分组优先：若该维度配置了步长分组，返回分组 CASE WHEN 表达式
        if norm_dim in self._numeric_group_exprs:
            return self._numeric_group_exprs[norm_dim]
        if is_intl:
            m = {
                "product_series": "COALESCE(product_series, '未归属系列')",
                "sales_team": "COALESCE(sales_team_rev, sales_team, '海外业务团队')",
                "province": "COALESCE(country_name, country, '未知地区')",
                "region": "COALESCE(region_rev, continent, '未划分大区')",
                "terminal_customer": "COALESCE(country_name, country, '通用散户')",
                "customer_name": "COALESCE(country_name, country, '海外渠道')",
                "country": "COALESCE(country_name, country, '其它国家')",
                "year": "CAST(year AS VARCHAR)",
                "quarter": "CASE WHEN month BETWEEN 1 AND 3 THEN 'Q1' WHEN month BETWEEN 4 AND 6 THEN 'Q2' WHEN month BETWEEN 7 AND 9 THEN 'Q3' ELSE 'Q4' END",
                "month": "CAST(month AS VARCHAR)",
                "property_type": "COALESCE(property_type, '本体')"
            }
            if norm_dim in m:
                return m[norm_dim]
        else:
            cn_m = {
                "continent": "COALESCE(NULLIF(TRIM(continent), ''), '中国区')",
                "country": "'中国'",
                "year": "CAST(year AS VARCHAR)",
                "month": "CAST(month AS VARCHAR)",
                "quarter": "COALESCE(quarter, 'Q1')",
            }
            if norm_dim in cn_m:
                return cn_m[norm_dim]

        expr = DIM_COL_MAP.get(norm_dim)
        if expr:
            if self.available_cols:
                # 检查表达式引用的列标识符在当前视图中是否存在
                tokens = re.findall(r'[a-zA-Z_][a-zA-Z0-9_]*', expr)
                keywords = {
                    'COALESCE', 'CASE', 'WHEN', 'THEN', 'ELSE', 'END', 'CAST', 'AS', 'VARCHAR',
                    'INTEGER', 'BIGINT', 'DOUBLE', 'FLOAT', 'NULLIF', 'TRIM', 'ROUND', 'SUM',
                    'LIKE', 'NOT', 'AND', 'OR', 'IS', 'NULL', 'IN', 'BETWEEN', 'FLOOR', 'CEIL',
                    'GREATEST', 'LEAST', 'ABS', 'TRUE', 'FALSE', 'REPLACE', 'EXTRACT'
                }
                missing = [t for t in tokens if t.upper() not in keywords and t not in self.available_cols]
                if missing:
                    return "'未分配'"
            return expr

        if self.available_cols and norm_dim not in self.available_cols:
            return "'未分配'"

        safe_dim = sanitize_identifier(norm_dim)
        return f"COALESCE({safe_dim}, '未分配')"

    def _get_dim_label(self, dim: str) -> str:
        """获取维度的前端展示别名"""
        norm_dim = self._normalize_dim_key(dim)
        # 数值分组维度使用带 "区间" 后缀的标签
        if norm_dim in self._numeric_group_labels:
            return self._numeric_group_labels[norm_dim]
        return DIM_LABEL_MAP.get(norm_dim, norm_dim)

    def _normalize_metric(self, m: Any) -> Dict[str, Any]:
        """归一化指标结构"""
        if isinstance(m, str):
            field = self._normalize_dim_key(m)
            return {
                "id": field,
                "field": field,
                "agg": "sum",
                "show_as": "normal",
                "alias": None,
                "formula": None,
            }
        elif isinstance(m, dict):
            field = m.get("field") or m.get("id") or "revenue"
            field = self._normalize_dim_key(str(field))
            return {
                "id": str(m.get("id", field)),
                "field": field,
                "agg": str(m.get("agg", "sum")).lower(),
                "show_as": str(m.get("show_as", "normal")).lower(),
                "alias": m.get("alias") or m.get("label"),
                "formula": m.get("formula"),
            }
        else:
            field = getattr(m, "field", None) or getattr(m, "id", None) or "revenue"
            field = self._normalize_dim_key(str(field))
            return {
                "id": str(getattr(m, "id", field)),
                "field": field,
                "agg": str(getattr(m, "agg", "sum") or "sum").lower(),
                "show_as": str(getattr(m, "show_as", "normal") or "normal").lower(),
                "alias": getattr(m, "alias", None) or getattr(m, "label", None),
                "formula": getattr(m, "formula", None),
            }

    def _is_text_dimension(self, field: str) -> bool:
        """判断是否为文本/分类维度，避免直接使用 SUM(VARCHAR) 引发 SQL 类型异常"""
        norm = self._normalize_dim_key(field)
        text_dims = {
            "province", "region", "product_series", "product_model", "property_type",
            "market_channel", "sales_team", "terminal_customer", "customer_name",
            "customer_nature", "customer_no", "outlet_customer_name", "country",
            "continent", "material_code", "material_desc", "material_group_code",
            "material_group_desc", "project_no", "project_name", "sales_org",
            "mfg_unit", "report_source", "industry", "biz_category", "currency",
            "product_platform", "product_manager_team", "product_category",
            "internal_customer_flag", "biz_type", "business_type",
            "frame_current", "operation_method", "breaking_capacity", "pole_count",
            "n_pole_type"
        }
        return norm in text_dims

    def _compile_metric_formula(self, formula: str, qty_col: str, cond_str: Optional[str] = None, is_intl: bool = False) -> str:
        """
        将自定义计算公式 (如 'revenue / qty', '(revenue - cost) / revenue * 100', 'net_amount * 1.13')
        安全转译为带 NULLIF 防除零的 DuckDB SQL 聚合表达式。
        使用 AST 解析进行严格校验，非白名单 token、变量或非法语法将抛出 ValueError。
        """
        if not formula or not str(formula).strip():
            return "0.0"

        rev_c = self._get_metric_col("revenue", qty_col)
        actual_qty_c = self._get_metric_col("qty", qty_col)
        cost_c = self._get_metric_col("cost", qty_col)
        gp_c = self._get_metric_col("gross_profit", qty_col)

        var_map = {
            "revenue": rev_c,
            "total_net_revenue": rev_c,
            "sales_revenue": rev_c,
            "net_revenue": rev_c,
            "销售净收入": rev_c,
            "qty": actual_qty_c,
            "quantity": actual_qty_c,
            "benti_qty": actual_qty_c,
            "invoice_qty": actual_qty_c,
            "本体发票台数": actual_qty_c,
            "本体台数": actual_qty_c,
            "cost": cost_c,
            "cost_wanyu": cost_c,
            "产品成本": cost_c,
            "gross_profit": gp_c,
            "gross_profit_wanyu": gp_c,
            "毛利额": gp_c,
            "billing_price_amount": "billing_price_amount",
            "开单价金额": "billing_price_amount",
            "settlement_price_amount": "settlement_price_amount",
            "结算价金额": "settlement_price_amount",
            "net_amount": "net_amount",
            "净额": "net_amount",
            "discount_amount": "discount_amount",
            "折让": "discount_amount",
            "expense_amount": "expense_amount",
            "费用": "expense_amount",
            "pocket_price": "pocket_price",
            "口袋价": "pocket_price",
        }

        import ast

        try:
            tree = ast.parse(str(formula).strip(), mode='eval')
        except Exception as e:
            raise ValueError(f"Invalid metric formula syntax: '{formula}'") from e

        def _compile_node(node: ast.AST) -> str:
            if isinstance(node, ast.Expression):
                return _compile_node(node.body)
            elif isinstance(node, ast.BinOp):
                left_expr = _compile_node(node.left)
                right_expr = _compile_node(node.right)
                if isinstance(node.op, ast.Add):
                    return f"({left_expr} + {right_expr})"
                elif isinstance(node.op, ast.Sub):
                    return f"({left_expr} - {right_expr})"
                elif isinstance(node.op, ast.Mult):
                    return f"({left_expr} * {right_expr})"
                elif isinstance(node.op, (ast.Div, ast.FloorDiv)):
                    return f"({left_expr} / NULLIF({right_expr}, 0))"
                elif isinstance(node.op, ast.Mod):
                    return f"({left_expr} % NULLIF({right_expr}, 0))"
                elif isinstance(node.op, ast.Pow):
                    return f"POWER({left_expr}, {right_expr})"
                else:
                    raise ValueError(f"Unsupported operator '{type(node.op).__name__}' in formula: '{formula}'")
            elif isinstance(node, ast.UnaryOp):
                operand_expr = _compile_node(node.operand)
                if isinstance(node.op, ast.UAdd):
                    return f"(+{operand_expr})"
                elif isinstance(node.op, ast.USub):
                    return f"(-{operand_expr})"
                else:
                    raise ValueError(f"Unsupported unary operator '{type(node.op).__name__}' in formula: '{formula}'")
            elif isinstance(node, ast.Constant):
                if isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
                    return str(node.value)
                else:
                    raise ValueError(f"Disallowed constant value '{node.value}' in formula: '{formula}'")
            elif isinstance(node, ast.Name):
                var_name = node.id
                if var_name in var_map:
                    col = var_map[var_name]
                    if cond_str:
                        return f"SUM(CASE WHEN {cond_str} THEN {col} ELSE 0 END)"
                    return f"SUM({col})"
                else:
                    raise ValueError(f"Unknown or unauthorized metric identifier '{var_name}' in formula: '{formula}'")
            else:
                raise ValueError(f"Disallowed syntax element '{type(node).__name__}' in formula: '{formula}'")

        compiled_inner = _compile_node(tree)
        return f"ROUND({compiled_inner}, 2)"

    def _get_metric_col(self, col_type: str, qty_col: str = "invoice_qty_benti") -> str:
        """获取相匹配的底层列名，兼容 v_china_sales_monthly 与 v_chint_cn_sales_*"""
        is_monthly = "monthly" in getattr(self, "view_name", "").lower()
        cols = self.available_cols
        has_cols = len(cols) > 0
        if col_type == "revenue":
            if is_monthly or (has_cols and "total_net_revenue" in cols and "net_revenue" not in cols):
                return "total_net_revenue"
            return "net_revenue"
        elif col_type == "qty":
            if is_monthly or (has_cols and "total_sales_qty" in cols and qty_col not in cols):
                return "total_sales_qty"
            elif has_cols and "invoice_qty" in cols and qty_col not in cols:
                return "invoice_qty"
            return qty_col
        elif col_type == "cost":
            if is_monthly or (has_cols and "cost" in cols and "product_cost" not in cols):
                return "cost"
            return "product_cost"
        elif col_type == "gross_profit":
            if is_monthly or (has_cols and "total_gross_profit" in cols and "gross_profit" not in cols):
                return "total_gross_profit"
            return "gross_profit"
        return col_type

    def _get_metric_sql_info(self, m_info: Dict[str, Any], qty_col: str, is_intl: bool = False) -> Tuple[str, str]:
        """
        获取指标的基础聚合 SQL 表达式和默认别名
        返回: (agg_expr, default_alias)
        """
        field = m_info["field"]
        agg = m_info["agg"].upper()
        formula = m_info.get("formula")

        # 1. 优先解析自定义计算公式 (支持 revenue / qty 等表达式)
        if formula or field.startswith("calc_"):
            if formula:
                agg_expr = self._compile_metric_formula(formula, qty_col, cond_str=None, is_intl=is_intl)
            else:
                agg_expr = "0.0"
            base_alias = m_info.get("alias") or m_info.get("label") or field
            return agg_expr, m_info.get("alias") or base_alias

        has_yoy = self._has_yoy_metric()
        has_mom = self._has_mom_metric()
        target_year = self._get_default_year()

        eff_row = getattr(self, "_effective_row_dims", None) or self.raw_row_dims
        eff_col = getattr(self, "_effective_col_dims", None) or self.raw_col_dims
        all_dim_keys = set([self._normalize_dim_key(d) for d in (eff_row + eff_col) if d])
        is_year_in_dims = "year" in all_dim_keys
        is_month_in_dims = "month" in all_dim_keys
        is_quarter_in_dims = "quarter" in all_dim_keys

        # 仅当 [年份] 未拖入行/列维度分组且非 'all' 时，才对常规基础指标限制 target_year (便于在未按年分组时同表计算同比基期)
        apply_yoy_period = has_yoy and not is_year_in_dims and str(self.year).lower() != "all"
        # 仅当 [月份/季度] 未拖入行/列维度分组时，才对常规基础指标限制环比目标月
        apply_mom_period = has_mom and not is_month_in_dims and not is_quarter_in_dims

        is_sum = (agg.upper() == "SUM")
        if apply_mom_period:
            t_year, t_month, p_year, p_month = self._resolve_mom_period()
            period_cond = f"CASE WHEN year = {t_year} AND month = {t_month} THEN "
            period_end = " ELSE 0 END" if is_sum else " ELSE NULL END"
        elif apply_yoy_period:
            period_cond = f"CASE WHEN year = {target_year} THEN "
            period_end = " ELSE 0 END" if is_sum else " ELSE NULL END"
        else:
            period_cond = ""
            period_end = ""

        rev_c = self._get_metric_col("revenue", qty_col)
        actual_qty_c = self._get_metric_col("qty", qty_col)
        cost_c = self._get_metric_col("cost", qty_col)
        gp_c = self._get_metric_col("gross_profit", qty_col)

        if field in ("revenue", "total_net_revenue", "sales_revenue", "net_revenue", "net_income_wanyu", "销售净收入"):
            col_expr = f"{period_cond}{rev_c}{period_end}" if (apply_mom_period or apply_yoy_period) else rev_c
            base_alias = "销售净收入 (元)"
        elif field in ("benti_qty", "invoice_qty_benti", "本体发票台数", "本体台数", "本体数量"):
            benti_col = self._get_metric_col("qty", "invoice_qty_benti")
            col_expr = f"{period_cond}{benti_col}{period_end}" if (apply_mom_period or apply_yoy_period) else benti_col
            base_alias = "本体台数 (台)"
        elif field in ("qty", "quantity", "total_qty", "invoice_qty", "sales_qty", "raw_sales_qty", "总台数", "发票数量", "总发票台数", "总数量", "发票台数"):
            qty_col_expr = self._get_metric_col("qty", "invoice_qty")
            col_expr = f"{period_cond}{qty_col_expr}{period_end}" if (apply_mom_period or apply_yoy_period) else qty_col_expr
            base_alias = "总台数 (台)"
        elif field in ("cost", "cost_wanyu", "product_cost", "产品成本"):
            col_expr = f"{period_cond}{cost_c}{period_end}" if (apply_mom_period or apply_yoy_period) else cost_c
            base_alias = "产品成本 (元)"
        elif field in ("gross_profit", "gross_profit_wanyu", "毛利额"):
            col_expr = f"{period_cond}{gp_c}{period_end}" if (apply_mom_period or apply_yoy_period) else gp_c
            base_alias = "毛利额 (元)"
        elif field in ("gross_margin_rate", "毛利率", "margin_rate", "gross_margin", "margin"):
            if apply_mom_period:
                t_year, t_month, _, _ = self._resolve_mom_period()
                rev_sub = f"CASE WHEN year = {t_year} AND month = {t_month} THEN {rev_c} ELSE 0 END"
                gp_sub = f"CASE WHEN year = {t_year} AND month = {t_month} THEN {gp_c} ELSE 0 END"
            elif apply_yoy_period:
                rev_sub = f"CASE WHEN year = {target_year} THEN {rev_c} ELSE 0 END"
                gp_sub = f"CASE WHEN year = {target_year} THEN {gp_c} ELSE 0 END"
            else:
                rev_sub = rev_c
                gp_sub = gp_c
            agg_expr = f"ROUND(SUM({gp_sub}) / NULLIF(SUM({rev_sub}), 0) * 100.0, 2)"
            base_alias = "毛利率 (%)"
            return agg_expr, m_info["alias"] or base_alias
        elif field in ("yoy_growth_rate", "同比增长率"):
            prev_year = target_year - 1
            alias_or_label = str(m_info.get("alias") or m_info.get("label") or "").lower()
            if any(k in alias_or_label for k in ("本体", "benti")):
                target_c = self._get_metric_col("qty", "invoice_qty_benti")
                base_alias = "本体台数 同比 (%)"
            elif any(k in alias_or_label for k in ("台数", "数量", "qty", "总台数", "发票台数")):
                target_c = self._get_metric_col("qty", "invoice_qty")
                base_alias = "总台数 同比 (%)"
            elif any(k in alias_or_label for k in ("成本", "cost")):
                target_c = cost_c
                base_alias = "成本 同比 (%)"
            elif any(k in alias_or_label for k in ("毛利", "profit", "gp")):
                target_c = gp_c
                base_alias = "毛利额 同比 (%)"
            else:
                target_c = rev_c
                base_alias = "同比增长率 (%)"
            if is_year_in_dims:
                return "CAST(NULL AS DOUBLE)", m_info.get("alias") or base_alias
            agg_expr = f"ROUND((SUM(CASE WHEN year = {target_year} THEN {target_c} ELSE 0 END) - SUM(CASE WHEN year = {prev_year} THEN {target_c} ELSE 0 END)) / NULLIF(ABS(SUM(CASE WHEN year = {prev_year} THEN {target_c} ELSE 0 END)), 0) * 100.0, 2)"
            return agg_expr, m_info["alias"] or base_alias
        elif field in ("mom_growth_rate", "环比增长率"):
            t_year, t_month, p_year, p_month = self._resolve_mom_period()
            alias_or_label = str(m_info.get("alias") or m_info.get("label") or "").lower()
            if any(k in alias_or_label for k in ("本体", "benti")):
                target_c = self._get_metric_col("qty", "invoice_qty_benti")
                base_alias = "本体台数 环比 (%)"
            elif any(k in alias_or_label for k in ("台数", "数量", "qty", "总台数", "发票台数")):
                target_c = self._get_metric_col("qty", "invoice_qty")
                base_alias = "总台数 环比 (%)"
            elif any(k in alias_or_label for k in ("成本", "cost")):
                target_c = cost_c
                base_alias = "成本 环比 (%)"
            elif any(k in alias_or_label for k in ("毛利", "profit", "gp")):
                target_c = gp_c
                base_alias = "毛利额 环比 (%)"
            else:
                target_c = rev_c
                base_alias = "环比增长率 (%)"
            agg_expr = f"ROUND((SUM(CASE WHEN year = {t_year} AND month = {t_month} THEN {target_c} ELSE 0 END) - SUM(CASE WHEN year = {p_year} AND month = {p_month} THEN {target_c} ELSE 0 END)) / NULLIF(ABS(SUM(CASE WHEN year = {p_year} AND month = {p_month} THEN {target_c} ELSE 0 END)), 0) * 100.0, 2)"
            return agg_expr, m_info["alias"] or base_alias
        elif field in ("replace_rate", "kunlun_replace_rate", "替换率", "昆仑替换率"):
            group_a_raw = self.filters.get("groupA") or self.filters.get("group_a") or []
            group_b_raw = self.filters.get("groupB") or self.filters.get("group_b") or []
            group_a = [group_a_raw] if isinstance(group_a_raw, str) else list(group_a_raw)
            group_b = [group_b_raw] if isinstance(group_b_raw, str) else list(group_b_raw)
            group_a = [v.strip() for v in group_a if str(v).strip()]
            group_b = [v.strip() for v in group_b if str(v).strip()]

            if not group_a or not group_b:
                cat = (self.product_class or "acb").lower()
                DEPT_REPLACE_SSOT = {
                    "acb": (["NXA"], ["NA1"]),
                    "mccb": (["NXM"], ["NM1"]),
                    "mcb": (["NXB-63"], ["NDM1-63"]),
                    "pq": (["SVG"], ["APF"]),
                    "atse": (["NZ7"], ["NZ1"]),
                    "vf": (["NXA"], ["NA1"]),
                    "all": (["NXA"], ["NA1"]),
                }
                def_a, def_b = DEPT_REPLACE_SSOT.get(cat, (["NXA"], ["NA1"]))
                group_a = group_a or def_a
                group_b = group_b or def_b

            if group_a and group_b:
                pm_expr = self._get_dim_expr("product_model", is_intl)
                a_str = ", ".join([f"'{v}'" for v in group_a if v])
                b_str = ", ".join([f"'{v}'" for v in group_b if v])
                # 支持按产品型号或产品系列双重匹配
                match_a = f"({pm_expr} IN ({a_str}) OR product_series IN ({a_str}))"
                match_b = f"({pm_expr} IN ({b_str}) OR product_series IN ({b_str}))"
                qty_a = f"SUM(CASE WHEN {match_a} THEN {actual_qty_c} ELSE 0 END)"
                qty_b = f"SUM(CASE WHEN {match_b} THEN {actual_qty_c} ELSE 0 END)"
                agg_expr = f"ROUND({qty_a} / NULLIF({qty_a} + {qty_b}, 0) * 100.0, 2)"
            else:
                agg_expr = "NULL"
            base_alias = "替换率 (%)"
            return agg_expr, m_info["alias"] or base_alias
        else:
            dim_expr = self._get_dim_expr(field, is_intl)
            col_expr = dim_expr
            base_alias = self._get_dim_label(field)
            # 文本分类字段在数值聚合下自动回退为 COUNT，防止 DuckDB 类型错误
            if agg in ("SUM", "AVG", "MEDIAN", "STDDEV") and self._is_text_dimension(field):
                agg = "COUNT"

        if agg == "COUNT":
            agg_expr = f"COUNT({col_expr})"
        elif agg == "AVG":
            agg_expr = f"ROUND(AVG({col_expr}), 2)"
        elif agg == "MAX":
            agg_expr = f"MAX({col_expr})"
        elif agg == "MIN":
            agg_expr = f"MIN({col_expr})"
        elif agg == "COUNT_DISTINCT":
            agg_expr = f"COUNT(DISTINCT {col_expr})"
        elif agg == "MEDIAN":
            agg_expr = f"ROUND(median({col_expr}), 2)"
        elif agg == "STDDEV":
            agg_expr = f"ROUND(stddev_pop({col_expr}), 2)"
        else:
            agg_expr = f"ROUND(SUM({col_expr}), 2)"
        return agg_expr, m_info["alias"] or base_alias

    def _get_companion_yoy_sql_info(self, m_info: Dict[str, Any], qty_col: str, is_intl: bool = False) -> Tuple[Optional[str], Optional[str]]:
        """为指定的基础指标生成伴生同比 SQL 表达式与别名"""
        field = m_info["field"]
        target_year = self.year or 2026
        prev_year = target_year - 1

        rev_c = self._get_metric_col("revenue", qty_col)
        actual_qty_c = self._get_metric_col("qty", qty_col)
        cost_c = self._get_metric_col("cost", qty_col)
        gp_c = self._get_metric_col("gross_profit", qty_col)

        target_c = None
        base_name = None
        if field in ("revenue", "total_net_revenue", "sales_revenue", "net_revenue", "net_income_wanyu", "销售净收入"):
            target_c = rev_c
            base_name = "销售净收入"
        elif field in ("benti_qty", "invoice_qty_benti", "本体发票台数", "本体台数", "本体数量"):
            target_c = self._get_metric_col("qty", "invoice_qty_benti")
            base_name = "本体台数"
        elif field in ("qty", "quantity", "total_qty", "invoice_qty", "sales_qty", "raw_sales_qty", "总台数", "发票数量", "总发票台数", "总数量", "发票台数"):
            target_c = self._get_metric_col("qty", "invoice_qty")
            base_name = "总台数"
        elif field in ("cost", "cost_wanyu", "product_cost", "产品成本"):
            target_c = cost_c
            base_name = "产品成本"
        elif field in ("gross_profit", "gross_profit_wanyu", "毛利额"):
            target_c = gp_c
            base_name = "毛利额"

        if target_c and base_name:
            agg_expr = f"ROUND((SUM(CASE WHEN year = {target_year} THEN {target_c} ELSE 0 END) - SUM(CASE WHEN year = {prev_year} THEN {target_c} ELSE 0 END)) / NULLIF(ABS(SUM(CASE WHEN year = {prev_year} THEN {target_c} ELSE 0 END)), 0) * 100.0, 2)"
            return agg_expr, f"{base_name}_同比增长率 (%)"
        return None, None

    def _get_companion_mom_sql_info(self, m_info: Dict[str, Any], qty_col: str, is_intl: bool = False) -> Tuple[Optional[str], Optional[str]]:
        """为指定的基础指标生成伴生环比 SQL 表达式与别名"""
        field = m_info["field"]
        t_year, t_month, p_year, p_month = self._resolve_mom_period()

        rev_c = self._get_metric_col("revenue", qty_col)
        cost_c = self._get_metric_col("cost", qty_col)
        gp_c = self._get_metric_col("gross_profit", qty_col)

        target_c = None
        base_name = None
        if field in ("revenue", "total_net_revenue", "sales_revenue", "net_revenue", "net_income_wanyu", "销售净收入"):
            target_c = rev_c
            base_name = "销售净收入"
        elif field in ("benti_qty", "invoice_qty_benti", "本体发票台数", "本体台数", "本体数量"):
            target_c = self._get_metric_col("qty", "invoice_qty_benti")
            base_name = "本体台数"
        elif field in ("qty", "quantity", "total_qty", "invoice_qty", "sales_qty", "raw_sales_qty", "总台数", "发票数量", "总发票台数", "总数量", "发票台数"):
            target_c = self._get_metric_col("qty", "invoice_qty")
            base_name = "总台数"
        elif field in ("cost", "cost_wanyu", "product_cost", "产品成本"):
            target_c = cost_c
            base_name = "产品成本"
        elif field in ("gross_profit", "gross_profit_wanyu", "毛利额"):
            target_c = gp_c
            base_name = "毛利额"

        if target_c and base_name:
            agg_expr = f"ROUND((SUM(CASE WHEN year = {t_year} AND month = {t_month} THEN {target_c} ELSE 0 END) - SUM(CASE WHEN year = {p_year} AND month = {p_month} THEN {target_c} ELSE 0 END)) / NULLIF(ABS(SUM(CASE WHEN year = {p_year} AND month = {p_month} THEN {target_c} ELSE 0 END)), 0) * 100.0, 2)"
            return agg_expr, f"{base_name}_环比增长率 (%)"
        return None, None

    def _build_case_agg_expr(self, m_info: Dict[str, Any], cond_str: str, qty_col: str, is_intl: bool = False) -> str:
        """构建列透视时的条件聚合表达式"""
        field = m_info["field"]
        agg = m_info["agg"].upper()
        formula = m_info.get("formula")

        # 1. 优先解析自定义计算公式
        if formula or field.startswith("calc_"):
            if formula:
                return self._compile_metric_formula(formula, qty_col, cond_str=cond_str, is_intl=is_intl)
            return "0.0"

        eff_row = getattr(self, "_effective_row_dims", None) or self.raw_row_dims
        eff_col = getattr(self, "_effective_col_dims", None) or self.raw_col_dims
        all_dim_keys = set([self._normalize_dim_key(d) for d in (eff_row + eff_col) if d])
        is_year_in_dims = "year" in all_dim_keys

        has_yoy = self._has_yoy_metric()
        target_year = self.year or 2026
        yr_cond = f" AND year = {target_year}" if (has_yoy and not is_year_in_dims and str(self.year).lower() != "all") else ""

        rev_c = self._get_metric_col("revenue", qty_col)
        actual_qty_c = self._get_metric_col("qty", qty_col)
        cost_c = self._get_metric_col("cost", qty_col)
        gp_c = self._get_metric_col("gross_profit", qty_col)

        if field in ("revenue", "total_net_revenue", "sales_revenue", "net_revenue", "net_income_wanyu", "销售净收入"):
            val_expr = rev_c
        elif field in ("qty", "quantity", "total_qty", "sales_qty", "raw_sales_qty", "benti_qty", "invoice_qty", "invoice_qty_benti", "本体发票台数", "总台数", "发票数量", "总发票台数", "总数量", "发票台数"):
            val_expr = actual_qty_c
        elif field in ("cost", "cost_wanyu", "产品成本"):
            val_expr = cost_c
        elif field in ("gross_profit", "gross_profit_wanyu", "毛利额"):
            val_expr = gp_c
        elif field in ("gross_margin_rate", "毛利率", "margin_rate", "gross_margin", "margin"):
            return f"ROUND(SUM(CASE WHEN {cond_str}{yr_cond} THEN {gp_c} ELSE 0 END) / NULLIF(SUM(CASE WHEN {cond_str}{yr_cond} THEN {rev_c} ELSE 0 END), 0) * 100.0, 2)"
        elif field in ("yoy_growth_rate", "同比增长率"):
            prev_year = target_year - 1
            return f"ROUND((SUM(CASE WHEN {cond_str} AND year = {target_year} THEN {rev_c} ELSE 0 END) - SUM(CASE WHEN {cond_str} AND year = {prev_year} THEN {rev_c} ELSE 0 END)) / NULLIF(ABS(SUM(CASE WHEN {cond_str} AND year = {prev_year} THEN {rev_c} ELSE 0 END)), 0) * 100.0, 2)"
        elif field in ("mom_growth_rate", "环比增长率"):
            t_year, t_month, p_year, p_month = self._resolve_mom_period()
            return f"ROUND((SUM(CASE WHEN {cond_str} AND year = {t_year} AND month = {t_month} THEN {rev_c} ELSE 0 END) - SUM(CASE WHEN {cond_str} AND year = {p_year} AND month = {p_month} THEN {rev_c} ELSE 0 END)) / NULLIF(ABS(SUM(CASE WHEN {cond_str} AND year = {p_year} AND month = {p_month} THEN {rev_c} ELSE 0 END)), 0) * 100.0, 2)"
        elif field in ("replace_rate", "kunlun_replace_rate", "替换率", "昆仑替换率"):
            group_a_raw = self.filters.get("groupA") or self.filters.get("group_a") or []
            group_b_raw = self.filters.get("groupB") or self.filters.get("group_b") or []
            group_a = [group_a_raw] if isinstance(group_a_raw, str) else list(group_a_raw)
            group_b = [group_b_raw] if isinstance(group_b_raw, str) else list(group_b_raw)
            group_a = [v.strip() for v in group_a if str(v).strip()]
            group_b = [v.strip() for v in group_b if str(v).strip()]
            if not group_a or not group_b:
                cat = (self.product_class or "acb").lower()
                DEPT_REPLACE_SSOT = {
                    "acb": (["NXA"], ["NA1"]),
                    "mccb": (["NXM"], ["NM1"]),
                    "mcb": (["NXB-63"], ["NDM1-63"]),
                    "pq": (["SVG"], ["APF"]),
                    "atse": (["NZ7"], ["NZ1"]),
                    "vf": (["NXA"], ["NA1"]),
                    "all": (["NXA"], ["NA1"]),
                }
                def_a, def_b = DEPT_REPLACE_SSOT.get(cat, (["NXA"], ["NA1"]))
                group_a = group_a or def_a
                group_b = group_b or def_b
            pm_expr = self._get_dim_expr("product_model", is_intl)
            if group_a and group_b:
                a_str = ", ".join([f"'{v}'" for v in group_a if v])
                b_str = ", ".join([f"'{v}'" for v in group_b if v])
                if a_str and b_str:
                    match_a = f"({pm_expr} IN ({a_str}) OR product_series IN ({a_str}))"
                    match_b = f"({pm_expr} IN ({b_str}) OR product_series IN ({b_str}))"
                    qty_a = f"SUM(CASE WHEN {cond_str}{yr_cond} AND {match_a} THEN {actual_qty_c} ELSE 0 END)"
                    qty_b = f"SUM(CASE WHEN {cond_str}{yr_cond} AND {match_b} THEN {actual_qty_c} ELSE 0 END)"
                    return f"ROUND({qty_a} / NULLIF({qty_a} + {qty_b}, 0) * 100.0, 2)"
            return "NULL"
        else:
            val_expr = self._get_dim_expr(field, is_intl)
            if agg in ("SUM", "AVG", "MEDIAN", "STDDEV") and self._is_text_dimension(field):
                agg = "COUNT"

        if agg == "COUNT":
            return f"COUNT(CASE WHEN {cond_str}{yr_cond} THEN {val_expr} ELSE NULL END)"
        elif agg == "AVG":
            return f"ROUND(AVG(CASE WHEN {cond_str}{yr_cond} THEN {val_expr} ELSE NULL END), 2)"
        elif agg == "MAX":
            return f"MAX(CASE WHEN {cond_str}{yr_cond} THEN {val_expr} ELSE NULL END)"
        elif agg == "MIN":
            return f"MIN(CASE WHEN {cond_str}{yr_cond} THEN {val_expr} ELSE NULL END)"
        elif agg == "COUNT_DISTINCT":
            return f"COUNT(DISTINCT CASE WHEN {cond_str}{yr_cond} THEN {val_expr} ELSE NULL END)"
        elif agg == "MEDIAN":
            return f"ROUND(median(CASE WHEN {cond_str}{yr_cond} THEN {val_expr} ELSE NULL END), 2)"
        elif agg == "STDDEV":
            return f"ROUND(stddev_pop(CASE WHEN {cond_str}{yr_cond} THEN {val_expr} ELSE NULL END), 2)"
        else:
            return f"ROUND(SUM(CASE WHEN {cond_str}{yr_cond} THEN {val_expr} ELSE 0 END), 2)"

    def _build_column_tree(
        self,
        col_tuples: List[Tuple[Any, ...]],
        col_dim_keys: List[str],
        metrics_info: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """生成前端渲染多层表头所需的 column_tree 元数据结构"""
        root: Dict[Any, Any] = {}
        for combo in col_tuples:
            curr = root
            for val in combo[:-1]:
                val_str = str(val)
                if val_str not in curr:
                    curr[val_str] = {}
                curr = curr[val_str]

            last_val = str(combo[-1])
            if last_val not in curr:
                curr[last_val] = []

            combo_prefix = "_".join(str(v) for v in combo)
            for m_info in metrics_info:
                _, base_alias = self._get_metric_sql_info(m_info, "invoice_qty_benti")
                col_alias = f"{combo_prefix}_{base_alias}"
                curr[last_val].append({
                    "title": base_alias if len(metrics_info) > 1 else last_val,
                    "field": col_alias
                })

        def dict_to_nodes(d: Any) -> List[Dict[str, Any]]:
            nodes = []
            if isinstance(d, dict):
                for k, v in d.items():
                    nodes.append({
                        "title": str(k),
                        "children": dict_to_nodes(v)
                    })
            elif isinstance(d, list):
                return d
            return nodes

        return dict_to_nodes(root)

    def _build_where_clauses(self, is_intl: bool = False) -> List[str]:
        """构建基础 WHERE 过滤条件语句列表 (禁止硬编码过滤，无损维度开放)"""
        where_clauses = []
        has_yoy = self._has_yoy_metric()
        has_mom = self._has_mom_metric()
        mom_period = self._resolve_mom_period() if has_mom else None

        # 优先使用日期层次展开后的有效维度集合 (避免年份/季度被重复过滤)
        eff_row = getattr(self, "_effective_row_dims", None) or self.raw_row_dims
        eff_col = getattr(self, "_effective_col_dims", None) or self.raw_col_dims
        all_dim_keys = set([self._normalize_dim_key(d) for d in (eff_row + eff_col) if d])
        is_year_in_dims = "year" in all_dim_keys
        is_quarter_in_dims = "quarter" in all_dim_keys or "month" in all_dim_keys
        is_property_in_dims = "property_type" in all_dim_keys or "property" in all_dim_keys

        # 1. 年份过滤构建：仅在【年份】未拖入行/列维度分组且 filters 中无显式 year 时应用全局年份配置
        has_explicit_year = any(k in self.filters for k in ("year", "selectedYear", "selected_year"))
        if self.year and str(self.year).lower() != "all" and not is_year_in_dims and not has_explicit_year:
            try:
                target_year = int(self.year)
                years_req = {target_year}
                if has_yoy:
                    years_req.add(target_year - 1)
                if has_mom and mom_period:
                    years_req.add(mom_period[0])
                    years_req.add(mom_period[2])
                if len(years_req) == 1:
                    where_clauses.append(f"year = {list(years_req)[0]}")
                else:
                    in_yrs = ", ".join(str(y) for y in sorted(years_req))
                    where_clauses.append(f"year IN ({in_yrs})")
            except (ValueError, TypeError):
                pass

        # 2. 季度过滤构建：仅在【季度/月份】未拖入行/列维度分组且 filters 中无显式 quarter/month 时应用
        has_explicit_quarter = any(k in self.filters for k in ("quarter", "selectedQuarter", "selected_quarter", "month", "selectedMonth", "selected_month"))
        if self.quarter and str(self.quarter).lower() != "all" and not is_quarter_in_dims and not has_explicit_quarter:
            q_map = {"q1": (1, 3), "q2": (4, 6), "q3": (7, 9), "q4": (10, 12)}
            q_range = q_map.get(str(self.quarter).lower())
            if q_range:
                where_clauses.append(f"month BETWEEN {q_range[0]} AND {q_range[1]}")

        # 同时间口径对齐：当计算同比且未显式指定月份时，自动将对比基期 (Y-1) 严格约束至目标年份的最大有效数据月份 (如 1-7月)
        if has_yoy and not is_quarter_in_dims and not has_explicit_quarter:
            try:
                target_year = int(self.year or 2026)
                max_m = self._get_max_available_month(target_year)
                if max_m and max_m < 12:
                    where_clauses.append(f"(month IS NULL OR month BETWEEN 1 AND {max_m})")
            except (ValueError, TypeError):
                pass

        # 环比单期对齐：当纯计算环比且未显式指定月份时，自动将对比范围约束至本期月与紧邻上一期月
        if has_mom and mom_period and not has_yoy and not is_quarter_in_dims and not has_explicit_quarter:
            t_y, t_m, p_y, p_m = mom_period
            if t_y == p_y:
                where_clauses.append(f"(month IS NULL OR month IN ({t_m}, {p_m}))")
            else:
                where_clauses.append(f"((year = {t_y} AND month = {t_m}) OR (year = {p_y} AND month = {p_m}))")

        # 3. 属性过滤构建：仅在【属性】未拖入行/列维度分组且 filters 中无显式 property 时应用
        has_explicit_property = any(k in self.filters for k in ("property_type", "property", "propertyType"))
        if self.property_type and self.property_type != "all" and not is_property_in_dims and not has_explicit_property:
            if self.property_type in ("benti", "本体"):
                where_clauses.append("property_type = '本体'")
            elif self.property_type in ("non_benti", "非本体", "附件"):
                where_clauses.append("property_type != '本体'")

        FILTER_KEY_ALIAS = {
            "selectedYear": "year",
            "selected_year": "year",
            "selectedQuarter": "quarter",
            "selected_quarter": "quarter",
            "propertyType": "property_type",
            "productClass": "product_class",
            "productCategory": "product_category",
            "productSeries": "product_series",
            "marketChannel": "market_channel",
            "salesTeam": "sales_team",
            "salesTeamRev": "sales_team_rev",
            "terminalCustomer": "terminal_customer",
            "customerName": "customer_name",
        }

        # 4. 动态 UI 筛选器构建 (取自 filters 字典)
        for fk, fval in self.filters.items():
            if fk in ("groupA", "group_a", "groupB", "group_b", "__top_n__", "top_n", "topN", "__advanced_filters__") or fk.startswith("__"):
                continue  # 自定义指标参数或特殊筛选配置不在 WHERE 子句中硬过滤

            if fval is not None and fval not in ("all", "ALL", "全部", "小计", "总计", ""):
                norm_fk = FILTER_KEY_ALIAS.get(fk, fk)
                nk = self._normalize_dim_key(norm_fk)
                expr = self._get_dim_expr(nk, is_intl)
                if nk == "year" and (has_yoy or has_mom):
                    years_set = set()
                    raw_years = fval if isinstance(fval, (list, tuple, set)) else [str(fval)]
                    for y in raw_years:
                        try:
                            iy = int(y)
                            years_set.add(str(iy))
                            if has_yoy:
                                years_set.add(str(iy - 1))
                        except ValueError:
                            years_set.add(str(y))
                    if has_mom and mom_period:
                        years_set.add(str(mom_period[0]))
                        years_set.add(str(mom_period[2]))
                    in_items = ", ".join(f"'{v}'" for v in sorted(years_set))
                    where_clauses.append(f"{expr} IN ({in_items})")
                    continue

                if nk == "month" and has_mom and mom_period:
                    t_y, t_m, p_y, p_m = mom_period
                    if t_y == p_y:
                        months_set = {str(t_m), str(p_m)}
                        in_items = ", ".join(f"'{v}'" for v in sorted(months_set, key=int))
                        where_clauses.append(f"{expr} IN ({in_items})")
                    else:
                        # 跨年情况（如 2026年1月 vs 2025年12月）
                        where_clauses.append(f"((year = {t_y} AND month = {t_m}) OR (year = {p_y} AND month = {p_m}))")
                    continue

                if nk == "month" and not (has_mom and mom_period):
                    raw_months = fval if isinstance(fval, (list, tuple, set)) else [str(fval)]
                    clean_months = []
                    for m in raw_months:
                        sm = str(m).strip().replace("月", "")
                        if sm and sm not in ("all", "ALL", "全部", "小计", "总计"):
                            clean_months.append(sm.replace("'", "''"))
                    if len(clean_months) == 1:
                        where_clauses.append(f"{expr} = '{clean_months[0]}'")
                    elif len(clean_months) > 1:
                        in_items = ", ".join(f"'{v}'" for v in clean_months)
                        where_clauses.append(f"{expr} IN ({in_items})")
                    continue

                if nk == "year" and not (has_yoy or has_mom):
                    raw_years = fval if isinstance(fval, (list, tuple, set)) else [str(fval)]
                    clean_years = []
                    for y in raw_years:
                        sy = str(y).strip().replace("年", "")
                        if sy and sy not in ("all", "ALL", "全部", "小计", "总计"):
                            clean_years.append(sy.replace("'", "''"))
                    if len(clean_years) == 1:
                        where_clauses.append(f"{expr} = '{clean_years[0]}'")
                    elif len(clean_years) > 1:
                        in_items = ", ".join(f"'{v}'" for v in clean_years)
                        where_clauses.append(f"{expr} IN ({in_items})")
                    continue

                if isinstance(fval, (list, tuple, set)):
                    valid_vals = [str(v).replace("'", "''") for v in fval if str(v) not in ("all", "ALL", "全部", "")]
                    if len(valid_vals) == 1:
                        where_clauses.append(f"{expr} = '{valid_vals[0]}'")
                    elif len(valid_vals) > 1:
                        in_items = ", ".join(f"'{v}'" for v in valid_vals)
                        where_clauses.append(f"{expr} IN ({in_items})")
                else:
                    val_str = str(fval).replace("'", "''")
                    where_clauses.append(f"{expr} = '{val_str}'")

        return where_clauses

    def _resolve_top_n_metric_alias(
        self,
        metrics_info: List[Dict[str, Any]],
        qty_col: str,
        is_intl: bool,
        pivot_col_metas: Optional[List[Dict[str, Any]]] = None,
        col_total_metas: Optional[List[Dict[str, Any]]] = None,
    ) -> Optional[str]:
        """
        解析 Top N 筛选所依据的指标列别名 (safe_alias)。
        支持无列维度模式与多列维度 (交叉透视表) 模式。
        1. 若指定了 top_n['metric']:
           - 先在 col_total_metas 中寻找匹配的汇总列 (如 "总计" 或 "总计_销售净收入 (元)")
           - 再在 pivot_col_metas 中寻找匹配列
           - 再在 metrics_info 中寻找匹配项
        2. 若未指定或未匹配到:
           - 若存在列总计 (col_total_metas)，优先使用第一个列总计别名 (对齐 Excel 默认按总计列过滤 Top N)
           - 否则使用 pivot_col_metas 的第一个列别名
           - 否则回退到 metrics_info 的第一个指标别名
        """
        desired_metric = (self.top_n or {}).get("metric")
        pivot_metas = pivot_col_metas or []
        total_metas = col_total_metas or []

        if desired_metric:
            norm_desired = self._normalize_dim_key(str(desired_metric))
            # 1.1 精确匹配已生成的安全别名或显示名称 (例如 "总计" 或 "2026_Q1_销售净收入 (元)")
            for meta in total_metas + pivot_metas:
                if (
                    meta.get("alias") == desired_metric
                    or meta.get("safe_alias") == desired_metric
                    or meta.get("safe_alias") == sanitize_identifier(str(desired_metric))
                ):
                    return meta["safe_alias"]

            # 1.2 按 metric field/id/alias 匹配列总计 (对齐 Excel 交叉表按该指标的 Grand Total 过滤)
            for ctm in total_metas:
                m = ctm.get("m_info") or {}
                _, base_alias = self._get_metric_sql_info(m, qty_col, is_intl)
                if (
                    m.get("field") == norm_desired
                    or m.get("id") == desired_metric
                    or base_alias == desired_metric
                    or m.get("alias") == desired_metric
                    or str(desired_metric) in (m.get("field"), m.get("id"), base_alias, m.get("alias"))
                ):
                    return ctm["safe_alias"]

            # 1.3 按 metric field/id/alias 匹配交叉列或基础列
            for pm in pivot_metas:
                m = pm.get("m_info") or {}
                _, base_alias = self._get_metric_sql_info(m, qty_col, is_intl)
                if (
                    m.get("field") == norm_desired
                    or m.get("id") == desired_metric
                    or base_alias == desired_metric
                    or m.get("alias") == desired_metric
                    or str(desired_metric) in (m.get("field"), m.get("id"), base_alias, m.get("alias"))
                ):
                    return pm["safe_alias"]

            # 1.4 回退匹配 metrics_info
            for m_info in metrics_info:
                _, base_alias = self._get_metric_sql_info(m_info, qty_col, is_intl)
                alias = m_info.get("alias") or base_alias
                if (
                    m_info.get("field") == norm_desired
                    or m_info.get("id") == desired_metric
                    or base_alias == desired_metric
                    or alias == desired_metric
                    or str(desired_metric) in (m_info.get("field"), m_info.get("id"), base_alias, alias)
                ):
                    return sanitize_identifier(alias)

        # 2. 未指定或未匹配到时：默认回退
        if total_metas:
            return total_metas[0]["safe_alias"]
        if pivot_metas:
            return pivot_metas[0]["safe_alias"]
        if metrics_info:
            first_info = metrics_info[0]
            _, base_alias = self._get_metric_sql_info(first_info, qty_col, is_intl)
            return sanitize_identifier(first_info.get("alias") or base_alias)

        return None

    def _wrap_sql_with_top_n(self, sql: str, metric_safe_alias: str) -> str:
        """
        在已生成的透视 SQL 外包裹一层 CTE，对明细行 (_grouping_id = 0) 应用 Top N 筛选。
        小计/总计行 (_grouping_id > 0) 全部保留，不参与筛选。

        实现方式：
        1. 将原 SQL (去除内层 LIMIT) 作为 inner CTE
        2. 用 ROW_NUMBER() OVER (ORDER BY metric DESC/ASC NULLS LAST) 对明细行编号
           (小计/总计行编号设为 NULL，确保不被 WHERE row_num <= N 过滤掉)
        3. 外层 WHERE row_num IS NULL OR row_num <= N
        4. 排序 ORDER BY _grouping_id ASC, _top_n_row_num ASC
        """
        top_n_cfg = self.top_n or {}
        count = int(top_n_cfg.get("count", 10))
        if count < 1:
            count = 1
        direction = str(top_n_cfg.get("direction", "top")).lower()
        order_dir = "DESC" if direction != "bottom" else "ASC"

        # 移除 inner SQL 尾部的 LIMIT 子句，确保 Top N 排名在全量明细数据上全局计算
        inner_sql = sql.rstrip().rstrip(';')
        inner_sql = re.sub(r"\s+LIMIT\s+\d+\s*$", "", inner_sql, flags=re.IGNORECASE)

        return f"""
WITH pivot_base AS (
    SELECT * FROM (
{inner_sql}
    )
),
pivot_ranked AS (
    SELECT
        *,
        CASE WHEN _grouping_id = 0
            THEN ROW_NUMBER() OVER (
                PARTITION BY CASE WHEN _grouping_id = 0 THEN 1 ELSE 0 END
                ORDER BY {metric_safe_alias} {order_dir} NULLS LAST
            )
            ELSE NULL
        END AS _top_n_row_num
    FROM pivot_base
)
SELECT *
FROM pivot_ranked
WHERE _top_n_row_num IS NULL OR _top_n_row_num <= {count}
ORDER BY _grouping_id ASC, _top_n_row_num ASC
LIMIT {self.limit};
""".strip()

    def translate(self) -> Tuple[str, str]:
        """执行 SQL 翻译生成工作流"""
        target_year = self.year or 2026
        self.view_name = resolve_view_name(self.product_class, target_year, self.con)
        if self.con and self.view_name:
            try:
                rows = self.con.execute(f"DESCRIBE {self.view_name}").fetchall()
                self.available_cols = {row[0] for row in rows}
            except Exception:
                self.available_cols = set()

        is_intl = "intl" in self.view_name.lower() or (self.product_class and self.product_class.lower() in ("intl", "overseas", "foreign", "海外", "国际"))

        qty_col = "invoice_qty_benti" if self.property_type in ("benti", "本体") else "invoice_qty"

        # 规范化维度 Key
        row_dim_keys = [self._normalize_dim_key(d) for d in self.raw_row_dims if d]
        col_dim_keys = [self._normalize_dim_key(d) for d in self.raw_col_dims if d]

        # 日期层次自动展开: 检测日期类型维度 (year/quarter/month/invoice_date)，
        # 自动补全为完整的 年→季度→月 层次结构 (对齐 Excel 透视表日期分组)。
        # 当 date_hierarchy=False 时不做展开。
        row_dim_keys = self._expand_date_hierarchy(row_dim_keys)
        col_dim_keys = self._expand_date_hierarchy(col_dim_keys)

        # 数值步长分组: 对配置了 numeric_grouping 的维度预生成分组 SQL 表达式
        # (对齐 Excel 透视表 "右键数值列 → 创建组 → 步长分组")。
        # 分组表达式缓存在 self._numeric_group_exprs，由 _get_dim_expr 注入到
        # SELECT / ROLLUP / GROUPING_ID 三处，确保小计/总计机制正确工作。
        row_dim_keys = self._apply_numeric_grouping(row_dim_keys, self.numeric_grouping)
        col_dim_keys = self._apply_numeric_grouping(col_dim_keys, self.numeric_grouping)

        # 暂存展开后的有效维度，供 _build_where_clauses 判断是否跳过年份/季度过滤
        self._effective_row_dims = row_dim_keys
        self._effective_col_dims = col_dim_keys

        all_dim_keys = set(row_dim_keys + col_dim_keys)
        is_year_in_dims = "year" in all_dim_keys
        is_month_in_dims = "month" in all_dim_keys
        is_quarter_in_dims = "quarter" in all_dim_keys

        # 构造 WHERE 过滤子句
        where_clauses = self._build_where_clauses(is_intl)
        where_str = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

        # 行维度 Select 表达式
        row_select_items = []
        row_group_exprs = []
        for d in row_dim_keys:
            expr = self._get_dim_expr(d, is_intl)
            label = self._get_dim_label(d)
            safe_alias = sanitize_identifier(label)
            row_group_exprs.append(expr)
            if self.include_subtotals and row_dim_keys:
                row_select_items.append(f"CASE WHEN GROUPING({expr}) = 1 THEN NULL ELSE {expr} END AS {safe_alias}")
            else:
                row_select_items.append(f"{expr} AS {safe_alias}")

        if not row_select_items:
            row_select_items = ['\'全部\' AS "汇总视角"']

        # 指标与列维度 Select 表达式
        metrics_info = [self._normalize_metric(m) for m in self.metrics_raw]

        col_select_items = []
        pivot_col_metas = []

        if col_dim_keys:
            col_exprs = [self._get_dim_expr(cd, is_intl) for cd in col_dim_keys]

            col_tuples = []
            if self.con:
                probe_sql = f"SELECT DISTINCT {', '.join(col_exprs)} FROM {self.view_name} {where_str} ORDER BY {', '.join(str(i+1) for i in range(len(col_dim_keys)))}"
                try:
                    col_tuples = self.con.execute(probe_sql).fetchall()
                except Exception:
                    col_tuples = []

            # 自然排序 col_tuples 确保 Q1 < Q2 < Q3 < Q4, 1月 < 2月 < 10月 等自然顺序
            if col_tuples:
                def _natural_key(combo):
                    parts = []
                    for val in combo:
                        if val is None:
                            parts.append(((0, -1, ""),))
                        else:
                            s = str(val)
                            sub_parts = []
                            for chunk in re.split(r'(\d+)', s):
                                if not chunk:
                                    continue
                                if chunk.isdigit():
                                    sub_parts.append((0, int(chunk), ""))
                                else:
                                    sub_parts.append((1, 0, chunk))
                            parts.append(tuple(sub_parts) if sub_parts else ((1, 0, ""),))
                    return tuple(parts)

                col_tuples.sort(key=_natural_key)

            # 校验 500 列防注入/爆炸上限
            if len(col_tuples) > MAX_PIVOT_COLS:
                raise ValueError("Pivot column limit exceeded (max 500)")

            if col_tuples:
                for combo in col_tuples:
                    combo_conds = []
                    for idx, val in enumerate(combo):
                        if val is None or val == "None" or val == "NULL":
                            combo_conds.append(f"({col_exprs[idx]} IS NULL OR {col_exprs[idx]} = '')")
                        else:
                            val_str = str(val).replace("'", "''")
                            combo_conds.append(f"{col_exprs[idx]} = '{val_str}'")
                    cond_str = " AND ".join(combo_conds)
                    combo_prefix = "_".join(str(v) for v in combo)

                    for m_info in metrics_info:
                        _, base_alias = self._get_metric_sql_info(m_info, qty_col, is_intl)
                        col_alias = f"{combo_prefix}_{base_alias}"
                        safe_col_alias = sanitize_identifier(col_alias)

                        case_agg_expr = self._build_case_agg_expr(m_info, cond_str, qty_col, is_intl)
                        col_select_items.append(f"{case_agg_expr} AS {safe_col_alias}")
                        pivot_col_metas.append({
                            "alias": col_alias,
                            "safe_alias": safe_col_alias,
                            "m_info": m_info,
                            "raw_expr": case_agg_expr
                        })

                self.column_tree = self._build_column_tree(col_tuples, col_dim_keys, metrics_info)

        if not col_select_items:
            has_yoy = self._has_yoy_metric()
            has_mom = self._has_mom_metric()
            for m_info in metrics_info:
                agg_expr, base_alias = self._get_metric_sql_info(m_info, qty_col, is_intl)
                safe_alias = sanitize_identifier(base_alias)
                col_select_items.append(f"{agg_expr} AS {safe_alias}")
                pivot_col_metas.append({
                    "alias": base_alias,
                    "safe_alias": safe_alias,
                    "m_info": m_info,
                    "raw_expr": agg_expr
                })
                # 当开启同比且年份未被作为维度切分时，自动为每个基础数值指标生成专属伴生同比列
                if has_yoy and not is_year_in_dims and m_info["field"] not in ("yoy_growth_rate", "同比增长率", "mom_growth_rate", "环比增长率", "replace_rate", "kunlun_replace_rate"):
                    comp_expr, comp_alias = self._get_companion_yoy_sql_info(m_info, qty_col, is_intl)
                    if comp_expr and comp_alias:
                        safe_comp_alias = sanitize_identifier(comp_alias)
                        col_select_items.append(f"{comp_expr} AS {safe_comp_alias}")
                # 当开启环比且月份未被作为维度切分时，自动为每个基础数值指标生成专属伴生环比列
                if has_mom and not is_month_in_dims and not is_quarter_in_dims and m_info["field"] not in ("yoy_growth_rate", "同比增长率", "mom_growth_rate", "环比增长率", "replace_rate", "kunlun_replace_rate"):
                    mom_expr, mom_alias = self._get_companion_mom_sql_info(m_info, qty_col, is_intl)
                    if mom_expr and mom_alias:
                        safe_mom_alias = sanitize_identifier(mom_alias)
                        col_select_items.append(f"{mom_expr} AS {safe_mom_alias}")

        # GROUP BY & ROLLUP 子句
        if self.include_subtotals and row_group_exprs:
            grouping_id_select = f"GROUPING_ID({', '.join(row_group_exprs)}) AS _grouping_id"
            group_by_clause = f"GROUP BY ROLLUP({', '.join(row_group_exprs)})"
        elif row_group_exprs:
            grouping_id_select = "0 AS _grouping_id"
            group_by_clause = f"GROUP BY {', '.join(row_group_exprs)}"
        else:
            grouping_id_select = "0 AS _grouping_id"
            group_by_clause = ""

        # 检查是否需要窗口函数计算占比 (show_as)
        has_show_as = any(m["show_as"] in ("percent_of_total", "percent_of_row", "percent_of_col", "percent_of_parent_row", "difference_from_total", "rank") for m in metrics_info)

        # ── 列总计 (Column Grand Total) 构建 ──────────────────────────
        # 当存在列维度时，追加"总计"列：该列为不按列维度分组的行维度汇总值。
        # 通过辅助 CTE (col_totals) 复用相同 ROLLUP 行分组，计算非条件聚合指标，
        # 再以行维度键 + _grouping_id 等值 (IS NOT DISTINCT FROM) JOIN 回主结果。
        has_col_totals = bool(col_dim_keys) and bool(col_select_items)

        # 列总计指标元信息：复用 _get_metric_sql_info 的非条件聚合表达式
        col_total_metas: List[Dict[str, Any]] = []
        if has_col_totals:
            for m_info in metrics_info:
                agg_expr, base_alias = self._get_metric_sql_info(m_info, qty_col, is_intl)
                # 单指标列名为"总计"；多指标列名为"总计_{base_alias}"以避免冲突
                total_alias = "总计" if len(metrics_info) == 1 else f"总计_{base_alias}"
                safe_total_alias = sanitize_identifier(total_alias)
                col_total_metas.append({
                    "alias": total_alias,
                    "safe_alias": safe_total_alias,
                    "m_info": m_info,
                    "raw_expr": agg_expr,
                })

        if not has_show_as and not has_col_totals:
            # 原始简单模式：无占比、无列总计
            select_clause = ",\n    ".join(row_select_items + [grouping_id_select] + col_select_items)
            self.sql = f"""
SELECT 
    {select_clause}
FROM {self.view_name}
{where_str}
{group_by_clause}
ORDER BY _grouping_id ASC
LIMIT {self.limit};
""".strip()
        elif not has_show_as and has_col_totals:
            # 简单模式 + 列总计：主聚合 CTE + 列总计 CTE，JOIN 合并
            main_select_clause = ",\n    ".join(row_select_items + [grouping_id_select] + col_select_items)

            # 列总计 CTE：相同 ROLLUP 行分组，非条件聚合指标
            ct_raw_selects = [f"{ctm['raw_expr']} AS {ctm['safe_alias']}" for ctm in col_total_metas]
            ct_select_items = row_select_items + [grouping_id_select] + ct_raw_selects
            ct_select_str = ",\n    ".join(ct_select_items)

            # JOIN 条件：行维度键 + _grouping_id 全部用 IS NOT DISTINCT FROM 匹配 (兼容 ROLLUP NULL)
            row_label_aliases = [sanitize_identifier(self._get_dim_label(d)) for d in row_dim_keys]
            if not row_label_aliases:
                row_label_aliases = ['"汇总视角"']
            join_conds = [f"m.{rl} IS NOT DISTINCT FROM ct.{rl}" for rl in row_label_aliases]
            join_conds.append("m._grouping_id IS NOT DISTINCT FROM ct._grouping_id")
            join_str = " AND ".join(join_conds)

            # 外层 SELECT：主 CTE 全部列 + 列总计 CTE 的总计列
            main_cols = [f"m.{rl}" for rl in row_label_aliases] + ["m._grouping_id"]
            main_cols += [f"m.{pmeta['safe_alias']}" for pmeta in pivot_col_metas]
            ct_cols = [f"ct.{ctm['safe_alias']}" for ctm in col_total_metas]
            outer_cols = main_cols + ct_cols
            outer_select_str = ",\n    ".join(outer_cols)

            self.sql = f"""
WITH main_pivot AS (
    SELECT 
        {main_select_clause}
    FROM {self.view_name}
    {where_str}
    {group_by_clause}
),
col_totals AS (
    SELECT 
        {ct_select_str}
    FROM {self.view_name}
    {where_str}
    {group_by_clause}
)
SELECT 
    {outer_select_str}
FROM main_pivot m
JOIN col_totals ct ON {join_str}
ORDER BY m._grouping_id ASC
LIMIT {self.limit};
""".strip()
        else:
            # CTE 模式：占比 (show_as) 计算，可选叠加列总计
            raw_col_selects = []
            outer_col_selects = []
            for idx, pmeta in enumerate(pivot_col_metas):
                raw_var = f"_m{idx}_raw"
                raw_col_selects.append(f"{pmeta['raw_expr']} AS {raw_var}")

                m_info = pmeta["m_info"]
                show_as = m_info["show_as"]
                safe_alias = pmeta["safe_alias"]

                if show_as == "percent_of_total":
                    outer_col_selects.append(
                        f"ROUND(({raw_var} / NULLIF(SUM(CASE WHEN _grouping_id = 0 THEN {raw_var} ELSE 0 END) OVER(), 0)) * 100.0, 2) AS {safe_alias}"
                    )
                elif show_as == "percent_of_row":
                    # 行占比：当前列 / 该行同一指标的全列汇总 (排除列总计重复相加，区分指标)
                    m_idx = idx % len(metrics_info)
                    if has_col_totals:
                        row_tot_expr = f"_ct{m_idx}_raw"
                    else:
                        same_metric_raw_vars = [
                            f"_m{i}_raw" for i in range(len(pivot_col_metas))
                            if (i % len(metrics_info)) == m_idx
                        ]
                        row_tot_expr = " + ".join(same_metric_raw_vars) if len(same_metric_raw_vars) > 1 else same_metric_raw_vars[0]
                    outer_col_selects.append(
                        f"ROUND(({raw_var} / NULLIF({row_tot_expr}, 0)) * 100.0, 2) AS {safe_alias}"
                    )
                elif show_as == "percent_of_col":
                    outer_col_selects.append(
                        f"ROUND(({raw_var} / NULLIF(SUM(CASE WHEN _grouping_id = 0 THEN {raw_var} ELSE 0 END) OVER(), 0)) * 100.0, 2) AS {safe_alias}"
                    )
                elif show_as == "percent_of_parent_row":
                    # 父行百分比：当前值 / 父级分组的汇总值
                    # 单行维度场景：父级 = 顶层汇总 (sum of leaf rows)
                    # 多行维度场景：叶子行按父级维度(除最后一层外的所有父维度)分组求和，顶层或小计行回退到总计
                    if len(row_dim_keys) <= 1:
                        outer_col_selects.append(
                            f"ROUND(({raw_var} / NULLIF(SUM(CASE WHEN _grouping_id = 0 THEN {raw_var} ELSE 0 END) OVER(), 0)) * 100.0, 2) AS {safe_alias}"
                        )
                    else:
                        parent_dim_aliases = [sanitize_identifier(self._get_dim_label(d)) for d in row_dim_keys[:-1]]
                        parent_part_clause = ", ".join(parent_dim_aliases)
                        outer_col_selects.append(
                            f"ROUND(({raw_var} / NULLIF(COALESCE(NULLIF(SUM(CASE WHEN _grouping_id = 0 THEN {raw_var} ELSE 0 END) OVER (PARTITION BY {parent_part_clause}), 0), SUM(CASE WHEN _grouping_id = 0 THEN {raw_var} ELSE 0 END) OVER()), 0)) * 100.0, 2) AS {safe_alias}"
                        )
                elif show_as == "difference_from_total":
                    # 与总计的差异：当前值 - 总计值 (总计行本身设为 0.00，避免浮点舍入误差)
                    grand_total_gid = (1 << len(row_dim_keys)) - 1
                    outer_col_selects.append(
                        f"CASE WHEN _grouping_id = {grand_total_gid} THEN 0.00 ELSE ROUND({raw_var} - SUM(CASE WHEN _grouping_id = 0 THEN {raw_var} ELSE 0 END) OVER(), 2) END AS {safe_alias}"
                    )
                elif show_as == "rank":
                    # 排名：仅对明细行 (_grouping_id = 0) 按当前指标值降序排名，小计/总计行置 NULL
                    outer_col_selects.append(
                        f"CASE WHEN _grouping_id = 0 THEN RANK() OVER (PARTITION BY CASE WHEN _grouping_id = 0 THEN 1 ELSE 0 END ORDER BY {raw_var} DESC) ELSE NULL END AS {safe_alias}"
                    )
                else:
                    outer_col_selects.append(f"ROUND({raw_var}, 2) AS {safe_alias}")

            # 列总计原始值变量 (供 percent_of_row 行汇总分母使用)
            ct_raw_selects = []
            ct_outer_selects = []
            for ct_idx, ctm in enumerate(col_total_metas):
                ct_raw_var = f"_ct{ct_idx}_raw"
                ct_raw_selects.append(f"{ctm['raw_expr']} AS {ct_raw_var}")

                m_info = ctm["m_info"]
                show_as = m_info["show_as"]
                safe_alias = ctm["safe_alias"]

                if show_as == "percent_of_total":
                    ct_outer_selects.append(
                        f"ROUND(({ct_raw_var} / NULLIF(SUM(CASE WHEN _grouping_id = 0 THEN {ct_raw_var} ELSE 0 END) OVER(), 0)) * 100.0, 2) AS {safe_alias}"
                    )
                elif show_as == "percent_of_row":
                    # 列总计的行占比恒为 100% (列总计 = 该行全列汇总)
                    ct_outer_selects.append(f"100.00 AS {safe_alias}")
                elif show_as == "percent_of_col":
                    ct_outer_selects.append(
                        f"ROUND(({ct_raw_var} / NULLIF(SUM(CASE WHEN _grouping_id = 0 THEN {ct_raw_var} ELSE 0 END) OVER(), 0)) * 100.0, 2) AS {safe_alias}"
                    )
                elif show_as == "percent_of_parent_row":
                    # 列总计本身即为父级汇总，父行百分比恒为 100%
                    ct_outer_selects.append(f"100.00 AS {safe_alias}")
                elif show_as == "difference_from_total":
                    # 列总计 - 总计 = 0
                    ct_outer_selects.append(f"0.00 AS {safe_alias}")
                elif show_as == "rank":
                    # 列总计行不参与排名
                    ct_outer_selects.append(f"NULL AS {safe_alias}")
                else:
                    ct_outer_selects.append(f"ROUND({ct_raw_var}, 2) AS {safe_alias}")

            cte_select_items = row_select_items + [grouping_id_select] + raw_col_selects + ct_raw_selects
            cte_select_str = ",\n        ".join(cte_select_items)
            outer_row_labels = [sanitize_identifier(self._get_dim_label(d)) for d in row_dim_keys]
            if not outer_row_labels:
                outer_row_labels = ['"汇总视角"']

            outer_select_items = outer_row_labels + ["_grouping_id"] + outer_col_selects + ct_outer_selects
            outer_select_str = ",\n    ".join(outer_select_items)

            self.sql = f"""
WITH base_pivot AS (
    SELECT 
        {cte_select_str}
    FROM {self.view_name}
    {where_str}
    {group_by_clause}
)
SELECT 
    {outer_select_str}
FROM base_pivot
ORDER BY _grouping_id ASC
LIMIT {self.limit};
""".strip()

        # Top N 值筛选 (对齐 Excel 透视表 "值筛选 → 前 10 项/后 10 项")
        # 仅当 top_n 启用且存在行维度时生效；在已生成 SQL 外包裹 CTE，
        # 对明细行 (_grouping_id = 0) 按 ROW_NUMBER() 筛选前/后 N 项，
        # 小计与总计行全部保留。
        top_n_applied = False
        if self.top_n and self.top_n.get("enabled") and row_dim_keys:
            metric_safe_alias = self._resolve_top_n_metric_alias(
                metrics_info, qty_col, is_intl, pivot_col_metas, col_total_metas
            )
            if metric_safe_alias:
                self.sql = self._wrap_sql_with_top_n(self.sql, metric_safe_alias)
                top_n_applied = True

        # 标注日期层次维度的中文名称 (年/季度/月)，供前端 column_tree 渲染
        row_dim_labels = [{"key": d, "label": self._get_dim_label(d)} for d in row_dim_keys]
        col_dim_labels = [{"key": d, "label": self._get_dim_label(d)} for d in col_dim_keys]

        # 标注应用了数值步长分组的维度元信息 (供前端 column_tree 渲染区间标签)
        numeric_grouping_applied = [
            {
                "key": k,
                "label": self._numeric_group_labels.get(k, k),
                "step": (self.numeric_grouping.get(k) or {}).get("step"),
                "start": (self.numeric_grouping.get(k) or {}).get("start"),
                "end": (self.numeric_grouping.get(k) or {}).get("end"),
            }
            for k in list(self._numeric_group_exprs.keys())
        ]

        self.grouping_meta = {
            "row_dims": row_dim_keys,
            "col_dims": col_dim_keys,
            "row_dim_labels": row_dim_labels,
            "col_dim_labels": col_dim_labels,
            "subtotals_included": self.include_subtotals,
            "date_hierarchy": self.date_hierarchy,
            "date_hierarchy_applied": (
                self.date_hierarchy
                and any(self._normalize_dim_key(d) in self.DATE_DIM_KEYS for d in self.raw_row_dims + self.raw_col_dims if d)
            ),
            "numeric_grouping_applied": numeric_grouping_applied,
            "top_n_applied": top_n_applied,
            "top_n_config": self.top_n if (top_n_applied) else None,
        }

        return self.sql, self.view_name


def build_pivot_sql(
    row_dims: List[str],
    col_dim: Optional[Union[str, List[str]]] = None,
    metrics: Optional[List[Union[str, dict, Any]]] = None,
    year: Optional[int] = 2026,
    product_class: Optional[str] = "acb",
    property_type: Optional[str] = "all",
    quarter: Optional[str] = "all",
    limit: int = 500,
    con: Any = None,
    include_subtotals: bool = True,
    col_dims: Optional[List[str]] = None,
    filters: Optional[Dict[str, Any]] = None,
    date_hierarchy: bool = False,
    numeric_grouping: Optional[Dict[str, Dict[str, Any]]] = None,
    top_n: Optional[Dict[str, Any]] = None,
) -> Tuple[str, str]:
    """
    构造多维透视 SQL 查询 (保持 100% 向下兼容)
    返回: (sql_string, target_view_name)

    Args:
        numeric_grouping: 可选数值步长分组配置，格式
            {dim_id: {'step': float, 'start': float|None, 'end': float|None}}
            对齐 Excel 透视表 "右键数值列 → 创建组 → 步长分组"。
        top_n: 可选 Top N 值筛选配置，格式
            {'enabled': bool, 'count': int, 'direction': 'top'|'bottom', 'metric': str}
            对齐 Excel 透视表 "值筛选 → 前 10 项/后 10 项"。
            仅作用于行维度明细行 (_grouping_id = 0)，不影响小计与总计行。
    """
    should_close = False
    if con is None:
        try:
            from config import get_duckdb_path
            db_file = get_duckdb_path(product_class)
        except Exception:
            db_file = "data/database/acb.duckdb"
        if os.path.exists(db_file):
            try:
                con = duckdb.connect(db_file, read_only=True)
                should_close = True
            except Exception:
                con = None

    resolved_col_dims = col_dims or ([col_dim] if col_dim else [])
    translator = PivotSQLTranslator(
        row_dims=row_dims,
        col_dims=resolved_col_dims,
        metrics=metrics,
        year=year,
        product_class=product_class,
        property_type=property_type,
        quarter=quarter,
        include_subtotals=include_subtotals,
        limit=limit,
        con=con,
        filters=filters,
        date_hierarchy=date_hierarchy,
        numeric_grouping=numeric_grouping,
        top_n=top_n,
    )
    sql, view_name = translator.translate()
    if should_close and con:
        try:
            con.close()
        except Exception:
            pass
    return sql, view_name


def build_drilldown_sql(
    row_filters: Optional[Dict[str, Any]] = None,
    col_filters: Optional[Dict[str, Any]] = None,
    global_filters: Optional[Dict[str, Any]] = None,
    year: Optional[int] = 2026,
    product_class: Optional[str] = "acb",
    property_type: Optional[str] = "all",
    quarter: Optional[str] = "all",
    limit: int = 500,
    con: Any = None,
) -> Tuple[str, str]:
    """
    构造明细钻取 SQL 查询
    根据用户在透视表点击的单元格筛选条件（row_filters 与 col_filters 及全局 global_filters），精确定位底层明细单据行
    返回: (sql_string, target_view_name)
    """
    view_name = resolve_view_name(product_class, year or 2026, con)
    is_intl = "intl" in view_name.lower() or (product_class and product_class.lower() in ("intl", "overseas", "foreign", "海外", "国际"))

    where_clauses = []
    if year and str(year).lower() != "all":
        try:
            where_clauses.append(f"year = {int(year)}")
        except (ValueError, TypeError):
            pass

    if quarter and str(quarter).lower() != "all":
        q_map = {"q1": (1, 3), "q2": (4, 6), "q3": (7, 9), "q4": (10, 12)}
        q_range = q_map.get(str(quarter).lower())
        if q_range:
            where_clauses.append(f"month BETWEEN {q_range[0]} AND {q_range[1]}")

    if property_type and property_type != "all":
        if property_type in ("benti", "本体"):
            where_clauses.append("property_type = '本体'")
        elif property_type in ("non_benti", "非本体", "附件"):
            where_clauses.append("property_type != '本体'")

    merged_filters = {}
    if global_filters:
        for gk, gv in global_filters.items():
            if gk not in ("groupA", "groupB") and not str(gk).startswith("__"):
                merged_filters[gk] = gv
    if row_filters:
        merged_filters.update(row_filters)
    if col_filters:
        merged_filters.update(col_filters)

    for fk, fval in merged_filters.items():
        if fval is not None and str(fval) not in ("all", "ALL", "全部", "小计", "总计", ""):
            nk = CHINESE_COL_ALIAS.get(fk, fk)
            if nk in ("quarter", "selectedQuarter", "selected_quarter", "quarter_rev") and isinstance(fval, str) and fval.upper() in ("Q1", "Q2", "Q3", "Q4"):
                q_map = {"Q1": (1, 3), "Q2": (4, 6), "Q3": (7, 9), "Q4": (10, 12)}
                q_range = q_map[fval.upper()]
                where_clauses.append(f"month BETWEEN {q_range[0]} AND {q_range[1]}")
                continue
            expr = DIM_COL_MAP.get(nk, sanitize_identifier(nk))
            if isinstance(fval, (list, tuple, set)):
                items = [str(x).replace("'", "''") for x in fval if x is not None and str(x) != ""]
                if items:
                    in_str = ", ".join([f"'{x}'" for x in items])
                    where_clauses.append(f"{expr} IN ({in_str})")
            else:
                val_str = str(fval).replace("'", "''")
                where_clauses.append(f"{expr} = '{val_str}'")

    where_str = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

    sql = f"""
SELECT *
FROM {view_name}
{where_str}
LIMIT {limit};
""".strip()

    return sql, view_name



# ── 5. 全量大屏 6 大面板 SQL 构建集合 ───────────────────────────
def build_full_dashboard_sqls(
    year: Optional[int] = None,
    product_class: str = "acb",
    property_type: str = "benti",
    quarter: Optional[str] = "all",
    con: Any = None
) -> Dict[str, Any]:
    """
    构造全量数据分析大屏 6 大核心维度的 SQL 语句集合
    返回包含各个 SQL 文本及对应视图信息的字典
    """
    if year is None and con:
        try:
            res_y = con.execute("SELECT COALESCE(MAX(year), 2026) FROM v_sales_all").fetchone()
            year = int(res_y[0]) if (res_y and res_y[0]) else 2026
        except Exception:
            year = 2026
    elif year is None:
        year = 2026

    view_name = resolve_view_name(product_class, year, con)
    
    prop_where = ""
    if property_type in ("non_benti", "非本体"):
        prop_where = "WHERE property_type != '本体'"
    elif property_type in ("benti", "本体"):
        prop_where = "WHERE property_type = '本体'"

    qty_col = "invoice_qty"

    # 动态计算月份区间对齐条件 (e.g. AND month <= 6)
    max_month, m_cond = resolve_max_month_condition(year, quarter, view_name, con)

    # 构造中国区专属卡片的显式过滤条件 (确保不受海外区并入干扰)
    cn_cond = "(report_source LIKE '%中国%' OR report_source_rev LIKE '%中国%')"
    prop_where_cn = f"{prop_where} AND {cn_cond}" if prop_where else f"WHERE {cn_cond}"

    # 1. 维度 1: KPI 大盘汇总 (同月度区间可比 YoY)
    sql_kpi = f"""
        SELECT 
            COALESCE(SUM(CASE WHEN year = {year} {m_cond} THEN net_revenue ELSE 0 END), 0) AS sales_revenue,
            COALESCE(SUM(CASE WHEN year = {year - 1} {m_cond} THEN net_revenue ELSE 0 END), 0) AS prev_revenue,
            COALESCE(SUM(CASE WHEN year = {year} {m_cond} THEN {qty_col} ELSE 0 END), 0) AS benti_qty,
            COALESCE(SUM(CASE WHEN year = {year - 1} {m_cond} THEN {qty_col} ELSE 0 END), 0) AS prev_qty,
            COALESCE(SUM(CASE WHEN year = {year} {m_cond} AND report_source LIKE '%诺雅克%' THEN net_revenue ELSE 0 END), 0) AS noark_rev,
            COALESCE(SUM(CASE WHEN year = {year} {m_cond} THEN gross_profit ELSE 0 END), 0) AS gross_profit
        FROM {view_name}
        {prop_where};
    """.strip()

    # 2. 维度 2: 中国区产品系列
    sql_p_cn = f"""
        SELECT 
            product_series AS series,
            product_series AS product_series,
            SUM(CASE WHEN year = {year} {m_cond} THEN net_revenue ELSE 0 END) AS revenue,
            SUM(CASE WHEN year = {year} {m_cond} THEN net_revenue ELSE 0 END) AS total_net_revenue,
            SUM(CASE WHEN year = {year - 1} {m_cond} THEN net_revenue ELSE 0 END) AS prev_revenue,
            ROUND((SUM(CASE WHEN year = {year} {m_cond} THEN net_revenue ELSE 0 END) - SUM(CASE WHEN year = {year - 1} {m_cond} THEN net_revenue ELSE 0 END)) / NULLIF(SUM(CASE WHEN year = {year - 1} {m_cond} THEN net_revenue ELSE 0 END), 0) * 100.0, 2) AS yoy_revenue_pct,
            SUM(CASE WHEN year = {year} {m_cond} THEN {qty_col} ELSE 0 END) AS qty,
            SUM(CASE WHEN year = {year} {m_cond} THEN {qty_col} ELSE 0 END) AS total_sales_qty
        FROM {view_name}
        {prop_where_cn}
        GROUP BY 1
        ORDER BY revenue DESC
        LIMIT 10;
    """.strip()

    # 3. 维度 3: 海外区产品系列
    sql_p_intl = f"""
        SELECT 
            product_series AS series,
            product_series AS product_series,
            SUM(CASE WHEN year = {year} {m_cond} THEN net_revenue ELSE 0 END) AS revenue,
            SUM(CASE WHEN year = {year} {m_cond} THEN net_revenue ELSE 0 END) AS total_net_revenue,
            SUM(CASE WHEN year = {year - 1} {m_cond} THEN net_revenue ELSE 0 END) AS prev_revenue,
            ROUND((SUM(CASE WHEN year = {year} {m_cond} THEN net_revenue ELSE 0 END) - SUM(CASE WHEN year = {year - 1} {m_cond} THEN net_revenue ELSE 0 END)) / NULLIF(SUM(CASE WHEN year = {year - 1} {m_cond} THEN net_revenue ELSE 0 END), 0) * 100.0, 2) AS yoy_revenue_pct,
            SUM(CASE WHEN year = {year} {m_cond} THEN {qty_col} ELSE 0 END) AS qty,
            SUM(CASE WHEN year = {year} {m_cond} THEN {qty_col} ELSE 0 END) AS total_sales_qty
        FROM v_chint_intl_sales
        GROUP BY 1
        ORDER BY revenue DESC
        LIMIT 10;
    """.strip()

    # 4. 维度 4: 中国区行业团队与区域
    sql_ind = f"""
        SELECT 
            COALESCE(sales_team_rev, sales_team, '其它团队') AS sales_team_cls,
            COALESCE(sales_team_rev, sales_team, '其它行业') AS industry,
            SUM(CASE WHEN year = {year} {m_cond} THEN net_revenue ELSE 0 END) AS revenue,
            SUM(CASE WHEN year = {year} {m_cond} THEN net_revenue ELSE 0 END) AS total_net_revenue,
            SUM(CASE WHEN year = {year - 1} {m_cond} THEN net_revenue ELSE 0 END) AS prev_revenue,
            ROUND((SUM(CASE WHEN year = {year} {m_cond} THEN net_revenue ELSE 0 END) - SUM(CASE WHEN year = {year - 1} {m_cond} THEN net_revenue ELSE 0 END)) / NULLIF(SUM(CASE WHEN year = {year - 1} {m_cond} THEN net_revenue ELSE 0 END), 0) * 100.0, 2) AS yoy_revenue_pct,
            SUM(CASE WHEN year = {year} {m_cond} THEN {qty_col} ELSE 0 END) AS qty,
            SUM(CASE WHEN year = {year} {m_cond} THEN {qty_col} ELSE 0 END) AS total_sales_qty
        FROM {view_name}
        {prop_where_cn}
        GROUP BY 1, 2
        ORDER BY revenue DESC
        LIMIT 10;
    """.strip()

    # 5. 维度 5: 海外出口 Top 10 与大区
    sql_intl_reg = f"""
        SELECT 
            COALESCE(country_name, continent, '海外国家') AS country,
            COALESCE(region_rev, continent, '海外大区') AS region,
            SUM(CASE WHEN year = {year} {m_cond} THEN net_revenue ELSE 0 END) AS revenue,
            SUM(CASE WHEN year = {year} {m_cond} THEN net_revenue ELSE 0 END) AS total_net_revenue,
            SUM(CASE WHEN year = {year - 1} {m_cond} THEN net_revenue ELSE 0 END) AS prev_revenue,
            ROUND((SUM(CASE WHEN year = {year} {m_cond} THEN net_revenue ELSE 0 END) - SUM(CASE WHEN year = {year - 1} {m_cond} THEN net_revenue ELSE 0 END)) / NULLIF(SUM(CASE WHEN year = {year - 1} {m_cond} THEN net_revenue ELSE 0 END), 0) * 100.0, 2) AS yoy_revenue_pct,
            SUM(CASE WHEN year = {year} {m_cond} THEN {qty_col} ELSE 0 END) AS qty,
            SUM(CASE WHEN year = {year} {m_cond} THEN {qty_col} ELSE 0 END) AS total_sales_qty
        FROM v_chint_intl_sales
        GROUP BY 1, 2
        ORDER BY revenue DESC
        LIMIT 10;
    """.strip()

    # 6. 维度 6: 中国区大区与省份 (对标海外洲区)
    sql_cn_regions = f"""
        SELECT 
            COALESCE(region_rev, sales_team_rev, province, '未划分大区') AS region,
            COALESCE(province, region_rev, '未知省份') AS province,
            SUM(CASE WHEN year = {year} {m_cond} THEN net_revenue ELSE 0 END) AS revenue,
            SUM(CASE WHEN year = {year} {m_cond} THEN net_revenue ELSE 0 END) AS total_net_revenue,
            SUM(CASE WHEN year = {year - 1} {m_cond} THEN net_revenue ELSE 0 END) AS prev_revenue,
            ROUND((SUM(CASE WHEN year = {year} {m_cond} THEN net_revenue ELSE 0 END) - SUM(CASE WHEN year = {year - 1} {m_cond} THEN net_revenue ELSE 0 END)) / NULLIF(SUM(CASE WHEN year = {year - 1} {m_cond} THEN net_revenue ELSE 0 END), 0) * 100.0, 2) AS yoy_revenue_pct,
            SUM(CASE WHEN year = {year} {m_cond} THEN {qty_col} ELSE 0 END) AS qty,
            SUM(CASE WHEN year = {year} {m_cond} THEN {qty_col} ELSE 0 END) AS total_sales_qty
        FROM {view_name}
        {prop_where_cn}
        GROUP BY 1, 2
        ORDER BY revenue DESC
        LIMIT 10;
    """.strip()

    # 7. 维度 7: 毛利率与成本结构 (分视角)
    sql_margin = f"""
        SELECT 
            product_series AS series,
            product_series AS product_series,
            SUM(net_revenue) AS revenue,
            SUM(net_revenue) AS total_net_revenue,
            SUM(product_cost) AS cost,
            SUM(gross_profit) AS gross_profit,
            ROUND(SUM(gross_profit) / NULLIF(SUM(net_revenue), 0) * 100.0, 2) AS gross_profit_rate
        FROM {view_name}
        WHERE year = {year} {m_cond} {prop_where_cn.replace('WHERE', 'AND')}
        GROUP BY 1
        ORDER BY revenue DESC
        LIMIT 10;
    """.strip()

    sql_intl_margin = f"""
        SELECT 
            product_series AS series,
            product_series AS product_series,
            SUM(net_revenue) AS revenue,
            SUM(net_revenue) AS total_net_revenue,
            SUM(product_cost) AS cost,
            SUM(gross_profit) AS gross_profit,
            ROUND(SUM(gross_profit) / NULLIF(SUM(net_revenue), 0) * 100.0, 2) AS gross_profit_rate
        FROM v_chint_intl_sales
        WHERE year = {year} {m_cond}
        GROUP BY 1
        ORDER BY revenue DESC
        LIMIT 10;
    """.strip()

    # 8. 维度 8: 部门维度销售额与销量汇总表 (动态检测视图存在性，跳过缺失视图)
    dept_views = [
        ("ACB 框架断路器", "v_sales_acb"),
        ("MCCB 塑壳断路器", "v_sales_mccb"),
        ("PQ 电能质量", "v_sales_pq"),
        ("ATSE 双电源", "v_sales_atse"),
        ("VF 虚拟工厂", "v_sales_vf"),
    ]
    available_dept_views = []
    for dept_label, dept_vn in dept_views:
        if con is not None:
            try:
                con.execute(f"SELECT 1 FROM {dept_vn} LIMIT 1").fetchone()
                available_dept_views.append((dept_label, dept_vn))
            except Exception:
                pass
        else:
            available_dept_views.append((dept_label, dept_vn))

    dept_union_parts = []
    for dept_label, dept_vn in available_dept_views:
        dept_union_parts.append(f"""
            SELECT 
                '{dept_label}' AS department,
                COALESCE(SUM(CASE WHEN year = {year} {m_cond} THEN net_revenue ELSE 0 END), 0) AS revenue,
                COALESCE(SUM(CASE WHEN year = {year} {m_cond} THEN invoice_qty ELSE 0 END), 0) AS qty,
                ROUND(COALESCE(SUM(CASE WHEN year = {year} {m_cond} THEN gross_profit ELSE 0 END) / NULLIF(SUM(CASE WHEN year = {year} {m_cond} THEN net_revenue ELSE 0 END), 0) * 100.0, 0), 2) AS gross_margin_rate
            FROM {dept_vn}
        """.strip())

    if dept_union_parts:
        sql_dept_summary = "\n        UNION ALL\n        ".join(dept_union_parts) + ";"
    else:
        sql_dept_summary = f"""
            SELECT 
                '全部部门' AS department,
                COALESCE(SUM(CASE WHEN year = {year} {m_cond} THEN net_revenue ELSE 0 END), 0) AS revenue,
                COALESCE(SUM(CASE WHEN year = {year} {m_cond} THEN invoice_qty ELSE 0 END), 0) AS qty,
                ROUND(COALESCE(SUM(CASE WHEN year = {year} {m_cond} THEN gross_profit ELSE 0 END) / NULLIF(SUM(CASE WHEN year = {year} {m_cond} THEN net_revenue ELSE 0 END), 0) * 100.0, 0), 2) AS gross_margin_rate
            FROM {view_name}
            {prop_where};
        """.strip()

    return {
        "view_name": view_name,
        "kpi": sql_kpi,
        "china_series": sql_p_cn,
        "overseas_series": sql_p_intl,
        "china_industry_region": sql_ind,
        "overseas_regions": sql_intl_reg,
        "china_regions": sql_cn_regions,
        "margin_structure": sql_margin,
        "overseas_margin_structure": sql_intl_margin,
        "department_summary": sql_dept_summary
    }


def get_analytics_metadata() -> Dict[str, Any]:
    """暴露引擎的完整维度、指标与别名元数据（供 AI Agent 自我感知与前端动态元数据接口调用）"""
    return {
        "dimensions": list(DIM_COL_MAP.keys()),
        "dimension_expressions": DIM_COL_MAP,
        "metrics": list(METRIC_MAP.keys()),
        "metric_units": {
            "revenue": "元",
            "total_net_revenue": "元",
            "qty": "台/万台",
            "quantity": "台/万台",
            "benti_qty": "台/万台",
            "cost": "元",
            "gross_profit": "元",
            "gross_margin_rate": "%"
        },
        "chinese_aliases": CHINESE_COL_ALIAS,
        "supported_views": [
            "v_sales_detailed",
            "v_sales_monthly",
            "v_sales_all",
            "v_sales_acb",
            "v_sales_mccb",
            "v_sales_pq",
            "v_sales_atse",
            "v_sales_vf",
            "v_china_sales_monthly",
            "v_overseas_sales_monthly"
        ]
    }


RAW_HEADER_ID_MAP: Dict[str, str] = {
    "报表来源": "report_source",
    "产业": "industry",
    "业务分类": "biz_category",
    "洲区": "continent",
    "国家": "country",
    "国家名称": "country_name",
    "省份": "province",
    "年份": "year",
    "月份": "month",
    "生产制造单位编码": "mfg_unit_code",
    "生产制造单位": "mfg_unit",
    "物料组编码": "material_group_code",
    "物料组描述": "material_group_desc",
    "物料编码": "material_code",
    "物料描述": "material_desc",
    "客户性质": "customer_nature",
    "网点客户号": "outlet_customer_no",
    "网点客户名称": "outlet_customer_name",
    "客户号": "customer_no",
    "客户名称": "customer_name",
    "终端客户": "terminal_customer",
    "项目编号": "project_no",
    "项目名称": "project_name",
    "销售组织编码": "sales_org_code",
    "销售组织": "sales_org",
    "新政策大类": "new_policy_category",
    "发票数量": "invoice_qty",
    "开单价金额（含税）": "billing_price_amount",
    "结算价金额（含税）": "settlement_price_amount",
    "净额（不含税）": "net_amount",
    "折让（不含税）": "discount_amount",
    "费用（不含税）": "expense_amount",
    "净收入（不含税）": "net_revenue",
    "口袋价（含税）": "pocket_price",
    "产品成本（不含税）": "product_cost",
    "总成本（不含税）": "total_cost",
    "毛利额（不含税）": "gross_profit",
    "本位币种": "currency",
    "汇率(本币)": "exchange_rate",
    "收入（本币）": "revenue_local_currency",
    "成本（本币）": "cost_local_currency",
    "产品产业分类": "product_industry_category",
    "销售团队": "sales_team_raw",
    "通用/专业": "general_or_specialized",
    "产品系列": "product_series_raw",
    "产品平台": "product_platform",
    "产品管理团队": "product_manager_team",
    "产品大类": "product_category",
    "内配客户标记": "internal_customer_flag",
}

DEFAULT_RAW_HEADERS: List[str] = [
    "报表来源", "产业", "业务分类", "洲区", "国家", "国家名称", "省份", "年份", "月份",
    "生产制造单位编码", "生产制造单位", "物料组编码", "物料组描述", "物料编码", "物料描述",
    "客户性质", "网点客户号", "网点客户名称", "客户号", "客户名称", "终端客户",
    "项目编号", "项目名称", "销售组织编码", "销售组织", "新政策大类", "发票数量",
    "开单价金额（含税）", "结算价金额（含税）", "净额（不含税）", "折让（不含税）", "费用（不含税）",
    "净收入（不含税）", "口袋价（含税）", "产品成本（不含税）", "总成本（不含税）", "毛利额（不含税）",
    "本位币种", "汇率(本币)", "收入（本币）", "成本（本币）", "产品产业分类", "销售团队",
    "通用/专业", "产品系列", "产品平台", "产品管理团队", "产品大类", "内配客户标记"
]


def get_raw_excel_headers(excel_path: Optional[str] = None) -> List[str]:
    """
    动态直接提取 raw 原始 Excel 文件 (如 26年1-7月配电电器合并报表.xlsx) 第一行的全量字段名称，严格保留先后物理顺序
    """
    if not excel_path:
        from config import BASE_DIR
        target_file = os.path.join(BASE_DIR, "data", "raw", "26年1-7月配电电器合并报表.xlsx")
        if os.path.exists(target_file):
            excel_path = target_file
        else:
            try:
                from etl.data_processor import find_latest_files
                files_dict = find_latest_files()
                excel_path = files_dict.get("supp_2026") or files_dict.get("src_main")
            except Exception:
                excel_path = None

    if excel_path and os.path.exists(excel_path):
        try:
            import openpyxl
            wb = openpyxl.load_workbook(excel_path, read_only=True)
            sheet_name = "中国区" if "中国区" in wb.sheetnames else wb.sheetnames[0]
            ws = wb[sheet_name]
            for row in ws.iter_rows(max_row=1, values_only=True):
                headers = [str(c).strip() for c in row if c is not None and str(c).strip()]
                if headers:
                    return headers
        except Exception:
            pass

    return DEFAULT_RAW_HEADERS


def get_department_dimensions_metadata(dept: str = "acb") -> Dict[str, Any]:
    """返回给定部门的动态元数据规范字典，供前端自动适配维度与列名映射"""
    d = (dept or "acb").lower()
    
    raw_headers = get_raw_excel_headers()
    dims: List[Dict[str, Any]] = []

    # 1. 原始物理字段：严格按 Excel 文件第一行顺序动态生成
    for h in raw_headers:
        dim_id = RAW_HEADER_ID_MAP.get(h, h)
        dims.append({"id": dim_id, "label": h, "layer": "raw", "dept": "common"})

    # 2. 映射/语义字段 (通用)：严格剔除"报表来源"，仅保留纯映射派生维度
    dims.extend([
        {"id": "property_type", "label": "属性", "layer": "semantic", "dept": "common"},
        {"id": "product_model", "label": "产品型号", "layer": "semantic", "dept": "common"},
        {"id": "quarter", "label": "季度", "layer": "semantic", "dept": "common"},
        {"id": "region", "label": "区域", "layer": "semantic", "dept": "common"},
        {"id": "sales_team", "label": "销售团队", "layer": "semantic", "dept": "common"},
        {"id": "biz_type", "label": "业务类型", "layer": "semantic", "dept": "common"},
        {"id": "product_series", "label": "产品系列", "layer": "semantic", "dept": "common"},
        {"id": "frame_current", "label": "壳架电流", "layer": "semantic", "dept": "common"},
        {"id": "breaking_capacity", "label": "分断能力", "layer": "semantic", "dept": "common"},
        {"id": "operation_method", "label": "安装方式", "layer": "semantic", "dept": "common"},
        {"id": "pole_count", "label": "极数", "layer": "semantic", "dept": "common"},
        {"id": "n_pole_type", "label": "N极连接方式", "layer": "semantic", "dept": "common"},
    ])
    
    # 3. 部门专属映射维度 (纯中文规范显示，无需品类后缀)
    if d == "acb":
        dims.extend([
            {"id": "acb_frame_current", "label": "壳架电流", "layer": "semantic", "dept": "acb"},
            {"id": "acb_installation_type", "label": "安装方式", "layer": "semantic", "dept": "acb"},
            {"id": "n_pole_connection", "label": "N极连接方式", "layer": "semantic", "dept": "acb"},
        ])
    elif d == "mccb":
        dims.extend([
            {"id": "mccb_breaking_capacity", "label": "分断能力", "layer": "semantic", "dept": "mccb"},
            {"id": "mccb_frame_size", "label": "壳架等级", "layer": "semantic", "dept": "mccb"},
        ])
    elif d == "mcb":
        dims.extend([
            {"id": "mcb_pole_count", "label": "极数", "layer": "semantic", "dept": "mcb"},
        ])
        
    metrics = [
        {"id": "revenue", "label": "销售净收入 (元)", "agg": "sum", "showAs": "normal", "layer": "raw", "dept": "common"},
        {"id": "qty", "label": "总台数 (台)", "agg": "sum", "showAs": "normal", "layer": "raw", "dept": "common"},
        {"id": "benti_qty", "label": "本体台数 (台)", "agg": "sum", "showAs": "normal", "layer": "raw", "dept": "common"},
        {"id": "cost", "label": "产品成本 (元)", "agg": "sum", "showAs": "normal", "layer": "raw", "dept": "common"},
        {"id": "gross_profit", "label": "毛利额 (元)", "agg": "sum", "showAs": "normal", "layer": "raw", "dept": "common"},
        {"id": "gross_margin_rate", "label": "毛利率 (%)", "agg": "avg", "showAs": "normal", "layer": "semantic", "dept": "common"},
        {"id": "yoy_growth_rate", "label": "同比增长率 (%)", "agg": "avg", "showAs": "normal", "layer": "semantic", "dept": "common"},
        {"id": "mom_growth_rate", "label": "环比增长率 (%)", "agg": "avg", "showAs": "normal", "layer": "semantic", "dept": "common"},
        {"id": "replace_rate", "label": "替换率 (%)", "agg": "avg", "showAs": "normal", "layer": "semantic", "dept": "common"},
    ]
    
    return {
        "status": "success",
        "department": d,
        "dimensions": dims,
        "raw_headers": raw_headers,
        "metrics": metrics,
        "dim_label_map": DIM_LABEL_MAP,
    }


def get_cascading_options(
    target_dims: List[str],
    filters: Optional[Dict[str, Any]] = None,
    year: Optional[int] = 2026,
    product_class: Optional[str] = "acb",
    property_type: Optional[str] = "all",
    quarter: Optional[str] = "all",
    con: Any = None,
) -> Dict[str, List[str]]:
    """
    根据当前筛选上下文，返回指定 target_dims 的【有效可选项集合】(DISTINCT 结果)。
    遵循【剔除自身筛选 (Exclude Self)】逻辑：
    查询维度 X 的有效选项时，过滤条件自动排除维度 X 自身的已选条件。
    """
    if not target_dims:
        return {}

    filters = filters or {}
    result: Dict[str, List[str]] = {}

    close_con = False
    if con is None:
        try:
            from config import get_duckdb_path
            db_p = get_duckdb_path(product_class)
            if os.path.exists(db_p):
                con = duckdb.connect(db_p, read_only=True)
                close_con = True
        except Exception:
            con = None

    try:
        for target_dim in target_dims:
            if not target_dim:
                continue
            
            norm_target = CHINESE_COL_ALIAS.get(target_dim, target_dim)
            filtered_context = {
                k: v for k, v in filters.items()
                if CHINESE_COL_ALIAS.get(k, k) != norm_target
            }

            # 动态级联联动：
            # 1. 目标为 year 时不限制年份；
            # 2. 目标为 month 或 quarter 时，若 filtered_context 显式指定 year，或外层传入 year，按该年份精确约束
            if norm_target == "year":
                target_year = None
            else:
                explicit_yr = next((v for k, v in filtered_context.items() if CHINESE_COL_ALIAS.get(k, k) == "year"), None)
                target_year = explicit_yr if explicit_yr is not None else year

            translator = PivotSQLTranslator(
                row_dims=[norm_target],
                metrics=["qty"],
                year=target_year,
                product_class=product_class,
                property_type=property_type,
                quarter=quarter if norm_target != "quarter" else "all",
                include_subtotals=False,
                con=con,
                filters=filtered_context,
            )

            view_name = resolve_view_name(product_class, target_year or 2026, con)
            if con and view_name:
                try:
                    rows = con.execute(f"DESCRIBE {view_name}").fetchall()
                    translator.available_cols = {row[0] for row in rows}
                except Exception:
                    translator.available_cols = set()

            is_intl = "intl" in view_name.lower() or (product_class and product_class.lower() in ("intl", "overseas", "foreign", "海外", "国际"))
            dim_expr = translator._get_dim_expr(norm_target, is_intl)

            where_clauses = translator._build_where_clauses(is_intl)
            where_clauses.append(f"{dim_expr} IS NOT NULL")
            where_clauses.append(f"{dim_expr} != '未分配'")

            # 产品型号动态过滤：剔除噪声并严格进行品类边界保护，杜绝跨品类干扰
            if norm_target == "product_model":
                where_clauses.append(f"{dim_expr} NOT IN ('未分配', '常规型号', '未解构型号', '通用-其他类', '配套元器件类-零部件')")
                where_clauses.append(f"{dim_expr} NOT LIKE '主开关%'")
                dept_lower = (product_class or "acb").lower()
                if dept_lower == "acb":
                    where_clauses.append(f"({dim_expr} NOT LIKE 'NM%' AND {dim_expr} NOT LIKE 'NXM%' AND {dim_expr} NOT LIKE 'DZ%' AND {dim_expr} NOT LIKE 'Ex9M%' AND {dim_expr} NOT LIKE 'NXB%' AND {dim_expr} NOT LIKE 'NDM%' AND {dim_expr} NOT LIKE '%塑壳%')")
                elif dept_lower == "mccb":
                    where_clauses.append(f"({dim_expr} NOT LIKE 'NXA%' AND {dim_expr} NOT LIKE 'NA%' AND {dim_expr} NOT LIKE 'DW%' AND {dim_expr} NOT LIKE 'Ex9A%' AND {dim_expr} NOT LIKE 'NXB%' AND {dim_expr} NOT LIKE 'NDM%' AND {dim_expr} NOT LIKE '%框架%')")
                elif dept_lower == "mcb":
                    where_clauses.append(f"({dim_expr} NOT LIKE 'NXA%' AND {dim_expr} NOT LIKE 'NA%' AND {dim_expr} NOT LIKE 'DW%' AND {dim_expr} NOT LIKE 'NM%' AND {dim_expr} NOT LIKE 'NXM%')")

            where_str = f"WHERE {' AND '.join(where_clauses)}"

            sql = f"SELECT DISTINCT {dim_expr} AS val FROM {view_name} {where_str} ORDER BY val LIMIT 300"

            try:
                if con:
                    rows = con.execute(sql).fetchall()
                    vals = [str(r[0]) for r in rows if r[0] is not None and str(r[0]).strip() != ""]
                else:
                    vals = []
            except Exception:
                vals = []

            result[target_dim] = vals
    finally:
        if close_con and con:
            con.close()

    return result


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="CHINT DuckDB OLAP 透视查询引擎 (QueryEngine)")
    parser.add_argument("--rows", type=str, default="product_series", help="行维度 (逗号分隔)")
    parser.add_argument("--metrics", type=str, default="revenue,qty", help="指标 (逗号分隔)")
    parser.add_argument("--year", type=int, default=2026, help="年份")
    parser.add_argument("--dept", type=str, default="acb", help="部门/品类 (acb/mccb/mcb)")
    args = parser.parse_args()

    row_dims = [r.strip() for r in args.rows.split(",") if r.strip()]
    metrics = [m.strip() for m in args.metrics.split(",") if m.strip()]
    print(f"═══ 运行 DuckDB 透视查询 (维度: {row_dims}, 指标: {metrics}, 年份: {args.year}) ═══")
    
    from config import get_duckdb_path
    db_path = get_duckdb_path(args.dept)
    con = duckdb.connect(str(db_path), read_only=True)
    try:
        translator = PivotSQLTranslator(row_dims=row_dims, metrics=metrics, year=args.year, product_class=args.dept, con=con)
        sql, _ = translator.translate()
        print("生成的 SQL:\n", sql)
        df = con.execute(sql).fetchdf()
        print("\n查询结果 (前 10 行):")
        print(df.head(10).to_string(index=False))
    finally:
        con.close()



