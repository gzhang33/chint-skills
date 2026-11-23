# IEC 60947-2:2024 (Edition 6.0) Authoritative Standard Reference

> **Single Source of Truth**: `IEC 60947-2:2024` (Edition 6.0, 2024-09) — *Low-voltage switchgear and controlgear — Part 2: Circuit-breakers* (English text, printed pages 1–276), supplemented by referenced general rules in `IEC 60947-1:2020`.
> **Pure Single-Track Rule**: Every row below fixes **one canonical IEC English term** (ZH→EN output) and **one canonical Chinese term** (EN→ZH anchor, aligned with `GB/T 14048.2`). All product ratings are `{{param_name: unit}}` slots; numbers quoted without `{{...}}` are standard-fixed normative thresholds in `IEC 60947-2:2024`.

---

## 1. Clause 3 — Core Terms & Definitions (`Cl. 3.1–3.19`, P19–22)

> **Edition 6.0 Clause Shift Alert**: Edition 6.0 inserted `Cl. 2 Normative references`, shifting all subsequent clauses by `+1` compared to Edition 5.x (`Cl. 2.x -> 3.x`, `3.x -> 4.x`, `4.x -> 5.x`, `5.x -> 6.x`, `7.x -> 8.x`, `8.x -> 9.x`). Never cite obsolete Ed. 5.x clause numbers (`Cl. 2.1`, `Cl. 4.3.2.x`, `Cl. 4.3.5.x`).

| Clause & Page | Chinese Term (✅ EN→ZH) | ✅ Unique Canonical IEC English (ZH→EN) | Symbol / Admitted Note |
| :--- | :--- | :--- | :--- |
| **Cl. 3.1** (P19) | 断路器 | **`circuit-breaker`** | Always hyphenated (667× in Ed. 6.0). Note: IEC 60947-2 defines the unified term `circuit-breaker` without dividing by ACB vs MCCB; `air circuit-breaker (ACB)` and `moulded-case circuit-breaker (MCCB)` are industry category terms harmonized to IEC spelling. |
| **Cl. 3.1.1** (P20) | 壳架等级（壳架电流） | **`frame size`** | Group of circuit-breakers sharing common external physical dimensions across a current range; **Note 1 explicitly states `frame size` is expressed in amperes corresponding to the highest current rating of the group** (28× in Ed. 6.0). **`Inm` has 0 occurrences in IEC 60947-2** (it is a `GB/T 14048.2` domestic symbol; IEC `Table 7` fn. a writes *"maximum rated current for a given frame size"*). |
| **Cl. 3.1.2 & 8.1.6** (P20, P33) | 结构差异（构造变更） | **`construction break`** | Significant difference in construction within a given frame size requiring additional type testing (`8.1.6` lists internal conductors, main contacts, manual mechanism, moulding/insulating materials, `arc extinction device`, and basic overcurrent trip design). |
| **Cl. 3.2 & 5.8** (P20, P30) | 带熔断器的断路器 | **`integrally fused circuit-breaker`** | Single device combining a circuit-breaker and one series fuse per line pole (`Cl. 8.2.7`, Test Sequence V `Cl. 9.3.8`). |
| **Cl. 3.3** (P20) | 限流断路器 | **`current-limiting circuit-breaker`** | Prevents `let-through current` (admitted synonym: `cut-off current`, Note 2; `Fig. K.2–K.3`) from reaching prospective peak and limits `let-through energy` ($I^2t$, `Fig. K.4–K.5`) below half-cycle symmetrical prospective wave. |
| **Cl. 3.4 & 4.4** (P20, P23) | 插入式断路器 | **`plug-in circuit-breaker`** | Has plug-in contacts enabling removal in addition to interrupting contacts. |
| **Cl. 3.5, 4.4 & 8.1.2** (P20, P33) | 抽出式断路器（抽屉式断路器） | **`withdrawable circuit-breaker`** | Has isolating contacts enabling withdrawal to achieve a specified `isolating distance` in the `disconnected position` (18× `withdrawable`; `Fig. J.1` P182 uses `draw-out cradle` once; commercial `drawout` is recognized in EN→ZH, never `drawer`). |
| **Cl. 3.6** (P20) | 瞬时合闸涌流脱扣器（MCR） | **`making-current release`** | Opens without intentional time-delay during closing only if making current exceeds threshold; rendered inoperative once closed. |
| **Cl. 3.7** (P20) | 短路脱扣器 | **`short-circuit release`** | Overcurrent release for protection against short circuits. |
| **Cl. 3.8** (P21) | 短延时短路脱扣器 | **`short-time delay short-circuit release`** | Operates at the end of intentional short-time delay ($t_{sd}$). |
| **Cl. 3.9** (P21) | 报警开关（故障脱扣触头） | **`alarm switch`** | Auxiliary switch operating **only** upon tripping of the circuit-breaker. |
| **Cl. 3.10** (P21) | 带防止闭合锁定装置的断路器 | **`circuit-breaker with lock-out device preventing closing`** | Moving contacts prevented from closing while specified conditions remain (`lock-out` always hyphenated). |
| **Cl. 3.11–3.11.3** (P21) | 极限 / 单极极限 / 运行短路分断能力 | **`ultimate / individual pole ultimate / service short-circuit breaking capacity`** | Definitions corresponding to rated quantities $I_{cu}$, $I_{cu1}$, and $I_{cs}$ in `Cl. 5.3.6.2`. |
| **Cl. 3.12** (P21) | 分断时间（脱扣时间） | **`opening time`** | Initiation of opening to arcing-contact separation in all poles; Note 2 notes `"tripping time"` is commonly used, though strictly ending when opening becomes irreversible. |
| **Cl. 3.13** (P21) | $I^2t$ 特性（允通能量特性） | **`I²t characteristic`** | Maximum $I^2t$ vs prospective RMS symmetrical current curve (`Fig. K.1`, `Fig. K.4–K.5`). |
| **Cl. 3.14** (P22) | 复位时间 | **`resetting time`** | Time from overcurrent tripping until the circuit-breaker can be reclosed. |
| **Cl. 3.15** (P22) | 瞬时短路整定电流 | **`instantaneous short-circuit current setting`** | Symbol **$I_i$** (`{{Ii_setting: ×In}}` or `A`; may be non-adjustable). |
| **Cl. 3.16** (P22) | 过载整定电流（长延时整定电流） | **`overload current setting`** | Symbol **$I_r$** (`{{Ir_setting: ×In}}` or `A`; equals $I_n$ if non-adjustable). |
| **Cl. 3.17** (P22) | 短延时起动电流整定值 | **`short-time pick-up current setting`** | Symbol **$I_{sd}$** (`{{Isd_setting: ×Ir}}`; operates with intentional time-delay $t_{sd}$; `pick-up` hyphenated). |
| **Cl. 3.18 & 8.1.8** (P22, P34) | 可编程逻辑控制器及数字量输入输出 | **`programmable logic controller (PLC)`** / **`digital inputs and outputs`** | Digital I/O intended for PLCs shall comply with `Cl. 8.1.8` (referencing `IEC 60947-1:2020 Annex S`). |
| **Cl. 3.19** (P22) | 闭合脱扣器（合闸线圈 / 闭合电磁铁） | **`closing release`** | Admitted synonym in `Cl. 3.19`: `closing coil` (recognize in EN→ZH; output `closing release` in ZH→EN). |
| *IEC 60947-3* | 隔离开关（开关-隔离器） | **`switch-disconnector`** | Governed by `IEC 60947-3` (`GB/T 14048.3`), NOT `IEC 60947-2` (`CBI` in `Annex L` is distinct). Never write `"隔离开关断路器"` or cite obsolete `Cl. 2.1.3`. |

---

## 2. Clause 4 & Clause 5 — Classification, Ratings & Releases (`P23–30`)

### 2.1 Clause 4 Classification (`Cl. 4.1–4.5`, P23)
- **Selectivity category (`Cl. 4.1`, `5.4`, P23/P27)**: **`selectivity category`** — **`Category A`** (no assigned $I_{cw}$ per `5.3.6.4`) or **`Category B`** (assigned $I_{cw}$ and intentional short-time delay $\ge 0.05\text{ s}$ per `5.3.6.4` & `Table 2`: preferred delays `0.05 – 0.1 – 0.25 – 0.5 – 1 s`; min $I_{cw} = 12\,I_n$ or `5 kA` for $I_n \le 2\,500\text{ A}$, `30 kA` for $I_n > 2\,500\text{ A}$). *Warning*: `"使用类别 A/B"` is an obsolete 2008 GB/T term — never conflate with **`utilization category`** (`AC-3`, `AC-15`, `AC-22`, `DC-13`).
- **Operating mechanism control (`Cl. 4.2` classification vs `Cl. 8.2.1.1` closing requirements)**:
  - Classification (`Cl. 4.2`, P23): **`dependent manual operation`**, **`independent manual operation`**, **`dependent power operation`**, **`independent power operation`**, **`stored energy operation`**.
  - Closing rules (`Cl. 8.2.1.1.2–8.2.1.1.6`, P34–35): **`dependent manual closing`**, **`independent manual closing`**, **`dependent power closing`**, **`independent power closing`**, **`stored energy closing`**.
- **Maintenance (`Cl. 4.3`, P23)**: **`maintainable`** vs **`non-maintainable`**.
- **Installation (`Cl. 4.4`, P23)**: **`fixed`**, **`plug-in`**, **`withdrawable`**.
- **Enclosure protection (`Cl. 4.5`, P23)**: **`degree of protection`** (`{{IP_code}}`, `IEC 60529` / `IEC 60947-1:2020 Cl. 8.1.12`).

### 2.2 Clause 5 Main-Circuit, Control & Release Characteristics (`Cl. 5.2–5.7`, P23–30)

| Symbol | Chinese Term (✅ EN→ZH) | ✅ Unique Canonical IEC English (ZH→EN) | Clause & Page | Value Slot |
| :--- | :--- | :--- | :--- | :--- |
| **$U_e$** | 额定工作电压 | **`Rated operational voltage`** | `Cl. 5.3.2.1` (P24) | `{{Ue: V AC}}` / `{{Ue: V DC}}` |
| **$U_i$** | 额定绝缘电压 | **`Rated insulation voltage`** | `Cl. 5.3.2.2` (P24; `60947-1 Cl. 5.3.1.2`) | `{{Ui: V}}` |
| **$U_{imp}$** | 额定冲击耐受电压 | **`Rated impulse withstand voltage`** | `Cl. 5.3.2.3` (P24; `60947-1 Cl. 5.3.1.3`) | `{{Uimp: kV}}` |
| **$I_{th}$** | 约定自由空气发热电流 | **`Conventional free air thermal current`** | `Cl. 5.3.3.1` (P24; `60947-1 Cl. 5.3.2.1`) | `{{Ith: A}}` |
| **$I_{the}$** | 约定封闭发热电流 | **`Conventional enclosed thermal current`** | `Cl. 5.3.3.2` (P24; `60947-1 Cl. 5.3.2.2`) | `{{Ithe: A}}` |
| **$I_n$** | 额定电流 | **`Rated current`** | `Cl. 5.3.3.3` (P24; $= I_u = I_{th}$) | `{{In: A}}` |
| **$f_n$ / Duty** | 额定频率 / 额定工作制 | **`Rated frequency`** / **`Rated duty`** (`eight-hour duty` / `uninterrupted duty`) | `Cl. 5.3.4 & 5.3.5` (P24) | `{{fn: Hz}}` |
| **$I_{cm}$** | 额定短路接通能力 | **`Rated short-circuit making capacity`** | `Cl. 5.3.6.1 & 5.3.6.3`, `Table 1` (P25–26) | `{{Icm: kA peak}}` ($\ge n \times I_{cu}$ AC; $\ge I_{cu}$ DC) |
| **$I_{cu}$** | 额定极限短路分断能力 | **`Rated ultimate short-circuit breaking capacity`** | `Cl. 5.3.6.2.2` (P25) | `{{Icu: kA rms}}` *(Catalogue header: `Ultimate breaking capacity Vac 50/60 Hz`)* |
| **$I_{cu1}$** | 相-中性线交流电压下的额定单极极限短路分断能力 | **`Rated individual pole ultimate short-circuit breaking capacity at phase-to-neutral AC voltage`** | `Cl. 5.3.6.2.3 & 9.3.11` (P26, P77) | `{{Icu1: kA rms}}` ($= I_{cu}$ if all phase poles share identical design) |
| **$I_{cs}$** | 额定运行短路分断能力 | **`Rated service short-circuit breaking capacity`** | `Cl. 5.3.6.2.4` (P26; $\ge 25\%\,I_{cu}$) | `{{Ics: kA rms}}` (`{{Ics_ratio: % of Icu}}`) |
| **$I_{cw}$** | 额定短时耐受电流 | **`Rated short-time withstand current`** | `Cl. 5.3.6.4`, `Table 2` (P26–27) | `{{Icw: kA rms}}` for `{{Icw_duration: s}}` |
| **$U_c$** | 额定控制电路电源电压 | **`Rated control circuit supply voltage`** | `Cl. 5.5.1`, `Table 3` (P27–28) | `{{Uc: V}}` (preferred DC `24–250 V`, AC `24–230 V`) |
| **Aux** | 辅助回路与辅助开关 | **`Auxiliary circuits`** / **`Auxiliary switches`** | `Cl. 5.6` (P28) | `{{aux_config}}` |
| **Releases** | 脱扣器类型（分励 / 过流 / 欠压 / 闭合） | **`Shunt release`** (`8.2.1.2.3`), **`Overcurrent release`** (`instantaneous`, `definite time-delay`, `inverse time-delay`, `ground-fault`), **`Undervoltage release`** (`8.2.1.2.2`), **`Closing release`** (`3.19`) | `Cl. 5.7.1–5.7.4` (P28–30) | Reference ambient temp for thermal releases: `+30 °C ± 2 °C` (`5.7.3`); non-thermal temperature-independent band `-5 °C` to `+40 °C` (`0.3 %/K`, `8.2.1.2.4 b)`). |

> **`ground-fault` vs `earth fault` Exact Standard Rule**: In `IEC 60947-2:2024`, hyphenated `earth-fault` has **0 occurrences**. Overcurrent G-stage protection (`Cl. 5.7.1` item 2d, `Cl. 8.2.1.2.4 c)` types `CI-A`/`CI-B`, `Table K.1`, `Fig. K.1`) uses **`ground-fault`** (19×, e.g. `ground-fault current setting` $I_g$). Physical fault current flowing to earth (`Annex B` `B.2.1.1`) uses unhyphenated **`earth fault`** (16×, e.g. `earth fault current`).

---

## 3. Clauses 6–9 — Marking, Service Conditions, Performance & Test Sequences (`P30–81`)

- **Product Information & Marking (`Cl. 6`, `Table 4`, P30–32)**:
  - **Visible in service (`1.1–1.3`)**: $I_n$, suitability for isolation symbol (`IEC 60617-S00287+S00220`), open/closed `O` / `|` (`IEC 60417-5008/5007`).
  - **Marked on body (`2.1–2.21`)**: Manufacturer/trademark, type designation / `catalogue reference`, `IEC 60947-2`, selectivity category `A`/`B`, $U_e$, crossed-out `IT` (`IEC 60417-6363`) if unsuitable for IT, $U_{imp}$, frequency/`DC`, $I_{cs}$, $I_{cu}$, $I_{cu1}$ (if $\ne I_{cu}$), $I_{cw}$ & delay, settings, terminals, `N` pole, `PE` (`IEC 60417-5019`).
  - **Literature (`6.1`, `6.3`)**: Power loss per frame size (`Annex G`), derating curves, clearing distances, and **`decommissioning and dismantling instructions`** (`6.3`, P32).
- **Normal Service Conditions (`Cl. 7`, P32)**: Default **`pollution degree 3`**; ambient `-5 °C` to `+40 °C` (`24 h` average $\le +35\,^\circ\text{C}$); altitude $\le 2\,000\text{ m}$ (`IEC 60947-1:2020 Cl. 7`); glow-wire (`8.1.1`, P32): `960 °C` (main-circuit retaining parts) / `850 °C` (other parts).
- **Withdrawable Positions & Isolation (`Cl. 8.1.2`, `8.1.3`, `8.2.6`, P33, P40)**: **`connected position`**, **`test position`**, **`disconnected position`** (with isolating distance, unambiguous position indication, and mechanical locking).
- **Release Calibration & Temperature-Rise (`Cl. 8.2.1.2.4`, `Table 5`, `8.2.2`, `Table 6`, P36–38)**:
  - Short-circuit release tolerance `±20 %`; instantaneous/definite-time overload `±10 %`.
  - Inverse time-delay overload (`Table 5`, P36): **`conventional non-tripping current`** $= 1.05 \times I_{\text{set}}$; **`conventional tripping current`** $= 1.30 \times I_{\text{set}}$; **`conventional time`** $= 2\text{ h}$ (`1 h` for $I_n \le 63\text{ A}$).
  - Temperature-rise (`Table 6`, P38): terminals `80 K`; manual operating means `25 K` (metal) / `35 K` (non-metal).
- **Operational Performance Capability (`Cl. 8.2.4.2`, `Table 7`, P39–40)**:
  - **`durability` has 0 occurrences in `IEC 60947-2:2024`**. Use **`operational performance without current`** / **`number of operating cycles without current`** (`{{mech_ops: operating cycles}}`) and **`operational performance with current`** / **`number of operating cycles with current`** (`{{elec_ops: operating cycles}}`); in `Annex B / M / R`, use **`mechanical and electrical endurance`** (`M.8.11`, `R.8.5`).
  - `Table 7` standard minimums (by max $I_n$ of frame size): $\le 100\text{ A}$ (`8 500 + 1 500 = 10 000`), $\le 315\text{ A}$ (`7 000 + 1 000 = 8 000`), $\le 630\text{ A}$ (`4 000 + 1 000 = 5 000`), $\le 2\,500\text{ A}$ (`2 500 + 500 = 3 000`), $> 2\,500\text{ A}$ (`1 500 + 500 = 2 000`). Overload test (`8.2.4.1`) applies to $I_n \le 630\text{ A}$.
- **Tests & Test Sequences I–VIII (`Cl. 9.1–9.5`, `Tables 8–15`, P41–81)**:
  - Categories (`9.1`): **`type tests`** (`9.3`), **`routine tests`** (`9.4`: mechanical operation, overcurrent calibration, shunt/undervoltage release operation, CBR tests, dielectric, reduced clearances), **`special tests`** (`9.5`: damp heat, salt mist, vibration, shock); multi-pole alternative test programmes in `9.3.2.4` & `Tables 12–14`.
  - **Seq I (`9.3.4`, P58)**: General performance characteristics | **Seq II (`9.3.5`, P68)**: $I_{cs}$ | **Seq III (`9.3.6`, P69)**: $I_{cu}$ | **Seq IV (`9.3.7`, P71)**: $I_{cw}$ | **Seq V (`9.3.8`, P72)**: Integrally fused CBs ($I_s$, $1.1\,I_B$, $I_{cu}$) | **Seq VI (`9.3.9`, P74)**: Combined test sequence (Cat B) | **Seq VII (`9.3.10`, P76)**: **`Critical DC load current`** (`4–63 A DC` steps, `5` forward + `5` reverse if unpolarized, arcing $\le 1\text{ s}$, + `50` cycles) | **Seq VIII (`9.3.11`, P77)**: Individual pole $I_{cu1}$ at phase-to-neutral AC voltage.

---

## 4. Clause 8.2.8 & Annex A — Coordination, Selectivity & Back-up Protection (`P41, P84–85`)

| Chinese Term (✅ EN→ZH) | ✅ Unique Canonical IEC English (ZH→EN) | Symbol & Clause | Technical Meaning |
| :--- | :--- | :--- | :--- |
| 断路器与同一电路另一短路保护电器的配合 | **`Coordination between a circuit-breaker and another short-circuit protective device (SCPD)`** | `Cl. 8.2.8`, `Annex A` (P41, P84) | Official Ed. 6.0 title uses unhyphenated `Coordination` (11×). Replaces $I_{cn}$ of `60947-1 Annex X` with $I_{cu}$. |
| 选择性（全选择性 / 局部选择性） | **`Selectivity`** (`total selectivity` / `partial selectivity`) | `Annex A (A.5)`, `Cl. 5.4` (P84) | Downstream SCPD clears faults up to $I_s$ without upstream CB tripping (never `discrimination`). |
| 选择性极限电流 | **`Selectivity limit current`** | **$I_s$** (`Cl. 8.2.7`, `A.5`, `Table K.1`) | Maximum prospective current up to which selectivity is ensured (`{{Is: kA rms}}`). |
| 后备保护（组合短路保护） | **`Back-up protection`** | `Annex A (A.6)`, `Fig. A.1` (P84–85) | Upstream SCPD assists downstream CB above its standalone $I_{cu}$ (`IEC 60364-5-53`: `"combined short-circuit protection"`). |
| 交接电流 | **`Take-over current`** | **$I_B$** (`Cl. 9.3.8`, `Table K.1`, P72) | Prospective current where fuse/upstream SCPD takes over interruption (`9.3.8.6` tested at $1.1\,I_B$). |
| 额定限制短路电流 | **`Rated conditional short-circuit current`** | **$I_{cc}$** (`Cl. L.4.2`, `M.4.3.1`, `Table K.1`) | `IEC 60947-2` symbol for CBIs/MRCDs is **$I_{cc}$** (reserve $I_q$ for `IEC 60947-1/3/4-1` equipment). |

---

## 5. Complete Normative & Informative Annexes Matrix (`Annexes A–R`, P84–273)

| Annex & Status | Chinese Domain & Terms (✅ EN→ZH) | ✅ Canonical IEC English Terms & Symbols (ZH→EN) | Key Clauses & Boundary Rules |
| :--- | :--- | :--- | :--- |
| **Annex B** (Normative, P86–129) | 带剩余电流保护的断路器（**CBR**）：额定剩余动作电流 $I_{\Delta n}$、额定剩余不动作电流 $I_{\Delta no}$、额定剩余短路接通和分断能力 $I_{\Delta m}$、极限不驱动时间 $\Delta t$、试验装置 `T`、功能与电源电压无关/有关的 CBR | **`Circuit-breaker incorporating residual current protection (CBR)`**; **`rated residual operating current`** ($I_{\Delta n}$), **`rated residual non-operating current`** ($I_{\Delta no}$), **`rated residual short-circuit making and breaking capacity`** ($I_{\Delta m}$), **`limiting non-actuating time at 2 IΔn`** ($\Delta t$), **`test device`** (`T`), **`CBR functionally independent of / dependent on line voltage`** | AC circuits only (`B.1`). Waveforms (`B.3.4`): **`Type AC`**, **`Type A`**, **`Type B`** (tested up to `1 000 Hz` in `B.8.8`; *Type F / B+ belong to `IEC 62423`, not `60947-2`*). $I_{\Delta n} = 30\text{ mA}$ shall be non-time-delay (`B.4.2.4.1`). Test button `T` **`colour shall not be red or green`** (`B.7.2.6`). Crossed-out `1~` (`IEC 60417-6364`, `Table B.3`) = 3-phase supply only. |
| **Annex C** (Normative, P130) | 相接地系统单极短路试验程序 | **`Individual pole short-circuit test sequence`** (phase-earthed systems); symbol **$I_{su}$** | Marked with `C` prefix on $U_e$ (`5.3.2.1`); $I_{su} \ge 25\%\,I_{cu}$ at phase-to-phase voltage (`C.2–C.4`). |
| **Annex D** (Normative, P131–142) | 铝导体连接用断路器：基准导体、均流器、稳定系数 $S$、未预处理圆铝导线可插入性试验 | **`Circuit-breakers intended for connection of aluminium conductors`** (`AL` / `AL/CU`); **`reference conductor`** (`D.2.1`), **`equalizer`** (`D.2.2`), **`stability factor`** ($S$, `D.2.3`), **`insertability of unprepared round aluminium conductors`** (`D.8.5`) | $\ge 10\text{ mm}^2$ solid/stranded Al cables & bars (`D.1`); current cycling (`D.8.2`), climatic (`D.8.3`), mechanical (`D.8.4`), surface prep & anti-oxidant compound (`D.5.2–D.5.3`). |
| **Annex E** (Informative, P143) | 制造厂与用户协商项目 | **`Items subject to agreement between manufacturer and user`** (`Table E.1`) | Higher $I_{cm}$, $U_{imp} > 1\,000\text{ V AC}$, 4th-pole current, special tests (`9.5`), $I_{\Delta n} > 30\text{ A}$, Al bars $> 3\,150\text{ A}$. |
| **Annex F** (Normative, P144–166) | 电子过电流保护断路器附加试验 | **`Additional tests for circuit-breakers with electronic overcurrent protection`** | EMC (`F.2.2`, `F.4–F.5`, `Table F.1`: harmonics, ESD, RF, EFT/B, surges, current dips; Criterion A: no trip at $0.9\,I_{\text{set}}$, trip within $\pm 10\%$ curve at $2.0\,I_{\text{set}}$); multiple frequencies (`F.6`), dry heat (`F.7`), damp heat (`F.8`), temperature variation cycles (`F.9`). |
| **Annex G** (Normative, P167–171) | 功率损耗测定（功率因数法 / 积分法） | **`Power loss`** (**`power factor method`** / **`integral method`**) | Free-air steady-state watts (`W`, `6.1`). AC $> 400\text{ A}$ (`G.2.1`), AC $\le 400\text{ A}$ (`G.2.2`), DC (`G.2.3`); 4P tested without N current (`G.4.1`). |
| **Annex H** (Normative, P172–173) | IT 系统断路器单极短路试验程序 / 不适用于 IT 系统标志 | **`Test sequence for circuit-breakers for IT systems`**; symbol **$I_{IT}$**; **`crossed-out IT symbol`** (`IEC 60417-6363`) | $I_{IT} = 1.2\times$ max short-time/instantaneous setting (`500 A`–`50 kA`, `H.2–H.4`). Unsuitable voltages marked with crossed-out `IT` (`H.5`, `Table H.2`). |
| **Annex I** (P174) | 附录 I（空缺） | **`Annex I (Vacant)`** | Vacant in Edition 6.0. |
| **Annex J** (Normative, P175–186) | 断路器电磁兼容（环境 A / 环境 B） | **`Electromagnetic compatibility (EMC)`** — **`Environment A`** (Class A) / **`Environment B`** (Class B) | Immunity (`Table J.1`: `IEC 61000-4-2/3/4/5/6/11`) & emissions (`Table J.3`: `CISPR 11/32`; `Fig. J.1` EUT in enclosure). |
| **Annex K** (Informative, P187–195) | 符号词汇表与特性曲线图示 | **`Glossary of symbols and graphical representation of characteristics`** | `Table K.1` master symbols; `Fig. K.1` (`RC, GF, LT, ST, INST`); `Fig. K.2–K.3` cut-off current; `Fig. K.4–K.5` let-through $I^2t$; `Fig. K.6–K.7` examples. |
| **Annex L** (Normative, P196–202) | 不满足过电流保护要求的断路器（**CBI**，俗称无过电流保护断路器） | **`Circuit-breaker not fulfilling the requirements for overcurrent protection (CBI)`** (`CBI-W`, `CBI-X`, `CBI-Y`, `CBI-X/W`, `CBI-Y/W`) | Derived from equivalent CB (`L.2.1`); **Class W** ($I_{cu}=I_{cw}$, external relay), **Class X** (self-protecting $I_i$, rated $I_{cc}$), **Class Y** (no overcurrent release, rated $I_{cc}$). $I_n$ correlated to **`utilization category AC-22`** (`L.4.1`, `Table L.1`). |
| **Annex M** (Normative, P203–249) | 模块化剩余电流装置（**MRCD**，不带一体式分断电器） | **`Modular residual current device (without integral current-breaking device) (MRCD)`** | **`Terminal type`** (`M.3.1.1`) vs **`through-conductor type`** (`M.3.1.2` combined/separated); $U_s$, $U_n$, $I_{cc}$, $I_{\Delta c}$ (`M.4.3.2`), $I_{\Delta w}$ (`M.4.3.5`), `combination time` (`M.2.2.2.2`), **`mechanical and electrical endurance`** (`M.7.2.3`, `M.8.11`), `Table M.1 / M.3`. |
| **Annex N** (Normative, P250–253) | 辅助电器 EMC 附加要求 | **`EMC requirements for auxiliary devices`** | Covers electronic `undervoltage releases`, `shunt releases`, `closing releases`, `motor-operators`, and `remote status indicators` (`N.1.1–N.3.3`). |
| **Annex O** (Normative, P254–256) | 瞬时脱扣断路器（**ICB**） | **`Instantaneous trip circuit-breaker (ICB)`** | Short-circuit protection only (no overload release), visibly marked `"ICB"` (`Table O.1`); co-ordinated with motor-starters / overload relays (`O.1–O.6.2`). |
| **Annex P** (Normative, P257–261) | 光伏（PV）用直流断路器 | **`DC circuit-breaker for use in photovoltaic (PV) applications`** (**`PV circuit-breaker`**) | Up to **`1 500 V DC`** (`P.1`); $U_{imp}$ per `Table P.1`; marked `IEC 60947-2:2024, Annex P` (`P.5`, `Table P.2`); interrupts **`forward and reverse currents`** (`P.7.2`); `8.2.4.1` overload waived; cycles per `Table P.3`; Seq VII (`P.8.3.9` `10` ops + `100` cycles); thermal cycling `-40/+85 °C` (`P.8.3.10`); climatic (`P.8.3.11`). |
| **Annex Q** (P262) | 附录 Q（空缺） | **`Annex Q (Vacant)`** | Vacant in Edition 6.0. |
| **Annex R** (Normative, P263–273) | 带自动重合闸功能的剩余电流断路器（**CBAR**） | **`Circuit-breaker incorporating residual current protection with automatic reclosing functions (CBAR)`** | AC only; **`integral CBAR`** (`R.3.1.1`) vs **`external automatic reclosing device`** (`R.3.1.2`); **`Type M`** (earth leakage monitoring, **$I_{\Delta ar}$**) vs **`Type TD`** (time-delay, `R.3.2`); non-reclosing after overcurrent/manual open (`R.8.2–R.8.3`); **`mechanical endurance`** (`R.8.5`), `Table R.1 / R.2`. |

---

## 6. Universal IEC Orthography, CAD & Anti-Chinglish Guardrails

| Chinese Term / Rule | ❌ Strictly Forbidden (Chinglish / US / Legacy) | ✅ Unique Canonical IEC Output |
| :--- | :--- | :--- |
| 断路器 / 塑壳 / 铝 / 颜色 / 样本 | `Circuit breaker` (unhyphenated), `Molded`, `Aluminum`, `Color`, `Catalog` | **`circuit-breaker`**, **`moulded`**, **`aluminium`**, **`colour`**, **`catalogue`** |
| 使用类别 / 通电激励 | `Use classes`, `Energise` / `Energised`, `Utilisation` (in `60947-2` citations) | **`utilization category`** (`L.4.1`), **`energize` / `energized` / `energization`** (ISO/IEC Oxford `-ize`) |
| 选择性 / 后备保护 / 闭锁 | `Discrimination`, `Backup`, `Lockout`, `Pickup` | **`selectivity`**, **`back-up`**, **`lock-out`**, **`pick-up`** |
| 分励 / 欠压 / 闭合脱扣器 | `Shunting release`, `Shunt opening release`, `Shunt Trip`, `Under-voltage`, `Lack voltage`, `Closing magnet` | **`shunt release`**, **`undervoltage release`**, **`closing release`** |
| 机械/电寿命（N 万次） | `Mechanical/Electrical durability`, `N ten thousand times`, `times` | **`operational performance without/with current`** (`{{ops: operating cycles}}`) / **`endurance`** (`Annex B/M/R`) |
| 基准 / 安装面 / 未注公差 | `Base`, `Install surface`, `No tolerance specified` | **`datum`**, **`mounting surface`**, **`unspecified linear tolerance`** |
| 安装调试 / 注意事项 / 订货须知 | `Installation and debugging`, `Matters need attention`, `Ordering instruction` | **`installation and commissioning`**, **`operating precautions`**, **`ordering information`** |
| 小电流测量下限 / 误动作 | `Below X, measurement is inaccurate`, `Wrong action / Error work` | **`Measurement unspecified below {{metering_threshold: A}}`**, **`false tripping`** (`nuisance tripping`) |
