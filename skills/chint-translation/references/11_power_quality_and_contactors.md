# Power Quality, Contactors & Motor Starters Standards Reference

## 1. Standards Compliance

- **Contactors & Starters**: `IEC 60947-4-1` (Low-voltage electromechanical contactors and motor-starters), `UL 60947-4-1`.
- **Power Quality (SVG / APF / Capacitors)**: `IEC 62477-1`, `IEC 61000-3-2`, `IEC 61000-3-12`, `IEEE 519` (Harmonic control in power systems).
- **CHINT Product Lines**:
  - **NXC Series Contactors & Starters**: AC/DC contactors ($6	ext{ A} \sim 630	ext{ A}$), thermal overload relays (NXR), star-delta starters.
  - **NDG / SV Series Power Quality**: Static Var Generators (SVG), Active Power Filters (APF), low-voltage power capacitor banks, detuned filter reactors.

---

## 2. Contactors & Starters Taxonomy (一接与电机控制)

| Chinese Term | Standard IEC English | North American (NEMA / UL) | Description |
| :--- | :--- | :--- | :--- |
| **交流接触器** | **AC Contactor** | Magnetic Contactor | Electromagnetic switching device for remote motor/load control. |
| **电动机起动器** | **Motor Starter** | Full Voltage Non-Reversing (FVNR) Starter | Contactor combined with thermal overload relay / manual motor protector. |
| **热过载继电器** | **Thermal Overload Relay (TOR)** | Thermal Overload Relay | Bimetallic thermal protection device against motor overload and phase loss. |
| **电子式过载继电器** | **Electronic Overload Relay (EOR)** | Solid-State Overload Relay (SSOLR) | Microprocessor-controlled motor overload, phase unbalance, and stall protection. |
| **星三角起动器** | **Star-Delta Starter ($Y	ext{-}\Delta$)** | Wye-Delta Starter | Reduced-voltage starting system for large 3-phase induction motors. |
| **可逆接触器 (机械联锁)** | **Reversing Contactor (Mechanically Interlocked)** | Reversing Contactor Assembly | Dual contactors with mechanical and electrical interlocks for forward/reverse motor control. |
| **真空接触器** | **Vacuum Contactor** | Vacuum Contactor | Contactor with vacuum interrupter bottles for high-switching frequency / harsh environments. |
| **使用类别 AC-3** | **Utilization Category AC-3** | Squirrel cage motor starting | Standard squirrel-cage induction motor starting and switching off during run. |
| **使用类别 AC-4** | **Utilization Category AC-4** | Inching / Plugging / Jogging | Severe duty motor starting, inching (jogging), and reverse current braking. |

---

## 3. Power Quality (APF, SVG, Capacitors & Harmonics)

| Chinese Term | Standard IEC / IEEE English | Abbr. | Technical Function |
| :--- | :--- | :--- | :--- |
| **有源电力滤波器** | **Active Power Filter** | **APF** | Fast IGBT-based power electronic device generating compensating currents to cancel load harmonics ($2	ext{nd} \sim 50	ext{th}$ orders). |
| **静止无功发生器** | **Static Var Generator** | **SVG** | High-speed dynamic reactive power compensator providing stepless inductive and capacitive reactive power (Target $	ext{PF} \ge 0.99$). |
| **自愈式低压电力电容器** | **Self-Healing Low-Voltage Shunt Power Capacitor** | **Power Capacitor** | Metalized polypropylene film capacitor with self-healing dielectric properties for power factor correction. |
| **滤波电抗器 (串联电抗器)** | **Detuned Filter Reactor / Series Reactor** | **Detuned Reactor** | Iron-core reactor paired with capacitors to avoid parallel resonance and suppress harmonic amplification ($7\%, 14\%$). |
| **总谐波失真 (电流/电压)** | **Total Harmonic Distortion (Current / Voltage)** | **THD-i / THD-u** | Ratio of RMS value of harmonic components to the fundamental frequency value. |
| **无功功率补偿控制器** | **Reactive Power Compensation Controller (PFC Controller)** | **PFC Controller** | Microprocessor unit measuring network grid parameters and step-switching capacitor banks or SVGs. |
