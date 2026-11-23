# `<Country / Region Standard Override>` (`<region_code>.md`)

> **Physical Isolation Rule (`regions/`)**: Loaded **only** when the user explicitly targets `<Country / Market>` (e.g. North America `UL 489 / UL 1066`, EU/UK `EN / UKCA`, Australia/NZ `AS/NZS`). Never merge into default `IEC 60947-2:2024` (EN) or `GB/T 14048.2—2020` (ZH) deliverables.

## 1. Governing Regional Standards & Units

- **Target Jurisdiction**: `{{country_or_region}}`
- **Mandatory Standards**: `{{regional_standards}}`
- **Orthography & Unit Policy**: `{{spelling_and_unit_policy}}` (default IEC uses UK + Oxford `-ize`; apply regional spelling or unit system strictly within this file's scope).

## 2. Regional Term & Classification Overrides (区域强制替换词)

| Statutory `IEC 60947-2:2024` / `GB/T 14048.2—2020` Concept | ✅ Required Regional Output | Standard Clause / Marking Rule |
| :--- | :--- | :--- |
| `{{concept}}` | **`{{regional_term}}`** | `{{regional_clause_or_label}}` |

## 3. Regional Compliance Warnings (区域合规红线)

- Never claim certification or rating compliance without an active test report for the target region (`{{missing_report_action}}`).
