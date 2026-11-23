# CHINT NZ7 Series Automatic Transfer Switch (ATS) — Manual Excerpt Translation

- **Translation Direction**: ZH → EN (Mode A: Direct Translation)
- **Linguistic Register**: Track 2 — OEM Manual Register (Installation and Operation Manual), aligned with IEC 60947-2:2024 British spelling and hyphenation
- **Applicable Standards**: `IEC 60947-6-1` (Multiple function equipment — transfer switching equipment (TSE)); domestic counterpart `GB/T 14048.11` *(North American counterpart for reference only: `UL 1008`)*

---

## English Translation (Track 2 — OEM Manual Register)

### 4.3 Transition Types

This product supports two transition types: open transition (Break-Before-Make, BBM) and closed transition (Make-Before-Break, MBB). During closed transition, the momentary paralleling time of the two power sources does not exceed 100 ms. The total operating time (transfer time) is not greater than 1.5 s, and the return transfer delay (RTD) can be set within the range of 0 s to 180 s.

### 4.4 Mechanical Interlock

The mechanical interlocking mechanism shall ensure that the two power sources cannot be closed simultaneously.

---

## Terminology Mapping

| Chinese Source | Standard English Term (Track 2 / IEC 60947-6-1) | Standard Basis & Guardrail Note |
| :--- | :--- | :--- |
| 双电源自动转换开关（ATS） | Automatic Transfer Switch (ATS) / Automatic Transfer Switching Equipment (TSE) | `IEC 60947-6-1` / `GB/T 14048.11`. Avoid literal wording such as "dual power auto switch". Keep the series code `NZ7` unchanged. |
| 转换方式 | Transition Types | Standard `IEC 60947-6-1` classification for BBM / MBB switching modes. |
| 先断后通（BBM） | Open transition (Break-Before-Make, BBM) | Primary source disconnects completely before the alternate source connects; no phase-synchronisation risk. |
| 先通后断（MBB） / 闭路转换 | Closed transition (Make-Before-Break, MBB) | Momentary paralleling of dual sources without power interruption during transfer. |
| 短时并列时间 | Momentary paralleling time | Product-specific closed-transition window; avoid literal "short-time parallel connection time". |
| 转换动作时间 | Total operating time (transfer time) | Time interval from initiation of switching to final contact closure on the alternate source; avoid literal "switching action time". |
| 恢复转换延时 | Return transfer delay (RTD) | Adjustable delay before automatic return to the primary supply after restoration. |
| 机械联锁 / 机械联锁机构 | Mechanical interlock / Mechanical interlocking mechanism | Physical interlocking mechanism preventing simultaneous closure of normal (Source I) and alternate/emergency (Source II) supplies. Do not assume cable-interlock construction unless specified. |
| 同时合闸 | Closed simultaneously / Simultaneous closing | Standard switchgear closing terminology; avoid conversational phrases such as "turned on at the same time". |

---

## Value, Formatting & Register Notes

1. **Standard vs. Datasheet Attribution (No Fabricated Ratings)**: `IEC 60947-6-1` defines transfer switching equipment classes (Class PC and Class CB) and transition types (BBM / MBB), not fixed operating times or delay limits. The three numeric quantities (`100 ms`, `1.5 s`, and `0 s to 180 s`) are product-specific characteristics carried strictly from the provided NZ7 manual excerpt and must trace to the official NZ7 product datasheet. No unstated parameters—such as Class PC / Class CB classification, rated operational voltage, rated current, short-time withstand current, or synchronising tolerances—have been inferred or added.
2. **Unit Spacing & Punctuation**: A single half-width space is enforced between every numeric value and its unit (`100 ms`, `1.5 s`, `0 s to 180 s`). The Chinese range tilde and full-width punctuation from the source have been replaced with standard English range notation (`0 s to 180 s`) and half-width punctuation.
3. **Track 2 Register Fidelity**: Written in normative, concise OEM installation-and-operation manual prose (`does not exceed`, `is not greater than`, `can be set`, `shall ensure`) aligned with numbered manual clauses (`4.3`, `4.4`), preserving original modal force without introducing Track 1 catalogue marketing phrasing or North American spellings.
