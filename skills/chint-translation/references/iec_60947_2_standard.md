# IEC 60947-2:2024 ⟷ GB/T 14048.2—2020 Dual-Standard Authoritative Reference

> **Pointers**: Load alongside `SKILL.md`. For full edition clause shifts, test recipes (`8.3.9`), and official standard print errata, see [edition_divergences_and_errata.md](edition_divergences_and_errata.md).

---

## 1. Core Terms & Definitions (`IEC 2024 Cl. 3.1–3.19` ⟷ `GB/T 2020 Cl. 2.1–2.23`)

> **Clause Alignment**: `IEC 60947-2:2024` inserted `Cl. 2` (`Normative references`), shifting `GB 2.x–8.x` to `IEC 3.x–9.x`; non-linear subclause shifts (`IEC Cl. 4` omits `GB 3.2/3.3/3.5`) also apply. Cite `IEC 2024` clauses in English and `GB/T 2020` clauses in Chinese.

<!-- AUTO:BEGIN standard/§1 -->
| IEC 2024 / GB/T 2020 | ✅ Statutory Chinese (`GB/T 14048.2—2020`) | ✅ Unique Canonical IEC English (`IEC 60947-2:2024`) | Symbol / Standard Note |
| :--- | :--- | :--- | :--- |
| **IEC 3.1** / **GB 2.1** | 断路器 | **`circuit-breaker`** | Always hyphenated. |
| **IEC 3.1.1** / **GB 2.1.1** | 壳架等级 | **`frame size`** | Expressed in `A`. Neither standard defines `Inm`. |
| **IEC 3.1.2, 8.1.6** / **GB 2.1.2, 7.1.6** | 结构段 | **`construction break`** | Construction differences within a `frame size`. |
| **IEC 3.2, 5.8** / **GB 2.2, 4.8** | 带熔断器的断路器 | **`integrally fused circuit-breaker`** | Series fuse per line pole (`IEC 8.2.7` Seq V `9.3.8` / `GB 7.2.8` Seq V `8.3.7`). |
| **IEC 3.3** / **GB 2.3** | 限流断路器 | **`current-limiting circuit-breaker`** | Limits **`let-through current`** / `cut-off current` (`Fig. K.2–K.3`) & $I^2t$ (`Fig. K.4–K.5`). |
| **IEC 3.4, 4.4** / **GB 2.4, 3.7** | 插入式断路器 | **`plug-in circuit-breaker`** | Removable via plug-in contacts. |
| **IEC 3.5, 4.4, 8.1.2** / **GB 2.5, 3.7, 7.1.2** | 抽屉式断路器 | **`withdrawable circuit-breaker`** | Isolating distance in `disconnected position` (`GB 7.1.2` `隔离位置`; `GB 2.5` `抽出位置`). |
| *Industry* / **GB 2.6, 3.3** | 塑料外壳式断路器 | **`moulded-case circuit-breaker`** | Statutory CB design classification in `GB 3.3` (`塑料外壳式` → `塑料外壳式断路器`). |
| *Industry* / **GB 2.7, 3.3** | 空气断路器（分类：万能式） | **`air circuit-breaker`** | `GB 2.7` defines `空气断路器`; `GB 3.3` classifies type as `万能式`. |
| **IEC 3.6** / **GB 2.10** | 接通电流脱扣器 | **`making-current release`** | *Industry* abbr. `MCR`; inoperative once closed. |
| **IEC 3.7** / **GB 2.11** | 短路脱扣器 | **`short-circuit release`** | Overcurrent release for short-circuit protection. |
| **IEC 3.8** / **GB 2.12** | 短延时短路脱扣器 | **`short-time delay short-circuit release`** | Operates after intentional short-time delay ($t_{sd}$). |
| **IEC 3.9** / **GB 2.13** | 报警开关 | **`alarm switch`** | Operates **only** upon circuit-breaker tripping. |
| **IEC 3.10** / **GB 2.14** | 带防止闭合的闭锁装置的断路器 | **`circuit-breaker with lock-out device preventing closing`** | `lock-out` always hyphenated. |
| **IEC 3.11.1–3.11.3** / **GB 2.15.1–2.15.2** | 极限短路分断能力 / 相-中性线交流电压下的单极极限短路分断能力 *(国标 2020 暂未收录，按 IEC 2024 译)* / 运行短路分断能力 | **`ultimate short-circuit breaking capacity`** / **`individual pole ultimate short-circuit breaking capacity at phase-to-neutral AC voltage`** / **`service short-circuit breaking capacity`** | Corresponds to $I_{cu}$, $I_{cu1}$ (`IEC 5.3.6.2.3`), and $I_{cs}$. |
| **IEC 3.12** / **GB 2.16** | 断开时间 | **`opening time`** | `tripping time` noted in Note 2. |
| **IEC 3.13** / **GB 2.18** | 断路器的 $I^2t$ 特性 | **`I²t characteristic of a circuit-breaker`** | Curve vs prospective RMS current (`Fig. K.4–K.5`). |
| **IEC 3.14** / **GB 2.19** | 复位时间 | **`resetting time`** | Time after tripping until reclosing capability resumes. |
| **IEC 3.15** / **GB 2.20** | 额定瞬时短路电流整定值 | **`instantaneous short-circuit current setting`** | Symbol **$I_i$** (`{{Ii_setting: ×In}}` or `A`; `GB 2.20` retains `额定`). |
| **IEC 3.16** / **GB 2.21** | 过载电流整定值 | **`overload current setting`** | Symbol **$I_r$** (`{{Ir_setting: ×In}}` or `A`; equals $I_n$ if non-adjustable). |
| **IEC 3.17** / **GB 表 K.1** | 短时动作电流 | **`short-time pick-up current setting`** | Symbol **$I_{sd}$** (`{{Isd_setting: ×Ir}}`; `GB 图 K.1`: `ST——短延时`). |
| **IEC 3.18, 8.1.8** / **GB 2.22, 7.1.8** | 可编程逻辑控制器 / 数字输入与输出 | **`programmable logic controller (PLC)`** / **`digital inputs and outputs`** | Refs `IEC 60947-1:2020 Annex S` / `GB/T 14048.1—2012 附录 S`. |
| **IEC 3.19** / **GB 2.23** | 闭合脱扣器 | **`closing release`** | Synonym `closing coil` / `闭合线圈` (`GB 2.23`). |
| *IEC 60947-3* / *GB/T 14048.3* | 隔离开关 | **`switch-disconnector`** | Distinct from `Annex L` `CBI`. |
<!-- AUTO:END standard/§1 -->

---

## 2. Classification, Ratings & Releases (`IEC Cl. 4–5` ⟷ `GB Cl. 3–4`)

### 2.1 Classification (`IEC Cl. 4.1–4.5` ⟷ `GB Cl. 3.1, 3.4, 3.6–3.8`)
- **Selectivity category (`IEC Cl. 4.1, 5.4` / `GB Cl. 3.1, 4.4`, `选择性类别`: `A 类` / `B 类`)**: **`selectivity category`** — **`Category A`** (no min $I_{cw}$ per `IEC 5.3.6.4 / GB 4.3.6.4`; intentional short-time delay permitted if declared $I_{cw}$ passes Seq IV per `IEC 5.4, 9.3.7 / GB 4.4, 8.3.6`) or **`Category B`** (delay $\ge 0.05\text{ s}$, preferred `0.05 – 0.1 – 0.25 – 0.5 – 1 s`; min $I_{cw} = 12\,I_n$ or `5 kA` [whichever is the greater / 取较大者] for $I_n \le 2\,500\text{ A}$, `30 kA` for $I_n > 2\,500\text{ A}$ per `IEC Table 2 / GB 表 3`). Distinct from **`utilization category`** (`使用类别`: `AC-3`, `AC-15`, `AC-22`, `DC-13`).
- **Operating control (`IEC 4.2` / `GB 3.4`) & closing (`IEC 8.2.1.1` / `GB 7.2.1.1`)**: **`dependent manual operation`** (`有关人力操作`), **`independent manual operation`** (`无关人力操作`), **`dependent power operation`** (`有关动力操作`), **`independent power operation`** (`无关动力操作`), **`stored energy operation`** (`储能操作`); closing forms use `closing` / `闭合`.
- **Maintenance (`IEC 4.3` / `GB 3.6`)**: **`maintainable`** (`需要维修`) vs **`non-maintainable`** (`不需要维修`).
- **Installation (`IEC 4.4` / `GB 3.7`)**: **`fixed`** (`固定式`), **`plug-in`** (`插入式`), **`withdrawable`** (`抽屉式`).
- **Enclosure (`IEC 4.5` / `GB 3.8` 外壳防护等级)**: **`degree of protection`** (`{{IP_code}}`, `IEC 60529` / `GB/T 14048.1—2012 Cl. 7.1.12`).

### 2.2 Main-Circuit, Control & Release Characteristics (`IEC 5.3–5.7` ⟷ `GB 4.3–4.7`)

<!-- AUTO:BEGIN standard/§2.2 -->
| Symbol | ✅ Statutory Chinese (`GB/T 14048.2—2020`) | ✅ Unique Canonical IEC English (`IEC 60947-2:2024`) | IEC 2024 / GB/T 2020 | Value Slot |
| :--- | :--- | :--- | :--- | :--- |
| **$U_e$** | 额定工作电压 | **`Rated operational voltage`** | `IEC 5.3.2.1` / `GB 4.3.2.1` | `{{Ue: V AC}}` / `{{Ue: V DC}}` |
| **$U_i$** | 额定绝缘电压 | **`Rated insulation voltage`** | `IEC 5.3.2.2` / `GB 4.3.2.2` | `{{Ui: V}}` |
| **$U_{imp}$** | 额定冲击耐受电压 | **`Rated impulse withstand voltage`** | `IEC 5.3.2.3` / `GB 4.3.2.3` | `{{Uimp: kV}}` |
| **$I_{th}$** | 约定自由空气发热电流 | **`Conventional free air thermal current`** | `IEC 5.3.3.1` / `GB 4.3.3.1` | `{{Ith: A}}` |
| **$I_{the}$** | 约定封闭发热电流 | **`Conventional enclosed thermal current`** | `IEC 5.3.3.2` / `GB 4.3.3.2` | `{{Ithe: A}}` |
| **$I_n$** | 额定电流 | **`Rated current`** | `IEC 5.3.3.3` / `GB 4.3.3.3` ($= I_u = I_{th}$) | `{{In: A}}` |
| **$f_n$** / **Duty** | 额定频率 / 额定工作制 | **`Rated frequency`** / **`Rated duty`** (`eight-hour duty` / `uninterrupted duty`) | `IEC 5.3.4–5.3.5` / `GB 4.3.4–4.3.5` | `{{fn: Hz}}` (`八小时工作制` / `不间断工作制`) |
| **$I_{cm}$** | 额定短路接通能力 | **`Rated short-circuit making capacity`** | `IEC 5.3.6.1, 5.3.6.3` / `GB 4.3.6.1, 4.3.6.3` | `{{Icm: kA peak}}` ($\ge n \times I_{cu}$ AC; $\ge I_{cu}$ DC) |
| **$I_{cu}$** | 额定极限短路分断能力 | **`Rated ultimate short-circuit breaking capacity`** | `IEC 5.3.6.2.2` / `GB 4.3.6.2.2` | `{{Icu: kA}}` |
| **$I_{cu1}$** | 相-中性线交流电压下的额定单极极限短路分断能力 *(国标 2020 暂未收录，按 IEC 2024 译)* | **`Rated individual pole ultimate short-circuit breaking capacity at phase-to-neutral AC voltage`** | `IEC 5.3.6.2.3, 9.3.11` / *—* | `{{Icu1: kA}}` |
| **$I_{cs}$** | 额定运行短路分断能力 | **`Rated service short-circuit breaking capacity`** | `IEC 5.3.6.2.4` / `GB 4.3.6.2.3` ($\ge 25\%\,I_{cu}$) | `{{Ics: kA}}` (`{{Ics_ratio: % of Icu}}`) |
| **$I_{cw}$** | 额定短时耐受电流 | **`Rated short-time withstand current`** | `IEC 5.3.6.4, Table 2` / `GB 4.3.6.4, 表 3` | `{{Icw: kA}}` for `{{Icw_duration: s}}` |
| **$U_s$ / $U_c$** | 额定控制电路电源电压 ($U_s$) / 额定控制电路电压 ($U_c$) | **`Rated control circuit supply voltage`** / **`Rated control circuit voltage`** | `IEC 5.5.1, Table 3, 5.7.2` / `GB 4.5.1, 表 5, 4.7.2` | `{{Us: V}}` (discrete preferred: DC `24 – 48 – 110 – 125 – 220 – 250 V`; 1~ AC `24 – 48 – 110 – 127 – 220 – 230 V`) |
| **Aux** | 辅助电路 / 辅助开关 | **`Auxiliary circuits`** / **`Auxiliary switches`** | `IEC 5.6` / `GB 4.6` (`IEC 3.9, L.1` / `GB 2.13, L.1`) | `{{aux_config}}` |
| **Releases** | 分励脱扣器 / 过电流脱扣器 / 欠电压脱扣器 / 闭合脱扣器 | **`Shunt release`** (`8.2.1.2.3; GB 7.2.1.2.3`) / **`Overcurrent release`** (`instantaneous`, `definite time-delay`, `inverse time-delay`, `ground-fault` *IEC 2024*) / **`Undervoltage release`** (`8.2.1.2.2; GB 7.2.1.2.2`) / **`Closing release`** (`3.19; GB 2.23`) | `IEC 5.7.1–5.7.4` / `GB 4.7.1–4.7.4` | Thermal ref `+30℃ ± 2℃`; non-thermal/electronic `-5℃` to `+40℃` (`IEC 5.7.3` `overload releases` / `GB 4.7.3`); ambient-compensated thermal band $\ge \pm 10\text{ K}$ within `0.3 %/K` (`IEC 8.2.1.2.4 b) 2), 9.3.4.2.3 b)` / `GB 7.2.1.2.4 b) 2), 8.3.3.2.3 b)`). |
<!-- AUTO:END standard/§2.2 -->

> **`ground-fault` vs `earth fault`**: G-stage protection (`IEC 5.7.1, 8.2.1.2.4 c)`, `Table K.1`) uses **`ground-fault`** (`GB 表 K.1 / 图 K.1`: `接地故障电流整定值` / `GF 接地故障`). Earth fault current (`Annex B.2.1.1`) uses **`earth fault`** (`GB 附录 B.2.1.1`: `接地故障电流`).

---

## 3. Product Information, Conditions & Tests (`IEC Cl. 6–9` ⟷ `GB Cl. 5–8`)

- **Product Info (`IEC Cl. 6, Table 4` / `GB Cl. 5.2, 表 13`)**: Visible `1.1–1.3` (`O`/`I` [`GB` `○`/`│`]), body `2.1–2.21` (`GB`: `2.1–2.18`), literature/instructions `3.1–3.19` (`GB` `资料`: `3.1–3.12`), auxiliaries `4.1–4.4`; `power loss` (`IEC 6.1` / `GB 5.1 功耗`); decommissioning & dismantling (`IEC 6.3` / `GB 5.3` `安装、操作及维修说明书`: `断路器停运和拆除的附加信息`).
- **Service Conditions (`IEC Cl. 7` / `GB Cl. 6`)**: Default **`pollution degree 3`** (`污染等级 3`); `-5℃` to `+40℃` (`24 h` avg $\le +35\,\text{℃}$); altitude $\le 2\,000\text{ m}$; glow-wire (`IEC 8.1.1` / `GB 7.1.1`): `960℃` / `850℃`.
- **Withdrawable Positions (`IEC 8.1.2` / `GB 7.1.2`)**: Statutory **`disconnected position`** (`隔离位置`; `GB 2.5` `抽出位置`); **`connected position`** and **`test position`** are *Industry* terms.
- **Calibration & Temperature-Rise (`IEC 8.2.1.2.4, Table 5–6` / `GB 7.2.1.2.4, 表 6–7`)**: Short-circuit `±20 %`; instantaneous/definite-time `±10 %`; inverse-time **`conventional non-tripping current`** (`约定不脱扣电流` `1.05`), **`conventional tripping current`** (`约定脱扣电流` `1.30`), **`conventional time`** (`约定时间` `2 h` / `1 h` for $I_n \le 63\text{ A}$); temperature-rise terminals `80 K`, handle `25 K` (metal) / `35 K` (non-metal).
- **Operational Performance (`IEC 8.2.4.2, Table 7` / `GB 7.2.4.2, 表 8`)**: Use **`operational performance without/with current`** (`不通电流/通电流的操作性能`; `GB 8.3.3.4.3–4`: `不带电/带电操作性能能力`) & **`operating cycles`** (`操作循环次数`); `Annex B`: **`operational performance capability`** (`操作性能能力`), `Annex M`: **`mechanical and electrical endurance`** (`机械和电气寿命`), `Annex R`: **`mechanical endurance`** (`机械耐久性`). Minimums (`Table 7 / 表 8`): `8 500+1 500` ($\le 100\text{ A}$), `7 000+1 000` ($\le 315\text{ A}$), `4 000+1 000` ($\le 630\text{ A}$), `2 500+500` ($\le 2\,500\text{ A}$), `1 500+500` ($> 2\,500\text{ A}$).
- **Tests (`IEC Cl. 9` / `GB Cl. 8`)**: **`type tests`** (`型式试验`), **`routine tests`** (`常规试验`), **`special tests`** (`特殊试验`); **Seq I–VI (`9.3.4–9.3.9` / `8.3.3–8.3.8`)**, **Seq VII (`9.3.10` / `8.3.9`)** **`Critical DC load current`** (`临界直流负载电流`: `4, 8, 16, 32, 63 A DC`), **Seq VIII (`9.3.11`, *IEC 2024 only*)** $I_{cu1}$.

---

## 4. Coordination, Selectivity & Back-up Protection (`IEC Cl. 8.2.8, Annex A` ⟷ `GB Cl. 7.2.9, 附录 A`)

<!-- AUTO:BEGIN standard/§4 -->
| ✅ Statutory Chinese (`GB/T 14048.2—2020`) | ✅ Unique Canonical IEC English (`IEC 60947-2:2024`) | Symbol | IEC 2024 / GB/T 2020 | Technical Meaning |
| :--- | :--- | :--- | :--- | :--- |
| 断路器与串联在同一电路中的另一台短路保护装置在短路条件下的配合 | **`Coordination between a circuit-breaker and another short-circuit protective device associated in the same circuit`** | — | `IEC 8.2.8, Annex A` / `GB 7.2.9, 附录 A` | `GB 2.17` = `过电流保护配合`, `GB 2.17.1` = `过电流选择性`. |
| 过电流选择性 / 全选择性 / 局部选择性 | **`Selectivity`** / **`total selectivity`** / **`partial selectivity`** | — | `IEC 60947-1:2020, Annex A (A.5)` / `GB 2.17.1–2.17.3, 附录 A (A.5)` | Downstream CB clears faults up to $I_s$ without upstream SCPD tripping (`GB A.1 / A.3.1 / A.5.2`). |
| 选择性极限电流 | **`Selectivity limit current`** | **$I_s$** | `IEC 8.2.7, A.5` / `GB 2.17.4` | Max prospective current ensuring selectivity (`{{Is: kA}}`). |
| 后备保护 | **`Back-up protection`** | — | `IEC Annex A (A.6), 60947-1 Annex X` / `GB 附录 A (A.6), 图 A.1, 图 A.3` | Upstream SCPD assists downstream CB above its standalone $I_{cu}$. |
| 交接电流 | **`Take-over current`** | **$I_B$** | `IEC 9.3.8` / `GB 2.17.5, 8.3.7` | Current where upstream SCPD takes over interruption (`1.1 I_B`). |
| 额定限制短路电流 | **`Rated conditional short-circuit current`** | **$I_{cc}$** | `Annex L / M, Table K.1` | Symbol for CBIs & MRCDs is **$I_{cc}$** (reserve $I_q$ for general switchgear). |
<!-- AUTO:END standard/§4 -->
