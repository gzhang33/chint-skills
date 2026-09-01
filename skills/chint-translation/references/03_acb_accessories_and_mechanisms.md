# ACB Internal & External Accessories Taxonomy (Global Standard)

Aligned with ABB Formula AIR / Emax2, Schneider Masterpact / EasyPact, and LS ELECTRIC Susol.

## 1. Operating Mechanisms & Releases (操作机构与线圈)

| International Code | Chinese Term | Standard Global English Term | Technical Description & Function |
| :--- | :--- | :--- | :--- |
| **SHT / MX / YO** | 分励脱扣器 | **Shunt opening release (Shunt trip)** | Electrically trips the circuit breaker remotely upon applying control voltage. |
| **UVR / MN / YU** | 欠电压脱扣器 | **Undervoltage release** | Automatically trips the breaker when supply voltage drops below $35\% \sim 70\% U_n$. |
| **CC / XF / YC** | 闭合电磁铁 (合闸线圈) | **Shunt closing release (Closing coil)** | Electrically closes the charged circuit breaker remotely. |
| **M / MCH** | 储能电机 (电动操作机构) | **Spring charging motor (Gear motor)** | Automatically recharges the operating spring mechanism after closing. |
| **RTC / PF** | 准备合闸触点 | **Ready-to-close contact** | Indicates breaker is open, springs charged, and no trip lockout present. |
| **AX / OF** | 辅助触头 (开/关状态) | **Auxiliary contacts (Open/Closed status)** | Changeover auxiliary contacts reporting main contact position ($4\text{NO}+4\text{NC}, 6\text{NO}+6\text{NC}$). |
| **AL / SDE / SD** | 故障跳闸报警触头 | **Fault-trip indication contact (Alarm switch)** | SDE contact closing only when breaker trips on electrical fault (ETU trip). |
| **RESET / RES** | 电动复位装置 | **Electrical fault reset device** | Remotely resets the fault-trip lockout indicator coil. |

---

## 2. Drawout Cradle, Racking & Mechanical Interlocks (抽屉座与机械联锁)

| Item | Chinese Term | Standard Global English Term | Global Description |
| :--- | :--- | :--- | :--- |
| **Cradle / Chassis** | 抽屉座 / 导轨座 | **Guide frame (Cradle / Drawout Chassis)** | Housing with guide rails, safety shutters, and isolating cluster contacts. |
| **3-Position Contacts (AUP / CE-CD-CT)** | 抽屉座三位置信号触点 | **Connected / Test / Disconnected position contacts** | Microswitches signaling breaker position in cradle (Connected, Test, Disconnected/Isolated). |
| **Racking Handle** | 摇动手柄 | **Racking handle (Cranking handle)** | Mechanical crank for racking breaker between Connected, Test, and Disconnected positions. |
| **Safety Shutters** | 安全绝缘活门 | **Safety shutters (Shutter locking device)** | Automatically isolates primary stationary busbar stabs when breaker is withdrawn. |
| **Door Flange / Escutcheon** | 柜门框 / 面罩 | **Door escutcheon (Door flange)** | Gasketed sealing frame for switchboard door panel cutout ($ ext{IP40 / IP54}$). |
| **Interphase Barrier (PB)** | 相间隔板 | **Interphase barriers (Phase separators)** | Dielectric insulation plates mounted between main rear/front terminal busbars. |
| **Key Lock in OFF Position** | 钥匙锁 (断开位置锁定) | **Key lock in open position (KLC / VSPO)** | Ronis / Profalux / Castell cylinder lock securing breaker in open position. |
| **Padlocking Device** | 挂锁装置 (合/分闸锁定) | **Padlocking device (PLC / VBP)** | Accepts up to 3 padlocks securing pushbuttons in open position. |
| **Mechanical Interlock** | 机械联锁机构 | **Mechanical interlock for source changeover** | Cable or rod interlocking mechanism between 2 or 3 breakers (Normal/Emergency/Bus-tie). |
