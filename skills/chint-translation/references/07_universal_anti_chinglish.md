# Anti-Chinglish Industrial Catalog Dictionary & False Friends

## 1. High-Frequency Forbidden Terms & Anti-Hallucination Guardrails

| Code | Chinese Term | ❌ Strictly FORBIDDEN Translation | ✅ Mandatory Professional English | Standard Rationale |
| :--- | :--- | :--- | :--- | :--- |
| **TRM-DON-001** | 万能式断路器 | ❌ `Universal Breaker ❌` | ✅ **Air Circuit Breaker (ACB) / Low-Voltage Power Circuit Breaker** | 万能式断路器中的'万能'指多功能通用，英文必须译为 Air Circuit Breaker，严禁直译为 Universal Circuit Breaker |
| **TRM-DON-002** | 闭合电磁铁 | ❌ `Closed electromagnet ❌` | ✅ **Closing Release (CC / CEM) / Closing Electromagnet** | '闭合'是动作而非状态，IEC标准功能术语为 Closing Release，硬件零件清单中可使用 Closing Electromagnet；严禁直译为 closed electromagnet 或 close electromagnet |
| **TRM-DON-003** | 分励脱扣器 | ❌ `Excitation release / Shunting release ❌` | ✅ **Shunt Release (SHT / MX) / Shunt Trip (ST)** | '分励'指旁路分励跳闸，IEC标准术语为 Shunt Release，北美为 Shunt Trip；严禁误译为 Excitation release 或中式英语 Shunting release |
| **TRM-DON-004** | 欠电压脱扣器 | ❌ `Lack voltage trip ❌` | ✅ **Undervoltage Release (UVR / MN) / Undervoltage Trip (UV)** | 必须严格使用标准术语 Undervoltage Release (UVR) |
| **TRM-DON-005** | 抽屉座 | ❌ `Drawer box ❌` | ✅ **Cradle / Drawout Chassis / Withdrawable Sub-base** | 断路器抽屉座的专业英文为 Cradle 或 Chassis，严禁直译为 Drawer box / Slide box |
| **TRM-DON-006** | 相间隔板 | ❌ `Phase space plate ❌` | ✅ **Interphase Barrier / Phase Barrier** | 电气绝缘隔板的标准英文为 Interphase Barrier 或 Phase Barrier |
| **TRM-DON-007** | 门框 / 柜门面罩 | ❌ `Face mask ❌` | ✅ **Door Flange / Escutcheon** | 配合柜门开孔密封的构件必须译为 Door Flange 或 Escutcheon |
| **TRM-DON-008** | 区域选择性联锁 | ❌ `Area select lock ❌` | ✅ **Zone Selective Interlocking (ZSI)** | 专有技术缩写与名称必须严格写作 Zone Selective Interlocking (ZSI) |
| **TRM-DON-009** | 正泰昆仑 / 昆仑系列 | ❌ `CHINT Kunlun / Kunlun series ❌` | ✅ **CHINT NXA Series ACB / NXA Series** | 万能式断路器出海技术与选型资料中，昆仑系列统一采用国际标准系列命名 NXA Series ACB |
| **TRM-DON-010** | 抽屉式 (断路器/安装) | ❌ `Drawer / Drawer type ❌` | ✅ **Drawout / Drawout type / Withdrawable** | 抽屉式断路器严禁译为 Drawer，必须使用国际通用的 Drawout 或 Withdrawable |
| **TRM-DON-011** | 电动操作机构 (电操) | ❌ `Operating device / Motor hand ❌` | ✅ **Motor Operator Device (MOD) / Motor Mechanism** | 电动操作机构标准缩写为 MOD，亦可用 Motor Operator / Motor Mechanism |
| **TRM-DON-012** | 灭弧室 | ❌ `Interrupter / Arc room ❌` | ✅ **Arc-extinguishing chamber / Arc chute** | 灭弧室标准电工术语为 Arc-extinguishing chamber 或 Arc chute，严禁使用 Interrupter |
| **TRM-DON-013** | 摇手柄存放孔 / 存放槽 | ❌ `Storage hole ❌` | ✅ **Racking handle storage slot / Storage slot** | 抽屉座或面板摇手柄收纳结构标准用词为 storage slot，严禁直译为 storage hole |
| **TRM-DON-014** | 智能控制器 / 控制器 | ❌ `Intelligent controller (literal) ❌` | ✅ **Controller / Electronic Trip Unit (ETU)** | 产品部件及选型标题中直接使用 Controller 或 Electronic Trip Unit，避免中式 redundant wording |
| **TRM-DON-015** | 按钮 (合闸/分闸按钮) | ❌ `Device button / Press key ❌` | ✅ **Pushbutton (Closing / Opening pushbutton)** | 电气开关面板按钮标准术语为 Pushbutton，严禁译为 device button 或 press key |
| **TRM-DON-016** | 分断能力型号 | ❌ `Breaking capacity levels ❌` | ✅ **Breaking capacity type (Type N / Type S / Type H)** | 分断能力等级型号应译为 breaking capacity type，而非 breaking capacity levels |
| **TRM-DON-017** | 指示灯 (如 Ig指示灯) | ❌ `Ig indicator light / lamp ❌` | ✅ **Ig indicator / Status indicator** | 面板指示灯标准术语使用 Indicator（如 Ig indicator），避免多余的 light 或 lamp |
| **TRM-DON-018** | 本体钥匙锁 | ❌ `Body key lock ❌` | ✅ **ACB Key Lock (KLC) / Key lock in open position** | 断路器本体锁具严禁字面直译为 Body key lock，必须译为 ACB Key Lock |
| **TRM-DON-019** | 壳架电流 (澄清) | ❌ `Frame size (when referring to Inm rating) ❌` | ✅ **Frame current / Frame rating (Inm)** | 澄清：Inm 为壳架等级额定电流 (Frame current)，Frame size 则用于指代物理外形框架尺寸 |

---

## 2. General Industrial Component & CAD Drawing False Friends

| Chinese Source | ❌ Forbidden Literal Translation | ✅ Mandatory Professional Term | Why & Standard Context |
| :--- | :--- | :--- | :--- |
| **基准 (CAD图纸)** | Base / Reference point *(or untranslated)* | **Datum** | Geometric dimensioning & tolerancing (GD&T) standard reference plane. |
| **安装面** | Install surface | **Mounting surface** | Switchboard rear/bottom structural mounting plane. |
| **柜门内侧** | Inside door / Door back | **Inner side of door / Door interior** | Enclosure door clearance dimensions. |
| **分离位置 / 隔离位置** | Separation place / Pull out | **Disconnected position / Isolated position** | Drawout cradle position terminology (Connected / Test / Disconnected). |
| **电工辅料 / 附件** | Auxiliary Materials | **Electrical Accessories / Installation Accessories** | "Auxiliary Materials" implies raw materials/steel, not electrical components. |
| **浮球液位开关** | Floating Ball Level Switch | **Float Level Switch / Cable Float Switch** | Industry standard terminology across ABB/Flygt/Schneider. |
| **重锤** | Heavy Hammer | **Counterweight / Balance Weight** | "Hammer" is a pounding tool; in float switches, it is a counterweight. |
| **约定自由空气发热电流** | Agreed-upon heating current in pure air | **Conventional free air thermal current Ith** | IEC 60947-1 Cl. 4.3.2.1 exact standard definition. |
| **额定冲击耐受电压** | Rated impact withstand voltage | **Rated impulse withstand voltage Uimp** | "Impact" is mechanical collision; "Impulse" is electrical surge/lightning. |
| **使用类别** | Use classes / Application class | **Utilization category** | IEC 60947-5-1 technical classification. |
| **寿命：50 万次** | 50 Ten thousand times | **500,000 operations / 500,000 cycles** | Never translate "万" literally into "Ten thousand". Use standard numbers. |
| **安装调试** | Installation and Debugging | **Installation and Commissioning** | "Debugging" is software troubleshooting; electromechanical apparatus uses "Commissioning". |
| **注意事项** | Matters need attention | **Operating Precautions / Safety Notes** | "Matters need attention" is poor literal translation. |
| **订货须知** | Ordering instruction | **Ordering Information** | Global standard catalog section heading. |
| **未注公差** | No tolerance specified | **Unspecified linear tolerance / General tolerance** | "No tolerance specified" implies zero control; "Unspecified" means general standard tolerance. |
| **误动作** | Wrong action / Bad work | **False tripping / Nuisance tripping / Malfunction** | Electrical switching & relay terminology. |
| **吸入** | Sucked in | **Drawn in / Entrapped by suction vortex** | Fluid mechanics and pump safety. |

---

## 3. Sentence-Level Anti-Chinglish & Native Engineering Rewriting Patterns

| Issue Type | ❌ Word-for-Word Chinese Literal Phrasing | ✅ Native International Engineering Rewriting | Key Improvement Principle |
| :--- | :--- | :--- | :--- |
| **Measurement Accuracy Boundary** | *Below 0.1In, the measurement is inaccurate.* | **Measurement unspecified below 0.1 In** *(or Accuracy unspecified below 0.1 In)* | Converts conversational critique into formal technical data sheet boundary specification. |
| **Accessory Function & Operating Logic** | *The time-delay undervoltage release is used when the line experiences short-time low voltage or loss of power, and can delay opening the circuit breaker.* | **The time-delay undervoltage release delays circuit-breaker tripping for short-term line low-voltage conditions or power loss.** | Replaces rambling sequential Chinese clauses ("is used when... and can...") with a concise, direct active predicate. |
| **Protective Indication** | *When earth current is too big, Ig lamp light up to warn user.* | **The Ig indicator illuminates upon detecting a residual earth fault.** | Replaces "light up / lamp" with standard electrotechnical terminology and active structure. |

---

## 4. Typography, Spacing & Unit Formatting Guardrails

1. **Mandatory Half-Width Space Before Units**:
   - Always insert a single space between numeric values and physical/electrical units:
     - ✅ `1600 A`, `400 V`, `50 Hz`, `6300 A`, `2.5 kV`, `15 kA`, `0.5 N·m`
     - ❌ `1600A`, `400V`, `50Hz`, `6300A`, `0.5N.m`
2. **Standard Temperature Notation**:
   - Always use a half-width space followed by the degree symbol and capital C:
     - ✅ `-35 °C`, `-5 °C to +40 °C`, `-45 °C ~ +70 °C`
     - ❌ `-35℃`, `-35C`, `-35 deg C`, `40 ℃` (full-width)
