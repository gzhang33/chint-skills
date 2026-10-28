#!/usr/bin/env python3
"""验证 CHINT 运营分析 PPTX 的生成结果。

用法:
    python verify_pptx.py <生成.pptx> <模板.pptx>

检查项:
    1. 每页数据表(表格 8/1/4/9) 内容是否相对模板发生变更 (= 已正确填充)
    2. 每页 Action Tracker 表(表格 7/7/7/8/10) 是否与模板逐字节一致 (= 原样保留, 预期行为)
    3. 图表 series 数量是否合理

退出码:
    0 = 全部通过
    1 = 存在异常(数据表未填充 / Action Tracker 被改)
    2 = 参数错误
"""
import sys
import zipfile
import re

# 代码实际填充的数据表: slide -> 表名
DATA_MAP = {2: "表格 8", 3: "表格 1", 4: "表格 1", 5: "表格 4", 6: "表格 9"}
# 代码从不引用的 Action Tracker 表: slide -> 表名
ACTION_MAP = {2: "表格 7", 3: "表格 7", 4: "表格 7", 5: "表格 8", 6: "表格 10"}


def slide_tables(path):
    """返回 {slide_index: {shape_name: tbl_xml}}。"""
    z = zipfile.ZipFile(path)
    res = {}
    n = len([x for x in z.namelist() if re.match(r"ppt/slides/slide\d+\.xml$", x)])
    for s in range(1, n + 1):
        xml = z.read(f"ppt/slides/slide{s}.xml").decode("utf-8")
        d = {}
        for gf in re.findall(r"<p:graphicFrame>.*?</p:graphicFrame>", xml, re.S):
            m = re.search(r'<p:cNvPr[^>]*\bname="([^"]+)"', gf)
            nm = m.group(1) if m else "?"
            t = re.findall(r"<a:tbl\b[^>]*>.*?</a:tbl>", gf, re.S)
            if t:
                d[nm] = t[0]
        res[s] = d
    return res, n


def main():
    if len(sys.argv) != 3:
        print("用法: python verify_pptx.py <生成.pptx> <模板.pptx>")
        sys.exit(2)

    out_path, tpl_path = sys.argv[1], sys.argv[2]
    t_out, n = slide_tables(out_path)
    t_tpl, _ = slide_tables(tpl_path)

    print(f"=== 验证: {out_path} (共 {n} 页) ===\n")
    ok = True

    for s in range(1, n + 1):
        if s in DATA_MAP:
            dn = DATA_MAP[s]
            if dn in t_out[s] and dn in t_tpl.get(s, {}):
                changed = t_tpl[s][dn] != t_out[s][dn]
                ok = ok and changed
                print(f"  slide{s} [数据表 {dn}] 内容变更={'是 ✓' if changed else '否 ✗ (未填充!)'}")
            else:
                ok = False
                print(f"  slide{s} [数据表 {dn}] 缺失! 模板有:{dn in t_tpl.get(s, {})} 生成有:{dn in t_out.get(s, {})}")

        if s in ACTION_MAP:
            an = ACTION_MAP[s]
            if an in t_out[s] and an in t_tpl.get(s, {}):
                ident = t_tpl[s][an] == t_out[s][an]
                ok = ok and ident
                print(f"  slide{s} [ActionTracker {an}] 原样保留={'是 ✓' if ident else '否 ✗ (被改!)'}")
            else:
                print(f"  slide{s} [ActionTracker {an}] 模板有:{an in t_tpl.get(s, {})} 生成有:{an in t_out.get(s, {})}")

    # 图表 series 数
    z = zipfile.ZipFile(out_path)
    charts = [x for x in z.namelist() if re.match(r"ppt/charts/chart\d+\.xml$", x)]
    print(f"\n=== 图表 ===\n  生成文件含图表: {len(charts)} 个")
    for ch in charts:
        cx = z.read(ch).decode("utf-8")
        sers = re.findall(r"<c:ser>", cx)
        print(f"  {ch}: series 数={len(sers)}")

    print(f"\n总结: {'全部通过 ✓' if ok else '存在异常 ✗'}")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
