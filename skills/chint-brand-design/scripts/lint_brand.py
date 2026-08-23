#!/usr/bin/env python3
"""
CHINT Brand Governance & Style Linter
Location: skills/chint-brand-design/scripts/lint_brand.py

Automated brand compliance auditing tool:
- Scans files and directories for:
  1. Forbidden decorative emojis (enforcing Minimum UI & zero-emoji rule).
  2. Non-standard blue/accent color codes (recommending official CHINT 2026 tokens).
  3. Font-family fallback stack compliance (verifying 'CHINTinno' and 'Microsoft YaHei' order).
"""

import os
import re
import sys
import argparse
from typing import List, Dict, Tuple

# Common decorative emojis prohibited by Minimum UI rules
FORBIDDEN_EMOJIS = [
    "⚡", "🚀", "💡", "🎉", "📌", "✅", "❌", "⚠️", "🔍", "🔥", "✨",
    "👍", "👏", "🎯", "📊", "📈", "📉", "🛠️", "⚙️", "🌟", "⭐", "✓", "✕",
]

# Non-standard blue hex codes commonly introduced by mistake
NON_BRAND_BLUES = {
    "#0000FF": ("#1E50E6", "Pure Blue -> CHINT Electric Blue"),
    "#1890FF": ("#1E50E6", "Ant Design Blue -> CHINT Electric Blue"),
    "#2F54EB": ("#1E50C8", "Geek Blue -> CHINT Deep Blue"),
    "#0052D9": ("#1E50E6", "Tencent Blue -> CHINT Electric Blue"),
    "#1677FF": ("#1E50E6", "AntD v5 Blue -> CHINT Electric Blue"),
    "#007AFF": ("#1E50E6", "Apple Blue -> CHINT Electric Blue"),
    "#2563EB": ("#1E50E6", "Tailwind Blue-600 -> CHINT Electric Blue"),
    "#3B82F6": ("#2378FF", "Tailwind Blue-500 -> CHINT Bright Blue"),
}


class LintIssue:
    def __init__(self, file_path: str, line_no: int, rule: str, message: str, snippet: str, fix_suggestion: str):
        self.file_path = file_path
        self.line_no = line_no
        self.rule = rule
        self.message = message
        self.snippet = snippet
        self.fix_suggestion = fix_suggestion

    def __str__(self) -> str:
        return (
            f"\n  [RULE: {self.rule}] line {self.line_no}\n"
            f"  Issue:   {self.message}\n"
            f"  Snippet: {self.snippet.strip()}\n"
            f"  Fix:     {self.fix_suggestion}"
        )


def lint_file(file_path: str) -> List[LintIssue]:
    issues: List[LintIssue] = []
    
    # Ignore binary files, fonts, images, pycache, git
    if any(file_path.endswith(ext) for ext in [".ttf", ".png", ".jpg", ".jpeg", ".ico", ".svg", ".pyc", ".pptx"]):
        return issues
    if any(part in file_path for part in [".git", "__pycache__", "node_modules", ".gemini", "assets/fonts"]):
        return issues

    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
    except Exception:
        return issues

    if os.path.basename(file_path) == "lint_brand.py":
        return issues

    for idx, line in enumerate(lines, start=1):
        # 1. Emoji Check
        for emoji in FORBIDDEN_EMOJIS:
            if emoji in line:
                issues.append(
                    LintIssue(
                        file_path=file_path,
                        line_no=idx,
                        rule="MINIMUM_UI_ZERO_EMOJI",
                        message=f"Found decorative emoji '{emoji}' in user-facing copy/code",
                        snippet=line,
                        fix_suggestion="Replace with semantic vector iconography (e.g. lucide-react / SVG) or concise copy.",
                    )
                )
                break

        # 2. Non-Brand Blue Check
        for non_brand, (official, desc) in NON_BRAND_BLUES.items():
            if non_brand.lower() in line.lower():
                issues.append(
                    LintIssue(
                        file_path=file_path,
                        line_no=idx,
                        rule="BRAND_COLOR_CONSISTENCY",
                        message=f"Found non-brand color '{non_brand}' ({desc})",
                        snippet=line,
                        fix_suggestion=f"Replace with official CHINT token '{official}' (#1E50E6 / #50C8FF / #1437AA).",
                    )
                )

        # 3. Font Family Fallback Check (CSS / style lines)
        if ("font-family" in line or "fontFamily" in line) and "CHINTinno" in line:
            if "PingFang SC" in line and "Microsoft YaHei" in line:
                pf_idx = line.find("PingFang SC")
                my_idx = line.find("Microsoft YaHei")
                if pf_idx < my_idx:
                    issues.append(
                        LintIssue(
                            file_path=file_path,
                            line_no=idx,
                            rule="TYPOGRAPHY_FALLBACK_ORDER",
                            message="Font fallback places 'PingFang SC' before 'Microsoft YaHei'",
                            snippet=line,
                            fix_suggestion="Reorder to: 'CHINTinno', 'Microsoft YaHei', 'PingFang SC', '微软雅黑', sans-serif",
                        )
                    )

    return issues


def lint_path(target_path: str) -> Dict[str, List[LintIssue]]:
    all_issues: Dict[str, List[LintIssue]] = {}

    if os.path.isfile(target_path):
        issues = lint_file(target_path)
        if issues:
            all_issues[target_path] = issues
    elif os.path.isdir(target_path):
        for root, _, files in os.walk(target_path):
            for file in files:
                fpath = os.path.join(root, file)
                issues = lint_file(fpath)
                if issues:
                    all_issues[fpath] = issues

    return all_issues


def main():
    parser = argparse.ArgumentParser(description="CHINT Brand Linter & Compliance Auditor")
    parser.add_argument(
        "target",
        nargs="?",
        default=".",
        help="Target file or directory to audit (default: current directory)",
    )
    args = parser.parse_args()

    results = lint_path(args.target)
    total_issues = sum(len(issues) for issues in results.values())

    print("=" * 70)
    print("  CHINT Brand Identity & Visual Compliance Audit Report")
    print("=" * 70)

    if total_issues == 0:
        print("\nAll scanned files strictly adhere to CHINT brand design standards!\n")
        sys.exit(0)

    print(f"\nFound {total_issues} brand design issue(s) across {len(results)} file(s):\n")
    for fpath, issues in results.items():
        print(f"--> File: {fpath} ({len(issues)} issue(s))")
        for issue in issues:
            print(issue)
        print("-" * 70)

    print(f"\nAudit complete: {total_issues} violation(s) need attention.\n")
    sys.exit(1)


if __name__ == "__main__":
    main()
