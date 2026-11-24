# `<Country / Region Standard Override>` (`<region_code>.md`)

> **Physical Isolation Rule (`regions/`)**: Copy to `references/regions/<country>.md` and load **only** when targeting `<Country / Market>` (e.g., North America `UL 489 / UL 1066`, EU/UK `EN / UKCA`, Australia/NZ `AS/NZS`). Keep default `IEC 60947-2:2024` (EN) and `GB/T 14048.2—2020` (ZH) runs isolated from regional overrides.

## 1. Governing Regional Standards & Units

- **Target Jurisdiction**: `{{country_or_region}}`
- **Mandatory Standards**: `{{regional_standards}}`
- **Orthography & Unit Policy**: `{{spelling_and_unit_policy}}` (apply regional spelling or unit conventions strictly within this file's scope).

## 2. Regional Term & Classification Overrides (区域强制替换词)

| Statutory Chinese (`GB/T 14048.2—2020`) | ✅ Regional Canonical English Output (`{{region_code}}`) | Standard Clause / Marking Rule |
| :--- | :--- | :--- |
| `{{zh_term}}` | **`{{regional_en_term}}`** | `{{regional_clause_or_label}}` |

## 3. Regional Compliance Warnings (区域合规红线)

- Claim regional certification or rating compliance strictly when backed by an active test report for `{{country_or_region}}` (`{{missing_report_action}}`).