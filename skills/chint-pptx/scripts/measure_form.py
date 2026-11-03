#!/usr/bin/env python3
"""chint-pptx 测定层（S2）—— 薄 CLI 壳。

测定核心已迁入 core.analyzer（S2 完成）；本文件仅保留 CLI 契约并转发到 core.analyzer，
不再承载任何判定逻辑。任何对测定行为的改动都应发生在 core.analyzer / spec/2026VI.yaml。

用法（与原 measure_form.py 等价）：
    python3 measure_form.py <source.pptx> [--out DIR] [--spec PATH] [--deck NAME]
"""
from __future__ import annotations

import pathlib
import sys

# 让 `from core.analyzer import ...` 与 `from verify_preserve_source import ...` 都能解析：
# skill 根目录（core/ 包所在）与 scripts/（verify_preserve_source 所在）都必须在 path 上。
_HERE = pathlib.Path(__file__).resolve().parent                      # scripts/
_SKILL = _HERE.parent                                               # skill 根
for _p in (str(_SKILL), str(_HERE)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from core.analyzer import (                                        # noqa: E402
    measure_deck,
    load_spec,
    SPEC_DEFAULT,
    build_decisions,
    main,
    measure_page,
    render_luminance,
    classify,
    T,
    markers,
)


if __name__ == "__main__":
    sys.exit(main())
