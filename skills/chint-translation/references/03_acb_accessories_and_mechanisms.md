# ACB Internal & External Accessories Taxonomy (Global Standard)

Aligned with ABB Formula AIR / Emax2, Schneider Masterpact / EasyPact, and LS ELECTRIC Susol.

## 1. Operating Mechanisms, Releases & Arc Quenching (操作机构、脱扣附件与灭弧系统)

| International Code | Chinese Term | Standard Global English Term | Technical Description & Function |
| :--- | :--- | :--- | :--- |
| **SHT / MX / YO** | 分励脱扣器 | **Shunt opening release (Shunt trip)** | Electrically trips the circuit breaker remotely upon applying control voltage. |
| **UVR / MN / YU** | 欠电压脱扣器 | **Undervoltage release** | Automatically trips the breaker when supply voltage drops below $35\% \sim 70\% U_n$. |
| **UVR-D** | 延时欠电压脱扣器 | **Time-delay undervoltage release** | Delays circuit-breaker tripping for short-term line low-voltage conditions or power loss. |
| **CC / XF / YC** | 闭合电磁铁 (合闸线圈) | **Shunt closing release (Closing coil)** | Electrically closes the charged circuit breaker remotely. |
| **M / MCH / MOD** | 电动操作机构 (储能电机/电操) | **Motor Operator Device (MOD) / Spring charging motor** *(Never "Operating device" or "Motor hand")* | Automatically recharges the operating spring mechanism after closing or operates remotely. |
| **Arc Chute** | 灭弧室 | **Arc-extinguishing chamber (Arc chute)** *(Never "Interrupter" or "Arc room")* | De-ionizing grid plates dividing and extinguishing the electrical arc during contact separation. |
| **Pushbuttons** | 合/分闸按钮 | **Pushbutton (Closing/Opening pushbutton, ON/OFF pushbutton)** *(Never "device button")* | Manual mechanical pushbuttons on breaker front fascia for local closing/opening. |
| **RTC / PF** | 准备合闸触点 | **Ready-to-close contact** | Indicates breaker is open, springs charged, and no trip lockout present. |
| **AX / OF** | 辅助触头 (开/关状态) | **Auxiliary contacts (Open/Closed status)** | Changeover auxiliary contacts reporting main contact position ($4\text{NO}+4\text{NC}, 6\text{NO}+6\text{NC}$). |
| **AL / SDE / SD** | 故障跳闸报警触头 | **Fault-trip indication contact (Alarm switch)** | SDE contact closing only when breaker trips on electrical fault (ETU trip). |
| **RESET / RES** | 电动复位装置 | **Electrical fault reset device** | Remotely resets the fault-trip lockout indicator coil. |

---

## 2. Drawout Cradle, Racking & Mechanical Interlocks (抽屉座与机械联锁)

| Item | Chinese Term | Standard Global English Term | Global Description |
| :--- | :--- | :--- | :--- |
| **Cradle / Chassis** | 抽屉座 / 导轨座 | **Guide frame (Cradle / Drawout Chassis)** | Housing with guide rails, safety shutters, and isolating cluster contacts. |
| **Racking Handle Slot** | 摇手柄存放孔 / 摇手柄插入口 | **Racking handle storage slot / Racking handle entry** *(Never "storage hole")* | Dedicated cradle compartment or fascia slot for storing/inserting the racking crank. |
| **Racking Handle** | 摇动手柄 | **Racking handle (Cranking handle)** | Mechanical crank for racking breaker between Connected, Test, and Disconnected positions. |
| **3-Position Contacts (AUP / CE-CD-CT)** | 抽屉座三位置信号触点 | **Connected / Test / Disconnected position contacts** | Microswitches signaling breaker position in cradle (Connected, Test, Disconnected/Isolated). |
| **Safety Shutters** | 安全绝缘活门 | **Safety shutters (Shutter locking device)** | Automatically isolates primary stationary busbar stabs when breaker is withdrawn. |
| **Door Flange / Escutcheon** | 柜门框 / 面罩 | **Door escutcheon (Door flange)** | Gasketed sealing frame for switchboard door panel cutout ($\text{IP40 / IP54}$). |
| **Interphase Barrier (PB)** | 相间隔板 | **Interphase barriers (Phase separators)** | Dielectric insulation plates mounted between main rear/front terminal busbars. |
| **ACB Key Lock (KLC)** | 本体钥匙锁 (断开位置锁定) | **ACB Key Lock / Key lock in open position (KLC / VSPO)** *(Never "Body key lock")* | Cylinder lock (Ronis / Profalux / Castell) securing breaker in open/isolated position. |
| **Padlocking Device** | 挂锁装置 (合/分闸锁定) | **Padlocking device (PLC / VBP)** | Accepts up to 3 padlocks securing pushbuttons in open position. |
| **Mechanical Interlock** | 机械联锁机构 | **Mechanical interlock for source changeover** | Cable or rod interlocking mechanism between 2 or 3 breakers (Normal/Emergency/Bus-tie). |

---

## 3. Drawing, Mounting & Panel Cutout Callouts (CAD图纸与结构标注)

| Chinese Annotation | ❌ Forbidden / Untranslated Literal | ✅ Mandatory Professional English Term | Drawing / Application Context |
| :--- | :--- | :--- | :--- |
| **基准** | Base / Reference *(or left untranslated)* | **Datum** | CAD dimensional reference plane / coordinate datum. |
| **安装面** | Install surface | **Mounting surface** | Switchboard rear/bottom structural mounting plane. |
| **柜门内侧** | Inside door / Door back | **Inner side of door / Door interior** | Escutcheon clearance and cutout dimensioning. |
| **连接位置** | Connected state | **Connected position** | Main circuit and secondary circuits connected. |
| **试验位置** | Test state | **Test position** | Main circuit isolated; secondary control circuit connected. |
| **分离位置 / 隔离位置** | Separation place / Pull out | **Disconnected position / Isolated position** | Both main and secondary circuits completely isolated. |
