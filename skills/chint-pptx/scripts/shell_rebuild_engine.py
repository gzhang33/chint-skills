#!/usr/bin/env python3
"""chint-pptx **Mode B** engine — preserve source pages, rebuild only the shell.

Mode B treats an uploaded deck as an immutable content plate and replaces only the
shell: cover, table of contents, chapter dividers, closing. Sub-page *bodies*
(tables, cards, photos, colours, layout) are never re-authored; the only permitted
sub-page edits are:

  * the two-line 2026 VI title grid (category line + main title), and
  * the standard three-piece footer (copyright line + rule + page number),

both of which the Mode B SOP classifies as *shell-level* chrome. Anything beyond
that — re-laying-out a page, restyling a table, swapping an archetype — is Mode A
territory and is explicitly out of scope here.

Design rules baked in
---------------------
  * The output is a NEW file. The uploaded source is never modified.
  * Chapter structure is configured, never guessed here; detection and user
    confirmation happen earlier in the SOP (Phase 1).
  * Give-way shifting is minimal and uniform per page: only content that actually
    intersects the title grid moves, and everything below it moves by the same delta.
  * Footer conflicts are resolved by tightening table ROW heights only (no text, no
    data, no graphics); if a page still cannot host a footer, the footer is skipped
    and the reason is reported.
  * The closing page draws the **contact line only**. The 2026 VI closing artwork already
    carries the THANKS wordmark and the copyright line, so a closing title or slogan would
    duplicate on-screen content; validation rejects such copy instead of drawing it.
  * ``docProps/app.xml`` slide count is repaired after saving (python-pptx does not
    maintain it; a stale count is a real, observable metadata defect).
  * The fidelity gate is invoked automatically at the end and its verdict is part of
    this engine's exit status.

Usage
-----
    python3 shell_rebuild_engine.py config.json [--dry-run] [--no-verify]

See ``references/preserve_source_pages_sop.md`` for the config contract and the
end-to-end SOP.
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from copy import deepcopy

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE, MSO_SHAPE_TYPE
from pptx.enum.text import PP_ALIGN
from pptx.util import Emu, Inches, Pt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# skill 根目录（core/ 包所在）也要在 path 上，供 `import core.analyzer` 等解析
_SKILL_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _SKILL_ROOT not in sys.path:
    sys.path.insert(0, _SKILL_ROOT)
from verify_preserve_source import (          # noqa: E402  (sibling module)
    is_bottom_furniture,
    is_footer_like,
    is_full_bleed_background,
    find_source_title,
    find_promoted_heading,
    table_row_heights,
)
# S3 架构（判定与执行分离）：引擎只做编排（orchestrator），测定 / 规划 / 渲染下沉到 core/。
#   analyzer  -> 源稿 → Slide IR（六类形态判定 + 逐页标题 + 外壳语言 + 封面原文）
#   planner   -> IR × spec × config → Change List（纯函数）
#   renderer  -> 只按 Change List 执行（零判断）
# 引擎执行路径不再读取任何形态键（dark/no_shift/skip/remove/promote）：这些事实全部来自 IR。
from core.analyzer import measure_deck, load_spec  # noqa: E402
from core.planner import build_change_list, derive_baseline  # noqa: E402
from core.output_paths import default_output_dir, ensure_output_path  # noqa: E402
from core.common import (
    inn,
    emu,
    rgb,
    canvas_scale,
    looks_like_department,
    looks_like_introduction_suffix,
    appended_cover_suffix,
    text_width_in,
    detect_source_language,
    source_cover_copy,
    EMU,
    DESIGN_W,
    DESIGN_H,
    LANG_ZH,
    LANG_EN,
    LANG_CJK_THRESHOLD,
    _CJK_RE,
    DEPT_NAME_MAX_LEN,
    COVER_TITLE_SUFFIXES,
    shell_font_path,
    resolve_asset_paths,
    SHELL_COPY,
)
from core.renderer import render               # noqa: E402

# 2026 VI reference canvas. Shell-page geometry below is authored in reference inches;
# on a deck whose canvas differs (a legacy 10" x 5.625" 16:9, for instance) every
# length and type size is multiplied by the deck's own ratio so the chrome fits the
# page instead of overflowing it. 1.0 on the reference canvas => unchanged output.

# Effective canvas ratio for the deck being rebuilt. A module-level value rather than a
# parameter because ``is_full_bleed_background`` is called from helpers that never see
# the config; it keeps the engine and the fidelity gate classifying shapes identically.
_SCALE = (1.0, 1.0)


# --------------------------------------------------------------------------- #
# shell language — the shell is authored in the SOURCE deck's own language
# --------------------------------------------------------------------------- #
# House rule: an English source gets an English cover / contents / chapter / closing /
# footer; a Chinese source gets Chinese. Detection reads the source's own body text; a
# ``shell_language`` value in the config overrides it, and the override is always printed
# rather than applied silently.

# Shell copy pack. Two house rules meet here (both 2026-09-16):
#   * the department name is the ONLY thing a deck may name in shell copy, and it is named
#     exactly once — as the cover subtitle. No footer, no closing slogan repeats it.
#   * there is no closing title and no closing slogan to configure. The 2026 VI closing
#     artwork renders the "THANKS" wordmark and the copyright line inside the image itself,
#     so the closing page draws the contact line and nothing else. See build_closing().
# Words that must never be appended to a source cover title. A suffix is not reuse: it
# invents a word the deck's own cover never carried, and it is exactly how two sibling
# decks in one series (one appending `… Introduction`, one not) drifted onto two
# different cover patterns.
# Effective shell language for the deck being rebuilt. Module-level for the same reason as
# _SCALE: shell helpers never see the config, and it must stay consistent between them.
_LANG = LANG_ZH

# A bare department name: no product line, no year, no separator chaining. This is the
# guard the house rule exists for — a source subtitle like
# "万能式断路器产品线 · 产品管理部 2026版" is a product line plus a year stacked onto a
# department name, and reusing it verbatim would print the exact wording the rule forbids
# on a brand-new cover. Reuse still comes first *within* the shape: a source that names a
# different department keeps that department.


# --------------------------------------------------------------------------- #
# measured text width — the copy gate
# --------------------------------------------------------------------------- #
# A character count cannot serve two languages: 正泰拓新体's Latin advances are roughly a
# third of its CJK ones, so "≤ 8 chars" rejects "Installation & Wiring" while waving
# through an equally wide 8-character Chinese string. The hard gate is therefore the
# *measured* width against the tightest place the string is actually rendered; the count
# survives as a warning, because its real subject is one-idea-per-title minimalism.


def name_render_sites(s: float, grid: dict):
    """Every place a chapter name / intro label is rendered, as (label, pt, box width).

    config 给了 ``title_grid`` 就用其画布绝对值；没给则取参考画布值按 ``s`` 缩放
    （与 core/renderer.ref 同一约定），这样非标准画布不必手工标定。
    """
    cat_pt = float(grid.get("category_pt", 10.0 * s))
    box = float(grid.get("box_width", 10.5 * s))
    intro_box = float(grid.get("intro_box_width", box))
    return (
        ("目录胶囊", 18.0 * s, 5.6 * s),
        ("章节页大字", 32.0 * s, 11.33 * s),
        ("分类行", cat_pt, max(box, intro_box)),
    )


def check_name_width(text: str, sites):
    """(ok|None, detail) measured against the tightest site; None = no font metrics."""
    measured = []
    for label, pt, box in sites:
        width = text_width_in(text, pt)
        if width is None:
            return None, "字体度量不可用（fontTools 缺失）"
        measured.append((label, width, box))
    worst = min(measured, key=lambda item: item[2] - item[1])
    ok = all(box - width >= 0.02 for _label, width, box in measured)
    detail = "，".join(f"{label} {width:.2f}\"/{box:.2f}\"" for label, width, box in measured)
    return ok, f"最紧位 {worst[0]}；{detail}"


# NOTE: fit_title_size() / default_footer_text() 已随执行函数搬至 core/renderer.py。


# Copy minimalism (de-AI) limits. Rationale in references/preserve_source_pages_sop.md §4,
# derived from the `humanizer` anti-pattern catalogue (L4 rule-of-three) and
# `chint-pm-copywriter` (no puffery, no vague adjectives).
STANDALONE_MAX_PAGES = 2       # a chapterless group may not exceed this (SOP 3.3)
COPY_MAX_NAME = 8              # characters, Chinese chapter name / intro label
COPY_MAX_NAME_EN_WORDS = 2     # words, English chapter name / intro label
COPY_MAX_TAGLINE = 14          # characters, optional chapter tagline
COPY_BANNED = ("赋能", "极致", "全域", "体系", "矩阵", "一体化", "全方位", "多维度", "抓手", "闭环")

# 2026 VI defaults — overridable through config["theme"]
# 2026 VI 数值 —— 单一真源在 spec/brand_tokens.json。
# 引擎不再自带一份可能过期的颜色副本；启动时读取快照的 theme，
# 路径相对本文件解析，与调用时的 CWD 无关。读不到 / 解析失败 / 缺键
# 一律非零退出，绝不静默回退到内置默认值。
BRAND_TOKENS_KEYS = ("font", "blue", "navy", "cyan", "ice", "white",
                     "muted", "light_bg", "card_border")


def load_brand_tokens() -> dict:
    """从品牌数值快照读取 9 个 VI 键的当前生效值。

    路径相对本引擎文件解析，换目录调用也不会静默取错值。
    快照缺失 / JSON 非法 / 缺必需键 -> 向 stderr 打印期望绝对路径与缺失键名，
    然后 sys.exit(2)。不允许任何形式的静默回退。
    """
    spec_path = pathlib.Path(__file__).resolve().parent.parent / "spec" / "brand_tokens.json"
    if not spec_path.exists():
        print(f"[FAIL] 品牌 token 快照缺失: {spec_path}", file=sys.stderr)
        sys.exit(2)
    try:
        spec = json.loads(spec_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"[FAIL] 品牌 token 快照不是合法 JSON: {spec_path}\n       {exc}",
              file=sys.stderr)
        sys.exit(2)
    theme = spec.get("theme")
    if not isinstance(theme, dict):
        print(f"[FAIL] 品牌 token 快照缺少 theme 表: {spec_path}", file=sys.stderr)
        sys.exit(2)
    missing = [k for k in BRAND_TOKENS_KEYS if k not in theme]
    if missing:
        print(f"[FAIL] 品牌 token 快照 theme 缺少必需键: {', '.join(missing)}\n"
              f"       路径: {spec_path}", file=sys.stderr)
        sys.exit(2)
    return {k: theme[k] for k in BRAND_TOKENS_KEYS}


# --------------------------------------------------------------------------- #
# text helpers
# --------------------------------------------------------------------------- #
def patch_app_metadata(path: str, slide_count: int, notes_count: int, slide_titles=None):
    """Repair docProps/app.xml counters that python-pptx does not maintain.

    ``<Slides>``/``<Notes>`` alone are not enough: the ``HeadingPairs`` /
    ``TitlesOfParts`` pair carries a *slide-title* vector whose length must equal the
    slide count. Left alone it keeps the source deck's length (14 for a 19-page deck),
    which is exactly the kind of stale count this function exists to prevent — visible
    in the file's properties pane even though nothing fails to open.
    """
    import re
    tmp = path + ".tmp"
    with zipfile.ZipFile(path, "r") as src, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as dst:
        for item in src.infolist():
            data = src.read(item.filename)
            if item.filename == "docProps/app.xml":
                text = data.decode("utf-8")
                text = re.sub(r"<Slides>\d+</Slides>", f"<Slides>{slide_count}</Slides>", text)
                text = re.sub(r"<Notes>\d+</Notes>", f"<Notes>{notes_count}</Notes>", text)
                if slide_titles:
                    text = _repair_title_vector(text, list(slide_titles))
                data = text.encode("utf-8")
            dst.writestr(item, data)
    shutil.move(tmp, path)


def strip_comment_metadata(path: str) -> list:
    """Strip PowerPoint collaboration metadata (modern comments) inherited from the source.

    批注元数据不是内容盘的一部分（不渲染、不影响版面），但留在产物里会让
    OpenXML schema 门禁判 FAIL（modernComment 重复 authorid + ``authors.xml`` 的
    ``authorLst`` 根元素无 schema 声明）。清理共四处，缺一不可：

      1. 部件本体：``ppt/comments/*.xml``、``ppt/authors.xml``
      2. ``[Content_Types].xml`` 里对应部件的 Override
      3. 各 ``.rels`` 里指向这些部件的 Relationship
      4. slide XML 内 ``<p:ext>`` 包裹的 ``<p188:commentRel r:id=…/>`` 扩展块
         （引用已删除的 r:id，残留会报 "references non-existent relationship"）

    幂等：对已剥离的文件重跑无副作用。返回留痕列表（每项一段动作描述）。
    """
    import re
    drop_re = re.compile(r"^ppt/(comments/[^/]+|authors\.xml)$")
    actions = []
    drop_parts = set()
    with zipfile.ZipFile(path) as zf:
        drop_parts = {n for n in zf.namelist() if drop_re.match(n)}
    if not drop_parts:
        return actions

    ct_patterns = [re.compile(rb'\s*<Override[^>]*PartName="/' + re.escape(p.encode())
                              + rb'"[^>]*/>') for p in drop_parts]
    basenames = [p.rsplit("/", 1)[-1] for p in drop_parts]
    rel_patterns = [re.compile(rb'\s*<Relationship[^>]*Target="[^"]*'
                               + re.escape(b.encode()) + rb'"[^>]*/>') for b in basenames]
    ext_re = re.compile(rb'<p:ext [^>]*>(?:(?!</p:ext>).)*commentRel(?:(?!</p:ext>).)*</p:ext>', re.S)

    tmp = path + ".tmp"
    with zipfile.ZipFile(path, "r") as src, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as dst:
        for item in src.infolist():
            data = src.read(item.filename)
            if item.filename in drop_parts:
                actions.append(f"移除部件 {item.filename}")
                continue
            if item.filename == "[Content_Types].xml":
                for pat in ct_patterns:
                    data, k = pat.subn(b"", data)
                    if k:
                        actions.append(f"[Content_Types].xml 移除 Override x{k}")
            elif item.filename.endswith(".rels"):
                for pat in rel_patterns:
                    data, k = pat.subn(b"", data)
                    if k:
                        actions.append(f"{item.filename} 移除 Relationship x{k}")
            elif item.filename.startswith("ppt/slides/slide"):
                n0 = data.count(b"commentRel")
                if n0:
                    data = ext_re.sub(b"", data)
                    data = data.replace(b"<p:extLst></p:extLst>", b"").replace(b"<p:extLst/>", b"")
                    actions.append(f"{item.filename} 移除 commentRel 扩展块 x{n0}")
            dst.writestr(item, data)
    shutil.move(tmp, path)
    return actions


def _repair_title_vector(text: str, slide_titles) -> str:
    """Rewrite the 幻灯片标题 group of HeadingPairs / TitlesOfParts to match the deck."""
    import re
    from xml.sax.saxutils import escape, unescape
    pairs = re.search(r"<HeadingPairs>.*?</HeadingPairs>", text, re.S)
    parts = re.search(r"<TitlesOfParts>.*?</TitlesOfParts>", text, re.S)
    if not pairs or not parts:
        return text
    groups = re.findall(r"<vt:lpstr>(.*?)</vt:lpstr>\s*</vt:variant>\s*<vt:variant>\s*"
                        r"<vt:i4>(\d+)</vt:i4>", pairs.group(0))
    try:
        prefix_len = sum(int(n) for name, n in groups if name != "幻灯片标题")
    except ValueError:
        return text
    if not groups or prefix_len <= 0:
        return text
    # TitlesOfParts stores XML-escaped text ("&amp;"); compare on the decoded form or a
    # title containing '&' silently fails to match and is replaced by the default string.
    items = [unescape(x) for x in re.findall(r"<vt:lpstr>(.*?)</vt:lpstr>", parts.group(0))]
    if len(items) <= prefix_len:
        return text
    prefix, old_titles = items[:prefix_len], items[prefix_len:]

    # Slides we did not author (untouched source pages) keep the name PowerPoint
    # recorded for them; anything else — including every newly built shell page, which
    # has no title placeholder — takes the deck's own default string rather than a
    # guess at a localised literal.
    default = max(set(old_titles), key=old_titles.count) if old_titles else ""
    page_names = list(slide_titles)
    kept = [t for t in page_names if t in old_titles and t not in ("", None)]
    new_titles = []
    for name in page_names:
        if name and name in kept:
            new_titles.append(name)
            kept.remove(name)
        else:
            new_titles.append(default)

    new_vec = "".join(f"<vt:lpstr>{escape(t)}</vt:lpstr>" for t in prefix + new_titles)
    text = text.replace(
        parts.group(0),
        f'<TitlesOfParts><vt:vector size="{len(prefix) + len(new_titles)}" '
        f'baseType="lpstr">{new_vec}</vt:vector></TitlesOfParts>')
    new_pairs = re.sub(
        r"(<vt:lpstr>幻灯片标题</vt:lpstr>\s*</vt:variant>\s*<vt:variant>\s*<vt:i4>)\d+(</vt:i4>)",
        rf"\g<1>{len(new_titles)}\g<2>", pairs.group(0))
    if new_pairs != pairs.group(0):
        text = text.replace(pairs.group(0), new_pairs)
    return text


# --------------------------------------------------------------------------- #
# geometry resolution
# --------------------------------------------------------------------------- #
def resolve_shell_language(cfg: dict, prs) -> str:
    """Shell language for this build: the source deck's own, unless configured.

    Prints the verdict either way — an override that changes the language of every shell
    page must never be silent.
    """
    detected, ratio, letters = detect_source_language(prs)
    configured = str(cfg.get("shell_language") or "").strip().lower()
    if configured and configured not in (LANG_ZH, LANG_EN):
        raise ValueError(f"shell_language 取值非法: {configured!r}（仅支持 zh / en）")
    if configured and configured != detected:
        print(f"[语言] 源稿探测为「{detected}」(CJK 占比 {ratio:.1%}，样本 {letters} 字)，"
              f"配置 shell_language 覆盖为「{configured}」")
        return configured
    if configured:
        print(f"[语言] 外壳语言 = {configured}（配置指定，与探测一致；"
              f"CJK 占比 {ratio:.1%}，样本 {letters} 字）")
        return configured
    print(f"[语言] 外壳语言由源稿自动判定为「{detected}」（CJK 占比 {ratio:.1%} / "
          f"阈值 {LANG_CJK_THRESHOLD:.0%}，样本 {letters} 字）")
    return detected


def lint_copy(cfg: dict, problems: list, warnings: list, sites=()):
    """De-AI copy lints for chapter names, intro label and taglines.

    Two rules with two different jobs, deliberately enforced at two different strengths:

    * **measured width** — a hard error. The string would physically collide with other
      chrome, and the measurement uses the real font's advances, so it holds for Chinese
      and English alike.
    * **name length** — a warning. Its subject is one-idea-per-title minimalism, which is
      a judgement call (the SOP chapter-name dictionary already covers the usual cases),
      not a fitting problem; the classic AI title is a three-concept chain
      ("核心技术优势与智能控制"), the house style is one plain idea ("产品亮点").
    """
    def check_name(text: str, where: str):
        if any(sep in text for sep in ("·", "／", "|", "/")):
            problems.append(f"{where}「{text}」用分隔符串联了多个概念 —— 极简规范要求只讲一个意思"
                            f"（例：核心技术优势与智能控制 → 产品亮点）")
        if sites:
            ok, detail = check_name_width(text, sites)
            if ok is False:
                problems.append(f"{where}「{text}」实测渲染宽度超出可用框（{detail}）—— "
                                f"请改名；该门禁按真字体度量计算，与字符数无关")
            elif ok is None:
                warnings.append(f"{where}「{text}」宽度未校验：{detail}")
        is_cjk = any(_CJK_RE.match(char) for char in text)
        # count content words: a bare connector ("&", "-") is punctuation, not a word, or
        # the perfectly minimal "Safety & Reliability" would trip a three-word warning
        words = [w for w in text.split() if any(ch.isalnum() for ch in w)]
        if is_cjk and len(text) > COPY_MAX_NAME:
            warnings.append(f"{where}「{text}」共 {len(text)} 字，偏离极简取向"
                            f"（中文建议 ≤{COPY_MAX_NAME} 字，一个标题只讲一个意思；"
                            f"例：产品概述与规格矩阵 → 产品概览）")
        elif not is_cjk and len(words) > COPY_MAX_NAME_EN_WORDS:
            warnings.append(f"{where}「{text}」共 {len(words)} 个实词，偏离极简取向"
                            f"（英文建议 ≤{COPY_MAX_NAME_EN_WORDS} 词；"
                            f"例：Overview and Specification Matrix → Product Overview）")
        for word in COPY_BANNED:
            if word in text:
                warnings.append(f"{where}「{text}」含堆砌词「{word}」，建议换成具体说法")

    intro = cfg.get("intro", {})
    if intro.get("enabled") and intro.get("label"):
        check_name(intro["label"], "开篇分类标")
    for chapter in cfg.get("chapters", []):
        if chapter.get("name"):
            check_name(chapter["name"], f"章节 {chapter.get('num', '?')} 名称")
        tagline = (chapter.get("tagline") or "").strip()
        if not tagline:
            continue                      # taglines are optional under the minimal style
        if "·" in tagline:
            problems.append(f"章节 {chapter.get('num')} 副标「{tagline}」是三点串联 —— "
                            f"极简规范要求 ≤{COPY_MAX_TAGLINE} 字且不用中点串联，也可直接留空")
        elif len(tagline) > COPY_MAX_TAGLINE:
            warnings.append(f"章节 {chapter.get('num')} 副标「{tagline}」共 {len(tagline)} 字，"
                            f"建议 ≤{COPY_MAX_TAGLINE} 字或留空")


def validate_config(cfg: dict, source_page_count: int):
    problems = []
    if not cfg.get("source"):
        problems.append("配置缺少 source")
    if not cfg.get("chapters"):
        problems.append("配置缺少 chapters（章节结构必须由 Phase 1 确认后写入）")

    seen_pages = []
    for chapter in cfg.get("chapters", []):
        for key in ("num", "name", "pages"):
            if key not in chapter:
                problems.append(f"章节缺少字段 {key}: {chapter}")
        seen_pages.extend(chapter.get("pages", []))
    intro = cfg.get("intro", {})
    if intro.get("enabled"):
        if not intro.get("label"):
            problems.append("intro 启用但缺少 label")
        # The intro mechanism carries a *single* lead page: its label only ever renders as
        # the 7pt category line, it has no divider page and no contents entry, so a group of
        # two or more pages parked there is invisible in the contents — the deck appears to
        # start at chapter 01 while three overview pages sit in front of it. Such a group
        # must be a real chapter. (2026-09-16)
        intro_pages = intro.get("pages", [])
        if len(intro_pages) >= 2:
            problems.append(
                f"intro 开篇机制只允许承载 1 页引导页（本次 {len(intro_pages)} 页: {intro_pages}）。"
                f"≥2 页的内容组会变成「目录里查不到、也没有章节页」的隐形容组 —— "
                f"请在 chapters 里新增一条真正的章节（含章节页与目录条目）")
        seen_pages.extend(intro_pages)

    standalone = cfg.get("standalone_pages", {}) or {}
    standalone_pages = list(standalone.get("pages", []) or [])
    if standalone_pages:
        # A sub-page that belongs to no chapter at all. Permitted only for genuinely
        # backdrop / redundant pages, and only when the config states why: an unlabelled
        # group is otherwise exactly the "invisible group" SOP 3.3 exists to prevent.
        if not (standalone.get("reason") or "").strip():
            problems.append(
                "standalone_pages 必须写明 reason（为何这些页不属于任何章节）："
                "无章页是例外而非常态，缺理由即按配置不全处理")
        if len(standalone_pages) > STANDALONE_MAX_PAGES:
            problems.append(
                "standalone_pages 最多 {} 页（本次 {} 页）。"
                "≥ {} 页的独立内容组请按 SOP 3.3 升格为真正的章节".format(
                    STANDALONE_MAX_PAGES, len(standalone_pages), STANDALONE_MAX_PAGES + 1))
        if standalone_pages != sorted(standalone_pages):
            problems.append("standalone_pages 必须按原稿页序升序: %s" % standalone_pages)
        chapter_pages = [p for ch in cfg.get("chapters", []) for p in ch.get("pages", [])]
        if chapter_pages and max(standalone_pages) > min(chapter_pages):
            problems.append(
                "无章页只允许置于全部章节之前（preamble）：{} "
                "与首章起始页 p{} 冲突".format(standalone_pages, min(chapter_pages)))
        seen_pages.extend(standalone_pages)

    for page in (cfg.get("no_shift_pages", []) or []):
        if page not in seen_pages:
            problems.append(
                f"no_shift_pages 含非内容页 p{page}（未出现在 chapters / intro / standalone_pages 中）")

    promote_pages = [int(p) for p in
                     (cfg.get("title_grid", {}).get("promote_heading_pages") or [])]
    # A page is promoted only when its title slot holds a repeated group label and the real
    # page title is the topmost body line. It must be a content page -- promoting a shell
    # page or a page that is being removed is meaningless -- and never listed twice.
    for page in promote_pages:
        if page not in seen_pages:
            problems.append(
                f"title_grid.promote_heading_pages 含非内容页 p{page}"
                f"（未出现在 chapters / intro / standalone_pages 中）")
    if len(set(promote_pages)) != len(promote_pages):
        problems.append(f"title_grid.promote_heading_pages 有重复页: {promote_pages}")

    for page in (cfg.get("footer", {}).get("skip_pages", []) or []):
        if page not in seen_pages:
            problems.append(
                f"footer.skip_pages 含非内容页 p{page}"
                f"（未出现在 chapters / intro / standalone_pages 中）")

    closing = cfg.get("closing", {})
    for key, label in (("title", "主标题"), ("slogan", "标语")):
        value = (closing.get(key) or "").strip()
        if value:
            problems.append(
                f"尾页不允许再写{label}（closing.{key} =「{value}」）：2026 VI 尾页底图 "
                f"closing_26_bg.jpg 已内含 THANKS 字样与版权行，再叠一层文字即为重复内容。"
                f"尾页只画联系行（closing.contact）")

    duplicates = {page for page in seen_pages if seen_pages.count(page) > 1}
    if duplicates:
        problems.append(f"以下原稿页码被重复引用: {sorted(duplicates)}")
    out_of_range = [page for page in seen_pages if not (1 <= page <= source_page_count)]
    if out_of_range:
        problems.append(f"页码超出原稿范围(1..{source_page_count}): {out_of_range}")

    removed = set(cfg.get("remove_source_pages", []))
    overlap = removed & set(seen_pages)
    if overlap:
        problems.append(f"以下页码同时被引用与移除: {sorted(overlap)}")
    return problems


def load_config(path: str) -> dict:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="chint-pptx Mode B shell rebuild engine")
    ap.add_argument("config", help="Mode B config JSON")
    ap.add_argument("--dry-run", action="store_true", help="validate and report, write nothing")
    ap.add_argument("--no-verify", action="store_true", help="skip the automatic fidelity gate")
    ap.add_argument("--json", dest="json_out", help="write the run report here")
    args = ap.parse_args(argv)

    cfg = load_config(args.config)
    resolve_asset_paths(cfg)   # 令牌展开 + 底图缺失即报错（不静默跳过）
    theme = {**load_brand_tokens(), **cfg.get("theme", {})}

    source_path = cfg["source"]
    if not os.path.exists(source_path):
        print(f"[FAIL] 原稿不存在: {source_path}")
        return 2

    default_stem, _ext = os.path.splitext(source_path)
    default_name = os.path.basename(default_stem) + "_2026VI.pptx"
    try:
        output_candidate = cfg.get("output") or str(default_output_dir() / default_name)
        output_path = str(ensure_output_path(output_candidate))
        if args.json_out:
            args.json_out = str(ensure_output_path(args.json_out))
            if os.path.abspath(args.json_out) in {
                os.path.abspath(output_path), os.path.abspath(source_path)
            }:
                raise ValueError("The JSON report path must be distinct from the source and output decks")
        scratch_root = str(ensure_output_path(
            os.environ.get("CHINT_PPTX_SCRATCH") or os.path.join(
                tempfile.gettempdir(), "chint-pptx-scratch")))
    except ValueError as exc:
        print(f"[FAIL] {exc}")
        return 2
    if os.path.abspath(output_path) == os.path.abspath(source_path):
        print("[FAIL] 输出路径与原稿相同。Mode B 绝不覆盖上传的原稿，请改用另存路径。")
        return 2

    prs = Presentation(source_path)
    source_page_count = len(prs.slides)
    requested_layout = cfg.get("blank_layout", "空白")
    available_layouts = [layout.name for master in prs.slide_masters
                        for layout in master.slide_layouts]
    if requested_layout not in available_layouts:
        print(f"[FAIL] 原稿中找不到版式「{requested_layout}」，无法创建外壳页。可用版式: {available_layouts}")
        return 2

    global _SCALE, _LANG
    _SCALE = canvas_scale(prs)
    scale_f = _SCALE[0]
    try:
        _LANG = resolve_shell_language(cfg, prs)
    except ValueError as exc:
        print(f"[FAIL] {exc}")
        return 2

    name_sites = name_render_sites(scale_f, cfg.get("title_grid", {}))

    problems = validate_config(cfg, source_page_count)
    copy_warnings = []
    lint_copy(cfg, problems, copy_warnings, name_sites)
    if problems:
        print("[FAIL] 配置校验未通过：")
        for problem in problems:
            print("   · " + problem)
        return 2

    # ---- 封面文案：逐字复用源稿，副标只能是源稿原词或本语言部门名 ----
    pack = SHELL_COPY[_LANG]
    cover_cfg = cfg.setdefault("cover", {})
    src_title, src_subtitle = source_cover_copy(prs)
    if src_subtitle and looks_like_department(src_subtitle):
        resolved_sub = src_subtitle
        print(f"[源稿复用] 封面副标逐字复用源稿: \"{resolved_sub}\"")
    else:
        resolved_sub = pack["department"]
        if src_subtitle:
            print(f"[文案规范] 源稿封面副标\"{src_subtitle}\"不符合「只放部门名」的规范形态"
                  f"（不得带产品线、年份或串联符），已按外壳语言改为\"{resolved_sub}\"")
        else:
            print(f"[源稿复用] 源稿封面无副标行，按外壳语言（{_LANG}）回退为\"{resolved_sub}\"")
    configured_sub = (cover_cfg.get("subtitle") or "").strip()
    if configured_sub and configured_sub != resolved_sub:
        print(f"[文案规范] 已忽略封面副标配置值\"{configured_sub}\"—— 副标只能是源稿原词，"
              f"或本语言的部门名\"{pack['department']}\"")
    cover_cfg["subtitle"] = resolved_sub
    configured_title = (cover_cfg.get("title") or "").strip()
    if not configured_title and src_title:
        cover_cfg["title"] = src_title
        print(f"[源稿复用] 封面主标题逐字复用源稿: \"{src_title}\"")
    elif configured_title and src_title and configured_title != src_title:
        copy_warnings.append(f"封面主标题未逐字复用源稿（配置\"{configured_title}\""
                             f"vs 源稿\"{src_title}\"）—— 规范要求逐字复用，"
                             f"除非源稿封面本身不可用")

    tail = appended_cover_suffix(configured_title, src_title)
    if tail and looks_like_introduction_suffix(tail):
        print(f"[FAIL] 封面主标题\"{configured_title}\"= 源稿标题\"{src_title}\"+ 后缀\"{tail}\"。"
              f"规范禁止在源稿标题上追加 Introduction / 产品介绍 / 概述 这类后缀词 —— "
              f"同系列各稿必须共用源稿原句式（本稿应为\"{src_title}\"）。"
              f"如确需改动，先确认源稿封面本身不可用。")
        return 2

    if copy_warnings:
        print("[文案提示] 不影响构建，但建议按极简规范收紧：")
        for w in copy_warnings:
            print("   · " + w)

    # ===== S3 架构：analyzer -> planner -> Change List -> renderer（判定与执行分离）=====
    # 1) 测定：源稿 -> Slide IR（六类形态判定 + 逐页标题 + 外壳语言 + 封面原文）
    spec = load_spec()
    ir, _low = measure_deck(pathlib.Path(source_path), spec,
                            deck_name=pathlib.Path(source_path).stem)

    # 2) 规划：IR x spec x config -> Change List（纯函数，无副作用）
    change_list = build_change_list(ir, spec, cfg)
    # 外壳语言以引擎解析为准（config 可覆盖 IR 的自动判定）
    if change_list.get("shell_language") != _LANG:
        change_list["shell_language"] = _LANG
    if change_list.get("problems"):
        print("[FAIL] 计划校验未通过：")
        for p in change_list["problems"]:
            print("   · " + p)
        return 2

    print("=" * 78)
    print("chint-pptx Mode B 引擎 / shell rebuild engine (orchestrator)")
    print(f"  原稿 source : {source_path}  ({source_page_count} 页)")
    print(f"  输出 output : {output_path}")
    print(f"  外壳语言    : {_LANG}（随源稿语言类型）")
    print(f"  画布 canvas : {inn(prs.slide_width):.3f}\" x {inn(prs.slide_height):.3f}\"  "
          f"-> 外壳页等比系数 {scale_f:.4f}（基准 {DESIGN_W}\" x {DESIGN_H}\"）")
    _implied = [k for k, present in (("title_grid", bool(cfg.get("title_grid"))),
                                     ("footer", bool(cfg.get("footer")))) if not present]
    if abs(scale_f - 1.0) > 1e-6 and _implied:
        # 非标准画布 + config 未给几何：缺省值已按系数缩放（renderer.ref），
        # 但手工标定仍是推荐做法 —— 缩放后的默认位不保证零让位。
        print(f"  [提示] 画布非基准且 config 未声明 {', '.join(_implied)}："
              f"标题/页脚几何取参考画布值 ×{scale_f:.4f} 的缩放默认位；"
              f"如需精确标定（零让位），请在 config 中显式填写画布绝对值。")
    print("=" * 78)

    # 3) 落盘 Change List（人类可读、可 diff、可评审；便于复盘「判错还是改错」）
    #    中间产物不落目标项目：写进系统临时 scratch（CHINT_PPTX_SCRATCH 可覆盖根目录），
    #    由 scripts/cleanup_scratch.py 按 TTL（默认 7 天）清扫。scratch 建不出来时
    #    回退到旧的「output 旁」位置，保证构建不因清扫目录权限而失败。
    changelist_name = os.path.basename(output_path) + ".changelist.json"
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    scratch_dir = os.path.join(scratch_root, f"{pathlib.Path(output_path).stem}-{stamp}")
    changelist_path: str
    try:
        os.makedirs(scratch_dir)
        changelist_path = os.path.join(scratch_dir, changelist_name)
    except OSError as exc:
        changelist_path = output_path + ".changelist.json"
        print(f"[WARN] scratch 目录不可用（{exc}），Change List 回退到 output 旁: {changelist_path}")
    with open(changelist_path, "w", encoding="utf-8") as fh:
        json.dump(change_list, fh, ensure_ascii=False, indent=2)
    print(f"[Change List] 已落盘（中间产物，TTL 清扫）: {changelist_path}")

    # 4) 渲染：只按 Change List 执行（零判断；不再读任何形态键）
    result = render(prs, change_list, cfg, theme, spec, scale_f=scale_f)
    if result is None:
        print("[FAIL] 渲染失败（见上）")
        return 2
    report, footer_skipped = result

    for line in report:
        print("   " + line)

    # ---- 保存 + 元数据修复 ----
    if args.dry_run:
        print("\n[dry-run] 未写出文件。")
        return 0

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    from core.brand import apply_brand
    badge_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                              "assets", "media", "chint_badge.png")
    if not os.path.isfile(badge_path):
        print(f"[FAIL] 正泰徽标缺失: {badge_path}")
        return 2
    apply_brand(prs, badge_path)
    prs.save(output_path)
    notes = 0
    with zipfile.ZipFile(output_path) as zf:
        notes = sum(1 for n in zf.namelist() if n.startswith("ppt/notesSlides/notesSlide"))
    slide_titles = [(e.get("title_text") or "") if e.get("source_page") else ""
                    for e in change_list["plan"]]
    patch_app_metadata(output_path, len(prs.slides), notes, slide_titles)
    strip_actions = strip_comment_metadata(output_path)
    print(f"\n=== 已生成: {output_path} （{len(prs.slides)} 页；docProps/app.xml 计数已校正为 "
          f"{len(prs.slides)} 页 / {notes} 备注 / 标题向量 {len(slide_titles)} 条）===")
    if strip_actions:
        print("  包卫生（批注元数据剥离，非内容盘）:")
        for a in strip_actions:
            print("   - " + a)
    if footer_skipped:
        print(f"页脚被跳过的页: {footer_skipped}（原因见上，按策略优先不动原内容）")

    # ---- 内建保真度门禁（分支不变）----
    verdict = None
    if not args.no_verify:
        baseline = derive_baseline(change_list)
        baseline_path = output_path + ".baseline.json"
        with open(baseline_path, "w", encoding="utf-8") as fh:
            json.dump(baseline, fh, ensure_ascii=False, indent=2)
        gate = os.path.join(os.path.dirname(os.path.abspath(__file__)), "verify_preserve_source.py")
        print("\n=== 自动保真度门禁 ===")
        proc = subprocess.run([sys.executable, gate, "--source", source_path,
                               "--target", output_path, "--baseline", baseline_path,
                               # 与 renderer.ref 同约定：缺省值按画布比例缩放，
                               # 否则非标准画布上门禁底带阈值会落在画布之外。
                               "--bottom-limit", str(cfg.get("footer", {})
                                                     .get("bottom_limit", 7.30 * scale_f))],
                              capture_output=True, text=True)
        tail_lines = [l for l in proc.stdout.splitlines() if l.startswith(("[", "  FAIL"))]
        for line in tail_lines[-12:]:
            print("   " + line)
        verdict = "PASS" if proc.returncode == 0 else "FAIL"
        print(f"   门禁结论: {verdict}")

    if args.json_out:
        with open(args.json_out, "w", encoding="utf-8") as fh:
            json.dump({
                "source": source_path, "output": output_path,
                "pages": len(prs.slides), "chapters": [c["num"] for c in cfg.get("chapters", [])],
                "shell_language": _LANG,
                "cover": {"title": cover_cfg.get("title", ""),
                          "subtitle": cover_cfg.get("subtitle", ""),
                          "source_title": src_title, "source_subtitle": src_subtitle},
                "intro_pages": (cfg.get("intro", {}) or {}).get("pages", []) if (cfg.get("intro", {}) or {}).get("enabled") else [],
                "standalone_pages": list((cfg.get("standalone_pages", {}) or {}).get("pages", []) or []),
                "removed_pages": change_list["removed_pages"],
                "footer_skipped_pages": footer_skipped,
                "fidelity_gate": verdict, "report": report,
            }, fh, ensure_ascii=False, indent=2)

    if verdict == "FAIL":
        print("\n[FAIL] 保真度门禁未通过 —— 子页已被改动，请检查配置后重跑。")
        return 1
    print("\n[OK] Mode B 重建完成。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
