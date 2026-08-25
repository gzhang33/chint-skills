#!/usr/bin/env python3
"""
CHINT PPTX Generation Engine (2026 VI Standard Master Edition - Modularized 12-Engine Architecture)

Features:
- Modularized 12 Core Composition Engines (_render_*) handling all 34 Slide Layout Archetypes cleanly.
- 100% Backward-Compatible Semantic Dispatch Routing for all 34 Archetype Aliases (ARCH_01 to ARCH_34).
- Full 1:1 Alignment with 2026 Master Template (26年模板拓新体.pptx - 109 pages).
- Official 2026 VI Color Palette Tokens & Multi-series 8-stage Chart Palette.
"""

import os
import io
import json
from copy import deepcopy
from typing import Dict, Any, List, Optional, Union

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION
from pptx.chart.data import CategoryChartData

from chint_vector_chart_builder import ChintVectorChartBuilder

# Official 2026 VI Brand Palette Tokens
C_BLUE = RGBColor(30, 80, 230)            # CHINT Electric Blue #1E50E6 (Primary)
C_CYAN = RGBColor(80, 200, 255)           # CHINT Light Cyan #50C8FF (Auxiliary / Accent)
C_RED_TEXT = RGBColor(215, 10, 50)        # CHINT Alert Red #D70A32 (Alert / Threat)
C_RED_BG = RGBColor(255, 235, 238)        # Soft Red Alert Background #FFEBEB
C_GREEN = RGBColor(20, 200, 50)           # Growth Green #14C832 (Opportunity / Growth)
C_GREEN_BG = RGBColor(232, 248, 238)      # Soft Green Background #E8F8EE
C_TEAL = RGBColor(20, 200, 180)           # Smart Teal #14C8B4
C_DEEP_BLUE = RGBColor(20, 55, 170)       # Deep Corporate Blue #1437AA (Base / Dark Header)
C_BLUE_BG = RGBColor(235, 243, 255)       # Soft Blue Container #EBF3FF
C_ICE_BLUE = RGBColor(215, 240, 255)       # Ice Blue #D7F0FF
C_ORANGE = RGBColor(245, 158, 11)         # Warning Orange #F59E0B
C_DARK = RGBColor(30, 32, 36)             # Primary Dark Text #1E2024
C_MUTED = RGBColor(90, 90, 90)            # Slate Gray #5A5A5A
C_LIGHT_BG = RGBColor(246, 248, 250)      # Container Background #F6F8FA
C_BORDER = RGBColor(208, 215, 222)        # Card Border #D0D7DE
C_WHITE = RGBColor(255, 255, 255)         # Pure White #FFFFFF
C_CARD_HEADER_BG = RGBColor(228, 238, 255)# Card Header Light Blue #E4EEFF

# Multi-series Data Chart 8-stage Palette
CHART_PALETTE = [
    C_BLUE,                    # 1. Primary #1E50E6
    C_CYAN,                    # 2. Contrast #50C8FF
    C_GREEN,                   # 3. Growth #14C832
    C_TEAL,                    # 4. Smart #14C8B4
    RGBColor(35, 120, 255),    # 5. Accent Blue #2378FF
    RGBColor(90, 220, 25),     # 6. Soft Green #5ADC19
    C_ORANGE,                  # 7. Warning #F59E0B
    C_RED_TEXT                 # 8. Alert #D70A32
]

FONT_FAMILY = "正泰拓新体"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), "assets")
MEDIA_DIR = os.path.join(ASSETS_DIR, "media")
TEMPLATES_DIR = os.path.join(ASSETS_DIR, "templates")


def calc_autofit_fontsize(text: str, base_size: float = 11.0, min_size: float = 9.5,
                          threshold_len: int = 40, step: float = 0.5) -> float:
    """Dynamically scale font size based on text character length to prevent card overflow."""
    if not text:
        return base_size
    length = len(text)
    if length <= threshold_len:
        return base_size
    excess = length - threshold_len
    reduction = (excess // 15 + 1) * step
    return max(min_size, base_size - reduction)


def set_para(p, text: str, font_name: str = FONT_FAMILY, font_size: Optional[float] = None,
             bold: Optional[bool] = None, color_rgb: Optional[RGBColor] = None,
             align: Optional[PP_ALIGN] = None):
    p.text = text
    if font_name: p.font.name = font_name
    if font_size: p.font.size = Pt(font_size)
    if bold is not None: p.font.bold = bold
    if color_rgb: p.font.color.rgb = color_rgb
    if align: p.alignment = align
    for r in p.runs:
        if font_name: r.font.name = font_name
        if font_size: r.font.size = Pt(font_size)
        if bold is not None: r.font.bold = bold
        if color_rgb: r.font.color.rgb = color_rgb


def resolve_template_path(custom_dir: Optional[str] = None) -> Optional[str]:
    """Dynamically resolve the 2026 Master Template path across environments without hardcoded paths."""
    candidates = [
        os.path.join(custom_dir, "26年模板拓新体.pptx") if custom_dir else None,
        os.getenv("CHINT_PPTX_TEMPLATE"),
        os.path.join(TEMPLATES_DIR, "26年模板拓新体.pptx"),
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(SCRIPT_DIR)))), "resources", "品牌资产", "26年模板拓新体(1).pptx"),
        os.path.join(os.getcwd(), "resources", "品牌资产", "26年模板拓新体(1).pptx"),
    ]
    for p in candidates:
        if p and os.path.exists(p):
            return p
    return None


class ChintPresentationEngine:
    def __init__(self, media_dir: Optional[str] = None, templates_dir: Optional[str] = None):
        self.media_dir = media_dir or MEDIA_DIR
        self.templates_dir = templates_dir or TEMPLATES_DIR
        
        tmpl_file = resolve_template_path(self.templates_dir)
        if tmpl_file and os.path.exists(tmpl_file):
            self.prs = Presentation(tmpl_file)
            for i in range(len(self.prs.slides) - 1, -1, -1):
                r_id = self.prs.slides._sldIdLst[i].rId
                self.prs.part.drop_rel(r_id)
                del self.prs.slides._sldIdLst[i]
        else:
            self.prs = Presentation()
            
        self.prs.slide_width = Inches(13.333)
        self.prs.slide_height = Inches(7.5)
        self.blank_layout = self.prs.slide_layouts[0] if len(self.prs.slide_layouts) > 0 else self.prs.slide_layouts[0]
        # Detect if master slide already contains the official CHINT logo/badge
        self.has_master_logo = any(
            s.shape_type == 13 and s.left > Inches(10)
            for master in self.prs.slide_masters
            for s in master.shapes
        )

    def _add_body_master(self, slide, title: str, category: Optional[str] = None):
        if not getattr(self, "has_master_logo", False):
            badge_path = os.path.join(self.media_dir, "chint_badge.png")
            if os.path.exists(badge_path):
                slide.shapes.add_picture(badge_path, Inches(11.4), Inches(0.0), Inches(1.53), Inches(1.15))
            
        tb = slide.shapes.add_textbox(Inches(0.8), Inches(0.45), Inches(10.5), Inches(0.8))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        if category:
            set_para(p, f"[{category}]  {title}", font_size=20, bold=True, color_rgb=C_BLUE)
        else:
            set_para(p, title, font_size=22, bold=True, color_rgb=C_BLUE)
            
        tb_foot = slide.shapes.add_textbox(Inches(9.5), Inches(7.0), Inches(3.2), Inches(0.4))
        p_f = tb_foot.text_frame.paragraphs[0]
        set_para(p_f, "Copyright © CHINT GROUP 2025-2026", font_size=9, bold=False, color_rgb=RGBColor(160, 160, 160), align=PP_ALIGN.RIGHT)

    @staticmethod
    def _set_tf_margins(tf, top: float = 8, bottom: float = 8, left: float = 8, right: float = 8):
        tf.margin_top = Pt(top)
        tf.margin_bottom = Pt(bottom)
        tf.margin_left = Pt(left)
        tf.margin_right = Pt(right)

    # =========================================================================
    # 12 CORE COMPOSITION ENGINES (_render_*)
    # =========================================================================

    def _render_master_frame(self, slide, s_data: Dict[str, Any], arch: str):
        """Engine 1: Master Frames (Cover, TOC, Chapter, Closing, Contact)"""
        if arch.startswith("ARCH_01"):
            cover_bg = os.path.join(self.media_dir, "cover_26_bg.png")
            if os.path.exists(cover_bg):
                slide.shapes.add_picture(cover_bg, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
            else:
                cover_img = os.path.join(self.media_dir, "image2.jpeg")
                if os.path.exists(cover_img):
                    slide.shapes.add_picture(cover_img, Inches(0), Inches(0), Inches(13.333), Inches(7.5))

            bar1 = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(3.93), Inches(4.85), Inches(9.4), Inches(1.05))
            bar1.fill.solid()
            bar1.fill.fore_color.rgb = C_BLUE
            bar1.line.fill.background()
            
            tb_t = slide.shapes.add_textbox(Inches(4.1), Inches(4.95), Inches(9.0), Inches(0.85))
            tf_t = tb_t.text_frame
            tf_t.word_wrap = True
            set_para(tf_t.paragraphs[0], s_data.get("title", "演示文稿标题"), font_size=28, bold=True, color_rgb=C_WHITE)

            bar2 = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(3.93), Inches(5.90), Inches(9.4), Inches(0.42))
            bar2.fill.solid()
            bar2.fill.fore_color.rgb = C_CYAN
            bar2.line.fill.background()

            tb_sub = slide.shapes.add_textbox(Inches(4.1), Inches(5.92), Inches(9.0), Inches(0.38))
            tf_sub = tb_sub.text_frame
            tf_sub.word_wrap = True
            set_para(tf_sub.paragraphs[0], s_data.get("subtitle", ""), font_size=13, bold=False, color_rgb=C_WHITE)

        elif arch.startswith("ARCH_02"):
            toc_bg = os.path.join(self.media_dir, "toc_26_bg.png")
            if os.path.exists(toc_bg):
                slide.shapes.add_picture(toc_bg, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
            else:
                ribbon = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(4.7), Inches(7.5))
                ribbon.fill.solid()
                ribbon.fill.fore_color.rgb = C_BLUE
                ribbon.line.fill.background()

                tb_c = slide.shapes.add_textbox(Inches(0.8), Inches(3.2), Inches(3.1), Inches(1.2))
                set_para(tb_c.text_frame.paragraphs[0], "CONTENTS", font_size=32, bold=True, color_rgb=C_WHITE, align=PP_ALIGN.CENTER)

            if not getattr(self, "has_master_logo", False):
                badge_path = os.path.join(self.media_dir, "chint_badge.png")
                if os.path.exists(badge_path):
                    slide.shapes.add_picture(badge_path, Inches(11.4), Inches(0.0), Inches(1.53), Inches(1.15))

            items = s_data.get("items", [])
            tmpl_file = resolve_template_path(self.templates_dir)
            
            template_copied = False
            if tmpl_file and os.path.exists(tmpl_file):
                try:
                    tmpl_prs = Presentation(tmpl_file)
                    tmpl_slide2 = tmpl_prs.slides[1]
                    target_spTree = slide.shapes._spTree
                    num_items = len(items) if items else 5
                    delta_w = 1097280
                    
                    for i in range(min(num_items, 5)):
                        item_data = items[i]
                        raw_title = item_data.get("title", "") if isinstance(item_data, dict) else str(item_data)
                        clean_title = raw_title.lstrip("0123456789. 、：: ")
                        
                        for sub_i in range(7):
                            src_shp = tmpl_slide2.shapes[i * 7 + sub_i]
                            new_elem = deepcopy(src_shp._element)
                            for cust in new_elem.xpath('.//p:custDataLst'):
                                cust.getparent().remove(cust)
                            
                            xfrm = new_elem.xpath('.//a:xfrm')
                            if xfrm:
                                ext = xfrm[0].xpath('./a:ext')
                                off = xfrm[0].xpath('./a:off')
                                if sub_i in (0, 1, 4) and ext:
                                    cur_cx = int(ext[0].get('cx'))
                                    ext[0].set('cx', str(cur_cx + delta_w))
                                elif sub_i in (5, 6) and off:
                                    cur_x = int(off[0].get('x'))
                                    off[0].set('x', str(cur_x + delta_w))
                            
                            if sub_i == 2:
                                t_nodes = new_elem.xpath('.//a:t')
                                if t_nodes: t_nodes[0].text = f"{i+1:02d}"
                            if sub_i == 4:
                                bodyPr = new_elem.xpath('.//a:bodyPr')
                                if bodyPr: bodyPr[0].set('wrap', 'none')
                                t_nodes = new_elem.xpath('.//a:t')
                                if t_nodes: t_nodes[0].text = clean_title
                            
                            target_spTree.append(new_elem)
                    template_copied = True
                except Exception as e:
                    print(f"[WARN] Failed to copy TOC template slide: {e}")
                    template_copied = False

            if not template_copied:
                num_items = min(len(items), 5) if items else 5
                base_tops = [Inches(1.30), Inches(2.29), Inches(3.28), Inches(4.27), Inches(5.26)]
                pill_w, pill_h, pill_left = Inches(7.76), Inches(0.76), Inches(5.02)

                for i in range(num_items):
                    cur_top = base_tops[i]
                    raw_title = items[i].get("title", "") if isinstance(items[i], dict) else str(items[i])
                    clean_title = raw_title.lstrip("0123456789. 、：: ")

                    outer_pill = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, pill_left, cur_top, pill_w, pill_h)
                    outer_pill.fill.solid()
                    outer_pill.fill.fore_color.rgb = C_BLUE_BG
                    outer_pill.line.color.rgb = RGBColor(200, 225, 255)
                    outer_pill.line.width = Pt(1.5)

                    inner_card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, pill_left + Inches(1.31), cur_top, pill_w - Inches(1.31), pill_h)
                    inner_card.fill.solid()
                    inner_card.fill.fore_color.rgb = C_WHITE
                    inner_card.line.fill.background()

                    tb_num = slide.shapes.add_textbox(pill_left + Inches(0.15), cur_top + Inches(0.08), Inches(0.7), Inches(0.6))
                    set_para(tb_num.text_frame.paragraphs[0], f"{i+1:02d}", font_size=28, bold=True, color_rgb=C_BLUE)

                    v_line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, pill_left + Inches(0.99), cur_top + Inches(0.16), Inches(0.015), Inches(0.44))
                    v_line.fill.solid()
                    v_line.fill.fore_color.rgb = C_BORDER
                    v_line.line.fill.background()

                    tb_title = slide.shapes.add_textbox(pill_left + Inches(1.15), cur_top + Inches(0.13), pill_w - Inches(1.85), Inches(0.5))
                    tf_title = tb_title.text_frame
                    tf_title.word_wrap = False
                    set_para(tf_title.paragraphs[0], clean_title, font_size=20, bold=True, color_rgb=C_DARK)

                    for chv_x in (Inches(7.02), Inches(7.16)):
                        chv = slide.shapes.add_shape(MSO_SHAPE.CHEVRON, pill_left + chv_x, cur_top + Inches(0.29), Inches(0.15), Inches(0.18))
                        chv.fill.solid()
                        chv.fill.fore_color.rgb = C_CYAN
                        chv.line.fill.background()

        elif arch == "ARCH_03_CHAPTER":
            chap_banner = os.path.join(self.media_dir, "image7.jpeg")
            if not os.path.exists(chap_banner):
                chap_banner = os.path.join(self.media_dir, "chapter_26_bg.png")
            
            if os.path.exists(chap_banner):
                slide.shapes.add_picture(chap_banner, Inches(0), Inches(1.71), Inches(13.333), Inches(3.42))
            else:
                band = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(1.71), Inches(13.333), Inches(3.42))
                band.fill.solid()
                band.fill.fore_color.rgb = C_BLUE
                band.line.fill.background()

            line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(5.13), Inches(13.333), Inches(0.06))
            line.fill.solid()
            line.fill.fore_color.rgb = C_CYAN
            line.line.fill.background()

            if not getattr(self, "has_master_logo", False):
                badge_path = os.path.join(self.media_dir, "chint_badge.png")
                if os.path.exists(badge_path):
                    slide.shapes.add_picture(badge_path, Inches(11.4), Inches(0.0), Inches(1.53), Inches(1.15))

            title_text = s_data.get("title") or s_data.get("headline") or "添加章节标题"
            subtitle_text = s_data.get("subtitle") or s_data.get("category") or ""

            if subtitle_text:
                tb_c = slide.shapes.add_textbox(Inches(1.0), Inches(2.7), Inches(11.33), Inches(1.8))
                tf_c = tb_c.text_frame
                tf_c.word_wrap = True
                set_para(tf_c.paragraphs[0], subtitle_text.upper(), font_size=13, bold=True, color_rgb=C_ICE_BLUE, align=PP_ALIGN.CENTER)
                p_t = tf_c.add_paragraph()
                set_para(p_t, title_text, font_size=32, bold=True, color_rgb=C_WHITE, align=PP_ALIGN.CENTER)
                p_t.space_before = Pt(6)
            else:
                tb_c = slide.shapes.add_textbox(Inches(1.0), Inches(3.0), Inches(11.33), Inches(1.4))
                tf_c = tb_c.text_frame
                tf_c.word_wrap = True
                set_para(tf_c.paragraphs[0], title_text, font_size=32, bold=True, color_rgb=C_WHITE, align=PP_ALIGN.CENTER)

        elif arch.startswith("ARCH_11"):
            closing_bg = os.path.join(self.media_dir, "closing_26_bg.png")
            if os.path.exists(closing_bg):
                slide.shapes.add_picture(closing_bg, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
            else:
                closing_img = os.path.join(self.media_dir, "image6.jpeg")
                if os.path.exists(closing_img):
                    slide.shapes.add_picture(closing_img, Inches(0), Inches(0), Inches(13.333), Inches(7.5))

                band = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(5.2), Inches(13.333), Inches(0.8))
                band.fill.solid()
                band.fill.fore_color.rgb = C_BLUE
                band.line.fill.background()

                tb_thx = slide.shapes.add_textbox(Inches(1.0), Inches(5.3), Inches(11.33), Inches(0.6))
                set_para(tb_thx.text_frame.paragraphs[0], "THANKS", font_size=28, bold=True, color_rgb=C_WHITE, align=PP_ALIGN.CENTER)

            tagline = s_data.get("tagline", "")
            team = s_data.get("team", "")
            sub_text = f"{tagline}  |  {team}" if tagline and team else (tagline or team or "")

            if sub_text:
                tb_sub = slide.shapes.add_textbox(Inches(1.0), Inches(6.8), Inches(11.33), Inches(0.5))
                set_para(tb_sub.text_frame.paragraphs[0], sub_text, font_size=11, bold=False, color_rgb=C_MUTED, align=PP_ALIGN.CENTER)

        elif arch.startswith("ARCH_15"):
            self._add_body_master(slide, s_data.get("title", "联系我们与办事处网点"), s_data.get("category", "服务网络"))
            channels = s_data.get("channels", [
                {"icon_label": "400", "title": "全国统一服务热线", "desc": "400-8877-666 (7×24h 快速响应)"},
                {"icon_label": "商务", "title": "全球商务合作", "desc": "sales@chint.com / 渠道合作赋能"},
                {"icon_label": "技术", "title": "方案与技术支持", "desc": "support@chint.com / 资深专家答疑"},
                {"icon_label": "门户", "title": "官方门户网站", "desc": "www.chint.com / 获取最新白皮书"}
            ])
            card_w, card_h, gap_y, top_m = Inches(5.6), Inches(1.1), Inches(0.18), Inches(1.6)
            
            for i, ch in enumerate(channels[:4]):
                cur_top = top_m + i * (card_h + gap_y)
                bg = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), cur_top, card_w, card_h)
                bg.fill.solid()
                bg.fill.fore_color.rgb = C_LIGHT_BG
                bg.line.color.rgb = C_BORDER
                bg.line.width = Pt(1)
                
                ic = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(1.0), cur_top + Inches(0.2), Inches(0.7), Inches(0.7))
                ic.fill.solid()
                ic.fill.fore_color.rgb = C_BLUE_BG
                ic.line.color.rgb = C_BLUE
                ic.line.width = Pt(1)
                tf_ic = ic.text_frame
                self._set_tf_margins(tf_ic, top=2, bottom=2, left=2, right=2)
                set_para(tf_ic.paragraphs[0], ch.get("icon_label", "服务"), font_size=11, bold=True, color_rgb=C_BLUE, align=PP_ALIGN.CENTER)
                
                tb_c = slide.shapes.add_textbox(Inches(1.85), cur_top + Inches(0.12), card_w - Inches(1.2), Inches(0.85))
                tf_c = tb_c.text_frame
                tf_c.word_wrap = True
                self._set_tf_margins(tf_c, top=6, bottom=6, left=6, right=6)
                set_para(tf_c.paragraphs[0], ch.get("title", ""), font_size=13.5, bold=True, color_rgb=C_DARK)
                p_desc = tf_c.add_paragraph()
                set_para(p_desc, ch.get("desc", ""), font_size=11, bold=False, color_rgb=C_MUTED)
                p_desc.space_before = Pt(4)
                
            right_w = Inches(5.8)
            right_bg = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.73), top_m, right_w, Inches(5.0))
            right_bg.fill.solid()
            right_bg.fill.fore_color.rgb = C_LIGHT_BG
            right_bg.line.color.rgb = C_BORDER
            right_bg.line.width = Pt(1)
            
            h_bar = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.73), top_m, right_w, Inches(0.7))
            h_bar.fill.solid()
            h_bar.fill.fore_color.rgb = C_CARD_HEADER_BG
            h_bar.line.fill.background()
            tf_hbar = h_bar.text_frame
            self._set_tf_margins(tf_hbar, top=4, bottom=4, left=8, right=8)
            set_para(tf_hbar.paragraphs[0], s_data.get("directory_title", "主要大区办事处与分支机构"), font_size=14, bold=True, color_rgb=C_BLUE, align=PP_ALIGN.CENTER)
            
            tb_r = slide.shapes.add_textbox(Inches(7.0), top_m + Inches(0.85), right_w - Inches(0.5), Inches(3.9))
            tf_r = tb_r.text_frame
            tf_r.word_wrap = True
            self._set_tf_margins(tf_r, top=8, bottom=8, left=8, right=8)
            offices = s_data.get("offices", [
                "华东大区总部：上海市松江区正泰启迪智电港",
                "华北大区总部：北京市亦庄经济技术开发区",
                "华南大区总部：广东省广州市天河区高新科技园",
                "西部大区总部：四川省成都市高新区天府软件园",
                "欧洲区域总部：德国法兰克福正泰欧洲创新中心",
                "北美区域总部：美国加利福尼亚州正泰北美研发中心"
            ])
            for j, o in enumerate(offices):
                p = tf_r.paragraphs[0] if j == 0 else tf_r.add_paragraph()
                set_para(p, f"• {o}", font_size=11.5, bold=False, color_rgb=C_DARK)
                p.space_before = Pt(8)

    def _render_dual_pane_split(self, slide, s_data: Dict[str, Any], arch: str):
        """Engine 2: 50:50 Dual-Pane Comparison (ARCH_07, ARCH_21, ARCH_22)"""
        self._add_body_master(slide, s_data.get("title", ""), s_data.get("category", ""))
        box_w, box_h, top_m = Inches(5.65), Inches(5.0), Inches(1.6)
        
        # Configure theme parameters based on archetype
        if arch.startswith("ARCH_07"):
            left_title = s_data.get("pain_header", "核心挑战与痛点剖析")
            left_items = s_data.get("pain_points", [])
            left_bg_color, left_border_color, left_title_color = C_RED_BG, RGBColor(255, 180, 180), C_RED_TEXT
            left_summary_title = "【核心挑战瓶颈】"
            left_summary_text = s_data.get("pain_summary", "传统电气运维与配电系统缺乏统一协同，存在安全与成本隐患")
            
            right_title = s_data.get("solution_header", "针对性应对解决方案")
            right_items = s_data.get("solutions", [])
            right_bg_color, right_border_color, right_title_color = C_BLUE_BG, RGBColor(180, 210, 255), C_BLUE
            right_summary_title = "【针对性破局方案】"
            right_summary_text = s_data.get("solution_summary", "构建正泰一站式智慧低压配电综合方案，实现全局数智化协同")
        elif arch.startswith("ARCH_21"):
            left_title = s_data.get("before_title", "传统模式 / 改造前 (Before)")
            left_items = s_data.get("before_items", [
                "人工巡检维护，响应周期长达 24-48 小时",
                "数据孤岛严重，系统互通性不足",
                "能效粗放管理，无实时负荷监测",
                "运维成本高昂，故障后被动抢修"
            ])
            left_bg_color, left_border_color, left_title_color = C_LIGHT_BG, C_BORDER, C_MUTED
            left_summary_title = "【传统模式痛点瓶颈】"
            left_summary_text = s_data.get("before_summary", "故障平均响应 > 24h | 年均额外运维成本超 120 万元 | 故障被动抢修")
            
            right_title = s_data.get("after_title", "正泰智能方案 / 升级后 (After)")
            right_items = s_data.get("after_items", [
                "AI 预测性维护，分钟级告警与远程诊断",
                "统一云边物联底座，设备无缝接入",
                "精细化动态节能，综合能耗降低 30%+",
                "全生命周期资产数字化管理"
            ])
            right_bg_color, right_border_color, right_title_color = C_BLUE_BG, RGBColor(180, 210, 255), C_BLUE
            right_summary_title = "【数字化升级核心价值】"
            right_summary_text = s_data.get("after_summary", "综合能耗降低 30%+ | 设备故障预警率 99.5% | 全域资产数字孪生")
        else: # ARCH_22
            left_title = s_data.get("problem_title", "当前现存主要问题与短板")
            left_items = s_data.get("problems", [
                "交付瓶颈：非标定制订单响应周期偏长",
                "供应链波动：部分关键电子元器件供货承压",
                "数字化渗透率不足：部分一线现场依赖纸质记录"
            ])
            left_bg_color, left_border_color, left_title_color = C_RED_BG, RGBColor(255, 180, 180), C_RED_TEXT
            left_summary_title = "【现存短板影响】"
            left_summary_text = s_data.get("problem_summary", "影响重大项目敏捷履约，面临供应链波动与现场协同交付风险")
            
            right_title = s_data.get("improve_title", "系统化改善对策与推进计划")
            right_items = s_data.get("improvements", [
                "柔性制造升级：交付周期压缩至 48 小时以内",
                "战略安全库存：建立核心物料双供应商机制",
                "移动数字赋能：推行移动 APP 巡检与电子看板"
            ])
            right_bg_color, right_border_color, right_title_color = C_BLUE_BG, RGBColor(180, 210, 255), C_BLUE
            right_summary_title = "【改进目标与落地收益】"
            right_summary_text = s_data.get("improve_summary", "交付准时率提升至 99.2% | 核心物料双供覆盖率 100% | 48h 极速交付")

        # --- Left Pane ---
        l_bg = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), top_m, box_w, box_h)
        l_bg.fill.solid()
        l_bg.fill.fore_color.rgb = left_bg_color
        l_bg.line.color.rgb = left_border_color
        l_bg.line.width = Pt(1.2)

        # Left Header Banner
        l_hdr = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), top_m, box_w, Inches(0.7))
        l_hdr.fill.solid()
        l_hdr.fill.fore_color.rgb = RGBColor(255, 240, 240) if left_bg_color == C_RED_BG else C_CARD_HEADER_BG
        l_hdr.line.fill.background()

        tb_lh = slide.shapes.add_textbox(Inches(1.0), top_m + Inches(0.1), box_w - Inches(0.4), Inches(0.5))
        tf_lh = tb_lh.text_frame
        tf_lh.word_wrap = True
        self._set_tf_margins(tf_lh, top=4, bottom=4, left=4, right=4)
        set_para(tf_lh.paragraphs[0], left_title, font_size=14, bold=True, color_rgb=left_title_color)

        # Left Body Content
        tb_lb = slide.shapes.add_textbox(Inches(1.0), top_m + Inches(0.85), box_w - Inches(0.4), Inches(2.65))
        tf_lb = tb_lb.text_frame
        tf_lb.word_wrap = True
        self._set_tf_margins(tf_lb, top=6, bottom=6, left=6, right=6)
        spacing_l = Pt(20) if len(left_items) <= 3 else Pt(14)
        for j, item in enumerate(left_items):
            p = tf_lb.paragraphs[0] if j == 0 else tf_lb.add_paragraph()
            p.space_before = spacing_l
            p.space_after = Pt(2)
            if "：" in item:
                lead, rest = item.split("：", 1)
                r_lead = p.add_run()
                r_lead.text = f"• {lead}："
                r_lead.font.name = "正泰拓新体"
                r_lead.font.size = Pt(12.0)
                r_lead.font.bold = True
                r_lead.font.color.rgb = C_DARK
                
                r_rest = p.add_run()
                r_rest.text = rest
                r_rest.font.name = "正泰拓新体"
                r_rest.font.size = Pt(11.0)
                r_rest.font.bold = False
                r_rest.font.color.rgb = C_DARK
            elif ":" in item:
                lead, rest = item.split(":", 1)
                r_lead = p.add_run()
                r_lead.text = f"• {lead}: "
                r_lead.font.name = "正泰拓新体"
                r_lead.font.size = Pt(12.0)
                r_lead.font.bold = True
                r_lead.font.color.rgb = C_DARK
                
                r_rest = p.add_run()
                r_rest.text = rest
                r_rest.font.name = "正泰拓新体"
                r_rest.font.size = Pt(11.0)
                r_rest.font.bold = False
                r_rest.font.color.rgb = C_DARK
            else:
                f_auto = calc_autofit_fontsize(item, base_size=11.5, min_size=9.5, threshold_len=26)
                set_para(p, f"• {item}", font_size=f_auto, bold=False, color_rgb=C_DARK)

        # Left Bottom Summary Box
        l_bot_box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.0), top_m + Inches(3.6), box_w - Inches(0.4), Inches(1.15))
        l_bot_box.fill.solid()
        l_bot_box.fill.fore_color.rgb = C_WHITE
        l_bot_box.line.color.rgb = left_border_color
        l_bot_box.line.width = Pt(1)
        
        tb_l_bot = slide.shapes.add_textbox(Inches(1.1), top_m + Inches(3.65), box_w - Inches(0.6), Inches(1.05))
        tf_l_bot = tb_l_bot.text_frame
        tf_l_bot.word_wrap = True
        self._set_tf_margins(tf_l_bot, top=4, bottom=4, left=4, right=4)
        set_para(tf_l_bot.paragraphs[0], left_summary_title, font_size=11, bold=True, color_rgb=left_title_color)
        p_l_bs = tf_l_bot.add_paragraph()
        f_sauto = calc_autofit_fontsize(left_summary_text, base_size=10.0, min_size=8.5, threshold_len=30)
        set_para(p_l_bs, left_summary_text, font_size=f_sauto, bold=False, color_rgb=C_DARK)
        p_l_bs.space_before = Pt(3)

        # --- Right Pane ---
        r_bg = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.88), top_m, box_w, box_h)
        r_bg.fill.solid()
        r_bg.fill.fore_color.rgb = right_bg_color
        r_bg.line.color.rgb = right_border_color
        r_bg.line.width = Pt(1.2)

        # Right Header Banner
        r_hdr = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.88), top_m, box_w, Inches(0.7))
        r_hdr.fill.solid()
        r_hdr.fill.fore_color.rgb = C_CARD_HEADER_BG
        r_hdr.line.fill.background()

        tb_rh = slide.shapes.add_textbox(Inches(7.08), top_m + Inches(0.1), box_w - Inches(0.4), Inches(0.5))
        tf_rh = tb_rh.text_frame
        tf_rh.word_wrap = True
        self._set_tf_margins(tf_rh, top=4, bottom=4, left=4, right=4)
        set_para(tf_rh.paragraphs[0], right_title, font_size=14, bold=True, color_rgb=right_title_color)

        # Right Body Content
        tb_rb = slide.shapes.add_textbox(Inches(7.08), top_m + Inches(0.85), box_w - Inches(0.4), Inches(2.65))
        tf_rb = tb_rb.text_frame
        tf_rb.word_wrap = True
        self._set_tf_margins(tf_rb, top=6, bottom=6, left=6, right=6)
        spacing_r = Pt(20) if len(right_items) <= 3 else Pt(14)
        for j, item in enumerate(right_items):
            p = tf_rb.paragraphs[0] if j == 0 else tf_rb.add_paragraph()
            p.space_before = spacing_r
            p.space_after = Pt(2)
            if "：" in item:
                lead, rest = item.split("：", 1)
                r_lead = p.add_run()
                r_lead.text = f"• {lead}："
                r_lead.font.name = "正泰拓新体"
                r_lead.font.size = Pt(12.0)
                r_lead.font.bold = True
                r_lead.font.color.rgb = C_DARK
                
                r_rest = p.add_run()
                r_rest.text = rest
                r_rest.font.name = "正泰拓新体"
                r_rest.font.size = Pt(11.0)
                r_rest.font.bold = False
                r_rest.font.color.rgb = C_DARK
            elif ":" in item:
                lead, rest = item.split(":", 1)
                r_lead = p.add_run()
                r_lead.text = f"• {lead}: "
                r_lead.font.name = "正泰拓新体"
                r_lead.font.size = Pt(12.0)
                r_lead.font.bold = True
                r_lead.font.color.rgb = C_DARK
                
                r_rest = p.add_run()
                r_rest.text = rest
                r_rest.font.name = "正泰拓新体"
                r_rest.font.size = Pt(11.0)
                r_rest.font.bold = False
                r_rest.font.color.rgb = C_DARK
            else:
                f_auto = calc_autofit_fontsize(item, base_size=11.5, min_size=9.5, threshold_len=26)
                set_para(p, f"• {item}", font_size=f_auto, bold=False, color_rgb=C_DARK)

        # Right Bottom Summary Box
        r_bot_box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.08), top_m + Inches(3.6), box_w - Inches(0.4), Inches(1.15))
        r_bot_box.fill.solid()
        r_bot_box.fill.fore_color.rgb = C_WHITE
        r_bot_box.line.color.rgb = right_border_color
        r_bot_box.line.width = Pt(1)
        
        tb_r_bot = slide.shapes.add_textbox(Inches(7.18), top_m + Inches(3.65), box_w - Inches(0.6), Inches(1.05))
        tf_r_bot = tb_r_bot.text_frame
        tf_r_bot.word_wrap = True
        self._set_tf_margins(tf_r_bot, top=4, bottom=4, left=4, right=4)
        set_para(tf_r_bot.paragraphs[0], right_summary_title, font_size=11, bold=True, color_rgb=right_title_color)
        p_r_bs = tf_r_bot.add_paragraph()
        f_sauto_r = calc_autofit_fontsize(right_summary_text, base_size=10.0, min_size=8.5, threshold_len=30)
        set_para(p_r_bs, right_summary_text, font_size=f_sauto_r, bold=False, color_rgb=C_DARK)
        p_r_bs.space_before = Pt(3)

    def _render_hero_split_pane(self, slide, s_data: Dict[str, Any], arch: str):
        """Engine 3: Asymmetric Hero Split (ARCH_10, ARCH_13, ARCH_19)"""
        self._add_body_master(slide, s_data.get("title", ""), s_data.get("category", ""))
        top_m, box_h = Inches(1.6), Inches(5.0)
        left_w, right_w = Inches(4.5), Inches(6.8)

        # Left Hero Card (Deep Blue / Electric Blue)
        left_bg = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), top_m, left_w, box_h)
        left_bg.fill.solid()
        left_bg.fill.fore_color.rgb = C_DEEP_BLUE if arch == "ARCH_13_GLOBAL_FOOTPRINT" else C_BLUE
        left_bg.line.fill.background()

        tb_l = slide.shapes.add_textbox(Inches(1.0), top_m + Inches(0.35), left_w - Inches(0.4), box_h - Inches(0.7))
        tf_l = tb_l.text_frame
        tf_l.word_wrap = True
        self._set_tf_margins(tf_l, top=8, bottom=8, left=8, right=8)

        if arch.startswith("ARCH_10"):
            set_para(tf_l.paragraphs[0], s_data.get("client_name", "标杆客户示范项目"), font_size=16, bold=True, color_rgb=C_WHITE)
            p_val = tf_l.add_paragraph()
            set_para(p_val, s_data.get("hero_metric", "核心成效提升"), font_size=34, bold=True, color_rgb=C_ICE_BLUE)
            p_val.space_before = Pt(14)
            p_val.space_after = Pt(4)
            p_sub = tf_l.add_paragraph()
            set_para(p_sub, s_data.get("hero_desc", "系统化解决方案端到端落地实施"), font_size=12, bold=False, color_rgb=C_WHITE)
            p_sub.space_before = Pt(8)
        elif arch.startswith("ARCH_13"):
            set_para(tf_l.paragraphs[0], s_data.get("coverage_title", "全球业务覆盖"), font_size=18, bold=True, color_rgb=C_WHITE)
            stats = s_data.get("stats", [("140+", "覆盖国家与地区"), ("30,000+", "全球员工总数"), ("4 大", "全球研发中心")])
            for val, lbl in stats:
                p1 = tf_l.add_paragraph()
                set_para(p1, val, font_size=30, bold=True, color_rgb=C_ICE_BLUE)
                p1.space_before = Pt(12)
                p2 = tf_l.add_paragraph()
                set_para(p2, lbl, font_size=11, bold=False, color_rgb=C_WHITE)
                p2.space_before = Pt(2)
        else: # ARCH_19
            set_para(tf_l.paragraphs[0], s_data.get("hero_label", "年度核心战果突破"), font_size=14, bold=True, color_rgb=C_ICE_BLUE)
            p_num = tf_l.add_paragraph()
            set_para(p_num, s_data.get("hero_number", "9,000 W+"), font_size=40, bold=True, color_rgb=C_WHITE)
            p_num.space_before = Pt(12)
            p_unit = tf_l.add_paragraph()
            set_para(p_unit, s_data.get("hero_unit", "智能终端设备累计安全运行量"), font_size=13, bold=False, color_rgb=C_ICE_BLUE)
            p_unit.space_before = Pt(4)
            p_desc = tf_l.add_paragraph()
            set_para(p_desc, s_data.get("hero_desc", "广泛应用于电力、新能源及工业基础设施。"), font_size=11, bold=False, color_rgb=C_WHITE)
            p_desc.space_before = Pt(14)

        # Right Container Card
        right_bg = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(5.73), top_m, right_w, box_h)
        right_bg.fill.solid()
        right_bg.fill.fore_color.rgb = C_LIGHT_BG
        right_bg.line.color.rgb = C_BORDER
        right_bg.line.width = Pt(1)

        tb_r = slide.shapes.add_textbox(Inches(6.0), top_m + Inches(0.35), right_w - Inches(0.5), box_h - Inches(0.7))
        tf_r = tb_r.text_frame
        tf_r.word_wrap = True
        self._set_tf_margins(tf_r, top=8, bottom=8, left=8, right=8)

        if arch.startswith("ARCH_13"):
            offices = s_data.get("offices", ["亚太总部：上海正泰园区", "欧洲总部：德国法兰克福", "北美总部：美国加利福尼亚", "中东总部：阿联酋迪拜"])
            set_para(tf_r.paragraphs[0], s_data.get("network_title", "主要区域总部与研发网点"), font_size=15, bold=True, color_rgb=C_BLUE)
            for o in offices:
                p = tf_r.add_paragraph()
                set_para(p, f"• {o}", font_size=12, bold=False, color_rgb=C_DARK)
                p.space_before = Pt(10)
                p.space_after = Pt(2)
        else:
            bullets = s_data.get("bullets", ["项目背景：核心业务场景与关键改造需求", "解决方案：部署定制化产品与综合解决方案", "商业价值：达成预期运营效益与高可靠回报"])
            set_para(tf_r.paragraphs[0], s_data.get("narrative_title", "核心价值与项目实践拆解"), font_size=15, bold=True, color_rgb=C_BLUE)
            for j, b in enumerate(bullets):
                p = tf_r.add_paragraph()
                set_para(p, f"• {b}", font_size=12, bold=False, color_rgb=C_DARK)
                p.space_before = Pt(12)
                p.space_after = Pt(2)

    def _render_n_column_card_grid(self, slide, s_data: Dict[str, Any], arch: str):
        """Engine 4: Vertical N-Column Card Grid with Dynamic Reflow (ARCH_04, ARCH_05, ARCH_12, ARCH_18, ARCH_24, ARCH_23, ARCH_33)"""
        self._add_body_master(slide, s_data.get("title", ""), s_data.get("category", ""))
        top_m, card_h, left_m = Inches(1.6), Inches(5.0), Inches(0.8)

        if arch.startswith("ARCH_04"):
            cards = s_data.get("kpi_cards", [])
            num_c = max(1, min(len(cards), 4)) if cards else 3
            gap = Inches(0.25) if num_c >= 4 else Inches(0.4)
            card_w = Inches((11.73 - (num_c - 1) * gap.inches) / num_c)
            band_h = Inches(1.35) if num_c >= 4 else Inches(1.5)
            num_fsize = 26 if num_c >= 4 else 32

            for i, card in enumerate(cards[:num_c]):
                cur_left = left_m + i * (card_w + gap)
                bg = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cur_left, top_m, card_w, card_h)
                bg.fill.solid()
                bg.fill.fore_color.rgb = C_LIGHT_BG
                bg.line.color.rgb = C_BORDER
                bg.line.width = Pt(1)

                band = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cur_left, top_m, card_w, band_h)
                band.fill.solid()
                band.fill.fore_color.rgb = C_BLUE
                band.line.fill.background()

                tb_band = slide.shapes.add_textbox(cur_left, top_m + Inches(0.12), card_w, band_h - Inches(0.2))
                tf_band = tb_band.text_frame
                tf_band.word_wrap = True
                self._set_tf_margins(tf_band, top=6, bottom=6, left=6, right=6)
                set_para(tf_band.paragraphs[0], card.get("number", card.get("metric", "")), font_size=num_fsize, bold=True, color_rgb=C_WHITE, align=PP_ALIGN.CENTER)
                p_lbl = tf_band.add_paragraph()
                set_para(p_lbl, card.get("label", ""), font_size=12 if num_c >= 4 else 13, bold=True, color_rgb=C_ICE_BLUE, align=PP_ALIGN.CENTER)
                p_lbl.space_before = Pt(3)

                details = card.get("details", card.get("bullets", []))
                tb_b = slide.shapes.add_textbox(cur_left + Inches(0.15), top_m + band_h + Inches(0.15), card_w - Inches(0.3), card_h - band_h - Inches(0.3))
                tf_b = tb_b.text_frame
                tf_b.word_wrap = True
                self._set_tf_margins(tf_b, top=6, bottom=6, left=6, right=6)
                f_detail = 10.5 if num_c >= 4 else 11.5
                for j, b in enumerate(details):
                    p = tf_b.paragraphs[0] if j == 0 else tf_b.add_paragraph()
                    f_auto = calc_autofit_fontsize(b, base_size=f_detail, min_size=9.0, threshold_len=30)
                    set_para(p, f"• {b}", font_size=f_auto, bold=False, color_rgb=C_DARK)
                    p.space_before = Pt(6 if num_c >= 4 else 8)
                    p.space_after = Pt(2)

        elif arch.startswith("ARCH_05"):
            cols = s_data.get("columns", [])
            num_cols = max(1, min(len(cols), 5)) if cols else 3
            gap = Inches(0.2) if num_cols >= 5 else (Inches(0.25) if num_cols == 4 else Inches(0.35))
            card_w = Inches((11.73 - (num_cols - 1) * gap.inches) / num_cols)
            f_hdr = 11.5 if num_cols >= 5 else (12.5 if num_cols == 4 else 13.5)
            f_body = 9.5 if num_cols >= 5 else (10.5 if num_cols == 4 else 11.5)

            for i, col in enumerate(cols[:num_cols]):
                cur_left = left_m + i * (card_w + gap)
                bg = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cur_left, top_m, card_w, card_h)
                bg.fill.solid()
                bg.fill.fore_color.rgb = C_LIGHT_BG
                bg.line.color.rgb = C_BORDER
                bg.line.width = Pt(1)

                h_bg = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cur_left, top_m, card_w, Inches(0.65))
                h_bg.fill.solid()
                h_bg.fill.fore_color.rgb = C_CARD_HEADER_BG
                h_bg.line.fill.background()

                tb_h = slide.shapes.add_textbox(cur_left + Inches(0.1), top_m + Inches(0.1), card_w - Inches(0.2), Inches(0.5))
                tf_h = tb_h.text_frame
                tf_h.word_wrap = True
                self._set_tf_margins(tf_h, top=4, bottom=4, left=6, right=6)
                set_para(tf_h.paragraphs[0], col.get("header", ""), font_size=f_hdr, bold=True, color_rgb=C_BLUE, align=PP_ALIGN.CENTER)

                bullets = col.get("bullets", [])
                tb_b = slide.shapes.add_textbox(cur_left + Inches(0.15), top_m + Inches(0.8), card_w - Inches(0.3), card_h - Inches(0.95))
                tf_b = tb_b.text_frame
                tf_b.word_wrap = True
                self._set_tf_margins(tf_b, top=6, bottom=6, left=6, right=6)
                for j, b in enumerate(bullets):
                    p = tf_b.paragraphs[0] if j == 0 else tf_b.add_paragraph()
                    f_auto = calc_autofit_fontsize(b, base_size=f_body, min_size=8.5, threshold_len=25)
                    set_para(p, f"• {b}", font_size=f_auto, bold=False, color_rgb=C_DARK)
                    p.space_before = Pt(5 if num_cols >= 5 else 7)
                    p.space_after = Pt(2)

        elif arch.startswith("ARCH_12"):
            members = s_data.get("members", [])
            num_m = max(1, min(len(members), 5)) if members else 3
            gap = Inches(0.2) if num_m >= 5 else (Inches(0.25) if num_m == 4 else Inches(0.35))
            card_w = Inches((11.73 - (num_m - 1) * gap.inches) / num_m)
            f_name = 13.0 if num_m >= 5 else (14.0 if num_m == 4 else 15.5)
            f_cred = 9.5 if num_m >= 5 else (10.0 if num_m == 4 else 10.5)

            for i, m in enumerate(members[:num_m]):
                cur_left = left_m + i * (card_w + gap)
                bg = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cur_left, top_m, card_w, card_h)
                bg.fill.solid()
                bg.fill.fore_color.rgb = C_LIGHT_BG
                bg.line.color.rgb = C_BORDER
                bg.line.width = Pt(1)

                pill = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cur_left + Inches(0.15), top_m + Inches(0.25), card_w - Inches(0.3), Inches(0.42))
                pill.fill.solid()
                pill.fill.fore_color.rgb = C_BLUE
                pill.line.fill.background()
                tf_pill = pill.text_frame
                self._set_tf_margins(tf_pill, top=2, bottom=2, left=4, right=4)
                set_para(tf_pill.paragraphs[0], m.get("role", "核心成员"), font_size=10.5 if num_m >= 5 else 11, bold=True, color_rgb=C_WHITE, align=PP_ALIGN.CENTER)

                tb = slide.shapes.add_textbox(cur_left + Inches(0.15), top_m + Inches(0.8), card_w - Inches(0.3), card_h - Inches(0.95))
                tf = tb.text_frame
                tf.word_wrap = True
                self._set_tf_margins(tf, top=6, bottom=6, left=6, right=6)
                set_para(tf.paragraphs[0], m.get("name", ""), font_size=f_name, bold=True, color_rgb=C_DARK, align=PP_ALIGN.CENTER)
                p_title = tf.add_paragraph()
                set_para(p_title, m.get("title", ""), font_size=10.5 if num_m >= 5 else 11, bold=False, color_rgb=C_BLUE, align=PP_ALIGN.CENTER)
                p_title.space_before = Pt(3)

                for b in m.get("credentials", []):
                    p_c = tf.add_paragraph()
                    f_auto = calc_autofit_fontsize(b, base_size=f_cred, min_size=8.5, threshold_len=20)
                    set_para(p_c, f"• {b}", font_size=f_auto, bold=False, color_rgb=C_MUTED)
                    p_c.space_before = Pt(4 if num_m >= 5 else 6)
                    p_c.space_after = Pt(2)

        elif arch.startswith("ARCH_18"):
            metrics = s_data.get("metrics", [
                {"number": "99.98%", "label": "核心供电可靠率", "trend": "+0.45% YoY", "desc": "关键回路连续安全运行 3000+ 天"},
                {"number": "32.5%", "label": "综合综合节能率", "trend": "+5.2% 提升", "desc": "全周期智慧能效管理降耗"},
                {"number": "140+", "label": "全球服务国家与地区", "trend": "+12 区域拓展", "desc": "本地化营销与服务网络全覆盖"},
                {"number": "48 h", "label": "定制化交付周期", "trend": "-35% 提速", "desc": "智能制造柔性产线极速交付"}
            ])
            num_m = max(1, min(len(metrics), 5))
            gap = Inches(0.2) if num_m >= 5 else (Inches(0.25) if num_m == 4 else Inches(0.35))
            card_w = Inches((11.73 - (num_m - 1) * gap.inches) / num_m)
            f_num = 26 if num_m >= 5 else (28 if num_m == 4 else 32)

            for i, m in enumerate(metrics[:num_m]):
                cur_left = left_m + i * (card_w + gap)
                bg = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cur_left, top_m, card_w, card_h)
                bg.fill.solid()
                bg.fill.fore_color.rgb = C_LIGHT_BG
                bg.line.color.rgb = C_BORDER
                bg.line.width = Pt(1)

                top_bar = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cur_left + Inches(0.15), top_m + Inches(0.15), card_w - Inches(0.3), Inches(0.08))
                top_bar.fill.solid()
                top_bar.fill.fore_color.rgb = C_BLUE
                top_bar.line.fill.background()

                tb_num = slide.shapes.add_textbox(cur_left + Inches(0.1), top_m + Inches(0.35), card_w - Inches(0.2), Inches(1.1))
                tf_num = tb_num.text_frame
                tf_num.word_wrap = True
                self._set_tf_margins(tf_num, top=6, bottom=6, left=6, right=6)
                set_para(tf_num.paragraphs[0], m.get("number", ""), font_size=f_num, bold=True, color_rgb=C_BLUE, align=PP_ALIGN.CENTER)

                trend = m.get("trend", "")
                if trend:
                    pill = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cur_left + Inches(0.2), top_m + Inches(1.5), card_w - Inches(0.4), Inches(0.36))
                    pill.fill.solid()
                    pill.fill.fore_color.rgb = C_GREEN_BG if "+" in trend or "提升" in trend else C_RED_BG
                    pill.line.fill.background()
                    tf_p = pill.text_frame
                    self._set_tf_margins(tf_p, top=2, bottom=2, left=4, right=4)
                    set_para(tf_p.paragraphs[0], trend, font_size=10, bold=True, color_rgb=C_GREEN if "+" in trend or "提升" in trend else C_RED_TEXT, align=PP_ALIGN.CENTER)

                tb_lbl = slide.shapes.add_textbox(cur_left + Inches(0.15), top_m + Inches(1.95), card_w - Inches(0.3), Inches(2.8))
                tf_lbl = tb_lbl.text_frame
                tf_lbl.word_wrap = True
                self._set_tf_margins(tf_lbl, top=6, bottom=6, left=6, right=6)
                set_para(tf_lbl.paragraphs[0], m.get("label", ""), font_size=12.5 if num_m >= 5 else 13.5, bold=True, color_rgb=C_DARK, align=PP_ALIGN.CENTER)
                p_d = tf_lbl.add_paragraph()
                f_desc = calc_autofit_fontsize(m.get("desc", ""), base_size=10.5 if num_m >= 5 else 11.0, min_size=9.0, threshold_len=20)
                set_para(p_d, m.get("desc", ""), font_size=f_desc, bold=False, color_rgb=C_MUTED, align=PP_ALIGN.CENTER)
                p_d.space_before = Pt(6)
                p_d.space_after = Pt(2)

        elif arch.startswith("ARCH_24"):
            pillars = s_data.get("pillars", [
                {"en_title": "MISSION", "cn_title": "企业使命", "slogan": "让电力能源更安全、绿色、便捷、高效", "details": ["以客户为中心，提供高品质智慧能源解决方案", "赋能全球清洁能源转型与工业数智化升级", "推动绿色低碳发展与全生命周期能效服务"], "commitment": "2030 绿色低碳战略承诺  |  赋能全球产业转型"},
                {"en_title": "VISION", "cn_title": "企业愿景", "slogan": "成为全球领先的智慧能源解决方案提供商", "details": ["打造绿色低碳与数字化双轮驱动的产业生态群", "成为备受全球信赖与尊重的可持续发展标杆", "构建开放协同、共生共赢的能源互联网生态"], "commitment": "全球 140+ 国家业务覆盖  |  世界一流品牌"},
                {"en_title": "VALUES", "cn_title": "核心价值观", "slogan": "客户导向、创新驱动、诚信立业、共创共享", "details": ["始终以客户价值创造为一切业务出发点", "坚持科技创新与组织活力，引领行业技术迭代", "恪守诚信合规经营，与全球生态伙伴共创共享"], "commitment": "客户第一  |  创新驱动  |  共赢未来"}
            ])
            num_p = max(1, min(len(pillars), 4))
            gap = Inches(0.25) if num_p >= 4 else Inches(0.4)
            card_w = Inches((11.73 - (num_p - 1) * gap.inches) / num_p)

            for i, p in enumerate(pillars[:num_p]):
                cur_left = left_m + i * (card_w + gap)
                bg = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cur_left, top_m, card_w, card_h)
                bg.fill.solid()
                bg.fill.fore_color.rgb = C_LIGHT_BG
                bg.line.color.rgb = C_BORDER
                bg.line.width = Pt(1)

                # English Pill
                en_pill = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cur_left + Inches(0.15), top_m + Inches(0.2), card_w - Inches(0.3), Inches(0.36))
                en_pill.fill.solid()
                en_pill.fill.fore_color.rgb = C_BLUE_BG
                en_pill.line.fill.background()
                tf_en = en_pill.text_frame
                self._set_tf_margins(tf_en, top=2, bottom=2, left=4, right=4)
                set_para(tf_en.paragraphs[0], p.get("en_title", ""), font_size=10.5 if num_p >= 4 else 11, bold=True, color_rgb=C_BLUE, align=PP_ALIGN.CENTER)

                # Chinese Title
                tb_title = slide.shapes.add_textbox(cur_left + Inches(0.15), top_m + Inches(0.62), card_w - Inches(0.3), Inches(0.45))
                tf_title = tb_title.text_frame
                tf_title.word_wrap = True
                self._set_tf_margins(tf_title, top=2, bottom=2, left=4, right=4)
                set_para(tf_title.paragraphs[0], p.get("cn_title", ""), font_size=16 if num_p >= 4 else 17, bold=True, color_rgb=C_BLUE, align=PP_ALIGN.CENTER)

                # Slogan Card Box
                slog_box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cur_left + Inches(0.12), top_m + Inches(1.15), card_w - Inches(0.24), Inches(0.85))
                slog_box.fill.solid()
                slog_box.fill.fore_color.rgb = C_WHITE
                slog_box.line.color.rgb = RGBColor(180, 210, 255)
                slog_box.line.width = Pt(1)
                tf_slog = slog_box.text_frame
                tf_slog.word_wrap = True
                tf_slog.vertical_anchor = MSO_ANCHOR.MIDDLE
                self._set_tf_margins(tf_slog, top=4, bottom=4, left=6, right=6)
                set_para(tf_slog.paragraphs[0], f"“{p.get('slogan', '')}”", font_size=11 if num_p >= 4 else 12.0, bold=True, color_rgb=C_DARK, align=PP_ALIGN.CENTER)

                # Details / Tenets Box
                tb_det = slide.shapes.add_textbox(cur_left + Inches(0.12), top_m + Inches(2.1), card_w - Inches(0.24), Inches(2.0))
                tf_det = tb_det.text_frame
                tf_det.word_wrap = True
                self._set_tf_margins(tf_det, top=4, bottom=4, left=6, right=6)
                for d_idx, d in enumerate(p.get("details", [])):
                    p_d = tf_det.paragraphs[0] if d_idx == 0 else tf_det.add_paragraph()
                    f_auto = calc_autofit_fontsize(d, base_size=10.0 if num_p >= 4 else 11.0, min_size=8.5, threshold_len=24)
                    set_para(p_d, f"• {d}", font_size=f_auto, bold=False, color_rgb=C_DARK)
                    p_d.space_before = Pt(14)
                    p_d.space_after = Pt(2)

                # Bottom Commitment Tag
                cmt_box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cur_left + Inches(0.12), top_m + Inches(4.2), card_w - Inches(0.24), Inches(0.6))
                cmt_box.fill.solid()
                cmt_box.fill.fore_color.rgb = C_BLUE_BG
                cmt_box.line.color.rgb = RGBColor(180, 210, 255)
                cmt_box.line.width = Pt(1)
                tf_cmt = cmt_box.text_frame
                tf_cmt.word_wrap = True
                tf_cmt.vertical_anchor = MSO_ANCHOR.MIDDLE
                self._set_tf_margins(tf_cmt, top=2, bottom=2, left=4, right=4)
                set_para(tf_cmt.paragraphs[0], p.get("commitment", "2030 绿色低碳战略承诺  |  赋能产业转型"), font_size=9.5 if num_p >= 4 else 10.0, bold=True, color_rgb=C_BLUE, align=PP_ALIGN.CENTER)

        elif arch.startswith("ARCH_23"):
            risks = s_data.get("risks", [
                {"level": "高风险", "title": "技术集成与接口兼容风险", "desc": "异构系统协议标准不统一", "impact": "★★★★★ 极高", "probability": "高 (35%)", "response": "制定标准化网关协议中间件", "prevent": "建立统一物模型标准与跨系统联调机制", "owner": "研发与技术 PMO", "timeline": "T+30天闭环"},
                {"level": "中风险", "title": "工期排程与协同延误", "desc": "涉及多个施工方交叉作业", "impact": "★★★★☆ 显著", "probability": "中 (20%)", "response": "设立联合 PMO 与每日站会机制", "prevent": "推行关键路径甘特图预警与资源动态调配", "owner": "工程管理部", "timeline": "全程常态化"},
                {"level": "低风险", "title": "运维人员操作培训门槛", "desc": "新型数字化系统操作习惯", "impact": "★★☆☆☆ 轻微", "probability": "低 (10%)", "response": "编制图文/视频微课与实操手册", "prevent": "上线模拟演练考核系统，实现持证上岗", "owner": "客户成功部", "timeline": "交付前 2 周"}
            ])
            num_r = max(1, min(len(risks), 4))
            gap = Inches(0.25) if num_r >= 4 else Inches(0.4)
            card_w = Inches((11.73 - (num_r - 1) * gap.inches) / num_r)

            for i, r in enumerate(risks[:num_r]):
                cur_left = left_m + i * (card_w + gap)
                lvl = r.get("level", "中风险")
                lvl_color = C_RED_TEXT if "高" in lvl else (C_BLUE if "低" in lvl else C_ORANGE)
                lvl_bg = C_RED_BG if "高" in lvl else (C_BLUE_BG if "低" in lvl else RGBColor(255, 245, 230))
                
                bg = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cur_left, top_m, card_w, card_h)
                bg.fill.solid()
                bg.fill.fore_color.rgb = C_LIGHT_BG
                bg.line.color.rgb = C_BORDER
                bg.line.width = Pt(1)
                
                # Risk Badge
                badge = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cur_left + Inches(0.15), top_m + Inches(0.2), card_w - Inches(0.3), Inches(0.38))
                badge.fill.solid()
                badge.fill.fore_color.rgb = lvl_bg
                badge.line.color.rgb = lvl_color
                badge.line.width = Pt(1)
                tf_bdg = badge.text_frame
                self._set_tf_margins(tf_bdg, top=2, bottom=2, left=4, right=4)
                set_para(tf_bdg.paragraphs[0], lvl, font_size=11 if num_r >= 4 else 12, bold=True, color_rgb=lvl_color, align=PP_ALIGN.CENTER)
                
                # Title & Description Box
                tb = slide.shapes.add_textbox(cur_left + Inches(0.15), top_m + Inches(0.65), card_w - Inches(0.3), Inches(1.55))
                tf = tb.text_frame
                tf.word_wrap = True
                self._set_tf_margins(tf, top=4, bottom=4, left=4, right=4)
                set_para(tf.paragraphs[0], r.get("title", ""), font_size=12.5 if num_r >= 4 else 13.5, bold=True, color_rgb=C_DARK)
                p_d = tf.add_paragraph()
                set_para(p_d, r.get("desc", ""), font_size=10.0 if num_r >= 4 else 10.5, bold=False, color_rgb=C_MUTED)
                p_d.space_before = Pt(4)
                
                p_dim = tf.add_paragraph()
                dim_str = f"影响: {r.get('impact', '极高')}  |  概率: {r.get('probability', '35%')}"
                set_para(p_dim, dim_str, font_size=9.5 if num_r >= 4 else 10.0, bold=True, color_rgb=lvl_color)
                p_dim.space_before = Pt(6)
                
                # Strategy Response Box
                resp_box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cur_left + Inches(0.12), top_m + Inches(2.3), card_w - Inches(0.24), Inches(2.5))
                resp_box.fill.solid()
                resp_box.fill.fore_color.rgb = C_WHITE
                resp_box.line.color.rgb = C_BORDER
                resp_box.line.width = Pt(1)
                
                tb_resp = slide.shapes.add_textbox(cur_left + Inches(0.15), top_m + Inches(2.35), card_w - Inches(0.3), Inches(2.4))
                tf_resp = tb_resp.text_frame
                tf_resp.word_wrap = True
                self._set_tf_margins(tf_resp, top=6, bottom=6, left=6, right=6)
                set_para(tf_resp.paragraphs[0], "【应对对策与落地预案】", font_size=11, bold=True, color_rgb=C_BLUE)
                
                p_r = tf_resp.add_paragraph()
                f_resp = calc_autofit_fontsize(r.get("response", ""), base_size=10.0 if num_r >= 4 else 10.5, min_size=8.5, threshold_len=24)
                set_para(p_r, f"• 核心对策: {r.get('response', '')}", font_size=f_resp, bold=False, color_rgb=C_DARK)
                p_r.space_before = Pt(8)
                
                p_prev = tf_resp.add_paragraph()
                prevent_txt = r.get("prevent", "建立多方联合评审与标准化接口联调机制")
                f_prev = calc_autofit_fontsize(prevent_txt, base_size=9.5 if num_r >= 4 else 10.0, min_size=8.0, threshold_len=24)
                set_para(p_prev, f"• 防控机制: {prevent_txt}", font_size=f_prev, bold=False, color_rgb=C_MUTED)
                p_prev.space_before = Pt(8)
                
                p_own = tf_resp.add_paragraph()
                own_txt = f"责任: {r.get('owner', '研发与交付 PMO')} | 时限: {r.get('timeline', 'T+30天闭环')}"
                set_para(p_own, own_txt, font_size=9.0 if num_r >= 4 else 9.5, bold=True, color_rgb=C_BLUE)
                p_own.space_before = Pt(12)

        else: # ARCH_33
            honors = s_data.get("honors", [
                {"badge": "国家级", "title": "国家科学技术进步奖", "org": "中华人民共和国国务院", "metric": "连续 5 年获奖"},
                {"badge": "国际化", "title": "IEC / UL 全球双重认证", "org": "国际电工委员会 / UL 认证", "metric": "100% 覆盖导出产品"},
                {"badge": "数智化", "title": "国家级智能制造示范工厂", "org": "工业和信息化部", "metric": "行业首批示范"},
                {"badge": "绿色零碳", "title": "零碳工厂与ESG A级认证", "org": "国际权威评级机构", "metric": "绿色电力率 100%"}
            ])
            num_h = max(1, min(len(honors), 5))
            gap = Inches(0.2) if num_h >= 5 else (Inches(0.25) if num_h == 4 else Inches(0.35))
            card_w = Inches((11.73 - (num_h - 1) * gap.inches) / num_h)

            for i, h in enumerate(honors[:num_h]):
                cur_left = left_m + i * (card_w + gap)
                bg = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cur_left, top_m, card_w, card_h)
                bg.fill.solid()
                bg.fill.fore_color.rgb = C_LIGHT_BG
                bg.line.color.rgb = C_BORDER
                bg.line.width = Pt(1)

                oval_w = Inches(0.75) if num_h >= 5 else Inches(0.8)
                bdg = slide.shapes.add_shape(MSO_SHAPE.OVAL, cur_left + card_w / 2 - oval_w / 2, top_m + Inches(0.3), oval_w, oval_w)
                bdg.fill.solid()
                bdg.fill.fore_color.rgb = C_BLUE_BG
                bdg.line.color.rgb = C_BLUE
                bdg.line.width = Pt(1)
                tf_bdg = bdg.text_frame
                self._set_tf_margins(tf_bdg, top=2, bottom=2, left=2, right=2)
                set_para(tf_bdg.paragraphs[0], h.get("badge", "荣誉"), font_size=10 if num_h >= 5 else 10.5, bold=True, color_rgb=C_BLUE, align=PP_ALIGN.CENTER)

                tb = slide.shapes.add_textbox(cur_left + Inches(0.1), top_m + Inches(1.2), card_w - Inches(0.2), Inches(3.5))
                tf = tb.text_frame
                tf.word_wrap = True
                self._set_tf_margins(tf, top=6, bottom=6, left=6, right=6)
                set_para(tf.paragraphs[0], h.get("title", ""), font_size=12.5 if num_h >= 5 else 13.5, bold=True, color_rgb=C_BLUE, align=PP_ALIGN.CENTER)
                p_org = tf.add_paragraph()
                set_para(p_org, h.get("org", ""), font_size=9.5 if num_h >= 5 else 10.5, bold=False, color_rgb=C_DARK, align=PP_ALIGN.CENTER)
                p_org.space_before = Pt(5)
                p_m = tf.add_paragraph()
                set_para(p_m, f"★ {h.get('metric', '')}", font_size=10.5 if num_h >= 5 else 11, bold=True, color_rgb=C_GREEN, align=PP_ALIGN.CENTER)
                p_m.space_before = Pt(8)
                p_m.space_after = Pt(2)

    def _render_horizontal_pipeline(self, slide, s_data: Dict[str, Any], arch: str):
        """Engine 5: Sequential Pipeline / Roadmap with Dynamic Reflow (ARCH_06, ARCH_25, ARCH_27, ARCH_28, ARCH_30)"""
        self._add_body_master(slide, s_data.get("title", ""), s_data.get("category", ""))
        top_m, left_m = Inches(1.6), Inches(0.8)

        if arch.startswith("ARCH_06"):
            stages = s_data.get("stages", [
                {"phase": "第一阶段", "title": "规划启动", "desc": "明确战略目标与需求"},
                {"phase": "第二阶段", "title": "试点验证", "desc": "关键业务验证与标准沉淀"},
                {"phase": "第三阶段", "title": "全面推广", "desc": "全链路赋能与规模化推广"},
                {"phase": "第四阶段", "title": "持续优化", "desc": "长效机制建设与运营迭代"}
            ])
            num_s = max(1, min(len(stages), 5))
            gap = Inches(0.2) if num_s >= 5 else Inches(0.3)
            card_w = Inches((11.73 - (num_s - 1) * gap.inches) / num_s)

            line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left_m + Inches(0.4), Inches(3.8), Inches(11.73 - 0.8), Inches(0.04))
            line.fill.solid()
            line.fill.fore_color.rgb = C_BLUE
            line.line.fill.background()

            for i, stg in enumerate(stages[:num_s]):
                cur_left = left_m + i * (card_w + gap)
                circle = slide.shapes.add_shape(MSO_SHAPE.OVAL, cur_left + card_w / 2 - Inches(0.2), Inches(3.62), Inches(0.4), Inches(0.4))
                circle.fill.solid()
                circle.fill.fore_color.rgb = C_CYAN
                circle.line.fill.background()

                bg = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cur_left, Inches(1.6), card_w, Inches(1.8))
                bg.fill.solid()
                bg.fill.fore_color.rgb = C_LIGHT_BG
                bg.line.color.rgb = C_BORDER
                bg.line.width = Pt(1)

                tb_top = slide.shapes.add_textbox(cur_left + Inches(0.1), Inches(1.7), card_w - Inches(0.2), Inches(1.5))
                tf_top = tb_top.text_frame
                tf_top.word_wrap = True
                self._set_tf_margins(tf_top, top=4, bottom=4, left=4, right=4)
                set_para(tf_top.paragraphs[0], stg.get("phase", f"阶段 0{i+1}"), font_size=11 if num_s >= 5 else 12, bold=True, color_rgb=C_BLUE, align=PP_ALIGN.CENTER)
                p_t = tf_top.add_paragraph()
                set_para(p_t, stg.get("title", ""), font_size=12.5 if num_s >= 5 else 14, bold=True, color_rgb=C_DARK, align=PP_ALIGN.CENTER)
                p_t.space_before = Pt(3)

                tb_bot = slide.shapes.add_textbox(cur_left, Inches(4.3), card_w, Inches(2.2))
                tf_bot = tb_bot.text_frame
                tf_bot.word_wrap = True
                self._set_tf_margins(tf_bot, top=4, bottom=4, left=4, right=4)
                f_desc = calc_autofit_fontsize(stg.get("desc", ""), base_size=10.0 if num_s >= 5 else 11.0, min_size=8.5, threshold_len=20)
                set_para(tf_bot.paragraphs[0], stg.get("desc", ""), font_size=f_desc, bold=False, color_rgb=C_MUTED, align=PP_ALIGN.CENTER)

        elif arch.startswith("ARCH_25"):
            steps = s_data.get("steps", [
                {"phase": "01", "title": "现场调研", "subtitle": "需求摸底与配电勘测", "actions": ["电力拓扑实地测绘与摸底", "用电设备安全隐患排查", "全天候能耗负荷数据采集"], "deliverable": "《现场勘测诊断报告》", "duration": "1-2 周"},
                {"phase": "02", "title": "系统设计", "subtitle": "元器件选型与图纸深化", "actions": ["断路器与配电设备精准选型", "BIM 3D 机房布局深化设计", "定制化通信协议拓扑规划"], "deliverable": "《电气系统深化设计蓝图》", "duration": "2-3 周"},
                {"phase": "03", "title": "智能排产", "subtitle": "灯塔工厂柔性定制生产", "actions": ["智能制造全流程自动化装配", "100% 关键元器件质量质检", "全链路数字化追溯码生成"], "deliverable": "《产品出厂合格质检报告》", "duration": "1 周"},
                {"phase": "04", "title": "现场联调", "subtitle": "通电联调与云平台接入", "actions": ["现场设备安装与母排搭接", "边缘网关数据采集上云联调", "保护定值校验与带电试运行"], "deliverable": "《系统联调验收签署单》", "duration": "1 周"},
                {"phase": "05", "title": "智慧运营", "subtitle": "全生命周期云端运维", "actions": ["7x24h 智能能效与负荷优化", "AI 故障预测性维护与预警", "定期巡检与主动式备件保障"], "deliverable": "《年度智慧能效运营报告》", "duration": "长效运营"}
            ])
            num_s = max(1, min(len(steps), 6))
            gap = Inches(0.2) if num_s >= 5 else Inches(0.35)
            card_w = Inches((11.73 - (num_s - 1) * gap.inches) / num_s)
            card_h = Inches(5.0)

            for i, st in enumerate(steps[:num_s]):
                cur_left = left_m + i * (card_w + gap)
                bg = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cur_left, top_m, card_w, card_h)
                bg.fill.solid()
                bg.fill.fore_color.rgb = C_LIGHT_BG
                bg.line.color.rgb = C_BORDER
                bg.line.width = Pt(1)

                # Step Badge Pill
                pill = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cur_left + Inches(0.12), top_m + Inches(0.2), card_w - Inches(0.24), Inches(0.42))
                pill.fill.solid()
                pill.fill.fore_color.rgb = C_BLUE
                pill.line.fill.background()
                tf_pill = pill.text_frame
                self._set_tf_margins(tf_pill, top=2, bottom=2, left=4, right=4)
                set_para(tf_pill.paragraphs[0], f"STEP {st.get('phase', f'0{i+1}')}", font_size=10.5 if num_s >= 5 else 11.5, bold=True, color_rgb=C_WHITE, align=PP_ALIGN.CENTER)

                # Title & Subtitle Box
                tb_hdr = slide.shapes.add_textbox(cur_left + Inches(0.08), top_m + Inches(0.68), card_w - Inches(0.16), Inches(0.85))
                tf_hdr = tb_hdr.text_frame
                tf_hdr.word_wrap = True
                self._set_tf_margins(tf_hdr, top=2, bottom=2, left=2, right=2)
                set_para(tf_hdr.paragraphs[0], st.get("title", ""), font_size=12.5 if num_s >= 5 else 14, bold=True, color_rgb=C_DARK, align=PP_ALIGN.CENTER)
                p_sub = tf_hdr.add_paragraph()
                f_sub = calc_autofit_fontsize(st.get("subtitle", st.get("desc", "")), base_size=9.5 if num_s >= 5 else 10.5, min_size=8.0, threshold_len=16)
                set_para(p_sub, st.get("subtitle", st.get("desc", "")), font_size=f_sub, bold=False, color_rgb=C_BLUE, align=PP_ALIGN.CENTER)
                p_sub.space_before = Pt(2)

                # Key Actions Box
                actions_box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cur_left + Inches(0.1), top_m + Inches(1.58), card_w - Inches(0.2), Inches(1.95))
                actions_box.fill.solid()
                actions_box.fill.fore_color.rgb = C_WHITE
                actions_box.line.color.rgb = C_BORDER
                actions_box.line.width = Pt(1)

                tb_acts = slide.shapes.add_textbox(cur_left + Inches(0.12), top_m + Inches(1.62), card_w - Inches(0.24), Inches(1.85))
                tf_acts = tb_acts.text_frame
                tf_acts.word_wrap = True
                self._set_tf_margins(tf_acts, top=4, bottom=4, left=4, right=4)
                
                act_list = st.get("actions", [])
                if not act_list and st.get("desc"):
                    act_list = [st.get("desc")]
                    
                for a_idx, act in enumerate(act_list[:3]):
                    p_a = tf_acts.paragraphs[0] if a_idx == 0 else tf_acts.add_paragraph()
                    f_a = calc_autofit_fontsize(act, base_size=9.0 if num_s >= 5 else 9.5, min_size=7.5, threshold_len=18)
                    set_para(p_a, f"• {act}", font_size=f_a, bold=False, color_rgb=C_DARK)
                    p_a.space_before = Pt(9)
                    p_a.space_after = Pt(2)

                # Bottom Deliverable Box
                deliv_box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cur_left + Inches(0.1), top_m + Inches(3.62), card_w - Inches(0.2), Inches(1.2))
                deliv_box.fill.solid()
                deliv_box.fill.fore_color.rgb = C_BLUE_BG
                deliv_box.line.color.rgb = RGBColor(180, 210, 255)
                deliv_box.line.width = Pt(1)

                tb_deliv = slide.shapes.add_textbox(cur_left + Inches(0.12), top_m + Inches(3.65), card_w - Inches(0.24), Inches(1.1))
                tf_deliv = tb_deliv.text_frame
                tf_deliv.word_wrap = True
                self._set_tf_margins(tf_deliv, top=2, bottom=2, left=2, right=2)
                set_para(tf_deliv.paragraphs[0], "【核心交付】", font_size=9.5 if num_s >= 5 else 10.0, bold=True, color_rgb=C_BLUE, align=PP_ALIGN.CENTER)
                
                p_del = tf_deliv.add_paragraph()
                f_del = calc_autofit_fontsize(st.get("deliverable", "《阶段交付物》"), base_size=9.0 if num_s >= 5 else 9.5, min_size=7.5, threshold_len=18)
                set_para(p_del, st.get("deliverable", "《阶段交付物》"), font_size=f_del, bold=False, color_rgb=C_DARK, align=PP_ALIGN.CENTER)
                p_del.space_before = Pt(2)

                p_dur = tf_deliv.add_paragraph()
                set_para(p_dur, f"周期: {st.get('duration', '1-2周')}", font_size=8.5 if num_s >= 5 else 9.0, bold=True, color_rgb=C_MUTED, align=PP_ALIGN.CENTER)
                p_dur.space_before = Pt(2)

                if i < num_s - 1:
                    chv_w = Inches(0.14) if num_s >= 5 else Inches(0.18)
                    chv = slide.shapes.add_shape(MSO_SHAPE.CHEVRON, cur_left + card_w + (gap - chv_w) / 2, top_m + Inches(2.25), chv_w, Inches(0.35))
                    chv.fill.solid()
                    chv.fill.fore_color.rgb = C_CYAN
                    chv.line.fill.background()

        elif arch.startswith("ARCH_27"):
            steps = s_data.get("steps", [
                {"ver": "2.0", "title": "基础电气化", "desc": "传统元器件与被动保护"},
                {"ver": "3.0", "title": "自动化联控", "desc": "PLC 逻辑控制与本地监测"},
                {"ver": "4.0", "title": "数智化能效", "desc": "云边协同与 AI 优化调度"},
                {"ver": "5.0", "title": "零碳自愈", "desc": "全自愈微网与生态赋能"}
            ])
            num_s = max(1, min(len(steps), 5))
            gap = Inches(0.2) if num_s >= 5 else Inches(0.35)
            card_w = Inches((11.73 - (num_s - 1) * gap.inches) / num_s)
            min_h, max_h = Inches(2.2), Inches(4.9)
            heights = [min_h + (max_h - min_h) * (i / max(1, num_s - 1)) for i in range(num_s)]

            for i, st in enumerate(steps[:num_s]):
                cur_left = left_m + i * (card_w + gap)
                cur_h = heights[i]
                cur_top = top_m + (Inches(5.0) - cur_h)
                is_last = (i == num_s - 1)

                bg = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cur_left, cur_top, card_w, cur_h)
                bg.fill.solid()
                bg.fill.fore_color.rgb = C_BLUE_BG
                bg.line.color.rgb = C_BLUE if is_last else C_BORDER
                bg.line.width = Pt(1.5 if is_last else 1)

                cap = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cur_left, cur_top, card_w, Inches(0.55))
                cap.fill.solid()
                cap.fill.fore_color.rgb = C_BLUE if is_last else RGBColor(70, 120, 230)
                cap.line.fill.background()
                tf_cap = cap.text_frame
                self._set_tf_margins(tf_cap, top=3, bottom=3, left=4, right=4)
                set_para(tf_cap.paragraphs[0], f"V {st.get('ver', '')}", font_size=12 if num_s >= 5 else 13, bold=True, color_rgb=C_WHITE, align=PP_ALIGN.CENTER)

                tb = slide.shapes.add_textbox(cur_left + Inches(0.1), cur_top + Inches(0.65), card_w - Inches(0.2), cur_h - Inches(0.75))
                tf = tb.text_frame
                tf.word_wrap = True
                self._set_tf_margins(tf, top=6, bottom=6, left=6, right=6)
                set_para(tf.paragraphs[0], st.get("title", ""), font_size=12.5 if num_s >= 5 else 14, bold=True, color_rgb=C_DARK, align=PP_ALIGN.CENTER)
                p_d = tf.add_paragraph()
                f_desc = calc_autofit_fontsize(st.get("desc", ""), base_size=10.0 if num_s >= 5 else 11.0, min_size=8.5, threshold_len=20)
                set_para(p_d, st.get("desc", ""), font_size=f_desc, bold=False, color_rgb=C_MUTED, align=PP_ALIGN.CENTER)
                p_d.space_before = Pt(5)

        elif arch.startswith("ARCH_28"):
            gates = s_data.get("gates", [
                {"gate": "G1 概念门禁", "title": "需求定义与可行性立项"},
                {"gate": "G2 计划门禁", "title": "系统架构与包方案冻结"},
                {"gate": "G3 开发门禁", "title": "样品试制与全测试验证"},
                {"gate": "G4 验证门禁", "title": "试点试运行与准入评估"},
                {"gate": "G5 发布门禁", "title": "量产上市与全球商业化"}
            ])
            num_g = max(1, min(len(gates), 6))
            gap = Inches(0.18) if num_g >= 6 else (Inches(0.22) if num_g == 5 else Inches(0.3))
            card_w = Inches((11.73 - (num_g - 1) * gap.inches) / num_g)

            line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), top_m + Inches(0.5), Inches(11.73), Inches(0.04))
            line.fill.solid()
            line.fill.fore_color.rgb = C_BORDER
            line.line.fill.background()

            for i, g in enumerate(gates[:num_g]):
                cur_left = left_m + i * (card_w + gap)
                d_w = Inches(0.55) if num_g >= 6 else Inches(0.65)
                node = slide.shapes.add_shape(MSO_SHAPE.DIAMOND, cur_left + card_w / 2 - d_w / 2, top_m + Inches(0.2), d_w, d_w)
                node.fill.solid()
                node.fill.fore_color.rgb = C_BLUE if i < num_g - 1 else C_CYAN
                node.line.fill.background()

                bg = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cur_left, top_m + Inches(1.1), card_w, Inches(3.8))
                bg.fill.solid()
                bg.fill.fore_color.rgb = C_LIGHT_BG
                bg.line.color.rgb = C_BORDER
                bg.line.width = Pt(1)

                tb = slide.shapes.add_textbox(cur_left + Inches(0.1), top_m + Inches(1.2), card_w - Inches(0.2), Inches(3.5))
                tf = tb.text_frame
                tf.word_wrap = True
                self._set_tf_margins(tf, top=6, bottom=6, left=4, right=4)
                set_para(tf.paragraphs[0], g.get("gate", f"G{i+1}"), font_size=11 if num_g >= 6 else 12, bold=True, color_rgb=C_BLUE, align=PP_ALIGN.CENTER)
                p_t = tf.add_paragraph()
                f_title = calc_autofit_fontsize(g.get("title", ""), base_size=10.5 if num_g >= 6 else 11.5, min_size=8.5, threshold_len=15)
                set_para(p_t, g.get("title", ""), font_size=f_title, bold=True, color_rgb=C_DARK, align=PP_ALIGN.CENTER)
                p_t.space_before = Pt(5)

        else: # ARCH_30
            milestones = s_data.get("milestones", [
                {"year": "2024", "title": "战略升级与智慧能效平台发布", "desc": "正泰发布全新智慧能效物联网平台，奠定数智化转型根基"},
                {"year": "2025", "title": "全球交付网络突破与生态共建", "desc": "海外业务增长超 40%，全产业生态伙伴突破 500 家"},
                {"year": "2026", "title": "2026 VI 规范全面重构与赋能", "desc": "全面推行企业级标准化交付，实现产品与营销端全面焕新"}
            ])
            num_ms = max(1, min(len(milestones), 4))
            gap_y_in = 0.15 if num_ms >= 4 else 0.25
            card_h_in = (5.0 - (num_ms - 1) * gap_y_in) / num_ms
            gap_y = Inches(gap_y_in)
            card_h_inch = Inches(card_h_in)

            for idx, ms in enumerate(milestones[:num_ms]):
                cur_top = top_m + idx * (card_h_inch + gap_y)
                year_pill = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), cur_top, Inches(2.2), card_h_inch)
                year_pill.fill.solid()
                year_pill.fill.fore_color.rgb = C_BLUE
                year_pill.line.fill.background()
                tf_yp = year_pill.text_frame
                self._set_tf_margins(tf_yp, top=6, bottom=6, left=6, right=6)
                set_para(tf_yp.paragraphs[0], ms.get("year", ""), font_size=20 if num_ms >= 4 else 24, bold=True, color_rgb=C_WHITE, align=PP_ALIGN.CENTER)

                card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(3.2), cur_top, Inches(9.33), card_h_inch)
                card.fill.solid()
                card.fill.fore_color.rgb = C_LIGHT_BG
                card.line.color.rgb = C_BORDER
                card.line.width = Pt(1)

                tb = slide.shapes.add_textbox(Inches(3.5), cur_top + Inches(0.12), Inches(8.8), card_h_inch - Inches(0.24))
                tf = tb.text_frame
                tf.word_wrap = True
                self._set_tf_margins(tf, top=6, bottom=6, left=6, right=6)
                set_para(tf.paragraphs[0], ms.get("title", ""), font_size=13 if num_ms >= 4 else 14, bold=True, color_rgb=C_DARK)
                p_d = tf.add_paragraph()
                f_desc = calc_autofit_fontsize(ms.get("desc", ""), base_size=10.5 if num_ms >= 4 else 11.0, min_size=9.0, threshold_len=40)
                set_para(p_d, ms.get("desc", ""), font_size=f_desc, bold=False, color_rgb=C_MUTED)
                p_d.space_before = Pt(4)

    def _render_funnel_stepped(self, slide, s_data: Dict[str, Any], arch: str):
        """Engine 6: Stepped Funnel Conversion (ARCH_26)"""
        self._add_body_master(slide, s_data.get("title", "营销转化与客户全生命周期漏斗"), s_data.get("category", "漏斗模型"))
        top_m = Inches(1.6)
        stages = s_data.get("stages", [
            {"stage": "1. 泛客户触达 (Awareness)", "value": "10,000+", "desc": "品牌曝光与白皮书下载触达"},
            {"stage": "2. 意向商机挖掘 (Interest)", "value": "2,500+", "desc": "技术交流与现场需求对接"},
            {"stage": "3. 方案PoC验证 (Evaluation)", "value": "600+", "desc": "定制化方案PoC与试点验证"},
            {"stage": "4. 最终签约落地 (Conversion)", "value": "180+", "desc": "商业合同签署与项目交付"}
        ])
        funnel_widths = [Inches(11.2), Inches(9.2), Inches(7.2), Inches(5.2)]
        colors = [C_BLUE, RGBColor(35, 120, 255), C_CYAN, C_ICE_BLUE]
        text_colors = [C_WHITE, C_WHITE, C_DARK, C_BLUE]

        for idx, stg in enumerate(stages[:4]):
            cur_w = funnel_widths[idx]
            cur_left = Inches(6.66) - (cur_w / 2)
            cur_top = top_m + idx * Inches(1.2)

            bar = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cur_left, cur_top, cur_w, Inches(1.05))
            bar.fill.solid()
            bar.fill.fore_color.rgb = colors[idx]
            bar.line.color.rgb = C_BORDER if idx == 3 else C_BLUE
            bar.line.width = Pt(1)

            tb = slide.shapes.add_textbox(cur_left + Inches(0.3), cur_top + Inches(0.1), cur_w - Inches(0.6), Inches(0.85))
            tf = tb.text_frame
            tf.word_wrap = True
            self._set_tf_margins(tf, top=4, bottom=4, left=6, right=6)
            set_para(tf.paragraphs[0], f"{stg.get('stage', '')}  —  【{stg.get('value', '')}】", font_size=13.5, bold=True, color_rgb=text_colors[idx], align=PP_ALIGN.CENTER)
            p_d = tf.add_paragraph()
            set_para(p_d, stg.get("desc", ""), font_size=11, bold=False, color_rgb=text_colors[idx], align=PP_ALIGN.CENTER)
            p_d.space_before = Pt(3)

    def _render_matrix_2x2_quadrant(self, slide, s_data: Dict[str, Any], arch: str):
        """Engine 7: 2x2 SWOT / TOWS Matrix (ARCH_20)"""
        self._add_body_master(slide, s_data.get("title", "SWOT 战略态势与业务诊断矩阵"), s_data.get("category", "战略诊断"))
        top_m, quad_w, quad_h = Inches(1.6), Inches(5.7), Inches(2.4)
        gap_x, gap_y = Inches(0.33), Inches(0.2)

        quadrants = [
            (0, 0, "S", "优势 (Strengths)", C_BLUE_BG, C_BLUE, C_BLUE, "strengths"),
            (0, 1, "W", "劣势 (Weaknesses)", C_RED_BG, C_RED_TEXT, C_RED_TEXT, "weaknesses"),
            (1, 0, "O", "机会 (Opportunities)", C_GREEN_BG, C_GREEN, C_GREEN, "opportunities"),
            (1, 1, "T", "威胁 (Threats)", C_LIGHT_BG, C_BORDER, C_DARK, "threats"),
        ]

        for r, c, letter, q_title, q_bg, q_border, q_color, key in quadrants:
            cur_left = Inches(0.8) + c * (quad_w + gap_x)
            cur_top = top_m + r * (quad_h + gap_y)

            bg = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cur_left, cur_top, quad_w, quad_h)
            bg.fill.solid()
            bg.fill.fore_color.rgb = q_bg
            bg.line.color.rgb = q_border
            bg.line.width = Pt(1)

            badge = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cur_left + Inches(0.15), cur_top + Inches(0.15), Inches(0.5), Inches(0.4))
            badge.fill.solid()
            badge.fill.fore_color.rgb = q_color if key != "threats" else C_MUTED
            badge.line.fill.background()
            tf_bdg = badge.text_frame
            self._set_tf_margins(tf_bdg, top=2, bottom=2, left=2, right=2)
            set_para(tf_bdg.paragraphs[0], letter, font_size=14, bold=True, color_rgb=C_WHITE, align=PP_ALIGN.CENTER)

            tb_t = slide.shapes.add_textbox(cur_left + Inches(0.75), cur_top + Inches(0.12), quad_w - Inches(0.9), Inches(0.45))
            tf_t = tb_t.text_frame
            tf_t.word_wrap = True
            self._set_tf_margins(tf_t, top=4, bottom=4, left=4, right=4)
            set_para(tf_t.paragraphs[0], q_title, font_size=13.5, bold=True, color_rgb=q_color)

            tb_b = slide.shapes.add_textbox(cur_left + Inches(0.2), cur_top + Inches(0.65), quad_w - Inches(0.4), quad_h - Inches(0.75))
            tf_b = tb_b.text_frame
            tf_b.word_wrap = True
            self._set_tf_margins(tf_b, top=6, bottom=6, left=6, right=6)
            items = s_data.get(key, ["关键分析点 01：核心业务影响与战略要素分析", "关键分析点 02：协同推进策略与落地要点"])
            for j, it in enumerate(items[:3]):
                p = tf_b.paragraphs[0] if j == 0 else tf_b.add_paragraph()
                set_para(p, f"• {it}", font_size=11, bold=False, color_rgb=C_DARK)
                p.space_before = Pt(4)
                p.space_after = Pt(2)

    def _render_matrix_grid_flat(self, slide, s_data: Dict[str, Any], arch: str):
        """Engine 8: 2xN Flat Grid Matrix with Dynamic Reflow (ARCH_09, ARCH_34)"""
        self._add_body_master(slide, s_data.get("title", ""), s_data.get("category", ""))
        top_m, left_m = Inches(1.6), Inches(0.8)

        if arch.startswith("ARCH_09"):
            modules = s_data.get("modules", [{"title": f"方案模块 0{i+1}", "desc": "业务应用场景与技术方案说明"} for i in range(6)])
            num_m = len(modules) if modules else 6
            if num_m <= 4:
                cols = 2
                card_w, card_h = Inches(5.6), Inches(2.25)
                gap_x, gap_y = Inches(0.53), Inches(0.35)
            elif num_m <= 6:
                cols = 3
                card_w, card_h = Inches(3.64), Inches(2.25)
                gap_x, gap_y = Inches(0.4), Inches(0.35)
            else:
                cols = 4
                card_w, card_h = Inches(2.72), Inches(2.25)
                gap_x, gap_y = Inches(0.28), Inches(0.35)

            f_t = 12.5 if cols >= 4 else 13.5
            f_d_base = 10.0 if cols >= 4 else 11.0

            for i, mod in enumerate(modules[:cols * 2]):
                col, row = i % cols, i // cols
                cur_left = left_m + col * (card_w + gap_x)
                cur_top = top_m + row * (card_h + gap_y)

                bg = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cur_left, cur_top, card_w, card_h)
                bg.fill.solid()
                bg.fill.fore_color.rgb = C_BLUE_BG
                bg.line.color.rgb = RGBColor(200, 220, 255)
                bg.line.width = Pt(1)

                tb_t = slide.shapes.add_textbox(cur_left + Inches(0.15), cur_top + Inches(0.12), card_w - Inches(0.3), Inches(0.45))
                tf_t = tb_t.text_frame
                tf_t.word_wrap = True
                self._set_tf_margins(tf_t, top=4, bottom=4, left=4, right=4)
                set_para(tf_t.paragraphs[0], mod.get("title", ""), font_size=f_t, bold=True, color_rgb=C_BLUE)

                tb_d = slide.shapes.add_textbox(cur_left + Inches(0.15), cur_top + Inches(0.6), card_w - Inches(0.3), card_h - Inches(0.75))
                tf_d = tb_d.text_frame
                tf_d.word_wrap = True
                self._set_tf_margins(tf_d, top=4, bottom=4, left=4, right=4)
                f_auto = calc_autofit_fontsize(mod.get("desc", ""), base_size=f_d_base, min_size=8.5, threshold_len=25)
                set_para(tf_d.paragraphs[0], mod.get("desc", ""), font_size=f_auto, bold=False, color_rgb=C_MUTED)

        else: # ARCH_34
            partners = s_data.get("partners", [
                {"category": "电力与能源巨头", "title": "国家电网 / 南方电网", "desc": "特高压与智慧配电战略合作"},
                {"category": "科技与物联网", "title": "阿里云 / 腾讯云", "desc": "工业云与 AI 能效算法联合开发"},
                {"category": "工业制造领军", "title": "中国中车 / 宝武钢铁", "desc": "高端制造示范工程落地实施"},
                {"category": "全球生态伙伴", "title": "施耐德 / 西门子合作项目", "desc": "国际标准联合推进与项目协同"}
            ])
            num_p = len(partners) if partners else 4
            if num_p > 4:
                cols = 3
                card_w, card_h = Inches(3.64), Inches(2.25)
                gap_x, gap_y = Inches(0.4), Inches(0.35)
            else:
                cols = 2
                card_w, card_h = Inches(5.6), Inches(2.25)
                gap_x, gap_y = Inches(0.53), Inches(0.35)

            for idx, pt in enumerate(partners[:cols * 2]):
                col, row = idx % cols, idx // cols
                cur_left = left_m + col * (card_w + gap_x)
                cur_top = top_m + row * (card_h + gap_y)

                bg = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cur_left, cur_top, card_w, card_h)
                bg.fill.solid()
                bg.fill.fore_color.rgb = C_WHITE
                bg.line.color.rgb = C_BORDER
                bg.line.width = Pt(1)

                tag_w = Inches(1.8) if cols == 3 else Inches(2.2)
                tag = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cur_left + Inches(0.15), cur_top + Inches(0.15), tag_w, Inches(0.38))
                tag.fill.solid()
                tag.fill.fore_color.rgb = C_BLUE_BG
                tag.line.fill.background()
                tf_tag = tag.text_frame
                self._set_tf_margins(tf_tag, top=2, bottom=2, left=4, right=4)
                set_para(tf_tag.paragraphs[0], pt.get("category", ""), font_size=10 if cols == 3 else 10.5, bold=True, color_rgb=C_BLUE, align=PP_ALIGN.CENTER)

                tb = slide.shapes.add_textbox(cur_left + Inches(0.15), cur_top + Inches(0.6), card_w - Inches(0.3), card_h - Inches(0.75))
                tf = tb.text_frame
                tf.word_wrap = True
                self._set_tf_margins(tf, top=4, bottom=4, left=4, right=4)
                set_para(tf.paragraphs[0], pt.get("title", ""), font_size=13 if cols == 3 else 14, bold=True, color_rgb=C_DARK)
                p_d = tf.add_paragraph()
                f_desc = calc_autofit_fontsize(pt.get("desc", ""), base_size=10.0 if cols == 3 else 11.0, min_size=8.5, threshold_len=25)
                set_para(p_d, pt.get("desc", ""), font_size=f_desc, bold=False, color_rgb=C_MUTED)
                p_d.space_before = Pt(4)

    def _render_platform_architecture(self, slide, s_data: Dict[str, Any], arch: str):
        """Engine 9: 4-Layer Stacked Architecture (ARCH_08)"""
        self._add_body_master(slide, s_data.get("title", ""), s_data.get("category", ""))
        layers = s_data.get("layers", [])
        arch_w, layer_h, gap, top_start = Inches(11.73), Inches(1.15), Inches(0.12), Inches(1.6)
        tag_colors = [C_BLUE, RGBColor(35, 120, 255), C_CYAN, C_DEEP_BLUE]

        for i, l in enumerate(layers[:4]):
            cur_top = top_start + i * (layer_h + gap)
            bg = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), cur_top, arch_w, layer_h)
            bg.fill.solid()
            bg.fill.fore_color.rgb = C_WHITE
            bg.line.color.rgb = C_BLUE if i == 0 else C_BORDER
            bg.line.width = Pt(1.5) if i == 0 else Pt(1)

            tag = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.0), cur_top + Inches(0.22), Inches(2.2), Inches(0.7))
            tag.fill.solid()
            tag.fill.fore_color.rgb = tag_colors[i] if i < len(tag_colors) else C_BLUE
            tag.line.fill.background()
            tf_tag = tag.text_frame
            self._set_tf_margins(tf_tag, top=4, bottom=4, left=4, right=4)
            set_para(tf_tag.paragraphs[0], l.get("layer_name", ""), font_size=12, bold=True, color_rgb=C_WHITE, align=PP_ALIGN.CENTER)

            tb_h = slide.shapes.add_textbox(Inches(3.4), cur_top + Inches(0.15), Inches(3.2), Inches(0.8))
            tf_h = tb_h.text_frame
            tf_h.word_wrap = True
            self._set_tf_margins(tf_h, top=6, bottom=6, left=6, right=6)
            set_para(tf_h.paragraphs[0], l.get("headline", ""), font_size=12.5, bold=True, color_rgb=C_BLUE if i == 0 else C_DARK)

            mods = l.get("modules", [])
            mod_text = "  |  ".join(mods)
            tb_m = slide.shapes.add_textbox(Inches(6.8), cur_top + Inches(0.15), arch_w - Inches(6.2), Inches(0.8))
            tf_m = tb_m.text_frame
            tf_m.word_wrap = True
            self._set_tf_margins(tf_m, top=6, bottom=6, left=6, right=6)
            set_para(tf_m.paragraphs[0], mod_text, font_size=11, bold=False, color_rgb=C_MUTED)

    def _render_pillars_and_base(self, slide, s_data: Dict[str, Any], arch: str):
        """Engine 10: 3 Pillars + Base Platform (ARCH_31)"""
        self._add_body_master(slide, s_data.get("title", "三支柱与平台底座支撑体系"), s_data.get("category", "平台支撑"))
        top_m = Inches(1.6)
        pillars = s_data.get("pillars", [
            {"title": "支柱一：产品硬实力", "bullets": ["标准化高端硬件", "极致质量管控与认证"]},
            {"title": "支柱二：软件数智化", "bullets": ["云边端协同平台", "AI 算法与能效调度"]},
            {"title": "支柱三：服务生态化", "bullets": ["7×24 全生命周期运维", "全球本地化交付网络"]}
        ])
        card_w, gap, left_m = Inches(3.64), Inches(0.4), Inches(0.8)

        for i, p in enumerate(pillars[:3]):
            cur_left = left_m + i * (card_w + gap)
            bg = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cur_left, top_m, card_w, Inches(3.3))
            bg.fill.solid()
            bg.fill.fore_color.rgb = C_BLUE_BG
            bg.line.color.rgb = C_BLUE
            bg.line.width = Pt(1)

            h_bar = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cur_left, top_m, card_w, Inches(0.6))
            h_bar.fill.solid()
            h_bar.fill.fore_color.rgb = C_BLUE
            h_bar.line.fill.background()
            tf_hbar = h_bar.text_frame
            self._set_tf_margins(tf_hbar, top=4, bottom=4, left=6, right=6)
            set_para(tf_hbar.paragraphs[0], p.get("title", ""), font_size=13, bold=True, color_rgb=C_WHITE, align=PP_ALIGN.CENTER)

            tb = slide.shapes.add_textbox(cur_left + Inches(0.2), top_m + Inches(0.75), card_w - Inches(0.4), Inches(2.4))
            tf = tb.text_frame
            tf.word_wrap = True
            self._set_tf_margins(tf, top=8, bottom=8, left=8, right=8)
            for j, b in enumerate(p.get("bullets", [])):
                para = tf.paragraphs[0] if j == 0 else tf.add_paragraph()
                set_para(para, f"• {b}", font_size=11, bold=False, color_rgb=C_DARK)
                para.space_before = Pt(8)
                para.space_after = Pt(2)

        base = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), top_m + Inches(3.5), Inches(11.73), Inches(1.5))
        base.fill.solid()
        base.fill.fore_color.rgb = C_DEEP_BLUE
        base.line.fill.background()

        tb_base = slide.shapes.add_textbox(Inches(1.0), top_m + Inches(3.6), Inches(11.33), Inches(1.3))
        tf_base = tb_base.text_frame
        tf_base.word_wrap = True
        self._set_tf_margins(tf_base, top=8, bottom=8, left=8, right=8)
        set_para(tf_base.paragraphs[0], s_data.get("base_title", "底座支撑：正泰统一云边物联 OS 与全球合规供应链"), font_size=14, bold=True, color_rgb=C_WHITE, align=PP_ALIGN.CENTER)
        p_bdesc = tf_base.add_paragraph()
        set_para(p_bdesc, s_data.get("base_desc", "提供强稳健、高并发、安全可信的底层技术支撑，全面赋能三大业务支柱高品质落地。"), font_size=11, bold=False, color_rgb=C_ICE_BLUE, align=PP_ALIGN.CENTER)
        p_bdesc.space_before = Pt(6)

    def _render_circular_hub_topology(self, slide, s_data: Dict[str, Any], arch: str):
        """Engine 11: Circular Hub Topology (ARCH_14, ARCH_32)"""
        top_m = Inches(1.6)
        if arch.startswith("ARCH_14"):
            self._add_body_master(slide, s_data.get("title", "核心战略闭环体系"), s_data.get("category", "战略闭环"))
            ring3 = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(3.8), Inches(1.5), Inches(5.7), Inches(5.7))
            ring3.fill.background()
            ring3.line.color.rgb = RGBColor(210, 230, 255)
            ring3.line.width = Pt(1)

            ring2 = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(4.5), Inches(2.2), Inches(4.3), Inches(4.3))
            ring2.fill.background()
            ring2.line.color.rgb = C_CYAN
            ring2.line.width = Pt(1.5)

            center_c = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(5.5), Inches(3.2), Inches(2.33), Inches(2.33))
            center_c.fill.solid()
            center_c.fill.fore_color.rgb = C_BLUE
            center_c.line.fill.background()

            center_label = s_data.get("center_label", "核心战略\n闭环赋能")
            c_lines = center_label.split("\n")
            tb_cc = slide.shapes.add_textbox(Inches(5.5), Inches(3.7), Inches(2.33), Inches(1.2))
            tf_cc = tb_cc.text_frame
            self._set_tf_margins(tf_cc, top=4, bottom=4, left=4, right=4)
            for line_i, cline in enumerate(c_lines):
                p_cline = tf_cc.paragraphs[0] if line_i == 0 else tf_cc.add_paragraph()
                set_para(p_cline, cline, font_size=15, bold=True, color_rgb=C_WHITE, align=PP_ALIGN.CENTER)

            node_positions = [
                (Inches(0.8), Inches(1.8), PP_ALIGN.RIGHT),
                (Inches(8.8), Inches(1.8), PP_ALIGN.LEFT),
                (Inches(0.8), Inches(4.8), PP_ALIGN.RIGHT),
                (Inches(8.8), Inches(4.8), PP_ALIGN.LEFT),
                (Inches(4.8), Inches(6.1), PP_ALIGN.CENTER),
            ]
            payload_nodes = s_data.get("nodes", s_data.get("items", []))
            default_nodes = [{"title": f"维度 0{i+1}", "desc": "关键业务推进策略与执行要点"} for i in range(5)]
            nodes_to_render = payload_nodes if payload_nodes else default_nodes

            for idx, nd in enumerate(nodes_to_render[:5]):
                n_left, n_top, n_align = node_positions[idx]
                tb_n = slide.shapes.add_textbox(n_left, n_top, Inches(3.8), Inches(1.1))
                tf_n = tb_n.text_frame
                tf_n.word_wrap = True
                self._set_tf_margins(tf_n, top=4, bottom=4, left=6, right=6)
                set_para(tf_n.paragraphs[0], nd.get("title", ""), font_size=14, bold=True, color_rgb=C_BLUE, align=n_align)
                p_d = tf_n.add_paragraph()
                set_para(p_d, nd.get("desc", nd.get("detail", "")), font_size=11, bold=False, color_rgb=C_MUTED, align=n_align)
                p_d.space_before = Pt(3)

        else: # ARCH_32
            self._add_body_master(slide, s_data.get("title", "产业协同与 4 方生态拓扑"), s_data.get("category", "生态拓扑"))
            ring = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(3.8), top_m + Inches(0.2), Inches(5.73), Inches(4.6))
            ring.fill.background()
            ring.line.color.rgb = C_CYAN
            ring.line.width = Pt(2)

            hub = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(5.66), top_m + Inches(1.5), Inches(2.0), Inches(2.0))
            hub.fill.solid()
            hub.fill.fore_color.rgb = C_BLUE
            hub.line.fill.background()
            tf_hub = hub.text_frame
            self._set_tf_margins(tf_hub, top=4, bottom=4, left=4, right=4)
            set_para(tf_hub.paragraphs[0], s_data.get("hub_label", "正泰生态\n中枢矩阵"), font_size=15, bold=True, color_rgb=C_WHITE, align=PP_ALIGN.CENTER)

            nodes = s_data.get("nodes", [
                {"title": "终端客户与业主", "desc": "需求牵引与场景体验"},
                {"title": "系统集成商", "desc": "联合开发与交付实施"},
                {"title": "设计院与专家", "desc": "标准制定与技术前瞻"},
                {"title": "供应与制造伙伴", "desc": "品质保障与极速履约"}
            ])
            pos = [
                (Inches(0.8), top_m + Inches(0.5)),
                (Inches(8.53), top_m + Inches(0.5)),
                (Inches(0.8), top_m + Inches(3.2)),
                (Inches(8.53), top_m + Inches(3.2))
            ]
            for idx, nd in enumerate(nodes[:4]):
                n_left, n_top = pos[idx]
                card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, n_left, n_top, Inches(4.0), Inches(1.3))
                card.fill.solid()
                card.fill.fore_color.rgb = C_BLUE_BG
                card.line.color.rgb = C_BLUE
                card.line.width = Pt(1)

                tb = slide.shapes.add_textbox(n_left + Inches(0.15), n_top + Inches(0.15), Inches(3.7), Inches(1.0))
                tf = tb.text_frame
                tf.word_wrap = True
                self._set_tf_margins(tf, top=6, bottom=6, left=6, right=6)
                set_para(tf.paragraphs[0], nd.get("title", ""), font_size=13.5, bold=True, color_rgb=C_BLUE)
                p_d = tf.add_paragraph()
                set_para(p_d, nd.get("desc", ""), font_size=11, bold=False, color_rgb=C_DARK)
                p_d.space_before = Pt(4)

    def _render_gantt_table(self, slide, s_data: Dict[str, Any], arch: str):
        """Engine 12: Gantt Schedule Table (ARCH_29)"""
        self._add_body_master(slide, s_data.get("title", "项目排期与推进进度甘特表"), s_data.get("category", "甘特排期"))
        top_m = Inches(1.6)

        table_shape = slide.shapes.add_table(6, 6, Inches(0.8), top_m, Inches(11.73), Inches(4.8))
        table = table_shape.table

        headers = ["阶段与关键任务", "责任人", "Q1 排期", "Q2 排期", "Q3 排期", "Q4 排期"]
        col_widths = [Inches(3.73), Inches(1.5), Inches(1.62), Inches(1.62), Inches(1.62), Inches(1.62)]
        for idx, width in enumerate(col_widths):
            table.columns[idx].width = width

        for idx, text in enumerate(headers):
            cell = table.cell(0, idx)
            cell.fill.solid()
            cell.fill.fore_color.rgb = C_BLUE
            tf_c = cell.text_frame
            self._set_tf_margins(tf_c, top=6, bottom=6, left=6, right=6)
            set_para(tf_c.paragraphs[0], text, font_size=12, bold=True, color_rgb=C_WHITE, align=PP_ALIGN.CENTER)

        task_rows = s_data.get("tasks", [
            ["1. 方案设计与规范冻结", "张经理", "■ 部署中", "✔ 已完成", "-", "-"],
            ["2. 核心系统开发与联调", "李工", "-", "■ 部署中", "■ 部署中", "-"],
            ["3. 试点验证与 PoC 测试", "王工", "-", "-", "■ 部署中", "-"],
            ["4. 全局上线与商业推广", "赵经理", "-", "-", "-", "■ 部署中"],
            ["5. 复盘总结与持续迭代", "刘工", "-", "-", "-", "■ 部署中"]
        ])

        for row_idx, r_data in enumerate(task_rows[:5]):
            for col_idx, cell_text in enumerate(r_data[:6]):
                cell = table.cell(row_idx + 1, col_idx)
                cell.fill.solid()
                cell.fill.fore_color.rgb = C_LIGHT_BG if row_idx % 2 == 1 else C_WHITE
                align = PP_ALIGN.LEFT if col_idx == 0 else PP_ALIGN.CENTER
                color = C_BLUE if "部署" in cell_text or "完成" in cell_text else C_DARK
                tf_cell = cell.text_frame
                self._set_tf_margins(tf_cell, top=6, bottom=6, left=6, right=6)
                set_para(tf_cell.paragraphs[0], cell_text, font_size=11, bold=("部署" in cell_text or "完成" in cell_text), color_rgb=color, align=align)


    def _render_chart_bar_trend(self, slide, s_data: Dict[str, Any], arch: str):
        """Native Bar & Trend Chart Engine (ARCH_16)"""
        self._add_body_master(slide, s_data.get("title", "核心指标趋势与对比分析"), s_data.get("category", "数据量化"))
        top_m, box_h = Inches(1.6), Inches(5.0)
        
        left_w = Inches(4.2)
        left_bg = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), top_m, left_w, box_h)
        left_bg.fill.solid()
        left_bg.fill.fore_color.rgb = C_LIGHT_BG
        left_bg.line.color.rgb = C_BORDER
        left_bg.line.width = Pt(1)
        
        tb_l = slide.shapes.add_textbox(Inches(1.0), top_m + Inches(0.25), left_w - Inches(0.4), box_h - Inches(0.5))
        tf_l = tb_l.text_frame
        tf_l.word_wrap = True
        self._set_tf_margins(tf_l, top=8, bottom=8, left=8, right=8)
        set_para(tf_l.paragraphs[0], s_data.get("summary_title", "数据洞察与业务启示"), font_size=14, bold=True, color_rgb=C_BLUE)
        
        summary_bullets = s_data.get("summary_bullets", [
            "主营业务营收稳步上扬，同比增长显著超出行业大盘",
            "战略新品替代率持续攀升，高附加值产品占比突破 45%",
            "海外业务保持高速扩张态势，全球交付履约韧性进一步夯实"
        ])
        for j, b in enumerate(summary_bullets):
            p = tf_l.add_paragraph()
            set_para(p, f"• {b}", font_size=11.5, bold=False, color_rgb=C_DARK)
            p.space_before = Pt(10)
            p.space_after = Pt(2)
        
        right_w, right_left = Inches(7.2), Inches(5.33)
        cats = s_data.get("categories", ["2023", "2024", "2025", "2026E"])
        series_data = s_data.get("series", [
            {"name": "主营业务收入 (亿元)", "values": [120, 150, 185, 220]},
            {"name": "战略新品产值 (亿元)", "values": [45, 68, 95, 130]}
        ])
        
        try:
            cdata = CategoryChartData()
            cdata.categories = cats
            for s in series_data:
                cdata.add_series(s.get("name", "系列"), tuple(s.get("values", [])))
            
            chart_shape = slide.shapes.add_chart(
                XL_CHART_TYPE.COLUMN_CLUSTERED,
                right_left, top_m, right_w, box_h, cdata
            )
            chart = chart_shape.chart
            chart.has_legend = True
            chart.legend.position = XL_LEGEND_POSITION.TOP
            chart.legend.include_in_layout = False
            
            # Enable value data labels on columns
            if chart.plots and len(chart.plots) > 0:
                plot = chart.plots[0]
                plot.has_data_labels = True
                data_labels = plot.data_labels
                data_labels.font.name = FONT_FAMILY
                data_labels.font.size = Pt(9.5)
                data_labels.font.color.rgb = C_DARK

            for s_idx, series in enumerate(chart.series):
                color = CHART_PALETTE[s_idx % len(CHART_PALETTE)]
                fill = series.format.fill
                fill.solid()
                fill.fore_color.rgb = color
        except Exception as e:
            right_bg = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, right_left, top_m, right_w, box_h)
            right_bg.fill.solid()
            right_bg.fill.fore_color.rgb = C_WHITE
            right_bg.line.color.rgb = C_BORDER
            right_bg.line.width = Pt(1)
            
            tb_fb = slide.shapes.add_textbox(right_left + Inches(0.3), top_m + Inches(0.3), right_w - Inches(0.6), box_h - Inches(0.6))
            tf_fb = tb_fb.text_frame
            self._set_tf_margins(tf_fb, top=8, bottom=8, left=8, right=8)
            set_para(tf_fb.paragraphs[0], s_data.get("chart_title", "核心业务指标量化看板"), font_size=14, bold=True, color_rgb=C_BLUE)
            for idx, cat in enumerate(cats):
                p = tf_fb.add_paragraph()
                val_str = " | ".join([f"{s.get('name', '指标')}: {s.get('values', [])[idx]}" for s in series_data if idx < len(s.get('values', []))])
                set_para(p, f"【{cat}】 {val_str}", font_size=12, bold=False, color_rgb=C_DARK)
                p.space_before = Pt(8)

    def _render_chart_pie_donut(self, slide, s_data: Dict[str, Any], arch: str):
        """Native Doughnut & Pie Chart Breakdown Engine with Dynamic Reflow (ARCH_17, 2-6 Slices)"""
        self._add_body_master(slide, s_data.get("title", "业务结构与占比分布"), s_data.get("category", "结构拆解"))
        top_m, box_h = Inches(1.6), Inches(5.0)
        
        slices = s_data.get("slices", [
            {"label": "新能源与绿色电工", "value": 42, "desc": "光伏、储能与智能配电方案高速增长"},
            {"label": "智能电气核心主业", "value": 35, "desc": "低压元器件与成套设备稳健支撑"},
            {"label": "工业自动化与物联网", "value": 15, "desc": "智慧能效管理与工业物联软件平台"},
            {"label": "海外新兴市场布局", "value": 8, "desc": "一带一路沿线及欧美战略新兴市场"}
        ])
        num_s = max(1, min(len(slices), 6))
        
        left_w = Inches(5.0)
        chart_top = top_m + Inches(0.2)
        chart_h = Inches(4.6)

        cdata = CategoryChartData()
        cdata.categories = [sl.get("label", "") for sl in slices[:num_s]]
        cdata.add_series("", tuple(sl.get("value", 0) for sl in slices[:num_s]))
        
        try:
            chart_shape = slide.shapes.add_chart(
                XL_CHART_TYPE.DOUGHNUT,
                Inches(0.8), chart_top, left_w, chart_h, cdata
            )
            chart = chart_shape.chart
            chart.has_legend = False
            chart.has_title = False

            # Explicitly color each slice to match right-hand card palette
            if chart.series and len(chart.series) > 0:
                series = chart.series[0]
                for p_idx, pt in enumerate(series.points):
                    fill = pt.format.fill
                    fill.solid()
                    fill.fore_color.rgb = CHART_PALETTE[p_idx % len(CHART_PALETTE)]

            # Precisely compute doughnut center
            cx = Inches(0.8) + left_w / 2
            cy = chart_top + chart_h / 2
            hole_w, hole_h = Inches(1.85), Inches(1.85)
            center_left = cx - hole_w / 2
            center_top = cy - hole_h / 2
            
            center_circle = slide.shapes.add_shape(MSO_SHAPE.OVAL, center_left, center_top, hole_w, hole_h)
            center_circle.fill.solid()
            center_circle.fill.fore_color.rgb = C_WHITE
            center_circle.line.color.rgb = C_BLUE_BG
            center_circle.line.width = Pt(2)
            
            tf_c = center_circle.text_frame
            tf_c.word_wrap = True
            tf_c.vertical_anchor = MSO_ANCHOR.MIDDLE
            self._set_tf_margins(tf_c, top=0, bottom=0, left=2, right=2)
            set_para(tf_c.paragraphs[0], s_data.get("center_metric", "100%"), font_size=20, bold=True, color_rgb=C_BLUE, align=PP_ALIGN.CENTER)
            p_clbl = tf_c.add_paragraph()
            set_para(p_clbl, s_data.get("center_label", "核心业务分布"), font_size=10.0, bold=False, color_rgb=C_MUTED, align=PP_ALIGN.CENTER)
            p_clbl.space_before = Pt(2)
        except Exception as e:
            print(f"[WARN] ARCH_17 doughnut chart rendering fallback: {e}")
        
        right_w, right_left = Inches(6.3), Inches(6.2)
        if num_s <= 3:
            card_h, gap_y = Inches(1.35), Inches(0.25)
            f_pct, f_lbl, f_desc = 22, 14, 11.5
        elif num_s == 4:
            card_h, gap_y = Inches(1.08), Inches(0.18)
            f_pct, f_lbl, f_desc = 20, 13, 11.0
        elif num_s == 5:
            card_h, gap_y = Inches(0.85), Inches(0.12)
            f_pct, f_lbl, f_desc = 17, 12, 10.0
        else: # 6 slices
            card_h, gap_y = Inches(0.70), Inches(0.10)
            f_pct, f_lbl, f_desc = 15, 11, 9.5

        for idx, sl in enumerate(slices[:num_s]):
            cur_top = top_m + idx * (card_h + gap_y)
            bg = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, right_left, cur_top, right_w, card_h)
            bg.fill.solid()
            bg.fill.fore_color.rgb = C_LIGHT_BG
            bg.line.color.rgb = C_BORDER
            bg.line.width = Pt(1)
            
            bar = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, right_left + Inches(0.1), cur_top + Inches(0.12), Inches(0.1), card_h - Inches(0.24))
            bar.fill.solid()
            bar.fill.fore_color.rgb = CHART_PALETTE[idx % len(CHART_PALETTE)]
            bar.line.fill.background()
            
            tb_pct = slide.shapes.add_textbox(right_left + Inches(0.25), cur_top + Inches(0.08), Inches(1.2), card_h - Inches(0.16))
            tf_pct = tb_pct.text_frame
            self._set_tf_margins(tf_pct, top=2, bottom=2, left=2, right=2)
            set_para(tf_pct.paragraphs[0], f"{sl.get('value', '')}%", font_size=f_pct, bold=True, color_rgb=C_BLUE)
            
            tb_txt = slide.shapes.add_textbox(right_left + Inches(1.5), cur_top + Inches(0.08), right_w - Inches(1.6), card_h - Inches(0.16))
            tf_txt = tb_txt.text_frame
            tf_txt.word_wrap = True
            self._set_tf_margins(tf_txt, top=2, bottom=2, left=4, right=4)
            set_para(tf_txt.paragraphs[0], sl.get("label", ""), font_size=f_lbl, bold=True, color_rgb=C_DARK)
            p_d = tf_txt.add_paragraph()
            f_auto = calc_autofit_fontsize(sl.get("desc", ""), base_size=f_desc, min_size=8.5, threshold_len=25)
            set_para(p_d, sl.get("desc", ""), font_size=f_auto, bold=False, color_rgb=C_MUTED)
            p_d.space_before = Pt(2)

    def _render_rich_chart(self, slide, s_data: Dict[str, Any], arch: str):
        """Vector Charts & Graphics Engine (ARCH_16_RICH_CHART, Radar, Combo, Diverging, Evolution, Heatmap)"""
        self._add_body_master(slide, s_data.get("title", "数据量化与战略对标看板"), s_data.get("category", "量化对标"))
        top_m = Inches(1.6)
        full_width = s_data.get("full_width", False)
        
        # Determine chart type from archetype name or explicit property
        chart_kind = s_data.get("chart_type", "").lower()
        if not chart_kind:
            if "RADAR" in arch:
                chart_kind = "radar"
            elif "COMBO" in arch or "DUAL_AXIS" in arch:
                chart_kind = "combo"
            elif "DIVERGING" in arch:
                chart_kind = "diverging"
            elif "EVOLUTION" in arch:
                chart_kind = "evolution"
            elif "HEATMAP" in arch or "MATRIX" in arch:
                chart_kind = "heatmap"
            elif "WATERFALL" in arch:
                chart_kind = "waterfall"
            elif "SANKEY" in arch:
                chart_kind = "sankey"
            elif "FUNNEL" in arch:
                chart_kind = "funnel"
            elif "GAUGE" in arch or "BULLET" in arch:
                chart_kind = "gauge"
            elif "STACKED_AREA" in arch or "AREA" in arch:
                chart_kind = "stacked_area"
            else:
                chart_kind = "radar" if "categories" in s_data and "series" in s_data else "combo"

        chart_w = Inches(11.73) if full_width else Inches(6.5)
        chart_h = Inches(5.0)
        img_w_in = 11.73 if full_width else 6.5
        img_h_in = 5.0
        
        try:
            if chart_kind == "radar":
                categories = s_data.get("categories", ["极限分断能力", "温升控制", "智能化感知", "低功耗表现", "结构紧凑度", "数字化运维"])
                series_data = s_data.get("series", [
                    {"name": "正泰 NXA 新一代", "values": [96, 92, 90, 88, 95, 94], "color": "#1E50E6"},
                    {"name": "行业主流标杆", "values": [80, 82, 75, 72, 78, 70], "color": "#50C8FF"}
                ])
                chart_buf = ChintVectorChartBuilder.render_radar_chart(
                    categories=categories,
                    series_data=series_data,
                    title=s_data.get("chart_title", ""),
                    figsize=(img_w_in, img_h_in)
                )
            elif chart_kind in ("combo", "dual_axis"):
                categories = s_data.get("categories", ["2022", "2023", "2024", "2025", "2026E"])
                bar_series = s_data.get("bar_series", {
                    "name": "业务营收", "values": [120, 155, 195, 245, 320], "unit": "亿", "color": "#1E50E6"
                })
                line_series = s_data.get("line_series", {
                    "name": "同比增速", "values": [16.5, 29.1, 25.8, 25.6, 30.6], "unit": "%", "color": "#14C832"
                })
                chart_buf = ChintVectorChartBuilder.render_combo_chart(
                    categories=categories,
                    bar_series=bar_series,
                    line_series=line_series,
                    title=s_data.get("chart_title", ""),
                    figsize=(img_w_in, img_h_in)
                )
            elif chart_kind == "diverging":
                categories = s_data.get("categories", ["新能源光伏", "智能电网", "数据中心", "轨道交通", "传统工商业", "高耗能冶金"])
                values = s_data.get("values", [42.5, 31.0, 26.8, 18.2, -8.5, -16.4])
                chart_buf = ChintVectorChartBuilder.render_diverging_bar(
                    categories=categories,
                    values=values,
                    title=s_data.get("chart_title", ""),
                    unit=s_data.get("unit", "%"),
                    figsize=(img_w_in, img_h_in)
                )
            elif chart_kind == "evolution":
                stages = s_data.get("stages", ["第一代标准断路器", "第二代数显断路器", "第三代物联网断路器", "第四代AI自愈断路器"])
                values = s_data.get("values", [65, 78, 89, 98])
                sub_labels = s_data.get("sub_labels", ["基础保护", "状态监测", "云边联动", "自主决策"])
                chart_buf = ChintVectorChartBuilder.render_evolution_chart(
                    stages=stages,
                    values=values,
                    sub_labels=sub_labels,
                    title=s_data.get("chart_title", ""),
                    unit=s_data.get("unit", "分"),
                    figsize=(img_w_in, img_h_in)
                )
            elif chart_kind == "heatmap":
                row_labels = s_data.get("row_labels", ["NXA 系列", "NA8 系列", "NM8N 系列", "NXM 系列"])
                col_labels = s_data.get("col_labels", ["集中光伏", "工商业储能", "智算中心", "轨道交通", "重工制造"])
                data_matrix = s_data.get("data_matrix", [
                    [95, 92, 96, 94, 90],
                    [90, 88, 92, 95, 86],
                    [85, 94, 88, 82, 92],
                    [80, 85, 78, 75, 88]
                ])
                chart_buf = ChintVectorChartBuilder.render_heatmap_matrix(
                    row_labels=row_labels,
                    col_labels=col_labels,
                    data_matrix=data_matrix,
                    title=s_data.get("chart_title", ""),
                    figsize=(img_w_in, img_h_in)
                )
            elif chart_kind == "waterfall":
                categories = s_data.get("categories", ["2025基准净利", "销量规模增长", "高端新品溢价", "原材料成本上涨", "数字化研发投入", "2026E净利"])
                values = s_data.get("values", [180.0, 52.0, 36.0, -18.0, -15.0, 235.0])
                chart_buf = ChintVectorChartBuilder.render_waterfall_chart(
                    categories=categories,
                    values=values,
                    initial_value=s_data.get("initial_value", None),
                    title=s_data.get("chart_title", ""),
                    unit=s_data.get("unit", "万"),
                    figsize=(img_w_in, img_h_in)
                )
            elif chart_kind == "sankey":
                flows = s_data.get("flows", None)
                nodes = s_data.get("nodes", None)
                links = s_data.get("links", None)
                chart_buf = ChintVectorChartBuilder.render_sankey_chart(
                    flows=flows,
                    nodes=nodes,
                    links=links,
                    title=s_data.get("chart_title", ""),
                    unit=s_data.get("unit", "万"),
                    figsize=(img_w_in, img_h_in)
                )
            elif chart_kind == "funnel":
                stages = s_data.get("stages", ["线索获取", "技术交流", "PoC 试点", "招投标入围", "商务签约"])
                values = s_data.get("values", [1200, 750, 420, 260, 180])
                conversion_rates = s_data.get("conversion_rates", None)
                chart_buf = ChintVectorChartBuilder.render_funnel_chart(
                    stages=stages,
                    values=values,
                    conversion_rates=conversion_rates,
                    title=s_data.get("chart_title", ""),
                    unit=s_data.get("unit", "个"),
                    figsize=(img_w_in, img_h_in)
                )
            elif chart_kind in ("gauge", "bullet"):
                current_val = float(s_data.get("current_val", s_data.get("value", 92.4)))
                target_val = float(s_data.get("target_val", 100.0))
                min_val = float(s_data.get("min_val", 0.0))
                max_val = float(s_data.get("max_val", 100.0))
                subtitle = s_data.get("subtitle", "")
                chart_buf = ChintVectorChartBuilder.render_gauge_kpi_chart(
                    current_val=current_val,
                    target_val=target_val,
                    min_val=min_val,
                    max_val=max_val,
                    title=s_data.get("chart_title", ""),
                    subtitle=subtitle,
                    unit=s_data.get("unit", "%"),
                    figsize=(img_w_in, img_h_in)
                )
            elif chart_kind in ("stacked_area", "area"):
                categories = s_data.get("categories", ["2021", "2022", "2023", "2024", "2025", "2026E"])
                series_data = s_data.get("series", [
                    {"name": "新能源光伏配电", "values": [35, 52, 78, 110, 150, 205], "color": "#1E50E6"},
                    {"name": "传统电网与工业", "values": [60, 68, 72, 76, 80, 85], "color": "#50C8FF"},
                    {"name": "算力中心与高精", "values": [12, 20, 35, 55, 82, 120], "color": "#14C832"}
                ])
                chart_buf = ChintVectorChartBuilder.render_stacked_area_chart(
                    categories=categories,
                    series_data=series_data,
                    title=s_data.get("chart_title", ""),
                    unit=s_data.get("unit", "亿"),
                    figsize=(img_w_in, img_h_in)
                )
            else:
                chart_buf = ChintVectorChartBuilder.render_radar_chart(
                    categories=["维度1", "维度2", "维度3", "维度4", "维度5"],
                    series_data=[{"name": "正泰方案", "values": [90, 85, 95, 92, 88]}],
                    figsize=(img_w_in, img_h_in)
                )

            slide.shapes.add_picture(chart_buf, Inches(0.8), top_m, chart_w, chart_h)
        except Exception as e:
            print(f"[WARN] _render_rich_chart rendering fallback: {e}")
            fb_shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), top_m, chart_w, chart_h)
            fb_shape.fill.solid()
            fb_shape.fill.fore_color.rgb = C_LIGHT_BG
            fb_shape.line.color.rgb = C_BORDER

        if not full_width:
            right_w = Inches(4.9)
            right_left = Inches(7.63)

            card_bg = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, right_left, top_m, right_w, chart_h)
            card_bg.fill.solid()
            card_bg.fill.fore_color.rgb = C_LIGHT_BG
            card_bg.line.color.rgb = C_BORDER
            card_bg.line.width = Pt(1)

            h_bg = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, right_left, top_m, right_w, Inches(0.65))
            h_bg.fill.solid()
            h_bg.fill.fore_color.rgb = C_CARD_HEADER_BG
            h_bg.line.fill.background()

            tb_h = slide.shapes.add_textbox(right_left + Inches(0.15), top_m + Inches(0.1), right_w - Inches(0.3), Inches(0.5))
            tf_h = tb_h.text_frame
            tf_h.word_wrap = True
            self._set_tf_margins(tf_h, top=4, bottom=4, left=6, right=6)
            set_para(tf_h.paragraphs[0], s_data.get("insight_header", "核心发现与战略洞察"), font_size=13.5, bold=True, color_rgb=C_BLUE, align=PP_ALIGN.CENTER)

            tb_body = slide.shapes.add_textbox(right_left + Inches(0.2), top_m + Inches(0.8), right_w - Inches(0.4), chart_h - Inches(0.95))
            tf_b = tb_body.text_frame
            tf_b.word_wrap = True
            self._set_tf_margins(tf_b, top=6, bottom=6, left=6, right=6)

            takeaways = s_data.get("insights", s_data.get("bullets", [
                "技术指标全维度领先：在核心分断能力与温升控制上建立显著专利壁垒",
                "数字化感知赋能：集成边缘 AI 算法，实现微秒级自愈与预测性维护",
                "生态协同与降本：标准化架构降低系统集成成本达 35%"
            ]))

            for j, t in enumerate(takeaways[:4]):
                p = tf_b.paragraphs[0] if j == 0 else tf_b.add_paragraph()
                f_auto = calc_autofit_fontsize(t, base_size=11.0, min_size=9.0, threshold_len=30)
                set_para(p, f"• {t}", font_size=f_auto, bold=False, color_rgb=C_DARK)
                p.space_before = Pt(8)
                p.space_after = Pt(2)

    def _render_fallback(self, slide, s_data: Dict[str, Any], arch: str):
        """Fallback Engine for Unknown Archetype IDs"""
        print(f"[WARN] Engine encountered unknown archetype '{arch}', rendering fallback body card.")
        self._add_body_master(slide, s_data.get("title", "未定义版式页"), s_data.get("category", "默认版式"))
        bg = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.6), Inches(11.73), Inches(5.0))
        bg.fill.solid()
        bg.fill.fore_color.rgb = C_LIGHT_BG
        bg.line.color.rgb = C_BORDER
        bg.line.width = Pt(1)

        tb = slide.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(11.33), Inches(4.5))
        tf = tb.text_frame
        tf.word_wrap = True
        self._set_tf_margins(tf, top=8, bottom=8, left=8, right=8)
        bullets = s_data.get("bullets", s_data.get("details", []))
        for j, b in enumerate(bullets):
            p = tf.paragraphs[0] if j == 0 else tf.add_paragraph()
            set_para(p, f"• {b}", font_size=13, bold=False, color_rgb=C_DARK)
            p.space_before = Pt(10)

    # =========================================================================
    # BUILD FROM PAYLOAD MAIN ENTRYPOINT & DISPATCH ROUTING
    # =========================================================================

    def build_from_payload(self, payload: Dict[str, Any], output_path: str):
        slides_data = payload.get("slides", [])

        # 34 Archetype Semantic Alias Dispatch Router
        ENGINE_ROUTER = {
            # 1. Master Frames
            "ARCH_01_COVER": self._render_master_frame,
            "ARCH_01_COVER_EARTH": self._render_master_frame,
            "ARCH_01_EARTH_COVER": self._render_master_frame,
            "ARCH_01_COVER_CITY": self._render_master_frame,
            "ARCH_01_CITY_COVER": self._render_master_frame,
            "ARCH_02_TOC": self._render_master_frame,
            "ARCH_02_FROSTED_GRID": self._render_master_frame,
            "ARCH_02_TOC_LIST": self._render_master_frame,
            "ARCH_02_RIBBON_TOC": self._render_master_frame,
            "ARCH_03_CHAPTER": self._render_master_frame,
            "ARCH_11_CLOSING": self._render_master_frame,
            "ARCH_11_CLOSING_MOSAIC": self._render_master_frame,
            "ARCH_11_MOSAIC_CLOSING": self._render_master_frame,
            "ARCH_11_CLOSING_BRAND": self._render_master_frame,
            "ARCH_11_SLOGAN_CLOSING": self._render_master_frame,
            "ARCH_15_CONTACT_US": self._render_master_frame,
            "ARCH_15_CONTACT": self._render_master_frame,

            # 2. Dual-Pane Split
            "ARCH_07_PROBLEM_SOLUTION_SWOT": self._render_dual_pane_split,
            "ARCH_21_BEFORE_AFTER_DIFF": self._render_dual_pane_split,
            "ARCH_21_BEFORE_AFTER": self._render_dual_pane_split,
            "ARCH_22_PROBLEM_IMPROVE_SPLIT": self._render_dual_pane_split,
            "ARCH_22_PROBLEM_IMPROVE": self._render_dual_pane_split,

            # 3. Hero Split Pane
            "ARCH_10_CASE_STUDY": self._render_hero_split_pane,
            "ARCH_13_GLOBAL_FOOTPRINT": self._render_hero_split_pane,
            "ARCH_19_HERO_METRIC_SPLIT": self._render_hero_split_pane,
            "ARCH_19_HERO_METRIC": self._render_hero_split_pane,

            # 4. N-Column Card Grid
            "ARCH_04_KPI_DASHBOARD": self._render_n_column_card_grid,
            "ARCH_05_MULTI_COLUMN_CARDS": self._render_n_column_card_grid,
            "ARCH_12_TEAM_PROFILE": self._render_n_column_card_grid,
            "ARCH_18_KPI_METRIC_GRID": self._render_n_column_card_grid,
            "ARCH_18_METRIC_GRID": self._render_n_column_card_grid,
            "ARCH_23_RISK_MATRIX_RESPONSE": self._render_n_column_card_grid,
            "ARCH_23_RISK_MATRIX": self._render_n_column_card_grid,
            "ARCH_24_MISSION_VISION_VALUES": self._render_n_column_card_grid,
            "ARCH_24_CULTURE": self._render_n_column_card_grid,
            "ARCH_33_HONOR_CERTIFICATION": self._render_n_column_card_grid,
            "ARCH_33_HONOR": self._render_n_column_card_grid,

            # Charts
            "ARCH_16_CHART_BAR_TREND": self._render_chart_bar_trend,
            "ARCH_16_BAR_CHART": self._render_chart_bar_trend,
            "ARCH_16_CHART_TREND": self._render_chart_bar_trend,
            "ARCH_16_RICH_CHART": self._render_rich_chart,
            "ARCH_16_RADAR": self._render_rich_chart,
            "ARCH_16_COMBO": self._render_rich_chart,
            "ARCH_16_DUAL_AXIS": self._render_rich_chart,
            "ARCH_16_DIVERGING": self._render_rich_chart,
            "ARCH_16_HEATMAP": self._render_rich_chart,
            "ARCH_16_EVOLUTION": self._render_rich_chart,
            "ARCH_16_MATRIX": self._render_rich_chart,
            "ARCH_16_WATERFALL": self._render_rich_chart,
            "ARCH_16_SANKEY": self._render_rich_chart,
            "ARCH_16_FUNNEL": self._render_rich_chart,
            "ARCH_16_GAUGE": self._render_rich_chart,
            "ARCH_16_BULLET": self._render_rich_chart,
            "ARCH_16_STACKED_AREA": self._render_rich_chart,
            "ARCH_16_AREA": self._render_rich_chart,
            "ARCH_17_CHART_PIE_DONUT": self._render_chart_pie_donut,
            "ARCH_17_PIE_CHART": self._render_chart_pie_donut,
            "ARCH_17_DONUT_CHART": self._render_chart_pie_donut,

            # 5. Horizontal Pipeline & Sequential
            "ARCH_06_TIMELINE_ROADMAP": self._render_horizontal_pipeline,
            "ARCH_25_PROCESS_STEP_HORIZONTAL": self._render_horizontal_pipeline,
            "ARCH_25_PROCESS_STEP": self._render_horizontal_pipeline,
            "ARCH_27_STEP_LADDER_MATURITY": self._render_horizontal_pipeline,
            "ARCH_27_MATURITY_LADDER": self._render_horizontal_pipeline,
            "ARCH_28_WATERFALL_DIAMOND": self._render_horizontal_pipeline,
            "ARCH_28_DIAMOND_PROCESS": self._render_horizontal_pipeline,
            "ARCH_30_MILESTONE_LIST_BADGE": self._render_horizontal_pipeline,
            "ARCH_30_MILESTONE_LIST": self._render_horizontal_pipeline,

            # 6. Stepped Funnel
            "ARCH_26_FUNNEL_CONVERSION": self._render_funnel_stepped,
            "ARCH_26_FUNNEL": self._render_funnel_stepped,

            # 7. 2x2 Matrix Quadrant
            "ARCH_20_SWOT_TOWS_MATRIX": self._render_matrix_2x2_quadrant,
            "ARCH_20_SWOT_MATRIX": self._render_matrix_2x2_quadrant,
            "ARCH_20_TOWS": self._render_matrix_2x2_quadrant,

            # 8. Flat Grid Matrix
            "ARCH_09_SOLUTION_GRID": self._render_matrix_grid_flat,
            "ARCH_34_PARTNER_LOGO_WALL": self._render_matrix_grid_flat,
            "ARCH_34_PARTNER_WALL": self._render_matrix_grid_flat,

            # 9. Platform Architecture
            "ARCH_08_PLATFORM_ARCHITECTURE": self._render_platform_architecture,

            # 10. Pillars and Base
            "ARCH_31_THREE_PILLARS_PLATFORM": self._render_pillars_and_base,
            "ARCH_31_THREE_PILLARS": self._render_pillars_and_base,

            # 11. Circular Hub Topology
            "ARCH_14_CONCENTRIC_HUB": self._render_circular_hub_topology,
            "ARCH_06_CONCENTRIC_HUB": self._render_circular_hub_topology,
            "ARCH_32_ECOSYSTEM_CIRCULAR": self._render_circular_hub_topology,
            "ARCH_32_ECOSYSTEM": self._render_circular_hub_topology,

            # 12. Gantt Table
            "ARCH_29_GANTT_SCHEDULE_TABLE": self._render_gantt_table,
            "ARCH_29_GANTT": self._render_gantt_table,
        }

        for s_data in slides_data:
            arch = s_data.get("archetype", "ARCH_01_COVER").upper()
            slide = self.prs.slides.add_slide(self.blank_layout)

            # Purge placeholder ghost shapes
            for shape in list(slide.shapes):
                if shape.is_placeholder:
                    sp = shape._element
                    sp.getparent().remove(sp)

            # Route to matched composition engine or fallback
            engine_fn = ENGINE_ROUTER.get(arch, self._render_fallback)
            engine_fn(slide, s_data, arch)

        self.prs.save(output_path)
        return output_path


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 2:
        payload_file = sys.argv[1]
        out_file = sys.argv[2]
        with open(payload_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        engine = ChintPresentationEngine()
        engine.build_from_payload(data, out_file)
        print(f"Generated {out_file} successfully.")
