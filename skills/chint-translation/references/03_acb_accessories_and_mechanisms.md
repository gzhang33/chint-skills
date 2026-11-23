# ACB Internal & External Accessories Taxonomy & Syntactic Style Guide (IEC 60947-2:2024, Ed. 6.0)

Dual-track standard harmonized to **IEC 60947-2:2024 (Edition 6.0)** single-track British spelling and hyphenation across BOTH registers (`circuit-breaker`, `withdrawable`, `undervoltage`, `shunt release`, `closing release`, `energization`, `colour`, `utilisation`, `signalling`):
1. **Track 1 (IEC Global Standard)**: the international catalogue register (ABB / Schneider / Siemens / Eaton class), using exact IEC 60947-2:2024 terms and clauses.
2. **Track 2 (OEM Manual SSOT)**: the OEM English operation and maintenance manual register. Keeps distinct CHINT OEM structural/accessory phrasing (`Closed electromagnet (CEM)`, `Door Frame and Pad`, `Steel Cable Interlock`, `Keys and locks (KL)`, `Drawer seat`) while harmonizing spelling and hyphenation to IEC 60947-2:2024 British English (`circuit-breaker`, `Undervoltage Instantaneous Trip`).

The two tracks are intentionally parallel. Where both are listed, the Track 2 wording is the one that goes into service documents; Track 1 wording is used only when quoting an international catalogue style. North American / UL / ANSI terms (`Shunt Trip`, `LVPCB`, `Molded`) are allowed ONLY in explicitly labelled UL / ANSI annotations.

## 0. Value Slot Convention

Every quantity below is a slot: `{{param_name: unit}}`. Slot fills follow `01_universal_iec_parameters.md` §4.
Where an accessory's characteristics live in a table in the source manual, cite the table in the sentence rather than inlining the number.

### IEC 60947-2:2024 Mechanism, Circuit & Installation Classification
- **Operating mechanism control methods (`4.2`, `8.2.1.1`)**: `dependent manual operation` (`8.2.1.1.2`), `independent manual operation` (`8.2.1.1.3`), `dependent power operation` (`8.2.1.1.4`), `independent power operation` (`8.2.1.1.5`), `stored energy operation` (`8.2.1.1.6`).
- **Provision for maintenance (`4.3`)**: `maintainable` / `non-maintainable`.
- **Method of installation (`4.4`)**: `fixed` / `plug-in` (`3.4`) / `withdrawable` (`3.5`, `8.1.2`).
- **Control & auxiliary circuits (`5.5`, `5.6`)**: `5.5.1` electrical control circuits (`Table 3` preferred $U_c$ values), `5.5.2` air-supply control circuits (pneumatic or electro-pneumatic), `5.6` auxiliary circuits.
- **Releases (`5.7`, `8.2.1.2`, `Annex N`)**: `5.7.1` lists `shunt release` (`8.2.1.2.3`), `overcurrent release`, `undervoltage release (for opening)` (`8.2.1.2.2`), and `closing release` (`3.19`). Electronic auxiliaries are EMC-tested per `Annex N`.

---

## 1. Operating Mechanisms & Releases (操作机构与脱扣附件)

| International Code | Chinese Term | Track 1: IEC Global Catalogue Term | Track 2: OEM Manual SSOT (IEC Spelling) | Technical Description & Functional Definition |
| :--- | :--- | :--- | :--- | :--- |
| **MOD / M / MOE** | 电动操作机构 (电操/储能电机) | **Motor Operator Device (MOD)** / Spring Charging Motor (`4.2` stored energy operation, `8.2.1.1.6`, `Annex N` motor-operators) | **Electric Energy Storage Mechanism (MOD)** / Motor | Automatically charges the operating spring mechanism after closing or operates remotely (`5.5.1`, `8.2.1.1.6`). Power-on time `{{motor_power_on_time: s}}` per operation; operating frequency `{{motor_frequency: times/min}}`. |
| **CEM / CC / XF** | 闭合电磁铁 (合闸线圈) | **Closing release (CC / CEM)** *(admitted synonym: closing coil, `3.19`, `5.7.1` item 4)* | **Closed electromagnet (CEM)** | Release, energized by a voltage source (`3.19`, `5.7.2` $U_c$), that triggers closing of the charged spring mechanism of the circuit-breaker upon remote electrical signal. Operating range `{{cem_operating_range: ×Us}}`; close time `{{cem_close_time: ms}}`. |
| **SHT / MX / ST** | 分励脱扣器 (分励线圈) | **Shunt release (SHT / MX)** *(`5.7.1` item 1, `8.2.1.2.3`; North American / UL / ANSI: Shunt Trip; never "shunt opening release")* | **Shunt Release (SHT)** | Remotely opens (trips) the closed circuit-breaker (`5.7.2` $U_c$, `8.2.1.2.3`). Operating range `{{sht_operating_range: ×Us}}`; break time `{{sht_break_time: ms}}`. |
| **UVT / UVR / MN** | 欠电压脱扣器 (瞬时) | **Undervoltage release (UVR / UVT)** *(`5.7.1` item 3, `8.2.1.2.2`; unhyphenated `undervoltage`)* | **Undervoltage Instantaneous Trip (UVT)** | Trips when voltage falls into `{{uvt_trip_band: ×Us}}`; permits closing above `{{uvt_pickup_level: ×Us}}`; prevents closing below `{{uvt_inhibit_level: ×Us}}`. |
| **UVTR / UVR-D** | 欠压延时脱扣器 | **Undervoltage time-delay release (UVTR)** | **Undervoltage Delayed Trip (UVTR)** | Delays tripping during transient voltage dips. Selectable delays `{{uvtr_delay_steps: s}}`; whether the steps are adjustable must be stated. Refuses to open if voltage recovers within `{{uvtr_ride_through_fraction}}` of the delay time. |
| **UVTZ** | 失压延时脱扣器 | **Loss-of-voltage time-delay release (UVTZ)** | **Undervoltage delay controller (UVTZ)** | External DIN-rail module with adjustable delay `{{uvtz_delay_range: s}}`, step `{{uvtz_delay_step: s}}` and a multi-colour status indicator. |
| **Arc Chute** | 灭弧室 | **Arc-extinguishing chamber (Arc chute)** *(IEC `8.1.6` term: `arc extinction device`)* | **Arc-extinguishing chamber** | De-ionizing grid splitter plates dividing and quenching the electrical arc during contact separation (`8.1.6` arc extinction device). |
| **Pushbuttons** | 合/分闸按钮 | **Pushbutton (Closing/Opening pushbutton)** | **Closing / Opening button** | Mechanical pushbuttons (`manual operating means`, `8.1.5`, `Table 6`) located on circuit-breaker front fascia for manual closing and tripping. |

---

## 2. Indication Devices & Position Contacts (指示装置与状态触点)

| International Code | Chinese Term | Track 1: IEC Global Catalogue Term | Track 2: OEM Manual SSOT (IEC Spelling) | Technical Definition & Logic |
| :--- | :--- | :--- | :--- | :--- |
| **AL / SDE / SD** | 故障脱扣指示触点 (报警触头) | **Alarm switch** / Fault-trip indication contact *(`3.9`: auxiliary switch operating only upon tripping of the circuit-breaker)* | **Trip alarm contact**, terminals `{{alarm_contact_terminals}}` | Form C changeover contact (`5.6` auxiliary circuits) signalling automatic tripping caused by overcurrent, short circuit, or earth fault. |
| **SPC / RTC / PF** | 合闸准备就绪指示触点 | **Ready-to-close contact (RTC / SPC)** | **Ready-to-close indication contact (SPC)**, terminals `{{rtc_contact_terminals}}` | Form A (1 NO) contact closing when circuit-breaker is open, springs charged (`8.2.1.1.6`), and no trip lock-out (`3.10`) is present. |
| **PSID** | 位置信号指示装置 | **Position signal indication device (PSID)** *(`8.1.2` reliable indicating device)* | **Position Signal Indication Device (PSID)** | Secondary circuit signalling mechanism unambiguously indicating circuit-breaker isolating-contact position in the cradle (Connected, Test, Disconnected — `8.1.2`). |
| **AUP / CE-CD-CT** | 抽架位置指示触点 | **Cradle position indication contacts** | **Cradle position indication contact**, configuration `{{aup_contact_config}}` | Microswitches installed in the cradle signalling Connected, Test, and Disconnected (OEM manual legacy: Separation) positions (`8.1.2`). |
| **Spring Status** | 弹簧储能指示触点 | **Spring charged indication contact** (`8.2.1.1.6` charge indicator) | **Energy storage indication**, terminals `{{spring_contact_terminals}}` | Form A (1 NO) contact signalling operating spring is fully charged and ready for closing. |
| **AX / OF** | 辅助触头 (开/关状态) | **Auxiliary contacts (AX / OF)** (`5.6` auxiliary circuits) | **Auxiliary Contacts (AX)** | Reports main contact position (`O`/`|`). Available configurations `{{aux_contact_configs}}`. Form C designated as **Conversion contacts**. |

---

## 3. Withdrawable Cradle, Locks & Mechanical Interlocks (抽屉座、锁具与机械联锁)

| International Code | Chinese Term | Track 1: IEC Global Catalogue Term | Track 2: OEM Manual SSOT (IEC Spelling) | Technical Definition & Application Scope |
| :--- | :--- | :--- | :--- | :--- |
| **Cradle / Chassis** | 抽屉座 / 导轨座 | **Guide frame (Withdrawable cradle / chassis)** *(`3.5`, `4.4` withdrawable circuit-breaker; `Fig. J.1` draw-out cradle)* | **Drawer seat / Cradle** | Housing with guide rails, safety shutters (isolating-contact shutters), and isolating cluster contacts (`3.5`, `8.1.2`). |
| **DSPL / 3-Pos Lock** | 抽屉座三位置锁定装置 | **Three-position locking device of cradle** (`8.1.2`) | **"Separated" Position Locking Device (DSPL)** | Locks the circuit-breaker securely in Connected, Test, or Disconnected position (OEM manual legacy: Separation position) per `8.1.2`, preventing inadvertent reduction of isolating distances and preventing racking until unlocked. |
| **VBP** | 按钮锁定装置 (按钮锁) | **Pushbutton padlocking device (VBP)** (`3.10` lock-out device preventing closing) | **Pushbutton lock (VBP)** | Transparent or metallic lock-out cover accepting padlocks to disable manual ON/OFF pushbuttons (`3.10`). |
| **KL / KLC** | 本体钥匙锁 (程序锁) | **ACB Key Lock (KLC)** *(`3.10` circuit-breaker with lock-out device preventing closing)* | **Keys and locks (KL)** | Cylinder lock schemes: `{{key_lock_schemes}}` (X locks Y keys). Field installation uses a **hole opener**, diameter `{{hole_opener_diameter: mm}}` per frame size (`3.1.1`). |
| **SDIL** | 断路器状态门联锁 | **Circuit-breaker status door interlock (SDIL)** | **Circuit-breaker status door interlock (SDIL)** | Enclosure door is forbidden to open when the circuit-breaker is closed; allowed to open when disconnected/open. |
| **PDIL** | 断路器位置门联锁 | **Circuit-breaker position door interlock (PDIL)** | **Circuit-breaker position door interlock (PDIL)** | Enclosure door is forbidden to open when the circuit-breaker is in Connected or Test position; allowed to open in Disconnected position (OEM manual legacy: Separation position) (`8.1.2`). |
| **MI** | 机械联锁 (钢缆/连杆) | **Mechanical Interlock (MI)** / Cable Interlock | **Steel Cable Interlock (MI)** | Double Interlock (two circuit-breakers) or Triple Interlock (three circuit-breakers). State the frame-size applicability separately; do not assume a threshold. |
| **Padlock** | 抽屉位置挂锁 | **Withdrawable position padlock** *(`3.5`, `8.1.2`)* | **Withdrawable position padlock** *(OEM manual legacy: Drawout position padlock)* | Blocks the racking handle entry slot when padlocked in the disconnected position (`3.5`, `8.1.2`), precluding body movement and ensuring isolating distances cannot be inadvertently reduced. |

---

## 4. External Transformers & Other Accessories (互感器与其他附件)

| Code | Chinese Term | Track 1: IEC Global Catalogue Term | Track 2: OEM Manual SSOT (IEC Spelling) | Technical Definition & Sampling Principle |
| :--- | :--- | :--- | :--- | :--- |
| **CTN** | 中性线互感器 | **Neutral Current Transformer (CTN)** (`8.1.7`) | **External Neutral Pole N Current Transformer (CTN)** | Installed in three-phase four-wire systems with 3P circuit-breakers to detect neutral unbalance current [(3P+N)T mode]. Selection is by frame size (`3.1.1`) and by transformer opening size `{{ctn_opening_sizes}}`. |
| **ECT** | 地电流互感器 | **Earth Current Transformer (ECT)** | **External Earth Current Transformer (ECT)** *(OEM manual legacy: External Ground Current Transformer)* | Installed on the transformer neutral earth line (W mode), connecting through the earth-current module for earth leakage protection. *(North American / UL / ANSI: Ground Current Transformer.)* |
| **RCT** | 漏电互感器 | **Residual Current Transformer (RCT)** (`Annex B`, `Annex M`) | **External Leakage Transformer (RCT) / Rectangular RCT** | Zero-sequence sampling transformer. Tripping value $I_{\Delta n}$ is expressed directly in amperes, independent of the circuit-breaker rated current ($I_n$). |
| **Door Frame** | 柜门框 / 面罩 | **Door Escutcheon (Door Flange)** | **Door Frame and Pad** | Gasketed sealing frame mounted on the switchboard door panel cutout; the degree of protection (`4.5`) it achieves must be stated as `{{door_frame_ip}}`. |
| **CD** | 自动电源控制装置 | **Automatic Transfer Controller (CD)** | **Automatic power supply control device (CD)** | Source-transfer controller matching the circuit-breaker family, executing two-source power transfer with mechanical/electrical interlocks. |
| **RU** | 继电器模块 | **Relay Module (RU)** | **Relay module (RU) / Relay unit (RU-1)** | Amplifies controller output contact capacity. Contact rating `{{ru_contact_rating_ac}}` / `{{ru_contact_rating_dc}}`. |
| **PSU** | 电源模块 | **Power Supply Module (PSU)** | **Power supply module (PSU) / PSU-1** | Supplies a stabilized DC output `{{psu_output: V}}` at `{{psu_power: W}}` from an AC or DC input `{{psu_input}}`. DIN-rail mount, rail width `{{psu_rail_width: mm}}`. |

---

## 5. Linguistic Style Abstractions & Syntactic Archetypes

When authoring, translating, or auditing technical documents across both registers, apply these six abstract sentence patterns. Every occurrence of `circuit-breaker` is hyphenated, and British IEC 60947-2:2024 spelling applies consistently across Track 1 and Track 2. Placeholders follow the slot convention in §0.

### Archetype 1: Modal Permission & Prohibition (门联锁与安全闭锁)
- **Grammar Structure**:
  `The [Enclosure Door / Guard] is forbidden to open when [Component] is [State A], and is allowed to open when [Component] is [State B].`
- **Application**:
  - *Status Interlock (SDIL)*: "The cabinet door is forbidden to open when the circuit-breaker is closed and is allowed to open when the circuit-breaker is disconnected."
  - *Position Interlock (PDIL)*: "The cabinet door is forbidden to open when the circuit-breaker is in the connected and test positions and is allowed to open when the circuit-breaker is in the disconnected position." *(OEM manual legacy: "connection" / "separation position".)*

### Archetype 2: Protective Ride-Through & Non-Tripping Refusal (保护拒动与穿越延时)
- **Grammar Structure**:
  `When [Monitored Parameter] returns to [Normal Operating State] within [Fraction] [Delay Time], the [Apparatus] refuses to open / will not trip.`
- **Application**:
  - *UVTR / UVTZ*: "When the voltage returns to normal within `{{uvtr_ride_through_fraction}}` of the delay time, the circuit-breaker refuses to open."

### Archetype 3: Rating Independence & Signal Topology (参数独立性与采样拓扑)
- **Grammar Structure**:
  `The [Fault Protection Value] is directly expressed in [Physical Unit], irrelevant to [Nominal Apparatus Rating]. The signal is taken in a [Sampling Mode], requiring an [External Sensor Component].`
- **Application**:
  - *Residual Current (RCT)*: "The leakage trip value $I_{\Delta n}$ is directly expressed in amperes, irrelevant to the rated current of the circuit-breaker. The signal is taken in a zero-sequence sampling mode, requiring an external leakage transformer."

### Archetype 4: Dual Threshold Terminology Mapping (动作阈值配对词法)
- **Release Thresholds**:
  - 脱扣: `Trip` (or `Drop-out` in catalogue)
  - 吸合: `Pull-in` (or `Pick-up / Closing` in catalogue)
  - 保持: `Holding` (or `Continuous` in catalogue)
- **Racking Mechanism Positions (IEC 60947-2:2024 Cl. `3.5`, `8.1.2`)**:
  - 分离位置: `Disconnected position` (IEC 60947-2:2024 standard; OEM manual legacy: `Separation position`)
  - 试验位置: `Test position`
  - 连接位置: `Connected position` (IEC standard; OEM manual legacy: `Connection position`)

### Archetype 5: Combinatorial Interlocking Scheme Archetype (锁具拓扑与开孔句型)
- **Grammar Structure**:
  `[X] locks and [Y] keys: [N] circuit-breakers are equipped with [X] [identical/separate] locks and [Y] [identical/separate] keys.`
- **Application**:
  - "Two locks and one key: Two circuit-breakers are equipped with two identical locks and one key."
  - "Three locks and two keys: Three circuit-breakers are equipped with three identical locks and two identical keys."
- **Installation Tool Idiom**:
  - Official Manual SSOT: `hole opener` (e.g., "opened with a hole opener with diameter of `{{hole_opener_diameter: mm}}`").
  - Catalogue Standard: `hole saw / punch` (e.g., "panel hole saw").

### Archetype 6: Pulse Energization Duty Constraint Archetype (脉冲通电工作制)
- **Grammar Structure**:
  `The [Release A] and [Release B] belong to the pulse energization working mode, and it is necessary to ensure that the pulse time t1 is not less than [T1] and the energization interval t2 is greater than [T2].` *(IEC 60947-2:2024 uses `-ize` / `energization`.)*
- **Application**:
  - "The Shunt Release and Closing Release (OEM: Closed Electromagnet) belong to the pulse energization working mode, and it is necessary to ensure that the pulse time t1 is not less than `{{pulse_time_t1: ms}}` and the energization interval t2 is greater than `{{pulse_interval_t2: s}}`."
