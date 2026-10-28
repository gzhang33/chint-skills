#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Portable consistency checker for chint-pptx deployment locations.

The canonical library is the parent directory of this script's `scripts/` folder.
Other endpoints must either link to the canonical library or contain identical files.

Endpoints can be supplied repeatedly with `--endpoint PATH`. By default, the checker
uses DEFAULT_ENDPOINTS (with `~` expanded) and paths from CHINT_PPTX_SYNC_ENDPOINTS,
separated by `os.pathsep`. Missing endpoints are skipped as undeployed unless
`--strict-missing` is set.

The checker hashes files and reports mismatches. A symlink to the canonical library is
considered consistent and its form is still reported.

Behavior:
* Prints all results in one invocation.
* Is read-only and safe to rerun.
* Exit codes: 0 means all judged endpoints match; 1 means at least one mismatch; 2 means
  a fatal error such as an inaccessible canonical library.
* Excludes `__pycache__`, `.pyc`, `.pyo`, and `.DS_Store` from comparisons because these
  are generated caches or local metadata, not skill resources.

Usage:
  python3 scripts/verify_skill_sync.py
  python3 scripts/verify_skill_sync.py --json
  python3 scripts/verify_skill_sync.py --quiet
  python3 scripts/verify_skill_sync.py --endpoint /path/to/chint-pptx --strict-missing
"""
from __future__ import annotations

import hashlib
import json
import os
import sys

# The parent of this script's `scripts/` directory is the canonical library.
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CANONICAL = os.path.dirname(SCRIPT_DIR)

# Default user-level endpoints are portable across devices and users.
# Missing endpoints are warnings unless `--strict-missing` is set. Use `--endpoint` or
# CHINT_PPTX_SYNC_ENDPOINTS (separated by `os.pathsep`) to configure additional targets.
DEFAULT_ENDPOINTS = [
    "~/Documents/chint/.agents/skills/chint-pptx",
    "~/Documents/chint/.codebuddy/skills/chint-pptx",
    "~/.workbuddy/skills/chint-pptx",
]

# Exclude generated Python bytecode and local filesystem metadata.
EXCLUDE_DIRNAMES = {"__pycache__"}
EXCLUDE_FILENAMES = {".DS_Store"}
EXCLUDE_SUFFIXES = {".pyc", ".pyo"}


def sha256_of_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def collect_files(root: str):
    """Return relative-path hashes, excluding bytecode caches and local metadata."""
    result = {}
    for dirpath, dirnames, filenames in os.walk(root):
        # Prune cache directories in place so os.walk does not enter them.
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRNAMES]
        for fn in filenames:
            if fn in EXCLUDE_FILENAMES or os.path.splitext(fn)[1].lower() in EXCLUDE_SUFFIXES:
                continue
            full = os.path.join(dirpath, fn)
            if not os.path.isfile(full) or os.path.islink(full):
                # Skip endpoint symlink files to avoid duplicate entries and cycles.
                continue
            rel = os.path.relpath(full, root)
            try:
                result[rel] = sha256_of_file(full)
            except OSError as e:
                result[rel] = f"<ERR:{e}>"
    return result


def resolve_target(path: str):
    """Return a normalized symlink target, or None when path is not a symlink."""
    if os.path.islink(path):
        return os.path.realpath(path)
    return None


def inspect_endpoint(path: str, canonical: str):
    """Return endpoint status and file differences."""
    info = {"path": path}

    if not os.path.exists(path) and not os.path.islink(path):
        info.update(status="MISSING", form="absent", diffs=[])
        return info

    target = resolve_target(path)
    if target is not None:
        info["form"] = "symlink"
        info["target"] = target
        if os.path.realpath(target) == os.path.realpath(canonical):
            info["status"] = "CONSISTENT"
            info["note"] = "symlink 指向运行库，自动一致"
        else:
            info["status"] = "MISMATCH"
            info["note"] = "symlink 未指向运行库"
        info["diffs"] = []
        return info

    # Compare real directories file by file.
    info["form"] = "realdir"
    try:
        ep_files = collect_files(path)
    except Exception as e:  # noqa: BLE001
        info.update(status="ERROR", diffs=[f"无法遍历: {e}"])
        return info

    try:
        ca_files = collect_files(canonical)
    except Exception as e:  # noqa: BLE001
        info.update(status="ERROR", diffs=[f"无法遍历运行库: {e}"])
        return info

    diffs = []
    ca_keys = set(ca_files)
    ep_keys = set(ep_files)
    for rel in sorted(ca_keys - ep_keys):
        diffs.append({"rel": rel, "kind": "MISSING_IN_ENDPOINT", "canonical_sha256": ca_files[rel]})
    for rel in sorted(ep_keys - ca_keys):
        diffs.append({"rel": rel, "kind": "EXTRA_IN_ENDPOINT", "endpoint_sha256": ep_files[rel]})
    for rel in sorted(ca_keys & ep_keys):
        cs, es = ca_files[rel], ep_files[rel]
        if cs != es:
            diffs.append({
                "rel": rel,
                "kind": "CONTENT_DIFF",
                "canonical_sha256": cs,
                "endpoint_sha256": es,
            })
    info["status"] = "CONSISTENT" if not diffs else "MISMATCH"
    info["diffs"] = diffs
    info["file_count_endpoint"] = len(ep_keys)
    info["file_count_canonical"] = len(ca_keys)
    return info


def main(argv=None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    as_json = "--json" in argv
    quiet = "--quiet" in argv
    strict_missing = "--strict-missing" in argv

    import argparse
    ap = argparse.ArgumentParser(description="chint-pptx 多落点一致性核验")
    ap.add_argument("--endpoint", action="append", default=None,
                    help="额外核验落点（可重复）。缺省用常规落点 + 环境变量 CHINT_PPTX_SYNC_ENDPOINTS")
    ap.add_argument("--strict-missing", action="store_true",
                    help="缺失落点也判负（默认仅 WARN，视为该设备未部署）")
    known, rest = ap.parse_known_args(argv)
    as_json = as_json or "--json" in rest
    quiet = quiet or "--quiet" in rest
    strict_missing = strict_missing or "--strict-missing" in rest

    if known.endpoint:
        raw_endpoints = known.endpoint
    else:
        env_val = os.environ.get("CHINT_PPTX_SYNC_ENDPOINTS", "")
        env_items = [v for v in env_val.split(os.pathsep) if v.strip()] if env_val else []
        raw_endpoints = DEFAULT_ENDPOINTS + env_items
    endpoints = [CANONICAL] + [os.path.expanduser(p) for p in raw_endpoints]

    if not os.path.isdir(CANONICAL):
        msg = f"[FATAL] 单一真源运行库不存在: {CANONICAL}"
        if as_json:
            print(json.dumps({"ok": False, "error": msg}, ensure_ascii=False))
        else:
            print(msg, file=sys.stderr)
        return 2

    results = [inspect_endpoint(p, CANONICAL) for p in endpoints]

    judged = [r for r in results
              if strict_missing or r["status"] != "MISSING" or r["path"] == CANONICAL]
    all_ok = all(r["status"] == "CONSISTENT" for r in judged)

    if as_json:
        print(json.dumps({"ok": all_ok, "canonical": CANONICAL, "endpoints": results}, ensure_ascii=False, indent=2))
    elif quiet:
        summary = "ALL_CONSISTENT" if all_ok else "HAS_MISMATCH"
        print(f"{summary} ({sum(1 for r in results if r['status']=='CONSISTENT')}/{len(results)} endpoints consistent)")
    else:
        print("=" * 72)
        print(f"chint-pptx 落点一致性核验")
        print(f"单一真源(运行库): {CANONICAL}")
        skipped = [r for r in results if r["status"] == "MISSING" and r["path"] != CANONICAL]
        if skipped and not strict_missing:
            print(f"[WARN] {len(skipped)} 个落点缺失，按未部署跳过（--strict-missing 可判负）:")
            for r in skipped:
                print(f"       {r['path']}")
        print("=" * 72)
        for r in results:
            print()
            print(f"落点: {r['path']}")
            print(f"  形态: {r['form']}")
            if r.get("target") is not None:
                print(f"  -> {r['target']}")
            if r.get("note"):
                print(f"  说明: {r['note']}")
            print(f"  状态: {r['status']}")
            if r["form"] == "realdir" and "file_count_endpoint" in r:
                print(f"  文件数: 落点 {r['file_count_endpoint']} / 运行库 {r['file_count_canonical']}")
            diffs = r.get("diffs", [])
            if diffs:
                print(f"  差异文件 ({len(diffs)}):")
                for d in diffs:
                    if d["kind"] == "MISSING_IN_ENDPOINT":
                        print(f"    [缺失] {d['rel']}  (运行库 sha256={d['canonical_sha256'][:16]})")
                    elif d["kind"] == "EXTRA_IN_ENDPOINT":
                        print(f"    [独占] {d['rel']}  (落点 sha256={d['endpoint_sha256'][:16]})")
                    else:  # CONTENT_DIFF
                        print(f"    [内容不同] {d['rel']}")
                        print(f"        运行库  sha256={d['canonical_sha256'][:32]}")
                        print(f"        落点    sha256={d['endpoint_sha256'][:32]}")
        print()
        print("=" * 72)
        print(f"结论: {'全部一致' if all_ok else '存在不一致'}")

    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
