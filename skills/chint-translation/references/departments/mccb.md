# MCCB Department Terminology & CHINT Accessory Standard (`mccb.md`)

> **Department Isolation**: MCCB Department only (`NXM`, `NXS`, `NM8`, `NM5`, `CBR`, `MRCD`, `CBI`, `ICB`, `PV DC`, `CBAR`). Load alongside `SKILL.md` and `iec_60947_2_standard.md`.

## 1. Applicable Series & Local Workspace Reference Pointers

- **Applicable CHINT Series**: `NXM`, `NXS`, `NM8`, `NM8N`, `NM5` (never transliterate registered series codes).
- **Primary Standard**: `IEC 60947-2:2024` (Clauses 3–9 & Annexes A–R; `GB/T 14048.2`).
- **Local Workspace Reference Paths** (consult on demand for exact model codes, pole configurations, and `{{...}}` datasheet slots):
  - `Projects/5 系列海外导入/` (MCCB parameter definitions, overseas onboarding templates, `NXM-NM5-NM8N` specs)
  - Current series datasheets / catalogues supplied by the user in session

---

## 2. MCCB Taxonomy, Trip Units & Setting Slots (双标唯一译法)

| Statutory Chinese (`GB/T 14048.2—2020`) | ✅ Unique Canonical IEC English (`IEC 60947-2:2024`) | Symbol / Slot | Clause & Usage Note |
| :--- | :--- | :--- | :--- |
| 塑料外壳式断路器 | **`Moulded-case circuit-breaker (MCCB)`** | `MCCB` | `GB/T 14048.2—2020 Cl. 2.6 & 3.3`; `IEC Cl. 3.1` hyphenated `circuit-breaker`. |
| 限流塑料外壳式断路器 | **`Current-limiting moulded-case circuit-breaker`** | $I^2t$ | `IEC 3.3, 3.13` / `GB 2.3, 2.18` (`let-through current` / `cut-off current`). |
| 热磁式过电流脱扣器 | **`Thermal-magnetic overcurrent release (TM)`** | `TM-D` / `TM-A` | `IEC 5.7.1 (2c), 5.7.3` / `GB 4.7.1, 4.7.3` (`+30 °C ± 2 °C`). |
| 电子脱扣器 | **`Electronic trip unit (ETU)`** | `ETU` | `IEC 5.7, Annex F` / `GB 4.7, 附录 F` (`-5 °C` to `+40 °C`, `0.3 %/K`). |
| 瞬时脱扣断路器 | **`Instantaneous trip circuit-breaker (ICB)`** | `ICB` | `Annex O` (`O.1, O.4, Table O.1`: marked `"ICB"`). |
| 具有剩余电流保护的断路器 | **`Circuit-breaker incorporating residual current protection (CBR)`** | `CBR` | `Annex B` (`Type AC`, `Type A`, `Type B`; $I_{\Delta n}$, $I_{\Delta no}$, $I_{\Delta m}$, $\Delta t$, test button `T` not red/green). |
| 无过电流保护要求的断路器 | **`Circuit-breaker not fulfilling the requirements for overcurrent protection (CBI)`** | `CBI-W / X / Y` | `Annex L`: `X`/`Y` in both standards; **`Class W` ($I_{cu}=I_{cw}$) is IEC 2024 only** (国标 2020 暂未收录). |
| 光伏用直流断路器 | **`DC circuit-breaker for use in photovoltaic (PV) applications`** | `PV circuit-breaker` | `Annex P` (up to `1 500 V DC`, `forward and reverse currents` `P.7.2`, `critical DC load current` `9.3.10 / P.8.3.9`). |
| 过载电流整定值 / 脱扣时间 | **`Overload current setting`** / **`Tripping time`** | $I_r$ = `{{Ir_setting: ×In}}` / $t_r$ = `{{tr_setting: s}}` | `IEC 3.16` / `GB 2.21, 图 K.1`. |
| 短时动作电流 / 人为短延时 | **`Short-time pick-up current setting`** / **`Intentional time-delay`** | $I_{sd}$ = `{{Isd_setting: ×Ir}}` / $t_{sd}$ = `{{tsd_setting: s}}` | `IEC 3.8, 3.17` / `GB 4.4, 图 K.1` (requires `Selectivity category B` & $I_{cw}$). |
| 额定瞬时短路电流整定值 | **`Instantaneous short-circuit current setting`** | $I_i$ = `{{Ii_setting: ×In}}` | `IEC 3.15` / `GB 2.20, 图 K.1`. |
| 接地故障电流整定值 / 脱扣时间 | **`Ground-fault current setting`** / **`Tripping time`** | $I_g$ = `{{Ig_setting: ×In}}` / $t_g$ = `{{tg_setting: s}}` | `IEC 8.2.1.2.4 c), Table K.1` / `GB 图 K.1`. |

---

## 3. CHINT MCCB Mounting, Connections & Exclusive Accessories

| CHINT Code / Type | Chinese Term (✅ EN→ZH) | ✅ Unique Canonical IEC English (ZH→EN) | Function, Clause & Value Slots |
| :--- | :--- | :--- | :--- |
| **`F`** | 板前接线（固定式） | **`Front connection (fixed)`** | Standard front busbar or cable-lug termination (`Cl. 4.4`); aluminium terminals marked `AL` / `AL/CU` per `Annex D`. |
| **`HR` / `VR`** | 板后水平 / 板后垂直接线 | **`Rear horizontal connection (HR)`** / **`Rear vertical connection (VR)`** | Rear flat busbar or stud connections (`HR` horizontal, `VR` vertical). |
| **Rotatable / Spreaders** | 旋转端子 / 扩展扩散端子 | **`Rotatable terminal pads`** / **`Extended terminal spreaders`** | On-site orientation `{{terminal_rotation_deg: °}}` (state only when documented) / widened pole pitch for large cables. |
| **Plug-in** | 插入式断路器 / 插入式底座 | **`Plug-in circuit-breaker`** / **`Plug-in base`** | `IEC 3.4, 4.4` / `GB 2.4, 3.7`; rapid replacement without disconnecting main busbars. |
| **Withdrawable** | 抽屉式断路器 / 抽屉式底座 | **`Withdrawable circuit-breaker`** / **`Withdrawable base`** | `IEC 3.5, 4.4, 8.1.2` / `GB 2.5, 3.7, 7.1.2`; isolating contacts, position indication (`connected / test / disconnected`), and safety shutters. |
| **Rotary Handle** | 旋转操作手柄（本体直接 / 柜门延伸） | **`Direct rotary handle`** / **`Extended door-mounted rotary handle`** | Manual rotary actuator on breaker cover or coupled through enclosure door (`{{handle_ip}}`, `Cl. 4.5`). |
| **`MOD`** | 电动机操作机构 | **`Motor-operator (MOD)`** | Remote electrical closing and opening mechanism (`IEC 4.2, Annex N`); control supply `{{Uc: V}}`. |
| **`SHT` / `UVT`** | 分励脱扣器 / 欠电压脱扣器 | **`Shunt release (SHT)`** / **`Undervoltage release (UVT)`** | `IEC 5.7.1, 8.2.1.2.2–8.2.1.2.3, Annex N`; control supply `{{Uc: V}}`. |
| **`AX` / `AL`** | 辅助触头 / 报警开关 | **`Auxiliary contact (AX)`** / **`Alarm switch (AL)`** | `IEC 5.6` main-contact status / `IEC 3.9` (`GB 2.13`) automatic trip indication (`{{aux_config}}`). |
| **Barriers / Shields** | 相间隔板 / 接线端子罩 / 扩展端子罩 | **`Interphase barrier`** / **`Terminal shield`** (`extended terminal shield`) | Phase-to-phase insulation / terminal IP protection `{{terminal_shield_ip}}` (`Cl. 4.5`). |
| **Lock-out / Contact** | 挂锁装置 / 旋转双断点触头系统 | **`Padlocking device`** (`IEC 3.10` / `GB 2.14` lock-out device) / **`Rotary double-break contact system`** | Locks actuator in open (`O`) position / current-limiting electrodynamic contact architecture (`Cl. 3.3`). |

---

## 4. MCCB Audit Blacklist (❌ Mode B 审查拦截与旧稿识别唯一真源)

> Consulted in `Mode B` audit or `EN→ZH` legacy decoding only; mirrored programmatically by [lint_text.py](../../scripts/lint_text.py).

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
