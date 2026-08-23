"""
analyzer.py — 5 大维度分析器

为 PPT 第三部分每一张表提供独立的生成函数。
输出均为统一结构的 pandas DataFrame，输入到 visualizer.py 做渲染。
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from loader import (
    load_china, load_intl, load_china_prev, load_intl_prev,
    calc_yoy,
    _normalize_year_vec, _month_str_to_int_vec,
    load_general_sheet,
)
try:
    from config import (
        Col,
        PRODUCT_HIERARCHY_CN,
        PRODUCT_HIERARCHY_INTL,
        UNIT,
        month_str_to_int,
        INDUSTRY_PROFESSIONAL,
        OVERSEAS_TOP_COUNTRIES,
    )
except ImportError:
    from config import (
        Col,
        PRODUCT_HIERARCHY_CN,
        PRODUCT_HIERARCHY_INTL,
        UNIT,
        month_str_to_int,
        INDUSTRY_PROFESSIONAL,
        OVERSEAS_TOP_COUNTRIES,
    )


__all__ = [
    "overview_global",
    "overview_global_comprehensive",
    "get_monthly_region_trend",
    "add_brand_label",
    "sum_metric",
    "calc_yoy_pct",
    "brand_metrics",
    "region_metrics",
    "overseas_region_yoy",
    "product_china",
    "product_intl",
    "industry_region_china",
    "region_overseas",
    "margin_analysis",
    "load_all_for_ppt",
]


# ── 工具函数 ──────────────────────────────────────────────────

def _agg_group(
    df: pd.DataFrame,
    group_cols: list[str],
    value_col: int = Col.NET_INCOME,
) -> pd.DataFrame:
    """按维度分组聚合销售指标"""
    agg = df.groupby(group_cols, observed=True).agg(
        sales=pd.NamedAgg(column=value_col, aggfunc="sum"),
        qty=pd.NamedAgg(column=Col.INVOICE_QTY, aggfunc="sum"),
    ).reset_index()
    return agg


def _add_pct_fields(grp: pd.DataFrame, sales_col: str = "sales", qty_col: str = "qty") -> pd.DataFrame:
    """给 group DataFrame 添加占比字段
    sales_col / qty_col 指定聚合后销售额/销量列名（不同分析器命名可能不同）
    """
    total_sales = grp[sales_col].sum()
    total_qty = grp[qty_col].sum()
    grp["sales_share"] = (grp[sales_col] / total_sales * 100).round(1) if total_sales else 0.0
    grp["qty_share"] = (grp[qty_col] / total_qty * 100).round(1) if total_qty else 0.0
    return grp


def _month_filter(df: pd.DataFrame, month: int) -> pd.DataFrame:
    """过滤单月数据（向量化版本）"""
    m_vec = _month_str_to_int_vec(df[Col.MONTH])
    mask = m_vec == month
    return df[mask].copy()


# ── 1. 全球总览 (3.1) ────────────────────────────────────────

# ════════════════════════════════════════════════════════════════
# T01 共享 helper —— 方案A「单一事实源」基石
# 所有金额 / 数量 / 同比指标统一经此处计算，杜绝多头口径
# ════════════════════════════════════════════════════════════════

def add_brand_label(df: pd.DataFrame | None) -> None:
    """原地给 DataFrame 添加 `brand` 列（'正泰' / '诺雅克'）。

    判定规则：使用 str.contains('诺雅克') 检查 BRAND_SRC (或 '产业')、REPORT_SOURCE 或 PLATFORM 字段。
    含「诺雅克」→ 诺雅克，否则正泰。
    df 为 None 或空时安全赋空 Series，不抛错。
    """
    if df is None:
        return
    if len(df) > 0:
        if Col.BRAND_SRC in df.columns:
            brand_src = df[Col.BRAND_SRC].astype(str)
        elif "产业" in df.columns:
            brand_src = df["产业"].astype(str)
        elif "brand_sector" in df.columns:
            brand_src = df["brand_sector"].astype(str)
        else:
            brand_src = pd.Series("", index=df.index)

        source = df[Col.REPORT_SOURCE].astype(str) if Col.REPORT_SOURCE in df.columns else (df["报表来源"].astype(str) if "报表来源" in df.columns else pd.Series("", index=df.index))
        
        is_noark = brand_src.str.contains('诺雅克') | source.str.contains('诺雅克')
        df['brand'] = np.where(is_noark, '诺雅克', '正泰')
    else:
        df['brand'] = pd.Series(dtype=str)


def sum_metric(df: pd.DataFrame | None, col: int = Col.NET_INCOME) -> float:
    """明细求和唯一入口：金额(NET_INCOME) / 数量(INVOICE_QTY)。

    None / 空 DataFrame / 列缺失 → 0.0。返回原始元 / 台（不换算单位）。
    使用 float64 累加器，避免 float32 深度累加大数精度丢失。
    """
    if df is None or len(df) == 0:
        return 0.0
    if col not in df.columns:
        return 0.0
    try:
        return float(df[col].astype(np.float64).sum())
    except (TypeError, ValueError):
        return 0.0


def calc_yoy_pct(curr: float | None, prev: float | None) -> float | None:
    """统一同比百分数：(curr - prev) / |prev| × 100。

    prev 无效 / ≤ 0 → None（前端渲染为「-」）。
    """
    if curr is None or prev is None:
        return None
    if prev <= 0:
        return None
    return (curr - prev) / prev * 100.0


def brand_metrics(
    df_cn: pd.DataFrame | None,
    df_intl: pd.DataFrame | None,
    df_cn_prev: pd.DataFrame | None,
    df_intl_prev: pd.DataFrame | None,
    brand: str,
    global_sales: float,
    global_qty: float,
) -> dict:
    """品牌汇总指标（中国区 + 海外区全量数据）。

    返回结构：{sales(元), qty(台), yoy_sales(%), yoy_qty(%), share_sales(%), share_qty(%)}
    """
    sales_cn = sum_metric(df_cn[df_cn['brand'] == brand], Col.NET_INCOME) if (df_cn is not None and 'brand' in df_cn.columns) else 0.0
    sales_intl = sum_metric(df_intl[df_intl['brand'] == brand], Col.NET_INCOME) if (df_intl is not None and 'brand' in df_intl.columns) else 0.0
    sales_curr = sales_cn + sales_intl

    qty_cn = sum_metric(df_cn[df_cn['brand'] == brand], Col.INVOICE_QTY) if (df_cn is not None and 'brand' in df_cn.columns) else 0.0
    qty_intl = sum_metric(df_intl[df_intl['brand'] == brand], Col.INVOICE_QTY) if (df_intl is not None and 'brand' in df_intl.columns) else 0.0
    qty_curr = qty_cn + qty_intl

    sales_cn_prev = sum_metric(df_cn_prev[df_cn_prev['brand'] == brand], Col.NET_INCOME) if (df_cn_prev is not None and 'brand' in df_cn_prev.columns) else 0.0
    sales_intl_prev = sum_metric(df_intl_prev[df_intl_prev['brand'] == brand], Col.NET_INCOME) if (df_intl_prev is not None and 'brand' in df_intl_prev.columns) else 0.0
    sales_prev = sales_cn_prev + sales_intl_prev

    qty_cn_prev = sum_metric(df_cn_prev[df_cn_prev['brand'] == brand], Col.INVOICE_QTY) if (df_cn_prev is not None and 'brand' in df_cn_prev.columns) else 0.0
    qty_intl_prev = sum_metric(df_intl_prev[df_intl_prev['brand'] == brand], Col.INVOICE_QTY) if (df_intl_prev is not None and 'brand' in df_intl_prev.columns) else 0.0
    qty_prev = qty_cn_prev + qty_intl_prev

    yoy_sales = calc_yoy_pct(sales_curr, sales_prev)
    yoy_qty = calc_yoy_pct(qty_curr, qty_prev)
    share_sales = sales_curr / global_sales * 100.0 if (global_sales and global_sales > 0) else 0.0
    share_qty = qty_curr / global_qty * 100.0 if (global_qty and global_qty > 0) else 0.0

    return {
        "sales": float(sales_curr),
        "qty": float(qty_curr),
        "yoy_sales": round(yoy_sales, 1) if yoy_sales is not None else None,
        "yoy_qty": round(yoy_qty, 1) if yoy_qty is not None else None,
        "share_sales": round(share_sales, 1),
        "share_qty": round(share_qty, 1),
    }


def region_metrics(
    df_cn: pd.DataFrame | None,
    df_intl: pd.DataFrame | None,
    df_cn_prev: pd.DataFrame | None,
    df_intl_prev: pd.DataFrame | None,
    region: str,
    global_sales: float,
    global_qty: float,
) -> dict:
    """单个区域的销售额 / 数量 / 同比 / 占比。

    region == "中国区" 取 df_cn；否则取 df_intl[REGION == region]。
    返回结构同 brand_metrics（金额=元、数量=台、yoy=百分数、share=百分数）。
    """
    if region == "中国区":
        src_curr, src_prev = df_cn, df_cn_prev
    else:
        src_curr = df_intl[df_intl[Col.REGION] == region] if df_intl is not None else None
        src_prev = df_intl_prev[df_intl_prev[Col.REGION] == region] if df_intl_prev is not None else None

    sales_curr = sum_metric(src_curr, Col.NET_INCOME)
    qty_curr = sum_metric(src_curr, Col.INVOICE_QTY)
    sales_prev = sum_metric(src_prev, Col.NET_INCOME)
    qty_prev = sum_metric(src_prev, Col.INVOICE_QTY)

    yoy_sales = calc_yoy_pct(sales_curr, sales_prev)
    yoy_qty = calc_yoy_pct(qty_curr, qty_prev)
    share_sales = sales_curr / global_sales * 100.0 if (global_sales and global_sales > 0) else 0.0
    share_qty = qty_curr / global_qty * 100.0 if (global_qty and global_qty > 0) else 0.0

    return {
        "sales": float(sales_curr),
        "qty": float(qty_curr),
        "yoy_sales": round(yoy_sales, 1) if yoy_sales is not None else None,
        "yoy_qty": round(yoy_qty, 1) if yoy_qty is not None else None,
        "share_sales": round(share_sales, 1),
        "share_qty": round(share_qty, 1),
    }


def overseas_region_yoy(
    df_intl: pd.DataFrame | None,
    df_intl_prev: pd.DataFrame | None,
    region: str,
    month: int,
) -> tuple[float, float | None]:
    """图二月度趋势用：返回 (当期销售额元, 同比百分数|None) 针对单个洲区单月。"""
    sales = 0.0
    if df_intl is not None and len(df_intl) > 0:
        sub = df_intl[df_intl[Col.REGION] == region]
        if len(sub) > 0:
            m_vec = _month_str_to_int_vec(sub[Col.MONTH])
            sub_m = sub[m_vec == month]
            sales = float(sub_m[Col.NET_INCOME].sum()) if len(sub_m) > 0 else 0.0

    prev = None
    if df_intl_prev is not None and len(df_intl_prev) > 0:
        sub_p = df_intl_prev[df_intl_prev[Col.REGION] == region]
        if len(sub_p) > 0:
            m_vec_p = _month_str_to_int_vec(sub_p[Col.MONTH])
            sub_pm = sub_p[m_vec_p == month]
            if len(sub_pm) > 0:
                prev = float(sub_pm[Col.NET_INCOME].sum())

    yoy = calc_yoy_pct(sales, prev)
    return sales, yoy


def overview_global(
    excel_path: str,
    year: int = 2026,
    months: list[int] | None = None,
    prev_year: int = 2025,
) -> dict[str, dict]:
    """
    返回 dict，结构：
    {
        "global":  {"sales": float, "qty": float, "yoy_sales": float, "yoy_qty": float},
        "china":   {同上, "share_sales": float, "share_qty": float},
        "intl":    {同上, "share_sales": float, "share_qty": float},
        "chint":   {同上},
        "noark":   {同上},
        "regions": {region_name: {sales, qty, yoy_sales, yoy_qty, share_sales, share_qty}},
        "overseas_total": {同上}
    }
    """
    df_cn = load_china(excel_path, year, months)
    df_intl = load_intl(excel_path, year, months)
    df_cn_prev = load_china_prev(excel_path, prev_year, months) if prev_year else None
    df_intl_prev = load_intl_prev(excel_path, prev_year, months) if prev_year else None

    # 品牌识别（统一 T01 helper）
    add_brand_label(df_cn)
    add_brand_label(df_intl)
    add_brand_label(df_cn_prev)
    add_brand_label(df_intl_prev)

    # Global summaries（明细求和，单一事实源）
    cn_sales = sum_metric(df_cn, Col.NET_INCOME)
    intl_sales = sum_metric(df_intl, Col.NET_INCOME)
    global_sales = cn_sales + intl_sales

    cn_qty = sum_metric(df_cn, Col.INVOICE_QTY)
    intl_qty = sum_metric(df_intl, Col.INVOICE_QTY)
    global_qty = cn_qty + intl_qty

    cn_sales_prev = sum_metric(df_cn_prev, Col.NET_INCOME)
    intl_sales_prev = sum_metric(df_intl_prev, Col.NET_INCOME)
    global_sales_prev = cn_sales_prev + intl_sales_prev
    cn_qty_prev = sum_metric(df_cn_prev, Col.INVOICE_QTY)
    intl_qty_prev = sum_metric(df_intl_prev, Col.INVOICE_QTY)
    global_qty_prev = cn_qty_prev + intl_qty_prev

    # YoY calculations（统一 T01 calc_yoy_pct）
    yoy_cn_sales = calc_yoy_pct(cn_sales, cn_sales_prev)
    yoy_intl_sales = calc_yoy_pct(intl_sales, intl_sales_prev)
    yoy_global_sales = calc_yoy_pct(global_sales, global_sales_prev)
    yoy_cn_qty = calc_yoy_pct(cn_qty, cn_qty_prev)
    yoy_intl_qty = calc_yoy_pct(intl_qty, intl_qty_prev)
    yoy_global_qty = calc_yoy_pct(global_qty, global_qty_prev)

    # Brand values（统一复用 brand_metrics）
    chint_metrics = brand_metrics(df_cn, df_intl, df_cn_prev, df_intl_prev, "正泰", global_sales, global_qty)
    noark_metrics = brand_metrics(df_cn, df_intl, df_cn_prev, df_intl_prev, "诺雅克", global_sales, global_qty)

    # Region values（复用 T01 region_metrics 统一口径）
    regions = ["中国区", "欧洲区", "亚太区", "西亚非洲区", "北美区", "拉美洲区"]
    regions_metrics = {r: region_metrics(df_cn, df_intl, df_cn_prev, df_intl_prev, r, global_sales, global_qty) for r in regions}

    # Overseas Total Box
    overseas_sales_curr = intl_sales
    overseas_sales_prev = intl_sales_prev
    overseas_qty_curr = intl_qty
    overseas_qty_prev = intl_qty_prev
    
    overseas_sales_yoy = (overseas_sales_curr - overseas_sales_prev) / overseas_sales_prev * 100 if overseas_sales_prev > 0 else None
    overseas_qty_yoy = (overseas_qty_curr - overseas_qty_prev) / overseas_qty_prev * 100 if overseas_qty_prev > 0 else None

    overseas_total = {
        "sales": round(overseas_sales_curr * UNIT.amt_to_wan_factor, 1),
        "qty": round(overseas_qty_curr * UNIT.qty_to_wantai_factor, 1),
        "yoy_sales": round(overseas_sales_yoy, 1) if overseas_sales_yoy is not None else None,
        "yoy_qty": round(overseas_qty_yoy, 1) if overseas_qty_yoy is not None else None,
        "share_sales": round(overseas_sales_curr / global_sales * 100, 1) if global_sales > 0 else 0.0,
        "share_qty": round(overseas_qty_curr / global_qty * 100, 1) if global_qty > 0 else 0.0,
    }

    result = {
        "global": {
            "sales": round(global_sales * UNIT.amt_to_wan_factor, 1),
            "qty": round(global_qty * UNIT.qty_to_wantai_factor, 1),
            "yoy_sales": round(yoy_global_sales, 1) if yoy_global_sales is not None else None,
            "yoy_qty": round(yoy_global_qty, 1) if yoy_global_qty is not None else None,
        },
        "china": {
            "sales": round(cn_sales * UNIT.amt_to_wan_factor, 1),
            "qty": round(cn_qty * UNIT.qty_to_wantai_factor, 1),
            "yoy_sales": round(yoy_cn_sales, 1) if yoy_cn_sales is not None else None,
            "yoy_qty": round(yoy_cn_qty, 1) if yoy_cn_qty is not None else None,
            "share_sales": round(cn_sales / global_sales * 100, 1) if global_sales > 0 else 0.0,
            "share_qty": round(cn_qty / global_qty * 100, 1) if global_qty > 0 else 0.0,
        },
        "intl": {
            "sales": round(intl_sales * UNIT.amt_to_wan_factor, 1),
            "qty": round(intl_qty * UNIT.qty_to_wantai_factor, 1),
            "yoy_sales": round(yoy_intl_sales, 1) if yoy_intl_sales is not None else None,
            "yoy_qty": round(yoy_intl_qty, 1) if yoy_intl_qty is not None else None,
            "share_sales": round(intl_sales / global_sales * 100, 1) if global_sales > 0 else 0.0,
            "share_qty": round(intl_qty / global_qty * 100, 1) if global_qty > 0 else 0.0,
        },
        "chint": chint_metrics,
        "noark": noark_metrics,
        "regions": regions_metrics,
        "overseas_total": overseas_total,
    }

    return result


def get_monthly_region_trend(
    excel_path: str,
    year: int = 2026,
    months: list[int] | None = None,
    prev_year: int = 2025,
) -> pd.DataFrame:
    """计算月度各洲区销售数据，用于生成双轴图（图二）。

    方案A：强制明细计算（删除汇总表优先分支），仅从 df_intl 按 REGION+MONTH 聚合求和。
    """
    months = months or [1, 2, 3]

    # 明细计算路径（单一事实源）
    df_cn = load_china(excel_path, year, months)
    df_intl = load_intl(excel_path, year, months)
    df_cn_prev = load_china_prev(excel_path, prev_year, months) if prev_year else None
    df_intl_prev = load_intl_prev(excel_path, prev_year, months) if prev_year else None

    # 向量化添加月份列
    cn_months = _month_str_to_int_vec(df_cn[Col.MONTH]) if len(df_cn) > 0 else pd.Series(dtype='Int8')
    intl_months = _month_str_to_int_vec(df_intl[Col.MONTH]) if len(df_intl) > 0 else pd.Series(dtype='Int8')

    records = []
    for m in months:
        row = {"month_str": f"{m}月"}

        # 当期：用向量化月份过滤
        cn_m = df_cn[cn_months == m] if len(df_cn) > 0 else df_cn

        # 各大区销售额（当期）：复用 T01 overseas_region_yoy 明细聚合
        row["中国区"] = cn_m[Col.NET_INCOME].sum() * UNIT.amt_to_wan_factor if len(cn_m) > 0 else 0.0
        row["欧洲区"] = overseas_region_yoy(df_intl, df_intl_prev, "欧洲区", m)[0] * UNIT.amt_to_wan_factor
        row["亚太区"] = overseas_region_yoy(df_intl, df_intl_prev, "亚太区", m)[0] * UNIT.amt_to_wan_factor
        row["西亚非洲区"] = overseas_region_yoy(df_intl, df_intl_prev, "西亚非洲区", m)[0] * UNIT.amt_to_wan_factor
        row["北美区"] = overseas_region_yoy(df_intl, df_intl_prev, "北美区", m)[0] * UNIT.amt_to_wan_factor
        row["拉美洲区"] = overseas_region_yoy(df_intl, df_intl_prev, "拉美洲区", m)[0] * UNIT.amt_to_wan_factor

        row["海外总计"] = row["欧洲区"] + row["亚太区"] + row["西亚非洲区"] + row["北美区"] + row["拉美洲区"]
        row["总计"] = row["中国区"] + row["海外总计"]

        # 上年同期：用向量化月份过滤
        if df_cn_prev is not None and len(df_cn_prev) > 0:
            cn_prev_months = _month_str_to_int_vec(df_cn_prev[Col.MONTH])
            cn_p = df_cn_prev[cn_prev_months == m][Col.NET_INCOME].sum() * UNIT.amt_to_wan_factor
        else:
            cn_p = 0.0

        if df_intl_prev is not None and len(df_intl_prev) > 0:
            intl_prev_months = _month_str_to_int_vec(df_intl_prev[Col.MONTH])
            intl_p_df = df_intl_prev[intl_prev_months == m]
            overseas_p = intl_p_df[Col.NET_INCOME].sum() * UNIT.amt_to_wan_factor if len(intl_p_df) > 0 else 0.0
        else:
            overseas_p = 0.0

        total_p = cn_p + overseas_p

        row["China_YoY"] = (row["中国区"] - cn_p) / cn_p * 100 if cn_p > 0 else None
        row["Overseas_YoY"] = (row["海外总计"] - overseas_p) / overseas_p * 100 if overseas_p > 0 else None
        row["Total_YoY"] = (row["总计"] - total_p) / total_p * 100 if total_p > 0 else None

        records.append(row)

    return pd.DataFrame(records)


# ── 2. 中国区 分产品 (3.2) ────────────────────────────────────

def product_china(
    excel_path: str,
    year: int = 2026,
    months: list[int] | None = None,
    prev_year: int = 2025,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    返回 (指标表, 摘要表)
    指标表列：platform, series, sales_monthly, sales_ytd, qty_monthly, qty_ytd, 同比, 占比
    摘要表：异常洞察汇总（暂时占位，后期可由外部导入）
    """
    df = load_china(excel_path, year, months)
    df_prev = load_china_prev(excel_path, prev_year, months)

    # 按平台+系列聚合
    grp = df.groupby([Col.PLATFORM, Col.SERIES], observed=False).agg(
        sales_ytd=pd.NamedAgg(column=Col.NET_INCOME, aggfunc="sum"),
        qty_ytd=pd.NamedAgg(column=Col.INVOICE_QTY, aggfunc="sum"),
    ).reset_index()

    # 同期同比
    if df_prev is not None:
        p_grp = df_prev.groupby([Col.PLATFORM, Col.SERIES], observed=False).agg(
            sales_prev=pd.NamedAgg(column=Col.NET_INCOME, aggfunc="sum"),
            qty_prev=pd.NamedAgg(column=Col.INVOICE_QTY, aggfunc="sum"),
        ).reset_index()
        grp = grp.merge(p_grp, on=[Col.PLATFORM, Col.SERIES], how="left")
        grp["sales_yoy"] = calc_yoy(grp["sales_ytd"], grp["sales_prev"])
        grp["qty_yoy"] = calc_yoy(grp["qty_ytd"], grp["qty_prev"])
    else:
        grp["sales_yoy"] = np.nan
        grp["qty_yoy"] = np.nan

    # 贴 PPT 展现层级标签
    grp["_label_cn"] = grp.apply(
        lambda r: f"{r[Col.PLATFORM]} → {r[Col.SERIES]}"
        if r[Col.SERIES] not in ("汇总", "") else str(r[Col.PLATFORM]),
        axis=1,
    )

    grp = _add_pct_fields(grp, sales_col="sales_ytd", qty_col="qty_ytd")
    grp["sales_ytd"] = (grp["sales_ytd"] * UNIT.amt_to_wan_factor).round(1)
    grp["qty_ytd"] = (grp["qty_ytd"] * UNIT.qty_to_wantai_factor).round(1)
    grp["sales_yoy"] = (grp["sales_yoy"] * 100).round(1)
    grp["qty_yoy"] = (grp["qty_yoy"] * 100).round(1)

    grp.sort_values([Col.PLATFORM, Col.SERIES], inplace=True)

    # 摘要表（空壳，后续可对接 AI 分析或手动录入）
    summary = pd.DataFrame(columns=["异常洞察", "原因分析", "行动计划", "责任人", "完成时间"])

    return grp, summary


# ── 3. 海外 分产品 (3.2) ─────────────────────────────────────

def product_intl(
    excel_path: str,
    year: int = 2026,
    months: list[int] | None = None,
    prev_year: int = 2025,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """同 product_china，但数据源为国际 sheet"""
    df = load_intl(excel_path, year, months)
    df_prev = load_intl_prev(excel_path, prev_year, months)

    grp = df.groupby([Col.PLATFORM, Col.SERIES], observed=False).agg(
        sales_ytd=pd.NamedAgg(column=Col.NET_INCOME, aggfunc="sum"),
        qty_ytd=pd.NamedAgg(column=Col.INVOICE_QTY, aggfunc="sum"),
    ).reset_index()

    if df_prev is not None:
        p_grp = df_prev.groupby([Col.PLATFORM, Col.SERIES], observed=False).agg(
            sales_prev=pd.NamedAgg(column=Col.NET_INCOME, aggfunc="sum"),
            qty_prev=pd.NamedAgg(column=Col.INVOICE_QTY, aggfunc="sum"),
        ).reset_index()
        grp = grp.merge(p_grp, on=[Col.PLATFORM, Col.SERIES], how="left")
        grp["sales_yoy"] = calc_yoy(grp["sales_ytd"], grp["sales_prev"])
        grp["qty_yoy"] = calc_yoy(grp["qty_ytd"], grp["qty_prev"])
    else:
        grp["sales_yoy"] = np.nan
        grp["qty_yoy"] = np.nan

    grp = _add_pct_fields(grp, sales_col="sales_ytd", qty_col="qty_ytd")
    grp["sales_ytd"] = (grp["sales_ytd"] * UNIT.amt_to_wan_factor).round(1)
    grp["qty_ytd"] = (grp["qty_ytd"] * UNIT.qty_to_wantai_factor).round(1)
    grp["sales_yoy"] = (grp["sales_yoy"] * 100).round(1)
    grp["qty_yoy"] = (grp["qty_yoy"] * 100).round(1)

    grp.sort_values([Col.PLATFORM, Col.SERIES], inplace=True)

    summary = pd.DataFrame(columns=["异常洞察", "原因分析", "行动计划", "责任人", "完成时间"])
    return grp, summary


# ── 4. 中国区 分行业/区域 (3.3) ──────────────────────────────

def industry_region_china(
    excel_path: str,
    year: int = 2026,
    months: list[int] | None = None,
    prev_year: int = 2025,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    返回 (行业表, 行业摘要表, 区域表, 区域摘要表)

    行业表按 销售团队（Col.SALES_TEAM）聚合
    区域表按 省份（Col.PROVINCE）聚合
    """
    df = load_china(excel_path, year, months)

    # ── 分行业 ──
    ind = df.groupby(Col.SALES_TEAM_REVISION, observed=False).agg(
        sales_ytd=pd.NamedAgg(column=Col.NET_INCOME, aggfunc="sum"),
        qty_ytd=pd.NamedAgg(column=Col.INVOICE_QTY, aggfunc="sum"),
    ).reset_index()
    ind = _add_pct_fields(ind, sales_col="sales_ytd", qty_col="qty_ytd")
    ind["sales_ytd"] = (ind["sales_ytd"] * UNIT.amt_to_wan_factor).round(1)
    ind["qty_ytd"] = (ind["qty_ytd"] * UNIT.qty_to_wantai_factor).round(1)
    ind.rename(columns={Col.SALES_TEAM_REVISION: "销售团队"}, inplace=True)

    if prev_year:
        df_prev = load_china_prev(excel_path, prev_year, months)
        p_ind = df_prev.groupby(Col.SALES_TEAM_REVISION, observed=False).agg(
            sales_prev=pd.NamedAgg(column=Col.NET_INCOME, aggfunc="sum"),
        ).reset_index()
        ind = ind.merge(p_ind, left_on="销售团队", right_on=Col.SALES_TEAM_REVISION, how="left")
        ind["sales_yoy"] = (calc_yoy(
            ind["sales_ytd"] / UNIT.amt_to_wan_factor,
            ind["sales_prev"],
        ) * 100).round(1)
        ind.drop(columns=[Col.SALES_TEAM_REVISION, "sales_prev"], inplace=True, errors="ignore")

    ind_summary = pd.DataFrame(columns=["异常洞察", "原因分析", "行动计划", "责任人", "完成时间"])

    # ── 分区域 ──
    reg = df.groupby(Col.PROVINCE, observed=False).agg(
        sales_ytd=pd.NamedAgg(column=Col.NET_INCOME, aggfunc="sum"),
        qty_ytd=pd.NamedAgg(column=Col.INVOICE_QTY, aggfunc="sum"),
    ).reset_index()
    reg = _add_pct_fields(reg, sales_col="sales_ytd", qty_col="qty_ytd")
    reg["sales_ytd"] = (reg["sales_ytd"] * UNIT.amt_to_wan_factor).round(1)
    reg["qty_ytd"] = (reg["qty_ytd"] * UNIT.qty_to_wantai_factor).round(1)
    reg.rename(columns={Col.PROVINCE: "区域"}, inplace=True)
    reg.sort_values("sales_ytd", ascending=False, inplace=True)

    reg_summary = pd.DataFrame(columns=["异常洞察", "原因分析", "行动计划", "责任人", "完成时间"])

    return ind, ind_summary, reg, reg_summary


# ── 5. 海外 分区域 (3.3) ─────────────────────────────────────

def region_overseas(
    excel_path: str,
    year: int = 2026,
    months: list[int] | None = None,
    prev_year: int = 2025,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    返回 (洲区表, 洲区摘要表, 国家表, 国家摘要表)
    """
    df = load_intl(excel_path, year, months)

    # ── 洲区 ──
    rs = df.groupby(Col.REGION, observed=False).agg(
        sales_ytd=pd.NamedAgg(column=Col.NET_INCOME, aggfunc="sum"),
        qty_ytd=pd.NamedAgg(column=Col.INVOICE_QTY, aggfunc="sum"),
    ).reset_index()
    rs = _add_pct_fields(rs, sales_col="sales_ytd", qty_col="qty_ytd")
    rs["sales_ytd"] = (rs["sales_ytd"] * UNIT.amt_to_wan_factor).round(1)
    rs["qty_ytd"] = (rs["qty_ytd"] * UNIT.qty_to_wantai_factor).round(1)
    rs.rename(columns={Col.REGION: "洲区"}, inplace=True)

    if prev_year:
        df_prev = load_intl_prev(excel_path, prev_year, months)
        p_rs = df_prev.groupby(Col.REGION, observed=False).agg(
            sales_prev=pd.NamedAgg(column=Col.NET_INCOME, aggfunc="sum"),
        ).reset_index()
        rs = rs.merge(p_rs, left_on="洲区", right_on=Col.REGION, how="left")
        rs["sales_yoy"] = (calc_yoy(
            rs["sales_ytd"] / UNIT.amt_to_wan_factor,
            rs["sales_prev"],
        ) * 100).round(1)
        rs.drop(columns=[Col.REGION, "sales_prev"], inplace=True, errors="ignore")

    rs_summary = pd.DataFrame(columns=["异常洞察", "原因分析", "行动计划", "责任人", "完成时间"])

    # ── 国家 ──
    ctry = df.groupby(Col.COUNTRY_NAME, observed=False).agg(
        sales_ytd=pd.NamedAgg(column=Col.NET_INCOME, aggfunc="sum"),
        qty_ytd=pd.NamedAgg(column=Col.INVOICE_QTY, aggfunc="sum"),
    ).reset_index()
    ctry = _add_pct_fields(ctry, sales_col="sales_ytd", qty_col="qty_ytd")
    ctry["sales_ytd"] = (ctry["sales_ytd"] * UNIT.amt_to_wan_factor).round(1)
    ctry["qty_ytd"] = (ctry["qty_ytd"] * UNIT.qty_to_wantai_factor).round(1)
    ctry.rename(columns={Col.COUNTRY_NAME: "国家"}, inplace=True)
    ctry.sort_values("sales_ytd", ascending=False, inplace=True)

    ctry_summary = pd.DataFrame(columns=["异常洞察", "原因分析", "行动计划", "责任人", "完成时间"])

    return rs, rs_summary, ctry, ctry_summary


# ── 6. 产品毛利分析 (3.5) ────────────────────────────────────

def margin_analysis(
    excel_path: str,
    year: int = 2026,
    months: list[int] | None = None,
    prev_year: int = 2025,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    按 产品系列 聚合毛利数据

    返回 (毛利指标表, 毛利摘要表)
    """
    df = load_china(excel_path, year, months)
    df_prev = load_china_prev(excel_path, prev_year, months)

    grp = df.groupby([Col.PLATFORM, Col.SERIES], observed=False).agg(
        sales=pd.NamedAgg(column=Col.NET_INCOME, aggfunc="sum"),
        cost=pd.NamedAgg(column=Col.TOTAL_COST, aggfunc="sum"),
        gm=pd.NamedAgg(column=Col.GROSS_MARGIN, aggfunc="sum"),
        dp=pd.NamedAgg(column=Col.PRODUCT_COST, aggfunc="mean"),
    ).reset_index()

    # 毛利率（YTD）
    grp["margin_ytd"] = (grp["gm"] / grp["sales"].replace(0, np.nan) * 100).round(1)

    # 上年毛利率
    if df_prev is not None:
        p_grp = df_prev.groupby([Col.PLATFORM, Col.SERIES], observed=False).agg(
            sales_p=pd.NamedAgg(column=Col.NET_INCOME, aggfunc="sum"),
            gm_p=pd.NamedAgg(column=Col.GROSS_MARGIN, aggfunc="sum"),
        ).reset_index()
        grp = grp.merge(p_grp, on=[Col.PLATFORM, Col.SERIES], how="left")
        grp["margin_prev"] = (grp["gm_p"] / grp["sales_p"].replace(0, np.nan) * 100).round(1)
    else:
        grp["margin_prev"] = np.nan

    grp["sales"] = (grp["sales"] * UNIT.amt_to_wan_factor).round(1)
    grp.sort_values([Col.PLATFORM, Col.SERIES], inplace=True)

    summary = pd.DataFrame(columns=["异常洞察", "原因分析", "行动计划", "责任人", "完成时间"])

    return grp, summary


# ── Comprehensive Analytics for PPTX Generation ──

def load_overview_from_total_sheet(
    excel_path: str,
    year: int = 2026,
    months: list[int] | None = None,
) -> dict:
    """从主配电-总数据工作表直接抓取全球大盘指标。"""
    try:
        df = load_general_sheet(excel_path, "主配电-总数据")
    except Exception as e:
        print(f"[WARN] 无法加载'主配电-总数据': {e}，将回退到原始明细计算。")
        return {}

    def get_val(region_name, target_year, is_yoy=False):
        start_row = None
        for r in range(len(df)):
            if str(df.iloc[r, 0]).strip() == region_name:
                start_row = r
                break
        if start_row is None:
            return None

        if not is_yoy:
            offset = {2024: 0, 2025: 1, 2026: 2}.get(target_year)
        else:
            offset = {2025: 3, 2026: 4}.get(target_year)

        if offset is None:
            return None

        row = start_row + offset
        last_m = months[-1] if months else 3
        col = 17 + last_m  # YTD列偏移（1月对应18，12月对应29，中间有空列17）
        if col < len(df.columns):
            val = df.iloc[row, col]
            if pd.isna(val) or str(val).strip() in ("-", ""):
                return None
            raw_val = float(val)
            if is_yoy:
                return raw_val * 100.0  # 增长率在Excel中是小数，转为百分数
            else:
                return raw_val / UNIT.amt_to_wan_factor  # 销售额在Excel中是万元，转为原始值
        return None

    res = {}
    res["global_sales"] = get_val("全球合计", year, is_yoy=False)
    res["cn_sales"] = get_val("中国区", year, is_yoy=False)
    res["yoy_cn_sales"] = get_val("中国区", year, is_yoy=True)
    res["intl_sales"] = get_val("海外洲区", year, is_yoy=False)
    res["yoy_intl_sales"] = get_val("海外洲区", year, is_yoy=True)

    if any(v is None for v in res.values()):
        return {}
    return res


def get_monthly_region_trend_from_sheet(
    excel_path: str,
    year: int = 2026,
    months: list[int] | None = None,
) -> pd.DataFrame | None:
    """从主配电-总数据中抓取各洲区月度销售额及增长率趋势。"""
    try:
        df = load_general_sheet(excel_path, "主配电-总数据")
    except Exception as e:
        print(f"[WARN] 无法加载'主配电-总数据': {e}，将回退到原始明细计算。")
        return None

    months = months or [1, 2, 3]
    records = []

    region_rows = {}
    for r in range(len(df)):
        val = str(df.iloc[r, 0]).strip()
        if val in ("中国区", "西亚非洲区", "拉美洲区", "亚太区", "欧洲区", "北美区", "海外洲区", "全球合计"):
            region_rows[val] = r

    required_regions = ["中国区", "西亚非洲区", "拉美洲区", "亚太区", "欧洲区", "北美区", "海外洲区", "全球合计"]
    if not all(r in region_rows for r in required_regions):
        return None

    for m in months:
        col_idx = 4 + m  # Col 5 is 1月

        row = {"month_str": f"{m}月"}
        row["中国区"] = float(df.iloc[region_rows["中国区"] + 2, col_idx])
        row["欧洲区"] = float(df.iloc[region_rows["欧洲区"] + 2, col_idx])
        row["亚太区"] = float(df.iloc[region_rows["亚太区"] + 2, col_idx])
        row["西亚非洲区"] = float(df.iloc[region_rows["西亚非洲区"] + 2, col_idx])
        row["北美区"] = float(df.iloc[region_rows["北美区"] + 2, col_idx])
        row["拉美洲区"] = float(df.iloc[region_rows["拉美洲区"] + 2, col_idx])

        row["海外总计"] = row["欧洲区"] + row["亚太区"] + row["西亚非洲区"] + row["北美区"] + row["拉美洲区"]
        row["总计"] = row["中国区"] + row["海外总计"]

        def get_yoy_val(r_idx):
            val = df.iloc[r_idx + 4, col_idx]
            if pd.isna(val) or str(val).strip() in ("-", ""):
                return 0.0
            return float(val) * 100.0

        row["China_YoY"] = get_yoy_val(region_rows["中国区"])
        row["Overseas_YoY"] = get_yoy_val(region_rows["海外洲区"])
        row["Total_YoY"] = get_yoy_val(region_rows["全球合计"])

        records.append(row)

    return pd.DataFrame(records)


def load_all_for_ppt(
    excel_path: str,
    year: int = 2026,
    months: list[int] | None = None,
    prev_year: int = 2025,
) -> dict:
    """一次性加载 PPT 生成所需的全部 DataFrame。

    将 5 个 comprehensive 函数各自调用 4 次 load（共 20 次）
    合并为 8 次 load（且有缓存命中），大幅减少重复加载开销。

    Returns
    -------
    dict : 包含 16 个 DataFrame 的字典
        cn_ytd, cn_prev_ytd, cn_month, cn_prev_month,
        intl_ytd, intl_prev_ytd, intl_month, intl_prev_month,
        和各自带 _all_qty 后缀的版本（不加本体过滤）
    """
    last_m = months[-1] if months else 3
    return {
        'cn_ytd': load_china(excel_path, year, months),
        'cn_prev_ytd': load_china_prev(excel_path, prev_year, months),
        'cn_month': load_china(excel_path, year, [last_m]),
        'cn_prev_month': load_china_prev(excel_path, prev_year, [last_m]),
        'intl_ytd': load_intl(excel_path, year, months),
        'intl_prev_ytd': load_intl_prev(excel_path, prev_year, months),
        'intl_month': load_intl(excel_path, year, [last_m]),
        'intl_prev_month': load_intl_prev(excel_path, prev_year, [last_m]),
    }


def overview_global_comprehensive(
    excel_path: str,
    year: int = 2026,
    months: list[int] | None = None,
    prev_year: int = 2025,
) -> dict:
    from loader import load_china, load_intl, load_china_prev, load_intl_prev

    df_cn_ytd = load_china(excel_path, year, months)
    df_intl = load_intl(excel_path, year, months)
    df_cn_prev_ytd = load_china_prev(excel_path, prev_year, months)
    df_intl_prev_ytd = load_intl_prev(excel_path, prev_year, months)

    # 品牌识别（统一 T01 helper）
    add_brand_label(df_cn_ytd)
    add_brand_label(df_intl)
    add_brand_label(df_cn_prev_ytd)
    add_brand_label(df_intl_prev_ytd)

    # —— 方案A 单一事实源：全部由明细求和，删除汇总表数值分支 ——
    cn_sales = sum_metric(df_cn_ytd, Col.NET_INCOME)
    intl_sales = sum_metric(df_intl, Col.NET_INCOME)
    global_sales = cn_sales + intl_sales

    cn_sales_prev = sum_metric(df_cn_prev_ytd, Col.NET_INCOME)
    intl_sales_prev = sum_metric(df_intl_prev_ytd, Col.NET_INCOME)
    global_sales_prev = cn_sales_prev + intl_sales_prev

    yoy_cn_sales = calc_yoy_pct(cn_sales, cn_sales_prev)
    yoy_intl_sales = calc_yoy_pct(intl_sales, intl_sales_prev)
    yoy_global_sales = calc_yoy_pct(global_sales, global_sales_prev)

    # 数量（台）
    cn_qty = sum_metric(df_cn_ytd, Col.INVOICE_QTY)
    intl_qty = sum_metric(df_intl, Col.INVOICE_QTY)
    global_qty = cn_qty + intl_qty

    cn_qty_prev = sum_metric(df_cn_prev_ytd, Col.INVOICE_QTY)
    intl_qty_prev = sum_metric(df_intl_prev_ytd, Col.INVOICE_QTY)
    global_qty_prev = cn_qty_prev + intl_qty_prev

    yoy_cn_qty = calc_yoy_pct(cn_qty, cn_qty_prev)
    yoy_intl_qty = calc_yoy_pct(intl_qty, intl_qty_prev)
    yoy_global_qty = calc_yoy_pct(global_qty, global_qty_prev)

    # 品牌（决策1：正泰/诺雅克仅取中国区明细）
    chint = brand_metrics(df_cn_ytd, df_intl, df_cn_prev_ytd, df_intl_prev_ytd, "正泰", global_sales, global_qty)
    noark = brand_metrics(df_cn_ytd, df_intl, df_cn_prev_ytd, df_intl_prev_ytd, "诺雅克", global_sales, global_qty)

    return {
        "global_sales": global_sales,
        "cn_sales": cn_sales,
        "yoy_cn_sales": yoy_cn_sales,
        "intl_sales": intl_sales,
        "yoy_intl_sales": yoy_intl_sales,
        "yoy_global_sales": yoy_global_sales,
        "global_qty": global_qty,
        "cn_qty": cn_qty,
        "yoy_cn_qty": yoy_cn_qty,
        "intl_qty": intl_qty,
        "yoy_intl_qty": yoy_intl_qty,
        "yoy_global_qty": yoy_global_qty,
        "chint_sales": chint["sales"],
        "chint_ys": chint["yoy_sales"],
        "chint_qty": chint["qty"],
        "chint_yq": chint["yoy_qty"],
        "noark_sales": noark["sales"],
        "noark_ys": noark["yoy_sales"],
        "noark_qty": noark["qty"],
        "noark_yq": noark["yoy_qty"],
    }



def aggregate_product_metrics_comprehensive(
    df_curr, df_prev, df_curr_m, df_prev_m
) -> dict:
    res = {}
    
    def calc_totals(df):
        if df is None or len(df) == 0:
            return None, None
        return df[Col.NET_INCOME].sum(), df[Col.INVOICE_QTY].sum()
        
    s_curr, q_curr = calc_totals(df_curr)
    s_prev, q_prev = calc_totals(df_prev)
    s_m_curr, q_m_curr = calc_totals(df_curr_m)
    s_m_prev, q_m_prev = calc_totals(df_prev_m)

    def get_metrics_dict(c_sales, p_sales, c_qty, p_qty, c_sales_m, p_sales_m, c_qty_m, p_qty_m, total_sales_ytd, total_qty_ytd, total_sales_prev, total_qty_prev):
        yoy_s = (c_sales - p_sales) / p_sales * 100 if (p_sales is not None and p_sales > 0) else None
        yoy_q = (c_qty - p_qty) / p_qty * 100 if (p_qty is not None and p_qty > 0) else None
        yoy_sm = (c_sales_m - p_sales_m) / p_sales_m * 100 if (p_sales_m is not None and p_sales_m > 0) else None
        yoy_qm = (c_qty_m - p_qty_m) / p_qty_m * 100 if (p_qty_m is not None and p_qty_m > 0) else None

        share_s = c_sales / total_sales_ytd * 100 if (total_sales_ytd is not None and total_sales_ytd > 0) else None
        share_s_p = p_sales / total_sales_prev * 100 if (p_sales is not None and total_sales_prev is not None and total_sales_prev > 0) else None
        share_q = c_qty / total_qty_ytd * 100 if (total_qty_ytd is not None and total_qty_ytd > 0) else None
        share_q_p = p_qty / total_qty_prev * 100 if (p_qty is not None and total_qty_prev is not None and total_qty_prev > 0) else None

        return {
            'sales_m': c_sales_m,
            'sales_m_yoy': yoy_sm,
            'sales_ytd': c_sales,
            'sales_ytd_yoy': yoy_s,
            'sales_share_prev': share_s_p,
            'sales_share': share_s,
            'qty_m': c_qty_m,
            'qty_m_yoy': yoy_qm,
            'qty_ytd': c_qty,
            'qty_ytd_yoy': yoy_q,
            'qty_share_prev': share_q_p,
            'qty_share': share_q,
            'sales_ytd_prev': p_sales,
            'qty_ytd_prev': p_qty
        }

    res["汇总"] = get_metrics_dict(
        s_curr or 0.0, s_prev, q_curr or 0.0, q_prev,
        s_m_curr or 0.0, s_m_prev, q_m_curr or 0.0, q_m_prev,
        s_curr, q_curr, s_prev, q_prev
    )

    platforms = set()
    if df_curr is not None and Col.PLATFORM in df_curr.columns:
        platforms.update(df_curr[Col.PLATFORM].dropna().unique())
    if df_prev is not None and Col.PLATFORM in df_prev.columns:
        platforms.update(df_prev[Col.PLATFORM].dropna().unique())

    for plat in platforms:
        def filter_plat(df):
            return df[df[Col.PLATFORM] == plat] if (df is not None and Col.PLATFORM in df.columns) else None
            
        df_c_y = filter_plat(df_curr)
        df_p_y = filter_plat(df_prev)
        df_c_m = filter_plat(df_curr_m)
        df_p_m = filter_plat(df_prev_m)

        sc, qc = calc_totals(df_c_y)
        sp, qp = calc_totals(df_p_y)
        smc, qmc = calc_totals(df_c_m)
        smp, qmp = calc_totals(df_p_m)

        res[plat] = get_metrics_dict(
            sc or 0.0, sp, qc or 0.0, qp,
            smc or 0.0, smp, qmc or 0.0, qmp,
            s_curr, q_curr, s_prev, q_prev
        )

        series_list = set()
        if df_c_y is not None:
            series_list.update(df_c_y[Col.SERIES].dropna().unique())
        if df_p_y is not None:
            series_list.update(df_p_y[Col.SERIES].dropna().unique())

        for ser in series_list:
            def filter_ser(df):
                return df[(df[Col.PLATFORM] == plat) & (df[Col.SERIES] == ser)] if df is not None else None
            
            df_c_ys = filter_ser(df_curr)
            df_p_ys = filter_ser(df_prev)
            df_c_ms = filter_ser(df_curr_m)
            df_p_ms = filter_ser(df_prev_m)

            scs, qcs = calc_totals(df_c_ys)
            sps, qps = calc_totals(df_p_ys)
            smcs, qmcs = calc_totals(df_c_ms)
            smps, qmps = calc_totals(df_p_ms)

            res[(plat, ser)] = get_metrics_dict(
                scs or 0.0, sps, qcs or 0.0, qps,
                smcs or 0.0, smps, qmcs or 0.0, qmps,
                s_curr, q_curr, s_prev, q_prev
            )
            
    return res


def product_china_comprehensive_ppt(
    excel_path: str,
    year: int = 2026,
    months: list[int] | None = None,
    prev_year: int = 2025,
    dfs: dict | None = None,
) -> dict:
    if dfs is None:
        dfs = load_all_for_ppt(excel_path, year, months, prev_year)
    df_curr = dfs['cn_ytd']
    df_prev = dfs['cn_prev_ytd']
    df_curr_m = dfs['cn_month']
    df_prev_m = dfs['cn_prev_month']

    # Brand splitting helper
    def _add_brand_label(df):
        add_brand_label(df)

    _add_brand_label(df_curr)
    _add_brand_label(df_prev)
    _add_brand_label(df_curr_m)
    _add_brand_label(df_prev_m)

    return aggregate_product_metrics_comprehensive(df_curr, df_prev, df_curr_m, df_prev_m)


def product_intl_comprehensive_ppt(
    excel_path: str,
    year: int = 2026,
    months: list[int] | None = None,
    prev_year: int = 2025,
    dfs: dict | None = None,
) -> dict:
    if dfs is None:
        dfs = load_all_for_ppt(excel_path, year, months, prev_year)
    df_curr = dfs['intl_ytd']
    df_prev = dfs['intl_prev_ytd']
    df_curr_m = dfs['intl_month']
    df_prev_m = dfs['intl_prev_month']

    # Brand splitting helper
    def _add_brand_label(df):
        add_brand_label(df)

    _add_brand_label(df_curr)
    _add_brand_label(df_prev)
    _add_brand_label(df_curr_m)
    _add_brand_label(df_prev_m)

    return aggregate_product_metrics_comprehensive(df_curr, df_prev, df_curr_m, df_prev_m)


def industry_region_china_comprehensive_ppt(
    excel_path: str,
    year: int = 2026,
    months: list[int] | None = None,
    prev_year: int = 2025,
    dfs: dict | None = None,
) -> dict:
    if dfs is None:
        dfs = load_all_for_ppt(excel_path, year, months, prev_year)
    df_curr = dfs['cn_ytd']
    df_prev = dfs['cn_prev_ytd']
    df_curr_m = dfs['cn_month']
    df_prev_m = dfs['cn_prev_month']

    res = {}
    
    def calc_totals(df):
        if df is None or len(df) == 0:
            return None, None
        return df[Col.NET_INCOME].sum(), df[Col.INVOICE_QTY].sum()
        
    s_curr, q_curr = calc_totals(df_curr)
    s_prev, q_prev = calc_totals(df_prev)
    s_m_curr, q_m_curr = calc_totals(df_curr_m)
    s_m_prev, q_m_prev = calc_totals(df_prev_m)

    def get_metrics_dict(c_sales, p_sales, c_qty, p_qty, c_sales_m, p_sales_m, c_qty_m, p_qty_m, total_sales_ytd, total_qty_ytd, total_sales_prev, total_qty_prev):
        yoy_s = (c_sales - p_sales) / p_sales * 100 if (p_sales is not None and p_sales > 0) else None
        yoy_q = (c_qty - p_qty) / p_qty * 100 if (p_qty is not None and p_qty > 0) else None
        yoy_sm = (c_sales_m - p_sales_m) / p_sales_m * 100 if (p_sales_m is not None and p_sales_m > 0) else None
        yoy_qm = (c_qty_m - p_qty_m) / p_qty_m * 100 if (p_qty_m is not None and p_qty_m > 0) else None

        share_s = c_sales / total_sales_ytd * 100 if (total_sales_ytd is not None and total_sales_ytd > 0) else None
        share_s_p = p_sales / total_sales_prev * 100 if (p_sales is not None and total_sales_prev is not None and total_sales_prev > 0) else None
        share_q = c_qty / total_qty_ytd * 100 if (total_qty_ytd is not None and total_qty_ytd > 0) else None
        share_q_p = p_qty / total_qty_prev * 100 if (p_qty is not None and total_qty_prev is not None and total_qty_prev > 0) else None

        return {
            'sales_m': c_sales_m,
            'sales_m_yoy': yoy_sm,
            'sales_ytd': c_sales,
            'sales_ytd_yoy': yoy_s,
            'sales_share_prev': share_s_p,
            'sales_share': share_s,
            'qty_m': c_qty_m,
            'qty_m_yoy': yoy_qm,
            'qty_ytd': c_qty,
            'qty_ytd_yoy': yoy_q,
            'qty_share_prev': share_q_p,
            'qty_share': share_q,
            'sales_ytd_prev': p_sales,
            'qty_ytd_prev': p_qty
        }

    res["汇总"] = get_metrics_dict(
        s_curr or 0.0, s_prev, q_curr or 0.0, q_prev,
        s_m_curr or 0.0, s_m_prev, q_m_curr or 0.0, q_m_prev,
        s_curr, q_curr, s_prev, q_prev
    )

    def filter_professional(df):
        if df is None or len(df) == 0:
            return df
        col1 = Col.SALES_TEAM_CLASS if Col.SALES_TEAM_CLASS in df.columns else (Col.SALES_TEAM if Col.SALES_TEAM in df.columns else None)
        col2 = Col.SALES_TEAM_REVISION if Col.SALES_TEAM_REVISION in df.columns else None
        if col1 and col2:
            mask = df[col1].isin(INDUSTRY_PROFESSIONAL) | df[col2].isin(INDUSTRY_PROFESSIONAL)
        elif col1:
            mask = df[col1].isin(INDUSTRY_PROFESSIONAL)
        else:
            return df
        return df[mask]

    df_c_pro_ytd = filter_professional(df_curr)
    df_p_pro_ytd = filter_professional(df_prev)
    df_c_pro_m = filter_professional(df_curr_m)
    df_p_pro_m = filter_professional(df_prev_m)

    spc, qpc = calc_totals(df_c_pro_ytd)
    spp, qpp = calc_totals(df_p_pro_ytd)
    spmc, qpmc = calc_totals(df_c_pro_m)
    spmp, qpmp = calc_totals(df_p_pro_m)

    res["专业市场"] = get_metrics_dict(
        spc or 0.0, spp, qpc or 0.0, qpp,
        spmc or 0.0, spmp, qpmc or 0.0, qpmp,
        s_curr, q_curr, s_prev, q_prev
    )

    for ind in INDUSTRY_PROFESSIONAL:
        def filter_ind(df):
            if df is None or len(df) == 0:
                return df
            col = Col.SALES_TEAM_REVISION if Col.SALES_TEAM_REVISION in df.columns else (Col.SALES_TEAM_CLASS if Col.SALES_TEAM_CLASS in df.columns else (Col.SALES_TEAM if Col.SALES_TEAM in df.columns else None))
            if not col:
                return df
            return df[df[col] == ind]
        
        df_c_i = filter_ind(df_curr)
        df_p_i = filter_ind(df_prev)
        df_c_im = filter_ind(df_curr_m)
        df_p_im = filter_ind(df_prev_m)

        sc, qc = calc_totals(df_c_i)
        sp, qp = calc_totals(df_p_i)
        smc, qmc = calc_totals(df_c_im)
        smp, qmp = calc_totals(df_p_im)

        res[ind] = get_metrics_dict(
            sc or 0.0, sp, qc or 0.0, qp,
            smc or 0.0, smp, qmc or 0.0, qmp,
            s_curr, q_curr, s_prev, q_prev
        )

    def filter_general(df):
        if df is None or len(df) == 0:
            return df
        col1 = Col.SALES_TEAM_CLASS if Col.SALES_TEAM_CLASS in df.columns else (Col.SALES_TEAM if Col.SALES_TEAM in df.columns else None)
        col2 = Col.SALES_TEAM_REVISION if Col.SALES_TEAM_REVISION in df.columns else None
        if col1 and col2:
            mask = (~df[col1].isin(INDUSTRY_PROFESSIONAL)) & (~df[col2].isin(INDUSTRY_PROFESSIONAL))
        elif col1:
            mask = ~df[col1].isin(INDUSTRY_PROFESSIONAL)
        else:
            return df
        return df[mask]

    df_c_gen_ytd = filter_general(df_curr)
    df_p_gen_ytd = filter_general(df_prev)
    df_c_gen_m = filter_general(df_curr_m)
    df_p_gen_m = filter_general(df_prev_m)

    sgc, qgc = calc_totals(df_c_gen_ytd)
    sgp, qgp = calc_totals(df_p_gen_ytd)
    sgmc, qgmc = calc_totals(df_c_gen_m)
    sgmp, qgmp = calc_totals(df_p_gen_m)

    res["通用市场"] = get_metrics_dict(
        sgc or 0.0, sgp, qgc or 0.0, qgp,
        sgmc or 0.0, sgmp, qgmc or 0.0, qgmp,
        s_curr, q_curr, s_prev, q_prev
    )

    regions = ["北部", "大湾区", "东北", "华中", "京津冀", "苏皖", "西北", "西南", "长三角", "科创业务"]
    from config import REGION_TO_BIG_AREA

    for reg in regions:
        def filter_reg(df):
            if df is None or len(df) == 0:
                return df
            if reg == "科创业务":
                return df[df[Col.PROVINCE].astype(str).str.contains("科创") | df[Col.SALES_TEAM].astype(str).str.contains("科创")]
            if reg in REGION_TO_BIG_AREA:
                provinces = REGION_TO_BIG_AREA[reg]
                return df[df[Col.PROVINCE].isin(provinces) | df[Col.PROVINCE].astype(str).str.contains(reg)]
            else:
                return df[df[Col.PROVINCE].astype(str).str.contains(reg)]
        
        df_c_r = filter_reg(df_c_gen_ytd)
        df_p_r = filter_reg(df_p_gen_ytd)
        df_c_rm = filter_reg(df_c_gen_m)
        df_p_rm = filter_reg(df_p_gen_m)

        sc, qc = calc_totals(df_c_r)
        sp, qp = calc_totals(df_p_r)
        smc, qmc = calc_totals(df_c_rm)
        smp, qmp = calc_totals(df_p_rm)

        res[reg] = get_metrics_dict(
            sc or 0.0, sp, qc or 0.0, qp,
            smc or 0.0, smp, qmc or 0.0, qmp,
            s_curr, q_curr, s_prev, q_prev
        )

    return res


def region_overseas_comprehensive_ppt(
    excel_path: str,
    year: int = 2026,
    months: list[int] | None = None,
    prev_year: int = 2025,
    dfs: dict | None = None,
) -> dict:
    if dfs is None:
        dfs = load_all_for_ppt(excel_path, year, months, prev_year)
    df_curr = dfs['intl_ytd']
    df_prev = dfs['intl_prev_ytd']
    df_curr_m = dfs['intl_month']
    df_prev_m = dfs['intl_prev_month']

    res = {}
    
    def calc_totals(df):
        if df is None or len(df) == 0:
            return None, None
        return df[Col.NET_INCOME].sum(), df[Col.INVOICE_QTY].sum()
        
    s_curr, q_curr = calc_totals(df_curr)
    s_prev, q_prev = calc_totals(df_prev)
    s_m_curr, q_m_curr = calc_totals(df_curr_m)
    s_m_prev, q_m_prev = calc_totals(df_prev_m)

    def get_metrics_dict(c_sales, p_sales, c_qty, p_qty, c_sales_m, p_sales_m, c_qty_m, p_qty_m, total_sales_ytd, total_qty_ytd, total_sales_prev, total_qty_prev):
        yoy_s = (c_sales - p_sales) / p_sales * 100 if (p_sales is not None and p_sales > 0) else None
        yoy_q = (c_qty - p_qty) / p_qty * 100 if (p_qty is not None and p_qty > 0) else None
        yoy_sm = (c_sales_m - p_sales_m) / p_sales_m * 100 if (p_sales_m is not None and p_sales_m > 0) else None
        yoy_qm = (c_qty_m - p_qty_m) / p_qty_m * 100 if (p_qty_m is not None and p_qty_m > 0) else None

        share_s = c_sales / total_sales_ytd * 100 if (total_sales_ytd is not None and total_sales_ytd > 0) else None
        share_s_p = p_sales / total_sales_prev * 100 if (p_sales is not None and total_sales_prev is not None and total_sales_prev > 0) else None
        share_q = c_qty / total_qty_ytd * 100 if (total_qty_ytd is not None and total_qty_ytd > 0) else None
        share_q_p = p_qty / total_qty_prev * 100 if (p_qty is not None and total_qty_prev is not None and total_qty_prev > 0) else None

        return {
            'sales_m': c_sales_m,
            'sales_m_yoy': yoy_sm,
            'sales_ytd': c_sales,
            'sales_ytd_yoy': yoy_s,
            'sales_share_prev': share_s_p,
            'sales_share': share_s,
            'qty_m': c_qty_m,
            'qty_m_yoy': yoy_qm,
            'qty_ytd': c_qty,
            'qty_ytd_yoy': yoy_q,
            'qty_share_prev': share_q_p,
            'qty_share': share_q,
            'sales_ytd_prev': p_sales,
            'qty_ytd_prev': p_qty
        }

    res["汇总"] = get_metrics_dict(
        s_curr or 0.0, s_prev, q_curr or 0.0, q_prev,
        s_m_curr or 0.0, s_m_prev, q_m_curr or 0.0, q_m_prev,
        s_curr, q_curr, s_prev, q_prev
    )

    from config import OVERSEAS_REGIONS, OVERSEAS_TOP_COUNTRIES
    for reg in OVERSEAS_REGIONS:
        def filter_reg(df):
            return df[df[Col.REGION] == reg] if df is not None else None
        
        df_c = filter_reg(df_curr)
        df_p = filter_reg(df_prev)
        df_cm = filter_reg(df_curr_m)
        df_pm = filter_reg(df_prev_m)

        sc, qc = calc_totals(df_c)
        sp, qp = calc_totals(df_p)
        smc, qc_ = calc_totals(df_cm)
        smp, qp_ = calc_totals(df_pm)

        res[reg] = get_metrics_dict(
            sc or 0.0, sp, qc or 0.0, qp,
            smc or 0.0, smp, qc_ or 0.0, qp_,
            s_curr, q_curr, s_prev, q_prev
        )

    res["国家_汇总"] = res["汇总"]

    # 动态获取当年 YTD 销售额前 10 的国家
    if df_curr is not None and len(df_curr) > 0 and Col.COUNTRY_NAME in df_curr.columns:
        country_sales = df_curr.groupby(Col.COUNTRY_NAME)[Col.NET_INCOME].sum()
        dynamic_countries = country_sales.sort_values(ascending=False).head(10).index.tolist()
    else:
        dynamic_countries = OVERSEAS_TOP_COUNTRIES[:10]

    for ctry in dynamic_countries:
        def filter_ctry(df):
            return df[df[Col.COUNTRY_NAME] == ctry] if df is not None else None
        
        df_c = filter_ctry(df_curr)
        df_p = filter_ctry(df_prev)
        df_cm = filter_ctry(df_curr_m)
        df_pm = filter_ctry(df_prev_m)

        sc, qc = calc_totals(df_c)
        sp, qp = calc_totals(df_p)
        smc, qc_ = calc_totals(df_cm)
        smp, qp_ = calc_totals(df_pm)

        res[f"国家_{ctry}"] = get_metrics_dict(
            sc or 0.0, sp, qc or 0.0, qp,
            smc or 0.0, smp, qc_ or 0.0, qp_,
            s_curr, q_curr, s_prev, q_prev
        )

    return res


def margin_analysis_comprehensive_ppt(
    excel_path: str,
    year: int = 2026,
    months: list[int] | None = None,
    prev_year: int = 2025,
    dfs: dict | None = None,
) -> dict:
    if dfs is None:
        dfs = load_all_for_ppt(excel_path, year, months, prev_year)
    df_curr = dfs['cn_ytd']
    df_prev = dfs['cn_prev_ytd']
    df_curr_m = dfs['cn_month']

    res = {}
    
    # Grand Totals
    tot_sales = df_curr[Col.NET_INCOME].sum() if df_curr is not None else 0.0
    tot_gm = df_curr[Col.GROSS_MARGIN].sum() if df_curr is not None else 0.0
    
    tot_sales_p = df_prev[Col.NET_INCOME].sum() if (df_prev is not None and len(df_prev) > 0) else None
    tot_gm_p = df_prev[Col.GROSS_MARGIN].sum() if (df_prev is not None and len(df_prev) > 0) else None

    tot_sales_m = df_curr_m[Col.NET_INCOME].sum() if df_curr_m is not None else 0.0
    tot_gm_m = df_curr_m[Col.GROSS_MARGIN].sum() if df_curr_m is not None else 0.0

    res["汇总"] = {
        'share': 100.0 if tot_sales > 0 else 0.0,
        'sales_ytd': tot_sales,
        'margin_prev': tot_gm_p / tot_sales_p * 100 if (tot_sales_p is not None and tot_sales_p > 0) else None,
        'margin_ytd': tot_gm / tot_sales * 100 if tot_sales > 0 else None,
        'margin_monthly': tot_gm_m / tot_sales_m * 100 if tot_sales_m > 0 else None
    }

    industry_series = ["9系列", "8系列", "5系列", "E系列", "P系列", "T系列", "H系列", "UL系列"]
    channel_series = ["昆仑系列", "1系列", "青峰系列", "其它"]

    def get_db_series_name(lbl):
        lbl_map = {
            "昆仑系列": "昆仑",
            "UL系列": "UL系列",
            "DZ系列": "DZ",
            "青峰系列": "青峰"
        }
        return lbl_map.get(lbl, lbl)

    def calc_series_metrics(ser_label):
        ser_name = get_db_series_name(ser_label)
        
        def filter_ser(df):
            return df[df[Col.SERIES].astype(str).str.contains(ser_name)] if df is not None else None
            
        df_c = filter_ser(df_curr)
        df_p = filter_ser(df_prev)
        df_cm = filter_ser(df_curr_m)

        s = df_c[Col.NET_INCOME].sum() if df_c is not None else 0.0
        gm_ = df_c[Col.GROSS_MARGIN].sum() if df_c is not None else 0.0
        
        sp = df_p[Col.NET_INCOME].sum() if (df_p is not None and len(df_p) > 0) else None
        gmp = df_p[Col.GROSS_MARGIN].sum() if (df_p is not None and len(df_p) > 0) else None
        
        sm_ = df_cm[Col.NET_INCOME].sum() if df_cm is not None else 0.0
        gmm = df_cm[Col.GROSS_MARGIN].sum() if df_cm is not None else 0.0

        return {
            'share': s / tot_sales * 100 if tot_sales > 0 else 0.0,
            'sales_ytd': s,
            'margin_prev': gmp / sp * 100 if (sp is not None and sp > 0) else None,
            'margin_ytd': gm_ / s * 100 if s > 0 else None,
            'margin_monthly': gmm / sm_ * 100 if sm_ > 0 else None,
            'sales_raw': s,
            'gm_raw': gm_,
            'sales_prev_raw': sp,
            'gm_prev_raw': gmp,
            'sales_m_raw': sm_,
            'gm_m_raw': gmm
        }

    all_metrics = {}
    for lbl in industry_series + channel_series:
        all_metrics[lbl] = calc_series_metrics(lbl)
        res[lbl] = all_metrics[lbl]

    def build_subtotal(sub_label, sub_list):
        s_raw = sum(all_metrics[x]['sales_raw'] for x in sub_list)
        gm_raw = sum(all_metrics[x]['gm_raw'] for x in sub_list)
        
        sp_raw = sum(all_metrics[x]['sales_prev_raw'] for x in sub_list if all_metrics[x]['sales_prev_raw'] is not None)
        gmp_raw = sum(all_metrics[x]['gm_prev_raw'] for x in sub_list if all_metrics[x]['gm_prev_raw'] is not None)
        
        sm_raw = sum(all_metrics[x]['sales_m_raw'] for x in sub_list)
        gmm_raw = sum(all_metrics[x]['gm_m_raw'] for x in sub_list)

        res[sub_label] = {
            'share': s_raw / tot_sales * 100 if tot_sales > 0 else 0.0,
            'sales_ytd': s_raw,
            'margin_prev': gmp_raw / sp_raw * 100 if sp_raw > 0 else None,
            'margin_ytd': gm_raw / s_raw * 100 if s_raw > 0 else None,
            'margin_monthly': gmm_raw / sm_raw * 100 if sm_raw > 0 else None
        }

    build_subtotal("行业", industry_series)
    build_subtotal("渠道", channel_series)

    return res


def detect_latest_month(excel_path: str, year: int = 2026) -> int:
    """自动从中国区数据中探测当期年份最新有销售额的月份"""
    try:
        import loader
        from config import Col
        sheet = loader._resolve_sheet_name(excel_path, "china")
        cache = loader.load_raw_sheet(excel_path, sheet)
        idx = cache["index"]
        if year in idx:
            df = cache["df"]
            detected_months = []
            for m in idx[year]:
                row_indices = idx[year][m]
                if len(row_indices) > 0:
                    subset_sales = df.iloc[row_indices][Col.NET_INCOME]
                    if (subset_sales > 0).any():
                        detected_months.append(m)
            if detected_months:
                return max(detected_months)
    except Exception as e:
        print(f"[WARN] 无法从缓存数据中探测最新月份: {e}")
        
    try:
        df = pd.read_excel(excel_path, sheet_name="主配电-总数据", header=None)
        detected_months = []
        for r in range(len(df)):
            val_year = df.iloc[r, 3]
            try:
                val_year_int = int(val_year)
            except:
                val_year_int = None
                
            if val_year_int == year:
                for m in range(1, 13):
                    col_idx = 4 + m
                    if col_idx < len(df.columns):
                        val = df.iloc[r, col_idx]
                        if pd.notna(val) and isinstance(val, (int, float)) and val > 0:
                            detected_months.append(m)
        if detected_months:
            return max(detected_months)
    except:
        pass
    return 3


def build_monthly_and_ytd_table(df_cn: pd.DataFrame, df_intl: pd.DataFrame, value_col: str, scale: float = 1.0) -> pd.DataFrame:
    """生成 框架-数量 / 框架-销售额 结构（跨年 1-12 月及累计）"""
    from config import Col, OVERSEAS_REGIONS
    years = [2024, 2025, 2026]
    records = []
    
    yr_col = 'year_int' if 'year_int' in df_cn.columns else ('year' if 'year' in df_cn.columns else Col.YEAR)
    mo_col = 'month_int' if 'month_int' in df_cn.columns else ('month' if 'month' in df_cn.columns else Col.MONTH)

    # 1. 中国区 - 正泰
    for yr in years:
        df_yr = df_cn[(df_cn[yr_col] == yr) & (df_cn['brand'] == '正泰')]
        m_vals = []
        ytd_vals = []
        running_sum = 0.0
        for m in range(1, 13):
            val = df_yr[df_yr[mo_col] == m][value_col].sum() * scale
            m_vals.append(val)
            running_sum += val
            ytd_vals.append(running_sum)
        records.append({
            "分州区": "中国区",
            "分类": "正泰",
            "年份": yr,
            "values": m_vals + ytd_vals
        })
        
    # 2. 中国区 - 诺雅克
    for yr in years:
        df_yr = df_cn[(df_cn[yr_col] == yr) & (df_cn['brand'] == '诺雅克')]
        m_vals = []
        ytd_vals = []
        running_sum = 0.0
        for m in range(1, 13):
            val = df_yr[df_yr[mo_col] == m][value_col].sum() * scale
            m_vals.append(val)
            running_sum += val
            ytd_vals.append(running_sum)
        records.append({
            "分州区": "中国区",
            "分类": "诺雅克",
            "年份": yr,
            "values": m_vals + ytd_vals
        })
        
    # 3. 海外 5 大洲区
    yr_col_intl = 'year_int' if 'year_int' in df_intl.columns else ('year' if 'year' in df_intl.columns else Col.YEAR)
    mo_col_intl = 'month_int' if 'month_int' in df_intl.columns else ('month' if 'month' in df_intl.columns else Col.MONTH)
    for reg in OVERSEAS_REGIONS:
        for yr in years:
            df_yr = df_intl[(df_intl[yr_col_intl] == yr) & (df_intl[Col.REGION] == reg)]
            m_vals = []
            ytd_vals = []
            running_sum = 0.0
            for m in range(1, 13):
                val = df_yr[df_yr[mo_col_intl] == m][value_col].sum() * scale
                m_vals.append(val)
                running_sum += val
                ytd_vals.append(running_sum)
            records.append({
                "分州区": reg,
                "分类": np.nan,
                "年份": yr,
                "values": m_vals + ytd_vals
            })
            
    cols = ["分州区", "分类", "年份"] + [f"{m}月" for m in range(1, 13)] + [f"{m}月累计" for m in range(1, 13)]
    rows_data = []
    for r in records:
        row = [r["分州区"], r["分类"], r["年份"]] + r["values"]
        rows_data.append(row)
        
    return pd.DataFrame(rows_data, columns=cols)


def build_industry_table(df_cn: pd.DataFrame, value_col: str, scale: float = 1.0) -> pd.DataFrame:
    """生成 框架-中国区-分行业2026 结构"""
    from config import Col
    years = [2024, 2025, 2026]
    records = []
    
    row_mapping = [
        ("能源与工业业务", "能源与工业业务"),
        ("发电与新能源业务", "发电与新能源业务"),
        ("电网业务", "电网业务"),
        ("信息与通信业务", "信息与通信业务"),
        ("交通与运输业务", "交通与运输业务"),
        ("基础设施业务", "基础设施业务"),
        ("区域工商业", "区域工商业"),
        ("行业内配", "行业内配"),
        ("流通业务", "流通业务"),
        ("盘柜厂", "盘柜厂业务"),
        ("OEM", "OEM业务"),
        ("建筑地产业务", "建筑地产业务"),
        ("集成三箱业务", "集成三箱业务"),
        ("专项业务", "专项业务"),
        ("科创", "科创"),
    ]
    
    team_col = None
    for cand in [53, Col.SALES_TEAM_REVISION, "sales_team_rev", "销售团队映射", "销售团队"]:
        if cand in df_cn.columns:
            team_col = cand
            break

    val_col = None
    for cand in [value_col, Col.NET_INCOME, "total_net_revenue", "销售净收入"]:
        if cand in df_cn.columns:
            val_col = cand
            break

    sales_data = {}
    for team_name, filter_name in row_mapping:
        sales_data[team_name] = {}
        for yr in years:
            if team_col is not None and val_col is not None and yr_col in df_cn.columns:
                df_yr = df_cn[(df_cn[yr_col] == yr) & (df_cn[team_col] == filter_name)]
                m_vals = []
                for m in range(1, 13):
                    val = df_yr[df_yr[mo_col] == m][val_col].sum() * scale if mo_col in df_yr.columns else 0.0
                    m_vals.append(val)
            else:
                m_vals = [0.0] * 12
            sales_data[team_name][yr] = m_vals
            
    pro_teams = ["能源与工业业务", "发电与新能源业务", "电网业务", "信息与通信业务", "交通与运输业务", "基础设施业务", "区域工商业", "行业内配"]
    gen_teams = ["流通业务", "盘柜厂", "OEM", "建筑地产业务", "集成三箱业务", "专项业务"]
    
    sales_data["行业业务"] = {}
    sales_data["渠道业务"] = {}
    sales_data["总计"] = {}
    
    for yr in years:
        sales_data["行业业务"][yr] = [sum(sales_data[t][yr][m] for t in pro_teams) for m in range(12)]
        sales_data["渠道业务"][yr] = [sum(sales_data[t][yr][m] for t in gen_teams) for m in range(12)]
        sales_data["总计"][yr] = [sales_data["行业业务"][yr][m] + sales_data["渠道业务"][yr][m] + sales_data["科创"][yr][m] for m in range(12)]
        
    output_order = [
        "能源与工业业务", "发电与新能源业务", "电网业务", "信息与通信业务",
        "交通与运输业务", "基础设施业务", "区域工商业", "行业内配",
        "流通业务", "盘柜厂", "OEM", "建筑地产业务", "集成三箱业务", "专项业务",
        "科创", "行业业务", "渠道业务", "总计"
    ]
    
    for name in output_order:
        for yr in years:
            m_vals = sales_data[name][yr]
            ytd_vals = []
            running_sum = 0.0
            for val in m_vals:
                running_sum += val
                ytd_vals.append(running_sum)
            records.append({
                "业务团队": name,
                "分类": "年份",
                "年份": yr,
                "values": m_vals + ytd_vals
            })
            
    cols = ["业务团队", "分类", "年份"] + [f"{m}月" for m in range(1, 13)] + [f"{m}月累计" for m in range(1, 13)]
    rows_data = []
    for r in records:
        row = [r["业务团队"], r["分类"], r["年份"]] + r["values"]
        rows_data.append(row)
        
    return pd.DataFrame(rows_data, columns=cols)






