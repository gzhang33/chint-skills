"""
config_loader.py — 100% 独立便携配置加载器与 56 列标准字典 SSOT (Skill Standalone Edition)

职责：
1. 保证 Skill 100% 自包含与物理隔离，绝对不越界引用外部项目路径。
2. 内置全量 56 列标准 Excel 标题与数据库物理列规范化映射表。
3. 统一管理 Skill 内部存储路径 (SKILL_DIR / "data" / "sales.duckdb")。
"""
from __future__ import annotations
import os
import json
from pathlib import Path
from typing import Dict, Any

# Skill 根目录定位 (自身所在目录 .agents/skills/chint-data-analysis)
SKILL_DIR = Path(__file__).resolve().parent.parent
SKILL_SCRIPTS_DIR = SKILL_DIR / "scripts"
SKILL_DATA_DIR = SKILL_DIR / "data"
SKILL_RESOURCES_DIR = SKILL_DIR / "resources"
SKILL_DUCKDB_PATH = SKILL_DATA_DIR / "sales.duckdb"

# 确保 Skill 数据目录存在
SKILL_DATA_DIR.mkdir(parents=True, exist_ok=True)

# ── 56 列全量标准 Excel 标题到数据库物理字段映射字典 ─────────────────────────
STANDARD_56_COLUMN_MAP: Dict[str, str] = {
    # 基础与地域维度
    "报表来源": "report_source", "数据来源": "report_source", "来源": "report_source",
    "市场": "market_channel", "市场通道": "market_channel", "渠道": "market_channel",
    "产业": "brand_sector", "品牌": "brand_sector",
    "产业分类": "product_industry_category", "产品产业分类": "product_industry_category", # 产业分类（如'低压'）独立映射，绝不污染 product_category
    "业务分类": "biz_category", # 业务分类独立映射，不污染 product_subclass
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
    "通用/专业": "biz_category", "通用专业": "biz_category", "专业/通用": "biz_category",
    "终端客户": "terminal_customer", "最终用户": "terminal_customer", "行业客户": "terminal_customer", "终端用户名称": "terminal_customer",
    "客户名称": "customer_name", "客户": "customer_name", "买方名称": "customer_name", "经销商": "customer_name", "代理商": "customer_name",
    "大客户": "key_account", "KA": "key_account", "行业": "industry", "行业分类": "industry_category",
    
    # 数值指标 (Excel 原生单位均为“元”和“台”，统一映射到基础元单位字段，绝不隐式乘以 10000)
    "发票数量": "raw_sales_qty", "发票数量(台)": "raw_sales_qty", "销售数量": "raw_sales_qty", "开票数量": "raw_sales_qty", "数量": "raw_sales_qty", "发票台数": "raw_sales_qty",
    "本体台数": "invoice_qty_benti", "本体台数(台)": "invoice_qty_benti", "发票数量_本体": "invoice_qty_benti", "本体数量": "invoice_qty_benti",
    # 净额与净收入物理列隔离（双物理列保留，绝不静默合并或取最大值高估）
    "净额（不含税）": "net_amount", "净额（不含税）(元)": "net_amount", "净额": "net_amount", "开票金额": "net_amount",
    "净收入（不含税）": "net_revenue", "净收入（不含税）(元)": "net_revenue", "净收入": "net_revenue",
    "销售净收入": "net_revenue", "销售净收入(元)": "net_revenue", "销售收入": "net_revenue",
    "产品成本（不含税）": "product_cost", "产品成本（不含税）(元)": "product_cost", "产品成本": "product_cost", "成本": "product_cost",
    "毛利额（不含税）": "gross_profit", "毛利额（不含税）(元)": "gross_profit", "毛利额": "gross_profit", "毛利": "gross_profit"
}

_cached_common = None


def load_common_config() -> dict:
    """加载通用映射规则（内置 56 列映射，支持 Skill 本地 JSON 覆盖）"""
    global _cached_common
    if _cached_common is not None:
        return _cached_common

    local_common_json = SKILL_DATA_DIR / "common.json"
    if local_common_json.exists():
        try:
            with open(local_common_json, "r", encoding="utf-8") as f:
                _cached_common = json.load(f)
                return _cached_common
        except Exception:
            pass

    _cached_common = {
        "excel_title_mappings": STANDARD_56_COLUMN_MAP,
        "common_rules": {
            "quarter": {"Q1": [1, 2, 3], "Q2": [4, 5, 6], "Q3": [7, 8, 9], "Q4": [10, 11, 12]}
        }
    }
    return _cached_common


def get_excel_title_mappings() -> Dict[str, str]:
    """获取 56 列标准标题到物理列的映射表"""
    return load_common_config().get("excel_title_mappings", STANDARD_56_COLUMN_MAP)


def get_common_rules() -> Dict[str, Any]:
    """获取通用派生规则配置 (quarter 等)"""
    return load_common_config().get("common_rules", {
        "quarter": {"Q1": [1, 2, 3], "Q2": [4, 5, 6], "Q3": [7, 8, 9], "Q4": [10, 11, 12]}
    })


def get_product_category_rules(category: str | None = None) -> Dict[str, Any]:
    """获取指定产品品类的过滤与映射规则"""
    return {
        "acb": {"name": "框架断路器", "series": ["NXA", "NA1", "NDW1", "NDW2", "NA8G"]},
        "mccb": {"name": "塑壳断路器", "series": ["NXM", "NM1", "NM8", "NM8N", "NXMLE", "NM1LE", "M"]},
        "mcb": {"name": "微型断路器", "series": ["NXB", "DZ47", "DZ158", "NB1", "Ex9B"]},
        "pq": {"name": "电能质量", "series": []},
        "atse": {"name": "双电源", "series": ["NXZ", "NZ7", "NH40"]},
    }.get(str(category).lower() if category else "", {})


def get_skill_duckdb_path() -> Path:
    """获取 Skill 内部独占的 DuckDB 数据库路径"""
    return SKILL_DUCKDB_PATH

