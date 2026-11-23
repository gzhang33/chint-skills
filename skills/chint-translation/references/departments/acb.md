# ACB Department Terminology & CHINT Accessory Standard (`acb.md`)

> **Department Isolation**: ACB Department only (`NXA`, `NA8`, `NA1`). Load alongside `SKILL.md` and `iec_60947_2_standard.md`.

## 1. Applicable Series & Local Workspace Reference Pointers

- **Applicable CHINT Series**: `NXA` (Kunlun series), `NA8`, `NA1` (never transliterate registered series codes).
- **Primary Standard**: `IEC 60947-2:2024` (`GB/T 14048.2`).
- **Local Workspace Reference Paths** (consult on demand to resolve exact SKU ordering codes, voltage options, and `{{...}}` datasheet slots; **never copy unreviewed ERP English typos**):
  - `Areas/样本册修改/NXA/参考资料/PRD附录_NXA附件订货数据包.xlsx` (SKU & CHINT accessory base codes)
  - `Areas/样本册修改/NXA/参考资料/附件更改/NXA系列产品附件型号汇总表20261019.xlsx` (accessory ordering code structure: `{{code}}{{frame}}-A1 {{voltage_code}} {{duty_code}}`)
  - `Areas/样本册修改/NXA/参考资料/说明书/` & `Areas/样本册修改/NXA/NXA-样本册-26-v7.pdf` (product parameters; note NXA manual PDF requires visual rendering if text layer is empty)

---

## 2. ACB Product Taxonomy, Electronic Trip Units & Protection (双标唯一译法)

| Statutory Chinese (`GB/T 14048.2—2020`) | ✅ Unique Canonical IEC English (`IEC 60947-2:2024`) | Symbol / Slot | Clause & Usage Note |
| :--- | :--- | :--- | :--- |
| 空气断路器（分类：万能式） | **`Air circuit-breaker (ACB)`** | `ACB` | `GB/T 14048.2—2020 Cl. 2.7 & 3.3`; `IEC Cl. 3.1` hyphenated `circuit-breaker`. |
| 抽屉式断路器 / 固定式断路器 | **`Withdrawable air circuit-breaker`** / **`Fixed air circuit-breaker`** | — | `IEC 3.5, 4.4, 8.1.2` / `GB 2.5, 3.7, 7.1.2`. |
| 配电子式过电流脱扣器的空气断路器 | **`Air circuit-breaker with electronic trip unit`** | — | `Annex F`; never output literal `"intelligent air circuit-breaker"`. |
| 电子脱扣器 | **`Electronic trip unit (ETU)`** | `ETU` | `IEC 5.7, Annex F` (`GB 4.7, 附录 F`). |
| 基本配电型 / 电流表型 / 功率型 / 谐波型脱扣器 | **`Basic distribution trip unit (M type)`** / **`Ammeter trip unit (A type)`** / **`Power monitoring trip unit (P type)`** / **`Harmonic analysis trip unit (H type)`** | `M / A / P / H` | Display readings readable regardless of CB status (`Cl. 5.7.3`); PLC digital I/O per `Cl. 8.1.8`. |
| 过载长延时保护 | **`Long-time overload protection (L)`** | $I_r$ = `{{Ir_setting: ×In}}`, $t_r$ = `{{tr_setting: s}}` | `Cl. 3.16, 5.7.1 (2c), Table 5, Fig. K.1`. |
| 短路短延时保护 | **`Short-time delay short-circuit protection (S)`** | $I_{sd}$ = `{{Isd_setting: ×Ir}}`, $t_{sd}$ = `{{tsd_setting: s}}` | `Cl. 3.8, 3.17, 3.13` ($I^2t$ ON/OFF); state any upper cap separately. |
| 短路瞬时保护 | **`Instantaneous short-circuit protection (I)`** | $I_i$ = `{{Ii_setting: ×In}}`, $t_i$ = `{{ti_max: ms}}` | `Cl. 3.7, 3.12, 3.15` (plus `OFF` if supported). |
| 接地故障保护 | **`Ground-fault protection (G)`** | $I_g$ = `{{Ig_setting: ×In}}`, $t_g$ = `{{tg_setting: s}}` | `Cl. 5.7.1 (2d), 8.2.1.2.4 c), Table K.1, Fig. K.1` (`CI-A` / `CI-B`). |
| 剩余电流保护 | **`Residual current protection`** | $I_{\Delta n}$ = `{{Idn_setting: A}}`, $\Delta t$ = `{{delta_t: s}}` | `Annex B, Annex M`; scaled directly in amperes, independent of $I_n$. |
| 中性极保护 | **`Neutral pole protection (N)`** | $I_{nN}$ = `{{InN_ratios}}` | `IEC 8.1.7, Table K.1` / `GB 7.1.7`. |
| 区域选择性联锁 / 接通电流脱扣器 / 热记忆 / Ig 指示器 | **`Zone selective interlocking (ZSI)`** / **`Making-current release (MCR)`** / **`Thermal memory`** / **`Ig indicator`** | `ZSI` / `MCR` | `Annex A (A.5)` / `IEC 3.6 (GB 2.10)` / `Cl. 3.14, 5.7.1` (never `"Ig indicator light"`). |

- **Value Ordering in Protection Sentences**: Always keep `pick-up` → `time-delay` → `$I^2t$ curve state` → `resetting time` → `tolerance`.

---

## 3. CHINT ACB Exclusive Accessories, Connections & Native Sentence Frames

### 3.1 Official CHINT ACB Accessory & Component Matrix (24+ Local Codes)

| CHINT Code | Chinese Term (✅ EN→ZH) | ✅ Unique Canonical IEC English (ZH→EN) | Function, Clause & Value Slots |
| :--- | :--- | :--- | :--- |
| **`SHT`** | 分励脱扣器 | **`Shunt release (SHT)`** | Remote opening (`IEC 5.7.1, 8.2.1.2.3`); range `{{sht_range: ×Uc}}`, opening time `{{sht_time: ms}}`; `PT` pulse / `HT` continuous duty. |
| **`CEM`** | 闭合脱扣器 | **`Closing release (CEM)`** | Voltage-energized closing release (`IEC 3.19` / `GB 2.23`; admitted synonym `closing coil`); range `{{cem_range: ×Uc}}`, closing time `{{cem_time: ms}}`. |
| **`UVT`** | 欠电压脱扣器 | **`Undervoltage release (UVT)`** | Instantaneous opening on voltage drop (`IEC 5.7.1, 8.2.1.2.2`); trip band `{{uvt_trip: ×Ue}}`, pick-up `{{uvt_pickup: ×Ue}}`. |
| **`UVTR`** | 欠电压延时脱扣器 | **`Undervoltage time-delay release (UVTR)`** | Delays tripping during voltage dips; delay steps `{{uvtr_delays: s}}`, ride-through fraction `{{uvtr_ride_through}}`. |
| **`UVTZ`** | 失压延时脱扣器 | **`Loss-of-voltage time-delay release (UVTZ)`** | External DIN-rail delay module; delay range `{{uvtz_range: s}}`, step `{{uvtz_step: s}}`, multi-colour LED status indicator. |
| **`MOD`** | 电动机操作机构 | **`Motor-operator (MOD)`** | Automatic spring charging & remote closing (`IEC 4.2, Annex N` / `GB 8.4.2`); charging time `{{mod_time: s}}`, rate `{{mod_rate: cycles/min}}`. |
| **`AX`** | 辅助触头 | **`Auxiliary contact (AX)`** | Reports main contact `O`/`|` status (`Cl. 5.6`); config `{{ax_config}}` (changeover contacts, `AC-15` / `DC-13`). |
| **`AL`** | 故障脱扣报警开关 | **`Alarm switch (AL)`** | Operates only upon automatic overcurrent/fault tripping (`Cl. 3.9`); terminals `{{al_terminals}}`. |
| **`SPC`** | 合闸准备就绪触点 | **`Ready-to-close contact (SPC)`** | Closes when CB is open, springs charged (`Cl. 8.2.1.1.6`), and no closing lock-out (`Cl. 3.10`) is active. |
| **`PSID`** | 位置信号指示装置 | **`Position signal indicating device (PSID)`** | Signals `connected`, `test`, and `disconnected` positions in the cradle (`Cl. 8.1.2`). |
| **`AUP`** | 抽屉座位置触点 | **`Cradle position contact (AUP)`** | Cradle microswitches signalling `connected`, `test`, and `disconnected` positions (`{{aup_config}}`). |
| **`DSPL`** | 分离位置锁定装置（三位置锁） | **`Disconnected-position locking device (DSPL)`** | Locks withdrawable CB in `connected`, `test`, or `disconnected` position (`Cl. 8.1.2`). |
| **`KL`** | 本体钥匙锁 | **`Key lock (KL)`** | Prevents closing (`Cl. 3.10`); scheme `{{kl_scheme}}`, panel cut-out diameter `{{cutout_dia: mm}}` via `panel hole saw`. |
| **`VBP`** | 按钮锁定装置 | **`Pushbutton lock-out cover (VBP)`** | Padlockable cover blocking manual ON/OFF pushbuttons (`Cl. 3.10`). |
| **`SDIL`** | 状态门联锁 | **`Status door interlock (SDIL)`** | Prevents opening the enclosure door while the circuit-breaker is closed. |
| **`PDIL`** | 位置门联锁 | **`Position door interlock (PDIL)`** | Prevents opening the enclosure door in `connected` or `test` position (`Cl. 8.1.2`). |
| **`MI`** | 钢缆机械联锁 | **`Cable mechanical interlock (MI)`** | Two-way or three-way mechanical interlock across circuit-breakers (state frame-size scope explicitly). |
| **`DD` / `FD`** | 抽屉式 / 固定式相间隔板 | **`Withdrawable interphase barrier (DD)`** / **`Fixed interphase barrier (FD)`** | Phase-to-phase insulating barriers between main terminals. |
| **`EB`** | 扩展母排（加长接线排） | **`Extended busbar (EB)`** | Terminal extension bars; main connections: **`Front connection`**, **`Horizontal rear connection`**, **`Vertical rear connection`**, **`{{deg: °}} rotatable terminal pads`**. |
| **`TSC`** | 透明防护罩 | **`Transparent protective cover (TSC)`** | Front protective fascia shield (`{{tsc_ip}}`, `Cl. 4.5`). |
| **`CDM`** | 操作计数器 | **`Operation counter (CDM)`** | Mechanical cycle counter recording cumulative operating cycles. |
| **`RU` / `PSU`** | 继电器模块 / 电源模块 | **`Relay unit (RU)`** / **`Power supply unit (PSU)`** | Output contact expansion (`{{ru_rating}}`) / auxiliary DC supply (`{{psu_out: V DC}}`, `{{psu_power: W}}`). |
| **`CTN` / `ECT` / `RCT`** | 中性线 / 地电流 / 剩余电流互感器 | **`Neutral current transformer (CTN)`** / **`Earth current transformer (ECT)`** / **`Residual current transformer (RCT)`** | External sensors for `(3P+N)T` (`Cl. 8.1.7`), `W`-mode earth fault, and zero-sequence residual current (`Annex B/M`). |
| — | 抽屉座 / 安全活门 / 摇动手柄 / 存放槽 / 门框 / 灭弧装置 | **`Withdrawable cradle`** (`Cl. 3.5`), **`Safety shutters`** (`Cl. 8.1.2`), **`Racking handle`**, **`Racking handle storage slot`**, **`Door escutcheon`** (`{{door_ip}}`), **`Arc extinction device`** (`Cl. 8.1.6`; sub-assembly: `arc-extinguishing chamber`) | Standard mechanical & arc-quenching sub-assemblies;飞弧距离 = **`Arcing distance`** (`{{arcing_distance: mm}}`, `Cl. 8.1.5`). |

### 3.2 Six Single-Track Native Engineering Sentence Frames
1. **Door Interlock (`SDIL` / `PDIL`)**: `"The enclosure door cannot be opened when the circuit-breaker is [closed / in the connected or test position] and can only be opened when the circuit-breaker is [open / in the disconnected position]."`
2. **Voltage-Dip Ride-Through (`UVTR` / `UVTZ`)**: `"When the supply voltage recovers within {{uvtr_ride_through}} of the delay time, the circuit-breaker does not trip."`
3. **Zero-Sequence Sampling (`RCT`)**: `"The residual tripping current IΔn is expressed directly in amperes, independent of the circuit-breaker rated current In, via zero-sequence sampling with an external residual current transformer (RCT)."`
4. **Threshold & Position Triads**: Thresholds: `Trip` ⟷ `Pull-in` ⟷ `Holding`. Cradle positions (`Cl. 8.1.2`): `Connected position` ⟷ `Test position` ⟷ `Disconnected position`.
5. **Key-Lock Schemes (`KL`)**: `"[N] locks and [M] keys: [X] circuit-breakers are equipped with [N] [identical/separate] locks and [M] [identical/separate] keys; panel cut-out diameter {{cutout_dia: mm}} drilled with a panel hole saw."`
6. **Pulse-Energization Duty (`SHT` / `CEM`)**: `"The shunt release (SHT) and closing release (CEM) operate on a pulse-energization duty; the pulse duration t1 shall be at least {{pulse_t1: ms}} and the energization interval t2 shall exceed {{pulse_t2: s}}."`

---

## 4. ACB Audit Blacklist (❌ Mode B 审查拦截与旧稿识别唯一真源)

> Consulted in `Mode B` audit or `EN→ZH` legacy decoding only; mirrored programmatically by [lint_text.py](../../scripts/lint_text.py).

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
| `refuses to open` / `is forbidden to open` / `irrelevant to` / `belong to the pulse energization working mode` | Legacy manual Chinglish syntax | Use §3.2 single-track native frames (`does not trip`, `cannot be opened`, `independent of`, `operate on a pulse-energization duty`) |
| `MX`, `MN`, `XF`, `OF`, `SDE`, `PF`, `MCH`, `YO`, `KLC` | Competitor (Schneider/ABB) accessory codes | Use official CHINT codes (`SHT`, `UVT`, `CEM`, `AX`, `AL`, `SPC`, `MOD`, `KL`) |
| `Universal Circuit Breaker`, `intelligent air circuit-breaker`, `LVPCB`, `Shunt Trip` | Literal Chinglish or North American UL bleed-over | **`Air circuit-breaker (ACB)`**, **`Air circuit-breaker with electronic trip unit`**, **`Shunt release (SHT)`** |

---

## 5. Department Custom Extensions (框架产品部自行补充区)

| Added Date | Chinese Term | ✅ Unique Canonical IEC English (with CHINT Code) | Value Slot | ❌ Forbidden Literal | Source / Submitter |
| :--- | :--- | :--- | :--- | :--- | :--- |
| — | *(在此行下方追加框架部门新增系列或专属字段)* | — | — | — | — |
