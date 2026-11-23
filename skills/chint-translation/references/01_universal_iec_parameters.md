# Universal Electrical Parameter & Rating Taxonomy (Global Industry Standard)

Aligned with the catalog conventions of the major low-voltage manufacturers (ABB / Schneider / Siemens / LS class).

## 0. Value Slot Convention (read first)

This file is a **translation configuration**, not a data sheet. No product specifications are stored here.
Every physical quantity is written as a slot:

```
{{param_name: unit}}
```

Rules:

1. A slot is **not a value**. It must never be rendered literally into a deliverable; the pipeline resolves it from the current product datasheet.
2. The unit inside the slot is part of the template and must be copied exactly (`kA rms`, `V`, `°C`, `N·m`, `mm²`).
3. When a source document supplies the number, the slot becomes `number + half-width space + unit` (see §4).
4. When no source is available, the slot stays unresolved and the sentence must be rewritten to avoid the quantity — never guess, never fill a default.
5. Standard identifiers (`IEC 60947-2`) and category designations (`AC-3`, `Curve C`, `Class PC`, `Cat B`, `ANSI 51N`) are terminology, not data, and are written literally.

---

## 1. Voltage, Current & Breaking Capacity Ratings

| Parameter Symbol | Chinese Term | Standard Global English Term | IEC Standard Basis | Value Slot |
| :--- | :--- | :--- | :--- | :--- |
| **$U_i$** | 额定绝缘电压 | **Rated insulation voltage** | IEC 60947-2:2024 Cl. 5.3.2.2 (refs IEC 60947-1:2020 Cl. 5.3.1.2) | `{{Ui: V}}` |
| **$U_{imp}$** | 额定冲击耐受电压 | **Rated impulse withstand voltage** | IEC 60947-2:2024 Cl. 5.3.2.3 (refs IEC 60947-1:2020 Cl. 5.3.1.3) | `{{Uimp: kV}}` |
| **$U_e$** | 额定工作电压 | **Rated operational voltage** *(phase-to-phase; IT systems require Annex H; phase-earthed systems require Annex C and `C` prefix)* | IEC 60947-2:2024 Cl. 5.3.2.1 | `{{Ue: V AC}}` / `{{Ue: V DC}}` |
| **$I_{th}$** | 约定自由空气发热电流 | **Conventional free air thermal current** | IEC 60947-2:2024 Cl. 5.3.3.1 (refs IEC 60947-1:2020 Cl. 5.3.2.1) | `{{Ith: A}}` |
| **$I_{the}$** | 约定封闭发热电流 | **Conventional enclosed thermal current** | IEC 60947-2:2024 Cl. 5.3.3.2 (refs IEC 60947-1:2020 Cl. 5.3.2.2) | `{{Ithe: A}}` |
| **$I_n$** | 额定电流 (额定不间断电流) | **Rated current** *(equal to rated uninterrupted current $I_u$ and $I_{th}$)* | IEC 60947-2:2024 Cl. 5.3.3.3 | `{{In: A}}` |
| **Frame size** / **$I_{nm}$** | 壳架等级 / 壳架电流 | **Frame size** *(IEC 60947-2:2024 term; expressed in amperes corresponding to the highest current rating of the group; construction variations within a frame size are a "construction break", Cl. 3.1.2)* / **Frame current ($I_{nm}$)** *(GB/T 14048.2 domestic symbol; not an IEC 60947-2 symbol, where Table 7 fn. a uses "maximum rated current for a given frame size")* | IEC 60947-2:2024 Cl. 3.1.1 & Cl. 3.1.2; $I_{nm}$: GB/T 14048.2 only | `{{Inm: A}}` |
| **Rated Duty** | 额定工作制 | **Rated duty (eight-hour duty / uninterrupted duty)** | IEC 60947-2:2024 Cl. 5.3.5 | `{{rated_duty}}` |
| **Breaking Capacity Type** | 分断能力型号 | **Breaking capacity type** *(Never "breaking capacity levels")* | Product Selection | Type N (Standard), Type S (Higher), Type H (High) |
| **$I_{cu}$** | 额定极限短路分断能力 | **Rated ultimate short-circuit breaking capacity** *(Catalog table header: Ultimate breaking capacity Vac 50/60 Hz)* | IEC 60947-2:2024 Cl. 5.3.6.2.2 | `{{Icu: kA rms}}` |
| **$I_{cu1}$** | 额定相间对中性线交流电压下极极限短路分断能力 | **Rated individual pole ultimate short-circuit breaking capacity at phase-to-neutral AC voltage** | IEC 60947-2:2024 Cl. 5.3.6.2.3 & Cl. 9.3.11 | `{{Icu1: kA rms}}` |
| **$I_{cs}$** | 额定运行短路分断能力 | **Rated service short-circuit breaking capacity** *(Catalog table header: Service breaking capacity Vac 50/60 Hz; must be $\ge 25\%$ of $I_{cu}$)* | IEC 60947-2:2024 Cl. 5.3.6.2.4 | `{{Ics: kA rms}}` (= `{{Ics_ratio: % of Icu}}` × `Icu`) |
| **$I_{cw}$** | 额定短时耐受电流 | **Rated short-time withstand current** *(preferred delays 0.05 s–1 s, Table 2)* | IEC 60947-2:2024 Cl. 5.3.6.4 & Table 2 | `{{Icw: kA rms}}` for `{{Icw_duration: s}}` |
| **$I_{cm}$** | 额定短路接通能力 | **Rated short-circuit making capacity** *(AC $\ge n \times I_{cu}$ per Table 1; DC $\ge I_{cu}$)* | IEC 60947-2:2024 Cl. 5.3.6.1 & Cl. 5.3.6.3 | Peak value: `{{Icm: kA peak}}` = `{{n_factor}}` × `Icu` |
| **$I_{cn}$** | 额定短路能力 (家用微断) | **Rated short-circuit capacity** | IEC 60898-1 | `{{Icn: kA}}` |

---

## 2. Operational Performance, Endurance, Power Loss & Selectivity

| Item | Chinese Term | Standard Global English Term | Standard Description / Unit |
| :--- | :--- | :--- | :--- |
| **Operational Performance (No Current) / Mechanical Endurance** | 机械寿命 / 无载操作循环次数 | **Operational performance without current / Number of operating cycles without current** *(main standard: Cl. 8.2.4.2 & Table 7)*; **Mechanical endurance** *(Annex M Cl. M.7.2.3 / M.8.11, Annex R Cl. R.8.5; NEVER attribute "durability" to IEC 60947-2 — 0 occurrences)* | Total operating cycles without current in the main circuit: `{{mech_ops: cycles}}` |
| **Operational Performance (With Current) / Electrical Endurance** | 电寿命 / 带载操作循环次数 | **Operational performance with current / Number of operating cycles with current** *(main standard: Cl. 8.2.4.2 & Table 7)*; **Electrical endurance** *(Annex M Cl. M.7.2.3 / M.8.11; NEVER attribute "durability" to IEC 60947-2)* | Operating cycles with current in the main circuit: `{{elec_ops: cycles}}` |
| **Power Loss** | 功率损耗 / 功耗 | **Power loss** *(IEC 60947-2:2024 Cl. 6.1 & Annex G; stated in watts per frame size or per pole)* | Thermal power loss at rated current: `{{power_loss: W/pole}}` |
| **Arcing Distance** | 飞弧距离 (零飞弧) | **Arcing distance / Zero arcing distance** | Required clear space above the arc extinction device (`Cl. 8.1.6`) / arc-extinguishing chamber / arc chutes *(catalog/OEM term; IEC 60947-2:2024 Cl. 8.1.5 addresses operator safety against discharged incandescent particles)*: `{{arcing_distance: mm}}` |
| **Selectivity Category** | 选择性类别 (A类/B类) | **Selectivity category (Category A / Category B)** *(IEC 60947-2:2024 Cl. 4.1 & Cl. 5.4; coordination in Cl. 8.2.8 & Annex A; never "discrimination")* | Cat A: non-selective or no assigned $I_{cw}$ per Cl. 5.3.6.4; Cat B: with assigned $I_{cw}$ and intentional short-time delay per Cl. 5.3.6.4 (min 0.05 s). |
| **Utilisation Category** | 使用类别 (AC-1 / AC-3 / AC-22 / AC-23A / DC-13 等) | **Utilisation category (AC-1 / AC-3 / AC-4 / AC-22 / AC-23A / DC-13 …)** *(IEC 60947-3 / IEC 60947-4-1; referenced for CBI in IEC 60947-2:2024 Annex L.4.1)* | Switchgear/contactor duty class; do NOT conflate with IEC 60947-2 selectivity category A/B. |

---

## 3. Environmental & Protection Ratings

| Item | Chinese Term | Standard Global English Term | Standards & Value Slot |
| :--- | :--- | :--- | :--- |
| **Degree of Protection** | 防护等级 | **Degree of protection (IP rating)** | IEC 60529 & IEC 60947-2:2024 Cl. 4.5 (refs IEC 60947-1:2020 Cl. 8.1.12); `{{IP_code}}` (write the two-digit code exactly as the datasheet gives it) |
| **Pollution Degree** | 污染等级 | **Pollution degree** | IEC 60947-2:2024 Cl. 7 (default pollution degree 3; refs IEC 60947-1:2020 Cl. 7.1.3.2); `{{pollution_degree}}` |
| **Ambient Temperature** | 运行环境温度 | **Ambient operating temperature range** | IEC 60947-2:2024 Cl. 7 (normal service conditions; thermal release ref. +30 °C per Cl. 5.7.3); `{{T_ambient_min: °C}}` to `{{T_ambient_max: °C}}`; different controller types may carry different ranges — always name the controller type in the sentence |
| **Altitude Derating** | 高原海拔及降容 | **Altitude & altitude derating factors** | IEC 60947-2:2024 Cl. 7 (normal service conditions; refs IEC 60947-1:2020 Cl. 7); no-derating ceiling `{{altitude_no_derating: m}}`; above it apply `{{altitude_factor_table}}` |
| **Tropicalization** | 湿热性能 / 热带化 | **Tropicalization / Damp heat capability** | IEC 60068-2-30 & IEC 60947-2:2024 Cl. 9.5 (special tests — damp heat) / Annex F (electronic overcurrent protection F.8) |
| **EMC Compliance** | 电磁兼容性 | **Electromagnetic compatibility (EMC)** | IEC 60947-2:2024 Cl. 8.3; Annex F (electronic overcurrent protection), Annex J (circuit-breakers, Environments A & B), Annex N (shunt/undervoltage/closing releases & motor-operators) |

---

## 4. Standard Units & Typographical Spacing Rules

1. **Space Between Number and Unit**:
   - A single half-width space MUST always be inserted between a numeric value and its physical unit.
     Write `{{value: A}}`, never the bare concatenation; the rule applies to every unit, e.g. `A`, `V`, `kV`, `kA`, `Hz`, `kW`, `N·m`, `mm`, `mm²`.
   - Correct: `number` + one space + `unit`. Wrong: no space, or two spaces.
2. **Temperature Notation**:
   - Always use a half-width space followed by the degree symbol and a capital `C`: `{{T: °C}}`.
   - Strictly prohibit the full-width Chinese temperature character `℃`, the bare `C` suffix without the degree symbol, or an omitted space (`{{T}}℃`, `{{T}}C`, `{{T}} ℃`).
3. **Placeholder Hygiene**:
   - Never ship a document containing an unresolved `{{...}}` slot. Resolve every slot, or rewrite the sentence without the quantity.
