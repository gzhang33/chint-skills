# Moulded-Case Circuit-Breaker (MCCB) and Special Derivative Series — Technical Specification

- **Translation Direction**: ZH → EN
- **Linguistic Register**: Track 1 — IEC Global Catalogue Register
- **Normative Baseline**: `IEC 60947-2:2024` (Edition 6.0, 2024-09)

---

## 1. Technical Specifications (Track 1 — IEC Global Catalogue Copy)

This series of moulded-case circuit-breakers (MCCBs, including withdrawable versions; `IEC 60947-2:2024 Cl. 3.1, Cl. 3.5, Cl. 4.4, Cl. 8.1.2 & Cl. 9.3.3.3`) is designed in accordance with `IEC 60947-2:2024`. The series supports terminals intended for connection of aluminium conductors, suitable for unprepared round aluminium conductors (`Annex D`, `Cl. D.1, Cl. D.3, Cl. D.5.2 & Cl. D.8.5`; terminal marking `AL` or `AL/CU`), and can be associated with external protection relays to form a circuit-breaker not fulfilling the requirements for overcurrent protection (`CBI`) correlated to utilisation category `AC-22` (`Annex L`, `Cl. L.1–L.5 & Table L.1`; symbol `CBI`, `AC-22`).

1. **Residual Current Protection Derivative (`CBR`, `Annex B`, `Cl. B.1`)**: Provides `Type B` residual current protection (`Cl. B.3.4, Cl. B.4.4 & Cl. B.8.8`), covering the rated residual operating current $I_{\Delta n}$ (`Cl. B.4.2.1 & Table K.1`) and the rated residual short-circuit making and breaking capacity $I_{\Delta m}$ (`Cl. B.4.1.3 & Table K.1`). Where equipped with a test device pushbutton designated by the letter `T` (`Cl. B.7.2.6 & Table K.1`), the pushbutton colour shall not be red or green.
2. **IT System Derivative (`Cl. 5.3.2.1` & `Annex H`)**: Verified in accordance with the individual pole short-circuit test sequence for circuit-breakers for IT systems (`Cl. H.2–H.4`) and marked with the IT system individual pole short-circuit current symbol $I_{\text{IT}}$ (`Cl. H.2 & Table K.1`). Voltage ratings not suitable for use in IT systems shall be marked with the crossed-out `IT` symbol (`IEC 60417-6363:2016-07`; `Cl. H.5, Table H.2, Table 4 item 2.6 & Table K.1`).
3. **Photovoltaic (PV) DC Derivative (`Annex P`)**: Dedicated to photovoltaic DC circuits (`Cl. P.1, Cl. P.4 & Cl. P.5`; marked `IEC 60947-2:2024, Annex P` per `Table P.2` and DC symbol `IEC 60417-5031:2002-10` per `Table 4 item 2.8`), subject to the standard upper voltage limit of `1 500 V DC` (`Cl. P.1`). Supports non-polarized interruption of both forward and reverse currents (`Cl. P.7.2 & Cl. P.8.3.2`) and is verified under Test Sequence VII for critical DC load current (`Cl. 9.3.10 & Cl. P.8.3.9`).
4. **Upstream/Downstream Selectivity and Back-up Protection Coordination (`Cl. 8.2.8` & `Annex A`)**: Provides selectivity limit current $I_s$ curves (`Cl. 8.2.7, Cl. A.5 & Table K.1`) and specifies the take-over current $I_B$ (`Cl. 9.3.8, Annex A & Table K.1`) in coordination with an upstream fuse or back-up short-circuit protective device (SCPD) (`Cl. A.6 & Figure A.1`).

---

## 2. IEC 60947-2:2024 Clause, Symbol & Terminology Mapping

| Chinese Source | Track 1 IEC 60947-2:2024 English | Standard Symbol / Marking | IEC 60947-2:2024 Clause Reference |
| :--- | :--- | :--- | :--- |
| 塑壳断路器（MCCB） | Moulded-case circuit-breaker (MCCB) | `MCCB` (`CB`) | `Cl. 1`, `Cl. 3.1`, `Cl. 8.1.6`, `Cl. 9.3.3.3` |
| 抽出式安装型 | Withdrawable circuit-breaker / Withdrawable mounting | `Withdrawable` | `Cl. 3.5`, `Cl. 4.4`, `Cl. 8.1.2` |
| 铝导体接线端子（适用于未经预处理的圆铝导线） | Terminals intended for connection of aluminium conductors (insertability of unprepared round aluminium conductors) | `AL` / `AL/CU` (`CU/AL`); stability factor `S` | `Annex D` (`Cl. D.1`, `Cl. D.2.3`, `Cl. D.3`, `Cl. D.5.2`, `Cl. D.8.5`) |
| 匹配外部继电器的无过电流保护派生型号（CBI） | Circuit-breaker not fulfilling the requirements for overcurrent protection (CBI) associated with external protection relays | `CBI` (`CBI-W` / `CBI-X` / `CBI-Y`, `Table L.1`); `Icu = Icw` (Class W) / `Icc` (Class X/Y) | `Annex L` (`Cl. L.1`, `Cl. L.2.1`, `Cl. L.3`, `Cl. L.4.2–L.4.3`, `Cl. L.5`, `Table L.1`) |
| 使用类别 AC-22 | Utilisation category `AC-22` | `AC-22` | `Cl. L.4.1` (Note); refs `IEC 60947-1:2020 Annex A` / `IEC 60947-3` |
| 剩余电流保护派生型（CBR） | Circuit-breaker incorporating residual current protection (CBR) | `CBR` | `Annex B` (`Cl. B.1`) |
| B 型剩余电流保护 | `Type B` residual current protection (behaviour in presence of a DC component) | `Type B` | `Cl. B.3.4`, `Cl. B.4.4`, `Cl. B.8.8` (`Tables B.6–B.9`) |
| 额定剩余动作电流 | Rated residual operating current | $I_{\Delta n}$ | `Cl. B.4.2.1`, `Annex K (Table K.1)` |
| 额定剩余短路接通和分断能力 | Rated residual short-circuit making and breaking capacity | $I_{\Delta m}$ | `Cl. B.4.1.3`, `Annex K (Table K.1)` |
| 测试按钮 T（颜色不得为红色或绿色） | Test device pushbutton designated by letter `T` (colour shall not be red or green) | `T` | `Cl. B.7.2.6`, `Annex K (Table K.1)` |
| IT 系统单极短路试验程序及符号 | Test sequence for circuit-breakers for IT systems (individual pole short-circuit test current) | $I_{\text{IT}}$ | `Cl. 5.3.2.1`, `Annex H` (`Cl. H.2–H.4`), `Annex K (Table K.1)` |
| 不适用电压等级的带叉 IT 符号 | Crossed-out `IT` symbol (not suitable for use in IT systems) | `IEC 60417-6363:2016-07` (crossed-out `IT`) | `Cl. H.5`, `Table H.2`, `Table 4 (item 2.6)`, `Annex K (Table K.1)` |
| 光伏直流派生型（标准上限 1 500 V DC） | DC circuit-breaker for use in photovoltaic (PV) applications (PV circuit-breaker; standard upper limit `1 500 V DC`) | `IEC 60947-2:2024, Annex P`; DC symbol `IEC 60417-5031:2002-10` | `Annex P` (`Cl. P.1`, `Cl. P.4`, `Cl. P.5`, `Table P.1`, `Table P.2`), `Table 4 (item 2.8)` |
| 正向与反向电流无极性分断 | Non-polarized interruption of forward and reverse currents | Terminals unmarked for line/load (`Table 15`) | `Cl. P.7.2`, `Cl. P.8.3.2` |
| 临界直流负载电流试验程序 | Test Sequence VII — Critical DC load current | `Seq VII` | `Cl. 9.3.10`, `Cl. P.8.3.9` |
| 上下级选择性与后备保护配合 | Coordination between a circuit-breaker and another SCPD: selectivity and back-up protection | `Annex A` (`Cl. A.5`, `Cl. A.6`, `Figure A.1`) | `Cl. 8.2.8`, `Annex A` (`Cl. A.5`, `Cl. A.6`, `Figure A.1`) |
| 选择性极限电流 | Selectivity limit current | $I_s$ | `Cl. 8.2.7`, `Annex A (Cl. A.5)`, `Annex K (Table K.1)` |
| 交接电流 | Take-over current | $I_B$ | `Cl. 9.3.8` (`Cl. 9.3.8.6`), `Annex A`, `Annex K (Table K.1)` |

---

## 3. Terminology & Standard Basis Notes

1. **IEC 60947-2:2024 Orthography and Core Nomenclature**:
   - Across `IEC 60947-2:2024`, the canonical terms use hyphenated `circuit-breaker`, British spelling (`moulded-case`, `withdrawable`, `aluminium`, `utilisation`, `colour`, `behaviour`), hyphenated `back-up` and `take-over`, and `-ize` verb/adjective morphology (`non-polarized`).
   - `IEC 60947-2:2024` does not establish a standalone product class for "moulded-case", but uses `moulded case` (`Cl. 9.3.3.3`) and `moulding` (`Cl. 8.1.6`). `Withdrawable circuit-breaker` (`Cl. 3.5 & Cl. 4.4`) requires a specified isolating distance in the disconnected position, position indication, and mechanical interlocks (`Cl. 8.1.2`).
2. **Aluminium Conductor Terminals (`Annex D`)**:
   - Normative `Annex D` applies to solid or stranded aluminium conductors and aluminium bars of cross-section $\ge 10\text{ mm}^2$ (`Cl. D.1`), excluding screwless terminals, flexible aluminium conductors, and simultaneous aluminium-plus-copper clamping in one unit.
   - `Cl. D.8.5` specifically defines the verification of insertability of `unprepared round aluminium conductors` having the maximum declared cross-section; terminal markings (`AL` or `AL/CU`) and surface preparation requirements (wire brushing with anti-oxidant compound or tin coating) are governed by `Cl. D.5.2–D.5.3`.
3. **CBI Derivative & Utilisation Category `AC-22` (`Annex L`)**:
   - A `CBI` (`Annex L`) is derived from an equivalent circuit-breaker of the same frame size (`Cl. L.2.1`) and cannot protect a circuit alone; it is distinct from a switch-disconnector under `IEC 60947-3`.
   - Under `Cl. L.3`, association with external protection relays and sensors specifically corresponds to `CBI Class W` (`CBI-W`, derived from a Selectivity Category B equivalent circuit-breaker with $I_{\text{cu}} = I_{\text{cw}}$ per `Cl. L.4.3`, isolation symbol `IEC 60617-S00287` + `S00220` per `Table L.1`), whereas `Class X` and `Class Y` carry a rated conditional short-circuit current $I_{\text{cc}}$ (`Cl. L.4.2`, isolation symbol `S00288`). `Cl. L.4.1` (Note) allows $I_n$ to be correlated to `utilisation category AC-22` (which must not be conflated with `selectivity category A/B` under `Cl. 4.1 & Cl. 5.4`).
4. **CBR Derivative (`Annex B`)**:
   - A `CBR` integrates both overcurrent and residual current protection in AC circuits (`Cl. B.1`), distinct from an `RCCB` (`IEC 61008-1`, no overcurrent protection) or household `RCBO` (`IEC 61009-1`).
   - `Annex B` (`Cl. B.3.4 & Cl. B.4.4`) covers `Type AC`, `Type A`, and `Type B` only (`Cl. B.8.8` verifies `Type B` up to `1 000 Hz` and composite/smooth DC residual currents); `Type F` and `Type B+` fall outside `IEC 60947-2:2024` (`IEC 62423` / `VDE 0664-400`).
   - `Cl. B.7.2.6` mandates that the test device be designated by the letter `T` and that its colour shall not be red or green (light colour preferred).
5. **IT System Suitability (`Annex H`)**:
   - Normative `Annex H` verifies individual pole short-circuit breaking capability under a second earth fault in the presence of a first fault (`Cl. 5.3.2.1 & Cl. H.2–H.4`), with normative test current bounds $500\text{ A} \le I_{\text{IT}} \le 50\text{ kA}$ (`Cl. H.2`) and post-test dielectric leakage current $\le 6\text{ mA}$ (`Cl. H.3`). Unsuitable voltage ratings require the crossed-out `IT` graphic symbol (`IEC 60417-6363:2016-07`) per `Cl. H.5`, `Table H.2`, and `Table 4 (item 2.6)`.
6. **PV DC Derivative (`Annex P`) & Test Sequence VII (`Cl. 9.3.10`)**:
   - Normative `Annex P` covers DC circuit-breakers for PV applications up to the standard ceiling of `1 500 V DC` (`Cl. P.1`; normative $U_{\text{imp}}$ values under OVC II in `Table P.1`, e.g. `8 000 V` at $U_e \le 1\,500\text{ V DC}$), requiring marking `IEC 60947-2:2024, Annex P` (`Cl. P.5 & Table P.2`).
   - Under `Cl. P.7.2`, overload tests (`Cl. 8.2.4.1`) and `Annex H` do not apply, and the circuit-breaker must interrupt both forward and reverse currents up to its breaking capacity (non-polarized terminals unmarked for line/load per `Table 15`, `Cl. P.8.3.2`).
   - Under `Cl. P.8.3.9`, Test Sequence VII (`Cl. 9.3.10`, critical DC load current) is executed with `10` operations (`5` forward and `5` reverse at `1 ms` time constant) followed by `100` operational performance cycles (increased from `50` cycles in general `Cl. 9.3.10`).
7. **Selectivity & Back-up Coordination (`Annex A`)**:
   - `IEC 60947-2:2024` uses `selectivity` (`Cl. A.5`, replacing legacy terminology) and hyphenated `back-up protection` (`Cl. A.6`, including `Figure A.1` for conditional $I_{\text{cu1}}$ verification).
   - `Selectivity limit current` ($I_s$, `Cl. 8.2.7, Cl. A.5 & Table K.1`) defines the upper current limit of selective coordination; `take-over current` ($I_B$, `Cl. 9.3.8 & Table K.1`, verified at `1.1 I_B` in `Cl. 9.3.8.6`) defines the current at which the associated fuse or back-up SCPD takes over interruption.
8. **Data Integrity & No-Fabrication Compliance**:
   - No product-specific ratings omitted from the source text (such as frame size, $I_n$, $U_e$, $I_{\text{cu}}$, $I_{\text{cs}}$, $I_{\Delta n}$, $I_{\Delta m}$, $I_{\text{IT}}$, $I_s$, $I_B$, or conductor cross-section range) have been fabricated or inherited. All numeric values mentioned in these notes (`1 500 V DC`, `10 mm²`, `1 000 Hz`, `500 A`–`50 kA`, `6 mA`, `8 000 V`, `1 ms`, `10` / `100` / `50` operations) are normative `IEC 60947-2:2024` standard boundaries or test requirements, not product datasheet claims.
