#!/usr/bin/env python3
"""
CHINT Official Presentation & Template Generator
Location: skills/chint-brand-design/scripts/generate_template.py

Dynamic generator for professional CHINT presentation decks (PPTX) and HTML reports,
strictly adhering to the 2026 CHINT Corporate Visual Identity Standards.
"""

import os
import sys
import shutil
import argparse
from typing import List, Dict, Any, Optional

try:
    from chint_theme import (
        CHINT_COLORS,
        CHINT_FONTS,
        CHINT_2026_MATRIX,
        get_template_path,
        get_logo_path,
        hex_to_rgb,
    )
except ImportError:
    from .chint_theme import (
        CHINT_COLORS,
        CHINT_FONTS,
        CHINT_2026_MATRIX,
        get_template_path,
        get_logo_path,
        hex_to_rgb,
    )


def create_clean_prs() -> Any:
    """
    Creates a Presentation object using the 2026 official master layouts,
    with all placeholder slides removed to start with a clean slate.
    """
    from pptx import Presentation
    template_file = get_template_path("chint_2026_template.pptx")
    if not template_file or not os.path.exists(template_file):
        raise FileNotFoundError(f"Official template not found: {template_file}")

    prs = Presentation(template_file)
    # Remove existing slides from the master container
    while len(prs.slides) > 0:
        rId = prs.slides._sldIdLst[0].rId
        prs.part.drop_rel(rId)
        del prs.slides._sldIdLst[0]
    return prs


def add_cover_slide(prs: Any, title: str, subtitle: str) -> Any:
    """Adds a standardized 2026 Cover Slide (Layout 1)."""
    from pptx.util import Pt
    slide = prs.slides.add_slide(prs.slide_layouts[1])
    for shp in slide.shapes:
        if shp.is_placeholder:
            ph_type = shp.placeholder_format.type
            if ph_type == 3 or "标题 1" in shp.name:  # CENTER_TITLE
                shp.text = title
                for p in shp.text_frame.paragraphs:
                    p.font.name = "正泰拓新体"
                    p.font.size = Pt(32)
                    p.font.bold = True
            elif ph_type == 2 or "副标题" in shp.name:  # SUBTITLE / BODY
                shp.text = subtitle
                for p in shp.text_frame.paragraphs:
                    p.font.name = "正泰拓新体"
                    p.font.size = Pt(14)
    return slide


def add_toc_slide(prs: Any, sections: List[str]) -> Any:
    """Adds a 5-card Table of Contents Slide (Layout 2)."""
    from pptx.util import Inches, Pt
    from pptx.dml.color import RGBColor
    from pptx.enum.shapes import MSO_SHAPE

    slide = prs.slides.add_slide(prs.slide_layouts[2])
    # Add 5 structured agenda cards
    top_starts = [1.30, 2.29, 3.28, 4.27, 5.26]
    for idx, sec_text in enumerate(sections[:5]):
        t_pos = top_starts[idx]
        # Outer Card Box
        card = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE,
            Inches(5.02), Inches(t_pos), Inches(6.56), Inches(0.76)
        )
        card.fill.solid()
        card.fill.fore_color.rgb = RGBColor(255, 255, 255)
        card.line.color.rgb = RGBColor(226, 232, 240)

        # Number Badge Box
        num_box = slide.shapes.add_textbox(Inches(5.19), Inches(t_pos + 0.08), Inches(0.68), Inches(0.60))
        p_num = num_box.text_frame.paragraphs[0]
        p_num.text = f"{idx+1:02d}"
        p_num.font.name = "正泰拓新体"
        p_num.font.size = Pt(18)
        p_num.font.bold = True
        p_num.font.color.rgb = RGBColor(30, 80, 230)

        # Text Label Box
        txt_box = slide.shapes.add_textbox(Inches(6.15), Inches(t_pos + 0.12), Inches(5.20), Inches(0.50))
        p_txt = txt_box.text_frame.paragraphs[0]
        p_txt.text = sec_text
        p_txt.font.name = "正泰拓新体"
        p_txt.font.size = Pt(14)
        p_txt.font.color.rgb = RGBColor(25, 25, 25)
    return slide


def add_chapter_slide(prs: Any, chapter_title: str) -> Any:
    """Adds a Chapter Transition Slide (Layout 3)."""
    from pptx.util import Pt
    slide = prs.slides.add_slide(prs.slide_layouts[3])
    for shp in slide.shapes:
        if shp.is_placeholder and (shp.placeholder_format.type == 1 or "标题" in shp.name):
            shp.text = chapter_title
            for p in shp.text_frame.paragraphs:
                p.font.name = "正泰拓新体"
                p.font.size = Pt(28)
                p.font.bold = True
    return slide


def add_content_slide(prs: Any, title: str, subtitle: Optional[str] = None) -> Any:
    """Adds a Content Slide (Layout 8) with clean Header and Logo."""
    from pptx.util import Pt
    slide = prs.slides.add_slide(prs.slide_layouts[8])
    for shp in slide.shapes:
        if shp.is_placeholder and "标题" in shp.name:
            shp.text = title
            for p in shp.text_frame.paragraphs:
                p.font.name = "正泰拓新体"
                p.font.size = Pt(24)
                p.font.bold = True
        elif shp.is_placeholder and "文本" in shp.name:
            shp.text = subtitle if subtitle else ""
            for p in shp.text_frame.paragraphs:
                p.font.name = "正泰拓新体"
                p.font.size = Pt(13)
    return slide


def add_closing_slide(prs: Any, closing_text: str = "感谢观看") -> Any:
    """Adds a Closing Slide (Layout 7)."""
    from pptx.util import Inches, Pt
    from pptx.dml.color import RGBColor
    slide = prs.slides.add_slide(prs.slide_layouts[7])
    txt_box = slide.shapes.add_textbox(Inches(3.40), Inches(2.80), Inches(6.53), Inches(1.20))
    p = txt_box.text_frame.paragraphs[0]
    p.text = closing_text
    p.font.name = "正泰拓新体"
    p.font.size = Pt(36)
    p.font.bold = True
    p.font.color.rgb = RGBColor(255, 255, 255)
    return slide


def generate_html_template(
    output_path: str,
    title: str = "正泰业务分析与决策报告",
    subtitle: str = "CHINT Corporate Executive Report",
) -> str:
    """Generates a responsive HTML report template."""
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
    }}
    .brand-title h1 {{
      font-size: 24px;
      font-weight: 700;
    }}
    .brand-title p {{
      font-size: 13px;
      opacity: 0.9;
      margin-top: 4px;
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
    }}
    .card {{
      background: var(--chint-surface);
      border: 1px solid var(--chint-border);
      border-radius: 6px;
      padding: 20px;
    }}
    .card-title {{
      font-size: 15px;
      font-weight: 700;
      color: var(--chint-text-dark);
      margin-bottom: 12px;
    }}
    footer {{
      text-align: center;
      padding: 24px;
      font-size: 12px;
      color: var(--chint-text-muted);
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
        <div class="card-title">万能式断路器 (ACB) 订货总额</div>
        <p>¥128.4M (+14.6% YoY 稳步增长)</p>
      </div>
      <div class="card">
        <div class="card-title">NXA 系列切换率</div>
        <p>68.2% (+8.5% 达成年度替代目标)</p>
      </div>
      <div class="card">
        <div class="card-title">新能源行业占比</div>
        <p>34.8% (光伏与储能板块驱动)</p>
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


def generate_clean_starter_deck(output_path: str, title: str, subtitle: str) -> str:
    """Generates a clean starter slide deck with Cover, Agenda, and Sample Content."""
    prs = create_clean_prs()
    add_cover_slide(prs, title, subtitle)
    add_toc_slide(prs, [
        "业务与市场背景总览",
        "核心产品架构与技术优势",
        "主力产品系列对比与参数矩阵",
        "重点行业与标杆应用场景",
        "演进规划与落地行动方案",
    ])
    add_content_slide(prs, "业务与市场背景总览", "请在此处构建核心业务观点与数据卡片")
    add_closing_slide(prs, "感谢观看")

    out_dir = os.path.dirname(os.path.abspath(output_path))
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)
    prs.save(output_path)
    return os.path.abspath(output_path)


def main():
    parser = argparse.ArgumentParser(description="CHINT Presentation & Template Generator")
    parser.add_argument(
        "--type",
        choices=["pptx", "html", "all"],
        default="all",
        help="Format to generate ('pptx', 'html', or 'all')",
    )
    parser.add_argument(
        "--outdir",
        default="./dist",
        help="Target directory for generated files",
    )
    parser.add_argument(
        "--title",
        default="正泰低压配电与新能源业务报告",
        help="Main deck title",
    )
    parser.add_argument(
        "--subtitle",
        default="2026 年度经营战略与产品演进方案",
        help="Deck subtitle",
    )
    args = parser.parse_args()

    os.makedirs(args.outdir, exist_ok=True)
    generated = []

    if args.type in ["pptx", "all"]:
        pptx_out = os.path.join(args.outdir, "chint_starter_2026.pptx")
        res = generate_clean_starter_deck(pptx_out, title=args.title, subtitle=args.subtitle)
        generated.append(f"PPTX: {res}")

    if args.type in ["html", "all"]:
        html_out = os.path.join(args.outdir, "chint_report_2026.html")
        res = generate_html_template(html_out, title=args.title, subtitle=args.subtitle)
        generated.append(f"HTML: {res}")

    for g in generated:
        print(f"Generated: {g}")


if __name__ == "__main__":
    main()
