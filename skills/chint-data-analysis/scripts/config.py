"""
config.py — 统一全局配置中心 SSOT (Unified Global Configuration SSOT)

职责：
1. 项目根目录核心配置中心。
2. 集中定义系统数据路径、6 大多维映射规范、DuckDB 部门物理隔离与表头适配器 (HeaderResolver)。
3. 提供配置热重载 (reload_config)。
"""
from __future__ import annotations
import os
import json
import functools
from pathlib import Path

# ===============================================================
# 1. 基础路径与配置文件加载 (User Config & Paths with Hot-Reload)
# ===============================================================
def _find_project_root() -> Path:
    cur = Path(__file__).resolve().parent
    for _ in range(5):
        if (cur / "data").exists() or (cur / "AGENTS.md").exists():
            return cur
        cur = cur.parent
    return Path(__file__).resolve().parent

BASE_DIR = _find_project_root()
USER_CONFIG_JSON_PATH = os.getenv("USER_CONFIG_PATH", os.path.join(BASE_DIR, "config", "user_config.json"))


@functools.lru_cache(maxsize=1)
def load_user_config() -> dict:
    """从 config/user_config.json 加载用户配置；失败时使用内置标准默认值（带 LRU 缓存）"""
    if os.path.exists(USER_CONFIG_JSON_PATH):
        try:
            with open(USER_CONFIG_JSON_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[Config Warning] Failed to load {USER_CONFIG_JSON_PATH}: {e}, using default user config.")

    return {
        "business_rules": {
            "framework_product_categories": ["框架类", "框架"],
            "virtual_factory_categories": ["其它低压类", "其他低压类"],
            "excluded_product_categories": ["隔离开关&刀开关"]
        },
        "excel_sheet_aliases": {
            "sheet_names_cn": ["中国区1-12月", "中国区1-6月", "中国区1-3月", "中国区-正泰", "中国区数据", "中国区源数据", "中国数据", "正泰中国", "正泰中压", "中国区", "中国", "CN"],
            "sheet_names_intl": ["国际1-12月", "国际视图", "国际1-6月", "国际1-3月", "国际数据", "国际源数据", "海外源数据", "海外数据", "海外区数据", "国际", "海外区", "海外"],
            "sheet_name_aux": "辅助数据表",
            "sheet_names_virtual_factory": ["中国区虚拟工厂", "海外区虚拟工厂", "虚拟工厂归档"]
        },
        "data_paths": {
            "data_dir": "data",
            "raw_dir": "data/raw",
            "processed_dir": "data/processed",
            "default_processed_filename": "主配电24-26年销售数据-框架.xlsx",
            "duckdb_filename": "acb.duckdb",
            "reports_dir": "reports",
            "quality_issues_filename": "quality_issues.json"
        },
        "product_code_map": {
            "acb": "acb", "框架类": "acb", "框架": "acb", "ACB": "acb",
            "mccb": "mccb", "塑壳类": "mccb", "塑壳": "mccb", "MCCB": "mccb",
            "pq": "pq", "电能质量": "pq", "PQ": "pq",
            "atse": "atse", "双电源": "atse", "ATSE": "atse",
            "vf": "vf", "虚拟工厂": "vf", "其它低压类": "vf", "其他低压类": "vf", "VF": "vf",
            "mcb": "vf", "微断类": "vf", "微断": "vf", "终端类": "vf"
        },
        "product_configs": {
            "acb": {"qty_unit": "台", "qty_factor": 1.0, "default_template": "acb", "code": "acb", "name": "框架"},
            "mccb": {"qty_unit": "万台", "qty_factor": 0.0001, "default_template": "dashboard", "code": "mccb", "name": "塑壳"},
            "pq": {"qty_unit": "台", "qty_factor": 1.0, "default_template": "dashboard", "code": "pq", "name": "电能质量"},
            "atse": {"qty_unit": "台", "qty_factor": 1.0, "default_template": "dashboard", "code": "atse", "name": "双电源"},
            "vf": {"qty_unit": "万台", "qty_factor": 0.0001, "default_template": "dashboard", "code": "vf", "name": "虚拟工厂"},
            "default": {"qty_unit": "万台", "qty_factor": 0.0001, "default_template": "dashboard", "code": "other", "name": "其他"}
        },
        "excel_header_aliases": {
            "REPORT_SOURCE": ["数据来源", "来源"],
            "BRAND_SRC": ["产业", "品牌来源"],
            "REGION": ["洲区", "区域"],
            "PROVINCE": ["省份", "省"],
            "INVOICE_QTY": ["发票数量", "开票数量", "销量"],
            "NET_INCOME": ["净收入", "销售净收入", "净收入（不含税）", "净额"],
            "PRODUCT_COST": ["产品成本", "销售成本", "成本"],
            "GROSS_MARGIN": ["毛利额", "毛利"],
            "SALES_TEAM": ["销售团队"],
            "GENERAL_PRO": ["通用/专业"],
            "SERIES": ["产品系列", "系列"],
            "PLATFORM": ["产品平台", "平台"],
            "PRODUCT_CLASS": ["产品大类"]
        }
    }


def reload_config() -> dict:
    """清空 LRU 缓存并重新加载 user_config.json 配置文件（实现 Hot-Reload）"""
    load_user_config.cache_clear()
    _init_globals()
    return load_user_config()


PRODUCT_CATEGORY = "acb"
PRODUCT_DISPLAY_NAME = "框架"


def _init_globals():
    global _cfg, _b_rules, _s_aliases, _d_paths, _h_aliases
    global FRAMEWORK_PRODUCT_CATEGORIES, VIRTUAL_FACTORY_CATEGORIES, EXCLUDED_PRODUCT_CATEGORIES
    global SHEET_NAMES_CN, SHEET_NAMES_INTL, SHEET_NAME_AUX, SHEET_NAMES_VIRTUAL_FACTORY
    global DATA_DIR, RAW_DIR, RAW_NEW_DIR, PROCESSED_DIR, DATABASE_DIR, MAPPING_DIR, TEMP_DIR, DEFAULT_PROCESSED_FILENAME, PROCESSED_EXCEL_PATH
    global DEFAULT_DUCKDB_FILENAME, DUCKDB_PATH, UNIFIED_DUCKDB_PATH, ARCHIVE_DIR, DEFAULT_ARCHIVE_FILENAME, ARCHIVE_EXCEL_PATH
    global REPORTS_DIR, QUALITY_ISSUES_FILENAME, QUALITY_ISSUES_REPORT_PATH
    global PRODUCT_HIERARCHY_CN, PRODUCT_HIERARCHY_INTL, INDUSTRY_PROFESSIONAL, REGION_TO_BIG_AREA
    global OVERSEAS_REGIONS, OVERSEAS_TOP_COUNTRIES
    global PRODUCT_CODE_MAP, PRODUCT_CONFIGS, EXCEL_HEADER_ALIASES, ACTIVE_CONFIG
    global REQUIRED_COLS, NUMERIC_COLS, CATEGORY_COLS

    _cfg = load_user_config()
    _b_rules = _cfg.get("business_rules", {})
    _s_aliases = _cfg.get("excel_sheet_aliases", {})
    _d_paths = _cfg.get("data_paths", {})
    _h_aliases = _cfg.get("excel_header_aliases", {})

    FRAMEWORK_PRODUCT_CATEGORIES = _b_rules.get("framework_product_categories", ["框架类", "框架"])
    VIRTUAL_FACTORY_CATEGORIES = _b_rules.get("virtual_factory_categories", ["其它低压类", "其他低压类"])
    EXCLUDED_PRODUCT_CATEGORIES = _b_rules.get("excluded_product_categories", ["隔离开关&刀开关"])

    SHEET_NAMES_CN = _s_aliases.get("sheet_names_cn", ["中国区源数据", "中国区数据", "中国数据"])
    SHEET_NAMES_INTL = _s_aliases.get("sheet_names_intl", ["海外源数据", "海外数据", "海外区数据"])
    SHEET_NAME_AUX = _s_aliases.get("sheet_name_aux", "辅助数据表")
    SHEET_NAMES_VIRTUAL_FACTORY = _s_aliases.get("sheet_names_virtual_factory", ["中国区虚拟工厂", "海外区虚拟工厂", "虚拟工厂归档"])

    global PROJECT_ROOT, DATA_DIR, RAW_DIR, RAW_NEW_DIR, PROCESSED_DIR, DATABASE_DIR, MAPPING_DIR, DEPARTMENTS_DIR, TEMP_DIR, DEFAULT_PROCESSED_FILENAME, PROCESSED_EXCEL_PATH
    global DEFAULT_DUCKDB_FILENAME, DUCKDB_PATH, ARCHIVE_DIR, DEFAULT_ARCHIVE_FILENAME, ARCHIVE_EXCEL_PATH
    global REPORTS_DIR, TEMPLATES_DIR, SESSIONS_DIR, UPLOAD_DIR, SCRIPTS_DATA_DIR, QUALITY_ISSUES_FILENAME, QUALITY_ISSUES_REPORT_PATH

    PROJECT_ROOT = Path(BASE_DIR)
    DATA_DIR = Path(BASE_DIR) / _d_paths.get("data_dir", "data")
    RAW_DIR = Path(BASE_DIR) / _d_paths.get("raw_dir", "data/raw")
    RAW_NEW_DIR = RAW_DIR / "new"
    PROCESSED_DIR = Path(BASE_DIR) / _d_paths.get("processed_dir", "data/processed")
    DATABASE_DIR = DATA_DIR / "database"
    MAPPING_DIR = DATA_DIR / "mapping"
    DEPARTMENTS_DIR = DATA_DIR / "departments"
    TEMP_DIR = Path(BASE_DIR) / "temp"
    REPORTS_DIR = Path(BASE_DIR) / _d_paths.get("reports_dir", "reports")
    TEMPLATES_DIR = Path(BASE_DIR) / "templates"
    SESSIONS_DIR = TEMP_DIR / "sessions"
    UPLOAD_DIR = TEMP_DIR / "uploads"
    SCRIPTS_DATA_DIR = Path(BASE_DIR) / "scripts" / "data"

    DEFAULT_PROCESSED_FILENAME = _d_paths.get("default_processed_filename", "主配电24-26年销售数据-框架.xlsx")
    candidates = [
        PROCESSED_DIR / "acb" / DEFAULT_PROCESSED_FILENAME,
        RAW_DIR / "acb" / "sales_acb.xlsx",
        RAW_DIR / "acb" / DEFAULT_PROCESSED_FILENAME,
    ]
    PROCESSED_EXCEL_PATH = str(candidates[0])
    for cand in candidates:
        if cand.exists():
            PROCESSED_EXCEL_PATH = str(cand)
            break

    DEFAULT_DUCKDB_FILENAME = _d_paths.get("duckdb_filename", "chint_analytics.duckdb")
    DUCKDB_PATH = os.getenv("DUCKDB_PATH", str(DATABASE_DIR / DEFAULT_DUCKDB_FILENAME))
    UNIFIED_DUCKDB_PATH = os.getenv("UNIFIED_DUCKDB_PATH", str(DATABASE_DIR / "chint_analytics.duckdb"))

    ARCHIVE_DIR = Path(BASE_DIR) / _d_paths.get("archive_dir", "data/archive")
    DEFAULT_ARCHIVE_FILENAME = _d_paths.get("archive_filename", "virtual_factory_archive.xlsx")
    ARCHIVE_EXCEL_PATH = str(ARCHIVE_DIR / DEFAULT_ARCHIVE_FILENAME)

    QUALITY_ISSUES_FILENAME = _d_paths.get("quality_issues_filename", "quality_issues.json")
    QUALITY_ISSUES_REPORT_PATH = str(REPORTS_DIR / QUALITY_ISSUES_FILENAME)

    PRODUCT_HIERARCHY_CN = [(item[0], item[1]) for item in _cfg.get("product_hierarchy_cn", [])]
    PRODUCT_HIERARCHY_INTL = [(item[0], item[1]) for item in _cfg.get("product_hierarchy_intl", [])]
    INDUSTRY_PROFESSIONAL = _cfg.get("industry_professional", [])
    REGION_TO_BIG_AREA = _cfg.get("region_to_big_area", {})
    OVERSEAS_REGIONS = _cfg.get("overseas_regions", [])
    OVERSEAS_TOP_COUNTRIES = _cfg.get("overseas_top_countries", [])

    PRODUCT_CODE_MAP = _cfg.get("product_code_map", {
        "acb": "acb", "框架类": "acb", "框架": "acb",
        "mccb": "mccb", "塑壳类": "mccb", "塑壳": "mccb",
        "pq": "pq", "电能质量": "pq", "电能质量类": "pq",
        "atse": "atse", "双电源": "atse", "双电源类": "atse",
        "vf": "vf", "虚拟工厂": "vf", "其它低压类": "vf", "mcb": "vf", "微断类": "vf", "微断": "vf", "终端类": "vf"
    })

    PRODUCT_CONFIGS = _cfg.get("product_configs", {
        "acb": {"qty_unit": "台", "qty_factor": 1.0, "default_template": "acb", "code": "acb"},
        "mccb": {"qty_unit": "万台", "qty_factor": 0.0001, "default_template": "dashboard", "code": "mccb"},
        "pq": {"qty_unit": "台", "qty_factor": 1.0, "default_template": "dashboard", "code": "pq"},
        "atse": {"qty_unit": "台", "qty_factor": 1.0, "default_template": "dashboard", "code": "atse"},
        "vf": {"qty_unit": "万台", "qty_factor": 0.0001, "default_template": "dashboard", "code": "vf"},
        "default": {"qty_unit": "万台", "qty_factor": 0.0001, "default_template": "dashboard", "code": "other"}
    })
    PRODUCT_CONFIGS["框架类"] = PRODUCT_CONFIGS.get("acb", {})
    PRODUCT_CONFIGS["塑壳类"] = PRODUCT_CONFIGS.get("mccb", {})
    EXCEL_HEADER_ALIASES = _h_aliases
    current_code = globals().get("PRODUCT_CATEGORY", "acb")
    ACTIVE_CONFIG = PRODUCT_CONFIGS.get(current_code, PRODUCT_CONFIGS.get("acb", {}))
    UNIT.qty_keep_unit = (ACTIVE_CONFIG.get("qty_unit") == "台")

    REQUIRED_COLS = [
        Col.REPORT_SOURCE, Col.BRAND_SRC, Col.REGION, Col.COUNTRY_NAME,
        Col.PROVINCE, Col.YEAR, Col.MONTH, Col.FACTORY, Col.SALES_ORG,
        Col.INVOICE_QTY, Col.NET_INCOME, Col.PRODUCT_COST, Col.TOTAL_COST,
        Col.GROSS_MARGIN, Col.SALES_TEAM, Col.GENERAL_PRO, Col.SERIES,
        Col.PLATFORM, Col.PRODUCT_CLASS, Col.CUSTOMER_NET_NAME,
        Col.FIXED_MAT_GROUP_DESC, Col.SALES_TEAM_REVISION, Col.SALES_TEAM_CLASS,
        Col.ATTRIBUTE, Col.TERMINAL_CUSTOMER
    ]

    NUMERIC_COLS = [
        Col.INVOICE_QTY, Col.NET_INCOME, Col.PRODUCT_COST,
        Col.TOTAL_COST, Col.GROSS_MARGIN
    ]

    CATEGORY_COLS = [
        Col.REPORT_SOURCE, Col.BRAND_SRC, Col.REGION, Col.COUNTRY_NAME,
        Col.PROVINCE, Col.FACTORY, Col.SALES_ORG, Col.SALES_TEAM,
        Col.GENERAL_PRO, Col.SERIES, Col.PLATFORM, Col.PRODUCT_CLASS
    ]

def get_department_duckdb_path(dept_code: str) -> str:
    """获取指定部门的 DuckDB 物理数据库路径 (如 data/database/acb.duckdb)"""
    dept = resolve_product_code(dept_code)
    if dept in ("all", "全部", "chint", "master", "unified", "common"):
        if "UNIFIED_DUCKDB_PATH" in globals() and os.path.exists(UNIFIED_DUCKDB_PATH):
            return UNIFIED_DUCKDB_PATH
        target_unified = os.path.join(DATABASE_DIR, "chint_analytics.duckdb")
        if os.path.exists(target_unified):
            return target_unified
        if "DUCKDB_PATH" in globals() and os.path.exists(DUCKDB_PATH):
            return DUCKDB_PATH
    target = os.path.join(DATABASE_DIR, f"{dept}.duckdb")
    if not os.path.exists(target):
        cur_file = Path(__file__).resolve()
        if ".agents" in cur_file.parts and "skills" in cur_file.parts:
            # Walk up to project root from skill subfolder
            try:
                skill_root = cur_file.parents[3]
                skill_target = str(skill_root / "data" / "database" / f"{dept}.duckdb")
                if os.path.exists(skill_target):
                    return skill_target
            except IndexError:
                pass
    return target

def get_department_mapping_path(dept_code: str) -> str:
    """获取指定部门的 JSON 映射表路径 (如 data/mapping/acb.json)"""
    dept = resolve_product_code(dept_code)
    return os.path.join(MAPPING_DIR, f"{dept}.json")

def get_department_raw_dir(dept_code: str) -> str:
    """获取指定部门的原始用户上传 Excel 目录 (如 data/raw/acb/)"""
    dept = resolve_product_code(dept_code)
    d_dir = os.path.join(RAW_DIR, dept)
    os.makedirs(d_dir, exist_ok=True)
    return d_dir

def get_department_processed_dir(dept_code: str) -> str:
    """获取指定部门的处理/压缩数据目录 (如 data/processed/acb/)"""
    dept = resolve_product_code(dept_code)
    d_dir = os.path.join(PROCESSED_DIR, dept)
    os.makedirs(d_dir, exist_ok=True)
    return d_dir

def get_department_temp_dir(dept_code: str) -> str:
    """获取指定部门的中间审阅与临时报表输出目录 (如 temp/acb/)"""
    dept = resolve_product_code(dept_code)
    t_dir = os.path.join(TEMP_DIR, dept)
    os.makedirs(t_dir, exist_ok=True)
    return t_dir

class UnitConfig:
    def __init__(self):
        self.amt_to_wan_factor = 0.0001     # 元 → 万元
        self.qty_keep_unit = True           # 框架断路器销量直接保留「台」展示

    @property
    def qty_to_wantai_factor(self) -> float:
        return 1.0 if self.qty_keep_unit else 0.0001


UNIT = UnitConfig()

# ===============================================================
# 2. 系统底层架构规范 (System Tech Specs)
# ===============================================================
DUCKDB_TABLE_SALES = "sales_data"
DUCKDB_TABLE_CN = "china_data"
DUCKDB_TABLE_INTL = "overseas_data"
DUCKDB_TABLE_AUX = "auxiliary_data"

SEMANTIC_VIEW_MONTHLY = "v_sales_monthly"
SEMANTIC_VIEW_DETAILED = "v_sales_detailed"
SEMANTIC_VIEW_CN = "v_china_sales_monthly"
SEMANTIC_VIEW_INTL = "v_overseas_sales_monthly"

PARQUET_PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
PARQUET_CN_PATTERN = os.path.join(PARQUET_PROCESSED_DIR, "*_china_data.parquet")
PARQUET_INTL_PATTERN = os.path.join(PARQUET_PROCESSED_DIR, "*_overseas_data.parquet")

ENABLE_PARQUET_FASTPATH = True
PARQUET_AUTO_SYNC = True

CORE_QUERY_COLUMNS_CN = [
    "report_source", "province", "year", "month", "product_subclass", "property",
    "sales_qty", "net_revenue", "product_cost", "gross_profit",
    "sales_team", "product_series", "product_category", "material_code", "material_desc",
    "_ingested_at", "_source_file"
]

CORE_QUERY_COLUMNS_INTL = [
    "report_source", "continent", "country", "year", "month", "product_subclass", "property",
    "sales_qty", "net_revenue", "product_cost", "gross_profit",
    "product_series", "product_category", "material_code", "material_desc",
    "_ingested_at", "_source_file"
]

AUXILIARY_COLUMNS = [
    "material_code", "material_desc_fixed", "product_manager",
    "property", "province", "region"
]


# ===============================================================
# 3. 动态表头解析器 (HeaderResolver)
# ===============================================================
class Col:
    """
    正泰电气 49 列原始销售报表标准物理列定义与 DuckDB 字段映射 SSOT
    保留全部物理字段定义，供底层 Loader、HeaderResolver 与数据清洗校验统一使用。
    """
    # ── 1. 基础报表与归属组织 ──────────────────────────────
    REPORT_SOURCE = 0           # 报表来源 -> report_source
    BRAND_SRC = 1               # 产业 (品牌来源) -> brand_sector
    BUSINESS_CLASS = 2          # 业务分类 -> biz_category
    REGION = 3                  # 洲区 -> continent
    COUNTRY_CODE = 4            # 国家编码 -> country_code
    COUNTRY_NAME = 5            # 国家名称 -> country_name
    PROVINCE = 6                # 省份 -> province
    YEAR = 7                    # 年份 -> year
    MONTH = 8                   # 月份 -> month
    FACTORY_CODE = 9            # 生产制造单位编码 -> mfg_unit_code
    FACTORY = 10                # 生产制造单位 -> mfg_unit
    SALES_ORG_CODE = 23         # 销售组织编码 -> sales_org_code
    SALES_ORG = 24              # 销售组织 -> sales_org
    SALES_TEAM = 42             # 销售团队 -> sales_team
    SALES_TEAM_REVISION = 53    # 销售团队修订 -> sales_team_rev
    SALES_TEAM_CLASS = 54       # 销售团队分类 -> sales_team_cls
    GENERAL_PRO = 43            # 通用/专业 -> general_or_specialized

    # ── 2. 物料与产品定义 ──────────────────────────────────
    MAT_GROUP_CODE = 11         # 物料组编码 -> material_group_code
    MAT_GROUP_DESC = 12         # 物料组描述 -> material_group_desc
    MAT_CODE = 13               # 物料编码 -> material_code
    MAT_DESC = 14               # 物料描述 -> material_desc
    FIXED_MAT_GROUP_DESC = 49   # 修正物料组描述 -> fixed_mat_group_desc
    SERIES = 44                 # 产品系列 -> product_series
    PLATFORM = 45               # 产品平台 -> product_platform
    PRODUCT_MGMT_TEAM = 46      # 产品管理团队 -> product_manager_team
    PRODUCT_CLASS = 47          # 产品大类 (框架类/塑壳类等) -> product_category
    ATTRIBUTE = 55              # 属性 (本体/附件) -> property / property_type

    # ── 3. 客户与项目信息 ──────────────────────────────────
    CUSTOMER_TYPE = 15          # 客户性质 -> customer_nature
    CUSTOMER_NET_NO = 16        # 网点客户号 -> outlet_customer_no
    CUSTOMER_NET_NAME = 17      # 网点客户名称 -> outlet_customer_name
    CUSTOMER_NO = 18            # 客户号 -> customer_no
    CUSTOMER_NAME = 19          # 客户名称 -> customer_name
    TERMINAL_CUSTOMER = 20      # 终端客户 -> terminal_customer
    PROJECT_CODE = 21           # 项目编号 -> project_no
    PROJECT_NAME = 22           # 项目名称 -> project_name
    INTERNAL_FLAG = 48          # 内配客户标记 -> internal_customer_flag

    # ── 4. 财务与开票指标 ──────────────────────────────────
    POLICY_CLASS = 25           # 新政策大类 -> new_policy_category
    INVOICE_QTY = 26            # 发票数量 -> invoice_qty / sales_qty
    PRICE_BILLING = 27          # 开单价金额 (含税) -> billing_price_amount
    PRICE_SETTLE = 28           # 结算价金额 (含税) -> settlement_price_amount
    NET_AMT = 29                # 净额 (不含税) -> net_amount
    DISCOUNT = 30               # 折让 (不含税) -> discount_amount
    EXPENSE = 31                # 费用 (不含税) -> expense_amount
    NET_INCOME = 32             # 净收入 (不含税) -> net_revenue
    POCKET_PRICE = 33           # 口袋价 (含税) -> pocket_price
    PRODUCT_COST = 34           # 产品成本 (不含税) -> product_cost
    TOTAL_COST = 35             # 总成本 (不含税) -> total_cost
    GROSS_MARGIN = 36           # 毛利额 (不含税) -> gross_profit
    CURRENCY = 37               # 本位币种 -> currency
    FX_RATE = 38                # 汇率 (本币) -> exchange_rate
    INCOME_LOCAL = 39           # 收入 (本币) -> revenue_local_currency
    COST_LOCAL = 40             # 成本 (本币) -> cost_local_currency
    INDUSTRY = 41               # 产品产业分类 -> product_industry_category


_init_globals()


class HeaderResolver:
    """动态表头自适应解析器：自动根据表头名称解析列索引"""
    
    @staticmethod
    def resolve_mapping(headers: list[str]) -> dict[str, int]:
        mapping = {}
        assigned_indices = set()
        header_clean = [str(h).strip().replace("\n", "") for h in headers]
        header_lower = [h.lower() for h in header_clean]
        
        attrs = [attr for attr in dir(Col) if not attr.startswith("_") and isinstance(getattr(Col, attr), int)]

        # Pass 1: 精确匹配
        for col_attr in attrs:
            aliases = EXCEL_HEADER_ALIASES.get(col_attr, [])
            for alias in aliases:
                a_lower = alias.lower()
                for idx, h_low in enumerate(header_lower):
                    if idx not in assigned_indices and a_lower == h_low:
                        mapping[col_attr] = idx
                        assigned_indices.add(idx)
                        break
                if col_attr in mapping:
                    break

        # Pass 2: 子串匹配
        for col_attr in attrs:
            if col_attr in mapping:
                continue
            aliases = EXCEL_HEADER_ALIASES.get(col_attr, [])
            for alias in aliases:
                a_lower = alias.lower()
                for idx, h_low in enumerate(header_lower):
                    if idx not in assigned_indices and a_lower in h_low:
                        mapping[col_attr] = idx
                        assigned_indices.add(idx)
                        break
                if col_attr in mapping:
                    break

        # Pass 3: 静态数字索引兜底
        for col_attr in attrs:
            if col_attr not in mapping:
                default_idx = getattr(Col, col_attr)
                if 0 <= default_idx < len(headers) and default_idx not in assigned_indices:
                    mapping[col_attr] = default_idx
                    assigned_indices.add(default_idx)

        return mapping


# ===============================================================
# 4. 动态产品品类映射与切换逻辑
# ===============================================================
def resolve_product_code(name: str) -> str:
    s = str(name).strip().lower()
    for k, v in PRODUCT_CODE_MAP.items():
        if k in s or s in k:
            return v
    return s


PRODUCT_CATEGORY = "acb"
PRODUCT_DISPLAY_NAME = "框架"


def set_active_product_class(product_class_name: str, display_name: str | None = None):
    global PRODUCT_CATEGORY, PRODUCT_DISPLAY_NAME, ACTIVE_CONFIG
    code = resolve_product_code(product_class_name)
    PRODUCT_CATEGORY = code
    
    if display_name:
        PRODUCT_DISPLAY_NAME = display_name
    else:
        if code == "acb":
            PRODUCT_DISPLAY_NAME = "框架"
        elif code == "mccb":
            PRODUCT_DISPLAY_NAME = "塑壳"
        elif code == "mcb":
            PRODUCT_DISPLAY_NAME = "微断"
        elif code == "pq":
            PRODUCT_DISPLAY_NAME = "电能质量"
        elif code == "atse":
            PRODUCT_DISPLAY_NAME = "双电源"
        elif code == "vf":
            PRODUCT_DISPLAY_NAME = "虚拟工厂"
        else:
            PRODUCT_DISPLAY_NAME = code.upper()

    ACTIVE_CONFIG = PRODUCT_CONFIGS.get(code, PRODUCT_CONFIGS.get(product_class_name, PRODUCT_CONFIGS.get("default", {})))
    UNIT.qty_keep_unit = (ACTIVE_CONFIG.get("qty_unit") == "台")


def get_duckdb_path(product_code: str | None = None) -> str:
    """按部门代码动态精准定位 data/database/{code}.duckdb 物理隔离数据库"""
    code = resolve_product_code(product_code or PRODUCT_CATEGORY or "acb")
    return get_department_duckdb_path(code)


def get_archive_excel_path(product_code: str | None = None) -> str:
    code = resolve_product_code(product_code or PRODUCT_CATEGORY)
    if code in ["acb", "mccb", "mcb"]:
        return os.path.join(ARCHIVE_DIR, f"virtual_factory_archive_{code}.xlsx")
    return ARCHIVE_EXCEL_PATH


def get_quality_issues_path(product_code: str | None = None) -> str:
    code = resolve_product_code(product_code or PRODUCT_CATEGORY)
    if code in ["acb", "mccb", "mcb"]:
        return os.path.join(REPORTS_DIR, f"quality_issues_{code}.json")
    return QUALITY_ISSUES_REPORT_PATH


def month_str_to_int(s: str) -> int:
    """'3月' -> 3,  '03'  -> 3"""
    if isinstance(s, int):
        return s
    s = str(s).strip().rstrip("月")
    return int(s)


def int_to_month_str(m: int) -> str:
    return f"{m}月"
