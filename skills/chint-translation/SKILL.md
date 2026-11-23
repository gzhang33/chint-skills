---
name: chint-translation
description: Pure single-track IEC 60947-2:2024 bidirectional (ZH↔EN) B2B translation, localization, and technical-audit standard for CHINT low-voltage circuit-breakers (ACB, MCCB, and Annex A–R derivatives). Enforces one canonical IEC English term per concept paired with CHINT-specific accessory codes, UK + ISO/IEC Oxford -ize orthography, an anti-Chinglish audit blacklist, a 1+1+N department-isolated loading rule, and a value-slot convention that forbids inventing any product rating. Use whenever translating, localizing, back-translating, or auditing electrical-apparatus specs, catalogues, datasheets, or manuals between Chinese and English.
---

# CHINT Low-Voltage Translation & Audit Standard (`chint-translation` v3.0.0)

## 1. Pure IEC Single-Track Mandate (纯正 IEC 单轨铁律)

1. **One Canonical Output Per Concept**: Every Chinese electrotechnical or product term maps to **one unique IEC-aligned English term** across catalogues, datasheets, tenders, and manuals alike. Dual-track translation (separate catalogue vs manual vocabularies) and North American UL columns are abolished.
2. **CHINT Exclusive Codes Only**: When an accessory or sub-assembly carries an official CHINT code (`SHT`, `CEM`, `UVT`, `MOD`, `SPC`, `KL`, `DD`, `FD`, etc.), format as **`Canonical IEC Term (CHINT Code)`** — e.g. `Closing release (CEM)`, `Shunt release (SHT)`, `Ready-to-close contact (SPC)`. Never output competitor codes (`MX`, `MN`, `XF`, `OF`, `SDE`, `PF`, `MCH`, `KLC`).
3. **IEC 60947-2:2024 Orthography**: Enforce British nouns (`circuit-breaker`, `moulded`, `withdrawable`, `colour`, `aluminium`, `catalogue`, `behaviour`, `programme`, `analogue`, `signalling`) + ISO/IEC Oxford `-ize` (`utilization`, `utilize`, `energize`, `energization`) + standard hyphenation (`lock-out`, `back-up`, `pick-up`, `time-delay`, `making-current release`, `let-through`, `cut-off`) + unhyphenated `undervoltage` and `Coordination`.

---

## 2. `1 + 1 + N` Context-Hygiene Routing (按需独立加载，严禁跨部门混读)

To prevent context bloat and cross-department collisions, this skill uses a strict **`1 + 1 + N`** layout:

| Tier | File Path | When to Load | Rule |
| :--- | :--- | :--- | :--- |
| **`1` Master SOP** | `SKILL.md` (this file) | Every task | Inline rules, direction, value slots, completion gate. |
| **`1` IEC Standard** | [iec_60947_2_standard.md](references/iec_60947_2_standard.md) | Any circuit-breaker / parameter / standard task | Authoritative `IEC 60947-2:2024` (Ed. 6.0, Cl. 3–9 & Annexes A–R) + `IEC 60947-1:2020` definitions, symbols, and clauses. |
| **`N` Department** | [departments/acb.md](references/departments/acb.md) | **ACB (框架断路器)** tasks only (`NXA`, `NA8`, `NA1`) | CHINT ACB ETUs, 24+ exclusive accessory codes, native sentence frames, ACB blacklist, custom extension table. |
| **`N` Department** | [departments/mccb.md](references/departments/mccb.md) | **MCCB (塑壳断路器)** tasks only (`NXM`, `NXS`, `NM8`, `NM5`) | CHINT MCCB releases, mounting/connection accessories, MCCB blacklist, custom extension table. |
| **Template** | [departments/_template.md](references/departments/_template.md) | Only when creating a new department file | Standalone template for new product departments (MCB, ATS, Contactors, etc.) — **never merge two departments into one file**. |

- **Hard Isolation Rule**: Load **only** the single `departments/<dept>.md` matching the product in scope. Never load another department's file.
- **Local Workspace Reference Rule**: When translating or auditing a specific CHINT series, check the local reference folder named in §1 of that department's file (e.g. `Areas/样本册修改/NXA/参考资料/` or `Projects/5 系列海外导入/`) to verify model designations, CHINT accessory codes, and datasheet numbers. Take only verified model/parameter facts from local files — never copy raw unreviewed ERP typos or legacy Chinglish.

---

## 3. Value-Slot & Formatting Invariant (值槽与排版红线)

Reference files store **terminology and `{{param_name: unit}}` slots, never product ratings**:

1. **Resolve from a datasheet or rewrite qualitatively**: Fill a slot only from the exact model's datasheet or user-supplied source. Never inherit a rating from another model, competitor catalogue, or memory.
2. **Zero unresolved slots in deliverables**: Never output literal `{{...}}` in a finished translation or audit.
3. **Unit spacing & numbers**: Insert **exactly one half-width space** between number and unit (`250 A`, `415 V AC`, `36 kA rms`, `50 Hz`, `8 kV`, `10 N·m`, `-5 °C` to `+40 °C`). Never use full-width `℃`, `400A` concatenation, or literal `"ten thousand times"` (convert `N 万次` to plain integer `{{ops: operating cycles}}`).
4. **Scoped claims**: Superlative or family-wide claims (`100% Ics`, rotatable terminals) require an explicit verified model scope (`{{claim_scope}}`) backed by datasheet rows.

---

## 4. Direction & Operating Modes (双向与双模式规则)

| Direction / Mode | Deliverable Language | Execution Rule |
| :--- | :--- | :--- |
| **ZH → EN (Default)** | English (Chinese allowed only in mapping-table source column or Mode B quoted source) | Output **only** the ✅ canonical IEC English term (+ CHINT code where applicable). Strip all full-width Chinese punctuation (`；` `（）` `：`). |
| **EN → ZH (Back-translation / Review)** | Chinese (English allowed only in mapping-table source column or quoted source; keep units/symbols half-width: `kA rms`, `V AC`) | Land strictly on the ✅ canonical Chinese term (`GB/T 14048.2` aligned). Legacy OEM/US terms in the ❌ blacklist are recognized for comprehension and mapped to the ✅ Chinese term — never invent fresh calques. |
| **Mode A: Direct Translation** | Target language per direction | Produce idiomatic, single-track IEC technical prose obeying §1–§4. Use normative `shall` for mandatory safety/installation instructions. |
| **Mode B: Technical & Translation Audit** | Target language per direction | Inspect draft against `iec_60947_2_standard.md` and the active `departments/<dept>.md`. Flag every ❌ blacklist term, US spelling leak, obsolete Ed. 5.x clause ref, unit-spacing error, unverified rating, or technical contradiction (e.g. `Category A` paired with `Isd` short-time delay) with location, clause basis, and exact fix. |

---

## 5. Completion Gate (交付前逐项核验)

- [ ] **Single-track & pure IEC**: Zero Track 2 legacy Chinglish (`Closed electromagnet`, `Drawer seat`, `refuses to open`), zero UL/US leaks (`Molded`, `Color`, `Aluminum`, `Shunt Trip`, `LVPCB`, unhyphenated `Circuit Breaker`), zero competitor codes (`MX`, `MN`, `XF`, `OF`, `SDE`, `PF`).
- [ ] **Exact `IEC 60947-2:2024` (Ed. 6.0) clauses & terms**: Verified against `iec_60947_2_standard.md` (zero obsolete Ed. 5.x `Cl. 2.x / 4.3.x`, zero `durability`, zero `discrimination`, `frame size` per `Cl. 3.1.1` vs `Inm` per `GB/T 14048.2`).
- [ ] **Zero unresolved slots & zero fabricated ratings**: No `{{...}}` remains; every number traces to source/datasheet with single half-width unit spacing and `°C`.
- [ ] **Department isolation honoured**: Only the target department module loaded; department-specific CHINT codes verified.
