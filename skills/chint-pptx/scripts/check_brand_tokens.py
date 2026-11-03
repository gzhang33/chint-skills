#!/usr/bin/env python3
"""chint-pptx —— 品牌 token 快照一致性校验

回答三个问题：

1. **快照过期了吗**？重算 `chint-brand-design/scripts/chint_theme.py` 的 sha256，
   与 `spec/brand_tokens.json` 里记录的值比对。变了就提醒重新抓取（只警告不判负）。
2. **快照的 theme 和品牌真值对得上吗**？用 `ast` 解析品牌源，取出每个映射键对应的
   品牌 token 数值，与快照 `theme` 逐键比对。凡 `mapping.<key>.aligned == true` 的键
   不一致都算故障（退出 1）——这是"文档和引擎各说各话"的根因，必须零容忍。
   `aligned == false` 的是已登记的对齐待办，只提示不判负。
3. **引擎还在自带颜色副本吗**？引擎从 2026-09-17 票01 起改为读取快照，不再内嵌
   `DEFAULTS` 颜色表。守卫扫描引擎源码：若仍存在 `DEFAULTS` 颜色表副本、或这 9 个
   品牌色值仍以字面量硬编码，即判负（退出 1）。这条路径取代了旧版"读引擎 DEFAULTS
   与快照比"——因为引擎已无 DEFAULTS 可比。

退出码：0 = 一致或仅有已登记的待办；1 = 出现未登记的漂移 / 引擎仍硬编码；2 = 文件缺失/格式错误。

用法：
    python3 scripts/check_brand_tokens.py
    python3 scripts/check_brand_tokens.py --json report.json
    python3 scripts/check_brand_tokens.py --source /path/to/chint_theme.py

品牌真源定位顺序（跨设备可移植）：--source 参数 → 环境变量 CHINT_BRAND_DESIGN_SOURCE
→ 快照 source.path（绝对路径直接用；相对路径在候选 skills 根下解析）→ 从本 skill
向上逐层自动发现 chint-brand-design 同级目录。全部落空仅 [WARN] 降级，不判负。
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import pathlib
import re
import sys

SKILL = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL))
from core.output_paths import ensure_output_path

SPEC = SKILL / "spec" / "brand_tokens.json"
ENGINE = SKILL / "scripts" / "shell_rebuild_engine.py"

ENV_SOURCE = "CHINT_BRAND_DESIGN_SOURCE"
ENV_SKILLS_ROOT = "CHINT_SKILLS_ROOT"

# 9 个 VI 键（font 非色值，其余 8 个是品牌 hex）。守卫扫描只盯这 8 个 hex 字面量，
# 因为引擎改色后这些值必须只能从快照来，绝不能以字面量出现在引擎源码里。
GUARDED_HEXES = ("1E50E6", "0E387A", "50C8FF", "D7F0FF", "FFFFFF",
                 "64748B", "F6F9FD", "D2E2F4", "1437AA", "666666",
                 "F3F6FE", "E2E8F0")


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def resolve_brand_source(spec: dict, override: str | None) -> pathlib.Path | None:
    """跨设备定位品牌真源 chint_theme.py，按优先级：

    1) ``--source`` 命令行参数；
    2) 环境变量 ``CHINT_BRAND_DESIGN_SOURCE``；
    3) 快照 ``source.path``——绝对路径直接用；相对路径在候选 skills 根下解析
       （skills 根 = 装有各 skill 目录的父目录，候选来自 CHINT_SKILLS_ROOT、
       本 skill 的父目录、~/.skills-manager/skills）；
    4) 兜底：从本 skill 目录向上最多 5 层，逐层找 ``chint-brand-design`` 同级目录。

    返回第一个真实存在的文件；全部落空返回 None（调用方按 [WARN] 降级，不判负）。
    """
    candidates: list[pathlib.Path] = []
    raw_override = override or os.environ.get(ENV_SOURCE)
    if raw_override:
        candidates.append(pathlib.Path(raw_override).expanduser())
    raw = (spec.get("source") or {}).get("path") or ""
    if raw:
        p = pathlib.Path(raw).expanduser()
        if p.is_absolute():
            candidates.append(p)
        else:
            roots = []
            env_root = os.environ.get(ENV_SKILLS_ROOT)
            if env_root:
                roots.append(pathlib.Path(env_root).expanduser())
            roots.append(SKILL.parent)
            roots.append(pathlib.Path.home() / ".skills-manager" / "skills")
            for root in roots:
                candidates.append(root / p)
    d = SKILL
    for _ in range(5):
        candidates.append(d.parent / "chint-brand-design" / "scripts" / "chint_theme.py")
        d = d.parent
    for c in candidates:
        if c.is_file():
            return c
    return None


def brand_namespace(src_path: pathlib.Path) -> dict:
    """用 ast 解析品牌源并求值，得到其全局命名空间（不含导入副作用之外的内容）。

    不直接 import 该模块，避免引入它的文件/字体/网络依赖；用 compile+exec 取命名空间。
    """
    tree = ast.parse(src_path.read_text(encoding="utf-8"))
    code = compile(tree, str(src_path), "exec")
    ns: dict = {"__file__": str(src_path)}  # 品牌源用到 __file__，须在命名空间内
    exec(code, ns)  # noqa: S102（受信的本地品牌源，非外部输入）
    return ns


def brand_value_for(key: str, ns: dict) -> str:
    """取出映射键对应的品牌 token 数值（大写 hex；font 返回原字符串）。"""
    colors = ns["CHINT_COLORS"]
    matrix = ns["CHINT_2026_MATRIX"]
    fonts = ns["CHINT_FONTS"]

    def up(h):
        return h.lstrip("#").upper() if isinstance(h, str) else h

    table = {
        "font": fonts["cjk_family"],
        "blue": up(colors["primary"]),
        "navy": up(matrix["primary_blues"][0]["hex"]),
        "cyan": up(colors["primary_light"]),
        "ice": up(matrix["primary_blues"][6]["hex"]),
        "white": up(colors["surface"]),
        "muted": up(colors["text_muted"]),
        "light_bg": up(colors["bg_subtle"]),
        "card_border": up(colors["border"]),
    }
    return table[key]


def engine_has_hardcoded_tokens(engine_path: pathlib.Path) -> list:
    """守卫：引擎源码是否仍硬编码了这 9 个色值的表副本。

    返回命中的具体问题列表（空 = 通过）。
    """
    text = engine_path.read_text(encoding="utf-8")
    problems = []

    # (a) 不应再存在 `DEFAULTS = {...}` 这类命名颜色表
    try:
        tree = ast.parse(text)
    except SyntaxError as exc:
        return [f"引擎源码语法错误，无法解析: {exc}"]
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id == "DEFAULTS":
                    problems.append("引擎仍存在 DEFAULTS 硬编码颜色表（应改为读取快照）")

    # (b) 这 8 个品牌 hex 不应再以字面量出现在引擎源码
    for hx in GUARDED_HEXES:
        if re.search(r'["\']' + hx + r'["\']', text, re.IGNORECASE):
            problems.append(f"引擎源码仍硬编码品牌色值字面量: {hx}")
    # font 的中文字体名也不应再作为值字面量出现（检查孤立的 正泰拓新体 赋值场景）
    if re.search(r'["\']正泰拓新体["\']', text):
        problems.append("引擎源码仍硬编码字体名字面量: 正泰拓新体")

    return problems


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="chint-pptx 品牌 token 快照校验")
    ap.add_argument("--source", help="品牌真源 chint_theme.py 路径（缺省按环境变量/快照/自动发现定位）")
    ap.add_argument("--json", dest="json_out", help="把结果写成 JSON")
    args = ap.parse_args(argv)
    if args.json_out:
        try:
            args.json_out = str(ensure_output_path(args.json_out))
        except ValueError as exc:
            ap.error(str(exc))

    if not SPEC.exists():
        print(f"[FAIL] 缺少快照: {SPEC}")
        return 2
    try:
        spec = json.loads(SPEC.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"[FAIL] 快照不是合法 JSON: {exc}")
        return 2

    src = resolve_brand_source(spec, args.source)
    theme = spec.get("theme", {})
    mapping = spec.get("mapping", {})
    report = {"schema": "chint-brand-token-check/1", "snapshot": str(SPEC),
              "source": str(src) if src else
                        f"<unresolved> spec.path={ (spec.get('source') or {}).get('path', '') }",
              "source_changed": None,
              "drift": [], "pending": [], "engine_hardcoded": []}

    # ---- 1. 快照是否过期 ------------------------------------------------- #
    if src is None:
        report["source_changed"] = "missing"
        print(f"[WARN] 品牌真源未能定位（已尝试 --source / {ENV_SOURCE} / "
              f"快照 source.path / skills 根自动发现）。快照仍可用于离线校验引擎。")
    else:
        got = sha256_file(src)
        want = spec["source"]["sha256"]
        report["source_sha256"] = got
        report["source_changed"] = (got != want)
        if got != want:
            print(f"[WARN] 品牌 token 已变，快照过期：")
            print(f"       快照记录 {want[:12]}…  实际 {got[:12]}…")
            print(f"       重新抓取后再改引擎；否则引擎对齐到的是一个旧品牌版本。")
        else:
            print(f"[ OK ] 品牌 token 未变（sha256 {got[:12]}…）")

    # ---- 2. 快照 theme 与品牌真值逐键比对 ---------------------------------- #
    ns = brand_namespace(src) if src is not None else None
    if ns is None:
        print(f"\n[WARN] 品牌源不可用，跳过 theme↔品牌真值比对（仅做了过期检查）")
    else:
        print(f"\n[INFO] 逐键比对快照 theme 与品牌真值（ast 解析源）：")
        for key in sorted(mapping):
            if key not in theme:
                print(f"       {key:<12} [FAIL] 快照 theme 缺键")
                report["drift"].append({"key": key, "snapshot": None,
                                        "brand": brand_value_for(key, ns),
                                        "aligned": mapping[key].get("aligned")})
                continue
            brand_val = brand_value_for(key, ns)
            snap_val = theme[key]
            aligned = (mapping.get(key) or {}).get("aligned")
            mark = "OK " if brand_val == str(snap_val).upper() else "FAIL"
            print(f"       {key:<12} 快照 {str(snap_val):<10} 品牌 {brand_val:<10} "
                  f"[{'对齐' if aligned else '待办'}] {mark}")
            if brand_val != str(snap_val).upper():
                entry = {"key": key, "snapshot": snap_val, "brand": brand_val,
                         "aligned": aligned}
                if aligned is True:
                    report["drift"].append(entry)
                else:
                    report["pending"].append(entry)

    # ---- 3. 引擎硬编码表副本守卫 ----------------------------------------- #
    if not ENGINE.exists():
        print(f"\n[WARN] 引擎不存在: {ENGINE}（跳过硬编码守卫）")
    else:
        problems = engine_has_hardcoded_tokens(ENGINE)
        report["engine_hardcoded"] = problems
        if problems:
            print(f"\n[FAIL] 引擎仍硬编码品牌色值（{len(problems)} 处）：")
            for p in problems:
                print(f"       - {p}")
        else:
            print(f"\n[ OK ] 引擎无硬编码颜色表副本（已改为读取快照）")

    # ---- 汇总 ----------------------------------------------------------- #
    if report["pending"]:
        print(f"\n[INFO] 已登记的对齐待办 {len(report['pending'])} 项（aligned=false，不判负）：")
        for e in report["pending"]:
            print(f"       {e['key']:<12} 快照 {e['snapshot']}  →  品牌 {e['brand']}")

    failed = bool(report["drift"]) or bool(report["engine_hardcoded"])
    if report["drift"]:
        print(f"\n[FAIL] 未登记的漂移 {len(report['drift'])} 项（aligned=true 却与品牌不符）：")
        for e in report["drift"]:
            print(f"       {e['key']:<12} 快照 {e['snapshot']}  !=  品牌 {e['brand']}")
    if not failed and not report["pending"]:
        print(f"\n[ OK ] 全部 {len(theme)} 个键与品牌真值一致，引擎无硬编码副本")

    if args.json_out:
        out = pathlib.Path(args.json_out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"\n报告: {out}")

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
