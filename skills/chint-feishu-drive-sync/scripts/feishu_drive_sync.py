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

删除传播(Git对称风格): 默认双向传播(本地删->远端删,远端删->本地删)。--no-sync-deletes关闭。

依赖：lark-cli（已配置 auth，需 drive:drive / space:document:retrieve / drive:file:download 等 scope）
状态文件与日志会被自动排除，不会进入同步范围。
"""

import argparse
import fnmatch
import hashlib
import json
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from datetime import datetime
from pathlib import Path

# ── 常量 ──────────────────────────────────────────────
LARK_CLI_BIN = None          # 首次调用时探查
# PUSH 看门狗：单轮超时 + 自动重试（防大文件上传半死连接无限悬挂）
PUSH_TIMEOUT_SECONDS = 1500  # 单轮 +push 最长 25 分钟，超时即杀掉进程组
PUSH_MAX_RETRIES = 4         # 失败/超时最多重试 4 轮（依赖 smart 跳过已传文件逐轮推进）
# 排除：仓库内部 / 工具 / 缓存 / 临时 / 运行时产物 / 独立代码工程
EXCLUDE_DEFAULT = [
    ".git", ".venv", "venv", ".zcode", ".DS_Store", "__pycache__", "*.pyc",
    ".playwright-mcp", "~$*", "*.bak*", "*.backup*",
    ".feishu_drive_sync_state.json", "feishu_drive_sync.log",
    "temp", "_backup_trash", ".feishu_conflict_tmp",
    "rescue_backup",
    "node_modules",
    ".next", "dist", "build",
    ".trae", ".trae-cn",
    ".claude", ".cursor", ".gemini", ".windsurf", ".workbuddy",
    "Areas/data-analytics", "Areas/竞品分析",
    "graphify-out",
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
    """运行 `lark-cli drive <...>` 并返回 (exit_code, stdout, stderr)。

    timeout 触发时通过进程组 SIGKILL 杀掉 lark-cli 及其派生的 node 子进程，
    避免“半死连接”残留孤儿进程导致后续同步无限悬挂。
    """
    global LARK_CLI_BIN
    if LARK_CLI_BIN is None:
        LARK_CLI_BIN = find_lark_cli()
    cmd = [LARK_CLI_BIN, "drive"] + args
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                text=True, cwd=cwd, start_new_session=True)
    except Exception as e:  # 启动失败
        return -2, "", f"spawn_error: {e}"
    try:
        out, err = proc.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        # 杀掉整个进程组（含 lark-cli 派生的 node 子进程），防止孤儿进程
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
        except Exception:
            try:
                proc.kill()
            except Exception:
                pass
        try:
            out, err = proc.communicate(timeout=5)
        except Exception:
            out, err = "", ""
        return -1, "", "timeout"
    clean_stdout = _strip_ansi(out or "")
    clean_stderr = _strip_ansi(err or "")
    return proc.returncode, clean_stdout, clean_stderr


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
    """检查 rel_path 是否匹配任一排除模式（支持文件名通配、单级目录名通配与多级目录前缀递归）"""
    rel_path = rel_path.replace(os.sep, "/").strip("/")
    parts = rel_path.split("/")
    for raw_pat in excludes:
        pat = raw_pat.rstrip("/")
        # 1. 完整路径通配匹配
        if fnmatch.fnmatch(rel_path, pat):
            return True
        # 2. 目录前缀精确命中（如 Areas/竞品分析 命中 Areas/竞品分析/foo.pdf）
        if rel_path == pat or rel_path.startswith(pat + "/"):
            return True
        # 3. 单级目录名/文件名通配匹配（如 temp 命中 a/b/temp/c.txt）
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


def _file_hash(path: str) -> str | None:
    """返回文件 sha256 hex（失败返回 None）。用于冲突判定的内容一致性比对。"""
    h = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(1 << 20), b""):
                h.update(chunk)
        return h.hexdigest()
    except OSError:
        return None


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
                # 疑似冲突：先下载远端内容到临时区，与本地做内容哈希比对，
                # 避免"两端 mtime 都变但内容已一致"（如中断重启导致基线漂移）的误判冲突。
                stem, ext = os.path.splitext(path)
                tmp_rel = f".feishu_conflict_tmp/{abs(hash(path)):016x}{ext}"
                ok, derr = download_file(r["token"], tmp_rel, local_dir, overwrite=True)
                if not ok:
                    failed.append((path, derr))
                    items.append({"action": "pull_failed", "rel_path": path, "error": derr})
                    continue
                tmp_path = os.path.join(local_dir, tmp_rel)
                local_path = os.path.join(local_dir, path)
                if _file_hash(tmp_path) == _file_hash(local_path):
                    # 内容一致 → 误判，跳过，不生成 conflict 副本（清理临时文件）
                    try:
                        os.remove(tmp_path)
                    except OSError:
                        pass
                    skipped.append(path)
                    items.append({"action": "pull_skipped",
                                  "rel_path": path, "note": "content-identical (false-conflict avoided)"})
                else:
                    # 真冲突：保全远端副本（临时文件 rename 到 conflict_rel，避免二次下载）
                    conflict_rel = f"{stem}.conflict-remote-{ts}{ext}".replace(os.sep, "/")
                    conflict_path = os.path.join(local_dir, conflict_rel)
                    try:
                        os.replace(tmp_path, conflict_path)
                        conflicts.append(conflict_rel)
                        items.append({"action": "conflict", "rel_path": conflict_rel, "src": path})
                    except OSError as e:
                        failed.append((path, str(e)))
                        items.append({"action": "pull_failed", "rel_path": path, "error": str(e)})
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
            # 本地不存在 → 三态判定
            p = prev_state.get(path)
            if p is not None:
                skipped.append(path)
                items.append({"action": "marked_deleted", "rel_path": path, "remote_token": r["token"]})
            else:
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

# ── 远端删除（DELETE 传播）───────────────────────────

def delete_remote_phase(delete_items: list[dict], dry_run: bool = False) -> tuple[list[str], list[tuple]]:
    """通过 lark-cli +delete 按 token 精准删除远端文件
    delete_items: [{"rel_path": ..., "remote_token": ...}]
    返回 (deleted_paths, failed_pairs)
    """
    deleted, failed = [], []
    for item in delete_items:
        path = item.get("rel_path", "?")
        tok = item.get("remote_token")
        if not tok:
            continue
        args = ["+delete", "--file-token", tok, "--type", "file", "--yes", "--format", "json"]
        if dry_run:
            deleted.append(path)
            continue
        rc, out, err = run_lark(args)
        obj = extract_json(out)
        if obj and obj.get("ok"):
            deleted.append(path)
        else:
            msg = (obj.get("error", {}).get("message", err) if obj else err)
            failed.append((path, msg))
    return deleted, failed



# ── 本地删除(DELETE LOCAL)──

def delete_local_phase(delete_items, local_dir, dry_run=False):
    """Safe local file deletion (remote delete event)"""
    deleted, skipped = [], []
    for item in delete_items:
        path = item["rel_path"]
        full = os.path.join(local_dir, path)
        if not os.path.exists(full):
            deleted.append(path)
            continue
        if dry_run:
            skipped.append((path, "dry-run"))
            continue
        try:
            os.remove(full)
            deleted.append(path)
        except OSError as e:
            skipped.append((path, str(e)))
    return deleted, skipped

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
            if os.path.islink(src_file) and not os.path.exists(src_file):
                continue
            dst_dir = os.path.dirname(os.path.join(stage, rel_path))
            os.makedirs(dst_dir, exist_ok=True)
            dst_file = os.path.join(stage, rel_path)
            try:
                os.link(src_file, dst_file)
            except OSError:
                try:
                    shutil.copy2(src_file, dst_file)
                except OSError as e:
                    shutil.rmtree(stage, ignore_errors=True)
                    raise RuntimeError(f"暂存文件失败（无法链接且无法复制）: {src_file} -> {dst_file} ({e})")
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
             dry_run: bool, cwd: str, timeout: int = PUSH_TIMEOUT_SECONDS) -> dict | None:
    """执行 `lark-cli drive +push`，返回解析后的 data dict。

    返回 None 表示可重试的失败（超时 / 输出无法解析 / 推送错误），由调用方决定是否重试；
    授权类错误 (missing_scope) 仍直接 sys.exit，不进入重试。
    """
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

    rc, out, err = run_lark(args, cwd=cwd, timeout=timeout)
    if rc == -1:
        print(f"[PUSH] 超时（>{timeout}s），连接可能半死，交由重试逻辑处理")
        return None
    if rc == -2:
        print(f"[PUSH] 启动失败：{err}")
        return None

    obj = extract_json(out)
    if not obj:
        print(f"[错误] 无法解析 push 输出\nstdout:\n{out}\nstderr:\n{err}")
        return None  # 可重试

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
        return None  # 可重试（走重试逻辑）

    data = obj.get("data") or {}
    if not data and not dry_run:
        print(f"[警告] push 返回无 data：{json.dumps(obj, ensure_ascii=False)}")
    return data


def run_push_with_retry(local_rel: str, folder_token: str, if_exists: str,
                        as_identity: str | None, dup_remote: str | None,
                        dry_run: bool, cwd: str,
                        timeout: int = PUSH_TIMEOUT_SECONDS,
                        retries: int = PUSH_MAX_RETRIES) -> dict | None:
    """带看门狗超时 + 自动重试的 PUSH。

    - 单轮 +push 受 timeout 限制，超时即杀掉进程组（防半死连接无限悬挂）；
    - 多轮重试依赖 --if-exists smart 跳过已成功上传的文件，逐轮推进；
    - 代理对大文件数据流间歇性挂死时，换连接重试通常可过（GFW 干扰下重试 1-2 次即可）。
    """
    last_data = None
    last_failed = None
    for attempt in range(1, retries + 1):
        print(f"[PUSH] 第 {attempt}/{retries} 轮（单轮超时 {timeout}s）...")
        data = run_push(local_rel, folder_token, if_exists, as_identity,
                        dup_remote, dry_run, cwd, timeout=timeout)
        if data is None:
            print(f"[PUSH] 第 {attempt} 轮超时/失败，{'准备重试' if attempt < retries else '已达重试上限'}")
            continue
        summary = data.get("summary", {}) or {}
        failed = summary.get("failed", 0)
        if failed == 0:
            print(f"[PUSH] 第 {attempt} 轮成功（无失败项）")
            return data
        last_data, last_failed = data, failed
        print(f"[PUSH] 第 {attempt} 轮有 {failed} 个失败项，依赖 smart 跳过已传文件后重试")
    if last_data is not None:
        print(f"[PUSH] 重试耗尽，仍有 {last_failed} 个失败项（不再无限挂死）")
        return last_data
    print("[PUSH] 重试耗尽且全部轮次超时/失败")
    return None


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
    "marked_deleted":  ("待删标记",   "MARKED_DELETED"),
    "local_deleted":   ("本地已删",   "LOCAL_DELETED"),
    "remote_deleted":  ("远端已删",   "REMOTE_DELETED"),
    "delete_failed":   ("删除失败",   "DELETE_FAILED"),
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
        ("DELETE_FAILED", "❌ 删除失败"),
        ("CONFLICT", "⚠️  冲突保全（远端副本另存本地）"),
        ("FOLDER", "📁 远端新建目录"),
        ("UPLOADED", "  ✅ 上传成功（新增）"),
        ("OVERWRITTEN", " 🔄 覆盖更新（上传）"),
        ("DOWNLOADED", "  ⬇️  下载成功（远端→本地）"),
        ("SKIPPED", " ⏭️  跳过（未变更）"),
        ("PULL_SKIPPED", " ⏭️  跳过（未变更）"),
        ("LOCAL_DELETED", " 🗑️  本地已删（远端删除事件）"),
        ("REMOTE_DELETED", " 🗑️  远端已删（本地删除事件）"),
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

    parser.add_argument("--no-sync-deletes", action="store_true",
                        help="关闭删除传播(默认双向传播,Git风格对称同步)")
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
    args.sync_deletes = not args.no_sync_deletes  # default ON (Git style)

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

    # ── 远端删除检测(DETECT REMOTE DELETE)──
    all_items = []
    remote_deletes = []
    for path, p in prev_state.items():
        if p.get("remote_token") and path not in remote_set and path in local_set:
            # 本地修改保护：仅当本地文件未被修改时才允许删除
            if path in local_set:
                lmt, _lsz = local_set[path]
                local_changed = (p.get("local_mtime") is not None 
                                 and p.get("local_mtime") != lmt)
                if local_changed:
                    # 远端删了，但本地也修改了 → 冲突，不删本地
                    print(f"  [CONFLICT] {path}: remote deleted but local also modified, keeping local")
                    all_items.append({"action": "conflict", "rel_path": path, 
                                      "src": f"remote-deleted-vs-local-modified"})
                    continue
            remote_deletes.append({"rel_path": path, "remote_token": p["remote_token"]})
    if remote_deletes:
        print(f"[DETECT] {len(remote_deletes)} remote-deleted local files pending")
        # 远端二次确认：重新列出远端文件，避免 API 截断误判
        if not args.dry_run and args.sync_deletes:
            remote_set_v2 = list_remote_recursive(folder_token, args.exclude)
            truly_deleted = []
            for it in remote_deletes:
                if it["rel_path"] not in remote_set_v2:
                    truly_deleted.append(it)
                else:
                    print(f"  [SKIP] {it['rel_path']}: reappeared on 2nd scan, NOT deleted")
            remote_deletes = truly_deleted
        for it in remote_deletes:
            all_items.append({"action": "local_deleted", "rel_path": it["rel_path"]})
        if args.sync_deletes and not args.dry_run:
            del_ok, del_skip = delete_local_phase(remote_deletes, abs_local)
            if del_skip:
                for p, e in del_skip:
                    print(f"  skip: {p} ({e})")
            print(f"  local delete: {len(del_ok)} ok, {len(del_skip)} skip")
        elif args.dry_run:
            print(f"  (dry-run)")
        elif not args.sync_deletes:
            print(f"  --no-sync-deletes: keep local files")

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
                    if prev_state.get(path) is not None:
                        pull_plan["skipped"].append(f"{path} (本地已删, will sync-delete remote)")
                    else:
                        pull_plan["downloaded"].append(path)
        # 刷新本地集合（PULL 可能新增 / 覆盖文件）
        if not args.dry_run:
            local_set = build_local_set(abs_local, args.exclude)
            remote_set = list_remote_recursive(folder_token, args.exclude)

    # ── PUSH 阶段（本地 → 远端）──
    push_plan = None
    all_items += list(pull_plan.get("items", []))
    if args.mode in ("bidirectional", "push"):
        print(f"[PUSH] 本地 → 远端（{len(local_set)} 个本地文件）...")
        if args.dry_run:
            # dry-run 纯内存元数据比对，零磁盘开销、零临时目录泄漏
            print(f"[PUSH] 预览跳过（无需物理暂存，以本地/远端元数据比对为准）")
            push_plan = {"summary": {}, "items": []}
        else:
            # 构建暂存目录（排除规则）
            staging = build_staging(abs_local, args.exclude) if args.exclude else None
            try:
                work_dir = staging if staging else abs_local
                work_parent = os.path.dirname(work_dir)
                work_name = os.path.basename(work_dir)
                os.chdir(work_parent)
                local_rel = work_name

                push_plan = run_push_with_retry(local_rel, folder_token, args.if_exists,
                                     args.as_identity, args.on_duplicate_remote,
                                     dry_run=False, cwd=work_parent,
                                     timeout=PUSH_TIMEOUT_SECONDS, retries=PUSH_MAX_RETRIES)
            finally:
                if staging:
                    shutil.rmtree(staging, ignore_errors=True)
                    print(f"[清理] 暂存目录已删除: {staging}")

        if push_plan:
            all_items.extend(push_plan.get("items", []))

    # ── 删除传播（DETECT DELETE）──
    delete_items = [it for it in all_items if it.get("action") == "marked_deleted"]
    if delete_items:
        print(f"[DELETE] {len(delete_items)} 个本地删除的远端文件待处理")
        if args.sync_deletes and not args.dry_run:
            deleted, failed = delete_remote_phase(delete_items)
            for d in deleted:
                all_items.append({"action": "remote_deleted", "rel_path": d})
            for f_path, f_err in failed:
                all_items.append({"action": "delete_failed", "rel_path": f_path, "error": f_err})
            print(f"  删除成功={len(deleted)}  失败={len(failed)}")
        elif args.dry_run:
            for it in delete_items:
                all_items.append({"action": "remote_deleted", "rel_path": it["rel_path"]})
        elif args.no_sync_deletes:
            print(f"  --no-sync-deletes: keep remote files")
        else:
            print(f"  will delete remote ({len(delete_items)} files)")

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
