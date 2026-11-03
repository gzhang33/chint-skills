#!/usr/bin/env python3
"""Contract sample: one page per supported archetype, watermarked, no business data.

Covers cover, contents, chapter, ARCH_TABLE (flat and merged headers), the three
retained native charts, and closing. Run it after changing the engine or the
compliance gate; a failure here means the contract is broken.
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path

from chint_pptx_engine import ChintPresentationEngine
from core.output_paths import default_output_dir, ensure_output_path

PAYLOAD = {
    "validation_fixture": True,
    "slides": [
        {"archetype": "ARCH_01_COVER", "title": "契约样例", "subtitle": "仅验证版式，不含业务数据"},
        {"archetype": "ARCH_02_TOC", "items": ["表格页", "多层表头", "图表页", "尾页"]},
        {"archetype": "ARCH_03_CHAPTER", "title": "01 表格页", "subtitle": "ARCH_TABLE"},
        {"archetype": "ARCH_TABLE",
         "title": "标准表格：单层表头 + 隔行浅底",
         "category": "ARCH_TABLE",
         "headers": ["项目", "数值", "占比", "同比"],
         "rows": [["TEST A", "1.00", "25.0%", "+1.0%"],
                  ["TEST B", "2.00", "50.0%", "+2.0%"],
                  ["TEST C", "1.00", "25.0%", "+3.0%"]],
         "align": ["left", "right", "right", "right"],
         "note": "TEST DATA ONLY · 口径说明写在这里。"},
        {"archetype": "ARCH_03_CHAPTER", "title": "02 多层表头", "subtitle": "合并单元格"},
        {"archetype": "ARCH_TABLE",
         "title": "多层表头：跨列合并 + 二级分类",
         "category": "ARCH_TABLE",
         "levels": [2, 1],
         "header_tree": [["区域", "收入", None, "备注"],
                         [None, "亿元", "同比", None]],
         "merge_groups": [{"row": 0, "columns": [1, 2]}],
         "headers": ["区域", "亿元", "同比", "备注"],
         "rows": [["TEST A", "1.00", "+1.0%", "-"],
                  ["TEST B", "2.00", "+2.0%", "-"]],
         "align": ["left", "right", "right", "center"]},
        {"archetype": "ARCH_03_CHAPTER", "title": "03 图表页", "subtitle": "保留的三个原生图表"},
        {"archetype": "ARCH_16_CHART_BAR_TREND",
         "title": "柱状图：分类随时间变化",
         "categories": ["T1", "T2", "T3"],
         "series": [{"name": "TEST", "values": [1.0, 2.0, 3.0]}],
         "summary_bullets": ["TEST DATA ONLY", "仅验证版式", "不含业务结论"]},
        {"archetype": "ARCH_17_CHART_PIE_DONUT",
         "title": "环形图：构成占比",
         "center_metric": "100%",
         "center_label": "TEST",
         "slices": [{"label": "A", "value": 40}, {"label": "B", "value": 35},
                    {"label": "C", "value": 25}]},
        {"archetype": "ARCH_16_RADAR",
         "title": "雷达图：多维度对标",
         "categories": ["D1", "D2", "D3", "D4", "D5"],
         "series": [{"name": "TEST", "values": [3, 4, 2, 5, 3]}],
         "insights": ["TEST DATA ONLY", "仅验证版式"]},
        {"archetype": "ARCH_03_CHAPTER", "title": "04 尾页", "subtitle": "CLOSING"},
        {"archetype": "ARCH_11_CLOSING", "tagline": "契约样例 · 无业务数据",
         "team": "正泰电器 · 产品发展与管理部"},
    ],
}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Generate the current-contract layout sample.")
    default_dir = os.environ.get("CHINT_PPTX_SAMPLE_OUT_DIR") or str(default_output_dir() / "samples")
    parser.add_argument("--output-dir", default=default_dir)
    args = parser.parse_args(argv)
    try:
        out_dir = ensure_output_path(args.output_dir)
    except ValueError as exc:
        parser.error(str(exc))
    out_dir.mkdir(parents=True, exist_ok=True)
    out_pptx = out_dir / "CHINT_CONTRACT_SAMPLE.pptx"
    ChintPresentationEngine().build_from_payload(PAYLOAD, str(out_pptx))
    print(f"Generated contract sample: {out_pptx}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
