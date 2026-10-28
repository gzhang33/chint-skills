#!/usr/bin/env bash
# chint-git-lfs-sync: 两步推送（LFS 走 HTTPS + gh 凭据，pack 走 SSH 跳过 LFS hook）
# 用法: bash sync_push.sh [REPO_DIR]   (默认 /Users/gianni/Documents/chint)
set -u
REPO_DIR="${1:-/Users/gianni/Documents/chint}"
cd "$REPO_DIR" || { echo "ERROR: 无法进入 $REPO_DIR"; exit 1; }

echo "=== 仓库: $REPO_DIR ==="

# 1) 关键锁 + 凭据助手 + 强制 LFS 走 HTTPS（repo-local, 幂等）
git config lfs.locksverify false
git config credential.https://github.com.helper "" 2>/dev/null
git config --add credential.https://github.com.helper "!gh auth git-credential" 2>/dev/null
git config lfs.url "https://github.com/gzhang33/chint-backup.git/info/lfs"

# 2) 状态自检
echo "=== gh 登录状态 ==="
gh auth status 2>&1 | grep -E "Logged in|Token scopes" || echo "WARN: gh 未登录或无 repo 作用域"
echo "=== 待推送 commit 数 ==="
AHEAD=$(git rev-list --count origin/main..HEAD 2>/dev/null || echo "0")
echo "ahead=$AHEAD"
if [ "$AHEAD" = "0" ]; then
  echo "无待推送 commit，结束。"; exit 0
fi

# 3) 步骤 A: LFS 对象走 HTTPS（5 次重试）
LFS_OK=0
for i in 1 2 3 4 5; do
  echo "=== git lfs push attempt $i (HTTPS via gh) ==="
  if git lfs push origin main >/tmp/lfs_push.log 2>&1; then
    echo "LFS_PUSH_OK at attempt $i"; LFS_OK=1; break
  else
    echo "LFS_PUSH_FAIL_$i"; tail -8 /tmp/lfs_push.log; echo "--- 5s 后重试 ---"; sleep 5
  fi
done

if [ "$LFS_OK" != "1" ]; then
  echo "LFS_PUSH_ALL_FAILED"; exit 1
fi

# 4) 步骤 B: 仅 pack 走 SSH，跳过 LFS pre-push hook（避免 idle SSH 超时 SIGPIPE）
echo "=== git push (pack only, skip lfs hook) over SSH ==="
GIT_LFS_SKIP_PUSH=1 git push origin main 2>&1; PEXIT=$?
echo "PACK_PUSH_EXIT=$PEXIT"
if [ "$PEXIT" != "0" ]; then
  echo "PACK_PUSH_FAILED"; exit 1
fi

# 5) 校验
echo "=== 最终校验 ==="
git status -s
git rev-list --count --left-right origin/main...HEAD
echo "DONE"
