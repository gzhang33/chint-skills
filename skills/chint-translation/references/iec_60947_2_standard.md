# IEC 60947-2:2024 ⟷ GB/T 14048.2—2020 Dual-Standard Authoritative Reference

> **Dual-Standard Statutory Anchors**: English deliverables obey **`IEC 60947-2:2024`** (Edition 6.0, 2024-09) + `IEC 60947-1:2020` exclusively. Chinese deliverables obey **`GB/T 14048.2—2020`** (*mod* `IEC 60947-2:2019`) statutory wording exclusively, with **zero colloquial parenthetical aliases**. `IEC 60947-2:2024` additions absent from `GB/T 14048.2—2020` (e.g. $I_{cu1}$, `CBI Class W`) are marked explicitly. All product ratings use `{{param_name: unit}}` slots.

---

## 1. Core Terms & Definitions (`IEC 2024 Cl. 3.1–3.19` ⟷ `GB/T 2020 Cl. 2.1–2.23`)

> **Clause Number Alignment**: `IEC 60947-2:2024` inserted `Cl. 2 Normative references`, shifting clauses `+1` relative to `GB/T 14048.2—2020` (`GB 2.x -> IEC 3.x`, `GB 3.x -> IEC 4.x`, `GB 4.x -> IEC 5.x`, `GB 5.x -> IEC 6.x`, `GB 7.x -> IEC 8.x`, `GB 8.x -> IEC 9.x`). Cite `IEC 60947-2:2024` clauses in English deliverables and `GB/T 14048.2—2020` clauses in Chinese deliverables.

| IEC 2024 / GB/T 2020 | ✅ Statutory Chinese (`GB/T 14048.2—2020`) | ✅ Unique Canonical IEC English (`IEC 60947-2:2024`) | Symbol / Standard Note |
| :--- | :--- | :--- | :--- |
| **IEC 3.1** / **GB 2.1** | 断路器 | **`circuit-breaker`** | Always hyphenated. |
| **IEC 3.1.1** / **GB 2.1.1** | 壳架等级 | **`frame size`** | Expressed in `A` (`frame size`). Neither standard defines `Inm`. |
| **IEC 3.1.2, 8.1.6** / **GB 2.1.2, 7.1.6** | 结构段 | **`construction break`** | Differences in construction within a given `frame size`; `IEC 8.1.6` / `GB 7.1.6`. |
| **IEC 3.2, 5.8** / **GB 2.2, 4.8** | 带熔断器的断路器 | **`integrally fused circuit-breaker`** | Series fuse per line pole (`IEC 8.2.7` Seq V `9.3.8` / `GB 7.2.8` Seq V `8.3.7`). |
| **IEC 3.3** / **GB 2.3** | 限流断路器 | **`current-limiting circuit-breaker`** | Limits **`let-through current`** / `cut-off current` (`Fig. K.2–K.3`) & $I^2t$ (`Fig. K.4–K.5`). |
| **IEC 3.4, 4.4** / **GB 2.4, 3.7** | 插入式断路器 | **`plug-in circuit-breaker`** | Has plug-in contacts enabling removal. |
| **IEC 3.5, 4.4, 8.1.2** / **GB 2.5, 3.7, 7.1.2** | 抽屉式断路器 | **`withdrawable circuit-breaker`** | Achieves isolating distance in `disconnected position` (`GB` statutory term: `抽屉式断路器`). |
| *Industry* / **GB 2.6, 3.3** | 塑料外壳式断路器 | **`moulded-case circuit-breaker`** | `GB 3.3` classifies under `塑料外壳式` (`EN→ZH` outputs `塑料外壳式断路器`). |
| *Industry* / **GB 2.7, 3.3** | 空气断路器（分类：万能式） | **`air circuit-breaker`** | `GB 2.7` defines `空气断路器`; `GB 3.3` classifies design type as `万能式`. |
| **IEC 3.6** / **GB 2.10** | 接通电流脱扣器 | **`making-current release`** | `MCR`: trips during closing above threshold; inoperative once closed. |
| **IEC 3.7** / **GB 2.11** | 短路脱扣器 | **`short-circuit release`** | Overcurrent release for short-circuit protection. |
| **IEC 3.8** / **GB 2.12** | 短延时短路脱扣器 | **`short-time delay short-circuit release`** | Operates after intentional short-time delay ($t_{sd}$). |
| **IEC 3.9** / **GB 2.13** | 报警开关 | **`alarm switch`** | Operates **only** upon tripping of the circuit-breaker. |
| **IEC 3.10** / **GB 2.14** | 带防止闭合的闭锁装置的断路器 | **`circuit-breaker with lock-out device preventing closing`** | `lock-out` always hyphenated. |
| **IEC 3.11–3.11.3** / **GB 2.15.1–2.15.2** | 极限短路分断能力 / 单极极限短路分断能力 *(国标 2020 暂未收录，按 IEC 2024 译)* / 运行短路分断能力 | **`ultimate short-circuit breaking capacity`** / **`individual pole ultimate short-circuit breaking capacity`** / **`service short-circuit breaking capacity`** | Corresponds to $I_{cu}$, $I_{cu1}$ (`IEC 5.3.6.2.3`), and $I_{cs}$. |
| **IEC 3.12** / **GB 2.16** | 断开时间 | **`opening time`** | `tripping time` noted in Note 2. |
| **IEC 3.13** / **GB 2.18** | 断路器的 $I^2t$ 特性 | **`I²t characteristic`** | Curve vs prospective RMS symmetrical current (`Fig. K.1`, `K.4–K.5`). |
| **IEC 3.14** / **GB 2.19** | 复位时间 | **`resetting time`** | Time after overcurrent tripping until reclosing capability resumes. |
| **IEC 3.15** / **GB 2.20** | 额定瞬时短路电流整定值 | **`instantaneous short-circuit current setting`** | Symbol **$I_i$** (`{{Ii_setting: ×In}}` or `A`). |
| **IEC 3.16** / **GB 2.21** | 过载电流整定值 | **`overload current setting`** | Symbol **$I_r$** (`{{Ir_setting: ×In}}` or `A`; equals $I_n$ if non-adjustable). |
| **IEC 3.17** / **GB 图 K.1** | 短时动作电流 | **`short-time pick-up current setting`** | Symbol **$I_{sd}$** (`{{Isd_setting: ×Ir}}`; `pick-up` hyphenated). |
| **IEC 3.18, 8.1.8** / **GB 2.22, 7.1.8** | 可编程逻辑控制器 / 数字输入与输出 | **`programmable logic controller (PLC)`** / **`digital inputs and outputs`** | References `IEC 60947-1:2020 Annex S` / `GB/T 14048.1 附录 S`. |
| **IEC 3.19** / **GB 2.23** | 闭合脱扣器 | **`closing release`** | Admitted IEC synonym: `closing coil` (`ZH` outputs `闭合脱扣器`; `EN` outputs `closing release`). |
| *IEC 60947-3* / *GB/T 14048.3* | 隔离开关 | **`switch-disconnector`** | Governed by `IEC 60947-3` / `GB/T 14048.3`, distinct from `Annex L` `CBI`. |

---

## 2. Clause 4 & Clause 5 — Classification, Ratings & Releases (`P23–30`)

### 2.1 Clause 4 Classification (`Cl. 4.1–4.5`, P23)
- **Selectivity category (`Cl. 4.1`, `5.4`, P23/P27)**: **`selectivity category`** — **`Category A`** (no assigned $I_{cw}$ per `5.3.6.4`) or **`Category B`** (assigned $I_{cw}$ and intentional short-time delay $\ge 0.05\text{ s}$ per `5.3.6.4` & `Table 2`: preferred delays `0.05 – 0.1 – 0.25 – 0.5 – 1 s`; min $I_{cw} = 12\,I_n$ or `5 kA` for $I_n \le 2\,500\text{ A}$, `30 kA` for $I_n > 2\,500\text{ A}$). Distinct from **`utilization category`** (`AC-3`, `AC-15`, `AC-22`, `DC-13`).
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
| **Releases** | 分励脱扣器 / 过电流脱扣器 / 欠电压脱扣器 / 闭合脱扣器 | **`Shunt release`** (`8.2.1.2.3`) / **`Overcurrent release`** (`instantaneous`, `definite time-delay`, `inverse time-delay`, `ground-fault`) / **`Undervoltage release`** (`8.2.1.2.2`) / **`Closing release`** (`3.19`) | `IEC 5.7.1–4` / `GB 4.7.1–4` | Thermal ref `+30 °C ± 2 °C`; electronic `-5 °C` to `+40 °C` (`0.3 %/K`). |

> **`ground-fault` vs `earth fault` Rule**: Overcurrent G-stage protection (`IEC 5.7.1`, `8.2.1.2.4 c)`, `Table K.1`, `Fig. K.1`) uses **`ground-fault`**. Physical fault current flowing to earth (`Annex B` `B.2.1.1`) uses **`earth fault`** (`GB 附录 B.2.1.1`: `接地故障电流`).

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
  - Use **`operational performance without current`** (`不通电流的操作性能`) / **`operational performance with current`** (`通电流的操作性能`) and **`operating cycles`** (`操作循环次数`); use **`mechanical and electrical endurance`** (`机械和电气寿命`) in `Annex B / M / R`.
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