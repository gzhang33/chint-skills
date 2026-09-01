---
name: chint-translation
description: Universal, zero-hallucination B2B industrial translation, localization, and technical auditing standard for all CHINT low-voltage power distribution and industrial control apparatus. Covers "三断一接" (ACB, MCCB, MCB, Contactors), Automatic Transfer Switches (ATS), Power Quality (SVG/APF), solid-state breakers, sensors, relays, electrical accessories, catalogs, brochures, datasheets, and technical specifications. Enforces IEC 60947, IEC 60898, IEC 61000, and UL 489/1066/1008 electrotechnical standards.
---

# Universal CHINT Low-Voltage & Industrial Translation Skill (`chint-translation`)

## Overview

`chint-translation` is the authoritative, multi-category translation and technical governance skill for **all CHINT overseas deliverables**, covering the complete low-voltage power distribution, circuit protection, and industrial control portfolios:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        CHINT Universal Translation Portfolio                           │
├────────────────────────────────┬───────────────────────────────────────────────────────┤
│ 1. 三断 (Three Breakers)       │ ACB (万能式/框架), MCCB (塑壳), MCB/RCBO (微断/漏电)  │
│ 2. 一接 (Contactors & Starters)│ AC Contactors (交流接触器), Motor Starters, Overload  │
│ 3. 关键配电切换与电能质量      │ ATS (双电源转换开关), Power Quality (SVG, APF, PFC)   │
│ 4. 工控、传感器与电工辅料      │ Float switches, sensors, relays, terminal accessories  │
│ 5. 出海物料类型                │ Catalogs, Brochures, Datasheets, Specs, Whitepapers   │
└────────────────────────────────┴───────────────────────────────────────────────────────┘
```

It guarantees **zero literal machine translation**, eliminates product-specific bias, dynamically routes domain terminology based on product category, strictly aligns with **IEC / UL / ANSI** standards, and outputs publication-ready, designer-friendly copy.

---

## Standard Reference Hierarchy

1. **IEC Electrotechnical Standards (Global Baseline)**:
   - `IEC 60947-1`: Low-voltage switchgear and controlgear - General rules.
   - `IEC 60947-2:2024`: Low-voltage circuit-breakers (ACB, MCCB, heavy industrial MCB).
   - `IEC 60898-1`: Circuit-breakers for overcurrent protection for household installations (MCB).
   - `IEC 60947-4-1`: Electromechanical contactors and motor-starters.
   - `IEC 60947-6-1`: Automatic transfer switching equipment (ATS / TSE).
   - `IEC 61008-1` / `IEC 61009-1`: Residual current operated circuit-breakers (RCCB, RCBO).
   - `IEC 61000-3-2` / `IEC 62477-1` / `IEEE 519`: Power quality, harmonic limits, SVG/APF.
   - `IEC 60529`: Degrees of protection provided by enclosures (IP Code).
2. **North American Standards (UL / ANSI / IEEE Mapping)**:
   - `UL 1066` / `ANSI C37.50`: Low-Voltage AC and DC Power Circuit Breakers (ACB / LVPCB).
   - `UL 489` / `CSA C22.2 No. 5`: Molded-Case Circuit Breakers & Enclosures (MCCB & MCB).
   - `UL 1077`: Supplementary Protectors for Use in Electrical Equipment.
   - `UL 1008`: Transfer Switch Equipment (ATS).
   - `UL 60947-4-1`: Industrial Control Equipment (Contactors & Starters).

---

## 4-Step Universal Translation SOP

```
Step 1: Layout Extraction ──> Step 2: Product Category Routing ──> Step 3: IEC/UL Normalization ──> Step 4: Designer-Ready Formatting
```

### Step 1: Structural Extraction & Layout Partitioning
- Deconstruct the Chinese document page by page into standard layout blocks:
  - Header / Footer / Slogan (`CHINT - Smart Energy Solutions Provider`)
  - Category Badge & Product Main Title
  - Section 1: Product Overview & Value Proposition
  - Section 2: Type Designation (Model code breakdown & decoding rules)
  - Section 3: Operating & Environmental Conditions (Ambient temp, altitude derating, tropicalization, pollution degree)
  - Section 4: Technical Specifications & Parameter Tables
  - Section 5: Overall Dimensions & CAD Drawing Callouts (Tolerances, units, diameters)
  - Section 6: Installation, Commissioning & Wiring Instructions
  - Section 7: Ordering Information

### Step 2: Product Category Routing & Module Loading (产品类型判断树)
Identify the primary product category from the title and context, then load the dedicated technical reference module:

| Product Category | Series Codes | Applicable Standards | Mandatory Reference Module |
| :--- | :--- | :--- | :--- |
| **ACB (Air Circuit Breakers / 框架断路器)** | NXA, NA8, NA1, Noark A | IEC 60947-2, UL 1066 | [02_acb_trip_units](references/02_acb_trip_units_and_protection.md), [03_acb_accessories](references/03_acb_accessories_and_mechanisms.md) |
| **MCCB (Molded Case Breakers / 塑壳断路器)** | NXM, NXS, NXC, NM8 | IEC 60947-2, UL 489 | [08_mccb_taxonomy](references/08_mccb_taxonomy_and_releases.md) |
| **MCB & Modular (微型断路器与终端配电)** | NXB, NXBLE, NL1, DPN | IEC 60898-1, IEC 60947-2 | [09_mcb_rcbo_curves](references/09_mcb_rcbo_curves_and_accessories.md) |
| **ATS (Automatic Transfer Switches / 双电源)** | NZ7, NZ6, NH40SZ | IEC 60947-6-1, UL 1008 | [10_ats_classes](references/10_ats_classes_and_controllers.md) |
| **Contactors & Power Quality (接触器与电能质量)** | NXC, NXR, NDG, SV | IEC 60947-4-1, IEC 61000 | [11_power_quality_and_contactors](references/11_power_quality_and_contactors.md) |
| **Electrical Accessories & Sensors (辅料与工控)** | FQK, Terminals, Connectors | IEC 60947-5-1, IEC 60529 | [04_universal_wiring](references/04_universal_wiring_and_contact_logic.md), [05_universal_safety](references/05_universal_safety_imperatives.md) |

### Step 3: IEC/UL Parameter Normalization & Engineering Localization
1. **Universal Parameter Symbols**:
   - $U_i$ -> `Rated insulation voltage`
   - $U_{imp}$ -> `Rated impulse withstand voltage` (Never "impact")
   - $I_{th}$ -> `Conventional free air thermal current` (Never "pure air" / "agreed-upon")
   - $U_e$ / $I_e$ -> `Rated operational voltage` / `Rated operational current`
   - $I_{cu}$ / $I_{cs}$ / $I_{cw}$ / $I_{cm}$ -> `Rated ultimate / service / short-time withstand / making capacity`
   - 使用类别 -> `Utilization category` (e.g. AC-15, DC-13, AC-3, Cat B)
   - 机械/电寿命 -> `Mechanical / Electrical endurance: 500,000 operations` (Convert "万次" into exact operations)
2. **Native Engineering Rewriting**:
   - **Overview**: Rewrite passive/literal sentences into active, value-driven technical descriptions (`The [Model] is designed for automatic [Function] in [Applications] using [Operating Principle]...`).
   - **Wiring & Contacts**: Symmetrical SPDT/DPDT logic (Auto-Fill vs Auto-Drain, COM / NC / NO).
   - **Safety Instructions**: Transform into verb-led imperative directives (`Direct motor control:`, `Discharge clearance:`, `Inlet clearance:`).

### Step 4: Designer-Ready Deliverable Formatting
- Produce clean, structured Markdown organized strictly by `[PAGE X]` and layout section blocks.
- Strip all Chinese full-width punctuation (`；`, `（ ）`, `：`) and replace with clean English half-width symbols.
- Unify global corporate branding: **`CHINT`** (all caps), Slogan: **`CHINT - Smart Energy Solutions Provider`**.

---

## Universal Anti-Chinglish Guardrails (High-Frequency Master List)

| Chinese Source | ❌ Forbidden Literal Translation | ✅ Mandatory Professional English | Category Scope |
| :--- | :--- | :--- | :--- |
| **万能式断路器** | Universal Circuit Breaker | **Air Circuit Breaker (ACB)** / LVPCB | ACB (IEC 60947-2) |
| **塑壳断路器** | Plastic shell breaker | **Molded Case Circuit Breaker (MCCB)** | MCCB (IEC 60947-2 / UL 489) |
| **微型断路器** | Mini circuit breaker / Small breaker | **Miniature Circuit Breaker (MCB)** | MCB (IEC 60898-1 / UL 489) |
| **漏电断路器** | Leakage breaker | **Residual Current Circuit Breaker (RCBO / RCCB)** | Modular Devices |
| **双电源自动转换开关** | Dual power auto switch | **Automatic Transfer Switch (ATS / TSE)** | ATS (IEC 60947-6-1) |
| **交流接触器** | AC connector / AC switcher | **AC Contactor** | Controlgear (IEC 60947-4-1) |
| **闭合电磁铁** | Closed electromagnet | **Closing Release (CC / CEM)** / Closing Coil | ACB / Switchgear |
| **分励脱扣器** | Excitation release / Shunting release | **Shunt Release (SHT / MX)** / Shunt Trip (ST) | ACB / MCCB |
| **欠电压脱扣器** | Less voltage trip / Lack voltage | **Undervoltage Release (UVR / MN)** | ACB / MCCB |
| **抽屉座** | Drawer box / Slide box | **Cradle** / Drawout Chassis / Sub-base | ACB / MCCB |
| **相间隔板** | Phase space plate | **Interphase Barrier / Phase Barrier** | ACB / MCCB / MCB |
| **门框 / 柜门面罩** | Face mask / Door frame | **Door Flange / Escutcheon** | Switchboard Panel |
| **区域选择性联锁** | Area choice lock | **Zone Selective Interlocking (ZSI)** | Electronic Trip Units |
| **电工辅料 / 附件** | Auxiliary Materials | **Electrical Accessories / Installation Accessories** | General Low-Voltage |
| **重锤 / 配重块** | Heavy Hammer / Heavy weight | **Counterweight / Balance Weight** | Sensors / Level Control |
| **约定自由空气发热电流** | Agreed-upon heating current in pure air | **Conventional free air thermal current Ith** | IEC 60947-1 |
| **额定冲击耐受电压** | Rated impact withstand voltage | **Rated impulse withstand voltage Uimp** | IEC 60947-1 |
| **50 万次** | 50 Ten thousand times | **500,000 operations / 500,000 cycles** | Endurance Rating |
| **安装调试** | Installation and Debugging | **Installation and Commissioning** | Equipment Deployment |
| **注意事项** | Matters need attention | **Operating Precautions / Safety Notes** | Catalog Standard Section |
| **订货须知** | Ordering instruction | **Ordering Information** | Catalog Standard Section |
| **误动作** | Wrong action / Error work | **False tripping / Nuisance tripping / Malfunction** | Electrical Protection |

---

## Granular Knowledge Base & Context Pointers (`references/`)

For specialized domain glossaries and deep reference tables, consult:

### Universal Modules
- [01_universal_iec_parameters.md](references/01_universal_iec_parameters.md): Universal electrical ratings ($U_e, U_i, U_{imp}, I_n, I_{cu}, I_{cs}, I_{cw}, I_{cm}, I_{th}$) & environmental/marine certifications.
- [04_universal_wiring_and_contact_logic.md](references/04_universal_wiring_and_contact_logic.md): Changeover / SPDT auto-fill/auto-drain wiring, terminal pad connections, and 3-position racking states.
- [05_universal_safety_imperatives.md](references/05_universal_safety_imperatives.md): Native engineering precaution phrasing (inrush currents, suction vortices, fluid turbulence).
- [06_universal_catalog_headings.md](references/06_universal_catalog_headings.md): Standard catalog section headings and marketing performance claims (100% $I_{cs}$, 90° rotatable busbars).
- [07_universal_anti_chinglish.md](references/07_universal_anti_chinglish.md): Master anti-literal translation table across low-voltage domains.

### Per-Category Extension Modules
- [02_acb_trip_units_and_protection.md](references/02_acb_trip_units_and_protection.md): ACB Electronic Trip Units (M/A/P/H), L/S/I/G/N protection, ZSI, MCR, harmonics.
- [03_acb_accessories_and_mechanisms.md](references/03_acb_accessories_and_mechanisms.md): ACB internal/external accessories (SHT, UVR, CC, RTC, M/MOE, key locks, safety shutters).
- [08_mccb_taxonomy_and_releases.md](references/08_mccb_taxonomy_and_releases.md): MCCB Thermal-Magnetic (TM) & Electronic (ETU) trip units, rotary handles, motor operators, plug-in/drawout bases.
- [09_mcb_rcbo_curves_and_accessories.md](references/09_mcb_rcbo_curves_and_accessories.md): MCB Type B/C/D curves, 1P+N/2P/3P/4P, RCCB/RCBO (Type AC/A/B), DIN-rail mounting.
- [10_ats_classes_and_controllers.md](references/10_ats_classes_and_controllers.md): Automatic Transfer Switches (Class PC vs Class CB), transition types, transfer time, mechanical interlocks.
- [11_power_quality_and_contactors.md](references/11_power_quality_and_contactors.md): AC Contactors (AC-3/AC-4), thermal overload relays, Static Var Generators (SVG), Active Power Filters (APF), detuned reactors.
- [acb_terminology_master.json](references/acb_terminology_master.json): Machine-readable structured dictionary for automated ACB terminology pipelines.

---

## Completion Criteria

1. **[ ] Category Routing Confirmed**: Correct product classification identified and corresponding category reference module consulted.
2. **[ ] Zero Literal Machine Translation**: All terms checked against `07_universal_anti_chinglish.md` and category-specific anti-Chinglish rules.
3. **[ ] Exact Standards Compliance**: Electrical parameters, tripping curves, and ratings accurately mapped to respective IEC (60947-2, 60898-1, 60947-4-1, 60947-6-1) or UL (489, 1066, 1008) standards.
4. **[ ] Symmetrical Contact Logic**: All changeover / SPDT / secondary circuit wiring instructions clearly specify contact states and operational sequences.
5. **[ ] Designer-Ready Deliverable Structure**: Output partitioned by page with clear InDesign/Illustrator block markers, half-width punctuation, and unified CHINT brand tokens.
