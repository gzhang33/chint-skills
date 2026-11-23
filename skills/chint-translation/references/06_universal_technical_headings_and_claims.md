# Standard Technical Document Headings & Marketing Claims Reference

## 0. Value Slot Convention

This file is a **sentence-template library**. It deliberately contains no claim numbers, percentages, angles or lifetimes.
Each claim is written as a frame with slots: `{{param_name: unit}}`. A claim frame may only be turned into public copy after every slot is resolved from an approved product datasheet.

Two hard rules for claim frames:

1. **No unverified superlative.** A superlative frame (`full series`, `ultra-wide`, `zero`, `maximum`) carries an explicit scope slot `{{claim_scope}}` that must name the exact models or controller types it covers.
2. **A claim frame is not evidence.** If a claim frame cannot be backed by a datasheet line, delete the frame rather than shipping it with a soft caveat.

---

## 1. Standard Technical Document Section Headings

| Section ID | Chinese Heading | Standard IEC / International English | Category Scope | Usage Context |
| :--- | :--- | :--- | :--- | :--- |
| **SEC-001** | 产品概述 / 简介 | **Product Overview / Introduction** | All Product Families | Executive technical summary and operating principles. |
| **SEC-002** | 结构特点与性能优势 | **Features and Characteristics / Performance Advantages** | All Product Families | Core engineering highlights and technological advantages. |
| **SEC-003** | 技术参数表 / 规格表 | **Technical Parameters / Specifications** | All Product Families | Electrical ratings, breaking capacities, and operational performance (operating cycles / endurance). |
| **SEC-004** | 型号含义与选型规则 | **Model Selection Guide / Type Designation Rules** | All Product Families | Model code breakdown and order configuration logic. |
| **SEC-005** | 接线原理图与二次回路 | **Wiring Diagrams / Electrical Schematics** | All Product Families | Power and secondary control circuit schematics. |
| **SEC-006** | 外形及安装尺寸 | **Overall and Mounting Dimensions** | All Product Families | Engineering CAD dimensions and mounting cutouts. |
| **SEC-007** | 安装、调试与注意事项 | **Installation, Commissioning and Precautions** | All Product Families | Mechanical installation, electrical wiring, and safety notes. |
| **SEC-008** | 订货信息 / 订货须知 | **Ordering Information** | All Product Families | Ordering codes, quantities, and selection examples. |

---

## 2. Standard Performance Marketing Claim Frames

| Code | Chinese Claim Pattern | Standard Idiomatic English Frame | Product Scope | Slot(s) to Resolve | Use Only When |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **CLM-001** | 分断能力达到 `{{Ics_ratio: % of Icu}}` | **Service breaking capacity reaches `{{Ics_ratio: % of Icu}}` of `Icu` across `{{claim_scope}}`.** | ACB / MCCB Series | `Ics_ratio`, `claim_scope` | The datasheet gives the ratio for **every** model named in `claim_scope`. Otherwise re-scope the claim to the models that do. Never generalize from one frame. |
| **CLM-002** | 支持水平、垂直与旋转 `{{terminal_rotation_deg: °}}` 接线 | **Supports horizontal, vertical and `{{terminal_rotation_deg: °}}` rotatable busbar connections.** | ACB / MCCB Series | `terminal_rotation_deg`, `claim_scope` | The rotatable-terminal feature is documented for the named models. Features that exist only on another series must not be described as a family feature. |
| **CLM-003** | 标配微处理器智能脱扣器 | **Equipped with a microprocessor-based electronic trip unit (ETU), providing comprehensive protection.** | ACB / MCCB Series | none | The basic configuration actually ships with an electronic trip unit; avoid literal `intelligent trip unit` per `TRM-DON-014`. |
| **CLM-004** | 宽运行环境温度范围 `{{T_ambient_min: °C}}` 至 `{{T_ambient_max: °C}}` | **Operating temperature range of `{{T_ambient_min: °C}}` to `{{T_ambient_max: °C}}` for `{{claim_scope}}`.** | Low-Voltage Distribution | `T_ambient_min`, `T_ambient_max`, `claim_scope` | The range is quoted together with the controller type it applies to. Do not present a controller-specific range as a circuit-breaker-wide range, and avoid the word "ultra-wide" unless a defined baseline is cited. |
| **CLM-005** | 飞弧距离 `{{arcing_distance: mm}}` | **`{{arcing_distance: mm}}` arcing distance design reduces the switchboard clear space.** | Air Circuit-Breakers | `arcing_distance` | The datasheet states the value, and the sentence keeps the physical meaning (clear space above the arc chutes) rather than the marketing gloss. |
| **CLM-006** | 延时欠电压脱扣保护 | **The time-delay undervoltage release delays circuit-breaker tripping for short-term line low-voltage conditions or power loss.** | ACB / MCCB Series | none | The device actually offers a time-delay variant. |
| **CLM-007** | 小电流测量下限 | **Measurement unspecified below `{{metering_threshold: A}}`.** | Electronic Trip Units | `metering_threshold` | The metering table states the lower boundary. |

---

## 3. Standard Technical Parameter Table Column Headers (参数表头标准表述)

| Standard Table Parameter | Chinese Column Header | Standard Catalogue / Benchmark English Header | Notes |
| :--- | :--- | :--- | :--- |
| **Ultimate Breaking Capacity** | 额定极限短路分断能力 | **Ultimate breaking capacity Vac 50/60 Hz** *(or Rated ultimate short-circuit breaking capacity Icu)* | Standard column header across the major international catalogues. |
| **Service Breaking Capacity** | 额定运行短路分断能力 | **Service breaking capacity Vac 50/60 Hz** *(or Rated service short-circuit breaking capacity Ics)* | Standard column header for service breaking capability. |
| **Frame Size / Frame Current** | 壳架电流 / 壳架等级 | **Frame size (A) / Frame current Inm (A)** | IEC 60947-2:2024 Cl. 3.1.1 defines **frame size** as expressed in amperes corresponding to the highest current rating of the group; `Inm` is a **GB/T 14048.2** domestic symbol (not in IEC 60947-2). |
| **Breaking Capacity Type** | 分断能力型号 | **Breaking capacity type** *(e.g. Type N, Type S, Type H)* | Never translate as "breaking capacity levels". |
| **Rated Short-time Current** | 额定短时耐受电流 | **Rated short-time withstand current Icw (kA rms, duration as stated)** | Category B selectivity baseline parameter. The duration belongs in the header, never silently assumed. |

---

## 4. Claim Audit Checklist

Before a claim frame leaves the dictionary, confirm all of the following:

- `{{claim_scope}}` names models, not a whole family by default.
- Every numeric slot traces to one datasheet line, quoted by table or section.
- The superlative word still holds after re-scoping; if it does not, drop the superlative.
- The English frame does not add a benefit the Chinese source did not claim.
