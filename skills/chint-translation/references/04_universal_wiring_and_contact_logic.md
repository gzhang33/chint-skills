# Universal Wiring & Contact Logic Reference (Global Standard)

## 1. Dual-Function Changeover / SPDT Level & Process Control Logic

```
                  ┌─── Blue Wire  (NC - Normally Closed Contact) ───> Filling / Water Supply Mode
Black Wire (COM) ─┤
                  └─── Brown Wire (NO - Normally Open Contact)   ───> Drainage / Sump Emptying Mode
```

- **Tank Filling Mode (Auto-Fill):** Connect Black (COM) and Blue (NC) in series with control circuit.
  - Low Liquid Level (Float Down) $\rightarrow$ Contact **closes (ON)** to start pump.
  - High Liquid Level (Float Up) $\rightarrow$ Contact **opens (OFF)** to stop pump.
- **Sump Drainage Mode (Auto-Drain):** Connect Black (COM) and Brown (NO) in series with control circuit.
  - Low Liquid Level (Float Down) $\rightarrow$ Contact **opens (OFF)** to stop pump.
  - High Liquid Level (Float Up) $\rightarrow$ Contact **closes (ON)** to start pump.

---

## 2. Secondary Control Circuit Wiring (二次控制回路接线)

| Terminal Marking | Function | Standard Global English Term | Standard Operation |
| :--- | :--- | :--- | :--- |
| **A1 - A2** | 分励 / 合闸 / 欠压线圈 | **Control supply voltage terminals** | Coil energization ($24\text{ V DC}, 110\text{ V AC}, 230\text{ V AC}, 400\text{ V AC}$). |
| **RTC / 11-14** | 准备合闸触点 | **Ready-to-close contact (RTC / PF)** | Closes when breaker is open, springs charged, and no trip lockout present. |
| **OF / 11-12-14** | 辅助状态触点 (转换型) | **Auxiliary contacts (OF / AX)** | Form C changeover contacts indicating breaker Open/Closed status. |
| **SDE / 181-182-184** | 故障跳闸报警触点 | **Fault-trip indication contact (SDE / AL)** | Changes state only when breaker trips automatically via trip unit. |
| **M1 - M2** | 储能电机供电端子 | **Spring charging motor supply (M / MCH)** | Automatic spring charging upon control voltage application ($<5\text{ s}$). |

---

## 3. Main Power Terminal Connection Forms (主回路端子接线形式)

| Terminal Type | Chinese Term | Standard Global English Term | Engineering Feature |
| :--- | :--- | :--- | :--- |
| **F** | 板前接线 | **Front connection (FC)** | Front busbar / cable lug termination with phase barriers. |
| **HR** | 板后水平接线 | **Rear horizontal connection (HR)** | Flat horizontal busbar studs for rear switchboard connection. |
| **VR** | 板后垂直接线 | **Rear vertical connection (VR)** | Flat vertical busbar studs for high-current parallel busbars. |
| **Rotatable 90°** | 90°旋转端子 | **90° rotatable terminal pads** | Modular terminal pads adaptable on-site between horizontal and vertical. |
| **Spreaders** | 加长接线排 / 扩散端子 | **Extended terminal spreaders** | Widens pole-to-pole pitch for heavy cable terminations. |
