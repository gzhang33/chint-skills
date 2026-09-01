# ACB Electronic Trip Units & Protection Taxonomy (Global Standard)

Aligned with ABB (Ekip / PR series), Schneider (Micrologic series), and LS (OCR / Trip Relay).

## 1. Trip Unit Types & Intelligence Levels

| Series / Type | Chinese Term | Standard Global English Term | Standard Features |
| :--- | :--- | :--- | :--- |
| **Basic Distribution Type (M Type)** | 基本型 / 配电型脱扣器 | **Basic Distribution Trip Unit (Standard Protection)** | Dual rotary switch / LED dial setting for standard L/S/I/G protection. |
| **Ammeter / Measurement Type (A Type)** | 电流测量型 / 仪表型脱扣器 | **Ammeter Trip Unit (Current Measurement)** | LCD digital display, real-time current metering ($I_a, I_b, I_c, I_n$), fault history log. |
| **Power / Energy Type (P Type)** | 功率型 / 电能监控型脱扣器 | **Power & Energy Trip Unit (Power Monitoring)** | Voltage, active/reactive power ($P, Q, S$), power factor ($\cos\phi$), energy consumption ($E$). |
| **Harmonic & Power Quality Type (H Type)**| 谐波型 / 高级电能质量型脱扣器| **Harmonic Analysis & Power Quality Trip Unit** | Advanced FFT harmonic analysis (THD, $2\text{nd} \sim 31\text{st}$ harmonics), waveform capture, load shedding. |

---

## 2. Protection Functions & Setting Parameters (四段保护与整定)

| Protection Symbol | Protection Function | Standard Global English Notation | Adjustable Parameter Range |
| :--- | :--- | :--- | :--- |
| **L** | 过载长延时保护 | **Long-time protection against overloads (L)** | Current pickup: $I_r = (0.4 \sim 1.0) \times I_n$; Time delay: $t_r = (15 \sim 480)\text{ s}$ |
| **S** | 短路短延时保护 | **Short-time protection against short circuits (S)** | Pickup: $I_{sd} = (1.5 \sim 10) \times I_r$; Time delay: $t_{sd} = (0.1 \sim 0.4)\text{ s}$ ($I^2t \text{ ON/OFF}$) |
| **I** | 短路瞬时保护 | **Instantaneous protection against short circuits (I)** | Pickup: $I_i = (1.5 \sim 15) \times I_n + \text{OFF}$ (Tripping time $< 30\text{ ms}$) |
| **G** | 接地故障保护 | **Ground-fault protection (G)** | Residual / Source ground return pickup: $I_g = (0.2 \sim 1.0) \times I_n$; Delay: $t_g = (0.1 \sim 0.4)\text{ s}$ |
| **N** | 中性极保护 | **Neutral pole protection (N)** | $I_{nN} = 50\%, 100\%, 200\% \times I_n$ or $\text{OFF}$ |
| **ZSI** | 区域选择性联锁 | **Zone Selective Interlocking (ZSI)** | Short-time & ground fault selectivity signal bus between upstream/downstream breakers. |
| **MCR** | 瞬时合闸涌流保护 | **Making Current Release (MCR)** | Instantaneous override protection active only during circuit breaker closing transient. |
| **Thermal Memory**| 热记忆功能 | **Thermal memory (Thermal image)** | Retains bimetallic heating profile to prevent repetitive overload cumulative damage. |
