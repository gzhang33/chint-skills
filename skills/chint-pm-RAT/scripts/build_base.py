#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build_base.py — 一次性构建 chint-pm-RAT 基座资产 template/one_pager_base.pptx

slide1 = RAT 表格模版 原样保留（主 12×9 表 + 团队表 + 标题占位 + 3 浮动小表，版式 logo 不动）
slide2 = 附录A 风险预案与有条件立项（模板视觉语言：灰标题条 + accent1 边框表）
slide3 = 附录B 销售预测交叉验证
运行：python3 scripts/build_base.py "<RAT 表格模版.pptx>" template/one_pager_base.pptx
"""
import sys
from copy import deepcopy
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.util import Inches, Pt

sys.path.insert(0, str(Path(__file__).parent))
import tplkit as tk


def make_bar(slide, text, x, y, w, h=0.34, size=12):
    """自建灰标题条（样式常量与模板一致：bg1 lumMod85 无边框、黑字加粗 CHINTinno）。"""
    shp = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE,
                                 Inches(x), Inches(y), Inches(w), Inches(h))
    shp.fill.solid()
    shp.fill.fore_color.rgb = RGBColor(0xD9, 0xD9, 0xD9)
    shp.line.fill.background()
    shp.shadow.inherit = False
    tf = shp.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Pt(4)
    tf.margin_top = tf.margin_bottom = Pt(1)
    p = tf.paragraphs[0]
    r = p.add_run()
    r.text = text
    r.font.bold = True
    r.font.size = Pt(size)
    r.font.name = "CHINTinno"
    r.font.color.rgb = RGBColor(0, 0, 0)
    rPr = r._r.find(tk.el('rPr'))
    for tag in ('latin', 'ea'):
        e = rPr.find(tk.el(tag))
        if e is None:
            e = tk.make(tag)
            rPr.append(e)
        e.set('typeface', 'CHINTinno')
    # 覆盖段落级符号（autoshape 默认无符号，保险置空）
    return shp


def clone_table(slide, proto_tbl_shape, x, y, widths_in, keep_rows=2, row_h=None):
    gfx = deepcopy(proto_tbl_shape._element)
    slide.shapes._spTree.append(gfx)
    from pptx.shapes.graphfrm import GraphicFrame
    gf = GraphicFrame(gfx, None)
    gf.left, gf.top = Inches(x), Inches(y)
    t = tk.tbl(gf)
    while len(tk.rows(t)) > keep_rows:
        tk.delete_row(t, len(tk.rows(t)) - 1)
    tk.set_table_width(gf, [Inches(w) for w in widths_in])
    if row_h:
        for tr in tk.rows(t):
            tr.set('h', str(int(Inches(row_h))))
    return gf


def main(src, dst):
    prs = Presentation(src)
    s1 = prs.slides[0]

    layout = None
    for ly in prs.slide_layouts:
        if ly.part.partname.endswith('slideLayout12.xml'):
            layout = ly
            break
    assert layout is not None, 'slideLayout12 not found'

    # 预测表原型：主表浮动小表 #5（4×5）——先克隆附录表，再删除全部浮动小表
    proto_tbl = list(s1.shapes)[5]
    assert proto_tbl.has_table

    # ---------------- 附录A ----------------
    sa = prs.slides.add_slide(layout)
    make_bar(sa, '附录A  风险预案与有条件立项', 0.4, 0.3, 6.0)
    make_bar(sa, '风险识别与应对预案', 0.4, 1.0, 3.4)
    ta = clone_table(sa, proto_tbl, 0.4, 1.42, [2.2, 2.4, 4.2, 2.4, 1.3],
                     keep_rows=5, row_h=0.5)
    taEl = tk.tbl(ta)
    tk.normalize_table(taEl, donor_tc=(1, 0), header_sz=10, body_sz=10)
    for ci, htxt in enumerate(['风险', '影响', '应对预案', '资源诉求', '责任人']):
        tk.set_cell(taEl, 0, ci, htxt, bold=True)
    for ri in range(1, len(tk.rows(taEl))):
        for ci in range(5):
            tk.set_cell(taEl, ri, ci, '')
    make_bar(sa, '有条件立项条件', 0.4, 4.35, 3.0)
    ca = make_bar(sa, '', 0.5, 4.8, 12.3, 1.4, size=11)
    ca.fill.solid()
    ca.fill.fore_color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    tk.set_paras(ca, [(0, [('1. （条件占位）', 0, None)]),
                      (1, [('2. （条件占位）', 0, None)])])

    # ---------------- 附录B ----------------
    sb = prs.slides.add_slide(layout)
    make_bar(sb, '附录B  销售预测交叉验证', 0.4, 0.3, 6.0)
    make_bar(sb, '独立推算链路：行业出货量 → 单台用量 → 总需求 → 与客户/销售预测对比', 0.4, 1.0, 8.0)
    tb = clone_table(sb, proto_tbl, 0.4, 1.42, [2.6, 2.6, 2.6, 2.6, 2.6],
                     keep_rows=5, row_h=0.55)
    tbEl = tk.tbl(tb)
    tk.delete_col(tbEl, 3)
    tk.delete_col(tbEl, 2)
    tk.set_table_width(tb, [Inches(w) for w in [2.6, 7.3, 2.6]])
    tk.normalize_table(tbEl, donor_tc=(1, 0), header_sz=10, body_sz=10)
    for ci, htxt in enumerate(['步骤', '推算过程', '数据来源']):
        tk.set_cell(tbEl, 0, ci, htxt, bold=True)
    for ri in range(1, len(tk.rows(tbEl))):
        for ci in range(3):
            tk.set_cell(tbEl, ri, ci, '')
    make_bar(sb, '对比结论', 0.4, 5.0, 2.2)
    cb = make_bar(sb, '', 0.5, 5.45, 12.3, 1.4, size=11)
    cb.fill.solid()
    cb.fill.fore_color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    tk.set_paras(cb, [(0, [('（对比结论占位）', 0, None)])])

    # 优化：删除主表上的 3 个浮动子表（M2 规格 7×7 / 投入 4×14 / 预测 4×5）
    # —— 非 PM 区仅保留标题条与空白正文，子表内容不再随模板交付
    sp1 = list(prs.slides[0].shapes)
    for idx in sorted((3, 4, 5), reverse=True):
        el_ = sp1[idx]._element
        el_.getparent().remove(el_)

    Path(dst).parent.mkdir(parents=True, exist_ok=True)
    prs.save(dst)
    print(f'OK base → {dst}（slides={len(prs.slides._sldIdLst)}）')


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
