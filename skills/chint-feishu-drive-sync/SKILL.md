---
name: chint-feishu-drive-sync
description: Use this skill to sync the CHINT `chint` working folder with Feishu Drive (飞书云盘) over the `lark-cli` — supporting BIDIRECTIONAL incremental sync (local↔remote), per-file status logging, conflict preservation, and auto folder mirroring. Encodes the baseline-state conflict-detection model, the pull-first/push-second ordering, the relative-path constraint of `lark-cli drive +push/+download`, and the auth scopes required (drive:drive / space:document:retrieve / drive:file:download). Trigger on: "同步到飞书", "飞书云盘同步", "chint 双向同步", "sync chint drive", "feishu drive sync", "同步 chint".
agent_created: true
---

# CHINT ↔ 飞书云盘 双向同步（lark-cli 驱动）

## 何时使用本 skill
- 用户要求「把 chint 同步到飞书云盘 / 从飞书云盘拉回 / 双向同步 / sync drive」。
- 需要在 macOS 本地工作树与飞书云盘之间保持文件一致，且**两个方向都要流通**（本地改了上传、云端改了拉回）。
- 定时自动化（每日 08:30 / 12:00 / 17:30）触发增量双向同步。

> 仓库事实（**按设备配置，不内置于脚本**）：本地路径由 `CHINT_REPO` 指定，缺省 `$HOME/Documents/chint`；飞书云盘目标文件夹 `chint`（token 由 `CHINT_DRIVE_FOLDER` 指定，缺省 `L6DNfECGTlrY13dQiL3cxQiOnBb`），URL `https://chintsso.feishu.cn/drive/folder/L6DNfECGTlrY13dQiL3cxQiOnBb`。工作树约 6GB / 189 个同步文件（已排除 `.git`/`.venv` 等）。换设备只需设置这两个环境变量。

## 同步模型（基线守护型双向同步）
维护基线状态文件 `.feishu_drive_sync_state.json`（位于本地 chint 根，自动排除，不进同步范围），记录每个文件上次同步时的「本地 mtime+size」与「远端 modified_time+token」。每次运行：

```
PULL 阶段（远端 → 本地，先于 PUSH）
  ├─ 仅远端有            → 下载到本地（新建）
  ├─ 两端都有，仅远端变更 → 下载覆盖本地
  ├─ 两端都有，仅本地变更 → 跳过（交给 PUSH 上传）
  ├─ 两端都有，两侧都变更 → 冲突：另存远端副本 <name>.conflict-remote-<时间戳><ext>，保留本地
  └─ 两端都有，都未变更   → 跳过

PUSH 阶段（本地 → 远端，复用 +push --if-exists smart）
  ├─ 仅本地有            → 上传
  ├─ 本地已变更          → 覆盖远端
  └─ PULL 已保全的冲突    → 本地版本覆盖到远端（本地胜出，远端副本已本地留存）
```

**PULL 先于 PUSH 是关键**：若先 PUSH 会把远端编辑覆盖掉，冲突便无法保全。

**首次运行无基线**：两端都存在的文件一律视为「已一致」跳过（不会误报冲突）；仅远端有→下载，仅本地有→上传。

**删除传播（Git 对称风格，默认双向传播）**：

```
本地删除  →  marked_deleted  →  delete_remote_phase()  →  lark-cli +delete --yes 删除远端
远端删除  →  DETECT REMOTE DELETE 阶段  →  远程二次确认 + 本地修改保护  →  delete_local_phase()  →  rm 本地
```

- **默认双向自动传播**（Git push/pull 风格），无需任何额外参数。
- 远端删除事件在同步时会触发**二次确认**（重新列出远端目录），避免 API 临时抖动导致误删本地文件。
- 本地修改保护：若本地文件自上次同步后被用户修改过，即使远端已删也**保留本地**（标记为冲突）。
- `--no-sync-deletes` 关闭删除传播（兜底安全）。
- `--dry-run` 仅预览，不执行任何删除。
- 删除操作记录到日志文件和 stdout（`LOCAL_DELETED` / `REMOTE_DELETED` / `DELETE_FAILED`）。

## CLI 速查（lark-cli drive）
```bash
# 列出文件夹（递归由脚本封装；单级如下）
lark-cli drive files list --params '{"folder_token":"<fld>"}' --format json
#   返回条目字段：name, type(file|folder), token, modified_time(Unix秒,字符串), parent_token, url
#   注意：files list 不含 size 字段（仅 modified_time）

# 下载单个文件（--output 必须是 cwd 内的相对路径，与 +push 同约束）
lark-cli drive +download --file-token <token> --output ./相对/路径.txt --overwrite

# 上传整个目录（--local-dir 必须是 cwd 内的相对路径）
lark-cli drive +push --local-dir <相对目录名> --folder-token <fld> --if-exists smart --format json

# 新建文件夹
lark-cli drive +create-folder --name <名> [--folder-token <父fld>]

# 删除远端文件（高危，需 --yes）
lark-cli drive +delete --file-token <token> --type file --yes
```

## 使用流程
```bash
cd "${CHINT_REPO:-$HOME/Documents/chint}"

# 1. 双向同步（默认，推荐每日自动化调用）
python scripts/feishu_drive_sync.py --local-dir . --folder-token "${CHINT_DRIVE_FOLDER:-L6DNfECGTlrY13dQiL3cxQiOnBb}" --mode bidirectional --verbose

# 2. 仅预览（不执行）
python scripts/feishu_drive_sync.py --local-dir . --folder-token L6DNfECGTlrY13dQiL3cxQiOnBb --dry-run

# 3. 仅单向
python scripts/feishu_drive_sync.py --local-dir . --folder-token L6DNfECGTlrY13dQiL3cxQiOnBb --mode push
python scripts/feishu_drive_sync.py --local-dir . --folder-token L6DNfECGTlrY13dQiL3cxQiOnBb --mode pull

# 4. 首次创建目标文件夹后同步
python scripts/feishu_drive_sync.py --local-dir . --create-folder chint
```

脚本参数：`--mode {bidirectional,push,pull}`（默认 bidirectional）、`--if-exists {smart,overwrite,skip}`、`--exclude`（fnmatch，默认见下）、`--log`、`--verbose/--quiet`、`--dry-run`、`--no-sync-deletes`。

## 排除规则（脚本内固化，默认）
```
.git  .venv  .zcode  .DS_Store  __pycache__  *.pyc  .playwright-mcp
~$*          (Excel 打开时的锁文件)
*.bak*       (备份文件，如 v2.bak-20260713.xlsx)
.feishu_drive_sync_state.json   (本脚本基线状态)
feishu_drive_sync.log           (本脚本日志)
```
即「完整同步 chint 工作树，但剔除工具 / 缓存 / 临时 / 仓库内部 / 运行时产物」。

## 冲突处理（不丢数据）
本地与远端同时修改同一文件 → 脚本保留本地版本，另存远端副本为 `<目录>/<名>.conflict-remote-<YYYYMMDD-HHMMSS><扩展名>` 到本地，并在日志与 stdout 标注。用户可手动比对合并后删除冲突副本。绝不静默覆盖任一侧。

## 排错
| 现象 | 根因 | 修复 |
|------|------|------|
| `+push`/`files list` 报 `missing_scope` | 缺 `drive:drive` / `space:document:retrieve` / `drive:file:download` | `lark-cli auth login --scope "drive:drive space:document:retrieve drive:file:download"` 重新授权 |
| `+push`/`+download` 报 `unsafe ... must be a relative path` | lark-cli 要求 `--local-dir`/`--output` 是 cwd 内相对路径 | 脚本已自动 `chdir` 到父目录后用相对名，勿传绝对路径 |
| 首次全量同步中途 `timout`（脚本退出码 -1） | 大文件（284MB Excel）超 600s 默认超时 | 脚本已调至 `timeout=3600`；重跑时 `--if-exists smart` 跳过已传文件续传 |
| `+download` 空输出无文件 | 同上相对路径约束 / token 错误 | 确认 token 为 file 类型、cwd 正确 |
| 远端出现孤儿（测试/锁文件） | 排除规则早期缺失或手动误传 | 用 `files list` 定位 token 后 `+delete --yes` 清理 |

## 参考
- 脚本：`scripts/feishu_drive_sync.py`（封装全部逻辑）
- 类似实践：`chint-git-lfs-sync` skill（Git LFS 双通道推送模型）
- 飞书 CLI 文档：`lark-drive` connector skill
