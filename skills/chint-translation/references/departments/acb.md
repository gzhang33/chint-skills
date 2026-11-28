# ACB Department Terminology & CHINT Accessory Standard (`acb.md`)

> **Department Isolation**: ACB Department only (`NXA`, `NA8`, `NA1`). Load alongside `SKILL.md` and `iec_60947_2_standard.md`.

## 1. Applicable Series & Session Datasheet References

- **Applicable CHINT Series**: `NXA` (Kunlun series), `NA8`, `NA1` (keep registered series codes verbatim).
- **Primary Standard**: `IEC 60947-2:2024` (`GB/T 14048.2—2020`).
- **Session Datasheets**: Resolve exact SKU codes (`{{code}}{{frame}}-A1 {{voltage_code}} {{duty_code}}`) and `{{...}}` slots solely from session datasheets or catalogues.

---

## 2. ACB Product Taxonomy, Electronic Trip Units & Protection (双标唯一译法)

<!-- AUTO:BEGIN acb/§2 -->
| Chinese Term (`GB/T 14048.2—2020` / *Industry & CHINT*) | ✅ Unique Canonical IEC English (`IEC 60947-2:2024`) | Symbol / Slot | Clause & Usage Note |
| :--- | :--- | :--- | :--- |
| 空气断路器（分类：万能式） | **`Air circuit-breaker (ACB)`** | `ACB` | `GB/T 14048.2—2020 Cl. 2.7 & 3.3`; `IEC Cl. 3.1`. |
| 抽屉式断路器 / 固定式断路器 | **`Withdrawable air circuit-breaker`** / **`Fixed air circuit-breaker`** | — | `IEC 3.5, 4.4, 8.1.2` / `GB 2.5, 3.7, 7.1.2` (`固定式`: `GB 3.7`). |
| 配电子式过电流脱扣器的空气断路器 | **`Air circuit-breaker with electronic trip unit`** | — | `IEC 8.1.6, 9.3.6.2, Annex F` / `GB 7.1.6, 8.3.5.2, 附录 F` (composite; `GB 1.1` `电子式过电流保护断路器`). |
| 电子脱扣器 | **`Electronic trip unit (ETU)`** | `ETU` | `IEC 5.7, 8.1.6, 9.3.6.2, Annex F` / `GB 8.3.3.2.1, 8.3.3.2.3 b), 8.3.5.2, 表 9b/9c` (`GB 7.1.6` 用「电子脱扣装置/单元」，`附录 F` 用「电子装置/控制器」; `ETU` is *Industry* abbr.). |
| 基本配电型脱扣器 / 电流表型脱扣器 / 功率型脱扣器 / 谐波型脱扣器 | **`Basic distribution trip unit (M type)`** / **`Ammeter trip unit (A type)`** / **`Power monitoring trip unit (P type)`** / **`Harmonic analysis trip unit (H type)`** | `M / A / P / H` | *CHINT* extension; readable regardless of CB state (`IEC 5.7.3 / GB 4.7.3`); PLC I/O (`IEC 8.1.8 / GB 7.1.8`). |
| 过载长延时保护 | **`Long-time overload protection (L)`** | $I_r$ = `{{Ir_setting: ×In}}`, $t_r$ = `{{tr_setting: s}}` | *Industry* composite (`IEC 3.16, 5.7.1 (2c), Table 5, Fig. K.1` / `GB 2.21, 4.7.1 2)c), 表 6, 图 K.1` — `GB 2.21` 称「过载电流整定值」，`表 6` 称「反时限过电流断开脱扣器」，`图 K.1` 标「LT 长延时」). |
| 短路短延时保护 | **`Short-time delay short-circuit protection (S)`** | $I_{sd}$ = `{{Isd_setting: ×Ir}}`, $t_{sd}$ = `{{tsd_setting: s}}` | *Industry* composite (`IEC 3.8, 3.17, 3.13, Table K.1` / `GB 2.12, 2.18, 表 K.1, 图 K.1` — `GB 2.12` 称「短延时短路脱扣器」，`表 K.1` 称「短时动作电流」，`图 K.1` 标「ST 短延时」); state upper cap separately. |
| 短路瞬时保护 | **`Instantaneous short-circuit protection (I)`** | $I_i$ = `{{Ii_setting: ×In}}`, $t_i$ = `{{ti_max: ms}}` | *Industry* composite (`IEC 3.7, 3.12, 3.15` / `GB 2.11, 2.16, 2.20, 图 K.1` — `GB 2.11` 称「短路脱扣器」，`2.20` 称「额定瞬时短路电流整定值」，`图 K.1` 标「INST 瞬时」; plus `OFF` if supported). |
| 接地故障保护 | **`Ground-fault protection (G)`** | $I_g$ = `{{Ig_setting: ×In}}`, $t_g$ = `{{tg_setting: s}}` | *Industry* term (`IEC 5.7.1 (2d), 8.2.1.2.4 c)` *IEC 2024 only*, `Table K.1, Fig. K.1` / `GB 表 K.1, 图 K.1` `GF 接地故障`); `CI-A/B` (`IEC 60947-1:2020 Annex T`). |
| 剩余电流保护 | **`Residual current protection`** | $I_{\Delta n}$ = `{{Idn_setting: A}}`, $\Delta t$ = `{{delta_t: s}}` | `IEC Annex B, M / GB 附录 B, M`; scaled directly in amperes, independent of $I_n$. |
| 中性极保护 | **`Neutral pole protection (N)`** | $I_{nN}$ = `{{InN_ratios}}` | *Industry* extension (`IEC 8.1.7 / GB 7.1.7`; `GB 表 9b 脚注 f` `中性线保护`, `H.2` `带保护中性极`, `GB 7.1.7` `具有中性极断路器的附加要求`, `表 K.1` `N = 中性极端子`). |
| 接通电流脱扣器 | **`Making-current release (MCR)`** | `MCR` | Statutory (`IEC 3.6 / GB 2.10`; `MCR` is *Industry* abbr.). |
| 区域选择性联锁 / 热记忆 / Ig 指示器 | **`Zone selective interlocking (ZSI)`** / **`Thermal memory`** / **`Ig indicator`** | `ZSI` / `—` / `—` | *Industry / CHINT* extensions (ref. `A.5` / `IEC 5.7.1 (2c)` / `IEC 5.7.1 (2d)` *IEC 2024 only*). |
<!-- AUTO:END acb/§2 -->

- **Value Ordering in Protection Sentences**: Always keep `pick-up` → `time-delay` → `$I^2t$ curve state` → `resetting time` → `tolerance`.

---

## 3. CHINT ACB Exclusive Accessories, Connections & Native Sentence Frames

### 3.1 Official CHINT ACB Accessory & Component Matrix

<!-- AUTO:BEGIN acb/§3.1 -->
| CHINT Code | Chinese Term (✅ EN→ZH) | ✅ Unique Canonical IEC English (ZH→EN) | Function, Clause & Value Slots |
| :--- | :--- | :--- | :--- |
| **`SHT`** | 分励脱扣器 | **`Shunt release (SHT)`** | Remote opening (`IEC 5.7.1, 8.2.1.2.3 / GB 4.7.1, 7.2.1.2.3`); range `{{sht_range: ×Uc}}`, opening time `{{sht_time: ms}}`; `PT`/`HT` duty. |
| **`CEM`** | 闭合脱扣器 | **`Closing release (CEM)`** | Voltage closing release (`IEC 3.19 / GB 2.23`; synonym `closing coil` / `闭合线圈`); range `{{cem_range: ×Uc}}`, time `{{cem_time: ms}}`. |
| **`UVT`** | 欠电压脱扣器 | **`Undervoltage release (UVT)`** | Instantaneous opening (`IEC 5.7.1, 8.2.1.2.2 / GB 4.7.1, 7.2.1.2.2`); trip `{{uvt_trip: ×Ue}}`, pick-up `{{uvt_pickup: ×Ue}}` (verify `×Ue` vs `Uc`). |
| **`UVTR`** | 欠电压延时脱扣器 | **`Undervoltage time-delay release (UVTR)`** | Time-delay undervoltage release; delay `{{uvtr_delays: s}}`, ride-through `{{uvtr_ride_through}}`. |
| **`UVTZ`** | 失压延时脱扣器 | **`Loss-of-voltage time-delay release (UVTZ)`** | External DIN-rail delay module; range `{{uvtz_range: s}}`, step `{{uvtz_step: s}}`, multi-colour LED status. |
| **`MOD`** | 电动机操作机构 | **`Motor-operator (MOD)`** | Spring charging & remote closing (`IEC 4.2, Annex N / GB 3.4, 表 13 (4.1), 附录 N`); time `{{mod_time: s}}`, rate `{{mod_rate: cycles/min}}`. |
| **`AX`** | 辅助触头 | **`Auxiliary contact (AX)`** | Reports main contact `O`/`I` (`IEC Table 4 (1.3)` / `GB 表 13 (1.3)` `○`/`│`; `IEC 5.6, Table 4 (4.4) / GB 4.6, 表 13 (4.4)`); `{{ax_config}}` (changeover contacts, `AC-15`/`DC-13`). |
| **`AL`** | 报警开关 | **`Alarm switch (AL)`** | Operates only on automatic tripping (`IEC 3.9 / GB 2.13`); terminals `{{al_terminals}}`. |
| **`SPC`** | 合闸准备就绪触点 | **`Ready-to-close contact (SPC)`** | Open, springs charged (`IEC 8.2.1.1.6 / GB 7.2.1.1.6`), and no lock-out (`IEC 3.10 / GB 2.14`). |
| **`PSID`** | 位置信号指示装置 | **`Position signal indicating device (PSID)`** | Signals `connected`, `test` (*Industry*), and `disconnected` (`IEC 8.1.2 / GB 7.1.2`) cradle positions. |
| **`AUP`** | 抽屉座位置触点 | **`Cradle position contact (AUP)`** | Cradle microswitches for `connected`, `test` (*Industry*), `disconnected` (`IEC 8.1.2 / GB 7.1.2`); `{{aup_config}}`. |
| **`DSPL`** | 隔离位置锁定装置（三位置锁） | **`Disconnected-position locking device (DSPL)`** | Locks withdrawable CB in `connected`, `test` (*Industry*), or `disconnected` (`IEC 8.1.2 / GB 7.1.2`) position. |
| **`KL`** | 本体钥匙锁 | **`Key lock (KL)`** | Prevents closing (`IEC 3.10 / GB 2.14`); scheme `{{kl_scheme}}`, cut-out `{{cutout_dia: mm}}` via `panel hole saw`. |
| **`VBP`** | 按钮锁定装置 | **`Pushbutton lock-out cover (VBP)`** | Padlockable cover blocking ON/OFF pushbuttons (`IEC 3.10 / GB 2.14`). |
| **`SDIL`** | 状态门联锁 | **`Status door interlock (SDIL)`** | Prevents opening enclosure door while closed. |
| **`PDIL`** | 位置门联锁 | **`Position door interlock (PDIL)`** | Prevents opening enclosure door in `connected` or `test` position (*Industry*). |
| **`MI`** | 钢缆机械联锁 | **`Cable mechanical interlock (MI)`** | Two-way or three-way mechanical interlock (state frame-size scope). |
| **`DD` / `FD`** | 抽屉式相间隔板 / 固定式相间隔板 | **`Withdrawable interphase barrier (DD)`** / **`Fixed interphase barrier (FD)`** | Phase-to-phase insulating barriers between main terminals. |
| **`EB`** | 扩展母排（加长接线排） | **`Extended busbar (EB)`** | Terminal extension bars: **`Front connection`**, **`Rear horizontal connection`**, **`Rear vertical connection`**, **`{{deg: °}} rotatable terminal pads`**. |
| **`TSC`** | 透明防护罩 | **`Transparent protective cover (TSC)`** | Front protective shield (`{{tsc_ip}}`, `IEC 4.5 / GB 3.8`). |
| **`CDM`** | 操作计数器 | **`Operation counter (CDM)`** | Mechanical cycle counter recording cumulative cycles. |
| **`RU` / `PSU`** | 继电器模块 / 电源模块 | **`Relay unit (RU)`** / **`Power supply unit (PSU)`** | Output relay contacts (`{{ru_rating}}`) / DC supply (`{{psu_out: V DC}}`, `{{psu_power: W}}`). |
| **`CTN` / `ECT` / `RCT`** | 中性线互感器 / 地电流互感器 / 剩余电流互感器 | **`Neutral current transformer (CTN)`** / **`Earth current transformer (ECT)`** / **`Residual current transformer (RCT)`** | External sensors for `(3P+N)T` (`IEC 8.1.7 / GB 7.1.7`), `W`-mode earth fault, and zero-sequence residual current (`Annex B/M / GB 附录 B/M`). |
| — | 抽屉座 / 安全活门 / 摇动手柄 / 存放槽 / 门框 / 熄灭电弧装置 | **`Withdrawable cradle`** (`Cl. 3.5; GB 2.5, 图 J.1 注`) / **`Safety shutters`** (*Industry*) / **`Racking handle`** / **`Racking handle storage slot`** / **`Door escutcheon`** (`{{door_ip}}`) / **`Arc extinction device`** (`Cl. 8.1.6 / GB 7.1.6; 灭弧区 9.3.3.6.1 b); GB 8.3.2.6.1 b)`) | Mechanical & arc-quenching assemblies; 飞弧距离 = **`Arcing distance`** (`{{arcing_distance: mm}}`, *Industry*, `IEC Table 4 (3.7) / GB 表 13 (3.7)`). |
<!-- AUTO:END acb/§3.1 -->

### 3.2 Six Single-Track Native Engineering Sentence Frames
1. **Door Interlock (`SDIL` / `PDIL`)**: `"The enclosure door cannot be opened when the circuit-breaker is [closed / in the connected or test position] and can only be opened when the circuit-breaker is [open / in the disconnected position]."`
2. **Voltage-Dip Ride-Through (`UVTR` / `UVTZ`)**: `"When the supply voltage recovers within {{uvtr_ride_through}} of the delay time, the circuit-breaker does not trip."`
3. **Zero-Sequence Sampling (`RCT`)**: `"The residual operating current IΔn is expressed directly in amperes, independent of the circuit-breaker rated current In, via zero-sequence sampling with an external residual current transformer (RCT) (CHINT external RCT design; IEC B.4.2.1 also permits IΔn as % of In)."`
4. **Threshold & Position Triads**: Thresholds: `Trip` ⟷ `Pull-in` ⟷ `Holding`. Cradle positions: `Connected position` (*Industry*) ⟷ `Test position` (*Industry*) ⟷ `Disconnected position` (`Cl. 8.1.2`).
5. **Key-Lock Schemes (`KL`)**: `"[N] locks and [M] keys: [X] circuit-breakers are equipped with [N] [identical/separate] locks and [M] [identical/separate] keys; panel cut-out diameter {{cutout_dia: mm}} drilled with a panel hole saw."`
6. **Pulse-Energization Duty (`SHT` / `CEM`)**: `"The shunt release (SHT) and closing release (CEM) operate on a pulse-energization duty; the pulse duration t1 shall be at least {{pulse_t1: ms}} and the energization interval t2 shall exceed {{pulse_t2: s}}."`
