---
name: chint-git-lfs-sync
description: Use this skill when pushing or syncing the CHINT `chint-backup` Git repo (or any repo with Git LFS) to GitHub from a headless / sandbox macOS environment — especially when `git lfs push` appears to hang with zero output. It encodes the two-channel push model (LFS objects over HTTPS via the `gh` credential helper; pack over SSH skipping the LFS pre-push hook), the `lfs.locksverify=false` lock, and the credential-helper fix for the `osxkeychain` stall. Trigger on: "push to github", "sync chint", "git lfs push hangs", "upload to remote", "同步到远程".
agent_created: true
---

# CHINT Git + LFS 同步（沙箱 / headless macOS → GitHub）

## 何时使用本 skill
- 在 macOS 沙箱（无 GUI keychain 应答）里对 `chint-backup` 执行 `git push` / `git lfs push` 卡死、0 字节无进度。
- 用户要求「推送到 GitHub / 同步到远程 / upload to remote」且仓库含 Git LFS 大文件（主配电 `*.xlsx`）。
- 新设备 `clone` / `pull` 时报 `Permission denied`（~/.ssh 沙箱保护）。

> 仓库事实：`remote.origin.url = git@github.com:gzhang33/chint-backup.git`（SSH）；LFS 仅追踪 `excel 表格报告/框架模型/data/主配电*.xlsx`（120MB + 298MB）；整库含 `.git` 约 6.2GB。

## 双通道推送模型（已验证）
```
git objects (commit / tree / blobs / LFS 指针) → SSH 端口 22
LFS objects (大文件真实内容)                  → HTTPS 端口 443（经 lfs.url + gh 凭据）
```
- SSH 通道带小数据（commit 元数据 + LFS 指针文件），国内 SSH 出站通常优于 HTTPS。
- HTTPS 通道带大文件内容，流式传输穿透 GFW 干扰能力强；但需 **basic auth 凭据**。
- **关键锁**：`lfs.locksverify=false` 不可缺省——GitHub 不支持 LFS locking API，默认会超时导致整体失败。

## 根因速查（lfs push 卡死）
1. git-lfs 先试 LFS-over-SSH（`ssh … git-lfs-transfer …`）→ GitHub 不支持 → `Invalid command` → 回退 HTTPS。
2. 回退后对 `https://github.com/…/info/lfs/objects/batch` 做 basic auth；若 credential helper 只有 `osxkeychain` 且无 GUI 凭据 → **沙箱内阻塞**（永远等不到 keychain 弹窗）。
3. 验证「网络通、纯缺凭据」：`curl -m5 -o /dev/null -w "%{http_code}" https://github.com/gzhang33/chint-backup.git/info/lfs` 应快速返回 404。
4. 修复：把 `gh` 注册为 `https://github.com` 的凭据助手（见下）。注意 git 调用的是 `gh auth git-credential get` 动作；手动跑 `gh auth git-credential fill` 会报 "fill operation not supported"，属正常，不影响 git 实际使用。

## 推送流程（push）

### 常规推送（两步推送，`sync_push.sh` 已封装）
1. **一次性配置（repo-local，已持久化进 .git/config）**：
   ```bash
   git config lfs.locksverify false
   git config credential.https://github.com.helper ""
   git config --add credential.https://github.com.helper "!gh auth git-credential"
   git config lfs.url "https://github.com/gzhang33/chint-backup.git/info/lfs"
   ```
2. **先提交本地改动**（本 skill 不自动 commit，避免夹带未审阅内容）：
   ```bash
   git add -A && git -c user.name=阿布 -c user.email=abu@chint.local commit -m "chore: <说明>"
   ```
3. **两步推送**（用 `scripts/sync_push.sh` 自动化，含 5 次重试）：
   ```bash
   # 步骤 A：LFS 对象走 HTTPS（经 gh 凭据）
   git lfs push origin main
   # 步骤 B：仅 pack 走 SSH，跳过 LFS pre-push hook（避免 idle SSH 超时 SIGPIPE）
   GIT_LFS_SKIP_PUSH=1 git push origin main
   ```
4. **校验**：
   ```bash
   git status -s                                   # 应为空
   git rev-list --count --left-right origin/main...HEAD   # 应为 0  0
   git lfs ls-files -s                             # 已追踪
   ```

### LFS 迁移（大文件超过 GitHub 100MB 限制时）
当 push 被拒 `GH001: Large files detected` 时，需将大文件移入 LFS 追踪：

```bash
# 1. 迁移大文件到 LFS
git lfs migrate import --include-ref=main --include="*.xlsx,*.xlsm,*.pptx,*.pdf,*.zip" --yes

# 2. 强制推送（历史被重写，必须 force push）

# ⚠️ 对于 4+ GB LFS 仓库，GitHub 处理 LFS 对象可能耗时 5-10 分钟。
#   push 命令会在 "Uploading LFS objects: 100% ... done." 后挂起，直到 GitHub 处理完毕。
#   若超时（exit 141=SIGPIPE），等 30 秒后重试 — LFS 对象已缓存，后续 push 仅推送 ref。
#   第三次仍超时可改用两阶段推送（见下）。
GIT_LFS_SKIP_PUSH=1 git push --force-with-lease origin main
git lfs push origin main
```

**大仓库 push 超时处理**（4+GB LFS 对象）：
```bash
# 方案 A：等 GitHub 处理（推荐，简单）
# push 挂起时等待 5-10 分钟，不要强杀进程
git push --force-with-lease origin main 2>&1

# 方案 B：两阶段推送（适合反复超时的环境）
GIT_LFS_SKIP_PUSH=1 git push --force-with-lease origin main
git lfs push origin main
```

## 拉取流程（pull / clone，新设备）
`~/.ssh` 沙箱保护会让 LFS smudge filter 读 known_hosts/密钥 → `Permission denied`。
```bash
# 解法 A（已 clone 仅缺 LFS 内容）：跳过 smudge 先 reset，再单独 lfs pull
git -c filter.lfs.smudge= -c filter.lfs.process= -c filter.lfs.required=false reset --hard origin/main
git lfs pull        # 走 HTTPS + gh 凭据下载大文件
# 解法 B（首次 clone）：先普通 clone，再 lfs pull
git clone git@github.com:gzhang33/chint-backup.git
cd chint-backup && git lfs pull
```

## 前提与边界
- `gh auth status` 须 `Logged in` 且 token 含 `repo` 作用域（本机 `gho_…` 已满足）。
- 凭据助手为 **repo-local**，不影响其他仓库；chint-backup 的 pack 仍走 SSH（remote 是 SSH URL），凭据助手仅在 HTTPS LFS 端点生效。
- **合规**：仓库含「净收入」销售数据（核心商密级），上云前须经数据合规/信息安全审批；本 skill 仅解决技术传输，不改合规要求。
- 本 skill 不处理飞书云盘同步（机制 B 由 `lark-cli` 另议，且当前缺 Drive 作用域）。

## 脚本（scripts/）
| 脚本 | 作用 |
|------|------|
| `sync_push.sh [REPO_DIR]` | 自动配置 locksverify + gh 凭据助手 + lfs.url，提交提示后执行两步推送（LFS 5 次重试 + pack），最后打印 ahead/behind 校验 |
| `sync_pull.sh [REPO_DIR]` | 新设备拉取：跳过 smudge reset + `git lfs pull`（HTTPS + gh 凭据） |

## 快速示例
```bash
# 推送到 GitHub（在 chint 仓库根目录执行，或显式传路径）
bash ~/.workbuddy/skills/chint-git-lfs-sync/scripts/sync_push.sh /Users/gianni/Documents/chint
```
