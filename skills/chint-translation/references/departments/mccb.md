# MCCB Department Terminology & CHINT Accessory Standard (`mccb.md`)

> **Department Isolation**: MCCB Department only (`NXM`, `NXS`, `NM8`, `NM8N`, `NM5`, `CBR`, `MRCD`, `CBI`, `ICB`, `PV DC`, `CBAR`). Load alongside `SKILL.md` and `iec_60947_2_standard.md`.

## 1. Applicable Series & Session Datasheet References

- **Applicable CHINT Series**: `NXM`, `NXS`, `NM8`, `NM8N`, `NM5` (keep registered series codes verbatim).
- **Primary Standard**: `IEC 60947-2:2024` (Clauses 1–9 & Annexes A–R, I/Q vacant; `GB/T 14048.2—2020`).
- **Session Datasheets**: Resolve model suffixes, pole counts, and `{{...}}` slots exclusively from session datasheets or catalogues.

---

## 2. MCCB Department Taxonomy & Protection Terms (双标唯一译法)

> Shared core ratings, `ICB`/`CBR`/`CBI`/`PV`, and $I_r$/$I_{sd}$/$I_i$ definitions live in `iec_60947_2_standard.md` and `iec_annexes.md`.

<!-- AUTO:BEGIN mccb/§2 -->
| Chinese Term (`GB/T 14048.2—2020` / *Industry*) | ✅ Unique Canonical IEC English (`IEC 60947-2:2024`) | Symbol / Slot | Clause & Usage Note |
| :--- | :--- | :--- | :--- |
| 塑料外壳式断路器 | **`Moulded-case circuit-breaker (MCCB)`** | `MCCB` | `GB/T 14048.2—2020 Cl. 2.6 & 3.3`; `IEC Cl. 3.1`. |
| 限流塑料外壳式断路器 | **`Current-limiting moulded-case circuit-breaker`** | $I^2t$ | `IEC 3.3, 3.13` / `GB 2.3 + 2.6, 2.18` (composite; `let-through current` / `cut-off current`). |
| 热磁脱扣器 | **`Thermal-magnetic overcurrent release (TM)`** | `TM-D / TM-A` | `IEC 5.7.1 (2c), 5.7.3` / `GB 4.7.1, 4.7.3, 7.1.6 b)` (`+30℃ ± 2℃`; ambient-compensated thermal band $\ge \pm 10\text{ K}$ within `0.3 %/K` per `IEC 8.2.1.2.4 b) 2), 9.3.4.2.3 b)` / `GB 7.2.1.2.4 b) 2), 8.3.3.2.3 b)`). |
| 电子脱扣器 | **`Electronic trip unit (ETU)`** | `ETU` | `IEC 5.7, 5.7.3, 8.1.6, 9.3.6.2, Annex F` / `GB 8.3.3.2.1, 8.3.3.2.3 b), 8.3.5.2, 表 9b/9c` (`GB 7.1.6` 用「电子脱扣装置/单元」，`附录 F` 用「电子装置/控制器」; `ETU` is *Industry* abbr.). |
| 人为短延时 | **`Intentional time-delay`** | $t_{sd}$ = `{{tsd_setting: s}}` | `IEC 3.8, 3.17, 5.4, Table K.1` / `GB 4.4, 2.12, 表 K.1, 图 K.1` (`GB 4.4` 称「人为短延时」，`2.12` 称「短延时短路脱扣器」，`表 K.1` 称 `Isd`「短时动作电流」/ `tsd`「相应脱扣时间」，`图 K.1` 标 `ST`「短延时」; typically `Selectivity category B` + `IEC Table 2 / GB 表 3` $I_{cw}$; `Category A` permitted with declared $I_{cw}$ verified by Seq IV per `IEC 5.4 / GB 4.4, 8.3.6`). |
| 接地故障电流整定值 | **`Ground-fault current setting`** | $I_g$ = `{{Ig_setting: ×In}}`, $t_g$ = `{{tg_setting: s}}` | `IEC 8.2.1.2.4 c)` (*IEC 2024 only*), `Table K.1, Fig. K.1` / `GB 表 K.1, 图 K.1`. |
<!-- AUTO:END mccb/§2 -->

---

## 3. CHINT MCCB Mounting, Connections & Exclusive Accessories

<!-- AUTO:BEGIN mccb/§3 -->
| CHINT Code / Type | Chinese Term (✅ EN→ZH) | ✅ Unique Canonical IEC English (ZH→EN) | Function, Clause & Value Slots |
| :--- | :--- | :--- | :--- |
| **`F`** | 板前接线（固定式） | **`Front connection (fixed)`** | Front busbar/cable-lug termination (`IEC 4.4 / GB 3.7`); Al terminals marked `AL` / `AL/CU` (`IEC D.5.2`) or `AL` / `CU/AL` (`GB D.5.2`). |
| **`HR` / `VR`** | 板后水平接线 / 板后垂直接线 | **`Rear horizontal connection (HR)`** / **`Rear vertical connection (VR)`** | Rear flat busbar or stud connections (`HR` horizontal, `VR` vertical). |
| **Rotatable / Spreaders** | 旋转端子 / 扩展扩散端子 | **`Rotatable terminal pads`** / **`Extended terminal spreaders`** | On-site orientation `{{terminal_rotation_deg: °}}` / widened pole pitch for large cables. |
| **Plug-in** | 插入式底座 | **`Plug-in base`** | `IEC 3.4, 4.4` / `GB 2.4, 3.7`; rapid replacement without disconnecting main busbars. |
| **Withdrawable** | 抽屉式底座 | **`Withdrawable base`** | `IEC 3.5, 4.4, 8.1.2` / `GB 2.5, 3.7, 7.1.2`; `disconnected position` (`隔离位置`; `connected / test` and `safety shutters` are *Industry*). |
| **Rotary Handle** | 旋转操作手柄（本体直接） / 柜门延伸旋转操作手柄 | **`Direct rotary handle`** / **`Extended door-mounted rotary handle`** | Manual rotary actuator on breaker cover or coupled through door (`{{handle_ip}}`, `IEC 4.5 / GB 3.8`). |
| **`MOD`** | 电动机操作机构 | **`Motor-operator (MOD)`** | Remote electrical closing & opening (`IEC 4.2, Annex N / GB 3.4, 表 13 (4.1), 附录 N`); `{{Uc: V}}`. |
| **`SHT` / `UVT`** | 分励脱扣器 / 欠电压脱扣器 | **`Shunt release (SHT)`** / **`Undervoltage release (UVT)`** | `IEC 5.7.1, 8.2.1.2.2–8.2.1.2.3, Annex N / GB 4.7.1, 7.2.1.2.2–7.2.1.2.3, 附录 N`; `{{Uc: V}}`. |
| **`AX` / `AL`** | 辅助触头 / 报警开关 | **`Auxiliary contact (AX)`** / **`Alarm switch (AL)`** | `IEC 5.6, Table 4 (4.4) / GB 4.6, 表 13 (4.4)` (`○`/`│` per `表 13 (1.3)`) main-contact status / `IEC 3.9` (`GB 2.13`) automatic trip indication (`{{aux_config}}`). |
| **Barriers / Shields** | 相间隔板 / 接线端子罩 / 扩展端子罩 | **`Interphase barrier`** / **`Terminal shield`** / **`Extended terminal shield`** | Phase-to-phase insulation / terminal IP protection `{{terminal_shield_ip}}` (`IEC 4.5 / GB 3.8`). |
| — | 挂锁装置 / 旋转双断点触头系统 | **`Padlocking device`** (`IEC 3.10 / GB 2.14` `闭锁装置`; `挂锁装置` is *Industry*) / **`Rotary double-break contact system`** | Locks actuator in `O` position / current-limiting electrodynamic contact architecture (`IEC 3.3 / GB 2.3`). |
<!-- AUTO:END mccb/§3 -->
