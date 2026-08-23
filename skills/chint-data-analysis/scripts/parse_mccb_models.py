#!/usr/bin/env python3
"""
CHINT Integrated Analytics - MCCB Model Parsing & Query CLI Tool
Path: scripts/parse_mccb_models.py

Usage:
  python3 scripts/parse_mccb_models.py --input "NXMS-160H/4300C 63A"
  python3 scripts/parse_mccb_models.py --file /Users/gianni/Downloads/26年1-7月配电电器合并报表-塑壳.xlsx --sheet 中国区 --limit 1000 --export output.csv
"""

import sys
import os
import argparse
import pandas as pd

# Add project root to sys.path
try:
    from etl.mccb_parser import MCCBModelParser
except ImportError:
    from mccb_parser import MCCBModelParser


def main():
    parser = argparse.ArgumentParser(description="CHINT MCCB Deterministic Model Parser CLI")
    parser.add_argument("--input", "-i", type=str, help="Single model string to parse")
    parser.add_argument("--file", "-f", type=str, help="Path to Excel or CSV file containing material descriptions")
    parser.add_argument("--column", "-c", type=str, default="物料描述", help="Column name containing material descriptions")
    parser.add_argument("--sheet", "-s", type=str, default="中国区", help="Excel sheet name")
    parser.add_argument("--limit", "-n", type=int, default=None, help="Limit number of rows to parse")
    parser.add_argument("--export", "-o", type=str, help="Export parsed results to CSV file")

    args = parser.parse_args()
    engine = MCCBModelParser()

    if args.input:
        res = engine.parse(args.input)
        print(f"\n================ MCCB MODEL PARSE RESULT ================")
        print(f"Original Input   : {res.raw_input}")
        print(f"Clean Model      : {res.clean_model}")
        print(f"Valid / Complete : {'Yes' if res.is_valid else 'No'}")
        print(f"Parse Status     : {res.parse_status}")
        print(f"\n--- Structured Specifications ---")
        for k, v in res.data.items():
            status = res.field_validations.get(k, "-")
            print(f"  {k:<20} : {v:<20} (Status: {status})")
        print(f"=========================================================\n")
        return

    if args.file:
        if not os.path.exists(args.file):
            print(f"Error: File not found at {args.file}")
            sys.exit(1)

        print(f"Loading {args.file} (Sheet: {args.sheet}, Column: {args.column})...")
        if args.file.endswith(".csv"):
            df = pd.read_csv(args.file)
        else:
            df = pd.read_excel(args.file, sheet_name=args.sheet, usecols=[args.column])

        descs = df[args.column].dropna().astype(str).tolist()
        if args.limit:
            descs = descs[:args.limit]

        print(f"Parsing {len(descs):,} items...")
        batch_res = engine.batch_parse(descs)

        print(f"\n================ BATCH PARSE SUMMARY ================")
        print(f"Total Items       : {batch_res['total']:,}")
        print(f"Success Count     : {batch_res['success_count']:,} ({batch_res['success_rate']}%)")
        print(f"Invalid Count     : {batch_res['invalid_count']:,}")
        print(f"Body Breakers     : {batch_res['summary']['body_count']:,}")
        print(f"Accessories       : {batch_res['summary']['accessory_count']:,}")
        print(f"Unknown Series    : {batch_res['summary']['unknown_series_count']:,}")
        print(f"Format Mismatch   : {batch_res['summary']['format_mismatch_count']:,}")
        print(f"=====================================================\n")

        if args.export:
            rows = []
            for r in batch_res["records"]:
                row = {
                    "原始物料描述": r["raw_input"],
                    "清洗型号": r["clean_model"],
                    "解析状态": r["parse_status"],
                    "有效性": "是" if r["is_valid"] else "否",
                    "产品型号/系列": r["data"].get("product_model", ""),
                    "壳架代号": r["data"].get("frame_current", ""),
                    "分断能力": r["data"].get("breaking_capacity", ""),
                    "极数": r["data"].get("pole_count", ""),
                    "附件功能码": r["data"].get("accessory_code", ""),
                    "N极连接方式": r["data"].get("n_pole_type", ""),
                    "额定电流": r["data"].get("rated_current", ""),
                    "操作方式": r["data"].get("operation_method", ""),
                    "属性": r["data"].get("property_type", "")
                }
                rows.append(row)
            out_df = pd.DataFrame(rows)
            out_df.to_csv(args.export, index=False, encoding="utf-8-sig")
            print(f"Successfully exported {len(rows):,} parsed rows to {args.export}")
        return

    parser.print_help()


if __name__ == "__main__":
    main()
