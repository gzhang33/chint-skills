# MCCB Department Terminology & CHINT Accessory Standard (`mccb.md`)

> **Department Isolation**: MCCB Department only (`NXM`, `NXS`, `NM8`, `NM8N`, `NM5`, `CBR`, `MRCD`, `CBI`, `ICB`, `PV DC`, `CBAR`). Load alongside `SKILL.md` and `iec_60947_2_standard.md`.

## 1. Applicable Series & Session Datasheet References

- **Applicable CHINT Series**: `NXM`, `NXS`, `NM8`, `NM8N`, `NM5` (keep registered series codes verbatim).
- **Primary Standard**: `IEC 60947-2:2024` (Clauses 3–9 & Annexes A–R; `GB/T 14048.2`).
- **Session Datasheets**: Resolve model suffixes, pole counts, and `{{...}}` slots exclusively from datasheets or catalogues supplied by the user in session.

---

## 2. MCCB Department Taxonomy & Protection Terms (双标唯一译法)

> Shared core ratings, `ICB`/`CBR`/`CBI`/`PV`, and $I_r$/$I_{sd}$/$I_i$ definitions live in `iec_60947_2_standard.md` and `iec_annexes.md`. Below are MCCB-specific product terms.

| Statutory Chinese (`GB/T 14048.2—2020`) | ✅ Unique Canonical IEC English (`IEC 60947-2:2024`) | Symbol / Slot | Clause & Usage Note |
| :--- | :--- | :--- | :--- |
| 塑料外壳式断路器 | **`Moulded-case circuit-breaker (MCCB)`** | `MCCB` | `GB/T 14048.2—2020 Cl. 2.6 & 3.3`; `IEC Cl. 3.1` hyphenated `circuit-breaker`. |
| 限流塑料外壳式断路器 | **`Current-limiting moulded-case circuit-breaker`** | $I^2t$ | `IEC 3.3, 3.13` / `GB 2.3, 2.18` (`let-through current` / `cut-off current`). |
| 热磁式过电流脱扣器 | **`Thermal-magnetic overcurrent release (TM)`** | `TM-D` / `TM-A` | `IEC 5.7.1 (2c), 5.7.3` / `GB 4.7.1, 4.7.3` (`+30 °C ± 2 °C`). |
| 电子脱扣器 | **`Electronic trip unit (ETU)`** | `ETU` | `IEC 5.7, Annex F` / `GB 4.7, 附录 F` (`-5 °C` to `+40 °C`, `0.3 %/K`). |
| 人为短延时 | **`Intentional time-delay`** | $t_{sd}$ = `{{tsd_setting: s}}` | `IEC 3.8, 3.17` / `GB 4.4, 图 K.1` (paired with `Selectivity category B` & $I_{cw}$). |
| 接地故障电流整定值 | **`Ground-fault current setting`** | $I_g$ = `{{Ig_setting: ×In}}`, $t_g$ = `{{tg_setting: s}}` | `IEC 8.2.1.2.4 c), Table K.1` / `GB 图 K.1`. |

---

## 3. CHINT MCCB Mounting, Connections & Exclusive Accessories

| CHINT Code / Type | Chinese Term (✅ EN→ZH) | ✅ Unique Canonical IEC English (ZH→EN) | Function, Clause & Value Slots |
| :--- | :--- | :--- | :--- |
| **`F`** | 板前接线（固定式） | **`Front connection (fixed)`** | Standard front busbar or cable-lug termination (`Cl. 4.4`); aluminium terminals marked `AL` / `AL/CU` per `Annex D`. |
| **`HR` / `VR`** | 板后水平接线 / 板后垂直接线 | **`Rear horizontal connection (HR)`** / **`Rear vertical connection (VR)`** | Rear flat busbar or stud connections (`HR` horizontal, `VR` vertical). |
| **Rotatable / Spreaders** | 旋转端子 / 扩展扩散端子 | **`Rotatable terminal pads`** / **`Extended terminal spreaders`** | On-site orientation `{{terminal_rotation_deg: °}}` (state only when documented) / widened pole pitch for large cables. |
| **Plug-in** | 插入式底座 | **`Plug-in base`** | `IEC 3.4, 4.4` / `GB 2.4, 3.7`; rapid replacement without disconnecting main busbars. |
| **Withdrawable** | 抽屉式底座 | **`Withdrawable base`** | `IEC 3.5, 4.4, 8.1.2` / `GB 2.5, 3.7, 7.1.2`; isolating contacts, position indication (`connected / test / disconnected`), and safety shutters. |
| **Rotary Handle** | 旋转操作手柄（本体直接 / 柜门延伸） | **`Direct rotary handle`** / **`Extended door-mounted rotary handle`** | Manual rotary actuator on breaker cover or coupled through enclosure door (`{{handle_ip}}`, `Cl. 4.5`). |
| **`MOD`** | 电动机操作机构 | **`Motor-operator (MOD)`** | Remote electrical closing and opening mechanism (`IEC 4.2, Annex N`); control supply `{{Uc: V}}`. |
| **`SHT` / `UVT`** | 分励脱扣器 / 欠电压脱扣器 | **`Shunt release (SHT)`** / **`Undervoltage release (UVT)`** | `IEC 5.7.1, 8.2.1.2.2–8.2.1.2.3, Annex N`; control supply `{{Uc: V}}`. |
| **`AX` / `AL`** | 辅助触头 / 报警开关 | **`Auxiliary contact (AX)`** / **`Alarm switch (AL)`** | `IEC 5.6` main-contact status / `IEC 3.9` (`GB 2.13`) automatic trip indication (`{{aux_config}}`). |
| **Barriers / Shields** | 相间隔板 / 接线端子罩 / 扩展端子罩 | **`Interphase barrier`** / **`Terminal shield`** (`extended terminal shield`) | Phase-to-phase insulation / terminal IP protection `{{terminal_shield_ip}}` (`Cl. 4.5`). |
| **Lock-out / Contact** | 挂锁装置 / 旋转双断点触头系统 | **`Padlocking device`** (`IEC 3.10` / `GB 2.14` lock-out device) / **`Rotary double-break contact system`** | Locks actuator in open (`O`) position / current-limiting electrodynamic contact architecture (`Cl. 3.3`). |