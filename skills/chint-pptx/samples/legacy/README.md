# 旧 34 版式样例（不参与回归）

`generate_all_archetypes_sample.py` 生成的是 2026-11 契约之前的全版式样例。
其中的 ARCH_04、ARCH_16 系、ARCH_29 等 archetype 现已被 `_validate_slide_payload` 拒绝。

保留原因：历史版式的渲染器仍在 `scripts/chint_pptx_engine.py` 中，需要时可用于比对与恢复。
**不要**把它接入 CI 或当作当前契约的样例；当前样例见 `scripts/generate_contract_sample.py`。
