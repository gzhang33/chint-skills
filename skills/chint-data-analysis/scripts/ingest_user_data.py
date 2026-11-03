#!/usr/bin/env python3
"""
ingest_user_data.py — PM 自有数据集主动摄入、质量契约校验与 DuckDB 智能增量更新 CLI

使用示例：
  # 1. 默认增量摄入（自动识别年月分区并幂等覆盖，保留历史月份）
  python3 .agents/skills/chint-data-analysis/scripts/ingest_user_data.py --file /path/to/my_data.xlsx

  # 2. 探查预览模式 (Dry-Run)，仅检查 Sheet、表头与列映射，不写数据库
  python3 .agents/skills/chint-data-analysis/scripts/ingest_user_data.py --file /path/to/my_data.xlsx --dry-run

  # 3. 显式指定收入列名 (如指定取“净收入（不含税）”避免取错)
  python3 .agents/skills/chint-data-analysis/scripts/ingest_user_data.py --file /path/to/my_data.xlsx --revenue-col "净收入（不含税）"

  # 4. 显式全量重置替换
  python3 .agents/skills/chint-data-analysis/scripts/ingest_user_data.py --file /path/to/my_data.xlsx --overwrite
"""

import sys
import os
import argparse
from pathlib import Path

# 确保加载 Skill 内部 scripts 目录
CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

try:
    from config_loader import SKILL_DIR, get_skill_duckdb_path
    from ingest_engine import read_and_clean_dataframe, upsert_to_duckdb, inspect_and_preview_file
except ImportError:
    from .config_loader import SKILL_DIR, get_skill_duckdb_path
    from .ingest_engine import read_and_clean_dataframe, upsert_to_duckdb, inspect_and_preview_file


def print_reconciliation_table(reconcile_data: dict):
    """格式化打印对账勾稽核算小结"""
    cross_list = reconcile_data.get("cross_summary", [])
    channel_list = reconcile_data.get("channel_summary", [])
    total_info = reconcile_data.get("total_summary", {})

    print("\n" + "═" * 78)
    print(" 📊 【入库对账小结】市场渠道 × 本体/附件 勾稽对账表")
    print("─" * 78)
    print(f" {'市场渠道':<8} | {'属性类别':<6} | {'有效行数':>8} | {'开票台数':>10} | {'净收入(万元)':>14} | {'毛利(万元)':>12}")
    print("─" * 78)
    for r in cross_list:
        mkt = r["market_channel"]
        prop = r["property_type"]
        rows = f"{r['row_cnt']:,}"
        qty = f"{r['total_qty']:,.0f}"
        rev = f"{r['net_revenue_wanyu']:,.2f}"
        profit = f"{r['profit_wanyu']:,.2f}"
        print(f" {mkt:<8} | {prop:<8} | {rows:>10} | {qty:>12} | {rev:>16} | {profit:>14}")

    print("─" * 78)
    for c in channel_list:
        mkt = f"{c['market_channel']}小计"
        rows = f"{c['row_cnt']:,}"
        qty = f"{c['total_qty']:,.0f}"
        rev = f"{c['net_revenue_wanyu']:,.2f}"
        profit = f"{c['profit_wanyu']:,.2f}"
        print(f" {mkt:<8} | {'全部':<8} | {rows:>10} | {qty:>12} | {rev:>16} | {profit:>14}")

    print("═" * 78)
    tot_rows = f"{total_info.get('total_rows', 0):,}"
    tot_qty = f"{total_info.get('total_qty', 0):,.0f}"
    tot_rev = f"{total_info.get('net_revenue_wanyu', 0):,.2f}"
    tot_profit = f"{total_info.get('profit_wanyu', 0):,.2f}"
    print(f" {'【大盘全量总计】':<12} | {tot_rows:>10} | {tot_qty:>12} | {tot_rev:>16} | {tot_profit:>14}")
    print("═" * 78)


def main():
    parser = argparse.ArgumentParser(
        description="CHINT PM 自有数据集摄入、质量契约校验与 DuckDB 年月增量更新引擎"
    )
    parser.add_argument("--file", "-f", required=True, help="待导入的 Excel/CSV 数据文件路径")
    parser.add_argument("--overwrite", action="store_true", help="显式开启全量替换模式（清空历史并重建，默认执行增量分区幂等更新）")
    parser.add_argument("--dry-run", "--preview", action="store_true", help="探查预览模式：解析 Sheet 与列映射关系，不写 DuckDB 库")
    parser.add_argument("--revenue-col", "-r", default=None, help="显式指定收入列名称（如'净收入（不含税）'或'净额（不含税）'）")
    parser.add_argument("--sheet", "-s", default=None, help="指定 Excel 工作表名称（可选，默认智能探测数据表）")
    parser.add_argument("--category", "-c", default=None, help="指定产品品类（如 ACB, MCCB, MCB，可选）")
    parser.add_argument("--output-db", "-o", default=None, help="自定义 DuckDB 输出路径（默认存储至 Skill 内部 data/sales.duckdb）")

    args = parser.parse_args()

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    input_path = Path(args.file).resolve()
    if not input_path.exists():
        print(f"❌ [Error] 指定的数据文件不存在: {input_path}")
        sys.exit(1)

    if args.output_db:
        target_db = Path(args.output_db).resolve()
    else:
        try:
            target_db = get_skill_duckdb_path()
        except FileNotFoundError as exc:
            print(f"❌ [Error] {exc}")
            sys.exit(1)

    # 1. 若为 Dry-Run 模式，输出探查矩阵并退出
    if args.dry_run:
        print(f"═══ 🔍 启动数据集 Dry-Run 结构探查: {input_path.name} ═══")
        try:
            preview = inspect_and_preview_file(input_path, sheet_name=args.sheet, revenue_col=args.revenue_col)
        except Exception as e:
            print(f"❌ [Error] 探查分析失败: {e}")
            sys.exit(1)

        print(f"• 文件大小: {preview['file_size_mb']} MB")
        print(f"• 探测 Sheet 页清单 ({len(preview['sheets'])} 个):")
        for s in preview['sheets']:
            print(f"   - [{s['sheet_name']}] 表头列数: {len(s['raw_columns'])} | 预览采样行数: {s['sample_rows_count']}")
        
        print("\n• 💰 收入字段候选识别:")
        for r_raw, r_target in preview['revenue_candidates']:
            print(f"   - 原始列: '{r_raw}' ==> 映射物理列: '{r_target}'")

        print(f"\n• 解析有效清洗行数: {preview['total_parsed_rows']:,} 行")
        print("\n• 📋 列映射矩阵 (前 15 项):")
        for m in preview['mapping_matrix'][:15]:
            print(f"   {m['raw_column']:<20} --> {m['mapped_target']}")
        if len(preview['mapping_matrix']) > 15:
            print(f"   ... (剩余 {len(preview['mapping_matrix']) - 15} 列)")

        print("\n✅ Dry-Run 探查完成！未对 DuckDB 进行写盘操作。")
        return

    # 2. 正常摄入与入库流程
    print(f"═══ 🚀 开始摄入 PM 数据集: {input_path.name} ═══")
    print(f"• 数据源路径: {input_path}")
    print(f"• 目标 DuckDB: {target_db}")
    print(f"• 更新模式: {'⚠️ 全量覆盖重置 (--overwrite)' if args.overwrite else '✨ 智能年月分区增量覆盖 (Partition Upsert)'}")
    if args.revenue_col:
        print(f"• 显式指定收入列: {args.revenue_col}")

    # 读取、清洗并执行强契约校验
    try:
        df_clean = read_and_clean_dataframe(
            input_path,
            sheet_name=args.sheet,
            revenue_col=args.revenue_col,
            run_validation=True
        )
        if args.category:
            df_clean["product_category"] = args.category.upper()
    except Exception as e:
        print(f"\n❌ [Error] 数据读取、清洗或契约校验失败:\n   {e}")
        sys.exit(1)

    print(f"• 本次解析有效数据: {len(df_clean):,} 行 (已通过 Pandera/数据质量强契约校验)")

    # 写入 DuckDB
    try:
        summary = upsert_to_duckdb(df_clean, duckdb_path=target_db, overwrite=args.overwrite)
    except Exception as e:
        print(f"\n❌ [Error] 写入 DuckDB 数据库失败: {e}")
        sys.exit(1)

    # 输出摄入总结与对账小结报告
    print("\n" + "═" * 50)
    print("✅ 数据集摄入与 DuckDB 转换成功！")
    print(f"• 执行模式: {summary['mode']}")
    print(f"• 本次导入年月: {', '.join(summary['incoming_partitions'])}")
    if summary['replaced_partitions']:
        print(f"• 幂等覆盖历史年月: {', '.join(summary['replaced_partitions'])}")
    print(f"• 本次写入行数: {summary['incoming_rows']:,} 行")
    print(f"• 数据库总行数: {summary['total_rows_in_db']:,} 行")
    print(f"• 库内年份覆盖: {', '.join(str(y) for y in summary['db_years'])} 年")
    print(f"• 库内月份覆盖: {', '.join(str(m) for m in summary['db_months'])} 月")
    print("═" * 50)

    # 打印对账小结
    if "reconciliation" in summary:
        print_reconciliation_table(summary["reconciliation"])

    print("\n💡 现在可以直接运行 query_sales.py 或 pptx_generator.py 进行多维分析与报告导出！")


if __name__ == "__main__":
    main()
