# ATS (Automatic Transfer Switching Equipment) Standards Reference

## 0. Value Slot Convention

Times, currents and delays are slots: `{{param_name: unit}}`.
IEC 60947-6-1 defines the classes and the transition types, not the timing values; every timing figure must therefore come from the product datasheet.

---

## 1. Product Series & Standards Compliance

- **Primary Standards**:
  - `IEC 60947-6-1`: Multiple function equipment — transfer switching equipment (TSE).
  - `GB/T 14048.11`: Automatic Transfer Switching Equipment.
  - `UL 1008`: Standard for Transfer Switch Equipment (North American standard).
- **Product Line Taxonomy** (fill names from the current catalog):
  - **Microprocessor-controlled ATS line**: Class CB / Class PC.
  - **Solenoid or motorized load-isolation transfer switch line**.

---

## 2. Equipment Classification (PC 级 vs CB 级)

| Class | Chinese Term | Standard IEC 60947-6-1 Definition | Mechanical Structure & Features |
| :--- | :--- | :--- | :--- |
| **PC Class** | **PC 级自动转换开关** | **Class PC TSE**: Capable of making, carrying, but not intended for interrupting short-circuit currents. | Uses a dedicated switch-disconnector or double-throw contact mechanism. High durability and high short-time withstand `{{Icw: kA rms}}`. |
| **CB Class** | **CB 级自动转换开关** | **Class CB TSE**: Equipped with overcurrent releases, intended to interrupt short-circuit currents. | Uses two interlocked circuit breakers (MCCB or MCB) with trip units providing overload & short-circuit protection. |

---

## 3. Transition Types & Operating Times

| Parameter / Mode | Chinese Term | Standard English Definition | Technical Meaning |
| :--- | :--- | :--- | :--- |
| **Open Transition (BBM)** | 先断后通 (开路转换) | **Open Transition (Break-Before-Make / BBM)** | Primary source disconnects completely before the secondary source connects. No phase-synchronisation risk. |
| **Closed Transition (MBB)** | 先通后断 (闭路转换) | **Closed Transition (Make-Before-Break / MBB)** | Momentary paralleling of synchronised dual sources without power interruption. Paralleling window `{{mbb_paralleling_time: ms}}`; the window is a product characteristic and must not be assumed. |
| **Transfer Time** | 转换动作时间 | **Total Operating Time / Transfer Time (t)** | Time interval from initiation of switching to final contact closure on the alternate source; `{{transfer_time: s}}`. |
| **Return Transfer Time** | 恢复转换延时 | **Return Transfer Delay (RTD)** | Delay before auto-switching back to the primary utility supply after restoration; `{{rtd: s}}`. |
| **Mechanical Interlock** | 机械联锁 | **Mechanical Interlocking Mechanism** | Physical barrier preventing simultaneous closing of the normal (Source I) and emergency (Source II) supplies. |
| **Electrical Interlock** | 电气联锁 | **Electrical Interlocking Circuit** | Auxiliary contact wiring preventing coil energization of the alternate breaker while the primary is closed. |

---

## 4. ATS Controller Modes & Terminology

- **Self-throw & Self-reset (自投自复)**: `Auto-Transfer and Auto-Recovery (Utility-to-Utility)`
- **Self-throw & Non-reset (自投不自复)**: `Auto-Transfer without Auto-Recovery (Mutual Standby)`
- **Utility to Generator (市电-发电机转换)**: `Utility-to-Generator Transfer Mode (Auto-start / Auto-cooldown signal)`
- **Phase Failure / Loss of Phase (缺相保护)**: `Phase loss protection / Phase failure detection`

---

## 5. Translation Guardrails

- Never state a paralleling window or a transfer time without a datasheet line; the standard fixes the class, not the timing.
- Keep `Class PC` / `Class CB` capitalised and never translate the class letters.
