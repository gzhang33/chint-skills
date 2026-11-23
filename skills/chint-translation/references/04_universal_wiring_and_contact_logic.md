# Universal Wiring & Contact Logic Reference (Global Standard)

## 0. Value Slot Convention

Terminal designations and voltages below are slots: `{{param_name}}` / `{{param_name: unit}}`.
Terminal designations are **platform-specific** and must be taken verbatim from the target device's wiring diagram — never inherited from another manufacturer's drawing.

---

## 1. Dual-Function Changeover / SPDT Level & Process Control Logic

```
                  ┌─── Blue Wire  (NC - Normally Closed Contact) ───> Filling / Water Supply Mode
Black Wire (COM) ─┤
                  └─── Brown Wire (NO - Normally Open Contact)   ───> Drainage / Sump Emptying Mode
```

- **Tank Filling Mode (Auto-Fill):** Connect Black (COM) and Blue (NC) in series with the control circuit.
  - Low Liquid Level (Float Down) $\rightarrow$ Contact **closes (ON)** to start the pump.
  - High Liquid Level (Float Up) $\rightarrow$ Contact **opens (OFF)** to stop the pump.
- **Sump Drainage Mode (Auto-Drain):** Connect Black (COM) and Brown (NO) in series with the control circuit.
  - Low Liquid Level (Float Down) $\rightarrow$ Contact **opens (OFF)** to stop the pump.
  - High Liquid Level (Float Up) $\rightarrow$ Contact **closes (ON)** to start the pump.

---

## 2. Secondary Control Circuit Wiring (二次控制回路接线)

| Function | Standard Global English Term | Terminal Marking Slot | Standard Operation |
| :--- | :--- | :--- | :--- |
| 分励 / 合闸 / 欠压线圈 | **Control supply voltage terminals** | `{{coil_terminals}}` | Coil energization voltage `{{coil_voltage: V AC/DC}}`; state AC or DC explicitly and keep the datasheet's voltage set, not a guessed one. |
| 准备合闸触点 | **Ready-to-close contact (RTC / PF)** | `{{rtc_terminals}}` | Closes when circuit-breaker is open, springs charged, and no trip lock-out present. |
| 辅助状态触点 (转换型) | **Auxiliary contacts (OF / AX)** | `{{aux_terminals}}` | Form C changeover contacts indicating circuit-breaker Open/Closed status. |
| 故障跳闸报警触点 | **Fault-trip indication contact (SDE / AL)** | `{{alarm_terminals}}` | Changes state only when the circuit-breaker trips automatically via the trip unit. |
| 储能电机供电端子 | **Spring charging motor supply (M / MCH)** | `{{motor_terminals}}` | Automatic spring charging on control voltage application; charging time `{{charging_time: s}}`. |

---

## 3. Main Power Terminal Connection Forms (主回路端子接线形式)

| Terminal Type | Chinese Term | Standard Global English Term | Engineering Feature |
| :--- | :--- | :--- | :--- |
| **F** | 板前接线 | **Front connection (FC)** | Front busbar / cable lug termination with phase barriers. |
| **HR** | 板后水平接线 | **Rear horizontal connection (HR)** | Flat horizontal busbar studs for rear switchboard connection. |
| **VR** | 板后垂直接线 | **Rear vertical connection (VR)** | Flat vertical busbar studs for high-current parallel busbars. |
| **Rotatable** | 旋转端子 | **Rotatable terminal pads** | Modular terminal pads adaptable on-site between horizontal and vertical. Rotation angle `{{terminal_rotation_deg: °}}`; quote it only when the target model actually documents it. |
| **Spreaders** | 加长接线排 / 扩散端子 | **Extended terminal spreaders** | Widens pole-to-pole pitch for heavy cable terminations. |

---

## 4. Wiring-Description Guardrails

- Never describe a terminal by its function alone when the wiring diagram labels it. The label wins.
- When a terminal designation cannot be confirmed from the target device's drawing, write the function and omit the number; do not borrow a designation from a competitor drawing.
- Opposite-polarity or coil-type terminals must always carry AC/DC in the sentence.
