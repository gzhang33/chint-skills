#!/usr/bin/env bash
# chint-git-lfs-sync: 新设备拉取（跳过 smudge reset + git lfs pull，HTTPS + gh 凭据）
# 用法: bash sync_pull.sh [REPO_DIR]   (默认 /Users/gianni/Documents/chint)
set -u
REPO_DIR="${1:-/Users/gianni/Documents/chint}"
cd "$REPO_DIR" || { echo "ERROR: 无法进入 $REPO_DIR（先 git clone git@github.com:gzhang33/chint-backup.git）"; exit 1; }

echo "=== 仓库: $REPO_DIR ==="

# 凭据助手 + 强制 LFS 走 HTTPS（repo-local, 幂等）
git config credential.https://github.com.helper "" 2>/dev/null
git config --add credential.https://github.com.helper "!gh auth git-credential" 2>/dev/null
git config lfs.url "https://github.com/gzhang33/chint-backup.git/info/lfs"
git config lfs.locksverify false

# ~/.ssh 沙箱保护会让 LFS smudge 读密钥失败 → 先跳过 smudge reset，再单独 lfs pull
echo "=== 跳过 smudge reset --hard origin/main ==="
git -c filter.lfs.smudge= -c filter.lfs.process= -c filter.lfs.required=false reset --hard origin/main 2>&1 | tail -3
echo "=== git lfs pull (HTTPS + gh 凭据) ==="
git lfs pull 2>&1 | tail -10
echo "=== 校验 ==="
git rev-list --count --left-right origin/main...HEAD
git lfs ls-files -s
echo "DONE"
