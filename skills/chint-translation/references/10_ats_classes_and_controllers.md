# ATS (Automatic Transfer Switching Equipment) Standards Reference

## 1. Product Series & Standards Compliance

- **Primary Standards**:
  - `IEC 60947-6-1`: Multiple function equipment - Transfer switching equipment (TSE).
  - `GB/T 14048.11`: Automatic Transfer Switching Equipment.
  - `UL 1008`: Standard for Transfer Switch Equipment (North American standard).
- **CHINT Product Lines**:
  - **NZ7 Series**: Microprocessor-controlled automatic transfer switches (Class CB / Class PC).
  - **NZ6 / NH40SZ Series**: Solenoid or motorized load-isolation transfer switches.

---

## 2. Equipment Classification (PC 级 vs CB 级)

| Class | Chinese Term | Standard IEC 60947-6-1 Definition | Mechanical Structure & Features |
| :--- | :--- | :--- | :--- |
| **PC Class** | **PC 级自动转换开关** | **Class PC TSE**: Capable of making, carrying, but not intended for interrupting short-circuit currents. | Uses a dedicated switch-disconnector or double-throw contact mechanism. Extreme endurance, high short-time withstand ($I_{cw}$). |
| **CB Class** | **CB 级自动转换开关** | **Class CB TSE**: Equipped with overcurrent releases, intended to interrupt short-circuit currents. | Uses two interlocked circuit breakers (MCCB or MCB) with trip units providing overload & short-circuit protection. |

---

## 3. Transition Types & Operating Times

| Parameter / Mode | Chinese Term | Standard English Definition | Technical Meaning |
| :--- | :--- | :--- | :--- |
| **Open Transition (BBM)** | 先断后通 (开路转换) | **Open Transition (Break-Before-Make / BBM)** | Primary source disconnects completely before secondary source connects. Zero phase synchronization risk. |
| **Closed Transition (MBB)** | 先通后断 (闭路转换) | **Closed Transition (Make-Before-Break / MBB)** | Momentary paralleling (<100 ms) of synchronized dual sources without power interruption. |
| **Transfer Time** | 转换动作时间 | **Total Operating Time / Transfer Time (t)** | Time interval from initiation of switching to final contact closure on alternate source. |
| **Return Transfer Time** | 恢复转换延时 | **Return Transfer Delay (RTD)** | Delay time before auto-switching back to primary normal utility power after restoration. |
| **Mechanical Interlock** | 机械联锁 | **Mechanical Interlocking Mechanism** | Physical barrier preventing simultaneous closing of normal (Source I) and emergency (Source II) supplies. |
| **Electrical Interlock** | 电气联锁 | **Electrical Interlocking Circuit** | Auxiliary contact wiring preventing coil energization of alternate breaker while primary is closed. |

---

## 4. ATS Controller Modes & Terminology

- **Self-throw & Self-reset (自投自复)**: `Auto-Transfer and Auto-Recovery (Utility-to-Utility)`
- **Self-throw & Non-reset (自投不自复)**: `Auto-Transfer without Auto-Recovery (Mutual Standby)`
- **Utility to Generator (市电-发电机转换)**: `Utility-to-Generator Transfer Mode (Auto-start / Auto-cooldown signal)`
- **Phase Failure / Loss of Phase (缺相保护)**: `Phase loss protection / Phase failure detection`
