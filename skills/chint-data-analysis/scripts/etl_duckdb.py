"""
etl_duckdb.py — DuckDB ETL 引擎与蓝绿原子替换 (Blue-Green Swap)

职责：
1. 从 data/processed/ 目录下的各产品大类 Excel 文件中，精准提取【中国区数据】/【中国数据】与【海外区数据】/【海外数据】及【辅助数据表】。
2. 规范转换为标准 DuckDB 数据库文件 data/database/<dept>.duckdb。
3. 采用蓝绿双文件 atomic mv 机制：先写 <dept>.duckdb.tmp，校验通过后操作系统级毫秒 replace 覆盖线上库 data/database/<dept>.duckdb。
4. 自动同步加载 semantic_views 构建统一 SQL 语义视图层。
"""
from __future__ import annotations
import os
import glob
import re
import shutil
import duckdb
import pandas as pd
import numpy as np
import json
from datetime import datetime
from pathlib import Path
import sys

def _get_file_registered_yms(f_path: str) -> set | None:
    """读取对应的 metadata.json 获取该文件注册的增量年月集合 (如 {"2026-08"})，防范月度累计文件重复导入历史数据"""
    try:
        f_obj = Path(f_path).resolve()
        for p in [f_obj.parent] + list(f_obj.parents)[:3]:
            for meta_path in [p / "metadata.json", p / "departments" / f_obj.parent.name / "metadata.json"]:
                if meta_path.exists():
                    with open(meta_path, "r", encoding="utf-8") as f:
                        meta = json.load(f)
                    for item in meta.get("files", []):
                        if item.get("saved_name") == f_obj.name or item.get("filename") == f_obj.name:
                            yms = item.get("year_months", [])
                            if yms:
                                return set(yms)
    except Exception as e:
        print(f"[Warning] Failed to read registered year_months for {f_path}: {e}")
    return None

def _get_file_sheet_override(f_path: str, region: str) -> str | None:
    """读取对应的 metadata.json 获取该 Excel 文件的 PM 手动选页覆盖配置 (sheet_overrides)"""
    try:
        f_obj = Path(f_path).resolve()
        for p in [f_obj.parent] + list(f_obj.parents)[:3]:
            for meta_path in [p / "metadata.json", p / "departments" / f_obj.parent.name / "metadata.json"]:
                if meta_path.exists():
                    with open(meta_path, "r", encoding="utf-8") as f:
                        meta = json.load(f)
                    for item in meta.get("files", []):
                        if item.get("saved_name") == f_obj.name or item.get("filename") == f_obj.name:
                            overrides = item.get("sheet_overrides", {})
                            if isinstance(overrides, dict) and region in overrides:
                                return overrides[region]
    except Exception as e:
        print(f"[Warning] Failed to read sheet_overrides for {f_path}: {e}")
    return None


# 确保项目根目录和 scripts 目录加入 sys.path
_scripts_dir = Path(__file__).resolve().parent
_project_root = _scripts_dir.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))
if str(_scripts_dir) not in sys.path:
    sys.path.insert(0, str(_scripts_dir))

try:
    from config import (
        BASE_DIR, RAW_DIR, PROCESSED_DIR, DATABASE_DIR, MAPPING_DIR, PROCESSED_EXCEL_PATH, DUCKDB_PATH,
        SHEET_NAMES_CN, SHEET_NAMES_INTL, SHEET_NAME_AUX,
        DUCKDB_TABLE_SALES, DUCKDB_TABLE_CN, DUCKDB_TABLE_INTL, DUCKDB_TABLE_AUX,
        PARQUET_CN_PATTERN, PARQUET_INTL_PATTERN
    )
except ImportError:
    BASE_DIR = str(_project_root)
    RAW_DIR = str(_project_root / "data" / "raw")
    PROCESSED_DIR = str(_project_root / "data" / "processed")
    DATABASE_DIR = str(_project_root / "data" / "database")
    MAPPING_DIR = str(_project_root / "data" / "mapping")
    PROCESSED_EXCEL_PATH = str(_project_root / "data" / "processed" / "acb" / "主配电24-26年销售数据-框架.xlsx")
    DUCKDB_PATH = str(_project_root / "data" / "database" / "acb.duckdb")
    SHEET_NAMES_CN = ["中国区数据", "中国数据", "中国区"]
    SHEET_NAMES_INTL = ["海外数据", "海外区数据", "国际数据", "国际"]
    SHEET_NAME_AUX = "辅助数据表"
    DUCKDB_TABLE_SALES = "sales_data"
    DUCKDB_TABLE_CN = "china_data"
    DUCKDB_TABLE_INTL = "overseas_data"
    DUCKDB_TABLE_AUX = "aux_data"
    PARQUET_CN_PATTERN = "china_*.parquet"
    PARQUET_INTL_PATTERN = "intl_*.parquet"

try:
    from loader import _resolve_sheet_name
except ImportError:
    try:
        from etl.loader import _resolve_sheet_name
    except ImportError:
        def _resolve_sheet_name(xl, candidates):
            sheet_names = xl.sheet_names if hasattr(xl, "sheet_names") else []
            for c in candidates:
                if c in sheet_names:
                    return c
            return sheet_names[0] if sheet_names else ""



def read_excel_fast(io, sheet_name=0, **kwargs):
    """Ultra-fast Excel reading using Rust-powered calamine engine."""
    if isinstance(io, pd.ExcelFile):
        return io.parse(sheet_name=sheet_name, **kwargs)
    try:
        ef = pd.ExcelFile(io, engine="calamine")
        return ef.parse(sheet_name=sheet_name, **kwargs)
    except Exception:
        try:
            return pd.read_excel(io, sheet_name=sheet_name, engine="calamine", **kwargs)
        except Exception:
            return pd.read_excel(io, sheet_name=sheet_name, **kwargs)


def read_excel_smart_header(io, sheet_name=0):
    """读取 Excel 表格，在前 5 行中自动探测有效表头行（仅单次探针采样，不重复全表读取）。"""
    keywords = ["报表来源", "产业", "年份", "月份", "发票数量", "净收入（不含税）", "产品系列", "物料编码", "物料描述", "客户名称"]
    
    ef = io if isinstance(io, pd.ExcelFile) else None
    if ef is None:
        try:
            ef = pd.ExcelFile(io, engine="calamine")
        except Exception:
            ef = None

    if ef is not None:
        best_header = 0
        for header_row in range(5):
            try:
                sample_df = ef.parse(sheet_name=sheet_name, header=header_row, nrows=5)
                cols = [str(c).strip() for c in sample_df.columns]
                if any(k in cols for k in keywords):
                    best_header = header_row
                    break
            except Exception:
                pass
        return ef.parse(sheet_name=sheet_name, header=best_header)

    for header_row in range(5):
        try:
            sample_df = pd.read_excel(io, sheet_name=sheet_name, header=header_row, nrows=5, engine="calamine")
            cols = [str(c).strip() for c in sample_df.columns]
            if any(k in cols for k in keywords):
                return pd.read_excel(io, sheet_name=sheet_name, header=header_row, engine="calamine")
        except Exception:
            pass
    return pd.read_excel(io, sheet_name=sheet_name)


def parse_month_to_int(val):
    try:
        from etl.loader import month_str_to_int
    except ImportError:
        from loader import month_str_to_int
    try:
        res = month_str_to_int(val)
        if res is not None:
            return res
    except (ValueError, TypeError):
        pass
    if pd.isna(val):
        return 0
    s = str(val).strip()
    match = re.search(r'^0*(\d{1,2})月?$', s)
    if match:
        mo = int(match.group(1))
        return mo if 1 <= mo <= 12 else 0
    return 0


_CATEGORY_REMAP_CACHE = None

def load_category_remap_rules():
    global _CATEGORY_REMAP_CACHE
    if _CATEGORY_REMAP_CACHE is not None:
        return _CATEGORY_REMAP_CACHE
    base_dir = Path(__file__).resolve().parent.parent
    json_path = os.path.join(base_dir, "data", "mapping", "category_remap.json")
    if os.path.exists(json_path):
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                _CATEGORY_REMAP_CACHE = json.load(f)
                return _CATEGORY_REMAP_CACHE
        except Exception as e:
            print(f"[Warning] Failed to read category_remap.json: {e}")
    _CATEGORY_REMAP_CACHE = {"material_code_map": {}, "material_desc_regex": [], "manufacturing_unit_map": {}}
    return _CATEGORY_REMAP_CACHE


def standardize_and_remap_categories(df: pd.DataFrame) -> pd.DataFrame:
    """
    清洗并规范化产品大类 (product_category)：
    1. 完全剔除 '隔离开关&刀开关' 大类，严禁写入数据仓库。
    2. 重命名：
       - '框架类' -> '框架' (代码: ACB)
       - '塑壳类' -> '塑壳' (代码: MCCB)
       - '其它低压类' / '其他低压类' -> '虚拟工厂' (代码: VF)
       - '微断类' / '微断' / '终端类' -> '虚拟工厂' (代码: VF)
    3. 对于 '其他' 大类，使用多级规则链匹配：
       - 级1: 物料编码 (material_code) 精准映射
       - 级2: 物料描述 (material_desc) / 产品系列 (product_series) 正则匹配
       - 级3: 生产制造单位 (factory) 匹配
       - 无法匹配的强制标记为 '[待PM确认]'，绝不隐式自动兜底！
    4. 添加/标准化 category_code 字段 (ACB, MCCB, PQ, ATSE, VF, 或 [待PM确认])
    """
    if df.empty:
        if "category_code" not in df.columns:
            df["category_code"] = pd.Series(dtype=str)
        return df

    if "product_category" not in df.columns:
        df["category_code"] = "[待PM确认]"
        return df

    # 1. 完全剔除 '隔离开关&刀开关'
    df = df[~df["product_category"].astype(str).str.strip().isin(["隔离开关&刀开关", "隔离开关", "刀开关"])].copy()
    if df.empty:
        df["category_code"] = pd.Series(dtype=str)
        return df

    # 2. 规范已知分类名称
    cat_series = df["product_category"].astype(str).str.strip()
    rename_map = {
        "框架类": "框架",
        "塑壳类": "塑壳",
        "其它低压类": "虚拟工厂",
        "其他低压类": "虚拟工厂",
        "微断类": "虚拟工厂",
        "微断": "虚拟工厂",
        "终端类": "虚拟工厂",
        "终端配电类": "虚拟工厂"
    }
    cat_series = cat_series.replace(rename_map)
    df["product_category"] = cat_series

    # 3. 处理 '其他' 分类 (多级规则链匹配)
    other_mask = df["product_category"].isin(["其他", "其它", "other", "Other", ""])
    if other_mask.any():
        rules = load_category_remap_rules()
        code_map = rules.get("material_code_map", {})
        regex_list = rules.get("material_desc_regex", [])
        mfg_map = rules.get("manufacturing_unit_map", {})

        compiled_regexes = []
        for r in regex_list:
            pat = r.get("pattern", "")
            target_cat = r.get("target_category", "")
            cat_code = r.get("category_code", "")
            if pat and target_cat:
                try:
                    compiled_regexes.append((re.compile(pat, re.IGNORECASE), target_cat, cat_code))
                except Exception:
                    pass

        other_indices = df[other_mask].index
        for idx in other_indices:
            mat_code = str(df.at[idx, "material_code"]).strip() if "material_code" in df.columns else ""
            mat_desc = str(df.at[idx, "material_desc"]).strip() if "material_desc" in df.columns else ""
            prod_series = str(df.at[idx, "product_series"]).strip() if "product_series" in df.columns else ""
            factory = str(df.at[idx, "factory"]).strip() if "factory" in df.columns else ""

            matched_cat = None
            # Step 1: 物料编码匹配
            if mat_code and mat_code in code_map:
                matched_cat = code_map[mat_code]
            # Step 2: 物料描述/系列正则匹配
            if not matched_cat and (mat_desc or prod_series):
                text_to_test = f"{mat_desc} {prod_series}"
                for cregex, tcat, ccode in compiled_regexes:
                    if cregex.search(text_to_test):
                        matched_cat = tcat
                        break
            # Step 3: 生产制造单位匹配
            if not matched_cat and factory and factory in mfg_map:
                matched_cat = mfg_map[factory]

            # 匹配成功则更新大类，否则显式设为 '[待PM确认]'（严禁隐式自动兜底）
            if matched_cat:
                df.at[idx, "product_category"] = matched_cat
            else:
                df.at[idx, "product_category"] = "[待PM确认]"

    category_code_map = {
        "框架": "ACB",
        "塑壳": "MCCB",
        "电能质量": "PQ",
        "双电源": "ATSE",
        "虚拟工厂": "VF",
    }
    df["category_code"] = df["product_category"].map(lambda x: category_code_map.get(str(x).strip(), "[待PM确认]"))
    return df


# Excel 原始 49 列物理字段映射定义 (SSOT)
EXCEL_COL_MAP = [
    # (中文列名别名列表, DuckDB字段名, 默认类型, 默认值)
    (["报表来源"], "report_source", "str", "中国区-正泰"),
    (["产业", "brand_sector"], "brand_sector", "str", "正泰电器"),
    (["业务分类", "biz_category"], "biz_category", "str", "渠道业务"),
    (["洲区", "continent"], "continent", "str", ""),
    (["国家", "country"], "country", "str", "中国"),
    (["国家名称", "country_name"], "country_name", "str", "中国"),
    (["省份", "province"], "province", "str", "其他"),
    (["年份", "year"], "year", "year", 0),
    (["月份", "month"], "month", "month", 0),
    (["生产制造单位编码", "mfg_unit_code"], "mfg_unit_code", "str", ""),
    (["生产制造单位", "mfg_unit", "制造单位", "生产单位"], "mfg_unit", "str", ""),
    (["物料组编码", "material_group_code"], "material_group_code", "str", ""),
    (["物料组描述", "material_group_desc", "物料组"], "material_group_desc", "str", ""),
    (["物料编码", "material_code"], "material_code", "str", ""),
    (["物料描述", "material_desc", "修正物料组描述"], "material_desc", "str", ""),
    (["客户性质", "customer_nature"], "customer_nature", "str", ""),
    (["网点客户号", "outlet_customer_no"], "outlet_customer_no", "str", ""),
    (["网点客户名称", "outlet_customer_name"], "outlet_customer_name", "str", ""),
    (["客户号", "customer_no"], "customer_no", "str", ""),
    (["客户名称", "customer_name"], "customer_name", "str", ""),
    (["终端客户", "terminal_customer"], "terminal_customer", "str", ""),
    (["项目编号", "project_no"], "project_no", "str", ""),
    (["项目名称", "project_name"], "project_name", "str", ""),
    (["销售组织编码", "sales_org_code"], "sales_org_code", "str", ""),
    (["销售组织", "sales_org"], "sales_org", "str", ""),
    (["新政策大类", "new_policy_category"], "new_policy_category", "str", ""),
    (["发票数量", "开票数量", "sales_qty", "invoice_qty"], "invoice_qty", "float", 0.0),
    (["开单价金额（含税）", "开单价金额(含税)", "billing_price_amount"], "billing_price_amount", "float", 0.0),
    (["结算价金额（含税）", "结算价金额(含税)", "settlement_price_amount"], "settlement_price_amount", "float", 0.0),
    (["净额（不含税）", "净额(不含税)", "net_amount"], "net_amount", "float", 0.0),
    (["折让（不含税）", "折让(不含税)", "discount_amount"], "discount_amount", "float", 0.0),
    (["费用（不含税）", "费用(不含税)", "expense_amount"], "expense_amount", "float", 0.0),
    (["净收入（不含税）", "净收入(不含税)", "净收入", "net_revenue"], "net_revenue", "float", 0.0),
    (["口袋价（含税）", "口袋价(含税)", "pocket_price"], "pocket_price", "float", 0.0),
    (["产品成本（不含税）", "产品成本(不含税)", "产品成本", "product_cost"], "product_cost", "float", 0.0),
    (["总成本（不含税）", "总成本(不含税)", "total_cost"], "total_cost", "float", 0.0),
    (["毛利额（不含税）", "毛利额(不含税)", "毛利额", "gross_profit"], "gross_profit", "float", 0.0),
    (["本位币种", "currency"], "currency", "str", "CNY"),
    (["汇率(本币)", "汇率（本币）", "exchange_rate"], "exchange_rate", "float", 1.0),
    (["收入（本币）", "收入(本币)", "revenue_local_currency"], "revenue_local_currency", "float", 0.0),
    (["成本（本币）", "成本(本币)", "cost_local_currency"], "cost_local_currency", "float", 0.0),
    (["产品产业分类", "product_industry_category"], "product_industry_category", "str", ""),
    (["销售团队", "sales_team"], "sales_team", "str", ""),
    (["通用/专业", "general_or_specialized"], "general_or_specialized", "str", ""),
    (["产品系列", "product_series"], "product_series", "str", ""),
    (["产品平台", "product_platform"], "product_platform", "str", ""),
    (["产品管理团队", "product_manager_team"], "product_manager_team", "str", ""),
    (["产品大类", "product_category"], "product_category", "str", ""),
    (["内配客户标记", "internal_customer_flag"], "internal_customer_flag", "str", ""),
]




def _extract_mapped_columns(df: pd.DataFrame, default_source: str = "中国区-正泰") -> pd.DataFrame:
    n = len(df)
    mapped = pd.DataFrame(index=df.index)

    for aliases, target_col, col_type, default_val in EXCEL_COL_MAP:
        effective_default = default_source if target_col == "report_source" else default_val
        src_col = next((c for c in aliases if c in df.columns), None)
        if src_col is not None:
            if col_type == "str":
                mapped[target_col] = df[src_col].fillna(effective_default).replace({"": effective_default}).astype(str).str.strip()
            elif col_type == "float":
                mapped[target_col] = pd.to_numeric(df[src_col], errors='coerce').fillna(effective_default).astype(float)
            elif col_type == "year":
                mapped[target_col] = pd.to_numeric(df[src_col].astype(str).str.replace("年", "").str.strip(), errors='coerce').fillna(0).astype(int)
            elif col_type == "month":
                mapped[target_col] = df[src_col].apply(parse_month_to_int)
        else:
            if col_type == "str":
                mapped[target_col] = [effective_default] * n
            elif col_type == "float":
                mapped[target_col] = [effective_default] * n
            elif col_type == "year":
                mapped[target_col] = [0] * n
            elif col_type == "month":
                mapped[target_col] = [0] * n

    # 属性提取 (property)
    prop_col = next((c for c in ["属性", "property"] if c in df.columns), None)
    mapped["property"] = df[prop_col].fillna("").astype(str).str.strip() if prop_col else [""] * n

    # 默认型号与特征参数
    for feat_col, feat_aliases in [
        ("product_model", ["产品型号", "product_model"]),
        ("frame_current", ["壳架电流", "frame_current"]),
        ("breaking_capacity", ["分断能力", "breaking_capacity"]),
        ("operation_method", ["操作方式", "安装方式", "operation_method"]),
        ("pole_count", ["极数", "pole_count"]),
        ("n_pole_type", ["N极方式", "N极连接方式", "n_pole_type"]),
    ]:
        found = next((c for c in feat_aliases if c in df.columns), None)
        mapped[feat_col] = df[found].fillna("").astype(str).str.strip() if found else [""] * n

    # 产品平台标准化清洗
    if "product_platform" in mapped.columns:
        plat_s = mapped["product_platform"].astype(str).str.strip()
        mapped["product_platform"] = (
            plat_s
            .replace({
                "新锐(5)": "新锐",
                "新锐（5）": "新锐",
                "新锐平台": "新锐",
                "诺雅克(9)": "诺雅克",
                "诺雅克（9）": "诺雅克",
                "诺雅克平台": "诺雅克",
                "昆仑平台": "昆仑",
                "其他": "其它",
                "其他平台": "其它",
                "其它平台": "其它",
                "": "其它",
                "nan": "其它",
                "None": "其它",
            })
        )

    # 产品系列标准化清洗
    if "product_series" in mapped.columns:
        series_s = mapped["product_series"].astype(str).str.strip()
        mapped["product_series"] = series_s.replace({
            "其他": "其它",
            "其它平台": "其它",
        })

    return mapped


def clean_cn_data(df: pd.DataFrame, source_file: str = "", df_aux: pd.DataFrame | None = None) -> pd.DataFrame:
    """按 DDL 规范清洗中国区数据，无损保留 49 列全部原始物理字段与衍生特征"""
    if df.empty:
        return pd.DataFrame()
    mapped = _extract_mapped_columns(df, default_source="中国区-正泰")

    # 针对属性缺失场景，优先通过辅助数据表 (df_aux) 根据物料描述或编码补全 property (本体/附件)
    if df_aux is not None and not df_aux.empty and "property" in df_aux.columns:
        missing_mask = mapped["property"].str.strip() == ""
        if missing_mask.any():
            if "material_desc_fixed" in df_aux.columns and "material_desc" in mapped.columns:
                aux_desc_map = dict(zip(df_aux["material_desc_fixed"].astype(str).str.strip(), df_aux["property"].astype(str).str.strip()))
                matched_by_desc = mapped.loc[missing_mask, "material_desc"].astype(str).str.strip().map(aux_desc_map)
                mapped.loc[missing_mask, "property"] = matched_by_desc.fillna("")

            still_missing = mapped["property"].str.strip() == ""
            if still_missing.any() and "material_code" in df_aux.columns and "material_code" in mapped.columns:
                aux_code_map = dict(zip(df_aux["material_code"].astype(str).str.strip(), df_aux["property"].astype(str).str.strip()))
                matched_by_code = mapped.loc[still_missing, "material_code"].astype(str).str.strip().map(aux_code_map)
                mapped.loc[still_missing, "property"] = matched_by_code.fillna("")

    mapped["_ingested_at"] = [datetime.now().isoformat()] * len(mapped)
    mapped["_source_file"] = [os.path.basename(source_file) if source_file else ""] * len(mapped)

    mapped = standardize_and_remap_categories(mapped)
    mapped = mapped[mapped["year"] > 0].reset_index(drop=True)
    return mapped


def clean_intl_data(df: pd.DataFrame, source_file: str = "", df_aux: pd.DataFrame | None = None) -> pd.DataFrame:
    """按 DDL 规范清洗海外区数据，无损保留 49 列全部原始物理字段与衍生特征"""
    if df.empty:
        return pd.DataFrame()
    mapped = _extract_mapped_columns(df, default_source="国际")
    if not mapped["report_source"].str.strip().any() or mapped["report_source"].str.strip().eq("中国区-正泰").all():
        mapped["report_source"] = "国际"

    # 针对属性缺失场景，优先通过辅助数据表 (df_aux) 根据物料描述或编码补全 property (本体/附件)
    if df_aux is not None and not df_aux.empty and "property" in df_aux.columns:
        missing_mask = mapped["property"].str.strip() == ""
        if missing_mask.any():
            if "material_desc_fixed" in df_aux.columns and "material_desc" in mapped.columns:
                aux_desc_map = dict(zip(df_aux["material_desc_fixed"].astype(str).str.strip(), df_aux["property"].astype(str).str.strip()))
                matched_by_desc = mapped.loc[missing_mask, "material_desc"].astype(str).str.strip().map(aux_desc_map)
                mapped.loc[missing_mask, "property"] = matched_by_desc.fillna("")

            still_missing = mapped["property"].str.strip() == ""
            if still_missing.any() and "material_code" in df_aux.columns and "material_code" in mapped.columns:
                aux_code_map = dict(zip(df_aux["material_code"].astype(str).str.strip(), df_aux["property"].astype(str).str.strip()))
                matched_by_code = mapped.loc[still_missing, "material_code"].astype(str).str.strip().map(aux_code_map)
                mapped.loc[still_missing, "property"] = matched_by_code.fillna("")

    mapped["_ingested_at"] = [datetime.now().isoformat()] * len(mapped)
    mapped["_source_file"] = [os.path.basename(source_file) if source_file else ""] * len(mapped)

    mapped = standardize_and_remap_categories(mapped)
    mapped = mapped[mapped["year"] > 0].reset_index(drop=True)
    return mapped




def clean_aux_data(df: pd.DataFrame) -> pd.DataFrame:
    """按 DDL 规范清洗辅助字典表"""
    mapped = pd.DataFrame()
    if not df.empty and len(df.columns) >= 6:
        cols = list(df.columns)
        mapped["material_code"] = df[cols[0]].fillna("").astype(str)
        mapped["material_desc_fixed"] = df[cols[1]].fillna("").astype(str)
        mapped["product_manager"] = df[cols[2]].fillna("").astype(str)
        mapped["property"] = df[cols[3]].fillna("").astype(str)
        mapped["province"] = df[cols[4]].fillna("").astype(str)
        mapped["region"] = df[cols[5]].fillna("").astype(str)
    else:
        mapped["material_code"] = []
        mapped["material_desc_fixed"] = []
        mapped["product_manager"] = []
        mapped["property"] = []
        mapped["province"] = []
        mapped["region"] = []
    return mapped


def get_all_processed_files(processed_dir=PROCESSED_DIR, raw_dir=RAW_DIR) -> list:
    """自动扫描 data/raw/ 根目录与 data/raw/new/ 目录下所有有效 Excel 统一数据源文件"""
    search_dirs = [raw_dir, processed_dir]
    files = []
    for d in search_dirs:
        if os.path.exists(d):
            found = [
                f for f in glob.glob(os.path.join(d, "**", "*.xlsx"), recursive=True)
                if not os.path.basename(f).startswith("~$") and not os.path.basename(f).startswith("test_") 
                and not f.endswith(".temp.xlsx") and not f.endswith(".tmp.xlsx") and not f.endswith(".tmp")
                and "映射清单" not in f and "待确认" not in f and "差异原因" not in f
                and "legacy_depts" not in f and "archive" not in f
            ]
            files.extend(found)

    if not files and os.path.exists(PROCESSED_EXCEL_PATH):
        return [PROCESSED_EXCEL_PATH]
    deduped = list(dict.fromkeys(files))
    return sorted(deduped, key=os.path.getmtime, reverse=True)


from config import UNIFIED_DUCKDB_PATH


def _resolve_all_matching_sheets(all_sheets: list, region: str, override: str | None = None) -> list:
    """智能解析并返回该 Excel 中属于指定区域（china 或 intl）的所有有效数据 Sheet 页名列表"""
    if override and override in all_sheets:
        return [override]

    china_keywords = ["中国区", "中国", "CN", "主配电", "分配电", "正泰中国", "正泰中压"]
    intl_keywords = ["国际", "海外", "海外区", "外贸"]
    excluded_keywords = [
        "虚拟", "归档", "草稿", "差异原因", "映射", "汇总", "透视", "备份", "副本",
        "summary", "pivot", "backup", "copy"
    ]

    matched = []
    for s in all_sheets:
        s_clean = s.strip()
        if s_clean.startswith("~$") or s_clean.lower().startswith("sheet"):
            continue
        if any(ex in s_clean.lower() for ex in excluded_keywords):
            continue
        if region == "china":
            if any(k in s_clean for k in china_keywords) and not any(k in s_clean for k in intl_keywords):
                matched.append(s)
        elif region == "intl":
            if any(k in s_clean for k in intl_keywords):
                matched.append(s)

    if not matched:
        try:
            cand = _resolve_sheet_name(None, region=region, sheet_override=override)
            if cand in all_sheets:
                matched.append(cand)
        except Exception:
            pass
    return list(dict.fromkeys(matched))


def run_duckdb_etl(source_excel: str = None,
                   target_db: str = UNIFIED_DUCKDB_PATH,
                   progress_callback = None,
                   force: bool = False,
                   df_china: pd.DataFrame | None = None,
                   df_intl: pd.DataFrame | None = None):
    """运行 DuckDB ETL，抽取数据、生成 FastPath Parquet 缓存并执行蓝绿原子替换"""
    if df_china is not None or df_intl is not None:
        df_cn = clean_cn_data(df_china) if df_china is not None else clean_cn_data(pd.DataFrame())
        df_intl = clean_intl_data(df_intl) if df_intl is not None else clean_intl_data(pd.DataFrame())
        df_aux = clean_aux_data(pd.DataFrame())

        tmp_db = target_db + ".tmp"
        if os.path.exists(tmp_db):
            try:
                os.remove(tmp_db)
            except Exception:
                pass
        os.makedirs(os.path.dirname(target_db), exist_ok=True)

        df_sales = pd.concat([df_cn, df_intl], ignore_index=True)
        con = duckdb.connect(tmp_db)
        try:
            con.register("df_sales_view", df_sales)
            con.register("df_aux_view", df_aux)
            con.execute(f"""
            CREATE TABLE {DUCKDB_TABLE_SALES} AS SELECT * FROM df_sales_view;
            CREATE TABLE {DUCKDB_TABLE_AUX} AS SELECT * FROM df_aux_view;
            """)
        finally:
            con.close()

        from etl.semantic_views import apply_semantic_views
        apply_semantic_views(db_path=tmp_db, read_only=False)
        os.replace(tmp_db, target_db)
        return

    if source_excel:
        target_files = [source_excel]
    else:
        target_files = get_all_processed_files()

    if not target_files:
        raise FileNotFoundError(f"No processed excel files found in {PROCESSED_DIR}")

    # 缓存实时性校验：若 force=False 且 DuckDB 数据库比所有原始数据源及映射配置新，直接跳过重解析
    if not force and os.path.exists(target_db):
        source_mtimes = [os.path.getmtime(f) for f in target_files if os.path.exists(f)]
        mapping_files = glob.glob(os.path.join(MAPPING_DIR, "*.json"))
        views_sql = os.path.join(os.path.dirname(__file__), "dataease_views.sql")
        if os.path.exists(views_sql):
            mapping_files.append(views_sql)
        source_mtimes.extend(os.path.getmtime(mf) for mf in mapping_files if os.path.exists(mf))

        if source_mtimes:
            max_source_mtime = max(source_mtimes)
            if os.path.getmtime(target_db) >= max_source_mtime:
                print(f"[ETL Cache] DuckDB 数据库 ({os.path.basename(target_db)}) 已是最新状态，跳过重复 Excel 解析。")
                from etl.semantic_views import apply_semantic_views
                apply_semantic_views(db_path=target_db, read_only=False)
                return

    # 0. 开展 Excel 原始数据文件结构合规检测
    try:
        from etl.data_validator import validate_raw_excel, format_validation_report
    except ImportError:
        try:
            from data_validator import validate_raw_excel, format_validation_report
        except ImportError:
            class _DummyValRes:
                is_valid = True
                errors = []
            def validate_raw_excel(f): return _DummyValRes()
            def format_validation_report(r): return "[Validation Bypass] data_validator not found."

    valid_target_files = []
    for f_path in target_files:
        val_res = validate_raw_excel(f_path)
        if not val_res.is_valid:
            print(format_validation_report(val_res))
            print(f"[ERROR] 文件 '{os.path.basename(f_path)}' 结构校验未通过，已被系统拦截，无法进行入库操作！")
        else:
            valid_target_files.append(f_path)

    if not valid_target_files:
        raise ValueError("所有输入的 Excel 数据源均未通过结构合规检测，请参照上面的指引修复表头或 Sheet 结构后重试。")
    target_files = valid_target_files

    if progress_callback:
        progress_callback("vectorized", "正在向量化清洗多维 50+ 交易明细列...", 45.0)

    tmp_db = target_db + ".tmp"
    if os.path.exists(tmp_db):
        try:
            os.remove(tmp_db)
        except Exception:
            pass

    os.makedirs(os.path.dirname(target_db), exist_ok=True)
    os.makedirs(PROCESSED_DIR, exist_ok=True)

    cn_list = []
    intl_list = []
    aux_list = []

    # 优先第一遍提取辅助数据表 (df_aux)，以便用来补全主表属性
    for f_path in target_files:
        if not os.path.exists(f_path):
            continue
        try:
            excel_file = pd.ExcelFile(f_path, engine="calamine")
            if SHEET_NAME_AUX in excel_file.sheet_names:
                df_aux_raw = read_excel_fast(excel_file, sheet_name=SHEET_NAME_AUX)
                aux_list.append(clean_aux_data(df_aux_raw))
        except Exception:
            pass

    df_aux = pd.concat(aux_list, ignore_index=True).drop_duplicates(subset=["material_code"]) if aux_list else clean_aux_data(pd.DataFrame())

    for f_path in target_files:
        if not os.path.exists(f_path):
            continue
        print(f"[ETL Process] Reading excel source via calamine: {f_path}")
        try:
            excel_file = pd.ExcelFile(f_path, engine="calamine")
        except Exception:
            excel_file = pd.ExcelFile(f_path)
        all_sheets = excel_file.sheet_names

        # 提取并清洗活跃 Sheet (支持单文件多业务 Sheet，如同时包含中国区主配电与分配电)
        override_cn = _get_file_sheet_override(f_path, "china")
        cn_sheets = _resolve_all_matching_sheets(all_sheets, "china", override=override_cn)

        override_intl = _get_file_sheet_override(f_path, "intl")
        intl_sheets = _resolve_all_matching_sheets(all_sheets, "intl", override=override_intl)

        reg_yms = _get_file_registered_yms(f_path)

        for cn_sheet in cn_sheets:
            try:
                df_cn_raw = read_excel_smart_header(excel_file, sheet_name=cn_sheet)
                cleaned_cn = clean_cn_data(df_cn_raw, source_file=f_path, df_aux=df_aux)
                if reg_yms and not cleaned_cn.empty and "year" in cleaned_cn.columns and "month" in cleaned_cn.columns:
                    ym_series = cleaned_cn["year"].astype(str) + "-" + cleaned_cn["month"].astype(str).str.zfill(2)
                    excel_yms = set(ym_series.unique())
                    effective_yms = reg_yms | excel_yms if (excel_yms - reg_yms) else reg_yms
                    cleaned_cn = cleaned_cn[ym_series.isin(effective_yms)]
                if not cleaned_cn.empty:
                    cn_list.append(cleaned_cn)
                    print(f"  [Sheet Ingested] {os.path.basename(f_path)} -> [{cn_sheet}]: {len(cleaned_cn)} rows")
            except Exception as e:
                print(f"[Warning] Failed to read {cn_sheet} from {f_path}: {e}")

        for intl_sheet in intl_sheets:
            try:
                df_intl_raw = read_excel_smart_header(excel_file, sheet_name=intl_sheet)
                cleaned_intl = clean_intl_data(df_intl_raw, source_file=f_path, df_aux=df_aux)
                if reg_yms and not cleaned_intl.empty and "year" in cleaned_intl.columns and "month" in cleaned_intl.columns:
                    ym_series = cleaned_intl["year"].astype(str) + "-" + cleaned_intl["month"].astype(str).str.zfill(2)
                    excel_yms = set(ym_series.unique())
                    effective_yms = reg_yms | excel_yms if (excel_yms - reg_yms) else reg_yms
                    cleaned_intl = cleaned_intl[ym_series.isin(effective_yms)]
                if not cleaned_intl.empty:
                    intl_list.append(cleaned_intl)
                    print(f"  [Sheet Ingested] {os.path.basename(f_path)} -> [{intl_sheet}]: {len(cleaned_intl)} rows")
            except Exception as e:
                print(f"[Warning] Failed to read {intl_sheet} from {f_path}: {e}")

    # 合并为统一销售事实表
    df_cn = pd.concat(cn_list, ignore_index=True) if cn_list else clean_cn_data(pd.DataFrame())
    df_intl = pd.concat(intl_list, ignore_index=True) if intl_list else clean_intl_data(pd.DataFrame())
    df_sales = pd.concat([df_cn, df_intl], ignore_index=True) if (cn_list or intl_list) else clean_cn_data(pd.DataFrame())

    if len(df_sales) == 0:
        raise ValueError("未能从输入的数据源文件提取到有效销售明细行，请检查 Sheet 名称与关键表头是否匹配。")

    # 3. 写入临时 DuckDB 文件
    if progress_callback:
        progress_callback("parquet", "正在全量落盘 DuckDB 表结构与高频索引...", 75.0)

    con = duckdb.connect(tmp_db)
    try:
        con.register("df_sales_view", df_sales)
        con.register("df_aux_view", df_aux)

        con.execute(f"""
        CREATE TABLE {DUCKDB_TABLE_SALES} AS SELECT * FROM df_sales_view;
        CREATE TABLE {DUCKDB_TABLE_AUX} AS SELECT * FROM df_aux_view;
        """)

        # 创建高频索引
        con.execute(f"CREATE INDEX idx_sales_ym ON {DUCKDB_TABLE_SALES}(year, month);")
        con.execute(f"CREATE INDEX idx_sales_cat ON {DUCKDB_TABLE_SALES}(product_category);")
        con.execute(f"CREATE INDEX idx_sales_src ON {DUCKDB_TABLE_SALES}(report_source);")
    finally:
        con.close()

    # 4. 自动装载统一 SQL 语义视图 (在原子替换前于 tmp_db 构建完毕，避免只读并发锁死)
    from etl.semantic_views import apply_semantic_views
    apply_semantic_views(db_path=tmp_db, read_only=False)

    # 5. 蓝绿原子替换 (Blue-Green Swap)
    if progress_callback:
        progress_callback("swap", "正在完成蓝绿无缝切库与零宕机装载...", 92.0)

    os.replace(tmp_db, target_db)
    # 同步更新 5 个双轨独立分库 (acb.duckdb, mccb.duckdb, pq.duckdb, atse.duckdb, vf.duckdb)
    export_dual_track_databases(target_db)
    print(f"[ETL Success] Unified Analytics DB updated at {target_db} (Sales: {len(df_sales)} rows [CN: {len(df_cn)}, INTL: {len(df_intl)}], AUX: {len(df_aux)} rows)")

    return {
        "total_rows": len(df_sales),
        "cn_rows": len(df_cn),
        "intl_rows": len(df_intl),
        "aux_rows": len(df_aux),
        "years": sorted(list(set(int(y) for y in df_sales["year"].dropna().unique() if int(y) > 0))) if "year" in df_sales.columns else [],
        "categories": {str(k): int(v) for k, v in df_sales["product_category"].value_counts().to_dict().items()} if "product_category" in df_sales.columns else {}
    }


def export_dual_track_databases(master_db_path: str):
    """
    从主库导出 5 个双轨独立分库 (acb.duckdb, mccb.duckdb, pq.duckdb, atse.duckdb, vf.duckdb)
    确保旧单部门/大类 CLI 运维工具（如 query_sales.py）与 Agent Skills 100% 兼容。
    """
    if not os.path.exists(master_db_path):
        return

    cat_map = {
        "acb": ["框架", "框架类", "ACB"],
        "mccb": ["塑壳", "塑壳类", "MCCB"],
        "pq": ["电能质量", "PQ"],
        "atse": ["双电源", "ATSE"],
        "vf": ["虚拟工厂", "VF", "其它低压类", "其他低压类", "微断类", "微断", "终端类"],
        "mcb": ["虚拟工厂", "VF", "微断", "终端类"]
    }

    try:
        from etl.semantic_views import apply_semantic_views
    except ImportError:
        from semantic_views import apply_semantic_views

    db_dir = os.path.dirname(master_db_path)
    try:
        for dept_code, cat_names in cat_map.items():
            cat_db = os.path.join(db_dir, f"{dept_code}.duckdb")
            cat_tmp = cat_db + ".tmp"
            if os.path.exists(cat_tmp):
                try:
                    os.remove(cat_tmp)
                except Exception:
                    pass

            cats_str = ", ".join([f"'{c}'" for c in cat_names])
            c_out = duckdb.connect(cat_tmp)
            try:
                c_out.execute(f"ATTACH '{master_db_path}' AS master_db (READ_ONLY);")
                c_out.execute(f"CREATE TABLE {DUCKDB_TABLE_SALES} AS SELECT * FROM master_db.{DUCKDB_TABLE_SALES} WHERE product_category IN ({cats_str});")
                c_out.execute(f"CREATE TABLE {DUCKDB_TABLE_AUX} AS SELECT * FROM master_db.{DUCKDB_TABLE_AUX};")
                c_out.execute("DETACH master_db;")
                c_out.execute(f"CREATE INDEX idx_sales_ym ON {DUCKDB_TABLE_SALES}(year, month);")
                c_out.execute(f"CREATE INDEX idx_sales_cat ON {DUCKDB_TABLE_SALES}(product_category);")
                count_res = c_out.execute(f"SELECT COUNT(*) FROM {DUCKDB_TABLE_SALES}").fetchone()[0]
            finally:
                c_out.close()

            apply_semantic_views(db_path=cat_tmp, read_only=False)
            os.replace(cat_tmp, cat_db)
            print(f"[Dual-Track Sync] Category DB exported successfully: {os.path.basename(cat_db)} (Sales: {count_res} rows)")
    except Exception as e:
        print(f"[Warning] Failed to export dual-track category DBs: {e}")


def ensure_fresh_parquet_cache(source_excel: str = None) -> bool:
    """
    检查 Parquet 数据的实时性 (mtime 时间戳对比)。
    如果 Excel 比 Parquet 新，或者 Parquet 不存在，自动重新触发数据校验与 Parquet 原子导出。
    返回 True 表示 Parquet 数据可用且是最新状态。
    """
    try:
        cn_parquets = glob.glob(PARQUET_CN_PATTERN)
        intl_parquets = glob.glob(PARQUET_INTL_PATTERN)

        target_files = [source_excel] if source_excel else get_all_processed_files()

        if not target_files:
            return bool(cn_parquets and intl_parquets)

        latest_excel = max(target_files, key=os.path.getmtime) if target_files else None
        if not latest_excel or not os.path.exists(latest_excel):
            return bool(cn_parquets and intl_parquets)

        excel_mtime = os.path.getmtime(latest_excel)

        needs_rebuild = False
        from config import get_duckdb_path
        target_db = get_duckdb_path()
        if os.path.exists(target_db) and os.path.getmtime(target_db) >= excel_mtime:
            # DuckDB 数据库已是最新的，无需重复重建
            return True

        if not cn_parquets or not intl_parquets:
            needs_rebuild = True
        else:
            cn_mtime = min(os.path.getmtime(p) for p in cn_parquets)
            intl_mtime = min(os.path.getmtime(p) for p in intl_parquets)
            if excel_mtime > cn_mtime or excel_mtime > intl_mtime:
                needs_rebuild = True

        if needs_rebuild:
            print(f"[Auto-Sync] 检测到原始 Excel ('{os.path.basename(latest_excel)}') 已更新且数据库需刷，开始刷新 Parquet 缓存与 DB...")
            run_duckdb_etl(source_excel=latest_excel)
            print("[Auto-Sync] 缓存与 DB 自动更新完成。")
        return True
    except Exception as e:
        print(f"[Auto-Sync Warning] 校验/更新 Parquet 缓存异常: {e}")
        return False


if __name__ == "__main__":
    run_duckdb_etl()

