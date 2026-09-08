#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CHINT RAT 立项资料一页纸生成器（chint-RAT）

用法:
    python3 generate_one_pager.py <spec.json> <output.pptx>

输入: 立项内容规格 JSON（schema 见 references/spec-schema.md，完整示例 examples/nxm_spec.json）
输出: 16:9 一页纸立项看板 .pptx + 附录页（风险预案 / 销售预测交叉验证，按 spec 提供与否自动追加）

版式规范: references/zone-spec.md（逆向自 NXA系列电炉行业专供产品开发202604.pptx 一页纸样板）
"""
import json
import sys
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.util import Emu, Inches, Pt

# ---------------------------------------------------------------- VI 常量
FONT = "CHINTinno"                 # 正泰拓新体；未安装时 PowerPoint 自动回退微软雅黑
EMU_IN = 914400
SLIDE_W, SLIDE_H = 13.333, 7.5
C_TITLE = RGBColor(0x23, 0x7A, 0xE4)      # 标题蓝（取自样板标题字色）
C_CHIP = RGBColor(0x44, 0x72, 0xC4)       # 顶部标签牌 accent1
C_BLACK = RGBColor(0x00, 0x00, 0x00)
C_WHITE = RGBColor(0xFF, 0xFF, 0xFF)
C_RED = RGBColor(0xD7, 0x0A, 0x32)        # 部分可行/风险警示
C_HDR_FILL = RGBColor(0xF2, 0xF2, 0xF2)   # 表头浅灰
BORDER = Pt(0.75)


# ---------------------------------------------------------------- 底层工具
def set_run(run, text, size, bold=False, color=C_BLACK, italic=False):
    """设置 run 文本并同步 latin+eastAsian 字体为 CHINTinno。"""
    run.text = text
    f = run.font
    f.size = Pt(size)
    f.bold = bold
    f.italic = italic
    f.color.rgb = color
    f.name = FONT
    rPr = run._r.get_or_add_rPr()
    ea = rPr.find("{http://schemas.openxmlformats.org/drawingml/2006/main}ea")
    if ea is None:
        ea = rPr.makeelement(
            "{http://schemas.openxmlformats.org/drawingml/2006/main}ea", {})
        rPr.append(ea)
    ea.set("typeface", FONT)


def add_rect(slide, x, y, w, h, fill=None, line=C_BLACK, line_w=BORDER):
    shp = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE,
                                 Inches(x), Inches(y), Inches(w), Inches(h))
    if fill is None:
        shp.fill.background()
    else:
        shp.fill.solid()
        shp.fill.fore_color.rgb = fill
    if line is None:
        shp.line.fill.background()
    else:
        shp.line.color.rgb = line
        shp.line.width = line_w
    shp.shadow.inherit = False
    return shp


def add_text_box(slide, x, y, w, h, valign=MSO_ANCHOR.TOP):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = valign
    tf.margin_left = tf.margin_right = Pt(2)
    tf.margin_top = tf.margin_bottom = Pt(1)
    return tb


def fill_para(p, segments, size, align=PP_ALIGN.LEFT, space_after=0, line=None):
    """segments: [(text, bold, color)] 或 [(text, bold)]"""
    p.alignment = align
    if space_after:
        p.space_after = Pt(space_after)
    if line:
        p.line_spacing = line
    for seg in segments:
        text, bold = seg[0], seg[1]
        color = seg[2] if len(seg) > 2 else C_BLACK
        set_run(p.add_run(), text, size, bold=bold, color=color)


GRID_STYLE_ID = "{5940675A-B579-460E-94D1-54222C63F5DA}"  # "No Style, Table Grid"


def _apply_grid_table_style(tbl):
    """去除主题带状底纹，改用细黑边框网格样式（对齐 NXA 样板表格观感）。"""
    ns = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
    tblPr = tbl._tbl.tblPr
    for attr in ("firstRow", "bandRow", "firstCol", "lastRow", "lastCol", "bandCol"):
        if attr in tblPr.attrib:
            del tblPr.attrib[attr]
    sid = tblPr.find(f"{ns}tableStyleId")
    if sid is None:
        sid = tblPr.makeelement(f"{ns}tableStyleId", {})
        tblPr.append(sid)
    sid.text = GRID_STYLE_ID


def zone_header(slide, x, y, w, title, verdict=None, size=12):
    """分区标题条: 白底黑框黑字加粗；verdict 为 -可行/-部分可行 后缀（部分可行标红）。"""
    bar = add_rect(slide, x, y, w, 0.34, fill=C_WHITE)
    tf = bar.text_frame
    tf.word_wrap = False
    tf.margin_left = tf.margin_right = Pt(4)
    tf.margin_top = tf.margin_bottom = Pt(0)
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    segs = [(title, True)]
    if verdict:
        red = "部分可行" in verdict or "不" in verdict
        segs.append(("-" + verdict, True, C_RED if red else C_BLACK))
    fill_para(p, segs, size)
    return bar


def add_table(slide, x, y, w, h, headers, rows, col_widths=None, size=8,
              header_size=None, first_col_left=False):
    """细边框表格；headers 可为 None（无表头）。col_widths: 英寸列表，None 则均分。"""
    n_rows = len(rows) + (1 if headers else 0)
    n_cols = len(headers or rows[0])
    gfx = slide.shapes.add_table(n_rows, n_cols, Inches(x), Inches(y),
                                 Inches(w), Inches(h))
    tbl = gfx.table
    _apply_grid_table_style(tbl)
    if col_widths:
        total = sum(col_widths)
        for i, cw in enumerate(col_widths):
            tbl.columns[i].width = Emu(int(Inches(w) * cw / total))
    if headers:
        tbl.rows[0].height = Emu(int(Inches(h) / n_rows * 1.1))
    for ri, row in enumerate(([headers] + rows) if headers else rows):
        for ci, val in enumerate(row):
            cell = tbl.cell(ri, ci)
            cell.margin_left = cell.margin_right = Pt(2)
            cell.margin_top = cell.margin_bottom = Pt(0)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            tf = cell.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            p.alignment = PP_ALIGN.LEFT if (first_col_left and ci == 0) else PP_ALIGN.CENTER
            is_hdr = headers and ri == 0
            set_run(p.add_run(), str(val),
                    (header_size or size + 0.5) if is_hdr else size,
                    bold=is_hdr)
            if is_hdr:
                cell.fill.solid()
                cell.fill.fore_color.rgb = C_HDR_FILL
    return tbl


def chip(slide, x, y, w, text, size=11):
    """顶部 accent1 标签牌：需求来源/规划方向/产品平台。"""
    shp = add_rect(slide, x, y, w, 0.38, fill=C_CHIP, line=None)
    tf = shp.text_frame
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf.margin_left = Pt(4)
    p = tf.paragraphs[0]
    fill_para(p, [(text, True, C_WHITE)], size)
    return shp


# ---------------------------------------------------------------- 一页纸主版
def build_one_pager(slide, spec):
    # R1 标题（>24 字符自动缩号防换行挤压版面）
    full_title = f"【{spec['title_category']}】 {spec['title_product']}"
    t_size = 20 if len(full_title) <= 24 else 17
    tb = add_text_box(slide, 0.2, 0.12, 6.2, 0.72)
    fill_para(tb.text_frame.paragraphs[0],
              [(f"【{spec['title_category']}】 ", True, C_TITLE),
               (spec["title_product"], True, C_TITLE)], t_size)

    # R2 承接单位 + 项目团队表（6.4,0.25 6.7x0.78，3r x 8c；承接单位跨列合并）
    team = spec["team"]
    roles = ["负责人", "产品", "研发", "制造", "质量", "财务", "供应链"]
    tbl = add_table(slide, 6.4, 0.25, 6.7, 0.78,
                    None,
                    [["承接单位", spec["org_unit"], "", "", "", "", "", ""],
                     ["项目团队"] + roles,
                     [team.get(r, "") for r in roles]],
                    col_widths=[1.3, 1, 1, 1, 1, 1, 1, 1], size=9)
    tbl.cell(0, 1).merge(tbl.cell(0, 7))

    # R3 顶部标签牌 + 项目计划表
    meta = spec["meta"]
    chip(slide, 0.4, 1.05, 2.45, f"需求来源：{meta['需求来源']}")
    chip(slide, 3.0, 1.05, 2.45, f"规划方向：{meta['规划方向']}")
    chip(slide, 5.6, 1.05, 2.2, f"产品平台：{meta['产品平台']}")
    plan = spec["plan"]["phases"]
    add_table(slide, 7.95, 1.05, 5.15, 0.52,
              ["项目计划"] + [p["name"] for p in plan],
              [[""] + [p["time"] for p in plan]], size=8.5, header_size=8.5)

    # L1 需求背景与调研（0.4,1.6 3.9x1.62）
    body = add_text_box(slide, 0.4, 1.62, 3.9, 1.6)
    fill_para(body.text_frame.paragraphs[0],
              [("需求背景：", True), (spec["research"], False)], 9, line=1.05)

    # L2 应用场景及客户痛点（header 0.4,3.3；box 0.4,3.68 3.9x0.98）
    zone_header(slide, 0.4, 3.3, 3.9, "应用场景及客户痛点")
    sp = spec["scenario_pain"]
    tb = add_text_box(slide, 0.42, 3.68, 3.86, 0.98)
    tf = tb.text_frame
    fill_para(tf.paragraphs[0], [("应用场景：", True), (sp["应用场景"], False)], 9)
    for i, pain in enumerate(sp["客户痛点"]):
        fill_para(tf.add_paragraph(), [(f"{i+1}、{pain}", False)], 9)

    # L3 快览（竞争对手/目标行业/销售通路）
    qf = spec["quick_facts"]
    y = 4.75
    for label in ["竞争对手", "目标行业", "销售通路"]:
        zone_header(slide, 0.4, y, 3.9, label, size=11)
        val = add_rect(slide, 0.4, y + 0.34, 3.9, 0.36, fill=C_WHITE)
        tfv = val.text_frame
        tfv.vertical_anchor = MSO_ANCHOR.MIDDLE
        tfv.margin_left = Pt(4)
        fill_para(tfv.paragraphs[0], [(qf.get(label, ""), False)], 10)
        y += 0.78

    # M1 产品定义（4.3,1.6 3.9x3.05）
    zone_header(slide, 4.3, 1.6, 3.9, "产品定义")
    pd = spec["product_definition"]
    tb = add_text_box(slide, 4.32, 1.98, 3.86, 2.68)
    tf = tb.text_frame
    first = tf.paragraphs[0]
    fill_para(first, [("外观：", True), (pd["外观"], False)], 9.5)
    fill_para(tf.add_paragraph(), [("材质：", True), (pd["材质"], False)], 9.5)
    fill_para(tf.add_paragraph(), [("认证：", True), (pd["认证"], False)], 9.5)
    fill_para(tf.add_paragraph(), [("性能及质量可靠性：", True)], 9.5)
    for param in pd["性能参数"]:
        fill_para(tf.add_paragraph(), [(param, False)], 9.5)

    # M2 价格、目标成本及毛利（4.3,4.75 3.9x2.55）
    zone_header(slide, 4.3, 4.75, 3.9, "价格、目标成本及毛利")
    pc = spec["price_cost"]
    tb = add_text_box(slide, 4.32, 5.12, 3.86, 0.72)
    fill_para(tb.text_frame.paragraphs[0], [(pc["策略"], True)], 9)
    st = pc["spec_table"]
    add_table(slide, 4.3, 5.9, 3.9, 1.35,
              st["headers"], st["rows"], size=8,
              col_widths=st.get("col_widths"))

    # R1 技术可行性（8.3,1.6 4.75x2.0）
    tec = spec["technical_feasibility"]
    zone_header(slide, 8.3, 1.6, 4.75, "技术可行性", verdict=tec["verdict"])
    tb = add_text_box(slide, 8.32, 1.98, 4.71, 1.6)
    tf = tb.text_frame
    fill_para(tf.paragraphs[0], [(tec["方案引言"], False)], 9)
    for item in tec["方案"]:
        fill_para(tf.add_paragraph(), [(item, False)], 9)
    fill_para(tf.add_paragraph(), [("创新点：", True), (tec.get("创新点", ""), False)], 9)
    if tec.get("不满足项"):
        fill_para(tf.add_paragraph(),
                  [("暂不满足：", True, C_RED), (tec["不满足项"], False, C_RED)], 9)

    # R2 生产可行性（8.3,3.7 4.75x0.95）
    prod = spec["production_feasibility"]
    zone_header(slide, 8.3, 3.7, 4.75, "生产可行性", verdict=prod["verdict"])
    tb = add_text_box(slide, 8.32, 4.07, 4.71, 0.56)
    items = "；".join(f"{k}：{prod[k]}" for k in ["人员", "设备", "场地", "物料"] if k in prod)
    fill_para(tb.text_frame.paragraphs[0], [(items, False)], 9)

    # R3 财务可行性（8.3,4.75 4.75x2.55）
    zone_header(slide, 8.3, 4.75, 4.75, "财务可行性")
    fin = spec["finance"]
    tb = add_text_box(slide, 8.32, 5.12, 4.71, 0.5)
    fill_para(tb.text_frame.paragraphs[0], [(fin["summary"], True)], 9)
    tb = add_text_box(slide, 8.32, 5.58, 4.71, 0.2)
    fill_para(tb.text_frame.paragraphs[0], [("项目投入（万元）：", True)], 8.5)
    inv = fin["investment"]
    add_table(slide, 8.3, 5.78, 4.75, 0.6,
              inv["headers"], inv["rows"], size=7.5)
    tb = add_text_box(slide, 8.32, 6.42, 4.71, 0.2)
    fill_para(tb.text_frame.paragraphs[0],
              [(fin.get("forecast_title", "销售预测："), True)], 8.5)
    fc = fin["forecast"]
    add_table(slide, 8.3, 6.62, 4.75, 0.78,
              fc["headers"], fc["rows"], size=8)


# ---------------------------------------------------------------- 附录页
def build_risk_appendix(slide, spec):
    tb = add_text_box(slide, 0.4, 0.2, 12.5, 0.6)
    fill_para(tb.text_frame.paragraphs[0],
              [("附录A  风险预案与有条件立项 —— ", True, C_TITLE),
               (spec["title_product"], False, C_TITLE)], 18)
    risks = spec["risks"]
    zone_header(slide, 0.4, 1.0, 12.5, "风险识别与应对预案", size=12)
    rows = [[r.get("风险", ""), r.get("影响", ""), r.get("预案", ""),
             r.get("资源诉求", ""), r.get("责任人", "")] for r in risks]
    add_table(slide, 0.4, 1.4, 12.5, 2.6,
              ["风险", "影响", "应对预案", "资源诉求", "责任人"],
              rows, col_widths=[2.2, 2.4, 4.2, 2.4, 1.3], size=10,
              first_col_left=True)
    zone_header(slide, 0.4, 4.3, 12.5, "有条件立项条件", size=12)
    cond = spec.get("conditional_approval", [])
    tb = add_text_box(slide, 0.5, 4.72, 12.3, 2.3)
    tf = tb.text_frame
    for i, c in enumerate(cond):
        fill_para(tf.paragraphs[0] if i == 0 else tf.add_paragraph(),
                  [(f"{i+1}. {c}", False)], 12, space_after=6)


def build_validation_appendix(slide, spec):
    cv = spec["cross_validation"]
    tb = add_text_box(slide, 0.4, 0.2, 12.5, 0.6)
    fill_para(tb.text_frame.paragraphs[0],
              [("附录B  销售预测交叉验证 —— ", True, C_TITLE),
               (spec["title_product"], False, C_TITLE)], 18)
    zone_header(slide, 0.4, 1.0, 12.5, "独立推算链路：行业出货量 → 单台用量 → 总需求 → 与客户/销售预测对比", size=12)
    rows = [[s.get("步骤", ""), s.get("推算", ""), s.get("数据来源", "")]
            for s in cv["steps"]]
    add_table(slide, 0.4, 1.4, 12.5, 3.4, ["步骤", "推算过程", "数据来源"],
              rows, col_widths=[2.6, 7.3, 2.6], size=10, first_col_left=True)
    zone_header(slide, 0.4, 5.0, 12.5, "对比结论", size=12)
    tb = add_text_box(slide, 0.5, 5.42, 12.3, 1.6)
    fill_para(tb.text_frame.paragraphs[0],
              [(cv["对比结论"], True)], 12, line=1.2)


# ---------------------------------------------------------------- 主流程
def main():
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(2)
    spec_path, out_path = sys.argv[1], sys.argv[2]
    spec = json.loads(Path(spec_path).read_text(encoding="utf-8"))

    prs = Presentation()
    prs.slide_width = Emu(int(SLIDE_W * EMU_IN))
    prs.slide_height = Emu(int(SLIDE_H * EMU_IN))
    blank = prs.slide_layouts[6]

    s1 = prs.slides.add_slide(blank)
    build_one_pager(s1, spec)
    built = ["一页纸看板"]

    if spec.get("risks"):
        s2 = prs.slides.add_slide(blank)
        build_risk_appendix(s2, spec)
        built.append("附录A 风险预案")
    if spec.get("cross_validation"):
        s3 = prs.slides.add_slide(blank)
        build_validation_appendix(s3, spec)
        built.append("附录B 交叉验证")

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    prs.save(out_path)
    print(f"OK: {out_path} 已生成（{'、'.join(built)}）")


if __name__ == "__main__":
    main()
