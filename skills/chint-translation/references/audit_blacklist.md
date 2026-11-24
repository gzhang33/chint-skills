# Legacy Decoding & Substantive Mistranslation Blacklist (`audit_blacklist.md`)

> **Conditional Disclosure**: Load during `EN` audit / legacy source decoding or `EN→ZH` statutory redline checks. Core substantive mistranslation, competitor-code, and contradiction rules are programmatically mirrored by [lint_text.py](../scripts/lint_text.py).

## 1. Substantive IEC & Anti-Chinglish Blacklist

| Chinese Term / Rule | ❌ Forbidden Mistranslation / Chinglish | ✅ Unique Canonical Output |
| :--- | :--- | :--- |
| 使用类别误用 | `Use classes` | **`selectivity category`** / **`utilization category`** (`L.4.1`) |
| 分励 / 欠压 / 闭合脱扣器 | `Shunting release`, `Shunt opening release`, `Excitation release`, `Shunt Trip`, `Lack voltage`, `Closing magnet` | **`shunt release`**, **`undervoltage release`**, **`closing release`** *(IEC 3.19 / GB 2.23 admits synonym `closing coil`; Annex N/R uses lowercase `shunt trip` descriptively)* |
| 万次换算 | `N ten thousand times` | Plain integer `operating cycles` |
| 通用工程术语错译 | `Installation and debugging`, `Matters need attention`, `Ordering instruction`, `Wrong action / Error work`, `No tolerance specified` | **`installation and commissioning`**, **`operating precautions`**, **`ordering information`**, **`false tripping`** *(normative IEC uses **`unwanted tripping`** per `B.7.2.8` / **`unintentional tripping`** per `F.3.2`, and `unintentional operation` per `B.8.1.2.1`)*, **`unspecified linear tolerance`** |
| `GB/T 14048.2—2020` 法定中文红线 (`EN→ZH` / `--mode zh`) | `抽出式断路器`、`塑壳断路器`、`万能式断路器`、`使用类别 A/B`、`功率损耗`、`结构差异`、`合闸涌流脱扣器`、`闭合电磁铁 / 合闸电磁铁 / 释能电磁铁`、`分离位置`、`Inm`、`漏电保护`、`漏电互感器` | **`抽屉式断路器`**、**`塑料外壳式断路器`**、**`空气断路器（分类：万能式）`** *(`GB 2.7 + 3.3`)*、**`选择性类别 A / B`** *(`使用类别 AC-22` 属 `L.4.1` 合法项)*、**`功耗`**、**`结构段`**、**`接通电流脱扣器`**、**`闭合脱扣器`**、**`隔离位置`** *(`GB 7.1.2`；`2.5` 称`抽出位置`)*、**`壳架等级`**、**`剩余电流保护`** *(`附录 B/R`)*、**`电流传感器`** *(`附录 B/M`；产品扩展可用「剩余电流互感器」)* |

## 2. ACB Substantive Blacklist

| ❌ Forbidden / Legacy / Non-IEC Form | Defect Category | ✅ Mandatory Single-Track Replacement |
| :--- | :--- | :--- |
| `Closed electromagnet` / `Close electromagnet` / `Closing magnet` | Raw ERP/legacy manual grammar error | **`Closing release (CEM)`** (`Cl. 3.19`) |
| `Earch current transformer` | Raw ERP typo in local SKU sheet | **`Earth current transformer (ECT)`** |
| `Draw-out Type Interphased Partition` / `Inter phased partition` / `Phase space plate` | Raw ERP Chinglish & non-word `interphased` | **`Withdrawable / Fixed interphase barrier (DD / FD)`** |
| `under voltage delay release-zero` | Raw ERP literal string | **`Loss-of-voltage time-delay release (UVTZ)`** |
| `Closing Preparation Contact` | Raw ERP literal translation | **`Ready-to-close contact (SPC)`** |
| `Drawer` / `Drawer type` / `Drawer box` / `Drawer seat` | Chinglish / legacy manual noun | **`Withdrawable`** / **`Withdrawable cradle`** |
| `Separation position` / `Connection position` | Legacy manual non-IEC position names | **`Disconnected position`** (`Cl. 8.1.2`) / **`Connected position`** (*Industry*) |
| `hole opener` / `Face mask` / `Storage hole` / `Body key lock` | Legacy Chinglish | **`panel hole saw`** / **`Door escutcheon`** / **`Racking handle storage slot`** / **`Key lock (KL)`** |
| `refuses to open` / `is forbidden to open` / `irrelevant to` / `belong to the pulse energization working mode` | Legacy manual Chinglish syntax | `does not trip`, `cannot be opened`, `independent of`, `operate on a pulse-energization duty` |
| `MX`, `MN`, `XF`, `OF`, `SDE`, `PF`, `MCH`, `YO`, `KLC` | Competitor (Schneider/ABB) accessory codes | Official CHINT codes (`SHT`, `UVT`, `CEM`, `AX`, `AL`, `SPC`, `MOD`, `KL`) |
| `Universal Circuit Breaker`, `intelligent air circuit-breaker`, `LVPCB` | Literal Chinglish / non-standard alias | **`Air circuit-breaker (ACB)`** *(for `Universal Circuit Breaker` / `LVPCB`)*, **`Air circuit-breaker with electronic trip unit`** |

## 3. MCCB Substantive Blacklist

| ❌ Forbidden / Legacy / Non-IEC Form | Defect Category | ✅ Mandatory Single-Track Replacement |
| :--- | :--- | :--- |
| `Plastic shell breaker` / `Plastic case breaker` | Literal Chinglish | **`Moulded-case circuit-breaker (MCCB)`** |
| `Leakage plastic shell` / `Earth leakage breaker` / `ELCB` | Chinglish / obsolete acronym | **`Circuit-breaker incorporating residual current protection (CBR)`** (`Annex B`) |
| `Motor Circuit Protector (MCP)` / `Non-automatic breaker` | North American UL 489 / vague literal | **`Instantaneous trip circuit-breaker (ICB)`** (`Annex O`) / **`CBI`** (`Annex L`) |
| `Double breaking point` / `Back wiring` / `Insert installation` / `Rotate handle` / `Wire cover` / `Motor hand` | Literal Chinglish | **`Rotary double-break contact system`** / **`Rear connection (HR / VR)`** / **`Plug-in base`** / **`Rotary handle`** / **`Terminal shield`** / **`Motor-operator (MOD)`** |
| Claiming `Type F` or `Type B+` compliance under `IEC 60947-2` | Standard scope error (`B.3.4` covers AC/A/B only) | Cite `IEC 62423` / `VDE 0664-400` if `Type F / B+` applies |
| `Category A` combined with `Isd` short-time delay without `Icw` | Technical contradiction (`Cl. 5.4`) | Flag contradiction: `Category A` with intentional short-time delay (`Isd` / `tsd`) requires a declared $I_{cw}$ verified by Test Sequence IV (or `Selectivity category B` + Table 2 $I_{cw}$) (`IEC 5.4 / GB 4.4`) |
