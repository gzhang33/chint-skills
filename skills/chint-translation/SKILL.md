---
name: chint-translation
description: Bidirectional (ZH↔EN) B2B industrial translation, localization, and technical-audit standard for CHINT low-voltage power distribution and industrial control apparatus — ACB, MCCB, MCB/RCBO, contactors and starters, ATS, power quality (SVG/APF), sensors and electrical accessories, across datasheets, technical specifications, catalogs, and product manuals. Enforces IEC 60947 / 60898 / 61000 and UL 489 / 1066 / 1008 terminology, dual-track register selection (IEC catalog vs OEM manual), an anti-Chinglish forbidden-term dictionary used in both directions, and a value-slot convention that forbids inventing or inheriting any product rating. Use this skill whenever the user asks to translate, localize, review, or audit electrical-apparatus content between Chinese and English — including English-to-Chinese back-translation and bilingual bid review — or asks why a term or number in a deliverable looks wrong, even if they do not name the skill or mention a standard.
---

# CHINT Low-Voltage & Industrial Translation Skill (`chint-translation`)

## Overview

`chint-translation` is the authoritative translation and technical-governance standard for **all CHINT overseas and domestic deliverables**, covering the complete low-voltage power distribution, circuit protection, and industrial control portfolio. It runs in both directions, ZH→EN and EN→ZH (§3.2).

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        CHINT Universal Translation Portfolio                           │
├────────────────────────────────┬───────────────────────────────────────────────────────┤
│ 1. 三断 (Three Breakers)       │ ACB (万能式/框架), MCCB (塑壳), MCB/RCBO (微断/漏电)  │
│ 2. 一接 (Contactors & Starters)│ AC Contactors (交流接触器), Motor Starters, Overload  │
│ 3. 关键配电切换与电能质量      │ ATS (双电源转换开关), Power Quality (SVG, APF, PFC)   │
│ 4. 工控、传感器与电工辅料      │ Float switches, sensors, relays, terminal accessories  │
│ 5. 出海物料类型                │ Technical Specs, Product Manuals, Datasheets, PRDs    │
└────────────────────────────────┴───────────────────────────────────────────────────────┘
```

This skill focuses **exclusively on translation fidelity, electrotechnical terminology accuracy, and linguistic fluency**, completely independent of layout, typesetting, or graphic design.

---

## 1. Value Slot Convention (read before producing any number)

The `references/` dictionary is a **translation configuration, not a data sheet**. It stores terminology, field names, and sentence frames — never product ratings. Every physical quantity in it appears as a slot:

```
{{param_name: unit}}
```

A slot is a promise, not a value. Follow these rules in every deliverable:

1. **Resolve from a datasheet or drop it.** Fill a slot only from the product datasheet for the exact model in scope. If the source text carries no number, keep the sentence qualitative and leave the slot unfilled.
2. **Never inherit a number.** A rating from a comparable model, a competitor catalog, an earlier generation, or your own recollection is a fabrication. This is the single most common failure mode in this domain.
3. **Never ship an unresolved slot.** A deliverable containing `{{...}}` is a broken deliverable, not a draft. Resolve it or rewrite the sentence without the quantity.
4. **Unit inside the slot is template.** Copy it exactly (`kA rms`, `V`, `°C`, `N·m`, `mm²`) so downstream rendering stays stable.
5. **Terminology is not data.** Standard identifiers (`IEC 60947-2`), clause numbers, category designations (`AC-3`, `Curve C`, `Class PC`, `Cat B`, `ANSI 51N`), pole notations (`1P+N`), and series codes used for routing (e.g. NXA, NXM, NZ7) are vocabulary — write them literally.
6. **Marketing claims are frames, not facts.** A claim such as "full series reaches 100% Ics" is a template with an explicit `{{claim_scope}}`. It may only be published after the scope names real models and every numeric slot traces to a datasheet line.

Slot names are listed in [01_universal_iec_parameters.md](references/01_universal_iec_parameters.md) §0, which is the canonical definition. Read it on the first translation task in a session, or whenever a deliverable involves ratings.

---

## 2. Standard Reference Hierarchy

1. **IEC Electrotechnical Standards (Global Baseline)**:
   - `IEC 60947-1:2020`: Low-voltage switchgear and controlgear — General rules.
   - `IEC 60947-2:2024` (Edition 6.0, 2024-09): Low-voltage switchgear and controlgear — Part 2: Circuit-breakers (ACB, MCCB, CBR, MRCD, CBI, ICB, PV DC, CBAR, heavy industrial MCB).
   - `IEC 60898-1`: Circuit-breakers for overcurrent protection for household installations (MCB).
   - `IEC 60947-4-1`: Electromechanical contactors and motor-starters.
   - `IEC 60947-6-1`: Automatic transfer switching equipment (ATS / TSE).
   - `IEC 61008-1` / `IEC 61009-1`: Residual current operated circuit-breakers (RCCB, RCBO).
   - `IEC 61000-3-2` / `IEC 62477-1` / `IEEE 519`: Power quality, harmonic limits, SVG/APF.
   - `IEC 60529`: Degrees of protection provided by enclosures (IP Code).
2. **North American Standards (UL / ANSI / IEEE Mapping — isolated to UL columns/annotations only)**:
   - `UL 1066` / `ANSI C37.50`: Low-Voltage AC and DC Power Circuit Breakers (ACB / LVPCB).
   - `UL 489` / `CSA C22.2 No. 5`: Molded-Case Circuit Breakers & Enclosures (MCCB & MCB).
   - `UL 1077`: Supplementary Protectors for Use in Electrical Equipment.
   - `UL 1008`: Transfer Switch Equipment (ATS).
   - `UL 60947-4-1`: Industrial Control Equipment (Contactors & Starters).

When the standard fixes a value or a band, cite the standard; when the product fixes it, cite the datasheet. The two are not interchangeable and must never be merged into one sentence.

---

## 3. Adaptive Operating Modes & Linguistic Registers

### 3.1 Dual-Track Linguistic Register System (双轨制术语与语体系统)

Select the register by delivery objective. Both tracks enforce **strict IEC 60947-2:2024 single-track British spelling and hyphenation** (`circuit-breaker`, `moulded-case`, `withdrawable`, `undervoltage`, `shunt release`, `closing release`, `utilisation`, `colour`, `aluminium`, `energization`, `selectivity`, `back-up`, `operational performance / operating cycles`). North American spellings (`Molded-Case`, `Drawout`, `Shunt Trip`, `Color`, `Aluminum`, `Utilization`, unhyphenated `Circuit Breaker`) are restricted **exclusively** to explicit North American UL 489 / UL 1066 mapping columns or annotations.

| Linguistic Register | Target Delivery Context | Canonical Style Characteristics | Benchmark SSOT |
| :--- | :--- | :--- | :--- |
| **Track 1: IEC Global Catalogue Register (国际 IEC 标准 / 海外通用样本册语体)** | Overseas marketing catalogues, EPC tender brochures, international distributor sales sheets. | Concise, active international electrotechnical phrasing (aligned with Schneider Masterpact / ABB Emax2 / Siemens class) using strict IEC 60947-2:2024 functional nomenclature and British spelling (`Closing release`, `Shunt release`, `Undervoltage release`, `Door escutcheon`, `Withdrawable circuit-breaker`). | `IEC 60947-2:2024`, `IEC 60947-1:2020`, international catalogue benchmarks. |
| **Track 2: OEM Manual Register (企业官方产品说明书 / 运维规程语体)** | Factory instruction manuals, user guides, O&M procedures, installation booklets, compliance filings. | Strict 1:1 terminological alignment with the OEM's own published English manuals, harmonized to IEC 60947-2:2024 British spelling and hyphenation. Retains corporate canonical structural/accessory phrasing (`Closed electromagnet (CEM)`, `Undervoltage Instantaneous Trip (UVT)`, `Keys and locks (KL)`, `Steel Cable Interlock`, `Door Frame and Pad`, `Drawer seat`). | The OEM English operation & maintenance manual for the product in scope — read it from the project's own reference store; this skill deliberately does not bundle or hard-code its path. |

The two tracks are intentionally parallel. When both appear in a reference table, Track 2 wins for service documents and Track 1 wins for catalogue copy — never mix tracks inside one deliverable, and never introduce US spellings into either IEC track.

### 3.2 Translation Direction (双语方向)

This skill runs in **both directions**. Direction is stated by the user or inferred from the source text — it is never guessed silently when the evidence is weak.

| Direction | Typical Trigger | Deliverable Language | Dictionary Role |
| :--- | :--- | :--- | :--- |
| **ZH → EN (中译英)** — default | Overseas catalogues, datasheets, manuals, tender documents. | English | `07` and `iec60947_2_terminology_master.json` define the **forbidden-term** guardrails: avoid the ❌ column and unguarded US forms, produce the ✅ IEC 60947-2:2024 column (or UL column only when targeting North America). |
| **EN → ZH (英译中)** — reverse | Domestic review of an overseas draft, bilingual bid submission, Chinese service literature derived from an English master, back-translation for QA. | Chinese | `07` and `iec60947_2_terminology_master.json` are the **allowed-term** list: the ✅ Chinese term is the only legitimate anchor; the ❌ column is evidence of what a bad back-translation looks like, not a term to reproduce. |

**Direction rules:**

1. **Infer direction from the source, then confirm if ambiguous.** Source is predominantly Chinese → ZH→EN. Source is predominantly English → EN→ZH. If the source mixes languages (a bilingual table, an English draft with Chinese comments), state the direction you are using in the first line of the deliverable and proceed; do not ask unless the two readings would produce materially different output.
2. **Deliverable language follows the direction, not the chat language.** A ZH→EN deliverable is written in English. An EN→ZH deliverable is written in Chinese. Conversational language has no bearing on the deliverable.
3. **Chinese is permitted in a ZH→EN deliverable only in two places:** the `Chinese Source` column of a terminology mapping table, and the quoted source text inside a Mode B review. Outside those, the body — including headings, findings, and notes — is English. The mirror rule applies to EN→ZH: English appears only in the `English Source` column and in quoted source text.
4. **EN→ZH must land on the dictionary's ✅ Chinese term**, not on a fresh literal rendering. If a source English term has no entry in `07` or `iec60947_2_terminology_master.json`, flag it rather than inventing a Chinese equivalent, because an invented Chinese term silently forks the terminology base.
5. **Numbers, units, and slots are direction-neutral.** The value-slot convention in §1 applies unchanged both ways: a slot is resolved from the datasheet for the model in scope, never from the source language. Unit spacing follows §4 regardless of direction.
6. **Anti-Chinglish audit applies to ZH→EN only.** The failure mode it targets — Chinese syntax leaking into English — has no counterpart in EN→ZH. The EN→ZH counterpart to watch is *translationese*: over-literal calques of English noun stacks that read as foreign Chinese. Prefer a natural Chinese technical phrasing over a word-order-preserving one.

### 3.3 Operating Modes

- **Mode A: Direct Translation (直接翻译)**: Output a compliant, idiomatic translation in the target language, following the 5-step SOP, the selected register, IEC 60947-2:2024 British spelling/hyphenation, and the direction rules above.
- **Mode B: Translation Audit & Review (翻译审查)**: Inspect an existing translation against the SOP, `IEC 60947-2:2024` (or applicable UL/IEC product standard), `07_universal_anti_chinglish.md`, and `iec60947_2_terminology_master.json`. Report findings with location, standard clause/rule basis, and suggested fix; do not silently rewrite. The audit report is itself a deliverable and follows the deliverable-language rule — a ZH→EN review is written in English, an EN→ZH review in Chinese.

---

## 4. 5-Step Master Translation SOP

```
Step 1: Semantic Ingestion ──> Step 2: Category Routing ──> Step 3: IEC/UL Normalization ──> Step 4: Style Abstraction ──> Step 5: Anti-Chinglish Audit
```

### Step 1: Semantic Ingestion & Context Analysis
Parse the source text to identify the translation direction (§3.2), the core technical domain, the functional principle, the operating condition, and the intended audience (engineer, panel builder, EPC contractor, or procurement manager). Note every quantity in the source and mark whether it is a rated value, a test value, a setting range, or a physical dimension — this determines which slot it fills later.

### Step 2: Product Category Routing & Module Loading (产品类型判断树)

Identify the product category, then load the corresponding modules. The universal parameter module is **mandatory for every category**, because it defines the slot convention and the symbol set used everywhere else.

| Product Category | Series Codes (routing only) | Applicable Standards | Mandatory Reference Modules |
| :--- | :--- | :--- | :--- |
| **All categories** | — | All | [01_universal_iec_parameters](references/01_universal_iec_parameters.md) — slot convention + parameter symbols |
| **ACB (Air Circuit-Breakers / 框架断路器)** | NXA, NA8, NA1, Noark A | IEC 60947-2:2024, UL 1066 | [02_acb_trip_units](references/02_acb_trip_units_and_protection.md), [03_acb_accessories](references/03_acb_accessories_and_mechanisms.md), [iec60947_2_terminology_master.json](references/iec60947_2_terminology_master.json) |
| **MCCB & Annex Products (Moulded-Case, CBR, MRCD, CBI, ICB, PV DC, CBAR / 塑壳及特种断路器)** | NXM, NXS, NM8 | IEC 60947-2:2024 (Cl. 3–9 & Annexes A–R), UL 489 | [08_mccb_taxonomy](references/08_mccb_taxonomy_and_releases.md), [iec60947_2_terminology_master.json](references/iec60947_2_terminology_master.json) |
| **MCB & Modular (微型断路器与终端配电)** | NXB, NXBLE, NL1, DPN | IEC 60898-1, IEC 60947-2 | [09_mcb_rcbo_curves](references/09_mcb_rcbo_curves_and_accessories.md) |
| **ATS (Automatic Transfer Switches / 双电源)** | NZ7, NZ6, NH40SZ | IEC 60947-6-1, UL 1008 | [10_ats_classes](references/10_ats_classes_and_controllers.md) |
| **Contactors & Power Quality (接触器与电能质量)** | NXC, NXR, NDG, SV | IEC 60947-4-1, IEC 61000 | [11_power_quality_and_contactors](references/11_power_quality_and_contactors.md) |
| **Electrical Accessories & Sensors (辅料与工控)** | Terminals, connectors, float switches | IEC 60947-5-1, IEC 60529 | [04_universal_wiring](references/04_universal_wiring_and_contact_logic.md), [05_universal_safety](references/05_universal_safety_imperatives.md) |

Load [06_universal_technical_headings_and_claims](references/06_universal_technical_headings_and_claims.md) in addition when the deliverable is a catalogue, datasheet, or any text carrying marketing claims, and [07_universal_anti_chinglish](references/07_universal_anti_chinglish.md) in every task.

### Step 3: IEC/UL Parameter & Symbol Normalization

Map every parameter name onto its standard symbol. The value stays a slot; only the *name* is normalized here. The table below is written ZH→EN; for EN→ZH read it right-to-left, and treat the Standard English column as the only accepted anchor for the Chinese rendering.

| Chinese | Standard English | Note |
| :--- | :--- | :--- |
| 额定绝缘电压 | `Rated insulation voltage` ($U_i$) | `IEC 60947-2:2024 Cl. 5.3.2.2` |
| 额定冲击耐受电压 | `Rated impulse withstand voltage` ($U_{imp}$) | `IEC 60947-2:2024 Cl. 5.3.2.3`; never "impact" |
| 约定自由空气发热电流 | `Conventional free air thermal current` ($I_{th}$) | `IEC 60947-2:2024 Cl. 5.3.3.1`; never "pure air" / "agreed-upon" |
| 额定工作电压 / 额定电流 | `Rated operational voltage` / `Rated current` ($U_e$ / $I_n$) | `IEC 60947-2:2024 Cl. 5.3.2.1` / `Cl. 5.3.3.3` ($I_n = I_u = I_{th}$) |
| 壳架等级 / 壳架电流 | `Frame size` (`Cl. 3.1.1`) / `Frame current` ($I_{nm}$, `GB/T 14048.2` only) | `IEC 60947-2:2024 Cl. 3.1.1` defines `frame size` in amperes (28×); `Inm` has 0 occurrences in IEC 60947-2 |
| 额定极限 / 单极极限 / 运行 / 短时耐受 / 接通 / 短路能力 | `Rated ultimate` ($I_{cu}$, `Cl. 5.3.6.2.2`) / `individual pole ultimate at phase-to-neutral AC voltage` ($I_{cu1}$, `Cl. 5.3.6.2.3 & 9.3.11`) / `service` ($I_{cs}$, `Cl. 5.3.6.2.4`) / `short-time withstand` ($I_{cw}$, `Cl. 5.3.6.4`) / `making` ($I_{cm}$, `Cl. 5.3.6.1`) / `short-circuit capacity` ($I_{cn}$, `IEC 60898-1`) | Catalogue table header: `Ultimate breaking capacity Vac 50/60 Hz` |
| 分断能力型号 | `Breaking capacity type` | e.g. Type N / S / H; never "breaking capacity levels" |
| 选择性类别 / 使用类别 | `Selectivity category` (`Category A / B`, `Cl. 4.1 & 5.4`) / `Utilisation category` (`AC-15`, `DC-13`, `AC-3`, `AC-22` per `Annex L.4.1`) | Never "discrimination"; never conflate Selectivity Cat B with Utilisation category |
| 机械 / 电寿命 | `Operational performance without / with current` / `Number of operating cycles` (`Cl. 8.2.4.2 & Table 7`); `Mechanical / Electrical endurance` (`Annex M M.8.11`, `Annex R R.8.5`) | `durability` = 0 occurrences in IEC 60947-2:2024; convert 万-based figures into a plain integer (`{{ops: cycles}}`) |

**Unit and number formatting:**

- Exactly one half-width space between a value and its unit. Write `{{value: A}}`, `{{value: V}}`, `{{value: Hz}}`, `{{value: kV}}`, `{{value: kA}}`, `{{value: N·m}}`. Never concatenate value and unit, and never insert two spaces.
- Temperature always carries a half-width space plus the degree symbol and a capital `C`: `{{T: °C}}`. Never the full-width `℃`, a bare `C`, a spelled-out `deg C`, or an omitted space.
- Values themselves are slots until a datasheet supplies them — see §1.

### Step 4: Linguistic Style Abstraction & Syntactic Archetypes (语言风格抽象化与句式文法原型)

Translate technical functions by instantiating these six abstract archetypes. Bracketed items are slots or free text, never invented values. Every occurrence of `circuit-breaker` is hyphenated and uses IEC 60947-2:2024 British spelling across both Track 1 and Track 2.

1. **Permission / Prohibition Modals (权限与闭锁模态句型)**
   - *Abstract*: `[Enclosure/Component] is forbidden to [Action] when [Condition A] and is allowed to [Action] when [Condition B].`
   - *Sample (SDIL/PDIL)*: "The cabinet door is forbidden to open when the circuit-breaker is closed and is allowed to open when the circuit-breaker is disconnected."
2. **Protective Ride-Through / Operational Refusal (保护拒动与穿越句型)**
   - *Abstract*: `When [Parameter] returns to [Nominal State] within [Fraction] [Delay Time], the [Apparatus] refuses to open / will not trip.`
   - *Sample (UVTR/UVTZ)*: "When the voltage returns to normal within `{{uvtr_ride_through_fraction}}` of the delay time, the circuit-breaker refuses to open."
3. **Rating Independence & Signal Sampling (定值独立性与采样拓扑句型)**
   - *Abstract*: `The [Tripping Value] is directly expressed in [Physical Unit], irrelevant to [Apparatus Rating]. The signal is taken in [Sampling Mode], requiring [External Component].`
   - *Sample (RCT)*: "The leakage trip value IΔn is directly expressed in amperes, irrelevant to the rated current of the circuit-breaker. The signal is taken in a zero-sequence sampling mode, requiring an external leakage transformer."
4. **Action Threshold Dichotomy (动作阈值配对词法原型)**
   - *Release Actions*: `Trip` (脱扣/分断) ⟷ `Pull-in` (吸合/接通) ⟷ `Holding` (保持).
   - *Mechanism States (`Cl. 3.5`, `8.1.2`)*: `Disconnected position` *(IEC 60947-2:2024 standard; OEM manual legacy: Separation position)* ⟷ `Test position` ⟷ `Connected position` *(IEC standard; OEM manual legacy: Connection position)*.
5. **Lock-and-Key Combinatorial (锁匙组合句式原型)**
   - *Abstract*: `[N] locks and [M] keys: [X] circuit-breakers are equipped with [N] [identical/separate] locks and [M] [identical/separate] keys.`
   - *Sample (KL)*: "Two locks and one key: Two circuit-breakers are equipped with two identical locks and one key."
   - *Tool Idiom*: `hole opener` (Manual SSOT) or `hole punch / hole saw` (Catalogue standard).
6. **Pulse Duty Cycle Constraint (脉冲通电工作制约束句型)**
   - *Abstract*: `The [Accessory A] and [Accessory B] belong to the pulse energization working mode, and it is necessary to ensure that the pulse time t1 is not less than [T1] and the energization interval t2 is greater than [T2].` *(IEC 60947-2:2024 uses `-ize` / `energization`.)*
   - *Sample (SHT/CEM)*: "The Shunt Release and Closing Release (OEM: Closed Electromagnet) belong to the pulse energization working mode, and it is necessary to ensure that the pulse time t1 is not less than `{{pulse_time_t1: ms}}` and the energization interval t2 is greater than `{{pulse_interval_t2: s}}`."

### Step 5: Quality Audit & Final Verification

- **Direction check.** Confirm the deliverable is in the language §3.2 requires, and that Chinese (in a ZH→EN deliverable) or English (in an EN→ZH deliverable) appears only in the two permitted positions.
- **ZH→EN:** filter the translated text against §5 below and the full dictionary in `07_universal_anti_chinglish.md`. Strip all Chinese full-width punctuation (`；`, `（ ）`, `：`) and replace with half-width English equivalents.
- **EN→ZH:** confirm every technical term landed on its ✅ Chinese form from `07`, and that no invented Chinese equivalent was substituted. Use Chinese full-width punctuation in Chinese prose, but keep half-width punctuation and half-width spacing inside code, units, and parameter symbols.
- Unify branding: the corporate name in all caps, and the series designation registered in the target market. Never transliterate or translate a brand or series name — in either direction.
- Run the slot check: no `{{...}}` may survive into the deliverable.

---

## 5. Anti-Chinglish Quick Reference (High-Frequency Master List)

This is a **quick-reference subset**, not the dictionary. The authoritative table — with forbidden forms, rationale, and per-category scope — is [07_universal_anti_chinglish.md](references/07_universal_anti_chinglish.md). When the two differ, `07` wins; when a term is missing here, consult `07` before deciding it is safe.

Read the table by direction (§3.2): ZH→EN takes the ✅ column as the required output; EN→ZH takes the ✅ column as the **only** acceptable Chinese rendering and the ❌ column as a marker of what a bad back-translation produces.

| Chinese Source | ❌ Forbidden Literal | ✅ Mandatory Professional English |
| :--- | :--- | :--- |
| **万能式断路器** | Universal Circuit Breaker | **Air Circuit-Breaker (ACB)** *(IEC Global / OEM)* / **Low-Voltage Power Circuit Breaker (LVPCB, UL 1066)** *(North America)* |
| **塑壳断路器** | Plastic shell breaker / Molded circuit breaker | **Moulded-case circuit-breaker (MCCB)** *(IEC British spelling)* / **Molded Case Circuit Breaker (MCCB, UL 489)** *(North America)* |
| **微型断路器** | Mini circuit breaker / Small breaker | **Miniature Circuit-Breaker (MCB)** |
| **漏电断路器** | Leakage breaker | **Residual Current Circuit-Breaker (RCBO / RCCB)** / **Circuit-Breaker Incorporating Residual Current Protection (CBR, Annex B)** |
| **双电源自动转换开关** | Dual power auto switch | **Automatic Transfer Switch (ATS / TSE)** |
| **交流接触器** | AC connector / AC switcher | **AC Contactor** |
| **抽屉式 / 抽屉座** | Drawer / Drawer type / Drawer box | **Withdrawable / Withdrawable circuit-breaker** (`Cl. 3.5, 4.4`); **Cradle / Withdrawable chassis** *(IEC)* / **Drawer seat** *(OEM manual)* / **Drawout / Drawout chassis** *(North America / UL)* |
| **闭合电磁铁** | Close electromagnet (verb form) / Closing magnet | **Closing release (closing coil) (CC / CEM)** *(IEC 60947-2:2024 Cl. 3.19)* / **Closed electromagnet (CEM)** *(OEM manual Track 2)* |
| **分励脱扣器** | Excitation release / Shunting release / Shunt opening release | **Shunt release (SHT / MX / YO)** *(IEC 60947-2:2024 Cl. 5.7.1)* / **Shunt Trip (ST)** *(North America / UL)* |
| **欠电压脱扣器** | Lack voltage trip / Less voltage trip / Under-voltage | **Undervoltage release (UVR / MN)** *(IEC 60947-2:2024 Cl. 5.7.1)* / **Undervoltage trip (UVT / UVTR)** *(OEM manual Track 2)* |
| **灭弧室** | Interrupter / Arc room | **Arc extinction device** (`Cl. 8.1.6`) / **Arc-extinguishing chamber / Arc chute** *(catalogue / OEM)* |
| **电动操作机构 (电操)** | Operating device / Motor hand | **Motor-operator / Motor operator device (MOD) / Motor mechanism** (`Annex N`) |
| **智能控制器 / 控制器** | Intelligent controller (literal) | **Controller / Electronic Trip Unit (ETU)** |
| **相间隔板** | Phase space plate | **Interphase barrier / Phase barrier** *(catalogue)* / **Interphase partition** *(OEM manual)* |
| **门框 / 柜门面罩** | Face mask | **Door escutcheon (Door flange)** *(catalogue)* / **Door Frame and Pad** *(OEM manual Track 2)* |
| **本体钥匙锁** | Body key lock | **Circuit-breaker key lock / ACB Key Lock (KLC)** *(catalogue)* / **Keys and locks (KL)** *(OEM manual Track 2)* |
| **机械联锁 (钢缆)** | Rope interlock | **Mechanical Interlock (MI)** *(catalogue)* / **Steel Cable Interlock** *(OEM manual Track 2)* |
| **区域选择性联锁** | Area choice lock / Area select lock | **Zone Selective Interlocking (ZSI)** |
| **分断能力型号** | Breaking capacity levels | **Breaking capacity type (Type N / Type S / Type H)** |
| **壳架等级 / 壳架电流** | Frame specification / Shell rating / Inm (attributed to IEC 60947-2) | **Frame size** *(IEC 60947-2:2024 Cl. 3.1.1)* / **Frame current (Inm)** *(GB/T 14048.2 domestic convention)* |
| **选择性 / 后备保护** | Discrimination / Backup | **Selectivity** (`Cl. 4.1, 5.4, Annex A`) / **Back-up protection** (`Annex A.6`) |
| **额定冲击耐受电压** | Rated impact withstand voltage | **Rated impulse withstand voltage Uimp** |
| **约定自由空气发热电流** | Agreed-upon heating current in pure air | **Conventional free air thermal current Ith** |
| **基准 (图纸标注)** | Base / Reference mark | **Datum** |
| **安装调试** | Installation and Debugging | **Installation and Commissioning** |
| **注意事项 / 订货须知** | Matters need attention / Ordering instruction | **Operating Precautions / Safety Notes**; **Ordering Information** |
| **误动作** | Wrong action / Error work | **False tripping / Nuisance tripping** |
| **重锤 / 配重块** | Heavy Hammer / Heavy weight | **Counterweight / Balance Weight** |
| **寿命：N 万次** | N Ten thousand times / Durability (IEC 60947-2) | **Operational performance / Operating cycles** (`Cl. 8.2.4.2, Table 7`) / **Endurance** (`Annex M/R`); `{{ops_wan: 万次}}` → `{{ops: operations}}` (plain integer from datasheet) |

---

## 6. Granular Knowledge Base & Context Pointers (`references/`)

Load only the modules the routing table selects, plus `01` and `07`. Every module opens with a §0 note stating which fields it fixes and which it deliberately leaves to the datasheet.

### Universal Modules
- [01_universal_iec_parameters.md](references/01_universal_iec_parameters.md) — **load first**: value-slot convention, parameter symbol set ($U_i$, $U_{imp}$, $U_e$, $I_n$, $I_{cu}$, $I_{cu1}$, $I_{cs}$, $I_{cw}$, $I_{cm}$, $I_{th}$, $I_{the}$, `frame size` vs $I_{nm}$), operational performance / endurance, environmental and derating fields, unit/spacing rules.
- [04_universal_wiring_and_contact_logic.md](references/04_universal_wiring_and_contact_logic.md) — changeover / SPDT auto-fill and auto-drain wiring, secondary control terminals, three-position racking states.
- [05_universal_safety_imperatives.md](references/05_universal_safety_imperatives.md) — native engineering precaution phrasing (inrush current, suction vortex, fluid turbulence); safety limits must never ship with an unresolved slot.
- [06_universal_technical_headings_and_claims.md](references/06_universal_technical_headings_and_claims.md) — standard section headings, plus claim *frames* with explicit scope slots and use-only-when conditions.
- [07_universal_anti_chinglish.md](references/07_universal_anti_chinglish.md) — authoritative forbidden-term dictionary, IEC 60947-2:2024 vs US spelling & annex false-friend guardrails, and sentence-level rewriting patterns.

### Per-Category Extension Modules
- [02_acb_trip_units_and_protection.md](references/02_acb_trip_units_and_protection.md) — ACB electronic trip units (M/A/P/H), L/S/I/G/V/N protection slots, ZSI, MCR, thermal memory, harmonics, and IEC 60947-2:2024 Cl. 3/5/8/Annex F/K/A/B/M alignment.
- [03_acb_accessories_and_mechanisms.md](references/03_acb_accessories_and_mechanisms.md) — ACB internal/external accessories (SHT/MX, UVR/MN, CC/CEM, MOD/MOE, RTC/SPC, PSID, key locks, safety shutters) harmonized to IEC 60947-2:2024 British spelling and six syntactic archetypes.
- [08_mccb_taxonomy_and_releases.md](references/08_mccb_taxonomy_and_releases.md) — complete MCCB & IEC 60947-2:2024 Clauses 3–9 and Annexes A–R taxonomy (TM/ETU releases, Test Sequences I–VIII, selectivity & back-up coordination, CBR, phase-earthed, aluminium conductors, EMC, power loss, IT systems, CBI, MRCD, ICB, PV DC up to 1 500 V DC, CBAR, plug-in/withdrawable bases, HR/VR terminals).
- [09_mcb_rcbo_curves_and_accessories.md](references/09_mcb_rcbo_curves_and_accessories.md) — MCB curve bands, pole configurations, RCCB/RCBO types (AC/A/B), DIN-rail mounting.
- [10_ats_classes_and_controllers.md](references/10_ats_classes_and_controllers.md) — ATS Class PC vs Class CB, transition types (BBM/MBB), transfer and return timing slots.
- [11_power_quality_and_contactors.md](references/11_power_quality_and_contactors.md) — AC contactors (AC-3/AC-4), thermal overload relays, SVG, APF, detuned reactors.
- [iec60947_2_terminology_master.json](references/iec60947_2_terminology_master.json) — machine-readable unified IEC 60947-2:2024 (Edition 6.0) structured terminology master covering ACB, MCCB, Clauses 3–9, and Annexes A–R; all product rating fields use value slots.

---

## 7. Completion Criteria

1. **[ ] No unresolved slot.** The deliverable contains no `{{...}}`. Every quantity traces to a datasheet line for the exact model in scope. This check blocks delivery — do not hand over work that fails it.
2. **[ ] Direction honoured.** The deliverable is in the target language required by §3.2, and the other language appears only in the two permitted positions (mapping-table source column, quoted source text).
3. **[ ] Category routing confirmed.** Product category identified and the matching modules loaded, including the mandatory universal parameter module.
4. **[ ] Zero literal machine translation.** ZH→EN: all terms checked against the dictionary in `07` and `iec60947_2_terminology_master.json`, plus the category-specific forbidden lists. EN→ZH: every term landed on the ✅ Chinese form, with no invented equivalent.
5. **[ ] Register & IEC orthography consistent.** The whole deliverable is Track 1 or Track 2 — not a mixture — uses strict IEC 60947-2:2024 British spelling and hyphenation (`circuit-breaker`, `moulded-case`, `withdrawable`, `undervoltage`, `utilisation`, `colour`, `aluminium`, `energization`), and isolates US spellings strictly to UL / North American columns.
6. **[ ] Exact standards compliance.** Parameters, curves, and ratings mapped to the correct IEC (`60947-2:2024`, `60898-1`, `60947-4-1`, `60947-6-1`) or UL (`489`, `1066`, `1008`) reference, with the standard cited rather than paraphrased.
7. **[ ] Contact logic symmetrical.** Every changeover / SPDT / secondary-circuit instruction states contact state and operating sequence explicitly.
8. **[ ] Claims scoped.** Every marketing claim names its model scope and survives re-scoping; superlatives removed where they do not.
9. **[ ] Fluency and ambiguity check.** Sentence structures follow native usage in the target language — no grammatical or contextual ambiguity, and no translationese in either direction.
