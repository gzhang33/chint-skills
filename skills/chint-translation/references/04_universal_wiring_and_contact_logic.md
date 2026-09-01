# Industrial Wiring Logic, Trip Units & Auxiliary Circuit Reference

## 1. Dual-Function Changeover / SPDT Wiring Schemes

```
                  ┌─── Blue Wire  (NC - Normally Closed Contact) ───> Filling / Tank Inflow Mode
Black Wire (COM) ─┤
                  └─── Brown Wire (NO - Normally Open Contact)   ───> Drainage / Sump Emptying Mode
```

- **Tank Filling Mode (Auto-Fill)**: Black (COM) + Blue (NC). Low Level -> Closed (ON); High Level -> Open (OFF).
- **Sump Drainage Mode (Auto-Drain)**: Black (COM) + Brown (NO). Low Level -> Open (OFF); High Level -> Closed (ON).

---

## 2. Electronic Trip Units & Protection Functions (Source: 03_脱扣器与智能控制器)

| Code | Protection Function | Standard IEC English | Symbol / Setting | North American (UL/ANSI) |
| :--- | :--- | :--- | :--- | :--- |
| **TRM-TRP-001** | 智能型控制器 | **Intelligent Controller / Electronic Trip Unit** | ETU | Electronic Trip Device (ETD) / Direct-Acting Trip |
| **TRM-TRP-002** | 长延时过载保护 | **Long-Time Delay Protection (L)** | L / Ir / tr | Long-Time Pickup & Delay (L) |
| **TRM-TRP-003** | 短延时短路保护 | **Short-Time Delay Protection (S)** | S / Isd / tsd | Short-Time Pickup & Delay (S) |
| **TRM-TRP-004** | 瞬时短路保护 | **Instantaneous Protection (I)** | I / Ii | Instantaneous Pickup (I) |
| **TRM-TRP-005** | 接地故障保护 | **Ground Fault Protection (G)** | G / Ig / tg | Ground Fault Pickup & Delay (GF) |
| **TRM-TRP-006** | 中性线保护 | **Neutral Pole Protection (N)** | InN | Neutral Protection |
| **TRM-TRP-007** | 区域选择性联锁 | **Zone Selective Interlocking** | ZSI | Zone Selective Interlocking (ZSI) |
| **TRM-TRP-008** | 瞬时合闸涌流保护 | **Making Current Release** | MCR | Making Current Trip (MCR) |
| **TRM-TRP-009** | 高瞬动保护 | **High Instantaneous Short-Circuit Protection** | Override | Instantaneous Override Protection |
| **TRM-TRP-010** | 热记忆功能 | **Thermal Memory** | Thermal Image | Thermal Memory |
| **TRM-TRP-011** | 电流测量与电流表型 | **Current Measurement / Ammeter Type** | A Type | Ammeter Trip Unit |
| **TRM-TRP-012** | 电能质量与谐波分析型 | **Harmonic Analysis & Power Quality Type** | H Type | Harmonic Analyzer Trip Unit |

## 3. Internal & External Accessories (Source: 04_内部与外部附件机构)

| Code | Accessory Name | Standard IEC English | Code / Symbol | North American Term |
| :--- | :--- | :--- | :--- | :--- |
| **TRM-ACC-001** | 分励脱扣器 | **Shunt Release** | SHT / MX | Shunt Trip (ST) |
| **TRM-ACC-002** | 欠电压脱扣器 | **Undervoltage Release** | UVR / MN | Undervoltage Trip (UV) |
| **TRM-ACC-003** | 闭合电磁铁 | **Closing Release / Closing Electromagnet** | CC / CEM / XF | Closing Coil / Closing Solenoid |
| **TRM-ACC-004** | 储能电机 | **Stored Energy Motor / Motor Operator** | M / MOE | Charging Motor / Motor Mechanism |
| **TRM-ACC-005** | 辅助触头 | **Auxiliary Contacts / Auxiliary Switches** | AX / OF | Auxiliary Switches (AUX) |
| **TRM-ACC-006** | 故障跳闸报警触头 | **Fault Trip Alarm Switch / Alarm Contact** | AL / SD | Bell Alarm / Trip Indicator Switch |
| **TRM-ACC-007** | 准备合闸触点 | **Ready-to-Close Contact** | RTC | Ready-to-Close Switch |
| **TRM-ACC-008** | 抽屉座位置信号触点 | **Position Indication Switches** | TOC / MOC | Drawout Position Switches |
| **TRM-ACC-009** | 钥匙锁 | **Key Lock / Cylinder Lock** | KL | Key Interlock |
| **TRM-ACC-010** | 按钮锁定装置 | **Pushbutton Lock Device / Lockout Cover** | VBP | Pushbutton Lockout Cover |
| **TRM-ACC-011** | 机械联锁 | **Mechanical Interlock** | Interlock | Mechanical Interlock |
| **TRM-ACC-012** | 相间隔板 | **Interphase Barrier / Phase Barrier** | DD / PB | Phase Barrier / Terminal Partition |
| **TRM-ACC-013** | 安全绝缘活门 | **Safety Shutters** | Shutters | Safety Shutters |
| **TRM-ACC-014** | 摇动手柄 | **Racking Handle / Cranking Handle** | Handle | Racking Crank |

## 4. Terminal Connections & Mechanical Positions (Source: 05_安装接线与结构尺寸)

| Code | Terminal / Position | Standard IEC English | Abbr. | North American Term |
| :--- | :--- | :--- | :--- | :--- |
| **TRM-INS-001** | 水平后接线 | **Horizontal Rear Connection** | Horizontal / H | Horizontal Rear Busbar Connection |
| **TRM-INS-002** | 垂直后接线 | **Vertical Rear Connection** | Vertical / V | Vertical Rear Busbar Connection |
| **TRM-INS-003** | 前接线 | **Front Connection** | FC | Front Connection Pads |
| **TRM-INS-004** | 旋转90°接线端子 | **90° Rotatable Terminal Pads** | Rotatable Terminal | 90° Rotatable Busbar Terminals |
| **TRM-INS-005** | 加长接线排 | **Extended Terminal Bars / Spreaders** | ET | Terminal Extension Spreaders |
| **TRM-INS-006** | 抽屉座 | **Cradle / Drawout Chassis** | Cradle / CD | Drawout Cradle / Sub-Base |
| **TRM-INS-007** | 连接位置 | **Connected Position** | Connected | Connected Position |
| **TRM-INS-008** | 试验位置 | **Test Position** | Test | Test Position |
| **TRM-INS-009** | 分离位置 | **Disconnected Position / Isolated Position** | Disconnected | Disconnected Position |
| **TRM-INS-010** | 外形尺寸 (宽×高×深) | **Overall Dimensions (W × H × D)** | W x H x D | Frame Dimensions (W x H x D) |
| **TRM-INS-011** | 门框 / 柜门面罩 | **Door Flange / Escutcheon** | DF / MP | Door Collar / Escutcheon Frame |
| **TRM-INS-012** | 防护等级 (IP30/IP40/IP54) | **Degree of Protection (IP30/IP40/IP54)** | IP Rating | Enclosure Protection Rating |
