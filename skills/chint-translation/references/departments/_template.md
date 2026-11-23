# `<Department / Product Line Name>` Translation & Terminology Extension (`<dept_id>.md`)

> **Isolation Rule (`1 + 1 + N`)**: One file per independent product department under `references/departments/`. Never merge two departments into one file, and never load this template during normal translation runs. Copy to `references/departments/<dept_code>.md` and register one row in `SKILL.md` §2.

## 0. Value-Slot & Single-Track Rule

- Every product rating is a slot `{{param_name: unit}}` resolved from the exact model's datasheet; store zero product specifications here.
- Enforce **one canonical IEC English output** per Chinese term (`Canonical IEC Term (CHINT Code)` when a CHINT code exists). Place legacy OEM errors, US/UL terms, and competitor codes strictly in §4 (`❌ Audit Blacklist`).

---

## 1. Applicable Series & Local Workspace Reference Pointers

- **Applicable CHINT Series** (routing only): `{{series_codes}}`
- **Primary IEC Standard**: `IEC {{standard_number}}` (`GB/T {{gbt_number}}`)
- **Local Workspace Reference Paths** (consult on demand for exact SKU codes, wiring labels, and datasheet values; never copy unreviewed ERP typos):
  - `Areas/样本册修改/{{product_line}}/参考资料/`
  - `Projects/{{project_folder}}/`

---

## 2. Core Taxonomy, Protection & Parameter Terms (一词一译主表)

| Chinese Term (✅ EN→ZH Anchor) | ✅ Unique Canonical IEC English (ZH→EN Output) | Symbol / Slot | IEC Clause / Note |
| :--- | :--- | :--- | :--- |
| `示例中文术语` | **`Canonical IEC English term`** | `{{slot: unit}}` | `IEC ... Cl. x.y` |

---

## 3. CHINT Exclusive Accessories, Mounting & Sentence Frames (正泰专属附件与句式)

| CHINT Code | Chinese Term | ✅ Unique Canonical IEC English (with CHINT Code) | Function & Value Slots |
| :--- | :--- | :--- | :--- |
| `CODE` | `附件中文名` | **`Canonical name (CODE)`** | Functional description with `{{param: unit}}`. |

---

## 4. Department Audit Blacklist (❌ 严禁中译英输出 · 仅供审查拦截与旧稿识别)

| ❌ Forbidden / Legacy / Non-IEC Form | Why Forbidden | ✅ Replace With |
| :--- | :--- | :--- |
| `Example literal / competitor / US term` | Chinglish / UL bleed-over / competitor code | **`Canonical IEC term`** |

---

## 5. Department Custom Extensions (部门自行补充区)

> Product managers of this department may append series-specific field names, new accessory codes, or project terms directly to the table below without modifying `SKILL.md` or `iec_60947_2_standard.md`.

| Added Date | Chinese Term | ✅ Unique Canonical IEC English (with CHINT Code) | Value Slot | ❌ Forbidden Literal | Source / Submitter |
| :--- | :--- | :--- | :--- | :--- | :--- |
| — | *(在此行下方追加本部门新增词条)* | — | — | — | — |
