# MCB, RCCB & RCBO (Modular DIN-Rail Devices) Standards Reference

## 1. Product Series & Standards Compliance

- **Primary Standards**:
  - `IEC 60898-1`: Household and similar electrical installations (AC).
  - `IEC 60947-2`: Industrial applications (Higher breaking capacities $I_{cu}/I_{cs}$).
  - `IEC 61008-1` / `IEC 61009-1`: Residual current operated circuit breakers (RCCB / RCBO).
  - `UL 489` (Branch Circuit Protection) / `UL 1077` (Supplementary Protectors).
- **CHINT Product Lines**:
  - **Kunlun NXB Series**: Miniature Circuit Breakers ($0.5	ext{ A} \sim 125	ext{ A}$, $4.5	ext{ kA} \sim 10	ext{ kA}$).
  - **NXBLE / NL1 Series**: Residual Current Circuit Breakers with / without Overcurrent Protection.
  - **DPN / NBH-125 Series**: Phase + Neutral compact modular breakers.

---

## 2. Tripping Characteristic Curves (脱扣特性曲线)

| Curve Type | Instantaneous Tripping Current Range | Typical Applications & Electrical Behavior |
| :--- | :--- | :--- |
| **B Curve** | $3 \sim 5 	imes I_n$ | Resistive loads, electric heating, long cable runs, generators with low short-circuit levels. |
| **C Curve** | $5 \sim 10 	imes I_n$ | Standard commercial and domestic inductive loads, lighting, socket circuits, standard motors. |
| **D Curve** | $10 \sim 14 	imes I_n$ (or $10 \sim 20 	imes I_n$) | Highly inductive loads, heavy motor starting, welding equipment, distribution transformers, inrush currents. |

---

## 3. Residual Current Device (RCD) Classification

| Device Type | Chinese Term | Standard Definition & Function |
| :--- | :--- | :--- |
| **RCCB** | 漏电开关 (无过载) | **Residual Current Circuit Breaker without Integral Overcurrent Protection** (Pure RCD / Isolator). |
| **RCBO** | 漏电断路器 (带过载) | **Residual Current Circuit Breaker with Integral Overcurrent Protection** (Overload + Short-circuit + Leakage). |
| **Type AC** | AC型 (交流漏电) | Detects sinusoidal alternating residual currents only. |
| **Type A** | A型 (脉动直流漏电) | Detects sinusoidal alternating currents and pulsating DC residual currents (inverters, EV chargers). |
| **Type B** | B型 (平滑直流漏电) | Detects sinusoidal AC, pulsating DC, and smooth DC residual currents (solar PV, VFDs, medical). |

---

## 4. Pole Configurations & Electrical Terminology

| Chinese Term | Standard Notation | English Description |
| :--- | :--- | :--- |
| **1P+N (单模双线/相线+中性线)** | **1P+N (1 Pole + Neutral)** | Phase pole protected + switched or unswitched neutral pole in 1 module ($18	ext{ mm}$). |
| **2P / 3P / 4P** | **2P / 3P / 4P** | Two-pole / Three-pole / Four-pole multi-phase modular breakers. |
| **额定运行短路分断能力 (Ics)** | **Rated service short-circuit breaking capacity Ics** | $I_{cs} = 75\% I_{cu}$ or $100\% I_{cu}$ per IEC 60947-2 / IEC 60898-1. |
| **额定短路能力 (Icn)** | **Rated short-circuit capacity Icn** | Maximum breaking capacity tested per household standard IEC 60898-1 ($6	ext{ kA}, 10	ext{ kA}$). |
| **导轨安装 (DIN导轨)** | **DIN-Rail Mounting (TH35-7.5 / TH35-15)** | Standard symmetrical $35	ext{ mm}$ top-hat DIN rail mounting per IEC 60715. |
| **自复式过欠压保护器** | **Self-Recovery Overvoltage and Undervoltage Protector (OVP / UVP)** | Automatic reconnecting protection device for residential distribution boards. |
