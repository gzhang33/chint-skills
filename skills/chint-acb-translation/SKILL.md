---
name: chint-acb-translation
description: Use when translating CHINT Air Circuit Breaker (ACB) product presentations, catalogs, brochures, datasheets, or technical specifications, including NXA, NA8, NA1, and Noark UL series. Triggers on ACB, Air Circuit Breaker, 万能式断路器, 框架断路器, NXA, NA8, Noark UL, IEC 60947-2, UL 1066, or low-voltage power circuit breaker translation.
---

# CHINT ACB Overseas Catalog & Technical Translation Skill (`chint-acb-translation`)

## Overview

This skill establishes an authoritative, zero-hallucination translation SOP and RAG reference system for **CHINT Air Circuit Breakers (ACB / 万能式断路器)**, covering **NXA (1000A~6300A), NA8 (1600A~7500A), NA1, and Noark UL (A25/A32/A40)** series.

It enforces strict compliance with **IEC 60947-2 / GB/T 14048.2** as the global backbone while mapping **UL 489 / UL 1066** North American standards, ensuring 100% precision in electrical parameters, trip unit algorithms, accessories, installation dimensions, and catalog templates.

---

## Standard Reference Hierarchy

1. **IEC & GB Primary Backbone**:
   - `IEC 60947-2:2024` / `GB/T 14048.2-2020` (Circuit-breakers)
   - `IEC 60947-1` / `GB/T 14048.1` (General rules)
2. **North American UL/ANSI Mapping**:
   - `UL 1066` / `ANSI C37.50` / `IEEE C37.13` (Low-Voltage AC and DC Power Circuit Breakers)
   - `UL 489` / `CSA C22.2 No. 5` (Molded-Case & Insulated-Case Circuit Breakers)

---

## Context Pointers & Knowledge Base Modules (`references/`)

For granular terminology lookups, the agent MUST read the corresponding Markdown file in `references/`:

- [01_产品名称与系列](references/01_产品名称与系列.md): Product names, series codes, pole configurations, operating mechanisms.
- [02_电气性能与参数](references/02_电气性能与参数.md): $U_e, U_i, U_{imp}, I_n, I_{nm}, I_{cu}, I_{cs}, I_{cw}, I_{cm}$, Category B, endurance, power loss.
- [03_脱扣器与智能控制器](references/03_脱扣器与智能控制器.md): M/A/P/H trip units, 2.0N/3.0N/4.0N, L/S/I/G/N protection, ZSI, MCR, harmonics.
- [04_内部与外部附件机构](references/04_内部与外部附件机构.md): SHT, UVR, CC/CEM, M/MOE, AX, AL, RTC, key locks, padlocks, mechanical interlocks.
- [05_安装接线与结构尺寸](references/05_安装接线与结构尺寸.md): Fixed, Drawout, Cradle/Chassis, Horizontal/Vertical/Front wiring, IP rating, door flange.
- [06_环境条件与标准认证](references/06_环境条件与标准认证.md): Temp (-45℃~+70℃), altitude derating, tropicalization, EMC, CB/CE/UL/Marine certs.
- [07_样本高频句式与栏目](references/07_样本高频句式与栏目.md): Standard catalog section titles, parameter table headings, marketing sentences.
- [08_翻译禁忌与防呆词库](references/08_翻译禁忌与防呆词库.md): False friends, strictly prohibited terms, and forbidden literal translations.

---

## High-Frequency Forbidden Terms (Do's & Don'ts)

| Chinese Term | Strictly FORBIDDEN Translation | Mandatory English Term | Rationale & Standard |
|:---|:---|:---|:---|
| **万能式断路器** | ❌ Universal Circuit Breaker | ✅ **Air Circuit Breaker (ACB)** / LVPCB | IEC 60947-2 Cl. 2.1 |
| **闭合电磁铁** | ❌ Closed electromagnet | ✅ **Closing Release (CC / CEM)** / Closing Coil | IEC 60947-2 (Action, not state) |
| **分励脱扣器** | ❌ Excitation release | ✅ **Shunt Release (SHT)** / Shunt Trip (ST) | IEC 60947-2 Cl. 7.2.1.2 |
| **欠电压脱扣器** | ❌ Less voltage trip | ✅ **Undervoltage Release (UVR)** | IEC 60947-2 Cl. 7.2.1.3 |
| **抽屉座** | ❌ Drawer box / Slide box | ✅ **Cradle** / Drawout Chassis | IEC 60947-2 Cl. 2.2.2 |
| **相间隔板** | ❌ Phase space plate | ✅ **Interphase Barrier** / Phase Barrier | IEC 60947-2 |
| **门框 / 面罩** | ❌ Face mask / Door frame | ✅ **Door Flange** / Escutcheon | Cabinet panel cutout seal |
| **区域选择性联锁** | ❌ Area choice lock | ✅ **Zone Selective Interlocking (ZSI)** | IEC 60947-2 Annex F |

---

## Translation Workflow SOP

1. **Identify Target Market & Standard Context**:
   - Global / European / Asian / Middle Eastern / Latin American -> Default to **IEC 60947-2** terms (ACB, Shunt Release, Drawout).
   - North America (USA / Canada / Mexico) -> Use **UL 1066 / UL 489** terms (LVPCB, Shunt Trip, Drawout Power Breaker).
2. **Scan Reference Table**:
   - Check `references/` files for exact matching term IDs and CHINT model codes (e.g. SHT-A1, VBP, CD).
3. **Apply Do's & Don'ts Guardrails**:
   - Filter against `08_翻译禁忌与防呆词库.md`. Never use literal machine-translated terms.
4. **Formatting & Punctuation**:
   - Use standard IEC mathematical symbols ($I_{cu}, I_{cs}, I_{cw}, U_e, U_i, U_{imp}, I_n$). Keep proper spacing around numbers and units (e.g., `415 V`, `6300 A`, `50 kA`).
