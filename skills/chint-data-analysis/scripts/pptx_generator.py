"""
pptx_generator.py — PowerPoint 自动化汇报生成引擎

文本框与元素定位指南 (Agent Quick Reference):
关于全量 76 个 Shapes/文本框在各 Slide 上的 ID、名称、坐标及语义功能，
请参阅详细速查手册：docs/pptx_template_shape_map.md
"""
from __future__ import annotations
import os
import sys
from pathlib import Path
from pptx import Presentation
from pptx.chart.data import CategoryChartData

CURRENT_DIR = Path(__file__).resolve().parent

def find_repo_root(start: Path) -> Path:
    cur = start
    for _ in range(6):
        if (cur / "etl").exists() and (cur / "config.py").exists():
            return cur
        if cur.parent == cur:
            break
        cur = cur.parent
    return start.parent

REPO_ROOT = find_repo_root(CURRENT_DIR)
for p in [str(REPO_ROOT), str(REPO_ROOT / "etl"), str(CURRENT_DIR)]:
    if p not in sys.path:
        sys.path.insert(0, p)

import analyzer
try:
    import config
    from config import UNIT, OVERSEAS_TOP_COUNTRIES
except ImportError:
    import config as config
    from config import UNIT, OVERSEAS_TOP_COUNTRIES

# ── 正泰品牌视觉规范与专属字体加载 (CHINT Brand System) ──────────────
try:
    _brand_candidates = [
        os.environ.get("CHINT_BRAND_RESOURCES_DIR"),
        str(Path(__file__).resolve().parent.parent / "resources" / "品牌资产"),
        str(Path(__file__).resolve().parent.parent / "resources"),
        str(Path.home() / "Documents" / "chint" / "resources" / "品牌资产"),
    ]
    _brand_dir = next((d for d in _brand_candidates if d and os.path.exists(d)), None)
    if _brand_dir and _brand_dir not in sys.path:
        sys.path.insert(0, _brand_dir)
    import theme_loader
    BRAND_FONT_NAME = theme_loader.get_font_family("matplotlib")  # "CHINTinno"
    FALLBACK_FONT_NAME = "微软雅黑"
    CHINT_PRIMARY_BLUE = theme_loader.get_brand_colors("chint").get("primary", "#1E50E6")
except Exception:
    BRAND_FONT_NAME = "CHINTinno"
    FALLBACK_FONT_NAME = "微软雅黑"
    CHINT_PRIMARY_BLUE = "#1E50E6"


# ──────────────────────────────────────────────────────────
# 全局 文本框与 Shape 名称定位速查字典 (Agent Quick Registry)
# 详见 docs/pptx_template_shape_map.md
# ──────────────────────────────────────────────────────────
SHAPE_MAP = {
    # Page 2 (Slide Index: 1) KPI 文本框
    "GLOBAL_SALES": "文本框 10",         # 全球总销售额 (万元)
    "CHINA_SALES": "文本框 38",          # 中国区销售额 (万元)
    "CHINA_SALES_YOY": "文本框 39",      # 中国区销售额增长率 ("增长率：-12.6%")
    "CHINA_SALES_SHARE": "文本框 13",    # 中国区销售额占比 ("销售占比：84.8%")
    "OVERSEAS_SALES_SUMMARY": "矩形 6",  # 海外区销售额汇总行
    "GLOBAL_SALES_YOY_BADGE": "椭圆 22",  # 全球销售额同比徽章 ("增长率\n-12.8%")

    "GLOBAL_QTY": "文本框 54",           # 全球总数量 (本体/台)
    "CHINA_QTY": "文本框 70",            # 中国区数量 (本体/台)
    "CHINA_QTY_YOY": "文本框 71",        # 中国区数量增长率 ("增长率：-30.6%")
    "CHINA_QTY_SHARE": "文本框 77",      # 中国区数量占比 ("销售占比：80.5%")
    "OVERSEAS_QTY_SUMMARY": "矩形 76",   # 海外区数量汇总行
    "GLOBAL_QTY_YOY_BADGE": "椭圆 103",   # 全球数量同比徽章 ("增长率\n-29.8%")

    "BRAND_SALES_SPLIT": "文本框 105",   # 销售额正泰 vs 诺雅克拆分
    "BRAND_QTY_SPLIT": "文本框 107",     # 数量正泰 vs 诺雅克拆分
}


def _fmt_amt(val: float | None) -> str:
    if val is None or val != val:  # None or NaN
        return "-"
    return f"{val:,.0f}"


def _fmt_qty(val: float | None) -> str:
    if val is None or val != val:
        return "-"
    if UNIT.qty_keep_unit:
        return f"{val:,.0f}"
    return f"{val:,.1f}"


def _fmt_pct(val: float | None) -> str:
    if val is None or val != val:
        return "-"
    return f"{val:+.1f}%" if val != 0 else "0.0%"


def _fmt_share(val: float | None) -> str:
    if val is None or val != val:
        return "-"
    if abs(val - round(val)) < 0.01:
        return f"{val:.0f}%"
    return f"{val:.1f}%"


def set_run_font_zhengtai(run, font_name=None, font_size=None, bold=None, color_rgb=None, color_theme=None, color_brightness=None):
    """
    Set run font to CHINT brand font ('正泰拓新体' / 'CHINTinno'), ensuring Chinese text, numbers (0-9),
    ASCII letters and symbols are all uniformly rendered in '正泰拓新体' without fallback to DengXian/Arial (正文).
    """
    cjk_font_name = "正泰拓新体"
    latin_font_name = "CHINTinno"

    run.font.name = cjk_font_name
    if font_size is not None:
        run.font.size = font_size
    if bold is not None:
        run.font.bold = bold
    if color_rgb is not None:
        run.font.color.rgb = color_rgb
    elif color_theme is not None:
        run.font.color.theme_color = color_theme
        if color_brightness is not None:
            run.font.color.brightness = color_brightness

    try:
        rPr = run._r.get_or_add_rPr()
        # Force language to zh-CN so PowerPoint evaluates CJK & Latin typeface names under Chinese locale
        rPr.set('lang', 'zh-CN')
        rPr.set('altLang', 'en-US')

        for child in list(rPr):
            if child.tag.endswith('}ea') or child.tag.endswith('}cs') or child.tag.endswith('}latin') or child.tag.endswith('}sym'):
                rPr.remove(child)

        from pptx.oxml import parse_xml
        from pptx.oxml.ns import nsdecls

        ea_elem = parse_xml(f'<a:ea {nsdecls("a")} typeface="{cjk_font_name}"/>')
        latin_elem = parse_xml(f'<a:latin {nsdecls("a")} typeface="{latin_font_name}"/>')
        cs_elem = parse_xml(f'<a:cs {nsdecls("a")} typeface="{cjk_font_name}"/>')
        sym_elem = parse_xml(f'<a:sym {nsdecls("a")} typeface="{cjk_font_name}"/>')
        trailing_tags = ('}hlinkClick', '}hlinkMouseOver', '}extLst')
        first_trailing = next((child for child in rPr if any(child.tag.endswith(t) for t in trailing_tags)), None)
        for elem in (latin_elem, ea_elem, cs_elem, sym_elem):
            if first_trailing is not None:
                first_trailing.addprevious(elem)
            else:
                rPr.append(elem)
    except Exception:
        pass


def set_paragraph_font_zhengtai(p, font_name="正泰拓新体"):
    """
    Ensure paragraph-level default run properties <a:defRPr> override Theme Body Fonts (+mn-lt / +mn-ea).
    """
    try:
        pPr = p._p.get_or_add_pPr()
        pPr.set('lang', 'zh-CN')
        defRPr = pPr.find('{http://schemas.openxmlformats.org/drawingml/2006/main}defRPr')
        from pptx.oxml import parse_xml
        from pptx.oxml.ns import nsdecls
        if defRPr is None:
            defRPr = parse_xml(f'<a:defRPr {nsdecls("a")} lang="zh-CN" altLang="en-US"/>')
            pPr.append(defRPr)
        else:
            defRPr.set('lang', 'zh-CN')
            defRPr.set('altLang', 'en-US')
            for child in list(defRPr):
                if child.tag.endswith('}ea') or child.tag.endswith('}cs') or child.tag.endswith('}latin') or child.tag.endswith('}sym'):
                    defRPr.remove(child)

        ea_elem = parse_xml(f'<a:ea {nsdecls("a")} typeface="正泰拓新体"/>')
        latin_elem = parse_xml(f'<a:latin {nsdecls("a")} typeface="CHINTinno"/>')
        cs_elem = parse_xml(f'<a:cs {nsdecls("a")} typeface="正泰拓新体"/>')
        sym_elem = parse_xml(f'<a:sym {nsdecls("a")} typeface="正泰拓新体"/>')
        trailing_tags = ('}hlinkClick', '}hlinkMouseOver', '}extLst')
        first_trailing = next((child for child in defRPr if any(child.tag.endswith(t) for t in trailing_tags)), None)
        for elem in (latin_elem, ea_elem, cs_elem, sym_elem):
            if first_trailing is not None:
                first_trailing.addprevious(elem)
            else:
                defRPr.append(elem)
    except Exception:
        pass



def update_shape_text_safe(shape, text: str):
    """
    Safely update shape text paragraph by paragraph to preserve formatting.
    If text has multiple lines (split by \n), update paragraph by paragraph.
    Handles shapes and table cells (which have text_frame).
    """
    tf = shape.text_frame
    lines = text.split('\n')

    for p_idx, line in enumerate(lines):
        if p_idx < len(tf.paragraphs):
            p = tf.paragraphs[p_idx]
            # Remove soft breaks (a:br) XML elements from the paragraph to avoid carriage issues
            for child in list(p._p):
                if child.tag.endswith('}br'):
                    p._p.remove(child)
            if len(p.runs) > 0:
                p.runs[0].text = line
                for r in p.runs[1:]:
                    r.text = ""
            else:
                p.text = line
        else:
            p = tf.add_paragraph()
            p.text = line

    # Safely remove any extra paragraphs to prevent empty lines from expanding cell heights
    while len(tf.paragraphs) > len(lines):
        p_to_remove = tf.paragraphs[-1]
        p_element = p_to_remove._p
        p_element.getparent().remove(p_element)


def update_cell_text(cell, text: str, bold: bool | None = None):
    """Write text to cell while keeping its paragraph formatting if possible."""
    tf = cell.text_frame

    # Standardize vertical tabs/soft breaks and newlines to \n
    text = text.replace('\x0b', '\n')
    lines = text.split('\n')

    # Walk up parent chain to find the Table object robustly
    table = None
    curr = cell
    while curr is not None:
        if curr.__class__.__name__ == 'Table' or (hasattr(curr, 'rows') and hasattr(curr, 'columns')):
            table = curr
            break
        curr = getattr(curr, '_parent', None)

    # Track formatting from the first paragraph (if it exists) to reuse for new paragraphs
    font_name = None
    font_size = None
    font_bold = None
    font_italic = None
    color_rgb = None
    color_theme = None
    color_brightness = None
    alignment = None

    original_cell_was_bold = False
    if len(tf.paragraphs) > 0 and len(tf.paragraphs[0].runs) > 0:
        ref_run = tf.paragraphs[0].runs[0]
        font_name = ref_run.font.name
        font_size = ref_run.font.size
        font_bold = ref_run.font.bold
        original_cell_was_bold = bool(font_bold)
        font_italic = ref_run.font.italic
        try:
            if ref_run.font.color.type == 1:
                color_rgb = ref_run.font.color.rgb
            elif ref_run.font.color.type == 2:
                color_theme = ref_run.font.color.theme_color
                color_brightness = ref_run.font.color.brightness
        except Exception:
            pass
        alignment = tf.paragraphs[0].alignment

    # Find r_idx
    r_idx = -1
    if table:
        for idx, row in enumerate(table.rows):
            if cell in row.cells:
                r_idx = idx
                break

    # If the cell is empty, try to find a reference run in the table with 5 layers of fallbacks
    if not font_name:
        from pptx.util import Pt
        ref_run = None
        ref_alignment = None
        row_cells = None
        if table and r_idx >= 0:
            row_cells = table.rows[r_idx].cells

        # Fallback Layer 1: Same row, columns >= 1 (excluding first column product label)
        if row_cells:
            for idx, other in enumerate(row_cells):
                if other is not cell and idx >= 1 and len(other.text_frame.paragraphs) > 0 and len(other.text_frame.paragraphs[0].runs) > 0:
                    ref_run = other.text_frame.paragraphs[0].runs[0]
                    ref_alignment = other.text_frame.paragraphs[0].alignment
                    break
            # Same row fallback: any column
            if not ref_run:
                for other in row_cells:
                    if other is not cell and len(other.text_frame.paragraphs) > 0 and len(other.text_frame.paragraphs[0].runs) > 0:
                        ref_run = other.text_frame.paragraphs[0].runs[0]
                        ref_alignment = other.text_frame.paragraphs[0].alignment
                        break

        # Fallback Layer 2: Other data rows (from bottom to top, column >= 1)
        if not ref_run and table:
            for r in range(len(table.rows) - 1, -1, -1):
                if r < 3 and len(table.rows) > 3:
                    continue
                for c in range(1, len(table.columns)):
                    other = table.cell(r, c)
                    if other is not cell and len(other.text_frame.paragraphs) > 0 and len(other.text_frame.paragraphs[0].runs) > 0:
                        ref_run = other.text_frame.paragraphs[0].runs[0]
                        ref_alignment = other.text_frame.paragraphs[0].alignment
                        break
                if ref_run:
                    break

        # Fallback Layer 3: Label column of other data rows
        if not ref_run and table:
            for r in range(len(table.rows) - 1, -1, -1):
                if r < 3 and len(table.rows) > 3:
                    continue
                other = table.cell(r, 0)
                if other is not cell and len(other.text_frame.paragraphs) > 0 and len(other.text_frame.paragraphs[0].runs) > 0:
                    ref_run = other.text_frame.paragraphs[0].runs[0]
                    ref_alignment = other.text_frame.paragraphs[0].alignment
                    break

        # Fallback Layer 4: Header rows (0, 1, 2)
        if not ref_run and table:
            for r in range(min(3, len(table.rows))):
                for c in range(len(table.columns)):
                    other = table.cell(r, c)
                    if other is not cell and len(other.text_frame.paragraphs) > 0 and len(other.text_frame.paragraphs[0].runs) > 0:
                        ref_run = other.text_frame.paragraphs[0].runs[0]
                        ref_alignment = other.text_frame.paragraphs[0].alignment
                        break
                if ref_run:
                    break

        # Fallback Layer 5: Extract properties or apply absolute defaults
        if ref_run:
            font_name = ref_run.font.name or BRAND_FONT_NAME
            font_size = ref_run.font.size
            font_bold = ref_run.font.bold
            font_italic = ref_run.font.italic
            try:
                if ref_run.font.color.type == 1:
                    color_rgb = ref_run.font.color.rgb
                elif ref_run.font.color.type == 2:
                    color_theme = ref_run.font.color.theme_color
                    color_brightness = ref_run.font.color.brightness
            except Exception:
                pass
            alignment = ref_alignment
        else:
            font_name = BRAND_FONT_NAME
            font_size = Pt(9.5)
            font_bold = False
            font_italic = False

    # Force styling consistency:
    # 1. Bold: 正常数据行统一取消加粗，仅在明确传参、表头行或高亮小查/汇总行保留加粗
    HIGHLIGHT_ROW_LABELS = {"汇总", "专业产品", "通用产品", "行业业务", "渠道业务", "行业", "渠道", "合计", "TOP10合计"}
    if bold is not None:
        font_bold = bold
    else:
        row_label = ""
        if table and r_idx >= 0:
            row_label = table.rows[r_idx].cells[0].text.strip()
        if row_label in HIGHLIGHT_ROW_LABELS:
            font_bold = True
        elif r_idx < 2 and original_cell_was_bold:
            font_bold = True
        else:
            font_bold = False

    # 2. Font Size: Force uniform font size (9.0pt for 13-column tables, 9.5pt for others) for all data rows to prevent large font bleeding and row height stretching
    from pptx.util import Pt
    is_data_row = False
    if table:
        if len(table.columns) >= 12:
            if r_idx >= 3:
                is_data_row = True
        else:
            if r_idx >= 1:
                is_data_row = True

    if is_data_row:
        if len(table.columns) >= 12:
            if not font_size or font_size > Pt(9.2):
                font_size = Pt(9.0)
        else:
            if not font_size:
                font_size = Pt(9.5)

    # 3. Alignment: Force center alignment for empty/missing values displayed as '-'
    if text.strip() == "-":
        from pptx.enum.text import PP_ALIGN
        alignment = PP_ALIGN.CENTER

    # 4. Color: Force blue/light-blue colors to normal black to avoid highlighted numbers
    if color_rgb:
        if color_rgb[2] > 150 and color_rgb[0] < 100:
            from pptx.dml.color import RGBColor
            color_rgb = RGBColor(0, 0, 0)
            color_theme = None

    # Write each line to its own paragraph
    for p_idx, line in enumerate(lines):
        if p_idx < len(tf.paragraphs):
            p = tf.paragraphs[p_idx]
            # Remove soft breaks (a:br) XML elements from the paragraph to avoid carriage issues
            for child in list(p._p):
                if child.tag.endswith('}br'):
                    p._p.remove(child)
            if len(p.runs) > 0:
                p.runs[0].text = line
                for r in p.runs[1:]:
                    r.text = ""
            else:
                p.text = line
        else:
            p = tf.add_paragraph()
            p.text = line

        # Apply formatting to the first run of the paragraph
        if len(p.runs) > 0:
            run = p.runs[0]
            target_font_name = BRAND_FONT_NAME
            set_run_font_zhengtai(run, font_name=target_font_name, font_size=font_size, bold=font_bold, color_rgb=color_rgb, color_theme=color_theme, color_brightness=color_brightness)
            if font_italic is not None:
                run.font.italic = font_italic
        if alignment is not None:
            p.alignment = alignment

    # Safely remove any extra paragraphs beyond the number of text lines
    while len(tf.paragraphs) > len(lines):
        p_to_remove = tf.paragraphs[-1]
        p_element = p_to_remove._p
        p_element.getparent().remove(p_element)


class PPTXGenerator:
    def __init__(self, excel_path: str, template_path: str, year: int = 2026, prev_year: int = 2025, months: list[int] | None = None):
        self.excel_path = excel_path
        self.template_path = template_path
        self.year = year
        self.prev_year = prev_year
        self.months = months or [1, 2, 3]
        self.last_month = self.months[-1]
        
        # 加载 / 校验 Locator Map (优先从模板目录读取 shape_locator_map.json)
        self.locator_map = {}
        t_dir = Path(template_path).parent
        for map_candidate in [t_dir / "shape_locator_map_acb.json", t_dir / "shape_locator_map.json"]:
            if map_candidate.exists():
                try:
                    with open(map_candidate, "r", encoding="utf-8") as f:
                        self.locator_map = json.load(f)
                    break
                except Exception:
                    pass

        # 模板表格行高快照：{(slide_idx, shape_name): [row0_h, row1_h, ...]}（EMU）
        self._tmpl_row_heights: dict[tuple[int, str], list[int]] = {}
        # 几何锁快照：{(slide_idx, shape_name): (left, top, width, height)}（EMU）
        self._tmpl_geom: dict[tuple[int, str], tuple[int, int, int, int]] = {}
        # 文本框边距与换行快照：{(slide_idx, shape_name): (margin_l, margin_r, margin_t, margin_b, word_wrap)}
        self._tmpl_margins: dict[tuple[int, str], tuple[int, int, int, int, bool | None]] = {}
        # 表格列宽快照：{(slide_idx, shape_name): [col0_w, col1_w, ...]}（EMU）
        self._tmpl_col_widths: dict[tuple[int, str], list[int]] = {}
        try:
            _prs = Presentation(self.template_path)
            def _snapshot_shape(s_idx, shp):
                self._tmpl_geom[(s_idx, shp.name)] = (int(shp.left), int(shp.top), int(shp.width), int(shp.height))
                if shp.has_text_frame:
                    tf = shp.text_frame
                    self._tmpl_margins[(s_idx, shp.name)] = (
                        int(tf.margin_left), int(tf.margin_right), int(tf.margin_top), int(tf.margin_bottom), tf.word_wrap
                    )
                if shp.has_table:
                    self._tmpl_row_heights[(s_idx, shp.name)] = [
                        int(row.height) for row in shp.table.rows
                    ]
                    self._tmpl_col_widths[(s_idx, shp.name)] = [
                        int(col.width) for col in shp.table.columns
                    ]
                if shp.shape_type == 6:  # GroupShape
                    for sub in shp.shapes:
                        _snapshot_shape(s_idx, sub)

            for s_idx, slide in enumerate(_prs.slides):
                for shp in slide.shapes:
                    _snapshot_shape(s_idx, shp)
        except Exception as e:
            print(f"[WARN] 读取模板几何快照失败：{e}，将跳过几何锁还原步骤")

    def generate(self, output_path: str):
        prs = Presentation(self.template_path)

        # 一次性预加载所有 DataFrame
        self._dfs = analyzer.load_all_for_ppt(
            self.excel_path, self.year, self.months, self.prev_year
        )

        # 动态判定模板是否包含封面页 (Cover Page)，自适应兼容 6 页与 7 页模版
        has_cover = len(prs.slides) >= 7
        offset = 1 if has_cover else 0

        print(f"[PPT-GEN] Starting slide filling (has_cover={has_cover}, offset={offset})...")

        # Slide 1 (或 Slide 0): 2.1 全球总览
        print("[PPT-GEN] Filling Slide 1 Overview...")
        self._fill_slide_overview(prs.slides[0 + offset])

        # Slide 2 (或 Slide 1): 2.2 中国区分产品
        print("[PPT-GEN] Filling Slide 2 Product CN...")
        self._fill_slide_product_cn(prs.slides[1 + offset])

        # Slide 3 (或 Slide 2): 2.3 中国区分行业/区域
        print("[PPT-GEN] Filling Slide 3 Industry Region CN...")
        self._fill_slide_industry_region_cn(prs.slides[2 + offset])

        # Slide 4 (或 Slide 3): 2.4 海外分产品
        print("[PPT-GEN] Filling Slide 4 Product INTL...")
        self._fill_slide_product_intl(prs.slides[3 + offset])

        # Slide 5 (或 Slide 4): 2.5 海外分区域/国家
        print("[PPT-GEN] Filling Slide 5 Region Country INTL...")
        self._fill_slide_region_country_intl(prs.slides[4 + offset])

        # Slide 6 (或 Slide 5): 2.5 产品毛利分析
        print("[PPT-GEN] Filling Slide 6 Margin...")
        self._fill_slide_margin(prs.slides[5 + offset])

        # 动态更新所有幻灯片的“数据截至”描述与单位以及表格表头月份
        for s_idx, slide in enumerate(prs.slides):
            self._update_dateline_and_units(slide)
            for shape in slide.shapes:
                if shape.has_table:
                    if s_idx == (5 + offset) and shape.name == "表格 12":
                        continue
                    self._update_table_headers(shape.table)

            # Prevent textbox collisions on the slide
            self._avoid_slide_textbox_collisions(slide)

        # 全局确保所有普通数据行的单元格不含错误加粗 (bold = False)
        HIGHLIGHT_ROW_LABELS = {"汇总", "专业产品", "通用产品", "行业业务", "渠道业务", "行业", "渠道", "合计", "TOP10合计"}
        for s_idx, slide in enumerate(prs.slides):
            for shape in slide.shapes:
                if shape.has_table:
                    tbl = shape.table
                    for r_idx, row in enumerate(tbl.rows):
                        label = row.cells[0].text.strip()
                        # 如果不是表头行且不是需要高亮的小计/汇总/类别行，强行取消 bold 属性
                        if r_idx >= 2 and label not in HIGHLIGHT_ROW_LABELS:
                            for cell in row.cells:
                                for p in cell.text_frame.paragraphs:
                                    for r in p.runs:
                                        r.font.bold = False

        # 全局自适应替换产品名称与标题 (如 框架/ACB -> 塑壳/MCCB 或 微断/MCB)
        self._replace_category_names_globally(prs)

        # 精确恢复模板原始行高
        if self._tmpl_row_heights:
            for s_idx, slide in enumerate(prs.slides):
                for shape in slide.shapes:
                    if shape.has_table:
                        key = (s_idx, shape.name)
                        snap = self._tmpl_row_heights.get(key)
                        if snap:
                            self._restore_template_row_heights(shape.table, snap)

        # ── 几何锁：保存前强制还原所有 Shapes/文本框/图表/表格的位置、尺寸、列宽，锁定框架结构 ──
        self._lock_all_shape_geometry(prs)

        # 全局统一应用“正泰拓新体”字体
        self._apply_font_globally(prs, "正泰拓新体")

        try:
            prs.save(output_path)
            print(f"[OK] PowerPoint report successfully generated: {output_path}")
            return output_path
        except PermissionError:
            import sys
            print(f"[WARNING] 无法保存到 {output_path}，文件可能已被 Microsoft PowerPoint 打开并锁定。")
            alt_path = output_path.replace(".pptx", "_new.pptx")
            try:
                prs.save(alt_path)
                print(f"[OK] 已将报告保存至备用路径: {alt_path}")
                print(f"[IMPORTANT] 请关闭 PowerPoint 中的旧文件以解除锁定，并手动使用新生成的 {alt_path} 文件。")
                return alt_path
            except Exception as e:
                print(f"[ERROR] 备用路径保存也失败: {e}")
                raise

    def _replace_tags_in_shape(self, shape, tags_map: dict[str, str]):
        if not shape.has_text_frame:
            return
        tf = shape.text_frame
        for p in tf.paragraphs:
            p_text = "".join(r.text for r in p.runs) if len(p.runs) > 0 else p.text
            if not p_text:
                continue

            has_tag = False
            for tag in tags_map:
                if tag in p_text:
                    has_tag = True
                    break
            if not has_tag:
                continue

            if len(p.runs) > 0:
                for r in p.runs:
                    if not r.text:
                        continue
                    new_r_text = r.text
                    for tag, replacement in tags_map.items():
                        new_r_text = new_r_text.replace(tag, replacement)
                    r.text = new_r_text
            else:
                new_p_text = p.text
                for tag, replacement in tags_map.items():
                    new_p_text = new_p_text.replace(tag, replacement)
                p.text = new_p_text

    # ── Slide 0: 全球总览 ──
    def _fill_slide_overview(self, slide):
        import config
        title_text = f"3.1 {self.year}年1-{self.last_month}月全球{config.PRODUCT_DISPLAY_NAME}类产品运营分析"
        
        title_shape = slide.shapes.title if slide.shapes.title else None
        if not title_shape:
            for shape in slide.shapes:
                if shape.has_text_frame and ("标题" in shape.name or "Title" in shape.name.lower()):
                    title_shape = shape
                    break
        if title_shape:
            t_p0 = title_shape.text_frame.paragraphs[0]
            if len(t_p0.runs) >= 4:
                t_p0.runs[0].text = f"3.1 {self.year}"
                t_p0.runs[1].text = "年"
                t_p0.runs[2].text = f"1-{self.last_month}"
                t_p0.runs[3].text = f"月全球{config.PRODUCT_DISPLAY_NAME}类产品运营分析"
            else:
                update_shape_text_safe(title_shape, title_text)

        # Fetch overview metrics from analyzer
        metrics = analyzer.overview_global_comprehensive(
            excel_path=self.excel_path,
            year=self.year,
            months=self.months,
            prev_year=self.prev_year
        )

        qty_unit = "台" if UNIT.qty_keep_unit else "万台"

        # ---- 方案B：直接按 shape.name 定位 KPI 文本框写入 Excel 计算值（不依赖占位符） ----
        F = UNIT.amt_to_wan_factor
        Q = UNIT.qty_to_wantai_factor

        def sh(a, b):
            try:
                return _fmt_share(a / b * 100) if (a is not None and b) else ""
            except Exception:
                return ""

        # 金额（万元）
        g_sales = _fmt_amt(metrics['global_sales'] * F)
        cn_sales = _fmt_amt(metrics['cn_sales'] * F)
        intl_sales = _fmt_amt(metrics['intl_sales'] * F)
        chint_sales = _fmt_amt(metrics['chint_sales'] * F)
        noark_sales = _fmt_amt(metrics['noark_sales'] * F)
        # 数量（台）
        g_qty = _fmt_qty(metrics['global_qty'] * Q)
        cn_qty = _fmt_qty(metrics['cn_qty'] * Q)
        intl_qty = _fmt_qty(metrics['intl_qty'] * Q)
        chint_qty = _fmt_qty(metrics['chint_qty'] * Q)
        noark_qty = _fmt_qty(metrics['noark_qty'] * Q)
        # 同比（带 %）
        cn_sy = _fmt_pct(metrics['yoy_cn_sales'])
        intl_sy = _fmt_pct(metrics['yoy_intl_sales'])
        cn_qy = _fmt_pct(metrics['yoy_cn_qty'])
        intl_qy = _fmt_pct(metrics['yoy_intl_qty'])
        chint_sy = _fmt_pct(metrics['chint_ys'])
        noark_sy = _fmt_pct(metrics['noark_ys'])
        chint_qy = _fmt_pct(metrics['chint_yq'])
        noark_qy = _fmt_pct(metrics['noark_yq'])
        # 占比（带 %）
        cn_ss = sh(metrics['cn_sales'], metrics['global_sales'])
        intl_ss = sh(metrics['intl_sales'], metrics['global_sales'])
        cn_qs = sh(metrics['cn_qty'], metrics['global_qty'])
        intl_qs = sh(metrics['intl_qty'], metrics['global_qty'])
        chint_ss = sh(metrics['chint_sales'], metrics['global_sales'])
        noark_ss = sh(metrics['noark_sales'], metrics['global_sales'])
        chint_qs = sh(metrics['chint_qty'], metrics['global_qty'])
        noark_qs = sh(metrics['noark_qty'], metrics['global_qty'])

        # Reference run for copying theme color and formatting to new paragraphs
        ref_run = None
        for s in slide.shapes:
            if s.name in ["文本框 105", "文本框 107"]:
                if s.has_text_frame and len(s.text_frame.paragraphs) > 0 and len(s.text_frame.paragraphs[0].runs) > 0:
                    ref_run = s.text_frame.paragraphs[0].runs[0]
                    break

        def update_brand_paragraph(p, brand_name, val, yoy, share, is_qty=False):
            unit = "台" if is_qty else "万元"
            yoy_clean = yoy.replace('%', '')
            share_clean = share.replace('%', '')
            
            new_text = f"{brand_name} {val}{unit}    同比{yoy_clean}%     占比{share_clean}%"
            
            if len(p.runs) > 0:
                p.runs[0].text = new_text
                for r in p.runs[1:]:
                    r.text = ""
            else:
                p.text = new_text
                if ref_run and len(p.runs) > 0:
                    p.runs[0].font.name = ref_run.font.name
                    p.runs[0].font.size = ref_run.font.size
                    p.runs[0].font.bold = ref_run.font.bold
                    p.runs[0].font.italic = ref_run.font.italic
                    try:
                        if ref_run.font.color.type == 1:
                            p.runs[0].font.color.rgb = ref_run.font.color.rgb
                        elif ref_run.font.color.type == 2:
                            p.runs[0].font.color.theme_color = ref_run.font.color.theme_color
                            p.runs[0].font.color.brightness = ref_run.font.color.brightness
                    except Exception:
                        pass

        def update_growth_rate_shape(shape, yoy_val):
            from pptx.util import Pt
            p = shape.text_frame.paragraphs[0]
            if len(p.runs) >= 2:
                p.runs[0].text = "增长率："
                set_run_font_zhengtai(p.runs[0], font_name="正泰拓新体")
                p.runs[1].text = yoy_val
                set_run_font_zhengtai(p.runs[1], font_name="正泰拓新体", font_size=Pt(14))
                for r in p.runs[2:]:
                    r.text = ""
            elif len(p.runs) == 1:
                p.runs[0].text = "增长率："
                set_run_font_zhengtai(p.runs[0], font_name="正泰拓新体")
                r1 = p.add_run()
                r1.text = yoy_val
                set_run_font_zhengtai(r1, font_name="正泰拓新体", font_size=Pt(14))
            else:
                p.text = "增长率："
                set_run_font_zhengtai(p.runs[0], font_name="正泰拓新体")
                r1 = p.add_run()
                r1.text = yoy_val
                set_run_font_zhengtai(r1, font_name="正泰拓新体", font_size=Pt(14))

        def set_kpi(shape_name, texts):
            shape = None
            for s in slide.shapes:
                if s.name == shape_name:
                    shape = s
                    break
            if shape is None or not shape.has_text_frame:
                print(f"  [overview] 未找到 KPI 形状 {shape_name!r}，跳过")
                return
            runs = []
            for p_ in shape.text_frame.paragraphs:
                set_paragraph_font_zhengtai(p_)
                for r in p_.runs:
                    runs.append(r)
            for idx, r in enumerate(runs):
                r.text = texts[idx] if idx < len(texts) else ""
                set_run_font_zhengtai(r, font_name="正泰拓新体")

        def set_kpi_brand(shape_name, chint_val, chint_yoy, chint_share, noark_val, noark_yoy, noark_share, is_qty=False):
            shape = None
            for s in slide.shapes:
                if s.name == shape_name:
                    shape = s
                    break
            if shape is None or not shape.has_text_frame:
                print(f"  [overview] 未找到 KPI 形状 {shape_name!r}，跳过")
                return
            tf = shape.text_frame
            while len(tf.paragraphs) < 2:
                tf.add_paragraph()
            update_brand_paragraph(tf.paragraphs[0], "正泰", chint_val, chint_yoy, chint_share, is_qty)
            update_brand_paragraph(tf.paragraphs[1], "诺雅克", noark_val, noark_yoy, noark_share, is_qty)

        # 销售额区
        set_kpi("文本框 10", [g_sales, "万元"])
        set_kpi("文本框 38", [cn_sales, "", "万元"])
        set_kpi("文本框 39", ["增长率：", cn_sy.replace('%', ''), "%"])
        set_kpi("文本框 13", ["销售占比：", cn_ss])
        set_kpi("矩形 6", [
            "海外洲区总计：", intl_sales, "万元", "     ", "总增长率：",
            intl_sy + "      ", "销售占比：", intl_ss.replace('%', ''), "%"])
        # 数量区
        set_kpi("文本框 54", [g_qty, qty_unit])
        set_kpi("文本框 70", [cn_qty, qty_unit])
        set_kpi("文本框 71", ["增长率：", cn_qy])
        set_kpi("矩形 76", [
            "海外洲区总计：", intl_qty, qty_unit, "     ", "总增长率：",
            intl_qy + "      ", "占比：", intl_qs.replace('%', ''), "%"])
        set_kpi("文本框 77", ["销售占比：", cn_qs.replace('%', ''), "%"])
        # 正泰/诺雅克（销售额）
        set_kpi_brand("文本框 105", chint_sales, chint_sy, chint_ss, noark_sales, noark_sy, noark_ss, is_qty=False)
        # 正泰/诺雅克（数量）
        set_kpi_brand("文本框 107", chint_qty, chint_qy, chint_qs, noark_qty, noark_qy, noark_qs, is_qty=True)

        # ── 方案A：固化 5 海外洲区数据（此前由一次性脚本写入，重生成会回退）──
        # 统一用 T01 region_metrics 从明细求和，杜绝双源 / 回退
        dfs = getattr(self, "_dfs", None)
        if dfs is not None:
            cn_ytd = dfs.get('cn_ytd')
            intl_ytd = dfs.get('intl_ytd')
            cn_prev_ytd = dfs.get('cn_prev_ytd')
            intl_prev_ytd = dfs.get('intl_prev_ytd')
            gs = metrics['global_sales']
            gq = metrics['global_qty']

            # 模板布局顺序（决策2：排除 埃及合资工厂 / 大客户业务部）
            OVERSEAS_REGION_ORDER = ["欧洲区", "亚太区", "西亚非洲区", "北美区", "拉美洲区"]
            # 5 海外洲区 → 组合名 → (销售额文本框, 增长率文本框)
            REGION_SALES_GROUPS = {
                "欧洲区": ("组合 17", "文本框 36", "文本框 37"),
                "亚太区": ("组合 19", "文本框 24", "文本框 25"),
                "西亚非洲区": ("组合 28", "文本框 33", "文本框 40"),
                "北美区": ("组合 41", "文本框 45", "文本框 46"),
                "拉美洲区": ("组合 47", "文本框 51", "文本框 52"),
            }
            REGION_QTY_GROUPS = {
                "欧洲区": ("组合 69", "文本框 101", "文本框 102"),
                "亚太区": ("组合 72", "文本框 96", "文本框 97"),
                "西亚非洲区": ("组合 73", "文本框 91", "文本框 92"),
                "北美区": ("组合 74", "文本框 86", "文本框 87"),
                "拉美洲区": ("组合 75", "文本框 81", "文本框 82"),
            }

            def _find_in_container(container, name):
                for s in container.shapes:
                    if s.name == name:
                        return s
                return None

            for region in OVERSEAS_REGION_ORDER:
                rm = analyzer.region_metrics(cn_ytd, intl_ytd, cn_prev_ytd, intl_prev_ytd, region, gs, gq)
                # 销售额组
                g_name, v_name, gw_name = REGION_SALES_GROUPS[region]
                grp = _find_in_container(slide, g_name)
                if grp is not None:
                    val_shape = _find_in_container(grp, v_name)
                    if val_shape is not None:
                        sales_val = rm.get('sales')
                        sales_text = _fmt_amt(sales_val * F) + "万元" if (sales_val is not None and sales_val == sales_val) else "-"
                        update_shape_text_safe(val_shape, sales_text)
                    
                    gr_shape = _find_in_container(grp, gw_name)
                    if gr_shape is not None:
                        yoy_val = rm.get('yoy_sales')
                        if yoy_val is not None and yoy_val == yoy_val:
                            yoy_text = _fmt_pct(yoy_val)
                            update_growth_rate_shape(gr_shape, yoy_text)
                        else:
                            update_shape_text_safe(gr_shape, "-")

                # 数量组
                g_name2, v_name2, gw_name2 = REGION_QTY_GROUPS[region]
                grp2 = _find_in_container(slide, g_name2)
                if grp2 is not None:
                    val_shape2 = _find_in_container(grp2, v_name2)
                    if val_shape2 is not None:
                        qty_val = rm.get('qty')
                        qty_text = _fmt_qty(qty_val * Q) + qty_unit if (qty_val is not None and qty_val == qty_val) else "-"
                        update_shape_text_safe(val_shape2, qty_text)
                    
                    gr_shape2 = _find_in_container(grp2, gw_name2)
                    if gr_shape2 is not None:
                        yoy_qty = rm.get('yoy_qty')
                        if yoy_qty is not None and yoy_qty == yoy_qty:
                            yoy_text = _fmt_pct(yoy_qty)
                            update_growth_rate_shape(gr_shape2, yoy_text)
                        else:
                            update_shape_text_safe(gr_shape2, "-")

            # 全球总量增长率徽章（椭圆 22 全球销售额同比 / 椭圆 103 全球数量同比 / 组合 7 / 组合 66）
            def update_ellipse_badge(shape_name, yoy_pct_str):
                shape = None
                for s in slide.shapes:
                    if s.name == shape_name:
                        shape = s
                        break
                if shape is not None and shape.has_text_frame:
                    tf = shape.text_frame
                    while len(tf.paragraphs) < 2:
                        tf.add_paragraph()
                    p0 = tf.paragraphs[0]
                    if len(p0.runs) > 0:
                        p0.runs[0].text = "增长率"
                        for r in p0.runs[1:]:
                            r.text = ""
                    else:
                        p0.text = "增长率"
                    
                    p1 = tf.paragraphs[1]
                    if len(p1.runs) > 0:
                        p1.runs[0].text = yoy_pct_str
                        for r in p1.runs[1:]:
                            r.text = ""
                    else:
                        p1.text = yoy_pct_str

            update_ellipse_badge("椭圆 22", _fmt_pct(metrics.get('yoy_global_sales')))
            update_ellipse_badge("椭圆 103", _fmt_pct(metrics.get('yoy_global_qty')))

            for badge_name, yoy_val in [("组合 7", metrics.get('yoy_global_sales')), ("组合 66", metrics.get('yoy_global_qty'))]:
                g = _find_in_container(slide, badge_name)
                if g is not None:
                    for sub in g.shapes:
                        if sub.has_text_frame and '增长率' in sub.text_frame.text:
                            update_shape_text_safe(sub, f"增长率\n{_fmt_pct(yoy_val)}")
                            break

        # Update Trend Chart
        chart_shape = None
        for shape in slide.shapes:
            if shape.has_chart:
                chart_shape = shape
                break
        
        if chart_shape:
            # 展示当前季度及之前的所有月份
            chart_months = list(range(1, self.last_month + 1))
            from analyzer import get_monthly_region_trend
            trend_df = get_monthly_region_trend(self.excel_path, year=self.year, months=chart_months, prev_year=self.prev_year)
            chart = chart_shape.chart
            
            # Direct updating of Excel cells and XML cache to prevent python-pptx from destroying 
            # custom properties like secondary axis, accent colors, and data label positioning / manual layout.
            import openpyxl
            import io
            
            # 1. Update embedded Excel workbook
            try:
                workbook_part = chart.part.chart_workbook
                xlsx_blob = workbook_part.xlsx_part.blob
                wb = openpyxl.load_workbook(io.BytesIO(xlsx_blob))
                ws = wb.active
                
                # Clear old rows in worksheet
                for r in range(2, 30):
                    for c in range(1, 20):
                        ws.cell(row=r, column=c).value = None

                # Write categories
                for idx, m in enumerate(chart_months):
                    ws.cell(row=1, column=idx + 2).value = f"{m}月"
                    
                series_names = ['中国区', '欧洲区', '西亚非洲区', '亚太区', '北美区', '拉美洲区', '中国区增长率', '海外增长率', '总增长率']
                series_values = {}
                
                for s_idx, name in enumerate(series_names):
                    ws.cell(row=s_idx + 2, column=1).value = name
                    if name == '中国区增长率':
                        values = [v / 100.0 if (v is not None and v == v) else 0.0 for v in trend_df['China_YoY']]
                    elif name == '海外增长率':
                        values = [v / 100.0 if (v is not None and v == v) else 0.0 for v in trend_df['Overseas_YoY']]
                    elif name == '总增长率':
                        values = [v / 100.0 if (v is not None and v == v) else 0.0 for v in trend_df['Total_YoY']]
                    elif name == '西亚非洲区':
                        values = [round(v) if (v is not None and v == v) else 0 for v in trend_df['西亚非洲区']]
                    elif name == '拉美洲区':
                        values = [round(v) if (v is not None and v == v) else 0 for v in trend_df['拉美洲区']]
                    else:
                        values = [round(v) if (v is not None and v == v) else 0 for v in trend_df[name]]
                        
                    series_values[s_idx] = values
                    
                    # Write to worksheet
                    for val_idx, val in enumerate(values):
                        ws.cell(row=s_idx + 2, column=val_idx + 2).value = val
                        
                # Save workbook back
                out_io = io.BytesIO()
                wb.save(out_io)
                workbook_part.xlsx_part._blob = out_io.getvalue()
            except ValueError as ve:
                print(f"[INFO] 图表数据簿为外部链接，跳过更新嵌入 Excel 仅更新 XML 缓存: {ve}")
                series_names = ['中国区', '欧洲区', '西亚非洲区', '亚太区', '北美区', '拉美洲区', '中国区增长率', '海外增长率', '总增长率']
                series_values = {}
                for s_idx, name in enumerate(series_names):
                    if name == '中国区增长率':
                        values = [v / 100.0 if (v is not None and v == v) else 0.0 for v in trend_df['China_YoY']]
                    elif name == '海外增长率':
                        values = [v / 100.0 if (v is not None and v == v) else 0.0 for v in trend_df['Overseas_YoY']]
                    elif name == '总增长率':
                        values = [v / 100.0 if (v is not None and v == v) else 0.0 for v in trend_df['Total_YoY']]
                    elif name == '西亚非洲区':
                        values = [round(v) if (v is not None and v == v) else 0 for v in trend_df['西亚非洲区']]
                    elif name == '拉美洲区':
                        values = [round(v) if (v is not None and v == v) else 0 for v in trend_df['拉美洲区']]
                    else:
                        values = [round(v) if (v is not None and v == v) else 0 for v in trend_df[name]]
                    series_values[s_idx] = values
            
            # 2. Update XML Cache and expand to len(chart_months)
            namespaces = {'c': 'http://schemas.openxmlformats.org/drawingml/2006/chart'}
            
            # 需求1：移除大客户业务部相关数据及图例
            from lxml import etree
            for ser_node in list(chart._element.findall('.//c:ser', namespaces)):
                ser_xml = etree.tostring(ser_node, encoding='utf-8').decode('utf-8')
                if '大客户' in ser_xml:
                    ser_node.getparent().remove(ser_node)
                    
            series_elements = chart._element.findall('.//c:ser', namespaces)
            
            # Calculate end column letter
            end_col_idx = len(chart_months) + 1  # e.g., B is 2, G is 7
            letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            end_col_letter = letters[end_col_idx - 1]
            
            # Helper to replace formula range end column
            import re
            def update_formula(f_node, col_letter):
                if f_node is not None and f_node.text:
                    f_node.text = re.sub(r'\$[A-Z]+\$(\d+)$', f'${col_letter}$\\1', f_node.text)
            
            from lxml import etree
            
            for s_idx, ser in enumerate(series_elements):
                if s_idx >= len(series_values):
                    continue
                # A. Update Categories Cache
                cat_node = ser.find('c:cat', namespaces)
                if cat_node is not None:
                    # Update formula
                    f_node = cat_node.find('.//c:f', namespaces)
                    update_formula(f_node, end_col_letter)
                    
                    # Rebuild strCache
                    str_cache = cat_node.find('.//c:strCache', namespaces)
                    if str_cache is not None:
                        pt_count = str_cache.find('c:ptCount', namespaces)
                        if pt_count is not None:
                            pt_count.set('val', str(len(chart_months)))
                        # Clear existing pt
                        for pt in str_cache.findall('c:pt', namespaces):
                            str_cache.remove(pt)
                        # Add new pt
                        ext_lst = str_cache.find('c:extLst', namespaces)
                        for idx, m in enumerate(chart_months):
                            pt = etree.Element('{http://schemas.openxmlformats.org/drawingml/2006/chart}pt')
                            pt.set('idx', str(idx))
                            v = etree.SubElement(pt, '{http://schemas.openxmlformats.org/drawingml/2006/chart}v')
                            v.text = f"{m}月"
                            if ext_lst is not None:
                                ext_lst.addprevious(pt)
                            else:
                                str_cache.append(pt)
                            
                # B. Update Values Cache
                val_node = ser.find('c:val', namespaces)
                if val_node is None:
                    val_node = ser.find('c:yVal', namespaces)
                    
                if val_node is not None:
                    # Update formula
                    f_node = val_node.find('.//c:f', namespaces)
                    update_formula(f_node, end_col_letter)
                    
                    # Rebuild numCache
                    num_cache = val_node.find('.//c:numCache', namespaces)
                    if num_cache is not None:
                        pt_count = num_cache.find('c:ptCount', namespaces)
                        if pt_count is not None:
                            pt_count.set('val', str(len(chart_months)))
                        # Clear existing pt
                        for pt in num_cache.findall('c:pt', namespaces):
                            num_cache.remove(pt)
                        # Add new pt
                        ext_lst = num_cache.find('c:extLst', namespaces)
                        series_vals = series_values[s_idx]
                        for idx, val in enumerate(series_vals):
                            pt = etree.Element('{http://schemas.openxmlformats.org/drawingml/2006/chart}pt')
                            pt.set('idx', str(idx))
                            v = etree.SubElement(pt, '{http://schemas.openxmlformats.org/drawingml/2006/chart}v')
                            v.text = str(val)
                            if ext_lst is not None:
                                ext_lst.addprevious(pt)
                            else:
                                num_cache.append(pt)
                            
            # 3. Format Data Labels on Series that already have them
            for s_idx, series in enumerate(chart.series):
                if s_idx >= len(series_values):
                    continue
                ser_el = series_elements[s_idx]
                has_dlbls = ser_el.find('{http://schemas.openxmlformats.org/drawingml/2006/chart}dLbls') is not None
                if has_dlbls:
                    from pptx.util import Pt
                    if "增长率" in series.name:
                        series.data_labels.number_format = '0%'
                        
                        from pptx.dml.color import RGBColor
                        from pptx.enum.chart import XL_DATA_LABEL_POSITION
                        
                        for p_idx, pt in enumerate(series.points):
                            dl = pt.data_label
                            dl.font.size = Pt(12)  # Set size to 12pt
                            dl.font.bold = True
                            
                            # Retrieve values to prevent overlaps
                            try:
                                val_cn = chart.series[6].values[p_idx] if len(chart.series) > 6 else None
                                val_os = chart.series[7].values[p_idx] if len(chart.series) > 7 else None
                                val_tot = chart.series[8].values[p_idx] if len(chart.series) > 8 else None
                            except Exception:
                                val_cn, val_os, val_tot = None, None, None
                                
                            if "中国" in series.name:
                                dl.font.color.rgb = RGBColor(23, 190, 207)  # Light Blue
                                dl.position = XL_DATA_LABEL_POSITION.BELOW  # China sinks down
                            elif "海外" in series.name:
                                dl.font.color.rgb = RGBColor(44, 160, 44)   # Green
                                dl.position = XL_DATA_LABEL_POSITION.ABOVE  # Overseas floats up
                            elif "总" in series.name or "综合" in series.name:
                                dl.font.color.rgb = RGBColor(255, 165, 0)  # Orange/Yellow
                                if val_tot is not None and val_cn is not None and val_os is not None:
                                    if (val_cn < val_tot < val_os) or (val_os < val_tot < val_cn):
                                        dl.position = XL_DATA_LABEL_POSITION.RIGHT
                                    elif val_tot >= max(val_cn, val_os):
                                        dl.position = XL_DATA_LABEL_POSITION.ABOVE
                                    else:
                                        dl.position = XL_DATA_LABEL_POSITION.BELOW
                                else:
                                    dl.position = XL_DATA_LABEL_POSITION.RIGHT
                    else:
                        series.data_labels.number_format = '#,##0'
                        for pt in series.points:
                            dl = pt.data_label
                            dl.font.size = Pt(12)
            
            # 动态更新图表标题中的产品类别
            import config
            if chart.has_title:
                tf = chart.chart_title.text_frame
                for p in tf.paragraphs:
                    for r in p.runs:
                        if "塑壳" in r.text:
                            r.text = r.text.replace("塑壳", config.PRODUCT_CATEGORY)
            
            # 4. Explicitly configure legend position and layout
            from pptx.enum.chart import XL_LEGEND_POSITION
            chart.has_legend = True
            chart.legend.position = XL_LEGEND_POSITION.TOP
            chart.legend.include_in_layout = False


    def _fill_slide_product_cn(self, slide):
        import config
        title_text = f"2.2 {config.PRODUCT_DISPLAY_NAME}产品运营分析 – 分产品（中国区）"
        title_shape = slide.shapes.title if slide.shapes.title else None
        if not title_shape:
            for shape in slide.shapes:
                if shape.has_text_frame and ("标题" in shape.name or "Title" in shape.name.lower()):
                    title_shape = shape
                    break
        if title_shape:
            update_shape_text_safe(title_shape, title_text)

        table = None
        for shape in slide.shapes:
            if shape.has_table and len(shape.table.columns) >= 8:
                table = shape.table
                break
        if not table:
            return

        # 需求2：第2页产品类别排序：汇总, 专业产品, 9系列, 8系列, 5系列, E系列, P系列, T系列, H系列, 通用产品, 昆仑, 1系列, 其它；删除青峰
        slide2_order = [
            "汇总", "专业产品", "9系列", "8系列", "5系列",
            "E系列", "P系列", "T系列", "H系列", "通用产品",
            "昆仑", "1系列", "其它"
        ]

        # 移除多余表格行（如原青峰行）
        while len(table.rows) > len(slide2_order) + 3:
            tr = table.rows[len(table.rows) - 1]._tr
            tr.getparent().remove(tr)

        metrics = analyzer.product_china_comprehensive_ppt(self.excel_path, self.year, self.months, self.prev_year, dfs=self._dfs)

        for idx, label in enumerate(slide2_order):
            r_idx = idx + 3
            if r_idx < len(table.rows):
                update_cell_text(table.rows[r_idx].cells[0], label)
                row_data = self._get_combined_row_data(metrics, label, is_slide_cn=True)

                # Write YTD and share data (9 columns)
                update_cell_text(table.rows[r_idx].cells[1], _fmt_amt(row_data.get('sales_ytd') * UNIT.amt_to_wan_factor if row_data.get('sales_ytd') is not None else None))
                update_cell_text(table.rows[r_idx].cells[2], _fmt_pct(row_data.get('sales_ytd_yoy')))
                update_cell_text(table.rows[r_idx].cells[3], _fmt_share(row_data.get('sales_share_prev')))
                update_cell_text(table.rows[r_idx].cells[4], _fmt_share(row_data.get('sales_share')))

                update_cell_text(table.rows[r_idx].cells[5], _fmt_qty(row_data.get('qty_ytd') * UNIT.qty_to_wantai_factor if row_data.get('qty_ytd') is not None else None))
                update_cell_text(table.rows[r_idx].cells[6], _fmt_pct(row_data.get('qty_ytd_yoy')))
                update_cell_text(table.rows[r_idx].cells[7], _fmt_share(row_data.get('qty_share_prev')))
                update_cell_text(table.rows[r_idx].cells[8], _fmt_share(row_data.get('qty_share')))

    # ── Slide 4: 海外分产品 ──
    def _fill_slide_product_intl(self, slide):
        import config
        title_text = f"2.4 {config.PRODUCT_DISPLAY_NAME}产品运营分析 – 分产品（海外）"
        title_shape = slide.shapes.title if slide.shapes.title else None
        if not title_shape:
            for shape in slide.shapes:
                if shape.has_text_frame and ("标题" in shape.name or "Title" in shape.name.lower()):
                    title_shape = shape
                    break
        if title_shape:
            update_shape_text_safe(title_shape, title_text)

        table = None
        for shape in slide.shapes:
            if shape.has_table and len(shape.table.columns) >= 8:
                table = shape.table
                break
        if not table:
            return

        # 需求4：第4页海外产品顺序：汇总, 9系列, 8系列, NXA, 1系列, 其他
        slide4_order = [
            "汇总", "9系列", "8系列", "NXA", "1系列", "其他"
        ]

        # 删除多余表格行
        while len(table.rows) > len(slide4_order) + 3:
            tr = table.rows[len(table.rows) - 1]._tr
            tr.getparent().remove(tr)

        metrics = analyzer.product_intl_comprehensive_ppt(self.excel_path, self.year, self.months, self.prev_year, dfs=self._dfs)

        for idx, label in enumerate(slide4_order):
            r_idx = idx + 3
            if r_idx < len(table.rows):
                update_cell_text(table.rows[r_idx].cells[0], label)
                row_data = self._get_combined_row_data(metrics, label, is_slide_cn=False)

                update_cell_text(table.rows[r_idx].cells[1], _fmt_amt(row_data.get('sales_ytd') * UNIT.amt_to_wan_factor if row_data.get('sales_ytd') is not None else None))
                update_cell_text(table.rows[r_idx].cells[2], _fmt_pct(row_data.get('sales_ytd_yoy')))
                update_cell_text(table.rows[r_idx].cells[3], _fmt_share(row_data.get('sales_share_prev')))
                update_cell_text(table.rows[r_idx].cells[4], _fmt_share(row_data.get('sales_share')))

                update_cell_text(table.rows[r_idx].cells[5], _fmt_qty(row_data.get('qty_ytd') * UNIT.qty_to_wantai_factor if row_data.get('qty_ytd') is not None else None))
                update_cell_text(table.rows[r_idx].cells[6], _fmt_pct(row_data.get('qty_ytd_yoy')))
                update_cell_text(table.rows[r_idx].cells[7], _fmt_share(row_data.get('qty_share_prev')))
                update_cell_text(table.rows[r_idx].cells[8], _fmt_share(row_data.get('qty_share')))

    # ── Slide 3: 中国区分行业/区域 ──
    def _fill_slide_industry_region_cn(self, slide):
        title_text = f"2.3 产品运营分析 – 分行业（中国区）"
        title_shape = slide.shapes.title if slide.shapes.title else None
        if not title_shape:
            for shape in slide.shapes:
                if shape.has_text_frame and ("标题" in shape.name or "Title" in shape.name.lower()):
                    title_shape = shape
                    break
        if title_shape:
            update_shape_text_safe(title_shape, title_text)

        table = None
        for shape in slide.shapes:
            if shape.has_table and len(shape.table.columns) >= 8:
                table = shape.table
                break
        if not table:
            return

        metrics = analyzer.industry_region_china_comprehensive_ppt(self.excel_path, self.year, self.months, self.prev_year, dfs=self._dfs)

        # 1. 行业板块（5-10行）按 2026年销售占比 降序排序
        industries = ['发电与新能源业务', '信息与通信业务', '电网业务', '能源与工业业务', '交通与运输业务', '基础设施业务']
        sorted_industries = sorted(industries, key=lambda k: metrics.get(k, {}).get('sales_share') or -99999.0, reverse=True)

        # 2. 区域板块（12-21行）按 2026年销售占比 降序排序
        regions = ['长三角', '北部', '苏皖', '华中', '大湾区', '西南', '西北', '京津冀', '东北', '科创业务']
        sorted_regions = sorted(regions, key=lambda k: metrics.get(k, {}).get('sales_share') or -99999.0, reverse=True)

        for r_idx in range(3, len(table.rows)):
            if r_idx == 3:
                key = "汇总"
            elif r_idx == 4:
                key = "专业市场"
                update_cell_text(table.rows[r_idx].cells[0], "行业业务")
            elif 5 <= r_idx <= 10:
                key = sorted_industries[r_idx - 5]
                update_cell_text(table.rows[r_idx].cells[0], key)
            elif r_idx == 11:
                key = "通用市场"
                update_cell_text(table.rows[r_idx].cells[0], "渠道业务")
            elif 12 <= r_idx <= 21:
                key = sorted_regions[r_idx - 12]
                update_cell_text(table.rows[r_idx].cells[0], key)
            else:
                continue

            row_data = metrics.get(key, {})

            update_cell_text(table.rows[r_idx].cells[1], _fmt_amt(row_data.get('sales_ytd') * UNIT.amt_to_wan_factor if row_data.get('sales_ytd') is not None else None))
            update_cell_text(table.rows[r_idx].cells[2], _fmt_pct(row_data.get('sales_ytd_yoy')))
            update_cell_text(table.rows[r_idx].cells[3], _fmt_share(row_data.get('sales_share_prev')))
            update_cell_text(table.rows[r_idx].cells[4], _fmt_share(row_data.get('sales_share')))

            update_cell_text(table.rows[r_idx].cells[5], _fmt_qty(row_data.get('qty_ytd') * UNIT.qty_to_wantai_factor if row_data.get('qty_ytd') is not None else None))
            update_cell_text(table.rows[r_idx].cells[6], _fmt_pct(row_data.get('qty_ytd_yoy')))
            update_cell_text(table.rows[r_idx].cells[7], _fmt_share(row_data.get('qty_share_prev')))
            update_cell_text(table.rows[r_idx].cells[8], _fmt_share(row_data.get('qty_share')))

        # 需求3：第3页表格最后一行颜色渲染异常，参照normal行样式调整
        if len(table.rows) > 21:
            last_row = table.rows[21]
            for cell in last_row.cells:
                tcPr = cell._tc.get_or_add_tcPr()
                for sf in tcPr.findall('{http://schemas.openxmlformats.org/drawingml/2006/main}solidFill'):
                    tcPr.remove(sf)
                if tcPr.find('{http://schemas.openxmlformats.org/drawingml/2006/main}noFill') is None:
                    from lxml import etree
                    tcPr.append(etree.Element('{http://schemas.openxmlformats.org/drawingml/2006/main}noFill'))
                for p in cell.text_frame.paragraphs:
                    for r in p.runs:
                        r.font.bold = False

    # ── Slide 5: 海外分区域/国家 ──
    def _fill_slide_region_country_intl(self, slide):
        title_text = f"2.5 产品运营分析 – 分区域（海外）"
        title_shape = slide.shapes.title if slide.shapes.title else None
        if not title_shape:
            for shape in slide.shapes:
                if shape.has_text_frame and ("标题" in shape.name or "Title" in shape.name.lower()):
                    title_shape = shape
                    break
        if title_shape:
            update_shape_text_safe(title_shape, title_text)

        table = None
        for shape in slide.shapes:
            if shape.has_table and len(shape.table.columns) >= 8:
                table = shape.table
                break
        if not table:
            return

        metrics = analyzer.region_overseas_comprehensive_ppt(self.excel_path, self.year, self.months, self.prev_year, dfs=self._dfs)

        # 1. 洲区（4-8行）按 2026年销售占比 降序排序
        regions = ['欧洲区', '亚太区', '西亚非洲区', '拉美洲区', '北美区']
        sorted_regions = sorted(regions, key=lambda k: metrics.get(k, {}).get('sales_share') or -99999.0, reverse=True)

        # 2. 国家（11-20行）按 2026年销售占比 降序排序，仅显示前10
        country_keys = [k.replace("国家_", "") for k in metrics.keys() if k.startswith("国家_") and k != "国家_汇总"]
        sorted_countries = sorted(country_keys, key=lambda k: metrics.get(f"国家_{k}", {}).get('sales_share') or -99999.0, reverse=True)

        for r_idx in range(3, len(table.rows)):
            if r_idx == 3:
                key = "汇总"
            elif 4 <= r_idx <= 8:
                key = sorted_regions[r_idx - 4]
                update_cell_text(table.rows[r_idx].cells[0], key)
            elif r_idx == 9:
                continue
            elif r_idx == 10:
                key = "国家_汇总"
                update_cell_text(table.rows[r_idx].cells[0], "TOP10合计")
            elif 11 <= r_idx <= 20:
                c_pos = r_idx - 11
                if c_pos < len(sorted_countries):
                    ctry_name = sorted_countries[c_pos]
                    key = f"国家_{ctry_name}"
                    update_cell_text(table.rows[r_idx].cells[0], ctry_name)
                else:
                    update_cell_text(table.rows[r_idx].cells[0], "")
                    key = None
            else:
                continue

            row_data = metrics.get(key, {}) if key else {}

            update_cell_text(table.rows[r_idx].cells[1], _fmt_amt(row_data.get('sales_ytd') * UNIT.amt_to_wan_factor if row_data.get('sales_ytd') is not None else None))
            update_cell_text(table.rows[r_idx].cells[2], _fmt_pct(row_data.get('sales_ytd_yoy')))
            update_cell_text(table.rows[r_idx].cells[3], _fmt_share(row_data.get('sales_share_prev')))
            update_cell_text(table.rows[r_idx].cells[4], _fmt_share(row_data.get('sales_share')))

            update_cell_text(table.rows[r_idx].cells[5], _fmt_qty(row_data.get('qty_ytd') * UNIT.qty_to_wantai_factor if row_data.get('qty_ytd') is not None else None))
            update_cell_text(table.rows[r_idx].cells[6], _fmt_pct(row_data.get('qty_ytd_yoy')))
            update_cell_text(table.rows[r_idx].cells[7], _fmt_share(row_data.get('qty_share_prev')))
            update_cell_text(table.rows[r_idx].cells[8], _fmt_share(row_data.get('qty_share')))

    # ── Slide 6: 产品毛利分析 ──
    def _fill_slide_margin(self, slide):
        title_text = f"2.5 产品运营分析 – 产品毛利率(中国区）"
        title_shape = slide.shapes.title if slide.shapes.title else None
        if not title_shape:
            for shape in slide.shapes:
                if shape.has_text_frame and ("标题" in shape.name or "Title" in shape.name.lower()):
                    title_shape = shape
                    break
        if title_shape:
            update_shape_text_safe(title_shape, title_text)

        table = None
        for shape in slide.shapes:
            if shape.has_table and len(shape.table.columns) == 10:
                table = shape.table
                break
        if not table:
            for shape in slide.shapes:
                if shape.has_table:
                    tbl = shape.table
                    if tbl.cell(0, 0).text.strip() in ['产品类别', '产品系列', '类别', '系列', '渠道']:
                        table = tbl
                        break
        if not table:
            return

        metrics = analyzer.margin_analysis_comprehensive_ppt(self.excel_path, self.year, self.months, self.prev_year, dfs=self._dfs)

        # 需求5：删除底部青峰条目与中间UL系列条目
        rows_to_remove = []
        for idx, r in enumerate(table.rows):
            lbl = r.cells[0].text.strip()
            if lbl in ['UL系列', '青峰']:
                rows_to_remove.append(idx)
        for idx in reversed(rows_to_remove):
            tr = table.rows[idx]._tr
            tr.getparent().remove(tr)

        # Label mapping for margin metrics
        label_map = {
            "昆仑": "昆仑系列",
            "青峰": "青峰系列"
        }

        for r_idx in range(1, len(table.rows)):
            label = table.rows[r_idx].cells[0].text.strip()
            mapped_label = label_map.get(label, label)
            row_data = metrics.get(mapped_label, {})

            update_cell_text(table.rows[r_idx].cells[1], _fmt_share(row_data.get('share')))
            update_cell_text(table.rows[r_idx].cells[2], _fmt_amt(row_data.get('sales_ytd') * UNIT.amt_to_wan_factor if row_data.get('sales_ytd') is not None else None))
            update_cell_text(table.rows[r_idx].cells[3], _fmt_share(row_data.get('margin_prev')))
            update_cell_text(table.rows[r_idx].cells[4], _fmt_share(row_data.get('margin_ytd')))
            update_cell_text(table.rows[r_idx].cells[5], _fmt_share(row_data.get('margin_monthly')))

        # Post-process the entire table to convert any remaining template blue font cells to black
        for r_idx in range(1, len(table.rows)):
            for c_idx in range(len(table.columns)):
                cell = table.cell(r_idx, c_idx)
                for p in cell.text_frame.paragraphs:
                    for run in p.runs:
                        if run.font.color.type == 1:
                            rgb = run.font.color.rgb
                            if rgb[2] > 150 and rgb[0] < 100:
                                from pptx.dml.color import RGBColor
                                run.font.color.rgb = RGBColor(0, 0, 0)

    def _get_combined_row_data(self, metrics: dict, label: str, is_slide_cn: bool = True) -> dict:
        default_empty = {
            'sales_ytd': 0.0, 'sales_ytd_yoy': None,
            'sales_share_prev': None, 'sales_share': None,
            'qty_ytd': 0.0, 'qty_ytd_yoy': None,
            'qty_share_prev': None, 'qty_share': None,
            'sales_ytd_prev': 0.0, 'qty_ytd_prev': 0.0
        }
        if label == "汇总":
            return metrics.get("汇总", default_empty)

        # Define series list to sum for this label
        PRO_SERIES = ["9系列", "8系列", "5系列", "E系列", "P系列", "T系列", "H系列", "UL系列"]
        GEN_SERIES = ["昆仑", "1系列", "青峰", "其它", "其他"]

        if label == "专业产品":
            series_list = PRO_SERIES
        elif label == "通用产品":
            series_list = GEN_SERIES
        elif label == "9系列":
            series_list = ["9系列", "UL系列", "9系列 UL"]
        elif label == "9系列 UL":
            series_list = ["UL系列", "9系列 UL"]
        elif label == "昆仑":
            series_list = ["昆仑", "青峰"]
        elif label == "NXA":
            series_list = ["NXA", "昆仑"]
        elif label in ["其他", "其它"]:
            series_list = ["其它", "其他"]
        else:
            series_list = [label]

        matching_values = []
        for k, v in metrics.items():
            if isinstance(k, tuple):
                if k[1] in series_list:
                    matching_values.append(v)

        # Fallback to direct key matching
        if not matching_values:
            for k in series_list:
                if k in metrics:
                    matching_values.append(metrics[k])

        if not matching_values:
            return default_empty

        sales_ytd = 0.0
        sales_ytd_prev = 0.0
        qty_ytd = 0.0
        qty_ytd_prev = 0.0

        for v in matching_values:
            sales_ytd += v.get('sales_ytd') or 0.0
            sales_ytd_prev += v.get('sales_ytd_prev') or 0.0
            qty_ytd += v.get('qty_ytd') or 0.0
            qty_ytd_prev += v.get('qty_ytd_prev') or 0.0

        tot = metrics.get("汇总", default_empty)
        tot_sales = tot.get('sales_ytd') or 0.0
        tot_sales_prev = tot.get('sales_ytd_prev') or 0.0
        tot_qty = tot.get('qty_ytd') or 0.0
        tot_qty_prev = tot.get('qty_ytd_prev') or 0.0

        sales_ytd_yoy = (sales_ytd - sales_ytd_prev) / sales_ytd_prev * 100 if sales_ytd_prev > 0 else None
        qty_ytd_yoy = (qty_ytd - qty_ytd_prev) / qty_ytd_prev * 100 if qty_ytd_prev > 0 else None

        sales_share = sales_ytd / tot_sales * 100 if tot_sales > 0 else None
        sales_share_prev = sales_ytd_prev / tot_sales_prev * 100 if tot_sales_prev > 0 else None
        qty_share = qty_ytd / tot_qty * 100 if tot_qty > 0 else None
        qty_share_prev = qty_ytd_prev / tot_qty_prev * 100 if tot_qty_prev > 0 else None

        return {
            'sales_ytd': sales_ytd,
            'sales_ytd_yoy': sales_ytd_yoy,
            'sales_share_prev': sales_share_prev,
            'sales_share': sales_share,
            'qty_ytd': qty_ytd,
            'qty_ytd_yoy': qty_ytd_yoy,
            'qty_share_prev': qty_share_prev,
            'qty_share': qty_share
        }

    def _map_label_to_db_series(self, label: str, platform: str | None) -> str:
        plat_str = platform or ""
        mapping = {
            "E系列（高压）": "E系列",
            "E系列（常规）": "E系列",
            "P系列（5P/3）": "P系列",
            "P系列（NXMP）": "P系列",
            "昆仑系列": "昆仑",
            "青峰系列": "青峰",
            "DZ系列": "DZ",
            "UL M系列": "UL系列",
            "M系列": "UL系列" if plat_str == "诺雅克" else label
        }
        return mapping.get(label, label)

    def _get_row_data(self, metrics: dict, platform: str | None, label: str) -> dict:
        default_empty = {
            'sales_m': None, 'sales_m_yoy': None,
            'sales_ytd': None, 'sales_ytd_yoy': None,
            'sales_share_prev': None, 'sales_share': None,
            'qty_m': None, 'qty_m_yoy': None,
            'qty_ytd': None, 'qty_ytd_yoy': None,
            'qty_share_prev': None, 'qty_share': None
        }
        if label == "汇总":
            return metrics.get("汇总", default_empty)
        if "平台" in label:
            plat = label.replace("平台", "")
            return metrics.get(plat, default_empty)

        db_ser = self._map_label_to_db_series(label, platform)

        # 1. 优先使用 (platform, series) 联合定位
        if platform:
            res = metrics.get((platform, db_ser))
            if res and (res.get('sales_ytd') or res.get('qty_ytd')):
                return res

        # 2. 如果不匹配，跨平台进行模糊搜索
        for k, v in metrics.items():
            if isinstance(k, tuple) and k[1] == db_ser:
                if v.get('sales_ytd') or v.get('qty_ytd'):
                    return v

        # 3. 兜底搜索扁平 String 类型的 key
        if db_ser in metrics:
            return metrics[db_ser]

        # 4. 返回默认空字典
        if platform:
            return metrics.get((platform, db_ser), default_empty)
        return metrics.get(db_ser, default_empty)

    def _update_dateline_and_units(self, slide):
        from pptx.enum.text import PP_ALIGN

        title_shape = slide.shapes.title if slide.shapes.title else None
        if not title_shape:
            for shp in slide.shapes:
                if shp.has_text_frame and ("标题" in shp.name or "Title" in shp.name.lower()):
                    title_shape = shp
                    break

        if title_shape and title_shape.width > 4500000:
            title_shape.width = 4500000

        date_str = f"{self.year % 100}年{self.last_month}月底"

        for shape in slide.shapes:
            if shape.has_text_frame and shape != title_shape:
                txt = shape.text.strip()
                if "数据截至" in txt or "数据截止" in txt or "金额单位" in txt or ("月底" in txt and "单位" in txt):
                    old_text = shape.text_frame.text
                    p0 = shape.text_frame.paragraphs[0]

                    import re
                    new_text = re.sub(r'\d+年\d+月底', date_str, old_text)
                    if new_text == old_text:
                        new_text = re.sub(r'\d+月底', f"{self.last_month}月底", old_text)

                    if len(p0.runs) > 0:
                        p0.runs[0].text = new_text
                        for r in p0.runs[1:]:
                            r.text = ""
                    else:
                        update_shape_text_safe(shape, new_text)

                    # 仅保留文本更新逻辑，Dateline 位置由模板 geom snapshot 全局锁定
                    pass

    def _update_table_headers(self, table):
        import re
        for r_idx in range(min(2, len(table.rows))):
            for c_idx in range(len(table.columns)):
                cell = table.cell(r_idx, c_idx)
                txt = cell.text
                if not txt:
                    continue
                modified = False

                # Adapt to any starting month range (e.g. "1-3月", "1-6月", etc.) and replace with the current last month YTD
                new_txt = re.sub(r'1-\d+月', f'1-{self.last_month}月', txt)
                if new_txt != txt:
                    txt = new_txt
                    modified = True

                new_txt = re.sub(r'1~\d+月', f'1~{self.last_month}月', txt)
    def _replace_text_in_text_frame(self, tf, target_word: str, replacement: str):
        if not target_word or target_word == replacement:
            return
        for p in tf.paragraphs:
            # 1. 尝试在 run 级别精准替换
            matched_run = False
            for r in p.runs:
                if target_word in r.text:
                    r.text = r.text.replace(target_word, replacement)
                    matched_run = True
            # 2. 若目标词跨越多个 run（如 '框' 在 run[0], '架' 在 run[1]），在段落级别合并替换并保留首 run 字体样式
            if not matched_run and target_word in p.text:
                new_text = p.text.replace(target_word, replacement)
                if p.runs:
                    p.runs[0].text = new_text
                    for extra_r in p.runs[1:]:
                        extra_r.text = ""
                else:
                    p.text = new_text

    def _replace_in_shape_recursive(self, shape, target_word: str, replacement: str):
        if not target_word or target_word == replacement:
            return
        # 1. 文本框与包含 text_frame 的形状
        if shape.has_text_frame:
            self._replace_text_in_text_frame(shape.text_frame, target_word, replacement)
        # 2. 表格各单元格
        if shape.has_table:
            for row in shape.table.rows:
                for cell in row.cells:
                    if cell.text_frame:
                        self._replace_text_in_text_frame(cell.text_frame, target_word, replacement)
        # 3. 图表标题
        if shape.shape_type == 3:  # CHART
            chart = shape.chart
            if chart.has_title and chart.chart_title.has_text_frame:
                self._replace_text_in_text_frame(chart.chart_title.text_frame, target_word, replacement)
        # 4. 组合形状递归下钻 (GroupShape)
        if shape.shape_type == 6:  # GROUP
            for sub in shape.shapes:
                self._replace_in_shape_recursive(sub, target_word, replacement)

    def _replace_category_names_globally(self, prs):
        """根据当前激活的产品大类 (如 塑壳/MCCB, 微断/MCB, 框架/ACB) 全局动态替换模板中的产品名称与标题"""
        display_name = getattr(config, "PRODUCT_DISPLAY_NAME", "框架")
        category_code = getattr(config, "PRODUCT_CATEGORY", "acb").upper()

        if display_name == "框架" and category_code == "ACB":
            return

        # 规则列表：长词优先匹配，避免子串误伤
        replacements = [
            ("框架断路器", f"{display_name}断路器"),
            ("框架类", f"{display_name}类"),
            ("框架产品", f"{display_name}产品"),
            ("框架", display_name),
            ("ACB", category_code),
            ("acb", category_code.lower()),
        ]

        for slide in prs.slides:
            for shape in slide.shapes:
                for tgt, rep in replacements:
                    self._replace_in_shape_recursive(shape, tgt, rep)

    def _restore_template_row_heights(self, table, template_heights: list[int]):
        """精确恢复模板原始行高"""
        for r_idx in range(len(table.rows)):
            orig_h = template_heights[r_idx] if r_idx < len(template_heights) else 0
            tr = table.rows[r_idx]._tr
            cur_h_str = tr.get('h')
            cur_h = int(cur_h_str) if cur_h_str is not None else None
            if cur_h != orig_h:
                tr.set('h', str(orig_h))

    def _lock_all_shape_geometry(self, prs):
        """几何锁：强制将输出中所有 Shapes 的位置、尺寸、列宽与边距还原为模板原始值"""
        restored = [0]
        def _restore_shape_geom(s_idx, shp):
            key = (s_idx, shp.name)
            geom = self._tmpl_geom.get(key)
            if geom:
                l, t, w, h = geom
                if int(shp.left) != l or int(shp.top) != t or int(shp.width) != w or int(shp.height) != h:
                    shp.left = l
                    shp.top = t
                    shp.width = w
                    shp.height = h
                    restored[0] += 1

            if shp.has_text_frame:
                m_info = self._tmpl_margins.get(key)
                if m_info:
                    ml, mr, mt, mb, ww = m_info
                    tf = shp.text_frame
                    tf.margin_left = ml
                    tf.margin_right = mr
                    tf.margin_top = mt
                    tf.margin_bottom = mb
                    tf.word_wrap = ww
            if shp.has_table:
                cw = self._tmpl_col_widths.get(key)
                if cw:
                    for i, col in enumerate(shp.table.columns):
                        if i < len(cw) and int(col.width) != cw[i]:
                            col.width = cw[i]
                            restored[0] += 1
            if shp.shape_type == 6:  # GroupShape
                for sub in shp.shapes:
                    _restore_shape_geom(s_idx, sub)

        for s_idx, slide in enumerate(prs.slides):
            for shp in slide.shapes:
                _restore_shape_geom(s_idx, shp)
        if restored[0]:
            print(f"  [geom-lock] 已还原 {restored[0]} 处形状/图表/表格/组合元素几何偏差，锁定框架结构")

    def _apply_font_globally(self, prs, font_name="正泰拓新体"):
        """全局统一字体：强制统一挂载 `font_name`"""
        def _process_text_frame(tf):
            if not tf:
                return
            for p in tf.paragraphs:
                set_paragraph_font_zhengtai(p)
                if len(p.runs) == 0 and p.text and p.text.strip():
                    t = p.text
                    p.text = ""
                    r = p.add_run()
                    r.text = t
                    set_run_font_zhengtai(r)
                else:
                    for r in p.runs:
                        set_run_font_zhengtai(r)

        def _process_shape(shp):
            if shp.shape_type == 6:  # Group shape
                for sub in shp.shapes:
                    _process_shape(sub)
                return
            if shp.has_text_frame:
                _process_text_frame(shp.text_frame)
            if shp.has_table:
                for row in shp.table.rows:
                    for cell in row.cells:
                        _process_text_frame(cell.text_frame)
            if shp.has_chart:
                chart = shp.chart
                if chart.has_title and chart.chart_title.has_text_frame:
                    _process_text_frame(chart.chart_title.text_frame)

        for slide in prs.slides:
            for shp in slide.shapes:
                _process_shape(shp)

    def _avoid_slide_textbox_collisions(self, slide):
        import re
        # 作用域严格限定（用户明确要求）：
        #   - 仅针对【第一页(Slide0)中底部的图表(图表 108)】做碰撞规避；
        #   - 绝不允许作用于其他内容：
        #       ① 非第一页 / 无底部图表 -> 直接跳过，不处理任何形状；
        #       ② 即使在第一页，也【仅以底部图表为唯一碰撞障碍物】，
        #          绝不把文本框彼此推开（否则会破坏上方 KPI 表格的紧凑锁定结构）。
        target_chart = None
        for s in slide.shapes:
            if s.has_chart and s.name == "图表 108":
                target_chart = s
                break
        if target_chart is None:
            return  # 非第一页或无底部图表 -> 不处理任何内容

        chart_l = int(target_chart.left)
        chart_t = int(target_chart.top)
        chart_r = chart_l + int(target_chart.width)
        chart_b = chart_t + int(target_chart.height)

        # 仅收集第一页中的纯文本框（标题除外）作为可能被图表挤压的对象
        txt_shapes = [
            sh for sh in slide.shapes
            if sh.has_text_frame and sh.text_frame.text.strip()
            and sh != slide.shapes.title
        ]

        margin = 40000
        for _ in range(5):
            moved = False
            for s in txt_shapes:
                l, t, w, h = int(s.left), int(s.top), int(s.width), int(s.height)
                r, b = l + w, t + h
                # 仅检测「文本框 与 底部图表」的重叠，不检测文本框彼此
                overlap_x = not (r + margin < chart_l or chart_r + margin < l)
                overlap_y = not (b + margin < chart_t or chart_b + margin < t)
                if overlap_x and overlap_y:
                    moved = True
                    # 朝离图表最近的外侧方向把文本框推开
                    up_dist = (chart_t - margin) - b       # 推到图表上方
                    down_dist = (chart_b + margin) - t      # 推到图表下方
                    left_dist = (chart_l - margin) - r      # 推到图表左侧
                    right_dist = (chart_r + margin) - l     # 推到图表右侧
                    choices = [("up", abs(up_dist)), ("down", abs(down_dist)),
                               ("left", abs(left_dist)), ("right", abs(right_dist))]
                    choices.sort(key=lambda x: x[1])
                    direction = choices[0][0]
                    if direction == "up":
                        s.top = int(chart_t - margin - h)
                    elif direction == "down":
                        s.top = int(chart_b + margin)
                    elif direction == "left":
                        s.left = int(chart_l - margin - w)
                    else:  # right
                        s.left = int(chart_r + margin)
            if not moved:
                break


CURRENT_DIR = Path(__file__).resolve().parent

def _find_project_root(start_dir: Path) -> Path:
    curr = start_dir.resolve()
    for parent in [curr] + list(curr.parents):
        if (parent / "pyproject.toml").exists() or (parent / "README.md").exists() or (parent / "data" / "data.duckdb").exists():
            return parent
    return start_dir.parent

PROJECT_ROOT = _find_project_root(CURRENT_DIR)

def generate_pptx_report(excel_path=None, template_path=None, output_path=None, year: int = 2026, prev_year: int = 2025, months: list[int] | None = None, category: str | None = None):
    """根据数据与 PPTX 模板生成正泰标准 PowerPoint 运营分析报告，支持按产品大类（如 塑壳、微断、框架）动态替换标题与文本"""
    if category:
        config.set_active_product_class(category)

    display_name = getattr(config, "PRODUCT_DISPLAY_NAME", "框架")

    if template_path is None:
        candidates = [
            PROJECT_ROOT / "templates" / "制造部框架汇报文件_模版" / "制造部框架汇报文件_模版.pptx",
            PROJECT_ROOT / "templates" / "制造部框架汇报文件_模版.pptx",
            PROJECT_ROOT / "resources" / "templates" / "制造部框架汇报文件_模版.pptx",
            PROJECT_ROOT / ".agents" / "skills" / "chint-data-analysis" / "resources" / "templates" / "制造部框架汇报文件_模版.pptx",
        ]
        for cand in candidates:
            if cand.exists():
                template_path = cand
                break

    if output_path is None:
        downloads_dir = Path.home() / "Downloads"
        downloads_dir.mkdir(parents=True, exist_ok=True)
        output_path = downloads_dir / f"{display_name}产品运营分析_{year}.pptx"

    template_path = Path(template_path)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if excel_path is None:
        try:
            from loader import resolve_default_input
            excel_path = resolve_default_input()
        except ImportError:
            from etl.loader import resolve_default_input
            excel_path = resolve_default_input()

    generator = PPTXGenerator(excel_path, str(template_path), year, prev_year, months)
    res_path = generator.generate(str(output_path))
    print(f"[OK] PPTX 报告生成成功: {output_path}")
    return res_path

def main():
    import argparse
    parser = argparse.ArgumentParser(description="PowerPoint 自动化汇报生成引擎")
    parser.add_argument("--excel", help="原始数据 Excel 路径")
    parser.add_argument("--template", help="自定义 PPT 模版路径")
    parser.add_argument("--category", "-c", default=None, help="产品大类: mccb/塑壳, mcb/微断, acb/框架 (默认 acb)")
    parser.add_argument("--year", type=int, default=2026, help="分析年份")
    parser.add_argument("--prev-year", type=int, default=2025, help="对比年份")
    parser.add_argument("--months", help="分析月份列表 (如 1,2,3,4,5,6)")
    parser.add_argument("--output", help="输出 PPTX 文件路径")
    args = parser.parse_args()

    months = [int(m) for m in args.months.split(",")] if args.months else None

    generate_pptx_report(
        excel_path=args.excel,
        template_path=args.template,
        output_path=args.output,
        year=args.year,
        prev_year=args.prev_year,
        months=months,
        category=args.category,
    )

if __name__ == "__main__":
    main()