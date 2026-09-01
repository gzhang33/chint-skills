# Industrial Safety & Application Imperative Guidelines

## 1. Structure of Native Industrial Safety Instructions

In European and North American industrial equipment manuals, precautions are written as **verb-led imperative instructions** or **prefixed engineering parameters**, avoiding conversational "When the user wants to..." structures.

### Standard Transformation Patterns:

| Context | ❌ Awkward Literal Phrasing | ✅ Native Engineering Imperative |
| :--- | :--- | :--- |
| **小功率电机直连** | When the product is directly connected to a small motor, the starting current must not be bigger... | **Direct motor control:** Ensure motor inrush/starting current does not exceed the switch rated operational current. |
| **大功率/频繁启停** | If you have big power motor or need frequent start, should use contactor together. | **Heavy-duty / high-frequency loads:** Always pair the switch with an external AC magnetic contactor. |
| **防出水口吸入** | Installation place should keep safe distance with water exit to avoid float sucked in. | **Discharge clearance:** Maintain sufficient clearance from pump discharge outlets to prevent float entrapment by suction vortices. |
| **防进水口冲击误动作** | Installation place must keep suitable distance with water entrance to avoid wrong action by shock. | **Inlet clearance:** Position the device away from incoming fluid streams to eliminate false tripping caused by turbulence or direct impact. |
| **重锤安装防撞** | When installing heavy hammer, because should avoid collision. | **Counterweight handling:** Avoid severe mechanical impacts or drop damage during counterweight adjustment. |
| **电缆中间接头禁水** | If must have middle joint, absolutely cannot immerse in water pool. | **Cable splicing:** Route cables directly without intermediate splices. If a splice is unavoidable, ensure it is fully sealed and never submerged in liquid. |
| **螺钉紧固力矩** | Tighten screw with screwdriver without broken wire skin, torque not over 0.5N.m. | **Fastener torque:** Tighten the securing screw using a screwdriver without pinching the outer cable sheath; maximum tightening torque: $0.5\text{ N}\cdot\text{m}$. |

---

## 2. Core Industrial Vocabulary for Precautions

- **Inrush current / Locked-rotor current**: 启动电流 / 堵转电流
- **Suction vortex / Entrapment**: 旋流吸入 / 卡滞
- **False tripping / Nuisance tripping**: 误动作 / 误跳闸
- **Fluid turbulence / Hydraulic shock**: 液体扰动 / 水锤冲击
- **Submerged / Immersion**: 浸入水中 / 浸没
- **Cable jacket / Outer sheath**: 电缆外皮 / 护套
