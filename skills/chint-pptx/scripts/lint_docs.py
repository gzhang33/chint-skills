#!/usr/bin/env python3
"""chint-pptx —— 文档纪律检查：禁用可执行数值

为什么需要它（2026-09-17 决策 Q2 / Q14）：

本 skill 曾经的病根是「同一件事有两套事实」——文档写 `#5A5A5A`、引擎用 `64748B`；
文档写「109 页母版」、实际只有 6 页。靠"手工保持一致"这条纪律从未守住。
所以定下一条硬纪律：**数值只存在于 `spec/brand_tokens.json` 与引擎代码里，
文档（SKILL.md / references）只允许引用键名，不得出现可执行数值。**

本脚本就是这条纪律的执行者。它把文档里的数值当成错误报出来，逼作者改成键名引用。

检查项：
    hex        十六进制色值（`#1E50E6` / `1E50E6`），至少含一位数字以免误伤普通单词
    dimension  pt / 磅 / inch / 英寸 / 双引号英寸
    percent    百分比阈值（如 `30%`）
    lineref    `L123` 形式的行号、`xxx.py:123` 形式的文件行号
    pagenum    `Slide 25` / `第 25 页` 形式的页码（旧文档里曾指向不存在的母版）
    cjkcount   中文量词前的数字（`8 字` / `2 页` / `8 阶`）——几乎总是引擎常量的副本
    encount    英文量词前的数字（`8 characters` / `2 pages` / `6 items`）——同上，
               只治中文量词等于把同一处病根留了一半（实测漏 8 处）
    anchor     `§N` 锚点是否真的落在目标文档里（拆文件后最易悬空，见 check_anchors）

anchor 是唯一的跨文件检查：`references/x.md §3.1` 会去 x.md 的标题里找 `3.1`，
左边没有文档名时才按自指处理。它守的是「凡被点名的引用都必须能被 grep 到」。

豁免机制：
    * 行内加 `lint-docs: allow` 注释即跳过该行（用于示例路径等必要场合）
    * `spec/lint_docs_allow.txt` 每行一个子串，命中该子串的行跳过

退出码：0 = 干净；1 = 有命中；2 = 用法/文件错误。

用法：
    python3 scripts/lint_docs.py                    # 检查 skill 内全部文档
    python3 scripts/lint_docs.py --path references  # 只查某个子目录/文件
    python3 scripts/lint_docs.py --json report.json
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

SKILL = pathlib.Path(__file__).resolve().parent.parent
ALLOW_FILE = SKILL / "spec" / "lint_docs_allow.txt"
sys.path.insert(0, str(SKILL))
from core.output_paths import ensure_output_path

RULES = [
    ("hex", re.compile(r"#[0-9A-Fa-f]{6}\b|\b[0-9A-Fa-f]{6}\b")),
    # 英寸用双引号写法时要求前面不是引号或字母数字：否则会把 `"01"` / `"2026"` 这类
    # 被引号包住的编号误判成尺寸（实测这是本规则唯一的误报来源）。
    ("dimension", re.compile(r"\d+(?:\.\d+)?\s*(?:pt|磅)\b"
                             r"|\d+(?:\.\d+)?\s*(?:inch|英寸)\b"
                             r"|(?<![\"'\w])(?!\d{4}\")\d+(?:\.\d+)?\"")),
    ("percent", re.compile(r"\d+(?:\.\d+)?\s*%")),
    ("lineref", re.compile(r"\bL\d{2,4}\b|\b[\w.\-]+\.(?:py|md|json|ya?ml|pptx|xlsx|tsv|csv|txt):\d+")),
    ("pagenum", re.compile(r"\b[Ss]lides?\s+\d+|\bpage\s+\d+|\b第\s*\d+\s*页")),
    # 中文量词后的数字：`≤ 8 字` / `2 页` / `3 行` / `2 个` / `8 阶`。
    #
    # 为什么必须单开一条（2026-09-17 实测）：这类写法几乎总是引擎常量的**数值副本**
    # （COPY_MAX_NAME / COPY_MAX_TAGLINE / STANDALONE_MAX_PAGES …），也就是本 skill
    # 的病根"同一件事两套事实"。但 `pagenum` 只认 `第 N 页` 与 `Slide N`，`dimension`
    # 只认 pt/英寸/双引号，于是这些副本**全部静默漏过**：一次实测漏掉 16 处，门禁照样
    # 报"未发现可执行数值"。常量一改，文档就悄悄过期，没人会发现。
    #
    # 前缀 `第` 用负向先行排除，避免与 `pagenum` 对 `第 N 页` 重复计数。
    ("cjkcount", re.compile(r"(?<!第)(?<!第 )\d+\s*(?:字|页|行|个|套|阶|档|条|篇|列)")),
    # 英文量词后的数字：`≤ 8 characters` / `2 pages` / `6 items`。
    #
    # 为什么必须再单开一条（2026-09-17 实测）：补上 cjkcount 之后，"0 命中"**仍然是假绿**——
    # 同一批常量副本改用英文写就全部漏过。实测漏掉 8 处，其中 `≤ 8 characters`（SKILL.md:79、
    # :149）是 COPY_MAX_NAME 的副本、`≤ 2 pages`（:50、:66）是 STANDALONE_MAX_PAGES 的副本、
    # `15 pages`（:60）干脆是一段历史读数。中文规则只治中文写法，等于把同一处病根留了一半。
    ("encount", re.compile(r"\d+\s*(?:chars?|characters?|words?|pages?|lines?|items?"
                           r"|steps?|slides?|rows?|columns?)\b", re.I)),
]


# —— anchor（跨文件锚点）用的模式与常量 ——
DOC_REF_RE = re.compile(r"(?:references/[\w.\-]+\.md|SKILL\.md)")
SEC_RE = re.compile(r"§\s*(\d+(?:\.\d+)*)")
HEAD_RE = re.compile(r"^#{1,6}\s+(\d+(?:\.\d+)*)[.\s、]?", re.M)
ANCHOR_WINDOW = 120          # `§N` 向左多少字符内出现的文档名算它的目标


def has_digit(s: str) -> bool:
    return any(c.isdigit() for c in s)


def load_allow() -> list:
    if not ALLOW_FILE.exists():
        return []
    return [ln.strip() for ln in ALLOW_FILE.read_text(encoding="utf-8").splitlines()
            if ln.strip() and not ln.strip().startswith("#")]


def doc_files(root: pathlib.Path, target: str | None) -> list:
    if target:
        p = pathlib.Path(target)
        if not p.is_absolute():
            p = root / p
        if p.is_file():
            return [p]
        root = p
    out = []
    for p in sorted(root.rglob("*.md")):
        s = str(p)
        if "__pycache__" in s:
            continue
        out.append(p)
    return out


def scan_file(path: pathlib.Path, allow: list) -> list:
    hits = []
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if "lint-docs: allow" in line:
            continue
        if any(a in line for a in allow):
            continue
        for name, rx in RULES:
            for m in rx.finditer(line):
                tok = m.group(0)
                if name == "hex" and not has_digit(tok):
                    continue                       # 纯字母的 6 位"像十六进制"的词，放过
                hits.append({"file": str(path), "line": n, "rule": name,
                             "token": tok, "text": line.strip()[:160]})
    return hits


def doc_sections(root: pathlib.Path) -> dict:
    """文档名 -> 该文档标题里出现的编号集合（`## 3.` -> "3"；`### 4.1 …` -> "4.1"）。

    以**真实 skill 目录**为准打底，再用本次扫描到的文件覆盖同名条目。
    原因：仓库级门禁是在临时树里跑本脚本的（只拷了暂存的那几份 .md），
    若只看临时树，未被暂存的被引用文档就会「查无此文件」而误报。
    """
    out = {}
    for base in (SKILL, root):
        if not base.is_dir():
            continue
        for p in base.rglob("*.md"):
            if "__pycache__" in str(p):
                continue
            try:
                text = p.read_text(encoding="utf-8")
            except Exception:
                continue
            out[p.name] = {m.group(1) for m in HEAD_RE.finditer(text)}
    return out


def check_anchors(path: pathlib.Path, sections: dict, allow: list) -> list:
    """检查 `§N` 是否真的落在目标文档的标题里。

    为什么单开一条（2026-09-17 实测）：sop 被拆成「契约 + runbook」之后，SKILL.md 里
    指向 sop 的 `§3.1 / §3.2 / §3.6 / §4.1 / §5.2` 全部悬空（sop 重写后只剩 §0–§8），
    另有 6 处自指 `§3.4`——SKILL.md 从来就没有编号章节。**11 处悬空引用全靠手工才
    查出来**，而「引用能不能 grep 到」本来完全可机器判定。数值纪律与引用纪律是一回事：
    前者治「两套事实」，后者治「指向不存在的地方」。

    归属规则：`§N` 归属于**同一行内它左边最近**的文档名（窗口 ANCHOR_WINDOW 字符），
    这样 `references/x.md §3.6, §5.2` 里的 `§5.2` 正确归给 x.md 而非本文档。
    左边没有文档名 → 按自指处理。
    """
    hits = []
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if "lint-docs: allow" in line or any(a in line for a in allow):
            continue
        refs = [(m.start(), m.group(0)) for m in DOC_REF_RE.finditer(line)]
        for m in SEC_RE.finditer(line):
            sec, pos = m.group(1), m.start()
            tgt, best = path.name, None
            for rpos, rname in refs:
                if rpos < pos and pos - rpos <= ANCHOR_WINDOW and (best is None or rpos > best[0]):
                    best = (rpos, rname)
            if best is not None:
                tgt = best[1].split("/")[-1]
            known = sections.get(tgt)
            if known is None:
                hits.append({"file": str(path), "line": n, "rule": "anchor",
                             "token": "§%s -> %s" % (sec, tgt),
                             "text": "引用的文档不存在：%s（%s）" % (tgt, line.strip()[:120])})
            elif sec not in known:
                hits.append({"file": str(path), "line": n, "rule": "anchor",
                             "token": "§%s -> %s" % (sec, tgt),
                             "text": "%s 中没有 §%s 这一节：%s" % (tgt, sec, line.strip()[:120])})
    return hits


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="chint-pptx 文档纪律检查（禁用可执行数值）")
    ap.add_argument("--root", default=str(SKILL))
    ap.add_argument("--path", help="只查这个文件/子目录（相对 skill 根）")
    ap.add_argument("--json", dest="json_out", help="把结果写成 JSON")
    ap.add_argument("--quiet", action="store_true", help="只打印汇总")
    args = ap.parse_args(argv)
    if args.json_out:
        try:
            args.json_out = str(ensure_output_path(args.json_out))
        except ValueError as exc:
            ap.error(str(exc))

    root = pathlib.Path(args.root).resolve()
    allow = load_allow()
    files = doc_files(root, args.path)

    sections = doc_sections(root)
    all_hits = []
    for f in files:
        all_hits.extend(scan_file(f, allow))
        all_hits.extend(check_anchors(f, sections, allow))

    by_rule: dict = {}
    by_file: dict = {}
    for h in all_hits:
        by_rule[h["rule"]] = by_rule.get(h["rule"], 0) + 1
        by_file[h["file"]] = by_file.get(h["file"], 0) + 1

    print(f"=== 文档纪律检查 · {root} ===")
    print(f"  文档 {len(files)} 份，豁免子串 {len(allow)} 条")
    if not all_hits:
        print("  [ OK ] 未发现可执行数值，亦无悬空锚点")
    else:
        print(f"  命中 {len(all_hits)} 处："
              + "  ".join(f"{k}={v}" for k, v in sorted(by_rule.items())))
        for f, n in sorted(by_file.items(), key=lambda kv: -kv[1]):
            print(f"    {n:>4}  {f.replace(str(root) + '/', '')}")
        if not args.quiet:
            print()
            for h in all_hits:
                rel = h["file"].replace(str(root) + "/", "")
                print(f"  {rel}:{h['line']}  [{h['rule']}]  {h['token']}")
                print(f"      {h['text']}")

    if args.json_out:
        out = pathlib.Path(args.json_out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps({"root": str(root), "files": len(files),
                                   "by_rule": by_rule,
                                   "hits": all_hits}, ensure_ascii=False, indent=2) + "\n",
                       encoding="utf-8")
        print(f"\n报告: {out}")

    return 1 if all_hits else 0


if __name__ == "__main__":
    sys.exit(main())
