# Rule Source Map (`sources.md`)

Deterministic rules cite their normative source here; rule data carries an optional `source` field. Standards are referenced by number and clause, never copied wholesale.

A rule is only listed under a standard when the standard's own text supports it. Corpus-derived calibration (word choice validated against peer catalogues) is documented in §3 and never attributed to a standard.

## 1. Language & Notation

| Standard | Rules | Where | Embedding boundary |
| :--- | :--- | :--- | :--- |
| **GF 1001—2001**《第一批异形词整理表》 | Only two entries: `连接—联接` (recommend 连接) and `联结—连结` (recommend 联结). 联结 means "bind/associate" and is *not* interchangeable with 连接. | `catalog_rules.json` → `cross_page_synonyms` where `source` names GF 1001 | Encoded pair-by-pair after checking the official 338-group table. The table contains no 锁/讯/它 entries — 联锁/连锁, 通信/通讯, 其他/其它 are NOT GF 1001 pairs and must not be tagged as such. |
| **GB/T 15835—2011**《出版物上数字用法》 | Two rules only: (a) 5.1.3 numeric ranges use `～` or `—`, not `-`; (b) 5.1.3 percent ranges carry `%` on both ends (`15％～30％`, not `15～30％`). 5.1.1 also permits space-grouped thousands (`12 500～20 000`), so grouping must not split a bound. | `catalog_rules.json` → `case_notation` (hyphen-range, percent-range); `audit_catalog.py` → `_NUM_GROUP` | Rule behavior only. Note: this standard does **not** govern magnitude ordering — inverted-range detection (`NUMERIC_RANGE`) is an internal sanity check, not a GB/T 15835 requirement. |
| **GB/T 15834—2011**《标点符号用法》 | 4.8 quotation-mark pairing; 4.9 bracket pairing principle; 4.13.3 `-` for 号码/型号, 一字线/浪纹线 for 数值范围 | `catalog_rules.json` → `zh_typos` `“黑色“`; `audit_catalog.py` → `BRACKET_UNBALANCED`; `case_notation` hyphen-range | The standard supplies the pairing principle only. All suppressions (list markers `1)`, footnote tails `ETU15B1)`, lone trailing `)`) are corpus-derived — see §3. |
| **SI Brochure, 9th ed. (BIPM, CC BY 4.0)** | Unit symbols and prefixes: `kV`/`kW`/`kA`/`kVA`/`kvar`/`kWh`/`kHz`/`MHz`/`Hz`/`mA` | `catalog_rules.json` → `case_notation` | CC BY 4.0: attribution + change notice when text is reused. |
| **ISO 80000-2** | Power factor symbol `cos φ` | `catalog_rules.json` → `case_notation` | Symbol only. |
| **Unicode UCD / East Asian Width** | Full-width vs half-width characters, character properties | Future normalization layer (`NFKC` in `load_units`) | Unicode License: permissive, keep notice. |
| **《现代汉语词典》** | Standard word forms and word-boundary judgements: `圆形` over `圆型`; `通信`/`通讯` and `其他`/`其它` treated as **different words**, so those groups are house terminology uniformity, *not* 异形词 — the entries say so explicitly | `catalog_rules.json` → `zh_typos` (圆型), `cross_page_synonyms` (通信/通讯, 其他/其它) | Lexicographic reference, not a normative standard. Citing it for a word *form* is legitimate; citing it for a mandated choice is not, hence the "用语统一" qualifier on the synonym entries. |
| **《通用规范汉字表》** | Simplified standard glyph forms (`部份` → `部分`) | `catalog_rules.json` → `case_notation` | Glyph standard only; it does not govern vocabulary choice. |

## 2. Electrical Terminology & Product Standards

| Standard | Rules | Where | Embedding boundary |
| :--- | :--- | :--- | :--- |
| **GB/T 14048.2—2020** (also IEC 60947-2) | Canonical ZH term table: 分励脱扣器, 过电流脱扣器, 欠电压脱扣器, 闭合脱扣器, 抽出式→抽屉式, 分离位置→隔离位置, 万能式断路器→空气断路器, 塑壳断路器→塑料外壳式断路器, 功率损耗→功耗, 结构差异→结构段, 使用类别 A/B→选择性类别 A/B | `chint-translation/scripts/lint_text.py` → `STD_CONCEPT_ZH` / `STD_STATUTORY_ZH` (live-loaded; builtin parity fallback in `audit_catalog.py`) | Most term fixes cite a GB/T 14048.2—2020 clause; the exceptions are marked inline — `单极极限` has no clause (CHINT extension), `隔离开关` cites IEC 60947-3 / GB/T 14048.3, which is a different standard. |
| **GB/T 2900.18—2008**《电工术语 低压电器》 | `联锁` / `连锁` word choice | `catalog_rules.json` → `cross_page_synonyms` 联锁/连锁 entry | The standard defines `联锁 interlock` as the term; the choice to standardise the whole catalogue on it is a house convention, and the entry says so. No IEC 60050-441 backlink exists in the code — that standard is **not** claimed as a source anywhere. |
| **IEC 60947-2:2024 (Ed. 6.0)** / **GB/T 14048.2—2020** | `Ics ≤ Icu`; `In ≤ Inm`; `Ue ≤ Ui`; Selectivity category A + `Isd` requires `Icw`; obsolete Ed. 5 clause numbers; `Ui`/`Uimp` unit inversion | `audit_catalog.py` → `ICS_RE`/`ICU_RE`/`IN_RE`/`INM_RE`/`UE_RE`/`UI_RE`, category-A block, `ED5_CLAUSE_RE` | `Ics ≤ Icu` (GB 4.3.6.2.3) and `Ue ≤ Ui` (IEC 5.3.4.1 ≤ 5.3.2.2) are standard-derived. `In ≤ Inm` is industry convention: **neither standard defines the symbol `Inm`** — GB/T 14048.2—2020 Cl. 2.1.1 defines 壳架等级 only. |
| **IEC 62423** (GB/T 22794) | `Type F` / `Type B+` must cite IEC 62423, not IEC 60947-2 Annex B | `audit_catalog.py` → `type_fb_re` block | Clause reference only. |
| **GB/T 4208—2017** (IEC 60529) | IP code direction and syntax | Semantic checklist (`不高于/不低于 IPxx`) | Reference only. |

## 3. Corpus-derived calibration (not standards)

`references/catalog_rules.json` → `severity_overrides.downgrade_if_pattern_contains` moves a blacklist pattern from `EN_SEVERE_ERROR` (L1 hard error) to `EN_TERM_CONSISTENCY` (L2 consistency) when the form is valid English or industry-standard at peers.

Evidence base: 81 PDFs under `Areas/竞品分析/data/pdfs` (77 excluding `archive/`), 15 vendor folders, scanned 2026-11-27. Counts below are **occurrence counts** (regex hits across extracted page text), not file counts.

| Form | Peer usage (occurrences) | Verdict |
| :--- | :--- | :--- |
| `withdrawable` | ABB 495, 西门子 124 | canonical, keep as suggested fix |
| `closing release` | ABB 33, 施耐德 10 | canonical, keep as suggested fix |
| `drawer`, `drawer type` | 凯帆 103, 德力西 63 | peer-valid legacy → L2 |
| `closing electromagnet` | 常熟开关 48, 凯帆 25 | peer-valid legacy → L2 |
| `separation position` | 凯帆 28 | peer-valid legacy → L2 |
| `shunt opening release` | ABB 13 | peer-valid legacy → L2 |

Same corpus drove these detector calibrations — each suppressed a peer catalogue's legitimate typography:

- **Numeric range**: clock spans (`00:00~24:00`), grouped thousands (`630~2,000AF`, `12 500～20 000`), zero bounds, and relative multiples (`40 ～ 1.2In`) are not inverted ranges.
- **Bracket pairing**: enumerated markers (`1)`, `a)`, `1a)`, `509)`), superscript footnote refs glued to text (`ETU15B1)`), and a lone trailing `)` are typography, not unmatched brackets.
- **Duplicated words**: hyphenated line breaks (`under under-`) and cross-case product names (`Formula AIR air circuit-breakers`) are not duplicates.

`COMPETITOR_CODE` fires only against CHINT-specific accessory codes (Schneider/ABB `MX`/`XF`/`MN`/`SDE`/`MCH`/`KLC`). Pass `--external-reference` when auditing a peer catalogue (or `--dept mccb` on a non-ACB document); the scanner also auto-suppresses `COMPETITOR_CODE` when the first 400 units contain zero CHINT identifiers and ≥3 peer brand mentions, while preserving checks on CHINT catalogues that merely cite a competitor once or twice.

## 4. Rules deliberately not encoded

- Full GF 1001 table, GB/T 15834/15835 full text, IEC/GB clause lists: require the official documents and licensing review; encode derived behavior with `source` fields instead.
- Competitor codes (Schneider/ABB/Siemens): internal detection only; never publish comparative lists.

## 5. Extension protocol

1. Add the rule entry with `source` (standard number + clause/table). If the rule has no standard basis, omit `source` — never invent one.
2. Verify the source against the official document; record the checked edition.
3. Add a positive and a clean negative fixture to `--self-test` / `evals.json`. The negative fixture must be a string the rule is expected to leave alone.
4. Never copy standard prose into the repository.
