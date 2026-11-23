# MCCB Department Terminology & CHINT Accessory Standard (`mccb.md`)

> **Department Isolation**: MCCB Department only (`NXM`, `NXS`, `NM8`, `NM5`, `CBR`, `MRCD`, `CBI`, `ICB`, `PV DC`, `CBAR`). Load alongside `SKILL.md` and `iec_60947_2_standard.md`.

## 1. Applicable Series & Local Workspace Reference Pointers

- **Applicable CHINT Series**: `NXM`, `NXS`, `NM8`, `NM8N`, `NM5` (never transliterate registered series codes).
- **Primary Standard**: `IEC 60947-2:2024` (Clauses 3–9 & Annexes A–R; `GB/T 14048.2`).
- **Local Workspace Reference Paths** (consult on demand for exact model codes, pole configurations, and `{{...}}` datasheet slots):
  - `Projects/5 系列海外导入/` (MCCB parameter definitions, overseas onboarding templates, `NXM-NM5-NM8N` specs)
  - Current series datasheets / catalogues supplied by the user in session

---

## 2. MCCB Taxonomy, Trip Units & Setting Slots (一词一译)

| Chinese Term (✅ EN→ZH) | ✅ Unique Canonical IEC English (ZH→EN) | Symbol / Slot | Clause & Usage Note |
| :--- | :--- | :--- | :--- |
| 塑壳断路器（塑料外壳式断路器） | **`Moulded-case circuit-breaker (MCCB)`** | `MCCB` | Industry category term harmonized to `IEC 60947-2:2024` (`moulded case` `Cl. 9.3.3.3`, `moulding` `Cl. 8.1.6`, hyphenated `circuit-breaker` `Cl. 3.1`). |
| 限流塑壳断路器 | **`Current-limiting moulded-case circuit-breaker`** | $I^2t$ | `Cl. 3.3, 3.13, Fig. K.2–K.5` (`let-through current` / admitted `cut-off current`; `let-through energy`). |
| 热磁式脱扣器（固定 / 可调） | **`Thermal-magnetic overcurrent release (TM)`** | `TM-D` / `TM-A` | `Cl. 5.7.1 (2c), 5.7.3` (reference calibration temp `+30 °C ± 2 °C`; `Table 5` $1.05 / 1.30 \times I_{\text{set}}$). |
| 电子式脱扣器（智能脱扣器） | **`Electronic trip unit (ETU)`** | `ETU` | `Cl. 5.7, Annex F` (temperature-independent `-5 °C` to `+40 °C`, `0.3 %/K`). |
| 单磁式脱扣器 / 瞬时脱扣断路器 | **`Instantaneous trip circuit-breaker (ICB)`** | `ICB` | `Annex O` (`O.1, O.4, Table O.1`: short-circuit protection only, marked `"ICB"`, co-ordinated with motor-starters). |
| 带剩余电流保护的塑壳断路器 | **`Circuit-breaker incorporating residual current protection (CBR)`** | `CBR` | `Annex B` (`Type AC`, `Type A`, `Type B`; $I_{\Delta n}$, $I_{\Delta no}$, $I_{\Delta m}$, $\Delta t$, test button `T` not red/green). |
| 不满足过电流保护要求的断路器（无过流保护型） | **`Circuit-breaker not fulfilling the requirements for overcurrent protection (CBI)`** | `CBI-W / X / Y` | `Annex L` (`L.1–L.5, Table L.1`: rated conditional short-circuit current **$I_{cc}$**, correlated to `utilization category AC-22` per `L.4.1`). |
| 光伏直流塑壳断路器 | **`DC circuit-breaker for use in photovoltaic (PV) applications`** | `PV circuit-breaker` | `Annex P` (up to `1 500 V DC`, interrupts `forward and reverse currents` `P.7.2`, `critical DC load current` Seq VII `9.3.10 / P.8.3.9`). |
| 过载长延时整定电流 / 时间 | **`Overload current setting`** / **`Tripping time`** | $I_r$ = `{{Ir_setting: ×In}}` / $t_r$ = `{{tr_setting: s}}` | `Cl. 3.16, Fig. K.1`. |
| 短路短延时整定电流 / 延时 | **`Short-time pick-up current setting`** / **`Intentional time-delay`** | $I_{sd}$ = `{{Isd_setting: ×Ir}}` / $t_{sd}$ = `{{tsd_setting: s}}` | `Cl. 3.8, 3.17, Fig. K.1` (requires `Selectivity category B` & declared $I_{cw}$ per `Cl. 5.4`). |
| 短路瞬时整定电流 | **`Instantaneous short-circuit current setting`** | $I_i$ = `{{Ii_setting: ×In}}` | `Cl. 3.15, Fig. K.1`. |
| 接地故障整定电流 / 延时 | **`Ground-fault current setting`** / **`Tripping time`** | $I_g$ = `{{Ig_setting: ×In}}` / $t_g$ = `{{tg_setting: s}}` | `Cl. 8.2.1.2.4 c), Table K.1, Fig. K.1`. |

---

## 3. CHINT MCCB Mounting, Connections & Exclusive Accessories

| CHINT Code / Type | Chinese Term (✅ EN→ZH) | ✅ Unique Canonical IEC English (ZH→EN) | Function, Clause & Value Slots |
| :--- | :--- | :--- | :--- |
| **`F`** | 板前接线（固定式） | **`Front connection (fixed)`** | Standard front busbar or cable-lug termination (`Cl. 4.4`); aluminium terminals marked `AL` / `AL/CU` per `Annex D`. |
| **`HR` / `VR`** | 板后水平 / 板后垂直接线 | **`Rear horizontal connection (HR)`** / **`Rear vertical connection (VR)`** | Rear flat busbar or stud connections (`HR` horizontal, `VR` vertical). |
| **Rotatable / Spreaders** | 旋转端子 / 扩展扩散端子 | **`Rotatable terminal pads`** / **`Extended terminal spreaders`** | On-site orientation `{{terminal_rotation_deg: °}}` (state only when documented) / widened pole pitch for large cables. |
| **Plug-in** | 插入式安装（插入式底座） | **`Plug-in circuit-breaker`** / **`Plug-in base`** | `Cl. 3.4, 4.4`; rapid replacement without disconnecting main busbars. |
| **Withdrawable** | 抽出式安装（抽屉式底座） | **`Withdrawable circuit-breaker`** / **`Withdrawable base`** | `Cl. 3.5, 4.4, 8.1.2`; isolating contacts, position indication (`connected / test / disconnected`), and safety shutters. |
| **Rotary Handle** | 旋转操作手柄（本体直接 / 柜门延伸） | **`Direct rotary handle`** / **`Extended door-mounted rotary handle`** | Manual rotary actuator on breaker cover or coupled through enclosure door (`{{handle_ip}}`, `Cl. 4.5`). |
| **`MOD`** | 电动操作机构（电操） | **`Motor-operator (MOD)`** | Remote electrical closing and opening mechanism (`Cl. 4.2, Annex N`); control supply `{{Uc: V}}`. |
| **`SHT` / `UVT`** | 分励脱扣器 / 欠电压脱扣器 | **`Shunt release (SHT)`** / **`Undervoltage release (UVT)`** | `Cl. 5.7.1, 8.2.1.2.2–8.2.1.2.3, Annex N`; control supply `{{Uc: V}}`. |
| **`AX` / `AL`** | 辅助触头 / 报警开关 | **`Auxiliary contact (AX)`** / **`Alarm switch (AL)`** | `Cl. 5.6` main-contact status / `Cl. 3.9` automatic trip indication (`{{aux_config}}`). |
| **Barriers / Shields** | 相间隔板 / 接线端子罩（扩展端子罩） | **`Interphase barrier`** / **`Terminal shield`** (`extended terminal shield`) | Phase-to-phase insulation / terminal IP protection `{{terminal_shield_ip}}` (`Cl. 4.5`). |
| **Lock-out / Contact** | 挂锁装置 / 旋转双断点触头系统 | **`Padlocking device`** (`Cl. 3.10` lock-out device) / **`Rotary double-break contact system`** | Locks actuator in open (`O`) position / current-limiting electrodynamic contact architecture (`Cl. 3.3`). |

---

## 4. MCCB Audit Blacklist (❌ Mode B 审查拦截与旧稿识别唯一真源)

> Consulted in `Mode B` audit or `EN→ZH` legacy decoding only; mirrored programmatically by [audit_catalogue.py](../../scripts/audit_catalogue.py).

| ❌ Forbidden / Legacy / Non-IEC Form | Defect Category | ✅ Mandatory Single-Track Replacement |
| :--- | :--- | :--- |
| `Plastic shell breaker` / `Plastic case breaker` | Literal Chinglish | **`Moulded-case circuit-breaker (MCCB)`** |
| `Molded Case Circuit Breaker` / `Molded-case` / `Circuit breaker` (unhyphenated) | North American UL 489 spelling bleed-over | **`Moulded-case circuit-breaker (MCCB)`** / **`circuit-breaker`** |
| `Leakage plastic shell` / `Earth leakage breaker` / `ELCB` | Chinglish / obsolete acronym | **`Circuit-breaker incorporating residual current protection (CBR)`** (`Annex B`) |
| `Motor Circuit Protector (MCP)` / `Non-automatic breaker` | North American UL 489 / vague literal | **`Instantaneous trip circuit-breaker (ICB)`** (`Annex O`) / **`CBI`** (`Annex L`) |
| `Double breaking point` / `Back wiring` / `Insert installation` / `Drawer type` / `Rotate handle` / `Wire cover` / `Motor hand` | Literal Chinglish | **`Rotary double-break contact system`** / **`Rear connection (HR / VR)`** / **`Plug-in base`** / **`Withdrawable base`** / **`Rotary handle`** / **`Terminal shield`** / **`Motor-operator (MOD)`** |
| Claiming `Type F` or `Type B+` compliance under `IEC 60947-2` | Standard scope error (`B.3.4` covers AC/A/B only) | Cite `IEC 62423` / `VDE 0664-400` if `Type F / B+` applies |
| `Category A` combined with `Isd` short-time delay without `Icw` | Technical contradiction (`Cl. 5.4`) | Flag contradiction: intentional short-time delay (`Isd` / `tsd`) requires `Selectivity category B` + declared $I_{cw}$ (or `Seq IV` verification) |

---

## 5. Department Custom Extensions (塑壳产品部自行补充区)

| Added Date | Chinese Term | ✅ Unique Canonical IEC English (with CHINT Code) | Value Slot | ❌ Forbidden Literal | Source / Submitter |
| :--- | :--- | :--- | :--- | :--- | :--- |
| — | *(在此行下方追加塑壳部门新增系列或专属字段)* | — | — | — | — |
