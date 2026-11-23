# ACB Accessories Catalogue Translation (ZH → EN)

- **Translation Direction**: ZH → EN
- **Product Category**: Air Circuit-Breaker (ACB) Accessories
- **Linguistic Register**: Track 1 — IEC Global Catalogue Register (`IEC 60947-2:2024`, Edition 6.0)
- **Operating Mode**: Mode A — Direct Translation

---

## English Translation (Track 1: IEC Global Catalogue Register)

**Shunt Release (SHT / MX)**
Remotely opens the circuit-breaker. Operating voltage range: 70% to 110% of the rated control supply voltage (Us); opening time not exceeding 50 ms. Both the closing release (CC / CEM) and the shunt release operate in pulse energization working mode; ensure that the pulse time t1 is not less than 200 ms and the energization interval t2 is greater than 15 s.

**ACB Key Lock (KLC)**
Three locks and two keys configuration. On-site installation requires cutting a Ø 28 mm mounting cutout in the enclosure door using a panel hole saw or hole punch.

---

## Terminology & Register Notes

| Chinese Source | Track 1 IEC Catalogue Term | Standard Basis | Excluded Forms (Track 2 OEM / UL / Forbidden) |
| :--- | :--- | :--- | :--- |
| 分励脱扣器 | **Shunt release (SHT / MX)** | `IEC 60947-2:2024` Cl. 5.7.1, Cl. 8.2.1.2.3 | Forbidden: `Excitation release`, `Shunting release`, `Shunt opening release`; North American / UL only: `Shunt Trip (ST)` |
| 断路器 | **circuit-breaker** | `IEC 60947-2:2024` Cl. 3.1 | North American / UL only: unhyphenated form |
| 额定控制电源电压 | **rated control supply voltage (Us)** | `IEC 60947-2:2024` Cl. 5.5.1 (`Uc`), Cl. 5.7.2, Table 3 | Literal paraphrases; no assumed voltage rating added |
| 动作时间 | **opening time** | `IEC 60947-2:2024` Cl. 3.12 | Literal: `action time` |
| 闭合电磁铁 | **Closing release (CC / CEM)** *(admitted synonym: closing coil)* | `IEC 60947-2:2024` Cl. 3.19, Cl. 5.7.1 | Track 2 OEM manual: `Closed electromagnet (CEM)`; Forbidden: `Close electromagnet`, `Closing magnet` |
| 脉冲通电工作制 | **pulse energization working mode** | `IEC 60947-2:2024` (`-ize` orthography) & Archetype 6 | British `-ise` variant (`energisation`), which does not appear in `IEC 60947-2:2024` |
| 断路器本体钥匙锁 | **ACB Key Lock (KLC)** / **circuit-breaker key lock** | `IEC 60947-2:2024` Cl. 3.10 (lock-out device preventing closing) | Track 2 OEM manual: `Keys and locks (KL)`; Forbidden: `Body key lock` |
| 3 把锁 2 把钥匙配置 | **Three locks and two keys configuration** | Archetype 5 (combinatorial key-lock scheme) | Literal: `3 locks 2 keys matching` |
| 开孔器 | **panel hole saw or hole punch** | Track 1 catalogue standard | Track 2 OEM manual: `hole opener` |

- **Register Separation**: All copy stays strictly within Track 1 (IEC Global Catalogue Register), avoiding Track 2 OEM manual phrasing (`Closed electromagnet`, `Keys and locks (KL)`, `hole opener`) and North American UL terminology (`Shunt Trip`).
- **IEC Orthography**: Applies `IEC 60947-2:2024` hyphenation (`circuit-breaker`) and British/IEC spelling (`catalogue`, plus standard-mandated `-ize` in `energization`).

---

## Numeric, Unit & Value-Slot Handling Notes

- **Mandatory Half-Width Unit Spacing**: Exactly one half-width space is inserted between each numeric value and its SI unit (`50 ms`, `200 ms`, `15 s`, `28 mm`), normalizing the unspaced source typography.
- **Range, Symbol & Punctuation Normalization**: The Chinese tilde range is rendered as `70% to 110%`; the source Greek phi diameter prefix is converted to the ISO diameter sign `Ø` (`Ø 28 mm`); all Chinese full-width punctuation is replaced with half-width English punctuation.
- **Value-Slot Fidelity**: Every numeric quantity in the deliverable (`70% to 110%`, `50 ms`, `200 ms`, `15 s`, `three locks and two keys`, `Ø 28 mm`) is taken directly from the source text. No unstated ratings (such as specific control voltage values, frame sizes, series designations, or power consumption) were invented or inherited, and zero unresolved value slots remain.
