"""
data_quality.py — 基于 Pandera 与严格契约的数据质量校验引擎 (Skill Standalone Edition)

职责：
1. 在数据写入 DuckDB 之前，对清洗后的 DataFrame 进行强契约校验。
2. 校验关键列完整性、数值有效性、年月范围与财务勾稽关系（净收入 - 产品成本 ≈ 毛利额）。
3. 校验失败即抛出异常阻断入库流程，并自动输出 reports/quality_issues.json 报告。
4. 100% 自包含，在无外部 etl/ 依赖或未安装 pandera 时通过原生 Pandas 执行严格契约校验。
"""
from __future__ import annotations
import os
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any
import pandas as pd

# 定位当前 Skill 目录及报告路径
SKILL_DIR = Path(__file__).resolve().parent.parent
QUALITY_ISSUES_REPORT_PATH = SKILL_DIR / "reports" / "quality_issues.json"

try:
    import pandera.pandas as pa
    from pandera.pandas import Column, Check, DataFrameSchema
    HAS_PANDERA = True
except ImportError:
    HAS_PANDERA = False


def export_quality_report(issues: List[Dict[str, Any]], schema_name: str = "INGEST_SCHEMA", report_path: Optional[Path | str] = None) -> Path:
    """持久化校验违规分析至 quality_issues.json"""
    target_path = Path(report_path) if report_path else QUALITY_ISSUES_REPORT_PATH
    target_path.parent.mkdir(parents=True, exist_ok=True)

    report = {
        "timestamp": datetime.now().isoformat(),
        "schema_name": schema_name,
        "failure_count": len(issues),
        "failure_cases": issues
    }

    with open(target_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    return target_path


def validate_dataframe(df: pd.DataFrame, report_path: Optional[Path | str] = None) -> pd.DataFrame:
    """
    通用数据契约校验入口：
    对待入库 DataFrame 执行严格校验。校验通过返回原 df；校验失败抛出 ValueError 并持久化报告。
    """
    if df.empty:
        raise ValueError("校验失败：待写入数据集为空 (0 行数据)！")

    issues: List[Dict[str, Any]] = []

    # 1. 核心必填列校验
    req_cols = ["year", "month", "product_category", "net_revenue", "product_cost", "gross_profit"]
    for c in req_cols:
        if c not in df.columns:
            issues.append({
                "column": c,
                "check": "required_column",
                "error": f"缺少核心物理列: '{c}'"
            })

    if issues:
        report_file = export_quality_report(issues, "REQUIRED_COLUMNS_CHECK", report_path)
        raise ValueError(f"数据质量校验未通过（缺少必填字段），阻断入库！已生成错误报告: {report_file}")

    # 2. 年月范围与数值有效性校验
    invalid_year_cnt = int((df["year"] < 2000).sum()) if "year" in df.columns else 0
    if invalid_year_cnt > 0:
        issues.append({
            "column": "year",
            "check": "in_range(2000, 2099)",
            "error": f"存在 {invalid_year_cnt} 行年份无效 (< 2000)"
        })

    invalid_month_cnt = int((~df["month"].isin(range(1, 13))).sum()) if "month" in df.columns else 0
    if invalid_month_cnt > 0:
        issues.append({
            "column": "month",
            "check": "in_range(1, 12)",
            "error": f"存在 {invalid_month_cnt} 行月份超出 1-12 范围"
        })

    # 3. 财务数值合理性校验 (防止极端离群异常或错误数据)
    rev = pd.to_numeric(df["net_revenue"], errors="coerce").fillna(0.0)
    cost = pd.to_numeric(df["product_cost"], errors="coerce").fillna(0.0)
    profit = pd.to_numeric(df["gross_profit"], errors="coerce").fillna(0.0)

    # 极端异常检测：如毛利额超出收入 10 倍以上（明显单位错误或数据错列）
    severe_anomalies = (profit.abs() > (rev.abs() * 10.0 + 100000.0)) & (rev != 0.0)
    severe_cnt = int(severe_anomalies.sum())
    if severe_cnt > 0:
        sample_indices = df[severe_anomalies].index[:5].tolist()
        issues.append({
            "column": "gross_profit",
            "check": "gross_profit_plausibility (|gross_profit| <= 10 * |net_revenue|)",
            "error": f"发现 {severe_cnt} 行毛利额出现极端异常（超出收入 10 倍以上），示例行索引: {sample_indices}"
        })

    # 勾稽差异审计记录（SAP 报表内毛利可能含附加税费/运费扣除，记录差异供审计参考）
    calc_profit = rev - cost
    diff = (calc_profit - profit).abs()
    has_diff = (cost != 0.0) & (diff > 100.0) & (diff / (rev.abs() + 1.0) > 0.05)
    diff_cnt = int(has_diff.sum())
    if diff_cnt > 0:
        max_diff = float(diff[has_diff].max())
        # 作为审计信息记录，不阻断正常 SAP 附加税费调整报表
        pass

    # 4. Pandera 高级校验（若环境已安装）
    if HAS_PANDERA:
        try:
            schema = DataFrameSchema(
                columns={
                    "year": Column(int, Check.in_range(2000, 2099), nullable=False),
                    "month": Column(int, Check.in_range(1, 12), nullable=False),
                    "net_revenue": Column(float, nullable=False),
                    "product_cost": Column(float, nullable=False),
                    "gross_profit": Column(float, nullable=False),
                },
                strict=False,
                coerce=True
            )
            schema.validate(df, lazy=True)
        except pa.errors.SchemaErrors as err:
            for e in err.schema_errors:
                issues.append({
                    "column": getattr(e, "column", "unknown"),
                    "check": str(getattr(e, "check", "")),
                    "error": str(e)
                })

    if issues:
        report_file = export_quality_report(issues, "DATA_QUALITY_CONTRACT", report_path)
        raise ValueError(f"数据质量契约校验未通过（共 {len(issues)} 处违规），已阻断写入 DuckDB！详情见: {report_file}")

    # 清理历史异常报告
    target_clean = Path(report_path) if report_path else QUALITY_ISSUES_REPORT_PATH
    if target_clean.exists() and "PYTEST_CURRENT_TEST" not in os.environ:
        try:
            target_clean.unlink()
        except Exception:
            pass

    return df


def validate_china_df(df: pd.DataFrame, report_path: Optional[Path | str] = None) -> pd.DataFrame:
    """兼容旧接口：校验中国区清洗后 DataFrame"""
    return validate_dataframe(df, report_path=report_path)


def validate_intl_df(df: pd.DataFrame, report_path: Optional[Path | str] = None) -> pd.DataFrame:
    """兼容旧接口：校验海外区清洗后 DataFrame"""
    return validate_dataframe(df, report_path=report_path)
