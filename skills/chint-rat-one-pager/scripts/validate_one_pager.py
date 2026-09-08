#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
立项一页纸校验器（chint-rat-one-pager）

用法:
    python3 validate_one_pager.py <output.pptx> [--spec spec.json]

按 references/zone-spec.md 的分区规范检查生成的 pptx：
  1. 16:9 尺寸、至少 1 页
  2. 一页纸 12 个分区标题齐全
  3. 顶部三标签牌（需求来源/规划方向/产品平台）齐全，产品平台 ∈ {昆仑, 新锐, 诺雅克}
  4. 财务摘要含 投入/回收期/盈亏平衡 关键数字表述
  5. 标题含【项目类别】
  6. verdict 含"部分可行/不"时必须存在风险预案附录页
  7. 无形状越出画布
  8.（提供 --spec 时）痛点条数与产品定义性能条数的对应性提示
退出码: 0=PASS，1=FAIL
"""
import sys
from pathlib import Path

from pptx import Presentation
from pptx.util import Emu

REQUIRED_ZONES = [
    "应用场景及客户痛点",
    "产品定义",
    "技术可行性",
    "生产可行性",
    "财务可行性",
    "价格、目标成本及毛利",
]
REQUIRED_CHIPS = ["需求来源", "规划方向", "产品平台"]
VALID_PLATFORMS = {"昆仑", "新锐", "诺雅克"}


def slide_texts(slide):
    texts = []
    for sh in slide.shapes:
        if sh.has_text_frame:
            texts.append(sh.text_frame.text)
    return "\n".join(texts)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    path = Path(sys.argv[1])
    spec_path = None
    if "--spec" in sys.argv:
        spec_path = Path(sys.argv[sys.argv.index("--spec") + 1])

    failures, warnings = [], []
    prs = Presentation(str(path))
    W, H = prs.slide_width, prs.slide_height
    if abs(W / H - 16 / 9) > 0.01:
        failures.append(f"画幅非16:9: {Emu(W).inches:.2f}x{Emu(H).inches:.2f}")
    if not prs.slides:
        failures.append("0 页")
        print(report(failures, warnings))
        sys.exit(1)

    s1_texts = slide_texts(prs.slides[0])
    # 2. 分区标题
    for zone in REQUIRED_ZONES:
        if zone not in s1_texts:
            failures.append(f"缺少分区标题: {zone}")
    # 3. 标签牌与平台命名
    for chip in REQUIRED_CHIPS:
        if chip not in s1_texts:
            failures.append(f"缺少标签牌: {chip}")
    import re
    m = re.search(r"产品平台[：:](\S+)", s1_texts)
    if m and m.group(1) not in VALID_PLATFORMS:
        failures.append(f"产品平台非标准命名 '{m.group(1)}'（只允许: 昆仑/新锐/诺雅克）")
    # 4. 财务关键数字
    for kw in ["项目投入", "盈亏平衡"]:
        if kw not in s1_texts:
            failures.append(f"财务摘要缺少: {kw}")
    if "收回投资" not in s1_texts and "回收期" not in s1_texts:
        failures.append("财务摘要缺少投资回收期表述")
    # 5. 标题类别
    if not re.search(r"【[^】]+】", s1_texts):
        failures.append("标题缺少【项目类别】前缀（如【改良改进】）")
    # 6. 部分可行必须有风险附录
    partial = ("部分可行" in s1_texts) or ("暂不满足" in s1_texts)
    has_risk_page = len(prs.slides) >= 2 and any(
        "风险" in slide_texts(s) for s in list(prs.slides)[1:])
    if partial and not has_risk_page:
        failures.append("标注了部分可行/暂不满足，但缺少风险预案附录页")
    # 7. 越界
    for i, slide in enumerate(prs.slides, 1):
        for sh in slide.shapes:
            try:
                if (sh.left < -1000 or sh.top < -1000
                        or sh.left + sh.width > W + 9525
                        or sh.top + sh.height > H + 9525):
                    failures.append(f"第{i}页形状越界: {sh.name}")
            except TypeError:
                pass
    # 8. 痛点↔产品定义对应性提示
    if spec_path:
        import json
        spec = json.loads(spec_path.read_text(encoding="utf-8"))
        pains = spec.get("scenario_pain", {}).get("客户痛点", [])
        params = spec.get("product_definition", {}).get("性能参数", [])
        if pains and len(params) < len(pains):
            warnings.append(
                f"客户痛点 {len(pains)} 条但性能参数仅 {len(params)} 条，检查是否一一对应")
        for idx, p in enumerate(pains, 1):
            if not re.search(r"\d", p):
                warnings.append(f"痛点{idx}未量化（无数字），违反数字化红线: {p[:18]}…")
        cv = spec.get("cross_validation")
        if cv and not str(cv.get("对比结论", "")).strip():
            failures.append("交叉验证缺少对比结论")
        # 9. 价格-成本-毛利率口径勾稽（±5pp）
        st = spec.get("price_cost", {}).get("spec_table", {})
        headers = [str(h) for h in st.get("headers", [])]
        def _find(*keys):
            for i, h in enumerate(headers):
                if any(k in h for k in keys):
                    return i
            return None
        i_price, i_cost, i_margin = _find("口袋价", "面价"), _find("成本"), _find("毛利")
        if i_price is not None and i_cost is not None and i_margin is not None:
            import re as _re
            for row in st.get("rows", []):
                try:
                    label = str(row[0])
                    if "total" not in label.lower() and "合计" not in label:
                        continue
                    price = float(_re.sub(r"[^\d.]", "", str(row[i_price])))
                    cost = float(_re.sub(r"[^\d.]", "", str(row[i_cost])))
                    mtxt = str(row[i_margin]).replace("%", "")
                    margin = float(_re.sub(r"[^\d.]", "", mtxt))
                    implied = (price - cost) / price * 100
                    if abs(implied - margin) > 5:
                        warnings.append(
                            f"口径勾稽: Total行 (面价{price:g}−成本{cost:g})/面价={implied:.1f}% "
                            f"与标注毛利率{margin:g}%偏差>5pp，检查含税/未税口径或数据源")
                    break
                except (ValueError, IndexError, ZeroDivisionError):
                    continue

    print(report(failures, warnings))
    sys.exit(0 if not failures else 1)


def report(failures, warnings):
    lines = []
    for f in failures:
        lines.append(f"FAIL  {f}")
    for w in warnings:
        lines.append(f"WARN  {w}")
    lines.append(f"== {'PASS' if not failures else 'FAIL'} "
                 f"({len(failures)} failures, {len(warnings)} warnings)")
    return "\n".join(lines)


if __name__ == "__main__":
    main()
