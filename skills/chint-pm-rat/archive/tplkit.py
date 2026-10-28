#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tplkit — 模板手术助手（chint-pm-RAT 模板填充路线共享层）

原则：一切新元素都从模板既有元素 deepcopy 而来，样式（字体/灰底/边框/符号）
构造性继承，不从零绘制。坐标单位英寸，内部 EMU。
"""
from copy import deepcopy

from lxml import etree
from pptx.oxml.ns import qn
from pptx.util import Emu, Inches

A_NS = 'http://schemas.openxmlformats.org/drawingml/2006/main'


def el(tag):
    return qn(f'a:{tag}')


def make(tag):
    """创建 a: 命名空间元素（append 进既有树后由父级 nsmap 接管序列化）。"""
    return etree.Element(qn(f'a:{tag}'))


def inch(v):
    return round(Emu(v).inches, 2) if v is not None else None


# ---------------------------------------------------------------- 文本手术
def proto_capture(sh):
    """捕获形状的段落原型：[(pPr, [rPr...]), ...] 供重建。"""
    protos = []
    for p in sh.text_frame._txBody.findall(el('p')):
        pPr = p.find(el('pPr'))
        runs = [deepcopy(r.find(el('rPr'))) for r in p.findall(el('r')) if r.find(el('rPr')) is not None]
        protos.append((deepcopy(pPr) if pPr is not None else None, runs))
    return protos


def set_paras(sh, items):
    """整体重建形状段落。items: [para_spec]
    para_spec: (proto_idx, [segment...])；segment = (text, run_idx, bold|None)
    run_idx 选该段原型的第几个 run 的 rPr 作为模板。
    """
    protos = proto_capture(sh)
    txBody = sh.text_frame._txBody
    for p in txBody.findall(el('p')):
        txBody.remove(p)
    for proto_idx, segs in items:
        pPr, rprs = protos[min(proto_idx, len(protos) - 1)]
        p = make('p')
        if pPr is not None:
            p.append(deepcopy(pPr))
        for text, run_idx, bold in segs:
            rPr = rprs[run_idx] if run_idx < len(rprs) else (rprs[-1] if rprs else None)
            p.append(_make_run(rPr, text, bold))
        txBody.append(p)


def _make_run(rPr, text, bold=None):
    r = make('r')
    if rPr is not None:
        rPr_c = deepcopy(rPr)
        if bold is not None:
            rPr_c.set('b', '1' if bold else '0')
        r.append(rPr_c)
    t = make('t')
    t.text = text
    t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
    r.append(t)
    return r


def set_text(sh, text, run_idx=0, bold=None):
    """单段形状整体替换文本（保留 pPr 与第 run_idx 个 run 的 rPr）。"""
    set_paras(sh, [(0, [(text, run_idx, bold)])])


# ---------------------------------------------------------------- 表格手术
def tbl(sh):
    return sh.table._tbl


def grid_cols(tblEl):
    return tblEl.find(el('tblGrid')).findall(el('gridCol'))


def rows(tblEl):
    return tblEl.findall(el('tr'))


def _row_uses_continuation(tr):
    return any(tc.get('hMerge') == '1' for tc in tr.findall(el('tc')))


def delete_col(tblEl, col_idx):
    """合并感知地删一列。按行自动识别两种真实模型：
    1) WPS 续格模型（存在 hMerge 续格）：每个物理 tc 恰占 1 逻辑列。
       删续格直接移除；删合并块首列则移除原格、提升首个续格为新原格（span-1）。
    2) 纯 gridSpan 模型（无续格）：按 acc 定位，跨列格覆盖时降 span。"""
    cols = grid_cols(tblEl)
    w = int(cols[col_idx].get('w'))
    tblEl.find(el('tblGrid')).remove(cols[col_idx])
    for tr in rows(tblEl):
        tcs = tr.findall(el('tc'))
        if _row_uses_continuation(tr):
            if col_idx >= len(tcs):
                continue
            tc = tcs[col_idx]
            if tc.get('hMerge') == '1':
                tr.remove(tc)
            else:
                span = int(tc.get('gridSpan', 1))
                if span > 1 and col_idx + 1 < len(tcs):
                    nxt = tcs[col_idx + 1]
                    tr.remove(tc)
                    nxt.attrib.pop('hMerge', None)
                    nxt.set('gridSpan', str(span - 1))
                else:
                    tr.remove(tc)
        else:
            acc = 0
            for tc in tcs:
                span = int(tc.get('gridSpan', 1))
                if acc <= col_idx < acc + span:
                    if span == 1:
                        tr.remove(tc)
                    else:
                        tc.set('gridSpan', str(span - 1))
                    break
                acc += span
    return w


def clear_row_spans(tblEl, row_idx):
    """清掉某行 tc 的 rowSpan/vMerge 标记（删行后防止悬空合并）。"""
    for tc in rows(tblEl)[row_idx].findall(el('tc')):
        for attr in ('rowSpan', 'vMerge', 'hMerge'):
            if tc.get(attr) is not None:
                del tc.attrib[attr]


def clone_col(tblEl):
    """克隆最后一列为新列（gridCol + 各行 tc），返回新列下标。"""
    grid = tblEl.find(el('tblGrid'))
    gc = deepcopy(grid.findall(el('gridCol'))[-1])
    grid.append(gc)
    for tr in rows(tblEl):
        tcs = tr.findall(el('tc'))
        tr.append(deepcopy(tcs[-1]))
    return len(grid.findall(el('gridCol'))) - 1


def collapse_span(tr, col_idx):
    """把行内从 col_idx 起的 gridSpan 合并单元格收缩 span（删除后列时用）。
    返回该 tc 的 span 值；无合并返回 1。"""
    tcs = tr.findall(el('tc'))
    idx = 0
    for tc in tcs:
        span = int(tc.get('gridSpan', 1))
        if idx == col_idx:
            return span
        idx += span
    return 0


def dec_span(tr, col_idx, by=1):
    tcs = tr.findall(el('tc'))
    idx = 0
    for tc in tcs:
        span = int(tc.get('gridSpan', 1))
        if idx <= col_idx < idx + span:
            tc.set('gridSpan', str(span - by))
            return True
        idx += span
    return False


def delete_row(tblEl, row_idx):
    trs = rows(tblEl)
    tblEl.remove(trs[row_idx])


def clone_row(tblEl, row_idx):
    tr = deepcopy(rows(tblEl)[row_idx])
    rows(tblEl)[-1].addnext(tr)
    return tr


def cell_run_pr(tc):
    """取单元格首 run 的 rPr 深拷贝（无则 None）。"""
    r = tc.find(f'{el("txBody")}/{el("p")}/{el("r")}')
    if r is None:
        return None
    rPr = r.find(el('rPr'))
    return deepcopy(rPr) if rPr is not None else None


def set_cell(tblEl, row_idx, col_idx, text, bold=None, size=None, donor_rpr=None):
    """按逻辑行列定位并替换单元格文本（保留样式）。
    WPS 续格模型下行内每 tc 占 1 逻辑列，命中续格时向前回溯合并原格写入；
    纯 gridSpan 模型按 acc 定位。donor_rpr: 无 run 时的 rPr 供体。"""
    tr = rows(tblEl)[row_idx]
    tcs = tr.findall(el('tc'))

    def _write(tc):
        txBody = tc.find(el('txBody'))
        ps = txBody.findall(el('p'))
        p0 = ps[0]
        r0 = p0.findall(el('r'))
        pPr = p0.find(el('pPr'))
        for p in ps:
            txBody.remove(p)
        np = make('p')
        if pPr is not None:
            np.append(deepcopy(pPr))
        if r0:
            np.append(_make_run(r0[0].find(el('rPr')), text, bold))
        else:
            np.append(_make_run(donor_rpr, text, bold))
        txBody.append(np)

    if any(tc.get('hMerge') == '1' for tc in tcs):
        idx = min(col_idx, len(tcs) - 1)
        while idx > 0 and tcs[idx].get('hMerge') == '1':
            idx -= 1
        _write(tcs[idx])
        return True
    acc = 0
    for tc in tcs:
        span = int(tc.get('gridSpan', 1))
        if acc <= col_idx < acc + span:
            _write(tc)
            return True
        acc += span
    return False


def normalize_table(tblEl, donor_tc=(0, 1), header_sz=None, body_sz=None):
    """所有单元格文本重建为单 run，rPr 取供体单元格，统一字号。
    用于清掉原型表里空单元格无 rPr / 杂字号的问题。"""
    trs = rows(tblEl)
    donor = trs[donor_tc[0]].findall(el('tc'))[donor_tc[1]]
    ref = cell_run_pr(donor)
    for ri, tr in enumerate(trs):
        for tc in tr.findall(el('tc')):
            txBody = tc.find(el('txBody'))
            cur = ''.join(t.text or '' for t in txBody.iter(el('t')))
            ps = txBody.findall(el('p'))
            pPr = ps[0].find(el('pPr')) if ps else None
            for p in ps:
                txBody.remove(p)
            np = make('p')
            if pPr is not None:
                np.append(deepcopy(pPr))
            rPr = deepcopy(ref) if ref is not None else None
            if rPr is not None:
                sz = header_sz if ri == 0 else body_sz
                if sz:
                    rPr.set('sz', str(int(sz * 100)))
            np.append(_make_run(rPr, cur))
            txBody.append(np)


def set_table_width(gfx, widths_emu):
    """重设 graphicFrame 宽度与 tblGrid 列宽。"""
    tblEl = gfx.table._tbl
    grid = tblEl.find(el('tblGrid'))
    for gc, w in zip(grid.findall(el('gridCol')), widths_emu):
        gc.set('w', str(int(w)))
    total = sum(int(w) for w in widths_emu)
    gfx.width = Emu(int(total))
