# MCCB & Special Circuit-Breakers Technical Taxonomy & Standards Reference (v2.0.0)

> **Authoritative Baseline**: `IEC 60947-2:2024` (Edition 6.0, 2024-09) — *Low-voltage switchgear and controlgear — Part 2: Circuit-breakers* (English text, printed pages 1–276).
> **Complementary Standards**: `GB/T 14048.2`, `UL 489` / `CSA C22.2 No. 5` (North American equivalents).

---

## 0. Value-Slot & Orthography Convention

1. **Value-Slot Invariant**: Every product rating below is a template slot: `{{param_name: unit}}`. Slots resolve strictly from the datasheet for the exact product model in scope; **zero hardcoded product ratings** live in this file. Numeric values cited below (e.g. `Table 1`, `Table 2`, `Table 5`, `Table 6`, `Table 7`, `Table P.1`, `30 mA`, `6 mA`, `1 500 V DC`) are **standard-fixed normative thresholds or test conditions** in `IEC 60947-2:2024`, never product datasheet claims.
2. **IEC 60947-2:2024 Single-Track British + `-ize` Orthography (Track 1 & Track 2)**:
   - Outside the explicit `North American (UL 489)` and `❌ Forbidden` columns, every deliverable under `IEC 60947-2:2024` uses verified standard spelling and hyphenation:
     - `circuit-breaker` (hyphenated), `moulded case` / `moulded-case circuit-breaker` (`IEC 60947-2:2024` uses `circuit-breaker` 667× and `moulded case` 1× in `Cl. 9.3.3.3`; no separate `moulded-case` classification exists in `IEC 60947-2`)
     - `withdrawable` (18×; `draw-out` appears 1× only for the cradle in `Fig. J.1`, P182)
     - `utilisation`, `colour` (8×), `aluminium` (45×)
     - `undervoltage` (36× vs 4× `under-voltage`), `shunt release` (25×; 0× `shunt opening release`), `closing release` (13×; `closing coil` 1× as admitted synonym in `Cl. 3.19`)
     - `energized` / `energizing` / `energization` (`energiz*` 37×; 0× `energis*`)
     - `selectivity` (40×; 0× `discrimination`), `back-up` (4×), `let-through` (21×), `cut-off` (9×)
     - `operational performance capability` (`operational performance` 40×), `operating cycles` (23×), `endurance` (9×, used in Annexes B, M, R — `M.8.11`, `R.8.5`); **0 occurrences of `durability`** in `IEC 60947-2:2024`
   - North American spellings (`Molded-Case Circuit Breaker`, `Molded Case`, `Drawout`, `Shunt Trip`, `Undervoltage Trip`, `Color`, `Aluminum`, `Utilization`, `Discrimination`) are permitted **only** inside the `North American (UL 489)` column or the `❌ Forbidden` column.

---

## 1. Product Taxonomy & IEC 60947-2:2024 Classification

### 1.1 Primary Standards & Product Line Slots

- **Primary Standards**: `IEC 60947-2:2024` (`Cl. 1`, P17), `GB/T 14048.2`, `UL 489` (North American MCCB standard).
- **Product Line Taxonomy** (resolve series names and ratings from the current catalogue, never from memory):
  - **Standard industrial and commercial distribution line**: frame size `{{frame_size: A}}`, rated current `{{In_range: A}}`.
  - **High-performance distribution line**: higher short-circuit breaking capacity for infrastructure and data-centre duty; frame size `{{frame_size_hp: A}}`, rated current `{{In_range_hp: A}}`.
  - **North American listed line**: `UL 489` listed MCCBs, rated current `{{ul_In_range: A}}` (use the `North American (UL 489)` column nomenclature below for US deliverables).

### 1.2 Core Structural Definitions (`Cl. 3`, P19–20 & `Cl. 8.1`, P33–34)

| Clause | Exact IEC 60947-2:2024 Term | Printed Page | Normative Definition & Technical Clarification |
| :--- | :--- | :--- | :--- |
| **3.1.1** | **frame size** | P20 | Group of circuit-breakers whose external physical dimensions are common to a range of current ratings; expressed in amperes corresponding to the **highest current rating of the group** (Note 1; width may vary by pole count, Note 2; does not imply dimensional standardization, Note 3). **GB/T 14048.2 Clarification**: `Inm` (壳架等级额定电流) has **0 occurrences** in `IEC 60947-2:2024`, which instead states *"maximum rated current for a given frame size"* (e.g. `Table 7` footnote a, P40). |
| **3.1.2** & **8.1.6** | **construction break** | P20, P33–34 | Significant difference in construction between circuit-breakers of a given frame size requiring additional type testing (`8.1.6` defines breaks: internal current-carrying parts, main contacts, manual operating mechanism, moulding/insulating materials, arc extinction device, basic overcurrent tripping device design; excludes variations `a)–i)` such as terminal dimensions, thermal/magnetic rating dimensions, CT secondary windings, external operating means, labels, unprotected neutral link, 2P from 3P centre-pole removal, non-tripping firmware, omitted PCB UI components). |
| **3.2** | **integrally fused circuit-breaker** | P20 | Combination in a single device of a circuit-breaker and fuses, one fuse in series with each line pole (`5.8`, P30; `8.2.7`, P40; Test Sequence V, `9.3.8`, P72). |
| **3.3** | **current-limiting circuit-breaker** | P20 | Prevents let-through current reaching the prospective peak value and limits let-through energy ($I^2t$) below that of a half-cycle symmetrical prospective wave; let-through current is also termed **cut-off current** (`Figures K.2–K.7`, P190–195). |
| **3.4** | **plug-in circuit-breaker** | P20 | Incorporates an additional set of contacts enabling removal of the circuit-breaker (may be plug-in on line side only, Note 1). |
| **3.5** & **8.1.2** | **withdrawable circuit-breaker** | P20, P33 | Incorporates additional isolating contacts enabling withdrawal from the main circuit and achieving a specified **isolating distance** in the disconnected position; requires position indication and mechanical interlocks (`8.1.2`). |

### 1.3 Clause 4 Classification (`Cl. 4.1–4.5`, P23)

| Subclause | Classification Axis | IEC 60947-2:2024 Categories & Cross-References |
| :--- | :--- | :--- |
| **4.1** | **Selectivity category** | **Category A** (all other circuit-breakers; may have intentional delay $< 5.3.6.4$ if tested per Sequence IV) or **Category B** (`5.4`, P27: assigned $I_{\text{cw}}$ and short-time delay $\ge 0{,}05\text{ s}$ per `5.3.6.4` & `Table 2`, P27 — preferred delays `0,05 s – 0,1 s – 0,25 s – 0,5 s – 1 s`; min $I_{\text{cw}} = 12\,I_n$ or `5 kA` for $I_n \le 2\,500\text{ A}$, `30 kA` for $I_n > 2\,500\text{ A}$). |
| **4.2** | **Method of controlling the operating mechanism** | **Dependent manual operation** (`8.2.1.1.2`, P34: not recommended for prospective peak making current $> 10\text{ kA}$ unless fitted with integral fast-acting opening release); **Independent manual operation** (`8.2.1.1.3`, P35); **Dependent power operation** (`8.2.1.1.4`, P35); **Independent power operation** (`8.2.1.1.5`, P35); **Stored energy operation** (`8.2.1.1.6`, P35). |
| **4.3** | **Provision for maintenance** | **Maintainable**; **Non-maintainable** (typical sealed moulded-case MCCBs). |
| **4.4** | **Method of installation** | **Fixed**; **Plug-in**; **Withdrawable**. |
| **4.5** | **Degree of protection by enclosure** | IP code in accordance with `IEC 60947-1:2020, 8.1.12` (`{{IP_code}}`). |

---

## 2. Releases, Tripping Characteristics & Setting Parameters

### 2.1 Release Definitions & Characteristics (`Cl. 3.6–3.19`, P20–22; `Cl. 5.7`, P28–30; `Cl. 8.2.1.2`, P36–37)

- **Release Types (`5.7.1`, P28)**:
  1. **Shunt release** (`8.2.1.2.3`, P36).
  2. **Overcurrent release**: a) instantaneous; b) definite time-delay; c) inverse time-delay (independent of previous load, or dependent on previous load such as thermal type); d) ground-fault (`8.2.1.2.4 c)`, P37: detection types `CI-A` or `CI-B` per `IEC 60947-1:2020 Annex T`). Note 1 distinguishes **overload release** vs **short-circuit release** (`3.7`, P20; includes **short-time delay short-circuit release**, `3.8`, P21); Note 2 includes interchangeable releases under "adjustable release".
  3. **Undervoltage release** (for opening, `8.2.1.2.2`, P36).
  4. **Closing release** (`3.19`, P22; admitted synonym: `closing coil` — auxiliary device energized by a voltage source triggering closing).
  5. **Other releases** — including **making-current release** (`3.6`, P20: opens without intentional time-delay during closing if making current exceeds threshold, rendered inoperative once closed).
- **Control Supply & Settings (`5.5.1`, `Table 3`, `5.7.2–5.7.4`, P28–30)**:
  - Preferred control supply voltages $U_c$ (`Table 3`, P28): DC `24 – 48 – 110 – 125 – 220 – 250 V`; 1-phase AC `24 – 48 – 110 – 127 – 220 – 230 V`.
  - Current settings (`5.7.3`, P29) may be marked on the release or shown on the release/external display (readable regardless of breaker status); local or remote external adjustment is permitted provided local indications are not exceeded or remote control is locally indicated.
  - **Reference ambient air temperature (`5.7.3`, P29)**: thermal releases are calibrated at `+30 °C ± 2 °C`; non-thermal temperature-independent releases operate across `-5 °C` to `+40 °C` (or manufacturer-declared band $\ge \pm 10\text{ K}$ around reference temperature within `0,3 %/K` per `8.2.1.2.4 b)`, P37).
- **Opening Tolerances & Inverse Time-Delay (`8.2.1.2.4` & `Table 5`, P36–37)**:
  - **Short-circuit release**: tripping tolerance `±20 %` of current setting; manufacturer provides max cut-off (let-through) peak current and $I^2t$ characteristic curves (`3.13`, P21; Category A, and Category B with instantaneous override).
  - **Instantaneous / definite time-delay overload release**: tripping tolerance `±10 %`.
  - **Inverse time-delay overload release (`Table 5`, P36)**: all phase poles loaded from cold state at reference temperature — conventional non-tripping current **$1{,}05 \times I_{\text{set}}$** (shall not trip in less than conventional time); conventional tripping current **$1{,}30 \times I_{\text{set}}$** (shall trip in less than conventional time); **conventional time** = `2 h` (`1 h` for $I_n \le 63\text{ A}$).
  - **Opening time vs tripping time (`3.12` Note 2, P21)** and **resetting time (`3.14`, P22)**: distinguish total opening time (initiation to arcing-contact separation in all poles) from tripping time, and declare resetting time after overcurrent tripping.

### 2.2 Release & Trip Unit Types (ZH ↔ IEC / UL Mapping)

| Chinese Term | Standard IEC English (`IEC 60947-2:2024`) | North American (`UL 489`) | Function & Slots |
| :--- | :--- | :--- | :--- |
| **热磁式脱扣器** | **Thermal-magnetic overcurrent release / Thermal-magnetic trip unit (TM)** | Thermal-Magnetic Trip | Bimetallic thermal overload (`5.7.1 2c`) + magnetic short-circuit protection (`3.7`). Fixed (`TM-D`) or adjustable (`TM-A`); reference temp `{{ref_temp: °C}}`. |
| **电子式脱扣器 / 智能脱扣器** | **Electronic overcurrent release / Electronic trip unit (ETU)** | Electronic Trip Unit | Microprocessor-based release (`Annex F`) providing L/S/I/G protection curves and optional PLC I/O (`3.18`, `8.1.8`). |
| **单磁式脱扣器 / 瞬时脱扣断路器** | **Instantaneous short-circuit release / Instantaneous trip circuit-breaker (ICB)** (`Annex O`) | Instantaneous-Only / Motor Circuit Protector (MCP) | Short-circuit protection only (no thermal overload release), co-ordinated with motor-starters / overload relays (`O.1`, `O.6.2`). |
| **剩余电流保护脱扣器 (漏电)** | **Residual current protection release / Circuit-breaker incorporating residual current protection (CBR)** (`Annex B`) | Ground-Fault / ELCB Module | Integral or combined residual current protection (`IΔn` = `{{I_delta_n: mA}}`); see §5 Annex B & Annex M. |

### 2.3 Setting Parameters & Value Slots (`Cl. 3.15–3.17`, P22; `Fig. K.1`, P189)

| Chinese Term | Standard IEC English (`IEC 60947-2:2024`) | North American (`UL 489`) | Symbol | Setting Slot |
| :--- | :--- | :--- | :--- | :--- |
| **过载长延时整定电流 / 时间** | **Overload current setting** / Tripping time (`3.16`, `Fig. K.1`) | Long-time pickup / Long-time delay | $I_r$ / $t_r$ | `{{Ir_setting: ×In}}` / `{{tr_setting: s}}` |
| **短路短延时整定电流 / 延时** | **Short-time pick-up current setting** / Intentional time-delay (`3.8`, `3.17`) | Short-time pickup / Short-time delay | $I_{sd}$ / $t_{sd}$ | `{{Isd_setting: ×Ir}}` / `{{tsd_setting: s}}` |
| **短路瞬时整定电流 / 动作时间** | **Instantaneous short-circuit current setting** / Max tripping time (`3.15`) | Instantaneous trip setting | $I_i$ / $t_i$ | `{{Ii_setting: ×In}}` / `{{ti_max: ms}}` |
| **接地故障整定电流 / 延时** | **Ground-fault current setting** / Corresponding tripping time (`8.2.1.2.4 c)`, `Fig. K.1`) | Ground-fault pickup / delay | $I_g$ / $t_g$ | `{{Ig_setting: ×In}}` / `{{tg_setting: s}}` |
| **额定剩余动作电流 / 极限不驱动时间** | **Rated residual operating current** / Limiting non-actuating time (`Annex B`) | Ground-fault trip sensitivity | $I_{\Delta n}$ / $\Delta t$ | `{{I_delta_n: A}}` / `{{delta_t: s}}` |
| **额定控制电路电源电压** | **Rated control circuit supply voltage** (`5.5.1`, `Table 3`) | Control voltage | $U_c$ | `{{Uc: V}}` |

---

## 3. Marking, Product Information & Test Sequences

### 3.1 Product Information & Marking (`Cl. 6` & `Table 4`, P30–32)

| Location Key (`Table 4`) | Mandatory Items (`IEC 60947-2:2024`) | Notes & Standard Symbol IDs |
| :--- | :--- | :--- |
| **Visible** (when installed in service, items `1.1–1.3`) | Rated current $I_n$ (`1.1`); suitability for isolation (`1.2`); open/closed position (`1.3`). | Isolation: `IEC 60617-S00287` + `S00220` (`O`/`I`: `IEC 60417-5008` / `5007`). |
| **Marked** (on circuit-breaker, items `2.1–2.21`) | Manufacturer/trademark, type designation, `IEC 60947-2`, selectivity category `A` or `B`, $U_e$, not-for-IT symbol (`2.6`), $U_{\text{imp}}$, frequency / `"DC"` (`2.8`), $I_{\text{cs}}$, $I_{\text{cu}}$, $I_{\text{cu1}}$ (`2.11`, if $\ne I_{\text{cu}}$), $I_{\text{cw}}$ & short-time delay (`2.12`, Cat B), settings $I_r$/$I_{sd}$/$t_{sd}$/$I_g$/$I_i$ (or displayed per footnote a), ref temp if $\ne 30\,^\circ\text{C}$, terminals, N pole, PE terminal (`2.21`). | Not-for-IT: crossed-out `IT` (`IEC 60417-6363:2016-07`); DC symbol: `IEC 60417-5031:2002-10`; PE symbol: `IEC 60417-5019:2006-08`. |
| **Literature** (`3.1–3.19` & `6.1`, `6.3`) | Typical power losses per frame size (`6.1`, `Annex G`); ambient/derating curves; mounting/clearing distances; **decommissioning and dismantling instructions** for foreseeable hazards such as stored energy or hazardous substances (`6.3`, P32). | Normal service default: **pollution degree 3** (`Cl. 7`, P32). Glow-wire (`8.1.1`, P32): `960 °C` (main circuit retaining parts) / `850 °C` (other circuits). |
| **Aux** (`4.1–4.4`) | Rated control voltage $U_c$, current kind/frequency of shunt/undervoltage releases (`4.2`); indirect release current (`4.3`); auxiliary contact types & ratings (`4.4`). | Marked on auxiliaries or breaker, plus literature. |

### 3.2 Core Performance Limits (`Table 1`, `Table 6`, `Table 7`)

- **Short-Circuit Making/Breaking Ratio $n$ & Power Factor (`5.3.6.1`, `5.3.6.3`, `Table 1`, P25–26)**: AC $I_{\text{cm}} \ge n \times I_{\text{cu}}$ (`1,41` at $\le 1{,}5\text{ kA}$, $\cos\varphi = 0{,}95$; up to `2,2` at $> 50\text{ kA}$, $\cos\varphi = 0{,}2$); DC $I_{\text{cm}} \ge I_{\text{cu}}$; **$I_{\text{cs}} \ge 25\%$ of $I_{\text{cu}}$** (`5.3.6.2.4`, P26).
- **Temperature-Rise Limits (`8.2.2`, `Table 6`, P38)**: External connection terminals `80 K`; manual operating means `25 K` metallic / `35 K` non-metallic; parts intended to be touched `40 K` / `50 K`; non-touched parts `50 K` / `60 K`.
- **Overload & Operational Performance Capability (`8.2.4`, `Table 7`, P39–40)**:
  - Overload performance (`8.2.4.1`) applies up to and including $I_n = 630\text{ A}$.
  - Operational performance capability (`8.2.4.2`, `Table 7`, P40) — total **operating cycles** ($I_n$ = max rated current for a given frame size, footnote a):
    - $I_n \le 100\text{ A}$: `120` cycles/h (`8 500` without + `1 500` with current = `10 000`)
    - $100 < I_n \le 315\text{ A}$: `120` cycles/h (`7 000` without + `1 000` with current = `8 000`)
    - $315 < I_n \le 630\text{ A}$: `60` cycles/h (`4 000` without + `1 000` with current = `5 000`)
    - $630 < I_n \le 2\,500\text{ A}$: `20` cycles/h (`2 500` without + `500` with current = `3 000`)
    - $I_n > 2\,500\text{ A}$: `10` cycles/h (`1 500` without + `500` with current = `2 000`)

### 3.3 Type, Routine, Special Tests & Sequences I–VIII (`Cl. 9`, P41–81)

- **Test Categories (`9.1`, P41)**: **Type tests** (`9.3`, `Table 8`, P41; alphabetical index in `Table 9`, P43); **Routine tests** (`9.4`, P78–80: mechanical operation, overcurrent calibration, undervoltage/shunt release operation, CBR tests, dielectric tests, reduced clearances); **Special tests** (`9.5`, P81: damp heat, salt mist, vibration, shock).
- **Test Sequences (`Table 10`, P44–45; `Table 11`, P46; `9.3.4–9.3.11`, P58–78)**:

| Sequence | Subclause & Page | Applicability | Key Tests & IEC 60947-2:2024 Specifics |
| :--- | :--- | :--- | :--- |
| **Seq I** | `9.3.4` (P58) | All circuit-breakers | Tripping limits (`9.3.4.2`), dielectric (`9.3.4.3`), mechanical & operational performance (`9.3.4.4`), overload performance (`9.3.4.5`), temperature-rise (`9.3.4.7`), release & contact-position verification. |
| **Seq II** | `9.3.5` (P68) | All CBs (unless replaced by Seq VI) | Rated service short-circuit breaking capacity $I_{\text{cs}}$, operational performance, dielectric + leakage, temperature-rise, overload verification. |
| **Seq III** | `9.3.6` (P69) | Cat A, and Cat B with instantaneous override (except $I_{\text{cs}} = I_{\text{cu}}$, Seq VI, or integrally fused) | Overload verification, rated ultimate short-circuit breaking capacity $I_{\text{cu}}$, dielectric + leakage, overload verification. |
| **Seq IV** | `9.3.7` (P71) | Cat B, and Cat A with assigned $I_{\text{cw}}$ (unless Seq VI applies) | Rated short-time withstand current $I_{\text{cw}}$, temperature-rise, breaking capacity at max $I_{\text{cw}}$, dielectric + leakage, overload verification. |
| **Seq V** | `9.3.8` (P72) | Integrally fused circuit-breakers | Stage 1: selectivity limit current $I_s$; Stage 2: $1{,}1\,I_B$ take-over current & $I_{\text{cu}}$, dielectric, overload verification. |
| **Seq VI** | `9.3.9` (P74) | Cat B combined sequence | $I_{\text{cw}} = I_{\text{cs}}$ replaces II + IV; $I_{\text{cw}} = I_{\text{cs}} = I_{\text{cu}}$ replaces II + III + IV. |
| **Seq VII** | `9.3.10` (P76–77) | Circuit-breakers with **DC ratings** | **Critical DC load current**: tested at $U_{e\,\max}$ DC across `4 A, 8 A, 16 A, 32 A, 63 A DC` (extended by `2×` up to $I_n$ if needed), `5` operations per current (or `5` forward + `5` reverse if unpolarized), arcing time $\le 1\text{ s}$, followed by `50` operational performance cycles at the critical current. |
| **Seq VIII** | `9.3.11` (P77–78), `5.3.6.2.3` (P26) | AC circuit-breakers with unequal pole designs | **Rated individual pole ultimate short-circuit breaking capacity at phase-to-neutral AC voltage ($I_{\text{cu1}}$)**; if all phase poles share the same design, $I_{\text{cu1}} = I_{\text{cu}}$ (`9.3.11.1`). |
| **Annex C / H** | `C.2–C.4` (P130), `H.2–H.4` (P172–173) | Phase-earthed systems / IT systems | Individual pole short-circuit sequences ($I_{\text{su}}$ / $I_{\text{IT}}$); see §5. |

---

## 4. Co-ordination, Selectivity & Back-up Protection (`Cl. 8.2.8`, P41 & `Annex A`, P84–85)

- **Normative Scope (`Annex A`, P84–85)**: Adapts `IEC 60947-1:2020 Annex X` (`X.1–X.6`) to circuit-breakers associated with another **short-circuit protective device (SCPD)** in the same circuit, replacing $I_{\text{cn}}$ with **$I_{\text{cu}}$** (`5.3.6.2.2`).
- **Key Co-ordination Concepts & Bilingual Terms**:

| Chinese Term | IEC 60947-2:2024 Standard English | Symbol / Clause | Technical Meaning |
| :--- | :--- | :--- | :--- |
| **上下级配合 / 协调配合** | **Co-ordination between a circuit-breaker and another SCPD** | `8.2.8`, `Annex A` (P84) | Overall overcurrent/short-circuit co-ordination using cut-off peak and $I^2t$ curves (`8.2.1.2.4 a)`, `A.3`). |
| **选择性 (完全/局部)** | **Selectivity (Total selectivity / Partial selectivity)** | `A.5` (P84), `5.4` (P27) | Downstream SCPD clears faults up to $I_s$ without upstream CB tripping (never use *discrimination*). |
| **选择性极限电流** | **Selectivity limit current** | $I_s$ (`8.2.7`, `A.5`, `Table K.1`) | Current value separating selective operation from non-selective tripping of upstream CB/fuse. |
| **后备保护 (级联)** | **Back-up protection** *(IEC 60364-5-53: "Combined short-circuit protection")* | `A.6` (P84) | Upstream SCPD assists downstream CB above its standalone $I_{\text{cu}}$; includes `Figure A.1` (P85) for conditional $I_{\text{cu1}}$ verification (`9.3.11`). |
| **交接电流** | **Take-over current** | $I_B$ (`9.3.8`, `Table K.1`) | Prospective current where integral fuse / upstream SCPD takes over interruption from the CB (`9.3.8.6`: tested at $1{,}1\,I_B$). |
| **额定限制短路电流** | **Rated conditional short-circuit current** | $I_{\text{cc}}$ (`Annex L`, `Annex M`, `Table K.1`) | Prospective short-circuit current sustainable when protected by a specified upstream SCPD/OCPD. |

---

## 5. Full Normative & Informative Annexes Terminology Matrix (Annexes A–R)

### 5.1 Complete Annex Inventory (`IEC 60947-2:2024`)

| Annex | Status | Exact 2024 Title | Printed Pages | Primary Domain |
| :--- | :--- | :--- | :--- | :--- |
| **Annex A** | Normative | Coordination between a circuit-breaker and another short-circuit protective device associated in the same circuit | P84–85 | Selectivity & back-up protection (§4) |
| **Annex B** | Normative | Circuit-breakers incorporating residual current protection (CBRs) | P86–129 | Integral / combined residual current CBs |
| **Annex C** | Normative | Individual pole short-circuit test sequence | P130 | Phase-earthed systems (`C` prefix, $I_{\text{su}}$) |
| **Annex D** | Normative | Additional requirements for circuit-breakers intended for connection of aluminium conductors | P131–142 | Aluminium cable & busbar terminals |
| **Annex E** | Informative | Items subject to agreement between manufacturer and user | P143 | Special ratings & agreement items |
| **Annex F** | Normative | Additional tests for circuit-breakers with electronic overcurrent protection | P144–166 | Electronic trip unit immunity & climate |
| **Annex G** | Normative | Power loss | P167–171 | Free-air power loss measurement (W) |
| **Annex H** | Normative | Test sequence for circuit-breakers for IT systems | P172–173 | IT earthing systems ($I_{\text{IT}}$, crossed-out `IT`) |
| **Annex I** | **Vacant** | Vacant | P174 | Reserved (vacant in 2024 Ed. 6.0) |
| **Annex J** | Normative | Electromagnetic compatibility (EMC) — Requirements and test methods for circuit-breakers | P175–186 | Master EMC immunity & emission tables |
| **Annex K** | Informative | Glossary of symbols and graphical representation of characteristics | P187–195 | `Table K.1`, `Fig. K.1`, `Fig. K.2–K.7` |
| **Annex L** | Normative | Circuit-breakers not fulfilling the requirements for overcurrent protection (CBIs) | P196–202 | CBI Class W, Class X, Class Y |
| **Annex M** | Normative | Modular residual current devices (without integral current breaking device) | P203–249 | MRCDs (relay + core-balance CT) |
| **Annex N** | Normative | Electromagnetic compatibility (EMC) — Additional requirements and test methods for devices not covered by Annex B, Annex F and Annex M | P250–253 | EMC for shunt/UVR/closing/motor auxiliaries |
| **Annex O** | Normative | Instantaneous trip circuit-breakers (ICBs) | P254–256 | Magnetic-only CBs for motor starters |
| **Annex P** | Normative | DC circuit-breakers for use in photovoltaic (PV) applications | P257–261 | PV DC CBs up to `1 500 V DC` |
| **Annex Q** | **Vacant** | Vacant | P262 | Reserved (vacant in 2024 Ed. 6.0) |
| **Annex R** | Normative | Circuit-breakers incorporating residual current protection with automatic reclosing functions (CBARs) | P263–273 | Auto-reclosing CBRs (Type M / Type TD) |

### 5.2 Annex B — CBRs (`P86–129`)

- **Scope (`B.1`)**: Integral CBRs and factory/field-combined CB + residual current units for AC circuits; `B.1.1` notes $I_{\Delta n} \le 30\text{ mA}$ provides additional basic protection.
- **Classification (`B.3`, P90)**:
  - **Operation method (`B.3.1`)**: **CBR functionally independent of line voltage** (`B.3.1.1`) vs **CBR functionally dependent on line voltage** (`B.3.1.2`: opening automatically on line-voltage failure `B.3.1.2.1`, or not opening automatically `B.3.1.2.2`).
  - **Adjustability (`B.3.2`)**: single $I_{\Delta n}$ vs multiple settings (fixed steps / continuous).
  - **Time delay (`B.3.3`)**: non-time-delayed type vs **time-delay CBR** (`B.2.3.8`; non-adjustable or adjustable; `B.4.2.4.1`, P91: $I_{\Delta n} = 30\text{ mA}$ shall be non-time-delay).
  - **DC component behaviour (`B.3.4`, `B.4.4`, P90)**: **Type AC**, **Type A**, and **Type B** (tested up to `1 000 Hz` in `B.8.8`). *Boundary Note*: **Type F** and **Type B+** are outside `IEC 60947-2:2024` and belong to `IEC 62423` / `VDE 0664-400`.
- **Key Symbols & Requirements (`B.4`, P90–91; `B.7.2.6`, P96)**:
  - **$I_{\Delta n}$**: rated residual operating current (preferred `0,006 – 0,01 – 0,03 – 0,1 – 0,3 – 0,5 – 1 – 3 – 10 – 30 A`, `B.4.2.1`).
  - **$I_{\Delta no}$**: rated residual non-operating current (min `0,5 IΔn`, `B.4.2.2`).
  - **$I_{\Delta m}$**: rated residual short-circuit making and breaking capacity (`B.4.1.3`).
  - **$\Delta t$**: limiting non-actuating time at $2\,I_{\Delta n}$ (`B.2.3.7`, `Table K.1`).
  - **Test device `T`** (`B.7.2.6`, P96): designated by letter `T`; **colour shall not be red or green** (light colour preferred).
  - **Crossed-out `1~`** (`Table B.3` item B2.3, `IEC 60417-6364:2016-07`): CBRs for 3-phase supply only.

### 5.3 Annex C & Annex H — Individual Pole Short-Circuit (`P130`, `P172–173`)

| Annex | System Application | Marking & Key Symbol | Test Current & Sequence | Post-Test Acceptance |
| :--- | :--- | :--- | :--- | :--- |
| **Annex C** (Normative, P130) | **Phase-earthed systems** (`5.3.2.1`) | Marked with `C` prefix on $U_e$; **$I_{\text{su}}$** | $I_{\text{su}} = 25\%\,I_{\text{cu}}$ (or higher declared) at phase-to-phase voltage; $\text{O} - t - \text{CO}$ per pole (`C.2`). | Dielectric withstand + leakage current $\le 6\text{ mA}$ (`C.3`); overload release verification (`C.4`). |
| **Annex H** (Normative, P172–173) | **IT systems** (`5.3.2.1`, second fault to earth in presence of first fault) | **$I_{\text{IT}}$**; voltages *not* suitable marked with crossed-out `IT` (`IEC 60417-6363:2016-07`, `Table H.2`, P173) | $I_{\text{IT}} = 1{,}2\times$ max short-time delay setting (or instantaneous / definite-time setting), bounded $500\text{ A} \le I_{\text{IT}} \le 50\text{ kA}$; $\text{O} - t - \text{CO}$ per pole (`H.2`). | Dielectric withstand + leakage current $\le 6\text{ mA}$ (`H.3`); overload release verification (`H.4`). |

### 5.4 Annex D — Aluminium Conductors (`P131–142`)

- **Scope (`D.1`, P131)**: Solid/stranded aluminium conductors and aluminium bars $\ge 10\text{ mm}^2$ (integral or accessory terminals). Excludes screwless terminals, flexible aluminium conductors, and simultaneous aluminium + copper in one clamping unit.
- **Classification & Marking (`D.3`, `D.5.2`, P132)**: Copper only; copper or aluminium (`AL/CU` or `CU/AL`); aluminium only (`AL`). Literature specifies conductor count, tightening torque, solid/stranded type, cross-section, and surface prep (wire brushing + anti-oxidant compound / tin coating, `D.5.3`).
- **Key Terms & Verification Tests (`D.2`, P131; `D.8`, P133–139)**: **Reference conductor** (`D.2.1`), **equalizer** (`D.2.2`), **stability factor $S$** (`D.2.3`); **current cycling test** (`D.8.2`, P134), **climatic test** (`D.8.3`, P138), **mechanical properties** (`D.8.4` flexion & pull-out, P139), and **insertability of unprepared round aluminium conductors** having maximum cross-section (`D.8.5`, P139).

### 5.5 Annex E — Items Subject to Agreement (`P143`)

- **Informative (`Table E.1`, P143)**: Supplements `IEC 60947-1:2020 Annex J` with CB-specific agreement items: higher $I_{\text{cm}}$ (`5.3.6.3`), $U_{\text{imp}} > 1\,000\text{ V AC}$, 4th pole test current (`9.3.3.6.4.3`), special tests (`9.5` damp heat/salt mist/vibration/shock), CBRs with $I_{\Delta n} > 30\text{ A}$ (`B.4.2.1`), and aluminium test bars $> 3\,150\text{ A}$ (`D.8`).

### 5.6 Annex F, Annex J & Annex N — Electronic Overcurrent Protection & EMC (`P144–166`, `P175–186`, `P250–253`)

| Annex | Scope | Key Requirements & Test Matrix |
| :--- | :--- | :--- |
| **Annex J** (`P175–186`) | Master EMC requirements for circuit-breakers (`8.3`) | **Immunity (`Table J.1`, P176–177)**: ESD (`IEC 61000-4-2`, `8 kV` air / `4 kV` contact), Radiated RF fields (`IEC 61000-4-3`, `10 V/m` `80 MHz–1 GHz`, `3 V/m` `1,4–6 GHz`), EFT/B (`IEC 61000-4-4`, `4 kV`/`2 kV`), Surges (`IEC 61000-4-5`, `4 kV` L-E, `2 kV` L-L [Annex F/N] or `4 kV` L-L [Annex B/M]), Conducted RF (`IEC 61000-4-6`, `10 V`), Voltage dips/interruptions (`IEC 61000-4-11`). **Emissions (`Table J.3`, P181)**: `CISPR 11` / `CISPR 32` **Environment A (Class A)** vs **Environment B (Class B)** (`150 kHz–30 MHz` conducted; `30–6 000 MHz` radiated). |
| **Annex F** (`P144–166`) | Electronic overcurrent CBs independent of line voltage or auxiliary supply (`F.1`) | **EMC (`F.2.2`, `F.4`, `F.5`, P144–150)**: Harmonic currents (`F.4.1`), ESD (`F.4.2`), Radiated RF (`F.4.3`), EFT/B (`F.4.4`), Surges (`F.4.5`), Conducted RF (`F.4.6`), Current dips (`F.4.7`, `Table F.1`), Emissions (`F.5.1–F.5.4`). **Criterion A**: no trip at $0{,}9\,I_{\text{set}}$; trips within $0{,}9\text{–}1{,}1\times$ curve at $2{,}0\,I_{\text{set}}$. **Environmental (`F.6–F.9`, P150–152)**: **Suitability for multiple frequencies** (`F.6`), **Dry heat** (`F.7`), **Damp heat** (`F.8`), **Temperature variation cycles** at specified rate of change (`F.9`). |
| **Annex N** (`P250–253`) | Electronic circuits in CB auxiliaries not covered by Annex B, F, or M (`N.1.1`) | Covers **undervoltage releases**, **shunt releases**, **closing releases** (exempt if identical to shunt release), **motor-operators**, and **remote status indicators** (excludes communication modules). Devices (except closing releases) tested with CB closed (`N.2.1.1`); covers immunity (`N.2.2–N.2.7`) and emissions (`N.3.2–N.3.3`). |

### 5.7 Annex G — Power Loss (`P167–171`)

- **General (`G.1`, P167)**: Measured in free air on new samples at steady-state $I_n$, stated in **watts (W)** (`6.1`). Four-pole AC CBs tested without current in neutral pole (`G.4.1`, P169).
- **Determination Methods (`G.2`, P167–168)**:
  - **AC $> 400\text{ A}$ (`G.2.1`)**: **Power factor method** ($P = \sum \Delta U_k I_k \cos\varphi_k$, or wattmeter) or **Integral method** (at least 10 AC cycles; preferred above `1 000 A` for iron-core CT breakers).
  - **AC $\le 400\text{ A}$ (`G.2.2`)**: Any `G.2.1` method, or single-phase AC measurement without power factor ($P = \sum \Delta U_k I$).
  - **DC circuit-breakers (`G.2.3`)**: Measured with DC current per `G.2.2`.

### 5.8 Annex K — Glossary of Symbols & Graphical Representation (`P187–195`)

- **`Table K.1` (P187–188)**: Authoritative master symbol registry ($I_n$, $I_{\text{th}}$, $I_{\text{the}}$, $U_e$, $U_i$, $U_{\text{imp}}$, $U_c$, $U_s$, $U_n$, $I_{\text{cu}}$, $I_{\text{cu1}}$, $I_{\text{cs}}$, $I_{\text{cm}}$, $I_{\text{cw}}$, $I_{\text{cc}}$, $I_s$, $I_B$, $I_{\text{su}}$, $I_{\text{IT}}$, $I_r$/$t_r$, $I_{sd}$/$t_{sd}$, $I_i$/$t_i$, $I_g$/$t_g$, $I_{\Delta n}$, $I_{\Delta no}$, $I_{\Delta m}$, $\Delta t$, $I_{\Delta c}$, $I_{\Delta w}$, $I_{\Delta\text{ar}}$, `C`, `T`, isolation/earth/crossed-out `IT` & `1~`).
- **Graphical Characteristics (`P189–195`)**: `Figure K.1` (tripping zones: RC, GF, LT, ST [$i^2t$ and non-$i^2t$], INST); `Figures K.2–K.3` (cut-off current templates); `Figures K.4–K.5` (let-through energy $I^2t$ templates); `Figures K.6–K.7` (worked examples).

### 5.9 Annex L — CBIs (`P196–202`)

- **Scope (`L.1`, P196)**: **Circuit-breakers not fulfilling the requirements for overcurrent protection (CBIs)**, derived from an **equivalent circuit-breaker** (`L.2.1`, same frame size); capable of auxiliary tripping and isolation, cannot protect circuits alone.
- **Classification (`L.3`, P196–197)**:
  - **Class W**: Derived from selectivity Category B equivalent CB; used with external protection relays + sensors; marked $I_{\text{cu}} = I_{\text{cw}}$ (`L.4.3`). Isolation symbol: `S00287+S00220` (`Table L.1`, P198).
  - **Class X**: Integral non-adjustable instantaneous short-circuit releases for self-protection (no overload release); rated conditional short-circuit current **$I_{\text{cc}}$** (`L.4.2`, P197). Isolation symbol: `S00288`.
  - **Class Y**: No integral overcurrent releases; rated **$I_{\text{cc}}$** (`L.4.2`). Isolation symbol: `S00288`. (*Note*: `IEC 60947-2:2024` `L.4.2` & `Table K.1` designate rated conditional short-circuit current as **$I_{\text{cc}}$**, equivalent to $I_q$ in `IEC 60947-1`/`60947-4-1`.)
- **Product Information (`L.5`, `Table L.1`, P198)**: Visible marking `CBI-W`, `CBI-X`, `CBI-Y`, `CBI-X/W`, or `CBI-Y/W` (with $I_i$ where applicable); $I_n$ may be correlated to **utilisation category** `AC-22` (`L.4.1` Note, P197).

### 5.10 Annex M — MRCDs (`P203–249`)

- **Scope (`M.1`, P203)**: **Modular residual current devices (without integral current-breaking device)** comprising a current-sensing means and a processing device (`M.2.2.1`, P204), controlling a separate circuit-breaker.
- **Classification (`M.3`, P204–205)**:
  - **Primary conductor configuration (`M.3.1`)**: **Terminal type** (`M.3.1.1`: incoming/outgoing terminals and integral primary conductors) vs **Through-conductor type** (`M.3.1.2`: **sensing means and processing device combined** `M.3.1.2.1` vs **separated** `M.3.1.2.2`).
  - **Operation (`M.3.2`)**: Without voltage source (`M.3.2.1`) vs with voltage source (`M.3.2.2.1` auto-operating on source failure vs `M.3.2.2.2` non-auto-operating).
  - **DC component behaviour (`M.3.5`)**: **Type AC**, **Type A**, **Type B**; $I_{\Delta n} = 30\text{ mA}$ shall be non-time-delay (`M.4.2.1`, P206).
- **Key Symbols & Endurance (`M.4`, P205–207; `M.8.11`, P222)**: $U_n$ (monitored circuit), $U_s$ (voltage source), $I_{\text{cc}}$ (`M.4.3.1`), $I_{\Delta c}$ (`M.4.3.2` conditional residual short-circuit current), $I_{\Delta w}$ (`M.4.3.5` residual short-time withstand current), **combination time** (`M.2.2.2.2`); **`M.8.11` Verification of mechanical and electrical endurance** (P222).

### 5.11 Annex O — Instantaneous Trip Circuit-Breakers (`P254–256`)

- **Status**: **Normative** (active in `IEC 60947-2:2024`).
- **Scope (`O.1`, `O.2.1`, P254)**: **Instantaneous trip circuit-breakers (ICBs)** fulfilling only the short-circuit portion of overcurrent protection (instantaneous short-circuit releases, may be adjustable; no overload releases), derived from an **equivalent circuit-breaker** (same frame size) and used with motor-starters or overload relays (`IEC 60947-4-1`, `O.6.2`).
- **Ratings & Marking (`O.3–O.4`, `Table O.1`, P254–255)**: $I_n \le I_n$ of equivalent CB (`O.3.2`); $I_{\text{cm}}$ and $I_{\text{cu}}/I_{\text{cs}}$ may differ from equivalent CB (`O.3.3–O.3.4`), including higher association ratings (`O.6.2`, not marked on the ICB itself); visible initialism **`"ICB"`** and marked $I_i$ setting (`3.15`) in A or $\times I_n$.

### 5.12 Annex P — PV DC Circuit-Breakers (`P257–261`)

- **Scope (`P.1`, P257)**: DC circuit-breakers rated up to **`1 500 V DC`** for photovoltaic (PV) applications (**"PV circuit-breakers"**). Dual-purpose breakers shall have only one $I_n$ (`P.4`).
- **Required $U_{\text{imp}}$ (`P.4`, `Table P.1`, P257 — OVC II)**: $U_e \le 300\text{ V} \to 2\,500\text{ V}$; $U_e \le 600\text{ V} \to 4\,000\text{ V}$; $U_e \le 1\,250\text{ V} \to 6\,000\text{ V}$; $U_e \le 1\,500\text{ V} \to 8\,000\text{ V}$.
- **Marking & Environment (`P.5`, `Table P.2`, `P.6`, P258)**: Marked **`IEC 60947-2:2024, Annex P`**; PV $U_e$ and $I_{\text{cu}}/I_{\text{cs}}$ clearly separated from non-PV ratings; literature supplies pole series-connection diagram; optional de-rating guidance up to `70 °C` and operation $< -5\,^\circ\text{C}$ (`P.6`).
- **Performance & Special Tests (`P.7–P.8`, P258–261)**:
  - Must interrupt forward and reverse currents up to breaking capacity (`P.7.2`, P258 — covers polarized/non-polarized polarity requirements via `Table 15` *"Terminals marked line/load-No"*, `P.8.3.2`).
  - `8.2.4.1` overload tests waived (overcurrent in PV is only short-circuit); `Annex H` not applicable (`P.7.2`, P259); operational performance cycles per `Table P.3` (P259).
  - **Test Sequence VII (`P.8.3.9`, P260)**: Critical DC load current tested with `10` operations (`5` forward + `5` reverse) at `1 ms` time constant, followed by `100` operational performance cycles (instead of `50`).
  - **Thermal cycling (`P.8.3.10`, P261)**: `50` cycles (`1 h` at `-40 °C` / `1 h` at `+85 °C`, `1 K/min`) per `IEC 60068-2-14` Test Nb; **Climatic test (`P.8.3.11`, P261)** per `IEC 60947-1:2020 Annex Q` Category B.

### 5.13 Annex R — CBARs (`P263–273`)

- **Scope (`R.1`, P263)**: CBRs incorporating residual current protection with automatic reclosing functions (**CBARs**), AC circuits only.
- **Classification (`R.3`, P265)**:
  - **Construction (`R.3.1`)**: **Integral CBAR** (`R.3.1.1`) vs **External automatic reclosing device** (`R.3.1.2`) combined with a CBR.
  - **Reclosing method (`R.3.2`)**: **Type M** (`R.3.2.1`: earth leakage monitoring type — monitors downstream circuit and inhibits reclosing if assessed leakage exceeds **$I_{\Delta\text{ar}}$**) vs **Type TD** (`R.3.2.2`: time-delay type — recloses after **reclosing time-delay** `R.2.6` without monitoring circuit conditions).
- **Key Terms & Tests (`R.2`, `R.4`, `R.8`, P264–270)**: **$I_{\Delta\text{ar}}$** (rated automatic reclosing operating residual current, $\le I_{\Delta n}$), **selector switch** (`R.2.3`), **reset time** (`R.2.4`), **blocked state** (`R.2.5`); mandatory verification of non-reclosing after overcurrent tripping (`R.8.2`) or intentional opening (`R.8.3`), and **mechanical endurance** (`R.8.5`).

---

## 6. Mounting, Connections & MCCB Accessories

| Chinese Term | ❌ Forbidden Literal Term | ✅ Track 1 / Track 2 IEC English (`IEC 60947-2:2024`) | North American (`UL 489`) | Description & Slots |
| :--- | :--- | :--- | :--- | :--- |
| **板前接线 (固定式)** | Front wiring | **Front connection (Fixed)** | Front-connected (Fixed) | Standard front busbar / cable lug connection (`4.4`). |
| **板后水平/垂直接线** | Back wiring | **Rear connection (Horizontal HR / Vertical VR studs)** | Rear-connected studs | Rear terminal studs for switchboard compartment mounting. |
| **插入式安装** | Insert installation | **Plug-in circuit-breaker / Plug-in base** (`3.4`, `4.4`) | Plug-in mounting | Additional plug-in contacts enabling rapid removal without disconnecting busbars. |
| **抽屉式安装 (抽出式)** | Drawer type / Drawer box | **Withdrawable circuit-breaker / Withdrawable base** (`3.5`, `4.4`, `8.1.2`) | Drawout mounting / Cradle | Withdrawable assembly with isolating contacts, position indication, and safety shutters (`8.1.2`). |
| **旋转操作手柄 (直接/门联锁)** | Rotate handle | **Rotary handle (Direct / Extended / Door-mounted)** | Rotary operating handle | Direct breaker-mounted handle or extended shaft door-coupling mechanism. |
| **电动操作机构 (电操)** | Motor hand / Operating device | **Motor-operator / Motor mechanism** (`Annex N`) | Motor operator | Remote electrical closing/opening drive; covered by `Annex N` EMC (`{{Uc: V}}`). |
| **分励脱扣器 / 欠电压脱扣器** | Excitation release / Lack voltage trip | **Shunt release** / **Undervoltage release** (`5.7.1`, `8.2.1.2`) | Shunt Trip / Undervoltage Trip | Remote opening or low-voltage trip release; control voltage `{{Uc: V}}`. |
| **闭合电磁铁 (合闸线圈)** | Close electromagnet / Closing magnet | **Closing release** *(admitted: closing coil)* (`3.19`, `5.7.1`) | Closing coil | Voltage-energized closing release (`Annex N`); control voltage `{{Uc: V}}`. |
| **相间隔板** | Phase space board / Phase space plate | **Interphase barriers / Phase barriers** | Phase barriers | Insulating barriers between adjacent terminal lugs. |
| **接线端子罩 (扩展罩)** | Wire cover | **Terminal shield / Extended terminal cover** | Terminal shield / Lug cover | Achieved enclosure degree of protection `{{terminal_cover_ip}}` (`4.5`). |
| **挂锁装置 / 钥匙锁** | Body key lock / Padlock device | **Padlocking device / Key lock** (`3.10` lock-out device) | Padlock attachment / Cylinder lock | Lock-out means in open or disconnected position (`{{key_lock_scheme}}`). |

---

## 7. MCCB & Annex Anti-Chinglish Guardrails (ZH ↔ EN Bidirectional)

| Direction / Issue | Chinese Source | ❌ Strictly Forbidden | ✅ Mandatory IEC 60947-2:2024 English | Standard Rationale |
| :--- | :--- | :--- | :--- | :--- |
| **Device Name** | 塑壳断路器 | *Plastic shell breaker*, *Circuit breaker* (unhyphenated), *Molded-case* (in IEC copy) | **Moulded-case circuit-breaker (MCCB)** / **Circuit-breaker** | `IEC 60947-2:2024` uses `circuit-breaker` (667×) and `moulded case` (1×). Reserve *Molded-Case* for `UL 489` column only. |
| **Frame Rating vs Size** | 壳架等级电流 / 壳架尺寸 | *Inm* (as an IEC 60947-2 symbol), *Shell frame current* | **Frame size** (`3.1.1`) / **Maximum rated current for a given frame size** (`Table 7`) | `Inm` has 0 occurrences in `IEC 60947-2:2024` (`GB/T 14048.2` term); use `frame size` (`Cl. 3.1.1`) in IEC deliverables. |
| **Endurance / Life** | 机械寿命 / 电寿命 | *Mechanical durability*, *Electrical durability*, *N Ten thousand times* | **Operational performance capability** / **Operating cycles** (`8.2.4.2`, `Table 7`); **Endurance** (`M.8.11`, `R.8.5`) | `durability` = 0 occurrences in `IEC 60947-2:2024`. Convert 万 to plain integer `{{ops: cycles}}`. |
| **Coordination** | 选择性配合 / 后备保护 | *Discrimination*, *Backup* (unhyphenated), *Area select* | **Selectivity** (`5.4`, `A.5`); **Back-up protection** (`A.6`) | `discrimination` = 0 occurrences in `IEC 60947-2:2024`; `back-up` is hyphenated. |
| **Releases** | 分励 / 欠压 / 闭合脱扣器 | *Shunt opening release*, *Under-voltage*, *Lack voltage*, *Closing magnet* | **Shunt release**; **Undervoltage release**; **Closing release** (`5.7.1`, `3.19`) | `term_audit.json`: `shunt release` (25× vs 0), `undervoltage` (36× vs 4), `closing release` (13×). |
| **Arc Chamber** | 灭弧室 / 双断点 | *Arc room*, *Interrupter*, *Double breaking point* | **Arc extinction device** (`8.1.6`); **Rotary double-break contact system** | `arc chute` and `arc-extinguishing` = 0 in `IEC 60947-2:2024`; `Cl. 8.1.6` uses `arc extinction device`. |
| **Withdrawable** | 抽出式 / 插入式 | *Drawer type*, *Insert type*, *Drawout* (in IEC copy) | **Withdrawable circuit-breaker** (`3.5`); **Plug-in circuit-breaker** (`3.4`) | `withdrawable` (18×) is the IEC 60947-2 term; reserve *Drawout* for `UL 489` / cradle context. |
| **CBR / Leakage** | 漏电塑壳 / F型 / B+型 | *Leakage plastic shell*, claiming *Type F / Type B+* under IEC 60947-2 | **Circuit-breaker incorporating residual current protection (CBR)** (`Annex B`: **Type AC / A / B** only) | `Annex B` (`B.3.4`) covers Type AC, A, B only; cite `IEC 62423` / `VDE 0664-400` if Type F/B+ applies. |
| **Aluminium Terminals** | 未预处理圆铝导线 | *Untreated round aluminum wire* | **Unprepared round aluminium conductors** (`D.8.5`); **Aluminium conductors** (`Annex D`) | British spelling `aluminium` (`D.1–D.8`); exact `D.8.5` test wording. |
| **PV DC Polarity** | 光伏直流无极性 / 临界电流 | *Non-polar PV breaker*, *Critical small DC current* | **Non-polarized PV circuit-breaker** (interrupts forward and reverse currents, `P.7.2`); **Critical DC load current** (`9.3.10`, `P.8.3.9`) | Cite `IEC 60947-2:2024, Annex P` (`P.5`) and Sequence VII (`9.3.10`). |
| **CBAR Reclosing** | 自动重合闸型漏电断路器 | *Auto-reset leakage breaker* | **CBAR (CBR with automatic reclosing functions)** — **Type M** (earth leakage monitoring) / **Type TD** (time-delay) (`Annex R`) | Distinguish automatic reclosing (`R.2.1`) from manual reset (`R.2.5` blocked state). |
| **IEC Spelling & Units** | 通用拼写与单位 | *Utilization*, *Color*, *Energised*, `℃`, `400A` (no space) | **Utilisation**, **Colour**, **Energized** (`37×` vs `0×` *-is-*); `{{T: °C}}`, `{{value: A}}` | Enforce `IEC 60947-2:2024` UK nouns + `-ize` verbs and single half-width space before units. |
