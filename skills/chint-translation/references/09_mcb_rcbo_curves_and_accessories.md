# MCB, RCCB & RCBO (Modular DIN-Rail Devices) Standards Reference

## 0. Value Slot Convention

Curve multiples, module widths and breaking capacities are slots: `{{param_name: unit}}`.
Where a curve band is defined by the standard rather than by a product, the band is written once here as a slot with its standard reference, so product documents point at it instead of restating numbers.

---

## 1. Product Series & Standards Compliance

- **Primary Standards**:
  - `IEC 60898-1`: Household and similar electrical installations (AC).
  - `IEC 60947-2`: Industrial applications (higher breaking capacities $I_{cu}/I_{cs}$).
  - `IEC 61008-1` / `IEC 61009-1`: Residual current operated circuit breakers (RCCB / RCBO).
  - `UL 489` (Branch Circuit Protection) / `UL 1077` (Supplementary Protectors).
- **Product Line Taxonomy** (fill names from the current catalog):
  - **Miniature circuit breaker line**: rated current `{{In_range: A}}`, rated breaking capacity `{{Icn_range: kA}}`.
  - **Residual current circuit breaker line**: with / without overcurrent protection.
  - **Compact phase + neutral line**: modular breakers with a switched or unswitched neutral pole.

---

## 2. Tripping Characteristic Curves (脱扣特性曲线)

| Curve Type | Instantaneous Tripping Band (per IEC 60898-1) | Typical Applications & Electrical Behavior |
| :--- | :--- | :--- |
| **B Curve** | `{{B_curve_band: ×In}}` | Resistive loads, electric heating, long cable runs, generators with low short-circuit levels. |
| **C Curve** | `{{C_curve_band: ×In}}` | Standard commercial and domestic inductive loads, lighting, socket circuits, standard motors. |
| **D Curve** | `{{D_curve_band: ×In}}` | Highly inductive loads, heavy motor starting, welding equipment, distribution transformers, inrush currents. |

> The band values are defined by IEC 60898-1 and are quoted in product documents by reference to the curve letter, not restated per model.

---

## 3. Residual Current Device (RCD) Classification

| Device Type | Chinese Term | Standard Definition & Function |
| :--- | :--- | :--- |
| **RCCB** | 漏电开关 (无过载) | **Residual Current Circuit Breaker without Integral Overcurrent Protection** (pure RCD / isolator). |
| **RCBO** | 漏电断路器 (带过载) | **Residual Current Circuit Breaker with Integral Overcurrent Protection** (overload + short-circuit + leakage). |
| **Type AC** | AC型 (交流漏电) | Detects sinusoidal alternating residual currents only. |
| **Type A** | A型 (脉动直流漏电) | Detects sinusoidal alternating currents and pulsating DC residual currents (inverters, EV chargers). |
| **Type B** | B型 (平滑直流漏电) | Detects sinusoidal AC, pulsating DC, and smooth DC residual currents (solar PV, VFDs, medical). |

---

## 4. Pole Configurations & Electrical Terminology

| Chinese Term | Standard Notation | English Description |
| :--- | :--- | :--- |
| **1P+N (单模双线/相线+中性线)** | **1P+N (1 Pole + Neutral)** | Phase pole protected + switched or unswitched neutral pole in one module of width `{{module_width: mm}}`. |
| **2P / 3P / 4P** | **2P / 3P / 4P** | Two-pole / three-pole / four-pole multi-phase modular breakers. |
| **额定运行短路分断能力 (Ics)** | **Rated service short-circuit breaking capacity Ics** | `{{Ics_ratio: % of Icu}}` of `Icu`, per IEC 60947-2 / IEC 60898-1. |
| **额定短路能力 (Icn)** | **Rated short-circuit capacity Icn** | Breaking capacity tested to IEC 60898-1; `{{Icn: kA}}`. |
| **导轨安装 (DIN导轨)** | **DIN-Rail Mounting** | Symmetrical top-hat rail to IEC 60715; rail width `{{rail_width: mm}}`. |
| **自复式过欠压保护器** | **Self-Recovery Overvoltage and Undervoltage Protector (OVP / UVP)** | Automatic reconnecting protection device for residential distribution boards. |
