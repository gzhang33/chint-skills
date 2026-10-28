#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""fill_one_pager.py — chint-pm-RAT 模板填充（格式零漂移 · PM 范围）

用法:
    python3 fill_one_pager.py <spec.json> <out.pptx> [--base template/one_pager_base.pptx]

基座 = RAT 表格模版（主 12×9 表 + 团队表 + 3 浮动小表，layout12 带 logo）+ 附录A/B。
PM 范围：需求背景/产品定义（含性能及质量可靠性）/应用场景及客户痛点/竞争对手/目标行业/
销售通路/标签牌/项目计划/承接单位团队。
非 PM 区（技术可行性、生产可行性、价格成本毛利、财务可行性）：保留标题条，正文与浮动
小表数据清空，其他部门续填。
超字符预算硬失败拒生成（主表行会膨胀推挤版面）；附录仅 WARN。
"""
import argparse
import json
import re
import sys
from pathlib import Path

from pptx import Presentation

sys.path.insert(0, str(Path(__file__).parent))
import tplkit as tk

# 主表（shapes[2]）单元格锚点：PM 填充区
CELLS = {
    'chip_source': (0, 0),
    'chip_dir': (0, 2),
    'chip_platform': (0, 3),
    'research': (2, 0),
    'm1_body': (3, 3),
    'pain': (5, 0),
    'qf_comp': (7, 0),
    'qf_ind': (9, 0),
    'qf_chan': (11, 0),
}
# 非 PM 区：标题保留，正文清空
CLEAR_CELLS = {
    'r1_body': (3, 5),
    'r2_body': (5, 5),
    'm2_strategy': (7, 1),
    'fin_summary': (7, 5),
}
# 非 PM 区标题锚点（存在性校验，保留原文）
KEEP_HEADERS = [(2, 5, '技术可行性'), (4, 5, '生产可行性'),
                (6, 1, '价格、目标成本及毛利'), (6, 5, '财务可行性')]

# 目标行业枚举（正泰行业口径 10 项；目标行业必须取且仅取其一）
INDUSTRY_ENUM = [
    '信息与通讯行业业务', 'OEM业务', '电网业务', '发电与新能源业务',
    '基础能源与流程工业业务', '基础设施业务', '盘柜厂业务', '建筑地产业务',
    '交通与运输业务', '流通业务',
]


def cell(table, r, c):
    return table.cell(r, c)


def cell_paras(cell, items):
    """单元格段落重建（保留 pPr 与原型 run 样式）。items: [(proto_idx, segs)]"""
    tk.set_paras(cell, items)


def clear_cell(table, r, c):
    cell_paras(cell(table, r, c), [(0, [('', 0, None)])])


# ---------------------------------------------------------------- 预算
def _eff(s):
    return round(sum(1.0 if ord(ch) > 0x2E7F else 0.5 for ch in str(s)), 1)


def _lines(s, width):
    return -(-_eff(s) // width)


def check_budgets(spec):
    fails = []

    def hard(zone, val, limit):
        e = _eff(val)
        if e > limit:
            fails.append(f'{zone} {e}/{limit} 字超预算（主表行会膨胀推挤版面）')

    hard('标题', f"【{spec['title_category']}】{spec['title_product']}", 30)
    hard('标签牌-需求来源', f"需求来源：{spec['meta']['需求来源']}", 12)
    hard('标签牌-规划方向', f"规划方向：{spec['meta']['规划方向']}", 14)
    hard('标签牌-产品平台', f"产品平台：{spec['meta'].get('产品平台', '')}", 17)
    hard('承接单位', spec['org_unit'], 30)

    r_ = spec['research']
    lines = _lines(r_.get('intro', ''), 32)
    hard('L1 intro ≤3行(32字/行)', r_.get('intro', ''), 96)
    for i, it in enumerate(r_.get('items', []), 1):
        lines += _lines(f'{i}、{it}', 32)
        hard(f'L1 条目{i} ≤2行(64字)', f'{i}、{it}', 64)
    if lines > 10:
        fails.append(f'L1 合计约 {lines}/10 行超预算')

    sp = spec['scenario_pain']
    lines = _lines(f"应用场景：{sp['应用场景']}", 26) + 1
    for i, p in enumerate(sp['客户痛点'], 1):
        pl = _lines(p, 26)
        lines += pl
        if pl > 2:
            fails.append(f'L2 痛点{i} 超 2 行')
    if lines > 6:
        fails.append(f'L2 痛点格约 {lines}/6 行超预算')

    for k, lim in (('竞争对手', 20), ('目标行业', 20), ('销售通路', 20)):
        hard(f'L3 {k}', spec['quick_facts'].get(k, ''), lim)
    ind = spec['quick_facts'].get('目标行业', '')
    if ind not in INDUSTRY_ENUM:
        fails.append(f"目标行业 '{ind}' 不在行业口径枚举内：{('、'.join(INDUSTRY_ENUM))}")
    comp = spec['quick_facts'].get('竞争对手', '')
    if comp and ('/' in comp or '、' in comp or ';' in comp or '；' in comp):
        fails.append("竞争对手只列最大的一家（多家用 research 深挖后取一手对手）")

    pd_ = spec['product_definition']
    total = 0
    for k in ('外观', '材质', '认证'):
        hard(f'M1 {k} ≤2行(54字)', f'{k}：{pd_[k]}', 54)
        total += _lines(f'{k}：{pd_[k]}', 27)
    total += 1
    for i, p in enumerate(pd_['性能参数'], 1):
        pl = _lines(p, 27)
        total += pl
        if pl > 2:
            fails.append(f'M1 性能{i} 超 2 行')
    if total > 15:
        fails.append(f'M1 合计约 {total}/15 行超预算')
    return fails


# ---------------------------------------------------------------- 页1填充
def fill_slide1(prs, spec):
    slide = prs.slides[0]
    shapes = list(slide.shapes)
    table = main_table(prs)

    # 标题
    title = shapes[1]
    tk.set_paras(title, [(0, [(f"【{spec['title_category']}】 ", 0, None),
                              (spec['title_product'], 0, None)])])

    # 团队表（shapes[0]）
    team = spec['team']
    tk.set_cell(tk.tbl(shapes[0]), 0, 1, spec['org_unit'])
    for i, role in enumerate(['负责人', '产品', '研发', '制造', '质量', '财务', '供应链'], 1):
        tk.set_cell(tk.tbl(shapes[0]), 2, i, team.get(role, ''))

    # 标签牌 + 项目计划（主表内）
    cell_paras(cell(table, *CELLS['chip_source']),
               [(0, [(f"需求来源：{spec['meta']['需求来源']}", 0, None)])])
    cell_paras(cell(table, *CELLS['chip_dir']),
               [(0, [(f"规划方向：{spec['meta']['规划方向']}", 0, None)])])
    cell_paras(cell(table, *CELLS['chip_platform']),
               [(0, [(f"产品平台：{spec['meta'].get('产品平台', '')}", 0, None)])])
    phases = spec['plan']['phases']
    if len(phases) != 4:
        raise SystemExit(f'BUDGET FAIL  plan.phases 必须恰 4 期（P1-P4），收到 {len(phases)}')
    for i, ph in enumerate(phases, 5):
        cell_paras(cell(table, 0, i), [(0, [(ph['name'], 0, None)])])
        cell_paras(cell(table, 1, i), [(0, [(ph['time'], 0, None)])])

    # L1 需求背景
    r_ = spec['research']
    items = [(0, [(r_.get('intro', ''), 0, None)])]
    for i, it in enumerate(r_.get('items', []), 1):
        items.append((1, [(f'{i}、{it}', 1, None)]))
    cell_paras(cell(table, *CELLS['research']), items)

    # M1 产品定义（外观/材质/认证/性能及质量可靠性 同格）
    pd_ = spec['product_definition']
    sh = cell(table, *CELLS['m1_body'])
    items = []
    for k in ('外观', '材质', '认证'):
        items.append((len(items), [(f'{k}：', 0, True), (pd_[k], 0, False)]))
    items.append((2, [('性能及质量可靠性：', 0, True)]))
    for p in pd_['性能参数']:
        items.append((2, [(p, 0, None)]))
    cell_paras(sh, items)

    # L2 痛点（Ø 符号即列表语义，条目不带数字前缀）
    sp = spec['scenario_pain']
    items = [(0, [('应用场景：', 0, True), (sp['应用场景'], 0, False)]),
             (1, [('客户痛点：', 0, True)])]
    for p in sp['客户痛点']:
        items.append((1, [(re.sub(r'^\d+、', '', p), 0, None)]))
    cell_paras(cell(table, *CELLS['pain']), items)

    # L3 快览
    qf = spec['quick_facts']
    cell_paras(cell(table, *CELLS['qf_comp']), [(0, [(qf.get('竞争对手', ''), 0, None)])])
    cell_paras(cell(table, *CELLS['qf_ind']), [(0, [(qf.get('目标行业', ''), 0, None)])])
    cell_paras(cell(table, *CELLS['qf_chan']), [(0, [(qf.get('销售通路', ''), 0, None)])])

    # 非 PM 区：标题存在性校验（保留原文），正文清空
    for r, c, must in KEEP_HEADERS:
        t = cell(table, r, c).text
        if must not in t:
            raise SystemExit(f'ANCHOR FAIL: 主表({r},{c}) 应含"{must}"，实际"{t[:20]}"——基座与脚本不同步')
    for r, c in CLEAR_CELLS.values():
        clear_cell(table, r, c)

    # 浮动小表已从基座删除（build_base），无需清理


def main_table(prs):
    return list(prs.slides[0].shapes)[2].table


# ---------------------------------------------------------------- 附录填充
def find_table(slide):
    for sh in slide.shapes:
        if sh.has_table:
            return sh
    raise SystemExit('附录页缺少表格')


def left_align(body):
    for p in body.text_frame.paragraphs:
        p.alignment = None


def fill_appendix_a(slide, spec):
    t = tk.tbl(find_table(slide))
    risks = spec.get('risks', [])
    while len(tk.rows(t)) - 1 > len(risks):
        tk.delete_row(t, len(tk.rows(t)) - 1)
    while len(tk.rows(t)) - 1 < len(risks):
        tk.clone_row(t, 1)
    for ri, r_ in enumerate(risks, 1):
        for ci, k in enumerate(('风险', '影响', '预案', '资源诉求', '责任人')):
            tk.set_cell(t, ri, ci, r_.get(k, ''))
    body = None
    for sh in slide.shapes:
        if sh.has_text_frame and '条件占位' in sh.text_frame.text:
            body = sh
    if body is not None and spec.get('conditional_approval'):
        items = [((i - 1) % 2, [(f'{i}. {c}', 0, None)])
                 for i, c in enumerate(spec['conditional_approval'], 1)]
        tk.set_paras(body, items)
        left_align(body)


def fill_appendix_b(slide, spec):
    cv = spec.get('cross_validation')
    if not cv:
        return
    t = tk.tbl(find_table(slide))
    steps = cv.get('steps', [])
    while len(tk.rows(t)) - 1 > len(steps):
        tk.delete_row(t, len(tk.rows(t)) - 1)
    while len(tk.rows(t)) - 1 < len(steps):
        tk.clone_row(t, 1)
    for ri, s_ in enumerate(steps, 1):
        for ci, k in enumerate(('步骤', '推算', '数据来源')):
            tk.set_cell(t, ri, ci, s_.get(k, ''))
    body = None
    for sh in slide.shapes:
        if sh.has_text_frame and '对比结论占位' in sh.text_frame.text:
            body = sh
    if body is not None:
        tk.set_paras(body, [(0, [(cv.get('对比结论', ''), 0, None)])])
        left_align(body)


# ---------------------------------------------------------------- 主流程
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('spec')
    ap.add_argument('out')
    ap.add_argument('--base', default=str(Path(__file__).parent.parent / 'template' / 'one_pager_base.pptx'))
    a = ap.parse_args()

    spec = json.loads(Path(a.spec).read_text(encoding='utf-8'))
    dropped = [k for k in ('technical_feasibility', 'production_feasibility',
                           'price_cost', 'finance') if k in spec]
    if dropped:
        print(f'SCHEMA v3  忽略非 PM 段: {dropped}（技术/生产/价格/财务由其他部门填写）')

    fails = check_budgets(spec)
    if fails:
        for f in fails:
            print(f'BUDGET FAIL  {f}')
        print('== 预算预检未通过，已拒绝生成。按报错压缩 spec 后重试。')
        sys.exit(1)

    prs = Presentation(a.base)
    fill_slide1(prs, spec)
    fill_appendix_a(prs.slides[1], spec)
    fill_appendix_b(prs.slides[2], spec)

    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(out))
    print(f'OK: {out} 已生成（chint-pm-RAT 模板填充：PM 范围正文 + 附录A + 附录B）')


if __name__ == '__main__':
    main()
