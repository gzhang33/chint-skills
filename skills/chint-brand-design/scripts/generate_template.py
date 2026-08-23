#!/usr/bin/env python3
"""
CHINT Official Template Generator
Location: skills/chint-brand-design/scripts/generate_template.py

Generates standardized CHINT presentation decks (PPTX) and web reports (HTML)
strictly aligned with the 2026 CHINT Corporate Visual Identity Standards.
"""

import os
import sys
import shutil
import argparse
from typing import List, Optional

try:
    from chint_theme import (
        CHINT_COLORS,
        CHINT_FONTS,
        CHINT_2026_MATRIX,
        get_template_path,
        get_logo_path,
        get_font_file,
    )
except ImportError:
    from .chint_theme import (
        CHINT_COLORS,
        CHINT_FONTS,
        CHINT_2026_MATRIX,
        get_template_path,
        get_logo_path,
        get_font_file,
    )


def generate_pptx_deck(
    output_path: str,
    title: str = "正泰低压配电与新能源业务报告",
    subtitle: str = "2026 年度经营战略与产品演进方案",
    sections: Optional[List[str]] = None,
) -> str:
    """
    Generates a standardized 16:9 CHINT corporate slide deck based on the 2026 official master.
    """
    if sections is None:
        sections = [
            "宏观市场与业务大盘总览",
            "万能式断路器 (ACB) 替换推进",
            "新能源与智慧低碳产品线布局",
            "行业客户与重点标杆项目解析",
            "下阶段行动计划与资源保障",
        ]

    template_file = get_template_path("chint_2026_template.pptx")
    out_dir = os.path.dirname(os.path.abspath(output_path))
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    try:
        from pptx import Presentation

        if template_file and os.path.exists(template_file):
            prs = Presentation(template_file)
            
            # 1. Update Title Slide (Slide 1)
            if len(prs.slides) > 0:
                s1 = prs.slides[0]
                for shape in s1.shapes:
                    if shape.has_text_frame:
                        txt = shape.text.strip()
                        if "文档标题" in txt or "标题" in shape.name:
                            shape.text = title
                            for p in shape.text_frame.paragraphs:
                                p.font.name = "正泰拓新体"
                        elif "副标题" in txt or "副标题" in shape.name:
                            shape.text = subtitle
                            for p in shape.text_frame.paragraphs:
                                p.font.name = "正泰拓新体"

            # 2. Update Table of Contents (Slide 2)
            if len(prs.slides) > 1:
                s2 = prs.slides[1]
                # Collect text box content shapes in TOC
                content_boxes = []
                for shape in s2.shapes:
                    if shape.has_text_frame:
                        txt = shape.text.strip()
                        if "单击添加文本" in txt or "单击此处添加" in txt:
                            content_boxes.append(shape)
                
                for idx, box in enumerate(content_boxes):
                    if idx < len(sections):
                        box.text = sections[idx]
                        for p in box.text_frame.paragraphs:
                            p.font.name = "正泰拓新体"

            prs.save(output_path)
            return os.path.abspath(output_path)
        else:
            raise FileNotFoundError("Official master template not found")

    except ImportError:
        # Graceful fallback: copy base template directly if python-pptx is not available
        if template_file and os.path.exists(template_file):
            shutil.copyfile(template_file, output_path)
            return os.path.abspath(output_path)
        raise RuntimeError("Neither python-pptx nor the base PPTX template is available.")


def generate_html_template(
    output_path: str,
    title: str = "正泰业务分析与决策报告",
    subtitle: str = "CHINT Corporate Executive Report",
) -> str:
    """
    Generates a responsive, zero-emoji, high-density HTML corporate report skeleton.
    """
    out_dir = os.path.dirname(os.path.abspath(output_path))
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} - 正泰集团</title>
  <link rel="icon" href="../assets/logos/chint_favicon.ico" type="image/x-icon">
  <style>
    @font-face {{
      font-family: 'CHINTinno';
      src: url('../assets/fonts/CHINTinno-Regular.ttf') format('truetype');
      font-weight: 400;
      font-style: normal;
      font-display: swap;
    }}
    @font-face {{
      font-family: 'CHINTinno';
      src: url('../assets/fonts/CHINTinno-Bold.ttf') format('truetype');
      font-weight: 700;
      font-style: normal;
      font-display: swap;
    }}
    :root {{
      --chint-primary: #1E50E6;
      --chint-primary-dark: #1E50C8;
      --chint-primary-light: #50C8FF;
      --chint-gradient-banner: linear-gradient(90deg, #50C8FF 0%, #1E50C8 100%);
      --chint-bg: #F6F6F6;
      --chint-surface: #FFFFFF;
      --chint-text-dark: #191919;
      --chint-text-soft: #333333;
      --chint-text-muted: #666666;
      --chint-border: #E2E8F0;
      --chint-status-success: #14C832;
      --chint-status-warning: #F59E0B;
      --chint-status-error: #D70A32;
      --font-chint: 'CHINTinno', 'Microsoft YaHei', 'PingFang SC', sans-serif;
    }}
    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}
    body {{
      font-family: var(--font-chint);
      background-color: var(--chint-bg);
      color: var(--chint-text-dark);
      line-height: 1.5;
      -webkit-font-smoothing: antialiased;
    }}
    header {{
      background: var(--chint-gradient-banner);
      color: #FFFFFF;
      padding: 24px 36px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      box-shadow: 0 2px 8px rgba(30, 80, 230, 0.15);
    }}
    .brand-title h1 {{
      font-size: 24px;
      font-weight: 700;
      letter-spacing: -0.02em;
    }}
    .brand-title p {{
      font-size: 13px;
      opacity: 0.9;
      margin-top: 4px;
    }}
    .header-tag {{
      background: rgba(255, 255, 255, 0.18);
      border: 1px solid rgba(255, 255, 255, 0.3);
      padding: 4px 12px;
      border-radius: 4px;
      font-size: 12px;
      font-weight: 600;
    }}
    main {{
      max-width: 1380px;
      margin: 28px auto;
      padding: 0 24px;
    }}
    .grid-container {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
      gap: 20px;
      margin-bottom: 24px;
    }}
    .card {{
      background: var(--chint-surface);
      border: 1px solid var(--chint-border);
      border-radius: 6px;
      padding: 20px;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
    }}
    .card-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-bottom: 1px solid var(--chint-border);
      padding-bottom: 12px;
      margin-bottom: 14px;
    }}
    .card-title {{
      font-size: 15px;
      font-weight: 700;
      color: var(--chint-text-dark);
    }}
    .metric-value {{
      font-size: 28px;
      font-weight: 700;
      color: var(--chint-primary);
      margin: 8px 0;
    }}
    .metric-delta {{
      font-size: 12px;
      font-weight: 600;
      color: var(--chint-status-success);
    }}
    footer {{
      text-align: center;
      padding: 24px;
      font-size: 12px;
      color: var(--chint-text-muted);
      border-top: 1px solid var(--chint-border);
      margin-top: 40px;
    }}
  </style>
</head>
<body>
  <header>
    <div class="brand-title">
      <h1>{title}</h1>
      <p>{subtitle}</p>
    </div>
    <div class="header-tag">CHINT 2026 BRAND DESIGN</div>
  </header>
  <main>
    <div class="grid-container">
      <div class="card">
        <div class="card-header">
          <span class="card-title">万能式断路器 (ACB) 订货总额</span>
        </div>
        <div class="metric-value">¥128.4M</div>
        <div class="metric-delta">+14.6% YoY 稳步增长</div>
      </div>
      <div class="card">
        <div class="card-header">
          <span class="card-title">NXA 系列切换率</span>
        </div>
        <div class="metric-value">68.2%</div>
        <div class="metric-delta">+8.5% 达成年度替代目标</div>
      </div>
      <div class="card">
        <div class="card-header">
          <span class="card-title">新能源行业占比</span>
        </div>
        <div class="metric-value">34.8%</div>
        <div class="metric-delta">光伏与储能板块驱动</div>
      </div>
    </div>
  </main>
  <footer>
    正泰集团股份有限公司 版权所有 &copy; 2026 CHINT Group. All Rights Reserved.
  </footer>
</body>
</html>
"""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    return os.path.abspath(output_path)


def main():
    parser = argparse.ArgumentParser(description="CHINT Template Generator")
    parser.add_argument(
        "--type",
        choices=["pptx", "html", "all"],
        default="all",
        help="Template format to generate ('pptx', 'html', or 'all')",
    )
    parser.add_argument(
        "--outdir",
        default="./dist",
        help="Directory to save generated template files",
    )
    parser.add_argument(
        "--title",
        default="正泰低压配电与新能源业务报告",
        help="Main presentation or report title",
    )
    parser.add_argument(
        "--subtitle",
        default="2026 年度经营战略与产品演进方案",
        help="Presentation or report subtitle",
    )
    args = parser.parse_args()

    os.makedirs(args.outdir, exist_ok=True)
    generated = []

    if args.type in ["pptx", "all"]:
        pptx_out = os.path.join(args.outdir, "chint_presentation_2026.pptx")
        res = generate_pptx_deck(pptx_out, title=args.title, subtitle=args.subtitle)
        generated.append(f"PPTX: {res}")

    if args.type in ["html", "all"]:
        html_out = os.path.join(args.outdir, "chint_report_2026.html")
        res = generate_html_template(html_out, title=args.title, subtitle=args.subtitle)
        generated.append(f"HTML: {res}")

    for g in generated:
        print(f"Generated: {g}")


if __name__ == "__main__":
    main()
