#!/usr/bin/env python3
r"""chint-pptx —— 中间产物 scratch 清扫（TTL 过期删除）

回答一个问题：构建过程中散落的中间产物（Change List、语料回归 runs/ 等）
如何不永久驻留？本脚本按 **TTL（默认 7 天）** 删除过期条目。

清扫范围
--------
1. 默认：系统临时目录下的 chint-pptx scratch——
   `<temp>/chint-pptx-scratch/`（引擎 Change List 落点，CHINT_PPTX_SCRATCH
   自定义根时以环境变量值为准）及其下超龄子目录；
2. `--dir PATH`（可重复）：对额外目录做同样的「超龄直接子项」清扫，
   例如语料回归 `corpus/runs/`（官方约定不入库、随时可重算）。

安全纪律
--------
* 只删「直接子项」且修改时间早于 TTL 截止；不递归扫描目录内容做 age 判断。
* 永远跳过 symlink（不 follow、不删除链接本身）。
* 拒绝清扫根目录、盘根（C:\ 等）、系统树、用户主目录等危险目标（POSIX 与 Windows 双平台）。
* 删除用 Python `shutil.rmtree` / `os.remove`（不经过 shell，与 rm shim 无关）。
* `--dry-run` 只列出不删除；退出码：0=完成（含无可清扫项），1=部分条目删除失败，2=参数错误。

用法
----
    python3 scripts/cleanup_scratch.py --dry-run          # 预览
    python3 scripts/cleanup_scratch.py                    # 清扫默认 scratch（7 天）
    python3 scripts/cleanup_scratch.py --days 7 \
        --dir "/path/to/corpus/runs"                      # 附加目录
"""

from __future__ import annotations

import argparse
import os
import pathlib
import shutil
import sys
import tempfile
import time

DEFAULT_DAYS = 7
SCRATCH_DIRNAME = "chint-pptx-scratch"

# 危险路径拒绝清单：禁止把「整棵系统树 / 根 / 主目录本身」当清扫目标。
# 只做相等比对（不做前缀比对）——深路径（如 ~/Documents/.../corpus/runs、
# /tmp/...）不受影响，本脚本本来就只删目标的超龄直接子项。
# POSIX 树 + Windows 系统目录（env 缺省回退）+ 任意盘根（C:\ 等）。
_POSIX_FORBIDDEN = ("/", "/System", "/Library", "/usr", "/etc", "/bin", "/sbin",
                    "/var/root", "/private/etc", "/private/var/root")


def _forbidden_roots() -> tuple[str, ...]:
    roots = list(_POSIX_FORBIDDEN)
    roots.append(str(pathlib.Path.home()))
    if os.name == "nt":
        for env_key, fallback in (("SystemRoot", r"C:\Windows"),
                                  ("ProgramFiles", r"C:\Program Files"),
                                  ("ProgramFiles(x86)", r"C:\Program Files (x86)")):
            roots.append(os.environ.get(env_key) or fallback)
    return tuple(roots)


FORBIDDEN = _forbidden_roots()


def safe_root(path: pathlib.Path) -> bool:
    for v in {str(path), os.path.realpath(path)}:
        drive, tail = os.path.splitdrive(v)
        if drive and tail in ("\\", "/"):
            return False  # 盘根本身（C:\ 等）永远是危险目标
        for f in FORBIDDEN:
            norm = f.rstrip("/\\") or "/"
            if v == norm:
                return False
    return True


def iter_stale(parent: pathlib.Path, cutoff: float):
    """产出 parent 下修改时间早于 cutoff 的直接子项（跳过 symlink）。"""
    try:
        children = list(parent.iterdir())
    except OSError as exc:
        print(f"[WARN] 无法遍历 {parent}: {exc}")
        return
    for child in children:
        if child.is_symlink():
            continue
        try:
            mtime = child.stat().st_mtime
        except OSError as exc:
            print(f"[WARN] 无法 stat {child}: {exc}")
            continue
        if mtime < cutoff:
            yield child


def remove_entry(entry: pathlib.Path) -> bool:
    try:
        if entry.is_dir() and not entry.is_symlink():
            shutil.rmtree(entry)
        else:
            entry.unlink()
        return True
    except OSError as exc:
        print(f"[FAIL] 删除失败 {entry}: {exc}")
        return False


def sweep(parent: pathlib.Path, cutoff: float, dry_run: bool, label: str) -> tuple[int, int]:
    if not parent.is_dir():
        print(f"[SKIP] {label} 不存在: {parent}")
        return 0, 0
    if not safe_root(parent):
        print(f"[FAIL] 拒绝清扫危险路径: {parent}")
        return 0, 0
    removed = failed = 0
    for child in iter_stale(parent, cutoff):
        age_days = (time.time() - child.stat().st_mtime) / 86400
        if dry_run:
            print(f"[DRY] 将删除 {child}（{age_days:.1f} 天前）")
            removed += 1
            continue
        if remove_entry(child):
            print(f"[DEL] {child}（{age_days:.1f} 天前）")
            removed += 1
        else:
            failed += 1
    return removed, failed


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="chint-pptx 中间产物 TTL 清扫")
    ap.add_argument("--days", type=float, default=DEFAULT_DAYS,
                    help=f"TTL 天数（默认 {DEFAULT_DAYS}）")
    ap.add_argument("--dir", action="append", default=[],
                    help="额外清扫目录（可重复）：删除其中超龄直接子项")
    ap.add_argument("--dry-run", action="store_true", help="只列出，不删除")
    args = ap.parse_args(argv)

    if args.days < 0:
        print("[FAIL] --days 不能为负")
        return 2
    cutoff = time.time() - args.days * 86400

    # 1) 默认 scratch：temp 根下的 chint-pptx-scratch 目录本身，或
    #    CHINT_PPTX_SCRATCH 指定的自定义根。清扫其「超龄子项」；
    #    自定义根不存在时回退扫描 temp 根下同前缀散落目录。
    custom_root = os.environ.get("CHINT_PPTX_SCRATCH")
    total_removed = total_failed = 0
    if custom_root:
        n, f = sweep(pathlib.Path(custom_root), cutoff, args.dry_run, "scratch(自定义根)")
        total_removed += n
        total_failed += f
    else:
        temp = pathlib.Path(tempfile.gettempdir())
        default_root = temp / SCRATCH_DIRNAME
        if default_root.is_dir():
            n, f = sweep(default_root, cutoff, args.dry_run, "scratch(默认)")
            total_removed += n
            total_failed += f
        else:
            n, f = sweep_parent_prefixed(temp, cutoff, args.dry_run)
            total_removed += n
            total_failed += f

    # 2) 附加目录
    for d in args.dir:
        n, f = sweep(pathlib.Path(d).expanduser(), cutoff, args.dry_run, f"--dir {d}")
        total_removed += n
        total_failed += f

    action = "将删除" if args.dry_run else "已删除"
    print(f"\n[ OK ] {action} {total_removed} 项，失败 {total_failed} 项"
          f"（TTL {args.days:g} 天）")
    return 1 if total_failed else 0


def sweep_parent_prefixed(temp: pathlib.Path, cutoff: float, dry_run: bool):
    """temp 根下直接以 chint-pptx-scratch 开头的散落条目（旧版布局兼容）。"""
    removed = failed = 0
    for child in iter_stale(temp, cutoff):
        if child.name.startswith(SCRATCH_DIRNAME):
            if dry_run:
                print(f"[DRY] 将删除 {child}")
                removed += 1
                continue
            if remove_entry(child):
                print(f"[DEL] {child}")
                removed += 1
            else:
                failed += 1
    return removed, failed


if __name__ == "__main__":
    sys.exit(main())
