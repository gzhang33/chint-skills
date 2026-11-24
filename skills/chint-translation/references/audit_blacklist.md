# Branch B & Legacy Decoding Blacklist (`audit_blacklist.md`)

> **Conditional Disclosure**: Load **only** during `Branch B` errata audits or `EN→ZH` legacy decoding. Programmatically mirrored by [lint_text.py](../scripts/lint_text.py).

## 1. Universal IEC & Anti-Chinglish Blacklist

| Chinese Term / Rule | ❌ Forbidden Legacy / Chinglish / US Form | ✅ Unique Canonical IEC Output |
| :--- | :--- | :--- |
| 断路器 / 塑壳 / 铝 / 颜色 / 样本 | `Circuit breaker` (unhyphenated), `Molded`, `Aluminum`, `Color`, `Catalog` | **`circuit-breaker`**, **`moulded`**, **`aluminium`**, **`colour`**, **`catalogue`** |
| 使用类别 / 通电激励 / 接地 | `Use classes`, `Energise` / `Energised`, `Utilisation`, `earth-fault` | **`utilization category`** (`L.4.1`), **`energize` / `energized` / `energization`**, **`ground-fault`** (`G-stage`) / **`earth fault`** (`Annex B`) |
| 选择性 / 后备保护 / 闭锁 / 动作值 | `Discrimination`, `Backup`, `Lockout`, `Pickup`, `under-voltage` / `under voltage` | **`selectivity`**, **`back-up`**, **`lock-out`**, **`pick-up`**, **`undervoltage`** |
| 分励 / 欠压 / 闭合脱扣器 | `Shunting release`, `Shunt opening release`, `Shunt Trip`, `Lack voltage`, `Closing magnet` | **`shunt release`**, **`undervoltage release`**, **`closing release`** |
| 机械/电寿命（N 万次） | `Mechanical/Electrical durability`, `N ten thousand times`, `times` | **`operational performance without/with current`** (`{{ops: operating cycles}}`) / **`endurance`** (`Annex B/M/R`) |
| 基准 / 安装面 / 未注公差 | `Base`, `Install surface`, `No tolerance specified` | **`datum`**, **`mounting surface`**, **`unspecified linear tolerance`** |
| 安装调试 / 注意事项 / 订货须知 | `Installation and debugging`, `Matters need attention`, `Ordering instruction` | **`installation and commissioning`**, **`operating precautions`**, **`ordering information`** |
| 小电流测量下限 / 误动作 | `Below X, measurement is inaccurate`, `Wrong action / Error work` | **`Measurement unspecified below {{metering_threshold: A}}`**, **`false tripping`** (`nuisance tripping`) |
| GB/T 法定中文红线 (`EN→ZH`) | `抽出式断路器`、`塑壳断路器`、`万能式断路器`、`使用类别 A/B`、`功率损耗`、`结构差异`、`合闸涌流脱扣器`、`闭合电磁铁` | **`抽屉式断路器`**、**`塑料外壳式断路器`**、**`空气断路器（分类：万能式）`**、**`选择性类别 A / B`**、**`功耗`**、**`结构段`**、**`接通电流脱扣器`**、**`闭合脱扣器`** |

## 2. ACB Audit Blacklist

| ❌ Forbidden / Legacy / Non-IEC Form | Defect Category | ✅ Mandatory Single-Track Replacement |
| :--- | :--- | :--- |
| `Closed electromagnet` / `Close electromagnet` / `Closing magnet` | Raw ERP/legacy manual grammar error | **`Closing release (CEM)`** (`Cl. 3.19`) |
| `Earch current transformer` | Raw ERP typo in local SKU sheet | **`Earth current transformer (ECT)`** |
| `Draw-out Type Interphased Partition` / `Inter phased partition` / `Phase space plate` | Raw ERP Chinglish & non-word `interphased` | **`Withdrawable / Fixed interphase barrier (DD / FD)`** |
| `under voltage delay release-zero` | Raw ERP literal string | **`Loss-of-voltage time-delay release (UVTZ)`** |
| `Closing Preparation Contact` | Raw ERP literal translation | **`Ready-to-close contact (SPC)`** |
| `Drawer` / `Drawer type` / `Drawer box` / `Drawer seat` | Chinglish / legacy manual noun | **`Withdrawable`** / **`Withdrawable cradle`** |
| `Separation position` / `Connection position` | Legacy manual non-IEC position names | **`Disconnected position`** / **`Connected position`** (`Cl. 8.1.2`) |
| `hole opener` / `Face mask` / `Storage hole` / `Body key lock` | Legacy Chinglish | **`panel hole saw`** / **`Door escutcheon`** / **`Racking handle storage slot`** / **`Key lock (KL)`** |
| `refuses to open` / `is forbidden to open` / `irrelevant to` / `belong to the pulse energization working mode` | Legacy manual Chinglish syntax | `does not trip`, `cannot be opened`, `independent of`, `operate on a pulse-energization duty` |
| `MX`, `MN`, `XF`, `OF`, `SDE`, `PF`, `MCH`, `YO`, `KLC` | Competitor (Schneider/ABB) accessory codes | Official CHINT codes (`SHT`, `UVT`, `CEM`, `AX`, `AL`, `SPC`, `MOD`, `KL`) |
| `Universal Circuit Breaker`, `intelligent air circuit-breaker`, `LVPCB`, `Ig indicator light` | Literal Chinglish / non-standard alias | **`Air circuit-breaker (ACB)`**, **`Air circuit-breaker with electronic trip unit`**, **`Ig indicator`** |

## 3. MCCB Audit Blacklist

| ❌ Forbidden / Legacy / Non-IEC Form | Defect Category | ✅ Mandatory Single-Track Replacement |
| :--- | :--- | :--- |
| `Plastic shell breaker` / `Plastic case breaker` | Literal Chinglish | **`Moulded-case circuit-breaker (MCCB)`** |
| `Molded Case Circuit Breaker` / `Molded-case` / `Circuit breaker` (unhyphenated) | North American UL 489 spelling bleed-over | **`Moulded-case circuit-breaker (MCCB)`** / **`circuit-breaker`** |
| `Leakage plastic shell` / `Earth leakage breaker` / `ELCB` | Chinglish / obsolete acronym | **`Circuit-breaker incorporating residual current protection (CBR)`** (`Annex B`) |
| `Motor Circuit Protector (MCP)` / `Non-automatic breaker` | North American UL 489 / vague literal | **`Instantaneous trip circuit-breaker (ICB)`** (`Annex O`) / **`CBI`** (`Annex L`) |
| `Double breaking point` / `Back wiring` / `Insert installation` / `Drawer type` / `Rotate handle` / `Wire cover` / `Motor hand` | Literal Chinglish | **`Rotary double-break contact system`** / **`Rear connection (HR / VR)`** / **`Plug-in base`** / **`Withdrawable base`** / **`Rotary handle`** / **`Terminal shield`** / **`Motor-operator (MOD)`** |
| Claiming `Type F` or `Type B+` compliance under `IEC 60947-2` | Standard scope error (`B.3.4` covers AC/A/B only) | Cite `IEC 62423` / `VDE 0664-400` if `Type F / B+` applies |
| `Category A` combined with `Isd` short-time delay without `Icw` | Technical contradiction (`Cl. 5.4`) | Flag contradiction: intentional short-time delay (`Isd` / `tsd`) requires `Selectivity category B` + declared $I_{cw}$ |