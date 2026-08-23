#!/usr/bin/env python3
"""feishu_drive_sync.py — 本地目录 ↔ 飞书云盘 双向增量同步（基于 lark-cli）

封装 `lark-cli drive` 实现双向镜像同步，附加：
  - 每个文件的上传 / 下载状态日志（成功 / 失败 / 跳过 / 冲突）
  - 增量模式：仅同步新增或修改的文件（基于基线状态文件做变更 / 冲突检测）
  - 冲突处理：本地与远端同时修改同一文件时，保留本地版本、另存远端版本为
    `<name>.conflict-remote-<时间戳><ext>`，绝不静默丢弃任何一侧数据
  - 目标文件夹自动创建
  - 排除规则（工具 / 缓存 / 临时 / 仓库内部 / 运行时产物）
  - 预览模式（--dry-run 同时展示两个方向的计划）

同步模型（基线守护型双向同步）
------------------------------
维护一个基线状态文件 `.feishu_drive_sync_state.json`，记录每个已同步文件在上次
同步时的「本地 mtime+size」与「远端 modified_time+size+token」。每次运行：

  PULL 阶段（远端 → 本地，先于 PUSH，确保冲突可被保全）：
    - 仅远端有 → 下载到本地（新建）
    - 两端都有，仅远端变更 → 下载覆盖本地
    - 两端都有，仅本地变更 → 跳过（交给 PUSH 上传）
    - 两端都有，两侧都变更 → 冲突：另存远端副本到本地，不覆盖本地
    - 两端都有，都未变更 → 跳过

  PUSH 阶段（本地 → 远端，复用 +push --if-exists smart）：
    - 仅本地有 → 上传
    - 仅远端有（已被 PULL 下载） → 跳过
    - 本地已变更 → 覆盖远端
    - PULL 阶段已保全的冲突：本地仍为本地版本，PUSH 将其覆盖到远端（本地胜出）

  PULL 先于 PUSH 是关键：若先 PUSH 会把远端编辑覆盖掉，冲突便无法保全。

删除传播：默认不传播（安全优先）。如需本地删除同步到远端，加 --sync-deletes。

依赖：lark-cli（已配置 auth，需 drive:drive / space:document:retrieve / drive:file:download 等 scope）
状态文件与日志会被自动排除，不会进入同步范围。
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime
from pathlib import Path

# ── 常量 ──────────────────────────────────────────────
LARK_CLI_BIN = None          # 首次调用时探查
# 排除：仓库内部 / 工具 / 缓存 / 临时 / 运行时产物
EXCLUDE_DEFAULT = [
    ".git", ".venv", ".zcode", ".DS_Store", "__pycache__", "*.pyc",
    ".playwright-mcp", "~$*", "*.bak*",
    ".feishu_drive_sync_state.json", "feishu_drive_sync.log",
]
STATE_FILE = ".feishu_drive_sync_state.json"


# ── 工具函数 ──────────────────────────────────────────

def find_lark_cli():
    """定位 lark-cli 可执行文件路径"""
    p = shutil.which("lark-cli")
    if p:
        return p
    candidates = [
        os.path.expanduser("~/.workbuddy/binaries/node/cli-connector-packages/bin/lark-cli"),
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    raise SystemExit("错误：未找到 lark-cli 可执行文件。请确认已安装飞书 CLI。")


def run_lark(args: list[str], *, cwd: str | None = None, timeout=3600) -> tuple[int, str, str]:
    """运行 `lark-cli drive <...>` 并返回 (exit_code, stdout, stderr)"""
    global LARK_CLI_BIN
    if LARK_CLI_BIN is None:
        LARK_CLI_BIN = find_lark_cli()
    cmd = [LARK_CLI_BIN, "drive"] + args
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=cwd)
    except subprocess.TimeoutExpired:
        return -1, "", "timout"
    clean_stdout = _strip_ansi(r.stdout)
    clean_stderr = _strip_ansi(r.stderr)
    return r.returncode, clean_stdout, clean_stderr


def _strip_ansi(text: str) -> str:
    import re
    return re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', text)


def extract_json(text: str) -> dict | None:
    """从文本中提取第一个 {…} JSON 对象（忽略前置进度行和 ANSI）"""
    start = text.find("{")
    if start == -1:
        return None
    end = text.rfind("}")
    if end == -1 or end < start:
        return None
    try:
        return json.loads(text[start:end + 1])
    except json.JSONDecodeError:
        return None


def _match_exclude(rel_path: str, excludes: list[str]) -> bool:
    """检查 rel_path 是否匹配任一排除模式（fnmatch）"""
    import fnmatch
    rel_path = rel_path.replace(os.sep, "/")
    for pat in excludes:
        if fnmatch.fnmatch(rel_path, pat):
            return True
        parts = rel_path.split("/")
        for part in parts:
            if fnmatch.fnmatch(part, pat):
                return True
    return False


# ── 本地 / 远端集合构建 ───────────────────────────────

def build_local_set(local_dir: str, excludes: list[str]) -> dict[str, tuple[float, int]]:
    """遍历本地目录，返回 {相对路径: (mtime, size)}（已排除 + 剪枝排除目录）"""
    result: dict[str, tuple[float, int]] = {}
    for root, dirs, files in os.walk(local_dir):
        rel = os.path.relpath(root, local_dir)
        dirs[:] = [d for d in dirs
                   if not _match_exclude(os.path.join(rel, d) if rel != "." else d, excludes)]
        for f in files:
            rp = os.path.join(rel, f) if rel != "." else f
            rp = rp.replace(os.sep, "/")
            if _match_exclude(rp, excludes):
                continue
            p = os.path.join(local_dir, rp)
            try:
                st = os.stat(p)
                result[rp] = (st.st_mtime, st.st_size)
            except OSError:
                continue
    return result


def list_remote_recursive(folder_token: str, excludes: list[str],
                           prefix: str = "") -> dict[str, dict]:
    """递归列出远端目录树，返回 {相对路径: {token, modified_time(int), size(int)}}

    注意：files list 的条目不含 size 字段（仅 modified_time），size 记为 0。
    """
    result: dict[str, dict] = {}
    rc, out, err = run_lark([
        "files", "list",
        "--params", json.dumps({"folder_token": folder_token}),
        "--format", "json",
    ])
    obj = extract_json(out)
    if not obj or not obj.get("ok"):
        msg = (obj or {}).get("error", {}).get("message", err) if obj else err
        print(f"[警告] 列出远端目录失败（{folder_token}）：{msg}")
        return result
    items = obj.get("data", {}).get("files", [])
    for it in items:
        name = it.get("name", "")
        rel = (prefix + "/" + name).lstrip("/")
        if _match_exclude(rel, excludes):
            continue
        if it.get("type") == "folder":
            result.update(list_remote_recursive(it["token"], excludes, rel))
        else:
            result[rel] = {
                "token": it.get("token", ""),
                "modified_time": int(it.get("modified_time", 0) or 0),
                "size": int(it.get("size", 0) or 0),
            }
    return result


# ── 基线状态文件 ──────────────────────────────────────

def load_state(local_dir: str) -> dict:
    """读取基线状态文件，不存在则返回空 dict"""
    path = os.path.join(local_dir, STATE_FILE)
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def save_state(local_dir: str, state: dict):
    """写回基线状态文件"""
    path = os.path.join(local_dir, STATE_FILE)
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
    except OSError as e:
        print(f"[警告] 保存状态文件失败：{e}")


def rebuild_state(local_set: dict, remote_set: dict) -> dict:
    """根据运行后的本地 / 远端集合重建基线状态"""
    state: dict = {}
    for path, (mt, sz) in local_set.items():
        r = remote_set.get(path)
        state[path] = {
            "local_mtime": mt,
            "local_size": sz,
            "remote_mtime": r["modified_time"] if r else None,
            "remote_size": r["size"] if r else None,
            "remote_token": r["token"] if r else None,
        }
    for path, r in remote_set.items():
        if path not in state:
            state[path] = {
                "local_mtime": None,
                "local_size": None,
                "remote_mtime": r["modified_time"],
                "remote_size": r["size"],
                "remote_token": r["token"],
            }
    return state


# ── 下载（PULL）──────────────────────────────────────

def download_file(token: str, rel_path: str, local_dir: str, overwrite: bool) -> tuple[bool, str]:
    """下载单个远端文件到本地（rel_path 相对于 local_dir）。返回 (成功, 错误信息)"""
    local_path = os.path.join(local_dir, rel_path)
    parent = os.path.dirname(local_path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    args = ["+download", "--file-token", token, "--output", rel_path]
    if overwrite:
        args.append("--overwrite")
    rc, out, err = run_lark(args, cwd=local_dir)
    obj = extract_json(out)
    if obj and obj.get("ok"):
        return True, ""
    return False, (obj.get("error", {}).get("message", err) if obj else err)


def pull_phase(local_dir: str, local_set: dict, remote_set: dict,
               prev_state: dict, verbose: bool) -> dict:
    """PULL 阶段：远端 → 本地。返回结果聚合 dict。"""
    downloaded, conflicts, skipped, failed = [], [], [], []
    items = []
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    for path in sorted(remote_set.keys()):
        r = remote_set[path]
        if path in local_set:
            lmt, lsz = local_set[path]
            p = prev_state.get(path)
            if p is None:
                # 无基线（首次出现）：假定两端已一致，跳过，不误报冲突
                skipped.append(path)
                items.append({"action": "pull_skipped", "rel_path": path})
                continue
            local_changed = p.get("local_mtime") != lmt or p.get("local_size") != lsz
            remote_changed = p.get("remote_mtime") != r["modified_time"]
            if remote_changed and local_changed:
                # 冲突：另存远端副本，保留本地版本
                stem, ext = os.path.splitext(path)
                conflict_rel = f"{stem}.conflict-remote-{ts}{ext}".replace(os.sep, "/")
                ok, err = download_file(r["token"], conflict_rel, local_dir, overwrite=False)
                if ok:
                    conflicts.append(conflict_rel)
                    items.append({"action": "conflict", "rel_path": conflict_rel, "src": path})
                else:
                    failed.append((path, err))
                    items.append({"action": "pull_failed", "rel_path": path, "error": err})
            elif remote_changed:
                ok, err = download_file(r["token"], path, local_dir, overwrite=True)
                if ok:
                    downloaded.append(path)
                    items.append({"action": "downloaded", "rel_path": path})
                else:
                    failed.append((path, err))
                    items.append({"action": "pull_failed", "rel_path": path, "error": err})
            else:
                skipped.append(path)
                items.append({"action": "pull_skipped", "rel_path": path})
        else:
            # 仅远端有 → 下载（新建）
            ok, err = download_file(r["token"], path, local_dir, overwrite=False)
            if ok:
                downloaded.append(path)
                items.append({"action": "downloaded", "rel_path": path})
            else:
                failed.append((path, err))
                items.append({"action": "pull_failed", "rel_path": path, "error": err})
    return {
        "downloaded": downloaded, "conflicts": conflicts,
        "skipped": skipped, "failed": failed, "items": items,
    }


# ── 暂存目录（PUSH 排除）─────────────────────────────

def build_staging(src: str, excludes: list[str]) -> str | None:
    """构建排除指定模式的硬链接暂存目录；返回暂存目录路径，若无排除则返回 None"""
    if not excludes:
        return None
    src = os.path.abspath(src)
    stage = tempfile.mkdtemp(prefix="feishu_sync_")
    for root, dirs, files in os.walk(src):
        rel = os.path.relpath(root, src)
        dirs[:] = [d for d in dirs if not _match_exclude(os.path.join(rel, d) if rel != "." else d, excludes)]
        for fname in files:
            rel_path = os.path.join(rel, fname) if rel != "." else fname
            rel_path = rel_path.replace(os.sep, "/")
            if _match_exclude(rel_path, excludes):
                continue
            src_file = os.path.join(root, fname)
            dst_dir = os.path.dirname(os.path.join(stage, rel_path))
            os.makedirs(dst_dir, exist_ok=True)
            dst_file = os.path.join(stage, rel_path)
            try:
                os.link(src_file, dst_file)
            except OSError:
                shutil.copy2(src_file, dst_file)
    return stage


# ── 核心操作 ──────────────────────────────────────────

def create_target_folder(name: str, parent_token: str | None, as_identity: str | None) -> str:
    """在飞书云盘创建目标文件夹，返回 folder_token"""
    args = ["+create-folder", "--name", name, "--format", "json"]
    if parent_token:
        args.extend(["--folder-token", parent_token])
    if as_identity:
        args.extend(["--as", as_identity])
    rc, out, err = run_lark(args)
    obj = extract_json(out)
    if not obj or not obj.get("ok"):
        msg = f"创建文件夹 '{name}' 失败"
        if obj and "error" in obj:
            msg += f"：{obj['error'].get('message', '')}"
        raise SystemExit(msg)
    token = (obj.get("data") or {}).get("folder_token", "")
    if not token:
        raise SystemExit(f"创建文件夹 '{name}' 成功但无法获取 token")
    print(f"[创建文件夹] {name} → token={token}")
    return token


def run_push(local_rel: str, folder_token: str, if_exists: str,
             as_identity: str | None, dup_remote: str | None,
             dry_run: bool, cwd: str) -> dict | None:
    """执行 `lark-cli drive +push`，返回解析后的 data dict 或 None"""
    args = ["+push"]
    if dry_run:
        args.append("--dry-run")
    args.extend(["--local-dir", local_rel,
                 "--folder-token", folder_token,
                 "--if-exists", if_exists,
                 "--format", "json"])
    if as_identity:
        args.extend(["--as", as_identity])
    if dup_remote:
        args.extend(["--on-duplicate-remote", dup_remote])

    rc, out, err = run_lark(args, cwd=cwd)
    obj = extract_json(out)

    if not obj:
        print(f"[错误] 无法解析 push 输出\nstdout:\n{out}\nstderr:\n{err}")
        sys.exit(3)

    if not obj.get("ok") and "error" in obj:
        err_info = obj["error"]
        if err_info.get("subtype") == "missing_scope":
            scopes = err_info.get("missing_scopes", [])
            hint = err_info.get("hint", "")
            print(f"[授权错误] 缺少 scope：{' '.join(scopes)}")
            if hint:
                print(f"  修复：{hint}")
            sys.exit(4)
        if dry_run:
            print(f"[预览错误] {err_info.get('message', '')}")
            return None
        print(f"[推送错误] {err_info.get('message', '')}")
        sys.exit(3 if rc != 0 else 0)

    data = obj.get("data") or {}
    if not data and not dry_run:
        print(f"[警告] push 返回无 data：{json.dumps(obj, ensure_ascii=False)}")

    if rc != 0 and not dry_run:
        summary = data.get("summary", {})
        if summary.get("failed", 0) > 0:
            print(f"[部分失败] 退出码={rc}，需查看日志中的失败项")
    return data


# ── 日志与展示 ────────────────────────────────────────

ACTION_LABELS = {
    "uploaded":        ("上传(新增)", "UPLOADED"),
    "overwritten":     ("覆盖更新",   "OVERWRITTEN"),
    "skipped":         ("跳过",       "SKIPPED"),
    "failed":          ("失败",       "FAILED"),
    "folder_created":  ("目录",       "FOLDER"),
    "downloaded":      ("下载",       "DOWNLOADED"),
    "conflict":        ("冲突保全",   "CONFLICT"),
    "pull_skipped":    ("跳过",       "PULL_SKIPPED"),
    "pull_failed":     ("下载失败",   "PULL_FAILED"),
}


def _log_line(item: dict) -> str:
    action = item.get("action", "?")
    label, _ = ACTION_LABELS.get(action, ("未知", "?"))
    rel_path = item.get("rel_path", "?")
    extra = item.get("src", "")
    error = item.get("error", "")
    parts = [label, rel_path]
    if extra:
        parts.append(f"src={extra}")
    if error:
        parts.append(error)
    return "\t".join(parts)


def print_per_file_items(items: list[dict], log_path: str | None, verbose: bool):
    """打印 per-file 状态 + 写入日志文件"""
    lines = []
    groups = {code: [] for code in ACTION_LABELS}
    for it in items:
        action = it.get("action", "?")
        _, code = ACTION_LABELS.get(action, ("未知", "?"))
        lines.append(_log_line(it))
        if code in groups:
            groups[code].append(it)

    if log_path:
        dir_name = os.path.dirname(log_path)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)
        with open(log_path, "w", encoding="utf-8") as f:
            f.write(f"# 飞书云盘双向同步日志 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"# 格式: 状态\\t相对路径\\t[src=冲突来源]\\t[错误信息]\n\n")
            for line in lines:
                f.write(line + "\n")
        print(f"[日志] 详细记录已写入 {log_path}")

    group_labels = [
        ("FAILED", "❌ 上传失败"),
        ("PULL_FAILED", "❌ 下载失败"),
        ("CONFLICT", "⚠️  冲突保全（远端副本另存本地）"),
        ("FOLDER", "📁 远端新建目录"),
        ("UPLOADED", "  ✅ 上传成功（新增）"),
        ("OVERWRITTEN", " 🔄 覆盖更新（上传）"),
        ("DOWNLOADED", "  ⬇️  下载成功（远端→本地）"),
        ("SKIPPED", " ⏭️  跳过（未变更）"),
        ("PULL_SKIPPED", " ⏭️  跳过（未变更）"),
    ]
    for code, title in group_labels:
        its = groups.get(code, [])
        if not its:
            continue
        print(f"\n{title} ({len(its)}):")
        if verbose:
            for it in its:
                rp = it.get("rel_path", "?")
                src = it.get("src", "")
                err = it.get("error", "")
                detail = f"    {rp}"
                if src:
                    detail += f"  (远端来源: {src})"
                if err:
                    detail += f"  error={err}"
                print(detail)
        else:
            for it in its[:3]:
                print(f"    {it.get('rel_path', '?')}")
            if len(its) > 3:
                print(f"    ... 还有 {len(its) - 3} 个")


def print_plan(pull_plan: dict, push_plan: dict | None):
    """打印双向预览计划"""
    print(f"\n[预览] PULL 计划（远端 → 本地）：")
    print(f"  下载(新增/远端变更): {len(pull_plan.get('downloaded', []))}")
    print(f"  冲突保全:           {len(pull_plan.get('conflicts', []))}")
    print(f"  跳过(未变更):       {len(pull_plan.get('skipped', []))}")
    print(f"  失败:               {len(pull_plan.get('failed', []))}")
    if pull_plan.get("downloaded"):
        print(f"  将下载:")
        for p in pull_plan["downloaded"][:8]:
            print(f"    ⬇️  {p}")
        if len(pull_plan["downloaded"]) > 8:
            print(f"    ... 还有 {len(pull_plan['downloaded']) - 8} 个")
    if pull_plan.get("conflicts"):
        print(f"  将保全冲突:")
        for p in pull_plan["conflicts"]:
            print(f"    ⚠️  {p}")

    if push_plan:
        summary = push_plan.get("summary", {})
        items = push_plan.get("items", [])
        actions = {}
        for it in items:
            a = it.get("action", "?")
            actions[a] = actions.get(a, 0) + 1
        print(f"\n[预览] PUSH 计划（本地 → 远端）：")
        for a, cnt in sorted(actions.items()):
            label, _ = ACTION_LABELS.get(a, (a, ""))
            print(f"  {cnt:4d}  {label}")
        print(f"  合计: {len(items)} 项")


# ── 主流程 ────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="本地目录 ↔ 飞书云盘 双向增量同步（基于 lark-cli drive）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 1. 双向同步（默认）：先拉取远端变更，再推送本地变更
  python feishu_drive_sync.py --local-dir . --folder-token fldXXXXXXXXX

  # 2. 首次创建目标文件夹后双向同步
  python feishu_drive_sync.py --local-dir . --create-folder chint

  # 3. 仅预览（不执行）
  python feishu_drive_sync.py --local-dir . --folder-token fldXXXXX --dry-run

  # 4. 仅单向：只上传 / 只下载
  python feishu_drive_sync.py --local-dir . --folder-token fldXXXXX --mode push
  python feishu_drive_sync.py --local-dir . --folder-token fldXXXXX --mode pull
        """)
    parser.add_argument("--local-dir", default=".",
                        help="本地目录路径（默认当前目录）")
    parser.add_argument("--folder-token", default=None,
                        help="飞书云盘已存在的目标文件夹 token")
    parser.add_argument("--create-folder", default=None,
                        help="自动创建文件夹名（与 --parent-token 配合）")
    parser.add_argument("--parent-token", default=None,
                        help="--create-folder 时的父文件夹 token（默认 Drive 根目录）")

    parser.add_argument("--mode", default="bidirectional",
                        choices=["bidirectional", "push", "pull"],
                        help="同步方向：bidirectional=双向(默认)  push=仅上传  pull=仅下载")

    parser.add_argument("--if-exists", default="smart",
                        choices=["smart", "overwrite", "skip"],
                        help="PUSH 阶段云端同名策略（默认 smart 增量）")
    parser.add_argument("--on-duplicate-remote", default="fail",
                        choices=["fail", "newest", "oldest"],
                        help="云端多条目同名策略")
    parser.add_argument("--as", dest="as_identity", default=None,
                        choices=["user", "bot"],
                        help="身份类型（默认 auto）")

    parser.add_argument("--sync-deletes", action="store_true",
                        help="传播删除（默认关闭，安全优先：不删除任一端文件）")
    parser.add_argument("--exclude", default=EXCLUDE_DEFAULT, nargs="*",
                        help="排除模式（fnmatch）")

    parser.add_argument("--dry-run", action="store_true",
                        help="预览模式：显示计划但不执行")
    parser.add_argument("--log", default=None,
                        help="详细日志文件路径（默认: scripts/feishu_drive_sync.log）")
    parser.add_argument("--verbose", action="store_true",
                        help="在 stdout 中逐行显示每个文件的状态")
    parser.add_argument("--quiet", action="store_true",
                        help="stdout 仅显示摘要+失败项")

    args = parser.parse_args()

    abs_local = os.path.abspath(args.local_dir)
    if not os.path.isdir(abs_local):
        print(f"错误：目录不存在 '{abs_local}'")
        sys.exit(1)

    if args.log:
        log_abs = os.path.abspath(args.log)
    else:
        log_abs = os.path.abspath(os.path.join(
            os.path.dirname(__file__) or os.getcwd(), "feishu_drive_sync.log"))
    if args.dry_run:
        log_abs = None

    # 加载基线状态（用于变更 / 冲突检测；dry-run 也加载以呈现真实计划）
    prev_state = load_state(abs_local)

    # 构建本地集合
    local_set = build_local_set(abs_local, args.exclude)

    # 解析目标文件夹
    folder_token = args.folder_token
    if not folder_token and not args.dry_run:
        if args.create_folder:
            folder_token = create_target_folder(args.create_folder, args.parent_token, args.as_identity)
        else:
            print("错误：必须指定 --folder-token 或 --create-folder（或 --dry-run 需 --folder-token）")
            sys.exit(1)
    if args.dry_run and not folder_token:
        print("错误：预览模式需要提供 --folder-token（远端基线）")
        sys.exit(1)

    # 构建远端集合
    remote_set = list_remote_recursive(folder_token, args.exclude) if folder_token else {}

    start_ts = time.time()
    print(f"\n{'=' * 50}")
    print(f"  开始双向同步")
    print(f"  本地: {abs_local}")
    print(f"  远端: folder_token={folder_token}")
    print(f"  模式: --mode={args.mode}")
    print(f"  时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'=' * 50}\n")

    # ── PULL 阶段（远端 → 本地）──
    pull_plan = {"downloaded": [], "conflicts": [], "skipped": [], "failed": [], "items": []}
    if args.mode in ("bidirectional", "pull"):
        print(f"[PULL] 远端 → 本地（{len(remote_set)} 个远端文件）...")
        if not args.dry_run:
            pull_plan = pull_phase(abs_local, local_set, remote_set, prev_state,
                                   verbose=args.verbose or not args.quiet)
        else:
            # dry-run：估算计划
            for path in sorted(remote_set.keys()):
                r = remote_set[path]
                if path in local_set:
                    p = prev_state.get(path)
                    lmt, lsz = local_set[path]
                    if p is None:
                        pull_plan["skipped"].append(path)
                        continue
                    local_changed = p.get("local_mtime") != lmt or p.get("local_size") != lsz
                    remote_changed = p.get("remote_mtime") != r["modified_time"]
                    if remote_changed and local_changed:
                        pull_plan["conflicts"].append(f"{path} (本地+远端均变更)")
                    elif remote_changed:
                        pull_plan["downloaded"].append(path)
                    else:
                        pull_plan["skipped"].append(path)
                else:
                    pull_plan["downloaded"].append(path)
        # 刷新本地集合（PULL 可能新增 / 覆盖文件）
        if not args.dry_run:
            local_set = build_local_set(abs_local, args.exclude)
            remote_set = list_remote_recursive(folder_token, args.exclude)

    # ── PUSH 阶段（本地 → 远端）──
    push_plan = None
    all_items = list(pull_plan.get("items", []))
    if args.mode in ("bidirectional", "push"):
        print(f"[PUSH] 本地 → 远端（{len(local_set)} 个本地文件）...")
        # 构建暂存目录（排除规则）
        staging = build_staging(abs_local, args.exclude) if args.exclude else None
        work_dir = staging if staging else abs_local
        work_parent = os.path.dirname(work_dir)
        work_name = os.path.basename(work_dir)
        os.chdir(work_parent)
        local_rel = work_name

        if args.dry_run:
            rc, out, err = run_lark([
                "+status", "--quick", "--local-dir", local_rel,
                "--folder-token", folder_token, "--format", "json",
            ], cwd=work_parent)
            # +status 不可靠（不应用排除），仅作参考不展示细节
            print(f"[PUSH] 预览跳过（+status 不应用排除规则，以实际运行结果为准）")
            push_plan = {"summary": {}, "items": []}
        else:
            push_plan = run_push(local_rel, folder_token, args.if_exists,
                                 args.as_identity, args.on_duplicate_remote,
                                 dry_run=False, cwd=work_parent)
            if staging:
                shutil.rmtree(staging, ignore_errors=True)
                print(f"[清理] 暂存目录已删除: {staging}")

        if push_plan:
            all_items.extend(push_plan.get("items", []))

    # ── 结果处理 ──
    if not args.dry_run:
        verbose = args.verbose or (not args.quiet)
        print_per_file_items(all_items, log_abs, verbose)

        # 重建并保存基线状态
        remote_final = list_remote_recursive(folder_token, args.exclude)
        local_final = build_local_set(abs_local, args.exclude)
        save_state(abs_local, rebuild_state(local_final, remote_final))

    elapsed = time.time() - start_ts
    print(f"\n  耗时: {elapsed:.1f}s")

    # 汇总
    pull_d = len(pull_plan.get("downloaded", []))
    pull_c = len(pull_plan.get("conflicts", []))
    pull_f = len(pull_plan.get("failed", []))
    push_u = (push_plan or {}).get("summary", {}).get("uploaded", 0)
    push_o = (push_plan or {}).get("summary", {}).get("overwritten", 0)
    push_s = (push_plan or {}).get("summary", {}).get("skipped", 0)
    push_f = (push_plan or {}).get("summary", {}).get("failed", 0)
    print(f"\n{'=' * 50}")
    print(f"  PULL  下载={pull_d}  冲突保全={pull_c}  失败={pull_f}")
    print(f"  PUSH  上传={push_u}  覆盖={push_o}  跳过={push_s}  失败={push_f}")
    print(f"{'=' * 50}")

    if args.dry_run:
        print("[完成] 预览结束（未执行）")
        sys.exit(0)

    total_failed = pull_f + push_f
    if total_failed > 0:
        print(f"[退出] {total_failed} 个文件同步失败，退出码=5")
        sys.exit(5)
    print("[完成] 双向同步成功")
    sys.exit(0)


if __name__ == "__main__":
    main()
