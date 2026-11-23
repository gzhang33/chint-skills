# IEC 60947-2:2024 ⟷ GB/T 14048.2—2020 Dual-Standard Authoritative Reference

> **Dual-Standard Statutory Anchors**: English deliverables obey **`IEC 60947-2:2024`** (Edition 6.0, 2024-09) + `IEC 60947-1:2020` exclusively. Chinese deliverables obey **`GB/T 14048.2—2020`** (*mod* `IEC 60947-2:2019`) statutory wording exclusively, with **zero colloquial parenthetical aliases** (`塑料外壳式断路器`, `抽屉式断路器`, `接通电流脱扣器`, `功耗`). `IEC 60947-2:2024` additions absent from `GB/T 14048.2—2020` (e.g. $I_{cu1}$, `CBI Class W`) are marked explicitly. All product ratings use `{{param_name: unit}}` slots.

---

## 1. Core Terms & Definitions (`IEC 2024 Cl. 3.1–3.19` ⟷ `GB/T 2020 Cl. 2.1–2.23`)

> **Clause Number Alignment**: `IEC 60947-2:2024` inserted `Cl. 2 Normative references`, shifting clauses `+1` relative to `GB/T 14048.2—2020` (`GB 2.x -> IEC 3.x`, `GB 3.x -> IEC 4.x`, `GB 4.x -> IEC 5.x`, `GB 5.x -> IEC 6.x`, `GB 7.x -> IEC 8.x`, `GB 8.x -> IEC 9.x`). Cite `IEC 60947-2:2024` clauses in English deliverables and `GB/T 14048.2—2020` clauses in Chinese deliverables.

| IEC 2024 / GB/T 2020 | ✅ Statutory Chinese (`GB/T 14048.2—2020`) | ✅ Unique Canonical IEC English (`IEC 60947-2:2024`) | Symbol / Standard Note |
| :--- | :--- | :--- | :--- |
| **IEC 3.1** / **GB 2.1** | 断路器 | **`circuit-breaker`** | Always hyphenated (667× in Ed. 6.0). |
| **IEC 3.1.1** / **GB 2.1.1** | 壳架等级 | **`frame size`** | Both Note 1 state expressed in `A` (`frame size`). Neither standard defines `Inm`. |
| **IEC 3.1.2, 8.1.6** / **GB 2.1.2, 7.1.6** | 结构段 | **`construction break`** | Differences in construction within a given `frame size`; `IEC 8.1.6` / `GB 7.1.6`. |
| **IEC 3.2, 5.8** / **GB 2.2, 4.8** | 带熔断器的断路器 | **`integrally fused circuit-breaker`** | Series fuse per line pole (`IEC 8.2.7` Seq V `9.3.8` / `GB 7.2.8` Seq V `8.3.7`). |
| **IEC 3.3** / **GB 2.3** | 限流断路器 | **`current-limiting circuit-breaker`** | Limits **`let-through current`** / `cut-off current` (`Fig. K.2–K.3`) & $I^2t$ (`Fig. K.4–K.5`). |
| **IEC 3.4, 4.4** / **GB 2.4, 3.7** | 插入式断路器 | **`plug-in circuit-breaker`** | Has plug-in contacts enabling removal. |
| **IEC 3.5, 4.4, 8.1.2** / **GB 2.5, 3.7, 7.1.2** | 抽屉式断路器 | **`withdrawable circuit-breaker`** | Achieves isolating distance in `disconnected position` (`GB` uses `抽屉式断路器`; never output `"抽出式断路器"`). |
| *Industry* / **GB 2.6, 3.3** | 塑料外壳式断路器 | **`moulded-case circuit-breaker`** | `GB 3.3` classifies under `塑料外壳式`; Preface notes common `"塑壳式"` (EN→ZH outputs `塑料外壳式断路器`). |
| *Industry* / **GB 2.7, 3.3** | 空气断路器（分类：万能式） | **`air circuit-breaker`** | `GB 2.7` defines `空气断路器`; `GB 3.3` & Preface classify design type as `万能式`. |
| **IEC 3.6** / **GB 2.10** | 接通电流脱扣器 | **`making-current release`** | `MCR`: trips during closing above threshold; inoperative once closed. |
| **IEC 3.7** / **GB 2.11** | 短路脱扣器 | **`short-circuit release`** | Overcurrent release for short-circuit protection. |
| **IEC 3.8** / **GB 2.12** | 短延时短路脱扣器 | **`short-time delay short-circuit release`** | Operates after intentional short-time delay ($t_{sd}$). |
| **IEC 3.9** / **GB 2.13** | 报警开关 | **`alarm switch`** | Operates **only** upon tripping of the circuit-breaker. |
| **IEC 3.10** / **GB 2.14** | 带防止闭合的闭锁装置的断路器 | **`circuit-breaker with lock-out device preventing closing`** | `lock-out` always hyphenated. |
| **IEC 3.11–3.11.3** / **GB 2.15.1–2.15.2** | 极限短路分断能力 / 单极极限短路分断能力 *(国标 2020 暂未收录，按 IEC 2024 译)* / 运行短路分断能力 | **`ultimate / individual pole ultimate / service short-circuit breaking capacity`** | Corresponds to $I_{cu}$, $I_{cu1}$ (`IEC 5.3.6.2.3`), and $I_{cs}$. |
| **IEC 3.12** / **GB 2.16** | 断开时间 | **`opening time`** | `tripping time` noted in Note 2. |
| **IEC 3.13** / **GB 2.18** | 断路器的 $I^2t$ 特性 | **`I²t characteristic`** | Curve vs prospective RMS symmetrical current (`Fig. K.1`, `K.4–K.5`). |
| **IEC 3.14** / **GB 2.19** | 复位时间 | **`resetting time`** | Time after overcurrent tripping until reclosing capability resumes. |
| **IEC 3.15** / **GB 2.20** | 额定瞬时短路电流整定值 | **`instantaneous short-circuit current setting`** | Symbol **$I_i$** (`{{Ii_setting: ×In}}` or `A`). |
| **IEC 3.16** / **GB 2.21** | 过载电流整定值 | **`overload current setting`** | Symbol **$I_r$** (`{{Ir_setting: ×In}}` or `A`; equals $I_n$ if non-adjustable). |
| **IEC 3.17** / **GB 图 K.1** | 短时动作电流 | **`short-time pick-up current setting`** | Symbol **$I_{sd}$** (`{{Isd_setting: ×Ir}}`; `pick-up` hyphenated). |
| **IEC 3.18, 8.1.8** / **GB 2.22, 7.1.8** | 可编程逻辑控制器 / 数字输入与输出 | **`programmable logic controller (PLC)`** / **`digital inputs and outputs`** | References `IEC 60947-1:2020 Annex S` / `GB/T 14048.1 附录 S`. |
| **IEC 3.19** / **GB 2.23** | 闭合脱扣器 | **`closing release`** | Admitted IEC synonym: `closing coil` (recognize in EN→ZH; output `闭合脱扣器` in ZH and `closing release` in EN). |
| *IEC 60947-3* / *GB/T 14048.3* | 隔离开关 | **`switch-disconnector`** | Governed by `IEC 60947-3` / `GB/T 14048.3`, distinct from `Annex L` `CBI`. |

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

### 2.2 Main-Circuit, Control & Release Characteristics (`IEC 5.2–5.7` ⟷ `GB 4.2–4.7`)

| Symbol | ✅ Statutory Chinese (`GB/T 14048.2—2020`) | ✅ Unique Canonical IEC English (`IEC 60947-2:2024`) | IEC 2024 / GB/T 2020 | Value Slot |
| :--- | :--- | :--- | :--- | :--- |
| **$U_e$** | 额定工作电压 | **`Rated operational voltage`** | `IEC 5.3.2.1` / `GB 4.3.2.1` | `{{Ue: V AC}}` / `{{Ue: V DC}}` |
| **$U_i$** | 额定绝缘电压 | **`Rated insulation voltage`** | `IEC 5.3.2.2` / `GB 4.3.2.2` | `{{Ui: V}}` |
| **$U_{imp}$** | 额定冲击耐受电压 | **`Rated impulse withstand voltage`** | `IEC 5.3.2.3` / `GB 4.3.2.3` | `{{Uimp: kV}}` |
| **$I_{th}$** | 约定自由空气发热电流 | **`Conventional free air thermal current`** | `IEC 5.3.3.1` / `GB 4.3.3.1` | `{{Ith: A}}` |
| **$I_{the}$** | 约定封闭发热电流 | **`Conventional enclosed thermal current`** | `IEC 5.3.3.2` / `GB 4.3.3.2` | `{{Ithe: A}}` |
| **$I_n$** | 额定电流 | **`Rated current`** | `IEC 5.3.3.3` / `GB 4.3.3.3` ($= I_u = I_{th}$) | `{{In: A}}` |
| **$f_n$ / Duty** | 额定频率 / 额定工作制 | **`Rated frequency`** / **`Rated duty`** (`eight-hour duty` / `uninterrupted duty`) | `IEC 5.3.4–5` / `GB 4.3.4–5` | `{{fn: Hz}}` (`八小时工作制` / `不间断工作制`) |
| **$I_{cm}$** | 额定短路接通能力 | **`Rated short-circuit making capacity`** | `IEC 5.3.6.1, 5.3.6.3` / `GB 4.3.6.1, 4.3.6.3` | `{{Icm: kA peak}}` ($\ge n \times I_{cu}$ AC; $\ge I_{cu}$ DC) |
| **$I_{cu}$** | 额定极限短路分断能力 | **`Rated ultimate short-circuit breaking capacity`** | `IEC 5.3.6.2.2` / `GB 4.3.6.2.2` | `{{Icu: kA rms}}` |
| **$I_{cu1}$** | 相-中性线交流电压下的额定单极极限短路分断能力 *(国标 2020 暂未收录，按 IEC 2024 译)* | **`Rated individual pole ultimate short-circuit breaking capacity at phase-to-neutral AC voltage`** | `IEC 5.3.6.2.3, 9.3.11` / *—* | `{{Icu1: kA rms}}` ($= I_{cu}$ if all phase poles share identical design) |
| **$I_{cs}$** | 额定运行短路分断能力 | **`Rated service short-circuit breaking capacity`** | `IEC 5.3.6.2.4` / `GB 4.3.6.2.3` ($\ge 25\%\,I_{cu}$) | `{{Ics: kA rms}}` (`{{Ics_ratio: % of Icu}}`) |
| **$I_{cw}$** | 额定短时耐受电流 | **`Rated short-time withstand current`** | `IEC 5.3.6.4, Table 2` / `GB 4.3.6.4, 表 3` | `{{Icw: kA rms}}` for `{{Icw_duration: s}}` |
| **$U_s$ / $U_c$** | 额定控制电路电源电压 ($U_s$) / 额定控制电路电压 ($U_c$) | **`Rated control circuit supply voltage`** | `IEC 5.5.1, Table 3` / `GB 4.5.1, 4.7.2` | `{{Us: V}}` (preferred DC `24–250 V`, AC `24–230 V`) |
| **Aux** | 辅助电路与辅助开关 | **`Auxiliary circuits`** / **`Auxiliary switches`** | `IEC 5.6` / `GB 4.6` | `{{aux_config}}` |
| **Releases** | 分励脱扣器 / 过电流脱扣器 / 欠电压脱扣器 / 闭合脱扣器 | **`Shunt release`** (`8.2.1.2.3`), **`Overcurrent release`** (`instantaneous`, `definite time-delay`, `inverse time-delay`, `ground-fault`), **`Undervoltage release`** (`8.2.1.2.2`), **`Closing release`** (`3.19`) | `IEC 5.7.1–4` / `GB 4.7.1–4` | Thermal ref `+30 °C ± 2 °C`; electronic `-5 °C` to `+40 °C` (`0.3 %/K`). |

> **`ground-fault` vs `earth fault` Exact Standard Rule**: In `IEC 60947-2:2024`, hyphenated `earth-fault` has **0 occurrences**. Overcurrent G-stage protection (`IEC 5.7.1`, `8.2.1.2.4 c)`, `Table K.1`, `Fig. K.1`) uses **`ground-fault`** (19×). Physical fault current flowing to earth (`Annex B` `B.2.1.1`) uses unhyphenated **`earth fault`** (16×; `GB 附录 B.2.1.1`: `接地故障电流`).

---

## 3. Product Information, Conditions & Tests (`IEC Cl. 6–9` ⟷ `GB Cl. 5–8`)

- **Product Information (`IEC Cl. 6, Table 4` / `GB Cl. 5.2, 表 13`)**: Visible in service (`1.1–1.3`: $I_n$, suitability for isolation symbol, `O` / `|`); marked on body (`2.1–2.21`); literature (`6.1`: power loss `Annex G` / `功耗 附录 G`, `6.3`: `decommissioning and dismantling instructions` / `停运和拆除的附加信息`).
- **Normal Service Conditions (`IEC Cl. 7` / `GB Cl. 6`)**: Default **`pollution degree 3`** (`污染等级 3`); ambient `-5 °C` to `+40 °C` (`24 h` average $\le +35\,^\circ\text{C}$); altitude $\le 2\,000\text{ m}$; glow-wire (`IEC 8.1.1` / `GB 7.1.1`): `960 °C` / `850 °C`.
- **Withdrawable Positions (`IEC Cl. 8.1.2` / `GB Cl. 7.1.2`)**: **`connected position`**, **`test position`**, **`disconnected position`** (`隔离位置`).
- **Release Calibration & Temperature-Rise (`IEC Cl. 8.2.1.2.4, Table 5, 8.2.2, Table 6` / `GB Cl. 7.2.1.2.4, 表 6, 7.2.2, 表 7`)**:
  - Short-circuit `±20 %`; instantaneous/definite-time overload `±10 %`.
  - Inverse time-delay (`IEC Table 5` / `GB 表 6`): **`conventional non-tripping current`** (`约定不脱扣电流` $= 1.05 \times I_{\text{set}}$); **`conventional tripping current`** (`约定脱扣电流` $= 1.30 \times I_{\text{set}}$); **`conventional time`** (`约定时间` $= 2\text{ h}$, `1 h` for $I_n \le 63\text{ A}$).
  - Temperature-rise (`IEC Table 6` / `GB 表 7`): terminals `80 K`; manual operating means `25 K` (metal) / `35 K` (non-metal).
- **Operational Performance Capability (`IEC Cl. 8.2.4.2, Table 7` / `GB Cl. 7.2.4.2, 表 8`)**:
  - **`durability` has 0 occurrences in `IEC 60947-2:2024`**. Use **`operational performance without current`** (`不通电流的操作性能`) / **`operational performance with current`** (`通电流的操作性能`) and **`operating cycles`** (`操作循环次数`); use **`mechanical and electrical endurance`** (`机械和电气寿命`) in `Annex B / M / R`.
  - Standard minimums (`IEC Table 7` / `GB 表 8`): $\le 100\text{ A}$ (`8 500 + 1 500`), $\le 315\text{ A}$ (`7 000 + 1 000`), $\le 630\text{ A}$ (`4 000 + 1 000`), $\le 2\,500\text{ A}$ (`2 500 + 500`), $> 2\,500\text{ A}$ (`1 500 + 500`).
- **Tests & Sequences (`IEC Cl. 9.1–9.5` / `GB Cl. 8.1–8.5`)**: **`type tests`** (`型式试验`), **`routine tests`** (`常规试验`), **`special tests`** (`特殊试验`); **Seq I (`9.3.4`/`8.3.3`)**, **Seq II (`9.3.5`/`8.3.4`)**, **Seq III (`9.3.6`/`8.3.5`)**, **Seq IV (`9.3.7`/`8.3.6`)**, **Seq V (`9.3.8`/`8.3.7`)**, **Seq VI (`9.3.9`/`8.3.8`)**, **Seq VII (`9.3.10`/`8.3.9`)** **`Critical DC load current`** (`临界直流负载电流`: `4–63 A DC`, `5` forward + `5` reverse if unpolarized, arcing $\le 1\text{ s}$, + `50` cycles), **Seq VIII (`9.3.11`, *IEC 2024 only*)** $I_{cu1}$.

---

## 4. Coordination, Selectivity & Back-up Protection (`IEC Cl. 8.2.8, Annex A` ⟷ `GB Cl. 7.2.9, 附录 A`)

| ✅ Statutory Chinese (`GB/T 14048.2—2020`) | ✅ Unique Canonical IEC English (`IEC 60947-2:2024`) | Symbol & Clause | Technical Meaning |
| :--- | :--- | :--- | :--- |
| 断路器与串联在同一电路中的另一台短路保护装置在短路条件下的配合 | **`Coordination between a circuit-breaker and another short-circuit protective device (SCPD)`** | `IEC 8.2.8, Annex A` / `GB 7.2.9, 附录 A` | Official Ed. 6.0 title uses unhyphenated `Coordination` (`GB` aligns to `over-current selectivity`). |
| 选择性 / 全选择性 / 局部选择性 | **`Selectivity`** (`total selectivity` / `partial selectivity`) | `Annex A (A.5)` / `GB 2.17.1–2.17.3` | Downstream SCPD clears faults up to $I_s$ without upstream CB tripping. |
| 选择性极限电流 | **`Selectivity limit current`** | **$I_s$** (`IEC 8.2.7, A.5` / `GB 2.17.4`) | Maximum prospective current up to which selectivity is ensured (`{{Is: kA rms}}`). |
| 后备保护 | **`Back-up protection`** | `Annex A (A.6), Fig. A.1` | Upstream SCPD assists downstream CB above its standalone $I_{cu}$. |
| 交接电流 | **`Take-over current`** | **$I_B$** (`IEC 9.3.8` / `GB 2.17.5`) | Prospective current where fuse/upstream SCPD takes over interruption (`1.1 I_B`). |
| 额定限制短路电流 | **`Rated conditional short-circuit current`** | **$I_{cc}$** (`Annex L / M, Table K.1`) | `IEC 60947-2` / `GB/T 14048.2` symbol for CBIs/MRCDs is **$I_{cc}$** (reserve $I_q$ for general switchgear). |

---

## 5. Complete Normative & Informative Annexes Matrix (`Annexes A–R`)

| Annex & Status | ✅ Statutory Chinese (`GB/T 14048.2—2020`) | ✅ Canonical IEC English (`IEC 60947-2:2024`) | Key Clauses & Boundary Rules |
| :--- | :--- | :--- | :--- |
| **Annex B** (Normative) | 具有剩余电流保护的断路器（**CBR**）：额定剩余动作电流 $I_{\Delta n}$、额定剩余不动作电流 $I_{\Delta no}$、额定剩余短路接通和分断能力 $I_{\Delta m}$、极限不驱动时间 $\Delta t$、试验装置 `T`、动作功能与电源电压无关/有关的 CBR | **`Circuit-breaker incorporating residual current protection (CBR)`**; **`rated residual operating current`** ($I_{\Delta n}$), **`rated residual non-operating current`** ($I_{\Delta no}$), **`rated residual short-circuit making and breaking capacity`** ($I_{\Delta m}$), **`limiting non-actuating time at 2 IΔn`** ($\Delta t$), **`test device`** (`T`), **`CBR functionally independent of / dependent on line voltage`** | AC only (`B.1`). **`Type AC`**, **`Type A`**, **`Type B`** (up to `1 000 Hz`, `B.8.8`; *Type F/B+ per `IEC 62423`*). $I_{\Delta n} \le 30\text{ mA}$ non-time-delay. Test button `T` **`colour shall not be red or green`** (`B.7.2.6`). Crossed-out `1~` = 3-phase supply only. |
| **Annex C** (Normative) | 单极的短路试验程序；$I_{su}$ | **`Individual pole short-circuit test sequence`** (phase-earthed systems); symbol **$I_{su}$** | Marked with `C` prefix on $U_e$; $I_{su} \ge 25\%\,I_{cu}$ (`C.2–C.4`). |
| **Annex D** (Normative) | 预期用于铝导线连接的断路器的附加要求：基准导线、等电位连接装置、稳定性因数 $S_f$、具有最大截面积的未经处理圆铝导线的接入能力试验 | **`Circuit-breakers intended for connection of aluminium conductors`** (`AL` / `AL/CU`); **`reference conductor`** (`D.2.1`), **`equalizer`** (`D.2.2`), **`stability factor`** ($S_f$, `D.2.3`), **`insertability of unprepared round aluminium conductors`** (`D.8.5` / `GB D.8.4`) | $\ge 10\text{ mm}^2$ Al cables & bars (`D.1`); current cycling (`D.8.2`), climatic (`D.8.3`), mechanical (`D.8.4`). |
| **Annex E** (Informative) | 提交制造厂与用户协商的项目 | **`Items subject to agreement between manufacturer and user`** | Higher $I_{cm}$, $U_{imp} > 1\,000\text{ V AC}$, 4th-pole current, special tests, Al bars $> 3\,150\text{ A}$. |
| **Annex F** (Normative) | 带电子过电流保护的断路器的附加试验 | **`Additional tests for circuit-breakers with electronic overcurrent protection`** | EMC (`F.4–F.5`, Criterion A: no trip at $0.9\,I_{\text{set}}$, trip within $\pm 10\%$ at $2.0\,I_{\text{set}}$); `F.6–F.9`. |
| **Annex G** (Normative) | 功耗（功率因数法 / 积分法） | **`Power loss`** (**`power factor method`** / **`integral method`**) | Free-air steady-state watts (`W`); `G.2.1–G.2.3`; 4P without N current (`G.4.1`). |
| **Annex H** (Normative) | 用于 IT 系统的断路器的试验程序；$I_{IT}$ | **`Test sequence for circuit-breakers for IT systems`**; symbol **$I_{IT}$**; **`crossed-out IT symbol`** (`IEC 60417-6363`) | $I_{IT} = 1.2\times$ max setting (`500 A`–`50 kA`, `H.2–H.4`). Unsuitable voltages marked with crossed-out `IT` (`H.5`). |
| **Annex I** (Vacant) | 附录 I 空白 | **`Annex I (Vacant)`** | Vacant in both standards. |
| **Annex J** (Normative) | 电磁兼容性（EMC）— 环境 A / 环境 B | **`Electromagnetic compatibility (EMC)`** — **`Environment A`** / **`Environment B`** | Immunity (`Table J.1`) & emissions (`Table J.3`; `CISPR 11/32`). |
| **Annex K** (Informative) | 特征量符号和图形表示汇总表 | **`Glossary of symbols and graphical representation of characteristics`** | `Table K.1` master symbols; `Fig. K.1` (`RC, GF, LT, ST, INST`); `Fig. K.2–K.7`. |
| **Annex L** (Normative) | 无过电流保护要求的断路器（**CBI**） | **`Circuit-breaker not fulfilling the requirements for overcurrent protection (CBI)`** (`CBI-W / X / Y`) | **`X`/`Y`** in both standards; **`Class W`** ($I_{cu}=I_{cw}$) is **`IEC 2024` only** *(国标 2020 暂未收录)*. **`utilization category AC-22`** (`L.4.1`). |
| **Annex M** (Normative) | 剩余电流装置模块（无内部电流分断装置）（**MRCD**）：端子型 / 穿线型、组合时间、机械和电气寿命 | **`Modular residual current device (without integral current-breaking device) (MRCD)`** (`terminal` / `through-conductor`, `combination time`, `mechanical and electrical endurance`) | $U_s$, $U_n$, $I_{cc}$, $I_{\Delta c}$ (`M.4.3.2`), $I_{\Delta w}$ (`M.4.3.5`), `M.8.11`. |
| **Annex N** (Normative) | 电磁兼容 — 不包括在附录 B、F、M 中附件的附加要求和试验 | **`EMC requirements for auxiliary devices`** | Covers electronic `undervoltage / shunt / closing releases`, `motor-operators`, `remote status indicators`. |
| **Annex O** (Normative) | 瞬时脱扣断路器（**ICB**） | **`Instantaneous trip circuit-breaker (ICB)`** | Short-circuit protection only, marked `"ICB"` (`Table O.1`). |
| **Annex P** (Normative) | 光伏用直流断路器（**PV 断路器**） | **`DC circuit-breaker for use in photovoltaic (PV) applications`** (**`PV circuit-breaker`**) | Up to **`1 500 V DC`** (`P.1`), **`forward and reverse currents`** (`P.7.2`), `9.3.10 / P.8.3.9`, `P.8.3.10–11`. |
| **Annex Q** (Vacant) | 附录 Q 空白 | **`Annex Q (Vacant)`** | Vacant in both standards. |
| **Annex R** (Normative) | 带自动重合闸功能的剩余电流保护断路器（**CBAR**）：对地泄漏监测型（M）/ 固定延时型（TD） | **`Circuit-breaker incorporating residual current protection with automatic reclosing functions (CBAR)`** (**`Type M`** $I_{\Delta ar}$ / **`Type TD`**, `mechanical endurance` `R.8.5`) | Non-reclosing after overcurrent or manual open (`R.8.2–R.8.3`). |

---

## 6. Universal IEC Orthography, CAD & Anti-Chinglish Blacklist

> **Single Source of Truth**: Consulted in `Mode B` audit or `EN→ZH` decoding only; mirrored programmatically by [lint_text.py](../scripts/lint_text.py).

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
