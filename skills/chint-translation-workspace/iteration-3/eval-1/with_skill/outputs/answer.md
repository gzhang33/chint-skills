Direction: ZH→EN — Mode B Translation & Terminology Audit (Track 1: IEC Global Catalogue Register, IEC 60947-2:2024)

# Mode B Translation & Terminology Audit Report — `NXM-250S` Specification Draft

## 1. Audit Metadata & Scope

- **Operating Mode**: Mode B — Translation & Terminology Audit (audit findings and modification recommendations only; no silent rewrite and no unprovided product ratings added).
- **Translation Direction**: ZH→EN (auditing an English specification draft intended for an overseas IEC catalogue; per `chint-translation` §3.2–3.3, a ZH→EN Mode B audit report is written in English, with Chinese restricted strictly to the `Chinese Source` column of the terminology alignment table).
- **Product Category**: Moulded-Case Circuit-Breaker (MCCB) — series designation `NXM-250S` (preserved verbatim; never translated or transliterated).
- **Target Linguistic Register**: Track 1 — IEC Global Catalogue Register (`IEC 60947-2:2024`, Edition 6.0, single-track British spelling + `-ize` verb orthography and mandatory hyphenation).
- **Authoritative References Applied**: `IEC 60947-2:2024` (Clauses 3–9 & Annexes A–R), `01_universal_iec_parameters.md`, `06_universal_technical_headings_and_claims.md`, `07_universal_anti_chinglish.md`, `08_mccb_taxonomy_and_releases.md`, and `iec60947_2_terminology_master.json`.

---

## 2. Executive Summary

| Audit Dimension | Count | Key Findings |
| :--- | :---: | :--- |
| **IEC 60947-2:2024 vs US Orthography & Hyphenation** | 4 | US `Molded`, unhyphenated `Circuit Breaker` / `circuit breaker` (2×), US `pickup` (2×) instead of IEC `pick-up` / `instantaneous short-circuit current setting`. |
| **Forbidden / Non-IEC Terminology & Anti-Chinglish** | 5 | `durability` (2×; 0 occurrences in `IEC 60947-2:2024`), Chinglish unit `times` (2×), literal phrasing `"suitable for distribution protection"`. |
| **Unit, Multiplier & Range Typography** | 9 | Missing half-width space before units (`250A`, `800V`, `8kV`, `36kA`, `415V`), CJK range tilde `~` and missing multiplication sign/spacing (`0.7~1.0In`, `2~10Ir`, `5~10In`), unformatted 4/5-digit cycle counts (`20000`, `8000`). |
| **Normative Parameter Naming & Completeness** | 2 + 8 gaps | Shortened breaking-capacity labels lacking current kind/frequency; 8 mandatory `IEC 60947-2:2024 Table 4` / datasheet fields missing (including `In`, `Ue` AC/DC & frequency, pole count, selectivity category, release type, and time settings). |
| **Colleague Comment Verdict (`Frame size` vs `Inm`)** | 1 | **Colleague's objection rejected.** `Frame size` is the exact `IEC 60947-2:2024 Cl. 3.1.1` term (28 occurrences); `Inm` has **0 occurrences** in `IEC 60947-2:2024` and belongs exclusively to `GB/T 14048.2`. Retain `Frame size` and fix unit spacing to `250 A`. |

---

## 3. Special Verification: `Frame size: 250A` vs `Frame current Inm`

**Verdict: Retain `Frame size` (corrected for unit spacing to `Frame size: 250 A`). Reject the colleague's proposal to mandate `Frame current Inm` in an `IEC 60947-2:2024` overseas catalogue.**

### 3.1 Normative Verification Against `IEC 60947-2:2024`

1. **`frame size` is an exact, normative `IEC 60947-2:2024` term (`Cl. 3.1.1`, printed page P20)**:
   - `IEC 60947-2:2024 Cl. 3.1.1` defines **`frame size`** as a group of circuit-breakers whose external physical dimensions are common to a range of current ratings.
   - **Note 1 to entry (`Cl. 3.1.1`, P20)** explicitly specifies that **`frame size` is expressed in amperes corresponding to the highest current rating of the group** (Note 2 clarifies that width may vary with the number of poles; Note 3 clarifies that it does not imply dimensional standardization).
   - Verified frequency across `IEC 60947-2:2024`: **`frame size` appears 28 times** in the standard text.
2. **`Inm` does not exist in `IEC 60947-2:2024`**:
   - Verified frequency across `IEC 60947-2:2024`: **`Inm` has 0 occurrences** (absent from `Cl. 3.1.1`, `Cl. 5.3.3`, and `Annex K Table K.1`).
   - Where `IEC 60947-2:2024` refers to the maximum rated current associated with a frame size — for example in **`Table 7` footnote a (P40)** — it uses the phrase ***"maximum rated current for a given frame size"***, never `Inm`.
3. **True provenance of `Inm`**:
   - **`Inm`** (frame current) is a domestic **`GB/T 14048.2`** convention, not an IEC 60947-2 symbol.
   - Under `chint-translation` guardrails (`TRM-DON-019` in `07_universal_anti_chinglish.md`, `01_universal_iec_parameters.md` §1, `08_mccb_taxonomy_and_releases.md` §1.2 & §7, and `IEC2-CORE-002` in `iec60947_2_terminology_master.json`), attributing `Inm` to `IEC 60947-2` is explicitly prohibited, and legacy prohibitions against `frame size` have been revoked.

### 3.2 Actual Defect in Line 2 & Required Action

- **What is right**: The term **`Frame size`** and expressing it in amperes (`250 A`) fully comply with `IEC 60947-2:2024 Cl. 3.1.1` Note 1.
- **What is wrong**: Only the unit spacing (`250A` lacks a half-width space between the numeral and `A`).
- **Required action**:
  - In **Track 1 overseas IEC catalogues**: write **`Frame size: 250 A`**.
  - Reserve **`Frame current Inm`** strictly for domestic `GB/T 14048.2` documentation; never replace `Frame size` with `Inm` under `IEC 60947-2:2024`.

---

## 4. Line-by-Line Mode B Audit Findings & Suggested Modifications

### Summary Matrix

| Line | Quoted Draft Text | Defect Type | Normative / Rule Basis | Suggested Modification (Draft Values Only) |
| :---: | :--- | :--- | :--- | :--- |
| **1** | `"NXM-250S Molded Case Circuit Breaker (IEC 60947-2)."` | US spelling + unhyphenated device noun | `IEC 60947-2:2024 Cl. 3.1` (P19), `Cl. 9.3.3.3`, `Cl. 8.1.6`; `TRM-DON-020`; `07` §5; `08` §0 & §7; `IEC2-CORE-001` | `NXM-250S Moulded-Case Circuit-Breaker (IEC 60947-2)` *(verify whether certification supports citing `IEC 60947-2:2024`)* |
| **2** | `"Frame size: 250A."` | Unit spacing missing (`Frame size` itself is correct) | `IEC 60947-2:2024 Cl. 3.1.1` (P20); `TRM-DON-019`; `01` §4; `07` §4; `IEC2-CORE-002` | `Frame size: 250 A` |
| **3** | `"Rated insulation voltage Ui: 800V."` | Unit spacing missing | `IEC 60947-2:2024 Cl. 5.3.2.2` (P24); `01` §4; `07` §4; `IEC2-CORE-021` | `Rated insulation voltage Ui: 800 V` |
| **4** | `"Rated impulse withstand voltage Uimp: 8kV."` | Unit spacing missing | `IEC 60947-2:2024 Cl. 5.3.2.3` (P24); `01` §4; `07` §4; `IEC2-CORE-022` | `Rated impulse withstand voltage Uimp: 8 kV` |
| **5** | `"Ultimate breaking capacity Icu: 36kA at 415V."` | Unit spacing missing (2×); abbreviated parameter name; missing current kind / frequency / `rms` qualification | `IEC 60947-2:2024 Cl. 5.3.6.2.2` & `Cl. 3.11.1` (P25), `Cl. 5.3.2.1`, `Cl. 5.3.4`; `01` §1 & §4; `06` §3; `IEC2-CORE-028` | `Rated ultimate short-circuit breaking capacity Icu: 36 kA at 415 V` *(confirm `kA rms`, AC/DC kind, and frequency from datasheet before adding them)* |
| **6** | `"Service breaking capacity Ics: 100% Icu."` | Abbreviated parameter name; ratio phrasing (`% of Icu`) & claim-scope check | `IEC 60947-2:2024 Cl. 5.3.6.2.4` & `Cl. 3.11.3` (P26); `01` §1; `06` §2 (`CLM-001`) & §3; `IEC2-CORE-030` | `Rated service short-circuit breaking capacity Ics: 100 % of Icu` *(confirm applicability strictly to `NXM-250S` at `415 V` from datasheet)* |
| **7** | `"Mechanical durability: 20000 times."` | Forbidden non-IEC term (`durability`); Chinglish unit (`times`); ungrouped 5-digit integer | `IEC 60947-2:2024 Cl. 8.2.4.2` & `Table 7` (P39–40), `Annex M.8.11`, `Annex R.8.5`; `01` §2; `07` §2, §4 & §5; `08` §7; `IEC2-CORE-033` | `Operational performance without current: 20 000 operating cycles` *(or Track 1 catalogue short form: `Mechanical endurance: 20 000 operating cycles`)* |
| **8** | `"Electrical durability: 8000 times."` | Forbidden non-IEC term (`durability`); Chinglish unit (`times`); ungrouped 4-digit integer | `IEC 60947-2:2024 Cl. 8.2.4.2` & `Table 7` (P39–40), `Annex M.8.11`; `01` §2; `07` §2, §4 & §5; `08` §7; `IEC2-CORE-034` | `Operational performance with current: 8 000 operating cycles` *(or Track 1 catalogue short form: `Electrical endurance: 8 000 operating cycles`)* |
| **9** | `"Overload setting Ir: 0.7~1.0In. Short-time pickup Isd: 2~10Ir. Instantaneous pickup Ii: 5~10In."` | US `pickup` (2×) & shortened IEC parameter names; CJK tilde `~` (3×); missing `×` multiplier & spacing (3×); omitted time settings & release type | `IEC 60947-2:2024 Cl. 3.15–3.17` (P22), `Cl. 3.8` (P21), `Table K.1` (P187–188), `Fig. K.1` (P189); `08` §2.3; `IEC2-CORE-050/051/052` | `Overload current setting Ir: (0.7 to 1.0) × In. Short-time pick-up current setting Isd: (2 to 10) × Ir. Instantaneous short-circuit current setting Ii: (5 to 10) × In.` |
| **10** | `"This circuit breaker is suitable for distribution protection."` | Unhyphenated `circuit breaker`; literal Chinese calque (`suitable for distribution protection`) | `IEC 60947-2:2024 Cl. 3.1` (P19); `07` §5; `SKILL.md` §3.1 & §7.9 | `This circuit-breaker is suitable for power distribution protection.` *(or Track 1 catalogue phrasing: `This moulded-case circuit-breaker is designed for power distribution circuit protection.`)* |

---

### Detailed Audit Notes

#### Finding 1 — Line 1: US Spelling & Unhyphenated Device Noun
- **Quoted source**: `"NXM-250S Molded Case Circuit Breaker (IEC 60947-2)."`
- **Diagnosis**:
  1. `Molded` is North American `UL 489` spelling. `IEC 60947-2:2024` enforces British spelling (`moulded case` in `Cl. 9.3.3.3`, `moulding` in `Cl. 8.1.6`; 0 occurrences of `molded`).
  2. `Circuit Breaker` omits the hyphen. `IEC 60947-2:2024` uses hyphenated `circuit-breaker` (`Cl. 3.1`, P19; 667 occurrences vs 3 unhyphenated). Unhyphenated `Molded Case Circuit Breaker` is restricted exclusively to North American `UL 489` columns (`TRM-DON-020`, `07` §5).
  3. The series code `NXM-250S` is correctly preserved unchanged (`TRM-DON-009`).
- **Suggested fix**: `NXM-250S Moulded-Case Circuit-Breaker (IEC 60947-2)` *(in running text: `moulded-case circuit-breaker (MCCB)`). Confirm whether the product's test reports cover Edition 6.0 before appending `:2024`.*

#### Finding 2 — Lines 2–5: Systematic Unit-Spacing Violations
- **Quoted source**: `"250A"`, `"800V"`, `"8kV"`, `"36kA"`, `"415V"`
- **Diagnosis**: Every numeric rating in Lines 2–5 concatenates the number directly onto its physical unit, violating `SKILL.md` §4, `01_universal_iec_parameters.md` §4, and `07_universal_anti_chinglish.md` §4 (mandatory single half-width space between value and unit).
- **Suggested fix**: `250 A`, `800 V`, `8 kV`, `36 kA`, `415 V`.
- **Additional check on Line 3 & Line 4**: Parameter terms `Rated insulation voltage Ui` (`Cl. 5.3.2.2`, P24) and `Rated impulse withstand voltage Uimp` (`Cl. 5.3.2.3`, P24; correctly avoids *"impact"*) are standard-compliant.

#### Finding 3 — Lines 5–6: Breaking Capacity Naming, Qualifications & Claim Scope
- **Quoted source**: `"Ultimate breaking capacity Icu: 36kA at 415V."` and `"Service breaking capacity Ics: 100% Icu."`
- **Diagnosis**:
  1. In narrative specification lines, the normative `IEC 60947-2:2024` names are **`Rated ultimate short-circuit breaking capacity (Icu)`** (`Cl. 5.3.6.2.2`, P25) and **`Rated service short-circuit breaking capacity (Ics)`** (`Cl. 5.3.6.2.4`, P26). Short forms (`Ultimate breaking capacity` / `Service breaking capacity`) are acceptable as compact Track 1 catalogue table headers only when paired with voltage kind and frequency (e.g. `Ultimate breaking capacity Vac 50/60 Hz`, `06` §3).
  2. Line 5 omits current kind (`AC` vs `DC`), rated frequency (`Cl. 5.3.4`, `Table 4` item 2.8), and the `rms` qualifier (`01` §1: `kA rms`). Do not insert `AC`, `50/60 Hz`, or `rms` without verifying against the `NXM-250S` datasheet.
  3. Line 6 writes `100% Icu` instead of the idiomatic IEC expression **`100 % of Icu`** (or `100% of Icu` in compact layouts; `IEC 60947-2:2024 Cl. 5.3.6.2.4` expresses the minimum ratio as a percentage *of* `Icu`, `≥ 25 % of Icu`). Per `06` §2 (`CLM-001`), confirm from the datasheet that `100 % of Icu` applies specifically to `NXM-250S` at `415 V` and do not extrapolate it to other voltages or models.
- **Suggested fix**:
  - `Rated ultimate short-circuit breaking capacity Icu: 36 kA at 415 V` *(append `rms`, `AC`, and rated frequency once verified from the datasheet)*
  - `Rated service short-circuit breaking capacity Ics: 100 % of Icu`

#### Finding 4 — Lines 7–8: Forbidden Term `durability`, Chinglish Unit `times`, and Datasheet Verification
- **Quoted source**: `"Mechanical durability: 20000 times."` and `"Electrical durability: 8000 times."`
- **Diagnosis**:
  1. **`durability` has 0 occurrences in `IEC 60947-2:2024`** and must never be attributed to IEC 60947-2 (`01` §2, `07` §5, `08` §0 & §7, `IEC2-CORE-033/034`). The main standard (`Cl. 8.2.4.2` & `Table 7`, P39–40) uses **`operational performance without current`** / **`operational performance with current`** and **`number of operating cycles`** (`operational performance` 40×; `operating cycles` 23×). Where endurance terminology is used in the standard (`Annex M Cl. M.7.2.3 / M.8.11`, P222; `Annex R Cl. R.8.5`), the exact word is **`endurance`** (9×), never `durability`.
  2. **`times`** is a direct Chinglish rendering of the Chinese counter character. Use **`operating cycles`** (or `cycles` / `operations`, `07` §2).
  3. **Number grouping**: Format `20000` and `8000` with an IEC space separator (`20 000`, `8 000`) — or consistent comma separators (`20,000`, `8,000`) if the broader Track 1 catalogue uses comma grouping — rather than ungrouped digits.
  4. **Standard baseline vs manufacturer-declared rating check**: In `IEC 60947-2:2024 Table 7` (P40), the minimum normative requirement for `100 A < In ≤ 315 A` is `7 000` cycles without current and `1 000` cycles with current (`8 000` total cycles at `120` cycles/h). Because `20 000` and `8 000` exceed the `Table 7` test floor, they represent manufacturer-declared product ratings; retain them as draft values pending `NXM-250S` datasheet verification and never conflate them with standard minimums (`SKILL.md` §2).
- **Suggested fix**:
  - Strict `IEC 60947-2:2024 Cl. 8.2.4.2 / Table 7` wording:
    - `Operational performance without current: 20 000 operating cycles`
    - `Operational performance with current: 8 000 operating cycles`
  - Acceptable Track 1 catalogue compact form (harmonized with `Annex M.8.11` / `R.8.5`):
    - `Mechanical endurance: 20 000 operating cycles`
    - `Electrical endurance: 8 000 operating cycles`

#### Finding 5 — Line 9: Protection Setting Terminology, Range Tilde `~`, and Multiplier Formatting
- **Quoted source**: `"Overload setting Ir: 0.7~1.0In. Short-time pickup Isd: 2~10Ir. Instantaneous pickup Ii: 5~10In."`
- **Diagnosis**:
  1. **US vs IEC setting nomenclature (`08` §2.3, `IEC2-CORE-050/051/052`)**:
     - `Overload setting Ir` → exact `IEC 60947-2:2024 Cl. 3.16` (P22) & `Table K.1` term is **`Overload current setting (Ir)`**.
     - `Short-time pickup Isd` → unhyphenated `pickup` is North American `UL 489` style (`Short-Time Pickup`). Exact `IEC 60947-2:2024 Cl. 3.17` (P22) & `Table K.1` term is hyphenated **`Short-time pick-up current setting (Isd)`**.
     - `Instantaneous pickup Ii` → North American `UL 489` style (`Instantaneous Pickup Setting`). Exact `IEC 60947-2:2024 Cl. 3.15` (P22) & `Table K.1` term is **`Instantaneous short-circuit current setting (Ii)`**.
  2. **CJK range tilde `~`**: Using `~` as a numeric range separator (`0.7~1.0`, `2~10`, `5~10`) is non-standard in English technical writing and collides with the IEC symbol `~` for alternating current (AC). Replace with **`to`** or an en-dash **`–`**.
  3. **Multiplier and symbol spacing**: Concatenating numerals directly to `In` / `Ir` (`1.0In`, `10Ir`, `10In`) violates unit/symbol spacing and omits the multiplication operator `×` (`08` §2.3, `IEC2-CORE-050/051/052`). Write `(0.7 to 1.0) × In`, `(2 to 10) × Ir`, and `(5 to 10) × In`.
  4. **Technical consistency flag (verify from datasheet)**: Presence of `Isd` implies a short-time delay short-circuit release (`Cl. 3.8`, typical of electronic overcurrent releases / ETUs under `Annex F`), yet neither the release type nor the associated time settings (`tr`, `tsd`, `ti` per `Fig. K.1`) are stated. Confirm from the `NXM-250S` datasheet whether `Isd` genuinely applies to this model and obtain the time-delay values.
- **Suggested fix**:
  `Overload current setting Ir: (0.7 to 1.0) × In. Short-time pick-up current setting Isd: (2 to 10) × Ir. Instantaneous short-circuit current setting Ii: (5 to 10) × In.`

#### Finding 6 — Line 10: Hyphenation & Track 1 Catalogue Phrasing
- **Quoted source**: `"This circuit breaker is suitable for distribution protection."`
- **Diagnosis**:
  1. `circuit breaker` must be hyphenated as **`circuit-breaker`** (`IEC 60947-2:2024 Cl. 3.1`, `07` §5).
  2. `"suitable for distribution protection"` is an overly literal translation of the Chinese application phrase and reads abruptly in an international Track 1 catalogue (`SKILL.md` §3.1 & §7.9). Clarifying it to `"power distribution protection"` or `"power distribution circuit protection"` improves naturalness without introducing unverified product claims (such as motor protection, isolation suitability, or IT-system suitability).
- **Suggested fix**:
  - Faithful minimal fix: `This circuit-breaker is suitable for power distribution protection.`
  - Idiomatic Track 1 catalogue alternative: `This moulded-case circuit-breaker is designed for power distribution circuit protection.`

---

## 5. Terminology Alignment Reference Table

| Chinese Source | Quoted Draft Text | Audit Status | Mandatory IEC 60947-2:2024 English (Track 1) | North American (`UL 489`) Reference Only | Normative / Dictionary Basis |
| :--- | :--- | :---: | :--- | :--- | :--- |
| 塑壳断路器 | `"Molded Case Circuit Breaker"` | ❌ Non-compliant | **Moulded-case circuit-breaker (MCCB)** | Molded Case Circuit Breaker (MCCB) | `IEC 60947-2:2024 Cl. 3.1`, `9.3.3.3`; `TRM-DON-020` |
| 断路器 | `"circuit breaker"` | ❌ Non-compliant | **circuit-breaker** | Circuit Breaker | `IEC 60947-2:2024 Cl. 3.1` (667× vs 3×); `IEC2-CORE-001` |
| 壳架等级 / 壳架电流 | `"Frame size: 250A"` | ⚠️ Spacing only (term ✅) | **Frame size** (`250 A`) *(note: `Inm` is `GB/T 14048.2` only)* | Frame Size Rating | `IEC 60947-2:2024 Cl. 3.1.1` (28×; `Inm` 0×); `TRM-DON-019`; `IEC2-CORE-002` |
| 额定绝缘电压 | `"Rated insulation voltage Ui: 800V"` | ⚠️ Spacing only | **Rated insulation voltage ($U_i$)** (`800 V`) | Rated Insulation Voltage | `IEC 60947-2:2024 Cl. 5.3.2.2`; `IEC2-CORE-021` |
| 额定冲击耐受电压 | `"Rated impulse withstand voltage Uimp: 8kV"` | ⚠️ Spacing only | **Rated impulse withstand voltage ($U_{\text{imp}}$)** (`8 kV`) | Rated Impulse Withstand Voltage | `IEC 60947-2:2024 Cl. 5.3.2.3`; `IEC2-CORE-022` |
| 额定极限短路分断能力 | `"Ultimate breaking capacity Icu: 36kA at 415V"` | ⚠️ Spacing & qualification | **Rated ultimate short-circuit breaking capacity ($I_{\text{cu}}$)** *(table header: `Ultimate breaking capacity Vac 50/60 Hz`)* | Short-Circuit Interrupting Rating (AIR) | `IEC 60947-2:2024 Cl. 5.3.6.2.2`, `3.11.1`; `06` §3; `IEC2-CORE-028` |
| 额定运行短路分断能力 | `"Service breaking capacity Ics: 100% Icu"` | ⚠️ Full name & `% of Icu` | **Rated service short-circuit breaking capacity ($I_{\text{cs}}$)** (`100 % of Icu`) | Service Interrupting Capacity | `IEC 60947-2:2024 Cl. 5.3.6.2.4`, `3.11.3`; `06` §3; `IEC2-CORE-030` |
| 机械寿命 / 无载操作循环次数 | `"Mechanical durability: 20000 times"` | ❌ Non-compliant | **Operational performance without current** (`20 000 operating cycles`) / **Mechanical endurance** (`Annex M/R`) | Mechanical Operations / Mechanical Endurance | `IEC 60947-2:2024 Cl. 8.2.4.2`, `Table 7`, `M.8.11`, `R.8.5` (`durability` 0×); `IEC2-CORE-033` |
| 电气寿命 / 带载操作循环次数 | `"Electrical durability: 8000 times"` | ❌ Non-compliant | **Operational performance with current** (`8 000 operating cycles`) / **Electrical endurance** (`Annex M`) | Electrical Operations under Load | `IEC 60947-2:2024 Cl. 8.2.4.2`, `Table 7`, `M.8.11` (`durability` 0×); `IEC2-CORE-034` |
| 过载整定电流 | `"Overload setting Ir: 0.7~1.0In"` | ❌ Range/multiplier & shortened term | **Overload current setting ($I_r$)** (`(0.7 to 1.0) × In`) | Long-Time Pickup Setting | `IEC 60947-2:2024 Cl. 3.16`, `Table K.1`; `IEC2-CORE-051` |
| 短延时起动电流整定值 | `"Short-time pickup Isd: 2~10Ir"` | ❌ US `pickup`, range & multiplier | **Short-time pick-up current setting ($I_{\text{sd}}$)** (`(2 to 10) × Ir`) | Short-Time Pickup Setting | `IEC 60947-2:2024 Cl. 3.17`, `Table K.1`; `IEC2-CORE-052` |
| 瞬时短路整定电流 | `"Instantaneous pickup Ii: 5~10In"` | ❌ US `pickup`, range & multiplier | **Instantaneous short-circuit current setting ($I_i$)** (`(5 to 10) × In`) | Instantaneous Pickup Setting | `IEC 60947-2:2024 Cl. 3.15`, `Table K.1`; `IEC2-CORE-050` |

---

## 6. Suggested Clean Reference Version (Audit Proposal Only — No Unprovided Values Added)

> **Note**: Presented strictly as a reference consolidation of the Mode B modification recommendations above, retaining **only** the numerical values present in the draft. It is **not** ready for final catalogue publication until the missing datasheet items in Section 7 are confirmed and supplied.

> NXM-250S Moulded-Case Circuit-Breaker (IEC 60947-2).
> Frame size: 250 A.
> Rated insulation voltage Ui: 800 V.
> Rated impulse withstand voltage Uimp: 8 kV.
> Rated ultimate short-circuit breaking capacity Icu: 36 kA at 415 V.
> Rated service short-circuit breaking capacity Ics: 100 % of Icu.
> Operational performance without current: 20 000 operating cycles *(catalogue short form: Mechanical endurance: 20 000 operating cycles)*.
> Operational performance with current: 8 000 operating cycles *(catalogue short form: Electrical endurance: 8 000 operating cycles)*.
> Overload current setting Ir: (0.7 to 1.0) × In. Short-time pick-up current setting Isd: (2 to 10) × Ir. Instantaneous short-circuit current setting Ii: (5 to 10) × In.
> This moulded-case circuit-breaker is designed for power distribution circuit protection.

---

## 7. Missing Mandatory Parameters & Datasheet Verification Checklist (Not Filled In)

Per `chint-translation` §1 (Value Slot Convention) and `IEC 60947-2:2024 Cl. 6.2 / Table 4` (P30–32), the following parameters are absent from or under-specified in the draft. None have been inferred or filled in; each must be confirmed from the official `NXM-250S` product datasheet before publication:

1. **Rated current ($I_n$)** (`Cl. 5.3.3.3`, `Table 4` item 1.1): The draft supplies `Frame size: 250 A` (highest rating of the frame group per `Cl. 3.1.1`) and expresses `Ir` and `Ii` as multiples of `In`, yet never states the actual rated current range or discrete ratings `In` available for `NXM-250S`.
2. **Rated operational voltage ($U_e$), current kind (AC/DC), and rated frequency** (`Cl. 5.3.2.1`, `Cl. 5.3.4`, `Table 4` items 2.5 & 2.8): Confirm whether `415 V` is AC, state the full set of `Ue` values and rated frequency (e.g. `50/60 Hz`), and verify whether `Icu` should be annotated as `kA rms`.
3. **Number of poles & neutral pole configuration** (`Cl. 8.1.7`, `Table 4` item 2.20): Confirm pole options (e.g. 3P / 4P) and whether the neutral pole is protected or unprotected.
4. **Selectivity category (`Category A` or `Category B`) and $I_{\text{cw}}$** (`Cl. 4.1`, `Cl. 5.4`, `Cl. 5.3.6.4`, `Table 2`, `Table 4` items 2.4 & 2.12): Required by `Table 4`; if `Category B` (or `Category A` with assigned $I_{\text{cw}}$), supply rated short-time withstand current $I_{\text{cw}}$ and its intentional short-time delay (`≥ 0.05 s`).
5. **Release / trip unit type and time settings ($t_r$, $t_{\text{sd}}$, $t_i$)** (`Cl. 3.8`, `Cl. 3.15–3.17`, `Cl. 5.7.1`, `Fig. K.1`, `Table 4` items 2.13–2.16): Confirm whether `NXM-250S` is fitted with a thermal-magnetic overcurrent release (TM) or an electronic overcurrent release / electronic trip unit (ETU), verify whether `Isd` applies to this specific `NXM-250S` variant, and supply the corresponding time-delay values.
6. **Rated short-circuit making capacity ($I_{\text{cm}}$) and individual-pole $I_{\text{cu1}}$** (`Cl. 5.3.6.1`, `Table 1`; `Cl. 5.3.6.2.3`, `Cl. 9.3.11`, `Table 4` item 2.11): Confirm $I_{\text{cm}}$ (peak value) and whether $I_{\text{cu1}}$ differs from $I_{\text{cu}}$ (mandatory marking if $I_{\text{cu1}} \neq I_{\text{cu}}$).
7. **Installation, isolation, environmental & power-loss specifications** (`Cl. 4.4–4.5`, `Cl. 5.7.3`, `Cl. 6.1`, `Cl. 7`, `Cl. 8.1.3`, `Annex G`, `Table 4` items 1.2, 2.6, 2.17, 3.1): Confirm method of installation (fixed / plug-in / withdrawable), suitability for isolation, IT-system applicability (or crossed-out `IT` marking), IP degree of protection, reference ambient air temperature (if other than `+30 °C`), pollution degree, and typical power loss per pole / frame size.
8. **Datasheet verification of draft ratings & standard edition**:
   - Confirm that `Ics = 100 % of Icu` holds for `NXM-250S` at `415 V` (`CLM-001` scope verification).
   - Confirm manufacturer-declared `20 000` (without current) and `8 000` (with current) operating cycles against the `NXM-250S` datasheet (exceeding `Table 7` test floor for `100 A < In ≤ 315 A`).
   - Confirm whether `NXM-250S` type-test certificates cover `IEC 60947-2:2024` (Edition 6.0) or an earlier edition before adding a publication year to `(IEC 60947-2)`.

---

## 8. Completion Gate Self-Check

- [x] **No unresolved slots**: Zero unresolved template slot placeholders appear anywhere in this deliverable.
- [x] **No fabricated ratings**: Every product rating cited in proposed edits comes verbatim from the draft; missing parameters are listed in Section 7 without filling in values.
- [x] **Direction honoured (`SKILL.md` §3.2–3.3)**: ZH→EN Mode B audit delivered in English; Chinese appears strictly in the `Chinese Source` column of Section 5.
- [x] **Track 1 IEC 60947-2:2024 orthography consistent**: Single-track British spelling (`moulded-case`, `catalogue`), `-ize` verbs (`standardization`), mandatory hyphenation (`circuit-breaker`, `short-time pick-up`), and half-width unit spacing enforced throughout; US spellings isolated strictly to quoted draft text and the `North American (UL 489)` reference column.
- [x] **Exact standard citations**: Every finding and the `Frame size` vs `Inm` verification trace directly to verified `IEC 60947-2:2024` clauses, tables, and printed pages.
