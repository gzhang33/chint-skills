#!/usr/bin/env bash
# chint-git-lfs-sync: 两步推送 + LFS force push 支持
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
BEHIND=$(git rev-list --count HEAD..origin/main 2>/dev/null || echo "0")
echo "ahead=$AHEAD behind=$BEHIND"

# 若有 behind，提示可选 pull
if [ "$BEHIND" != "0" ] && [ "$AHEAD" != "0" ]; then
  echo "WARN: 本地与远端分叉（ahead=$AHEAD behind=$BEHIND），需 force push"
  echo "  若因 LFS 迁移历史重写导致分叉，执行：git push --force-with-lease origin main"
fi

if [ "$AHEAD" = "0" ] && [ "$BEHIND" = "0" ]; then
  echo "已同步，结束。"; exit 0
fi

# 3) 检测是否为分叉（需要 LFS 迁移后的 force push）
if [ "$BEHIND" != "0" ] && [ "$AHEAD" != "0" ]; then
  echo "=== 分叉检测：执行两阶段 force push ==="
  GIT_LFS_SKIP_PUSH=1 git push --force-with-lease origin main 2>&1; PEXIT=$?
  echo "PACK_PUSH_EXIT=$PEXIT"
  if [ "$PEXIT" != "0" ]; then
    echo "PACK_FORCE_PUSH_FAILED"; exit 1
  fi
  # 第二阶段：LFS 对象
  echo "=== git lfs push (HTTPS via gh) ==="
  git lfs push origin main 2>&1; LEXIT=$?
  echo "LFS_PUSH_EXIT=$LEXIT"
  if [ "$LEXIT" != "0" ]; then
    echo "LFS_PUSH_FAILED"; exit 1
  fi
else
  # 4) 常规两步推送（无分叉）
  LFS_OK=0
  for i in 1 2 3 4 5; do
    echo "=== git lfs push attempt $i (HTTPS via gh) ==="
    if git lfs push origin main >/tmp/lfs_push.log 2>&1; then
      echo "LFS_PUSH_OK at attempt $i"; LFS_OK=1; break
    else
      echo "LFS_PUSH_FAIL_$i"; tail -8 /tmp/lfs_push.log; sleep 5
    fi
  done

  if [ "$LFS_OK" != "1" ]; then
    echo "LFS_PUSH_ALL_FAILED"; exit 1
  fi

  echo "=== git push (pack only, skip lfs hook) over SSH ==="
  GIT_LFS_SKIP_PUSH=1 git push origin main 2>&1; PEXIT=$?
  echo "PACK_PUSH_EXIT=$PEXIT"
  if [ "$PEXIT" != "0" ]; then
    echo "PACK_PUSH_FAILED"; exit 1
  fi
fi

# 5) 校验
echo "=== 最终校验 ==="
git fetch origin main 2>&1 | tail -1
git status -s
git rev-list --count --left-right origin/main...HEAD
echo "DONE"
