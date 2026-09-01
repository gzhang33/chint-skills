# MCCB (Molded Case Circuit Breaker) Technical Taxonomy & Standards Reference

## 1. Product Series & Standards Compliance

- **Primary Standards**: `IEC 60947-2:2024` (Low-Voltage Circuit-Breakers), `GB/T 14048.2`, `UL 489` (Molded-Case Circuit Breakers).
- **CHINT Product Lines**:
  - **Kunlun NXM Series**: Standard industrial and commercial distribution (10 A to 1600 A).
  - **High-End NXS / NM8 Series**: High-breaking capacity, critical infrastructure and datacenter distribution.
  - **Noark Ex9M Series**: North American UL 489 listed molded case circuit breakers.

---

## 2. Release & Trip Unit Types (脱扣器分类与术语)

| Chinese Term | Standard IEC English | North American (UL 489) | Function & Description |
| :--- | :--- | :--- | :--- |
| **热磁式脱扣器** | **Thermal-Magnetic Trip Unit (TM)** | Thermal-Magnetic Trip | Bimetallic thermal overload + magnetic short-circuit protection. Fixed (TM-D) or Adjustable (TM-A). |
| **电子脱扣器 / 智能脱扣器** | **Electronic Trip Unit (ETU)** | Electronic Trip Unit | Microprocessor-based trip unit providing precise L/S/I/G protection curves. |
| **电磁脱扣器 (单磁式)** | **Magnetic-Only Trip Unit (MA / M)** | Instantaneous-Only / MCP | Motor circuit protector without thermal element, paired with thermal overload relay. |
| **剩余电流保护脱扣器 (漏电)** | **Residual Current Protection Release (RCD)** | Ground Fault / ELCB Module | Integrated or add-on residual current / earth leakage trip unit (NXMLE series). |
| **过载长延时整定 (Ir)** | **Overload setting / Long-time pickup Ir** | Long-time pickup setting | Adjustable current threshold ($0.7 \sim 1.0  imes I_n$). |
| **短路短延时整定 (Isd)** | **Short-time delay pickup Isd** | Short-time pickup setting | Selective short-circuit current threshold ($2 \sim 10  imes I_r$). |
| **短路瞬时整定 (Ii)** | **Instantaneous pickup Ii** | Instantaneous trip setting | Fast short-circuit tripping threshold ($5 \sim 10  imes I_n$). |

---

## 3. Mounting, Mechanism & Accessories (安装方式与附件)

| Chinese Term | ❌ Forbidden Literal Term | ✅ Mandatory Professional English | Description |
| :--- | :--- | :--- | :--- |
| **板前接线 (固定式)** | Front wiring | **Front Connection (Fixed mounted)** | Standard front busbar / cable lug connection. |
| **板后水平/垂直接线** | Back wiring | **Rear Connection (Rear horizontal HR / Rear vertical VR studs)** | Rear terminal studs for switchboard compartment. |
| **插入式安装** | Insert installation | **Plug-in Mounting (Plug-in Base)** | Allows quick replacement without disconnecting busbars. |
| **抽屉式安装 (拔出式)** | Drawer type | **Drawout Mounting / Withdrawable Base** | Withdrawable chassis with safety shutters. |
| **旋转操作手柄 (直接/门部)** | Rotate handle | **Rotary Handle (Direct / Extended / Door-mounted)** | Direct handle on breaker or door coupling mechanism. |
| **电动操作机构 (电操)** | Motor hand | **Motor Operator / Motor Mechanism (MOE / MOD)** | Remote electric charging and switching unit. |
| **相间隔板** | Phase space board | **Interphase Barriers / Phase Barriers** | Insulation barriers between terminal lugs. |
| **接线端子罩 (扩展罩)** | Wire cover | **Terminal Cover / Extended Terminal Shield** | IP40 protection against direct contact. |

---

## 4. MCCB Specific Anti-Chinglish Guardrails

- ❌ *Plastic shell breaker* -> ✅ **Molded Case Circuit Breaker (MCCB)**
- ❌ *Double breaking point* -> ✅ **Rotary double-break contact system (Roto-active breaking)**
- ❌ *Leakage plastic shell* -> ✅ **Molded Case Circuit Breaker with Residual Current Protection (CBR / RCBO)**
