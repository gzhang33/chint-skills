# IEC 60947-2:2024 ⟷ GB/T 14048.2—2020 Edition Divergences & Official Print Errata

> **Conditional Disclosure**: Load only when auditing standard edition differences, detailed test procedures, or verifying apparent typos printed verbatim in the source standards.

## 1. Clause-Number Shifts & Core Terminology Divergences

- **Top-level `+1` shift**: `IEC 60947-2:2024` inserted `Cl. 2 Normative references`, shifting `GB 2.x -> IEC 3.x`, `GB 3.x -> IEC 4.x`, `GB 4.x -> IEC 5.x`, `GB 5.x -> IEC 6.x`, `GB 6.x -> IEC 7.x`, `GB 7.x -> IEC 8.x`, `GB 8.x -> IEC 9.x`.
- **Non-linear subclause shifts**: `IEC Cl. 4` omits `GB 3.2 / 3.3 / 3.5` (Foreword b)); `GB 7.2.6` vs `IEC 8.2.x`; `GB 8.3.x` vs `IEC 9.3.x`.
- **Ed. 6.0 additions absent in `GB/T 14048.2—2020`**:
  - `$I_{cu1}$` (`IEC 3.11.2, 5.3.6.2.3, 9.3.11` Seq VIII) — `GB` defines `2.15.1–2.15.2` ($I_{cu}$, $I_{cs}$) only.
  - `ground-fault` overcurrent release classification & test (`IEC 5.7.1 (2d), 8.2.1.2.4 c)`) — `GB 4.7.1 2)` lists `a)–c)` only, though `GB 表 K.1 / 图 K.1` already define `接地故障电流整定值 ($I_g$)` / `GF 接地故障`.
- **`IEC 3.15` vs `GB 2.20`**: `IEC 2024 Cl. 3.15` dropped `"rated"` (`instantaneous short-circuit current setting`), whereas `GB 2.20` retains `额定` (`额定瞬时短路电流整定值`).
- **`IEC 5.7.3` vs `GB 4.7.3`**: Ambient-independent `-5℃` to `+40℃` band applies to `overload releases` in `IEC 5.7.3` (plus external/remote display setting adjustment added in Ed. 6.0), vs non-thermal `过电流脱扣器（除热式外）` in `GB 4.7.3`.
- **Withdrawable `disconnected position`**: `GB 2.5` uses `抽出位置`, whereas `GB 7.1.2` uses `隔离位置`; both map to IEC **`disconnected position`**.
- **Operational performance wording**: `GB 7.2.4.2` & `表 8` use `不通电流的操作性能` / `通电流的操作性能` (`操作循环次数`), whereas test subclauses `GB 8.3.3.4.3 / 8.3.3.4.4` & `表 9b/9c` use `不带电操作性能能力` / `带电操作性能能力`.
- **Selectivity & coordination**: `IEC 2024` Title uses `Coordination` (`A.3` spells `co-ordination`) and delegates selectivity definitions (`A.5`) and curves (`Annex X`) to `IEC 60947-1:2020`; `GB 2.17.1–2.17.3` & `图 A.1–图 A.5` retain them directly (`IEC Fig. A.1` is single-pole `$I_{cu1}$` wiring).
- **`Critical DC load current` (`IEC 9.3.10 / GB 8.3.9`) full recipe**: Discrete test currents `4, 8, 16, 32, 63 A DC` (`±10%`, `≤ I_n`), `2×` up/down step extension when needed, `5` forward + `5` reverse ops if unpolarized (`5` ops if polarized), arcing time `≤ 1 s`, `+ 50` operations on same sample, followed by DC dielectric test (`IEC 9.3.4.6 / GB 8.3.3.6`).

## 2. Annex A–R Edition Divergences (`IEC 2024` vs `GB/T 2020`)

- **Annex B (CBRs)**: `GB B.2.3.2–B.2.3.3` definitions use `动作功能与电源电压无关/有关的 CBR`, while `B.3.1`, `表 B.4`, and test clauses use `功能上与电源电压无关/有关的 CBR`.
- **Annex C (`C.3`) & Annex H (`H.3`)**: `IEC 2024` adds leakage current verification (`≤ 6 mA`) alongside dielectric withstand; `GB` retains `验证介电耐受能力` only.
- **Annex D (Aluminium conductors)**: `IEC D.1` requires `≥ 10 mm²` (`D.8.3` DC climatic test is IEC-only; `D.5.2` allows `AL` / `AL/CU` or `CU/AL`). `GB` covers down to `4 mm²` (`表 D.4/D.6/D.7`; `表 D.2` `0–10 mm²`), marks `AL` / `CU/AL`, lacks `D.8.3` climatic test, and places round-Al insertability at `GB D.8.4` (`IEC D.8.5`).
- **Annex E (Items subject to agreement)**: `GB 附录 E` has no `表 E.1` table number and omits `7.2.3.2` (`> 1 000 V AC`), `表 D.8` (Al bars `> 3 150 A`), `B.8.2.3`, and the first `9.3.4.5` entry.
- **Annex F / Annex J (EMC)**: Radiated emission ceiling is `30–6 000 MHz` (`CISPR 11/32`) in `IEC F.5.4 / Table J.3`, vs `30–1 000 MHz` (`GB 4824 / CISPR 32`) in `GB F.5.4 / 表 J.3`.
- **Annex G (Power loss)**: `IEC G.2.1` restricts scope to `> 400 A`, splits `power factor method` (`G.2.1 a`) vs `integral method` (`G.2.1 b`, *IEC 2024 only*), and adds `G.4` (4P without N current). `GB G.2.1` (`一般情况`) uses the summation formula without `> 400 A` cap and ends at `G.3`.
- **Annex L (CBIs)**: `CBI Class W` ($I_{cu} = I_{cw}$) is `IEC 2024` only; `GB/T 14048.2—2020` covers `X` / `Y` only.
- **Annex M (MRCDs)**: `M.7.2.3` & `表 M.3` use `机械和电气寿命`, whereas `M.8.11` heading uses `机电寿命`.
- **Annex P (PV DC)**: `Table P.1` ($U_{imp}=6\,000\text{ V}$ tier) max $U_e$ is `1 250 V` (`IEC`) vs `1 000 V` (`GB`); `表 P.2 (P2.1)` marking is `GB/T 14048.2—2020-附录P或PV` vs `IEC 60947-2:2024, Annex P`.

## 3. Official Standard Print Errata (Verified on Source Scans — Preserve Quotes)

- **`GB/T 14048.2—2020`**:
  - `前言` PⅢ misprints `2.21 过电流整定值` (normative `2.21` & `表 K.1` is **`过载电流整定值`**).
  - `前言` PⅣ misprints `附录 D … 特殊要求` (normative `附录 D` title is **`附加要求`**).
  - `表 6` (`PDF P26`) header misprints `定时间` (normative `7.2.1.2.4` is **`约定时间`**).
  - `表 9` omits sequence numeral `Ⅶ`.
  - `表 K.1` (`PDF P154`) mistakenly cites `B.8.9.2` for `IEC 60417-6364:2016-07` (`只用于三相电源的 CBR`; actual clause is `表 B.3 (B2.3)`).
  - `R.7.2.2` prints `监测时间应不少于 1 h` ($\ge 1\text{ h}$), inverted against `IEC R.7.2.2` (`shall be less than 1 h`, $< 1\text{ h}$).
  - `R.8.3` prints `分励脱扣和过电压脱扣` ("overvoltage"), whereas `IEC R.8.3` states `shunt trip or undervoltage release`.
- **`IEC 60947-2:2024` (Ed. 6.0)**:
  - `Table 4 (3.19)` spells `aluminum` (`D.7` mixes `aluminium`/`aluminum`); `Table B.3 (B2.8)` spells `catalog`; TOC prints `I_CC` vs `$I_{cc}$` in `Annex L/M`.
  - `R.8.7` / `Table R.2` cite `B.8.10` / `B.8.11–B.8.12` (off-by-1 relative to `Annex B` `B.8.11–B.8.13`).
