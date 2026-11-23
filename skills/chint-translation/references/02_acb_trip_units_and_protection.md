# ACB Electronic Trip Units & Protection Taxonomy (IEC 60947-2:2024, Ed. 6.0)

Aligned with **IEC 60947-2:2024 (Edition 6.0)** and the trip-unit naming conventions of major low-voltage manufacturers (ABB Ekip / PR class, Schneider Micrologic class, LS OCR class). Uses strict IEC British spelling and hyphenation (`circuit-breaker`, `pick-up`, `time-delay`, `selectivity`, `back-up`, `withdrawable`). North American / UL / ANSI equivalents appear only in explicitly labelled annotations.

## 0. Value Slot Convention

This is a translation configuration, not a data sheet. Every physical quantity is a slot resolved from the product datasheet:
`{{param_name: unit}}`. Slot fills and number formatting follow `01_universal_iec_parameters.md` §4.

---

## 1. Trip Unit Types & Intelligence Levels

| Series / Type | Chinese Term | Standard Global English Term (IEC 60947-2:2024) | Standard Features & Clause Grounding |
| :--- | :--- | :--- | :--- |
| **Controller / ETU** | 智能控制器 / 控制器 | **Controller / Electronic Trip Unit (ETU)** *(Never literal "intelligent controller" in component listings)* | Microprocessor-based digital overcurrent protection and monitoring unit (`5.7`, `8.1.6` items h–i, `Annex F`). |
| **Basic Distribution Type (M Type)** | 基本型 / 配电型脱扣器 | **Basic Distribution Trip Unit (Standard Protection)** | Dual rotary switch / LED dial setting for standard L/S/I/G protection (`5.7.3`). |
| **Ammeter / Measurement Type (A Type)** | 电流测量型 / 仪表型脱扣器 | **Ammeter Trip Unit (Current Measurement)** | LCD digital display, real-time current metering ($I_a, I_b, I_c, I_n$), fault history log. Per `5.7.3`, display readings must remain readable regardless of circuit-breaker status. |
| **Power / Energy Type (P Type)** | 功率型 / 电能监控型脱扣器 | **Power & Energy Trip Unit (Power Monitoring)** | Voltage, active/reactive/apparent power ($P, Q, S$), power factor ($\cos\varphi$), energy consumption ($E$). |
| **Harmonic & Power Quality Type (H Type)** | 谐波型 / 高级电能质量型脱扣器 | **Harmonic Analysis & Power Quality Trip Unit** | Advanced FFT harmonic analysis (THD, harmonic order range per product datasheet), waveform capture, load shedding; PLC digital I/O where fitted (`3.18`, `8.1.8`). |

---

## 2. Protection Functions, Indicators & Setting Parameters (四段保护与整定)

| Protection Symbol | Chinese Term | Standard Global English Notation (IEC 60947-2:2024) | Adjustable Parameter Slot & Clause Reference |
| :--- | :--- | :--- | :--- |
| **L** | 过载长延时保护 | **Long-time protection against overloads (L)** / Inverse time-delay overload release (`5.7.1` item 2c, `5.7.4`) | Overload current setting: $I_r$ = `{{Ir_setting: ×In}}` (`3.16`, `Table K.1`; equals $I_n$ if non-adjustable); tripping time: $t_r$ = `{{tr_setting: s}}` at a stated multiple of $I_r$ (`Figure K.1`, `8.2.1.2.4` item b, `Table 5`). |
| **S** | 短路短延时保护 | **Short-time protection against short circuits (S)** / Short-time delay short-circuit release (`3.8`, `3.7`, `5.7.1` item 2b) | Short-time pick-up current setting: $I_{sd}$ = `{{Isd_setting: ×Ir}}` (`3.17`, `Table K.1`); intentional time-delay: $t_{sd}$ = `{{tsd_setting: s}}` ($I^2t$ ON/OFF per `3.13` $I^2t$ characteristic & `Figure K.1`); name any upper current cap separately in the sentence. |
| **I** | 短路瞬时保护 | **Instantaneous protection against short circuits (I)** / Instantaneous short-circuit release (`3.7`, `5.7.1` item 2a) | Instantaneous short-circuit current setting: $I_i$ = `{{Ii_setting: ×In}}` (`3.15`, `Table K.1`) plus an OFF position; opening time (commonly referred to as tripping time per `3.12` Note 2): $t_i$ = `{{ti_fast: ms}}` (fast) / `{{ti_standard: ms}}` (standard). |
| **G** | 接地故障保护 | **Earth-fault protection (G)** *(IEC preferred; IEC `5.7.1` item 2d & `Table K.1` also list `ground-fault`; North American / UL / ANSI: Ground-fault protection, ANSI 51N)* | Residual vector summation / source ground return pick-up: $I_g$ = `{{Ig_setting: ×In}}` (`Table K.1`, `Figure K.1`, scaled on $I_n$); tripping time: $t_g$ = `{{tg_setting: s}}`. |
| **V** | 剩余电流/漏电保护 (Vigi) | **Earth leakage / Residual current protection (V)** *(IEC `Annex B` CBR / `Annex M` MRCD; Schneider: Vigi; North American / ANSI: 51G)* | Rated residual operating current: $I_{\Delta n}$ = `{{Idn_setting: A}}` with step `{{Idn_step: A}}` (`Annex B`, `Annex M`, `Table K.1`; alongside $I_{\Delta no}$, $I_{\Delta m}$, $\Delta t$); scaled in amperes, not in $I_n$ multiples. ≠ Earth-fault (G / ANSI 51N). |
| **N** | 中性极保护 | **Neutral pole protection (N)** (`8.1.7`, `8.1.6` item f, `Table K.1`) | $I_{nN}$ setting ratios `{{InN_ratios}}` or OFF. |
| **Ig Indicator** | Ig指示灯 / 接地故障指示灯 | **Ig indicator** *(Never "Ig indicator light")* | LED status indicator illuminating upon earth-fault pick-up/trip. |
| **ZSI** | 区域选择性联锁 | **Zone Selective Interlocking (ZSI)** *(IEC term: `selectivity`, `5.4`, `Annex A` `A.5`; never "discrimination")* | Short-time & earth-fault selectivity signal bus between upstream/downstream circuit-breakers (`Annex A` coordination: selectivity `A.5` with selectivity limit current $I_s$, back-up protection `A.6` with take-over current $I_B$). |
| **MCR** | 瞬时合闸涌流保护 | **Making-current release (MCR)** (`3.6`) | Instantaneous override release permitting a circuit-breaker to open without intentional time-delay during a closing operation if making current exceeds threshold, and rendered inoperative when the circuit-breaker is in the closed position (`3.6`). |
| **Thermal Memory** | 热记忆功能 | **Thermal memory (Thermal image)** (`5.7.1` item 2c, `3.14`) | Retains heating profile (*inverse time-delay dependent on previous load*, `5.7.1` item 2c) across the `resetting time` (`3.14`) from overcurrent tripping until reclosing condition is reached. |

---

## 3. IEC 60947-2:2024 Protection, Timing & Compliance Reference

### 3.1 Core Definitions, Releases & Timing (`Cl. 3`, `Cl. 5.7`, `Cl. 8`)
- **Overcurrent releases (`3.6`–`3.8`, `5.7.1`–`5.7.4`)**:
  - `3.6` *making-current release*: opens without intentional time-delay during closing only; inoperative once closed.
  - `3.7` *short-circuit release*: overcurrent release intended for protection against short circuits.
  - `3.8` *short-time delay short-circuit release*: short-circuit release operating at the end of an intentional short-time delay ($t_{sd}$).
  - `5.7.1`–`5.7.4`: distinguishes instantaneous, definite time-delay, and inverse time-delay releases (independent of or dependent on previous load); adjustable releases cover interchangeable releases (`5.7.1` Note 2). Remote/external setting adjustment is permitted if local setting indications are not exceeded or remote control is locally indicated (`5.7.3`).
- **Opening time vs Tripping time (`3.12` Note 2)**: `opening time` is the interval from initiation of the opening operation until arcing contacts separate in all poles. Note 2 specifies that for circuit-breakers, "opening time" is commonly referred to as "tripping time", although strictly speaking *tripping time* ends when the opening command becomes irreversible.
- **$I^2t$ characteristic (`3.13`)**: curve giving maximum $I^2t$ values related to break time as a function of prospective current (RMS symmetrical for AC) up to rated short-circuit breaking capacity (`Figure K.1`, `8.2.1.2.4` item a).
- **Resetting time (`3.14`)**: time elapsed between overcurrent tripping and reaching a condition where the circuit-breaker can be reclosed.
- **Tripping settings & symbols (`3.15`–`3.17`, `Table K.1`, `Figure K.1`)**:
  - $I_r$ / $t_r$ (`3.16`, `5.7.3`, `Figure K.1`): overload current setting and corresponding tripping time.
  - $I_{sd}$ / $t_{sd}$ (`3.17`, `Figure K.1`): short-time pick-up current setting and corresponding intentional time-delay (`ST`: $i^2t$ and non-$i^2t$ curves in `Figure K.1`).
  - $I_i$ / $t_i$ (`3.15`, `5.7.3`, `Figure K.1`): instantaneous short-circuit current setting and maximum corresponding tripping time (`INST`).
  - $I_g$ / $t_g$ (`Figure K.1`, `Table K.1`): ground-fault current setting and corresponding tripping time (`GF`).
- **PLC Digital I/O (`3.18`, `8.1.8`)**: `programmable logic controller (PLC)` defined in `3.18`; digital inputs and outputs of a circuit-breaker (or its electronic trip unit) intended for use with PLCs shall comply with `8.1.8` (referencing Annex S of IEC 60947-1:2020).

### 3.2 Electronic Overcurrent, Coordination & Residual Annexes (`Annex F`, `Annex K`, `Annex A`, `Annex B/M`)
- **Annex F — Electronic overcurrent protection (supplementary type tests)**: applies to line-voltage/auxiliary-supply-independent electronic overcurrent protection (`F.1`), covering EMC immunity (`F.2.2` -> `Table J.1` & `Table J.3`: Criterion A requires no trip at `0,9` × current setting and tripping within `0,9`–`1,1` × curve at `2,0` × current setting), suitability for multiple frequencies (`F.6`), dry heat (`F.7`), damp heat (`F.8`), and temperature variation cycles (`F.9`).
- **Annex K — Glossary & Graphical Characteristics**: `Table K.1` defines all standardized protection and rating symbols; `Figure K.1` maps the five tripping zones (`RC`, `GF`, `LT`, `ST`, `INST`) and $i^2t$ vs non-$i^2t$ characteristics.
- **Annex A — Coordination (`A.5`, `A.6`, `5.4`, `8.2.7`, `9.3.8`)**: `Selectivity` (`A.5`, never "discrimination") and `back-up protection` (`A.6`, combined short-circuit protection). Key coordination quantities in `Table K.1` are selectivity limit current $I_s$ (`8.2.7`) and take-over current $I_B$ (`9.3.8`). Selectivity category B circuit-breakers declare $I_{\text{cw}}$ and short-time delay per `5.4` & `5.3.6.4`.
- **Annex B (CBRs) & Annex M (MRCDs)**: residual current protection using $I_{\Delta n}$ (rated residual operating current), $I_{\Delta no}$ (non-operating current), $I_{\Delta m}$ (residual short-circuit making and breaking capacity), and $\Delta t$ (limiting non-actuating time at $2\,I_{\Delta n}$); Type AC, Type A, and Type B waveforms (`Table K.1`).

---

## 4. Native Phrasing Guardrails for Trip Unit Specifications

- **Measurement & Threshold Limitations**:
  - ❌ *"Below {threshold}, the measurement is inaccurate."*
  - ✅ **"Measurement unspecified below `{{metering_threshold: A}}`"** (or *"Accuracy unspecified below `{{metering_threshold: A}}`"*).
  - Always quote the threshold as a slot; never soften it into a vague qualitative remark.
- **Protection Descriptions**:
  - ❌ *"Ig light lights up when there is ground leak."*
  - ✅ **"The Ig indicator illuminates upon detecting an earth fault."**
- **Range Statements**:
  - ✅ Write the setting range as `{{Isd_setting: ×Ir}}` and name its upper current cap separately in the same sentence, so a translator cannot drop the cap.
- **IEC 60947-2:2024 Lexical Guardrails**:
  - Always hyphenate `circuit-breaker`, `pick-up` (or `short-time pick-up`), `time-delay` (attributive), `making-current release`, `back-up`, and `let-through` / `cut-off`.
  - Always use `selectivity` (never `discrimination`) and `earth-fault` (keep `ground-fault` only when quoting IEC `5.7.1`/`Table K.1` `ground-fault` or explicit North American / UL / ANSI context).

---

## 5. Ordering of Values in a Protection Sentence

When a sentence carries several quantities, keep this order so translations do not reshuffle them:
pick-up → time-delay → curve shape ($I^2t$ ON/OFF) → reset/return condition (`resetting time`) → accuracy tolerance.
