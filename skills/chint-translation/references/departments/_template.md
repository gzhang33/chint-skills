# `<Department / Product Line Name>` Translation & Terminology Extension (`<dept_id>.md`)

> **Isolation Rule (`1 + 1 + N`)**: Create one file per independent product department under `references/departments/`. Copy to `references/departments/<dept_code>.md`, register the department option in `SKILL.md` Step 1, add `<dept_code>` to `--dept` `choices` in `scripts/lint_text.py` and `scripts/glossary_lookup.py`, and keep this template file excluded from runtime runs.

## 0. Value-Slot & Single-Track Rule

- Express every rating as a slot `{{param_name: unit}}` resolved from the exact model's datasheet; store zero product specifications here.
- Enforce **one canonical IEC English output** per Chinese term (`Canonical IEC Term (CHINT Code)` when a CHINT code exists). Add legacy OEM errors, US/UL terms, and competitor codes strictly to [audit_blacklist.md](../audit_blacklist.md).

---

## 1. Applicable Series & Session Datasheet References

- **Applicable CHINT Series** (routing only): `{{series_codes}}`
- **Primary IEC Standard**: `IEC {{standard_number}}:{{year}}` (`GB/T {{gbt_number}}—{{year}}`)
- **Session Datasheets**: Resolve exact SKU codes, wiring labels, and ratings exclusively from user-supplied datasheets in the active session.

---

## 2. Core Taxonomy, Protection & Parameter Terms (一词一译主表)

| Statutory Chinese (`GB/T ...`) | ✅ Unique Canonical IEC English (`IEC ...`) | Symbol / Slot | Clause & Usage Note |
| :--- | :--- | :--- | :--- |
| `示例中文术语` | **`Canonical IEC English term`** | `{{slot: unit}}` | `IEC ... Cl. x.y` |

---

## 3. CHINT Exclusive Accessories, Mounting & Sentence Frames (正泰专属附件与句式)

| CHINT Code | Chinese Term | ✅ Unique Canonical IEC English (with CHINT Code) | Function, Clause & Value Slots |
| :--- | :--- | :--- | :--- |
| `CODE` | `附件中文名` | **`Canonical name (CODE)`** | Functional description with `{{param: unit}}`. |