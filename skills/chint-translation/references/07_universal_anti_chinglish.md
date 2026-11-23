# Anti-Chinglish Industrial Catalogue Dictionary & False Friends

Aligned with **IEC 60947-2:2024 (Edition 6.0)** single-track Oxford/British spelling (`-our`/`-ou-`/`-re`/`-ll-` + ISO/IEC `-ize` verbs/nouns such as `utilization`, `energize`) and hyphenation across Track 1 (IEC Global Catalogue) and Track 2 (OEM Manual).

## 0. Scope Note

This file is a **terminology dictionary**, not a specification table. It contains no product ratings.
Where a runtime value appears inside an example (operation counts, thresholds), it is a **number-formatting example only** and is written as a slot `{{param: unit}}`; it must never be read as a product attribute.

---

## 1. High-Frequency Forbidden Terms & Anti-Hallucination Guardrails

| Code | Chinese Term | ❌ Strictly FORBIDDEN Translation | ✅ Mandatory Professional English | Standard Rationale |
| :--- | :--- | :--- | :--- | :--- |
| **TRM-DON-001** | 万能式断路器 | ❌ `Universal Breaker ❌` | ✅ **Air Circuit-Breaker (ACB)** *(IEC Global / OEM)* / **Low-Voltage Power Circuit Breaker (LVPCB, UL 1066)** *(North America)* | 万能式断路器中的"万能"指多功能通用，属于全球行业品类词；IEC 60947-2:2024 正文仅统一使用连字符 `circuit-breaker`（667 vs 3，`Cl. 3.1`），不按 ACB/MCCB 命名，ACB 沿用标准连字符 `air circuit-breaker`；非连字符 `Circuit Breaker` 仅限北美 UL 1066 / ANSI 语境 |
| **TRM-DON-002** | 闭合电磁铁 | ❌ `Close electromagnet / Closing magnet ❌` | ✅ **Closing release (closing coil) (CC / CEM)** *(IEC 60947-2:2024 Cl. 3.19)* / **Closed electromagnet (CEM)** *(OEM manual Track 2 legacy 1:1 compatibility only)* | IEC 60947-2:2024 Cl. 3.19 标准术语为 `closing release`（允许同义词 `closing coil`）；`Closed electromagnet (CEM)` 仅限既有 OEM 印刷手册 1:1 维护兼容（新编手册应优先使用 Track 1）；严禁误写为动词原形 close electromagnet 或 closing magnet |
| **TRM-DON-003** | 分励脱扣器 | ❌ `Excitation release / Shunting release / Shunt opening release ❌` | ✅ **Shunt release (SHT / MX / YO)** *(IEC 60947-2:2024 Cl. 5.7.1)* / **Shunt Trip (ST)** *(North America / UL)* | IEC 60947-2:2024 统一术语为 `shunt release`（25 次，`shunt opening release` 0 次），北美 UL 为 `Shunt Trip`；严禁误译为 Excitation release 或中式英语 Shunting release |
| **TRM-DON-004** | 欠电压脱扣器 | ❌ `Lack voltage trip ❌` | ✅ **Undervoltage release (UVR / MN)** *(IEC 60947-2:2024 Cl. 5.7.1 & 8.2.1.2.2)* / **Undervoltage trip (UVT / UVTR)** *(OEM manual Track 2)* | IEC 60947-2:2024 主流拼写为无连字符 `undervoltage`（36 vs 4 `under-voltage`）；Track 1 与 Track 2 统一采用 `Undervoltage` |
| **TRM-DON-005** | 抽屉座 | ❌ `Drawer box / Slide box ❌` | ✅ **Cradle / Withdrawable chassis / Withdrawable sub-base** *(IEC)* / **Drawer seat** *(OEM manual legacy 1:1 compatibility only)* / **Drawout chassis** *(international commercial / UL synonym)* | IEC 60947-2:2024 术语为 `withdrawable`（18 次；Fig. J.1 亦作 `draw-out cradle`）；`Drawout chassis` 属合规国际商业及北美 UL 同义词，`Drawer seat` 仅限旧版 OEM 手册 1:1 维护；严禁直译 Drawer box / Slide box |
| **TRM-DON-006** | 相间隔板 | ❌ `Phase space plate ❌` | ✅ **Interphase barrier / Phase barrier** *(catalogue)* / **Interphase partition** *(OEM manual)* | 电气绝缘隔板的标准英文为 Interphase barrier 或 Phase barrier |
| **TRM-DON-007** | 门框 / 柜门面罩 | ❌ `Face mask ❌` | ✅ **Door escutcheon (Door flange)** *(catalogue)* / **Door Frame and Pad** *(OEM manual Track 2)* | 配合柜门开孔密封的构件译为 Door escutcheon / Door flange（样本）或 Door Frame and Pad（OEM 手册） |
| **TRM-DON-008** | 区域选择性联锁 | ❌ `Area select lock ❌` | ✅ **Zone Selective Interlocking (ZSI)** | 专有技术缩写与名称必须严格写作 Zone Selective Interlocking (ZSI) |
| **TRM-DON-009** | 品牌系列名 (产品线命名) | ❌ literal transliteration of the brand line ❌ | ✅ **the series designation registered in the target market** | 产品线名一律使用该市场已注册的系列代号；不音译、不意译品牌词 |
| **TRM-DON-010** | 抽屉式 (断路器/安装) | ❌ `Drawer / Drawer type ❌` | ✅ **Withdrawable / Withdrawable circuit-breaker** *(IEC 60947-2:2024 Cl. 3.5 & Cl. 4.4)* / **Drawout / Drawout type** *(international commercial / UL synonym)* | IEC 60947-2:2024 首选 `withdrawable`（18 次）；`Drawout` 属国际商业样本（如 Schneider）及北美 UL 的合规同义词，非中式英语；严禁译为 `Drawer` / `Drawer type` |
| **TRM-DON-011** | 电动操作机构 (电操) | ❌ `Operating device / Motor hand ❌` | ✅ **Motor-operator / Motor operator device (MOD) / Motor mechanism** | IEC 60947-2:2024 Annex N (N.1.1) 使用 `motor-operators`，样本常用 `Motor operator device (MOD)` 或 `Motor mechanism` |
| **TRM-DON-012** | 灭弧室 | ❌ `Interrupter / Arc room ❌` | ✅ **Arc extinction device** *(IEC 60947-2:2024 Cl. 8.1.6)* / **Arc-extinguishing chamber / Arc chute** *(catalogue / OEM)* | IEC 60947-2:2024 Cl. 8.1.6 正文规范用语为 `arc extinction device`（`arc chute` / `arc-extinguishing` 在标准正文 0 次，Cl. 8.1.5 规范操作人员电弧颗粒防护）；样本与手册常用 `Arc-extinguishing chamber` 或 `Arc chute`；严禁使用 Interrupter / Arc room |
| **TRM-DON-013** | 摇手柄存放孔 / 存放槽 | ❌ `Storage hole ❌` | ✅ **Racking handle storage slot / Storage slot** | 抽屉座或面板摇手柄收纳结构标准用词为 storage slot，严禁直译为 storage hole |
| **TRM-DON-014** | 智能控制器 / 控制器 | ❌ `Intelligent controller (literal) ❌` | ✅ **Controller / Electronic Trip Unit (ETU)** | 产品部件及选型标题中直接使用 Controller 或 Electronic Trip Unit，避免中式 redundant wording；整机严禁直译为 `intelligent air circuit-breaker` |
| **TRM-DON-015** | 按钮 (合闸/分闸按钮) | ❌ `Device button / Press key ❌` | ✅ **Pushbutton (Closing / Opening pushbutton)** | 电气开关面板按钮标准术语为 Pushbutton，严禁译为 device button 或 press key |
| **TRM-DON-016** | 分断能力型号 | ❌ `Breaking capacity levels ❌` | ✅ **Breaking capacity type (Type N / Type S / Type H)** | 分断能力等级型号应译为 breaking capacity type，而非 breaking capacity levels |
| **TRM-DON-017** | 指示灯 (如 Ig指示灯) | ❌ `Ig indicator light / lamp ❌` | ✅ **Ig indicator / Status indicator** | 面板指示灯标准术语使用 Indicator（如 Ig indicator），避免多余的 light 或 lamp |
| **TRM-DON-018** | 本体钥匙锁 / 锁具 | ❌ `Body key lock ❌` | ✅ **Circuit-breaker key lock / ACB Key Lock (KLC)** *(catalogue)* / **Keys and locks (KL)** *(OEM manual Track 2)* | 断路器本体锁具严禁直译为 Body key lock；Track 2 OEM 保留 `Keys and locks (KL)`；标准功能见 `circuit-breaker with lock-out device preventing closing`（IEC 60947-2:2024 Cl. 3.10） |
| **TRM-DON-019** | 壳架等级 / 壳架电流 | ❌ `Frame specification / Shell rating / Inm (attributed to IEC 60947-2) ❌` | ✅ **Frame size** *(IEC 60947-2:2024 Cl. 3.1.1)* / **Frame current (Inm)** *(GB/T 14048.2 domestic convention)* | **撤销旧版对 `frame size` 的禁用**：`IEC 60947-2:2024 Cl. 3.1.1` 明确定义 **frame size** 为具有共同外部物理尺寸的一组断路器，且 Note 1 明确规定其以**该组最高额定电流的安培值**表示（全标准共 28 次）。**`Inm` 并非 IEC 60947-2 符号**（2024 版 0 次，标准仅在 Table 7 fn. a 使用 "maximum rated current for a given frame size"），`Inm` 属 **GB/T 14048.2** 国内约定符号 |
| **TRM-DON-020** | 塑壳断路器 | ❌ `Plastic case breaker / Molded circuit breaker ❌` | ✅ **Moulded-case circuit-breaker (MCCB)** *(IEC-harmonized industry term)* / **Molded Case Circuit Breaker (MCCB, UL 489)** *(North America)* | 塑壳断路器（MCCB）为全球行业通用产品品类词（IEC 60947-2:2024 正文未按 MCCB 分类，仅 Cl. 9.3.3.3 出现 `moulded case`、Cl. 8.1.6 出现 `moulding`，`moulded-case` 0 次）；IEC 交付件沿用英式 `moulded` 与连字符 `circuit-breaker`，美式 `Molded` 与非连字符 `Circuit Breaker` 仅限北美 UL 489 专栏 |

---

## 2. General Industrial Component & CAD Drawing False Friends

| Chinese Source | ❌ Forbidden Literal Translation | ✅ Mandatory Professional Term | Why & Standard Context |
| :--- | :--- | :--- | :--- |
| **基准 (CAD图纸)** | Base / Reference point *(or untranslated)* | **Datum** | Geometric dimensioning & tolerancing (GD&T) standard reference plane. |
| **安装面** | Install surface | **Mounting surface** | Switchboard rear/bottom structural mounting plane. |
| **柜门内侧** | Inside door / Door back | **Inner side of door / Door interior** | Enclosure door clearance dimensions. |
| **分离位置 / 隔离位置** | Separation place / Pull out | **Disconnected position / Isolated position** | Withdrawable circuit-breaker position terminology (Connected / Test / Disconnected; IEC 60947-2:2024 Cl. 3.5 & Cl. 8.1.2). |
| **电工辅料 / 附件** | Auxiliary Materials | **Electrical Accessories / Installation Accessories** | "Auxiliary Materials" implies raw materials/steel, not electrical components. |
| **浮球液位开关** | Floating Ball Level Switch | **Float Level Switch / Cable Float Switch** | Industry standard terminology across the major international catalogues. |
| **重锤** | Heavy Hammer | **Counterweight / Balance Weight** | "Hammer" is a pounding tool; in float switches, it is a counterweight. |
| **约定自由空气发热电流** | Agreed-upon heating current in pure air | **Conventional free air thermal current Ith** | IEC 60947-2:2024 Cl. 5.3.3.1 (refs IEC 60947-1:2020 Cl. 5.3.2.1) exact standard definition. |
| **额定冲击耐受电压** | Rated impact withstand voltage | **Rated impulse withstand voltage Uimp** | IEC 60947-2:2024 Cl. 5.3.2.3 (refs IEC 60947-1:2020 Cl. 5.3.1.3). "Impact" is mechanical collision; "Impulse" is electrical surge/lightning. |
| **使用类别** | Use classes / Application class | **Utilization category** *(IEC 60947-2:2024 Annex L.4.1 Oxford `-ize`; `Utilisation category` is an acceptable European `-ise` variant)* | IEC 60947-3 / 60947-4-1 / 60947-5-1 technical classification (IEC 60947-2:2024 `L.4.1` verbatim: `utilization category AC-22`). |
| **寿命 / 操作循环次数：`{{ops_wan: 万次}}`** | `{{ops_wan}}` Ten thousand times / Durability (IEC) | **`{{ops: operations}}` / `{{ops: cycles}}`** *(IEC 60947-2:2024: operating cycles / endurance)* | Never translate 万 literally into "Ten thousand". Convert to a plain integer: `{{ops_wan: 万次}}` → `{{ops: operations}}`. The number itself comes from the datasheet. |
| **安装调试** | Installation and Debugging | **Installation and Commissioning** | "Debugging" is software troubleshooting; electromechanical apparatus uses "Commissioning". |
| **注意事项** | Matters need attention | **Operating Precautions / Safety Notes** | "Matters need attention" is poor literal translation. |
| **订货须知** | Ordering instruction | **Ordering Information** | Global standard catalogue section heading. |
| **未注公差** | No tolerance specified | **Unspecified linear tolerance / General tolerance** | "No tolerance specified" implies zero control; "Unspecified" means general standard tolerance. |
| **误动作** | Wrong action / Bad work | **False tripping / Nuisance tripping / Malfunction** | Electrical switching & relay terminology. |
| **吸入** | Sucked in | **Drawn in / Entrapped by suction vortex** | Fluid mechanics and pump safety. |

---

## 3. Sentence-Level Anti-Chinglish & Native Engineering Rewriting Patterns

| Issue Type | ❌ Word-for-Word Chinese Literal Phrasing | ✅ Native International Engineering Rewriting | Key Improvement Principle |
| :--- | :--- | :--- | :--- |
| **Measurement Accuracy Boundary** | *Below `{{metering_threshold: A}}`, the measurement is inaccurate.* | **Measurement unspecified below `{{metering_threshold: A}}`** *(or Accuracy unspecified below `{{metering_threshold: A}}`)* | Converts conversational critique into a formal data-sheet boundary specification. |
| **Accessory Function & Operating Logic** | *The time-delay undervoltage release is used when the line experiences short-time low voltage or loss of power, and can delay opening the circuit breaker.* | **The time-delay undervoltage release delays circuit-breaker tripping for short-term line low-voltage conditions or power loss.** | Replaces rambling sequential Chinese clauses ("is used when... and can...") with a concise, direct active predicate, using `undervoltage release` and hyphenated `circuit-breaker`. |
| **Protective Indication** | *When earth current is too big, Ig lamp light up to warn user.* | **The Ig indicator illuminates upon detecting a residual earth fault.** | Replaces "light up / lamp" with standard electrotechnical terminology and active structure. |

---

## 4. Typography, Spacing & Unit Formatting Guardrails

1. **Mandatory Half-Width Space Before Units**:
   - Always insert exactly one space between a numeric value and its physical/electrical unit.
     - ✅ `{{value: A}}`, `{{value: V}}`, `{{value: Hz}}`, `{{value: kV}}`, `{{value: kA}}`, `{{value: N·m}}`
     - ❌ any form that concatenates the value and the unit with no space, or with two spaces
   - The patterns above describe **spacing only**; this file carries no product ratings.
2. **Standard Temperature Notation**:
   - Always use a half-width space followed by the degree symbol and capital C:
     - ✅ `{{T: °C}}`, `{{T_min: °C}}` to `{{T_max: °C}}`
     - ❌ full-width `℃`, bare `C` without the degree symbol, `deg C` spelled out, or an omitted space
3. **Number Conversion Guardrail**:
   - 万-based Chinese figures are converted to a plain integer, never transliterated: `{{ops_wan: 万次}}` → `{{ops: operations}}`.

---

## 5. IEC 60947-2:2024 vs US Spelling & Legacy Term Guardrails

Single-track Oxford/British spelling (`-our`/`-ou-`/`-re`/`-ll-` + ISO/IEC `-ize` verbs/nouns) & hyphenation applies across **both** Track 1 (IEC Global Catalogue) and Track 2 (OEM Manual). North American spellings (`Molded`, `Color`, `Aluminum`, unhyphenated `Circuit Breaker`) are permitted **only** inside explicit North American / UL 489 / UL 1066 columns or annotations.

| Category | ❌ Forbidden in IEC Track 1 & 2 | ✅ Mandatory IEC 60947-2:2024 Form | Verified Standard Basis & Audit Count |
| :--- | :--- | :--- | :--- |
| **Device noun** | `circuit breaker` *(unhyphenated; UL/ANSI only)* | **`circuit-breaker`** | 667 vs 3 in IEC 60947-2:2024 (`Cl. 3.1`) |
| **Enclosure material** | `molded` / `molded-case` *(UL 489 only)* | **`moulded`** / **`moulded-case circuit-breaker`** | `moulded case` (`Cl. 9.3.3.3`), `moulding` (`Cl. 8.1.6`); 0 `molded` |
| **Mounting method** | `Drawer` / `Drawer type` *(Chinglish)* | **`withdrawable`** *(IEC standard primary)*; **`drawout`** *(accepted international commercial / UL synonym)* | 18 `withdrawable` vs 1 `draw-out cradle` (`Fig. J.1`); `Cl. 3.5`, `4.4`, `8.1.2` |
| **Verbs / `-ize` nouns** | `energis*`, `utilis*` *(when citing IEC 60947-2:2024 verbatim)* | **`utilization`** (`L.4.1`), **`utilize`**, **`energize` / `energized` / `energizing` / `energization`** | ISO/IEC Oxford `-ize`: `utilization` (`L.4.1`, 1 vs 0 `utilisation`), `energiz*` (37 vs 0 `energis*`) |
| **Conductors** | `aluminum` *(US/UL only)* | **`aluminium`** | 45 vs 1 in IEC 60947-2:2024 (`Cl. 8.1.1`, `Annex D`) |
| **Indicator / enclosure colour** | `color` *(US/UL only)* | **`colour`** | 8 vs 0 in IEC 60947-2:2024 (`Annex B`, `Annex M`) |
| **Catalogue noun** | `catalog` *(US/UL only)* | **`catalogue`** | IEC 60947-2:2024 `Table 4` (`catalogue reference`) |
| **Coordination** | `discrimination` *(legacy IEC edition)* | **`selectivity`** | 40 vs 0 `discrimination` in IEC 60947-2:2024 (`Cl. 4.1`, `5.4`, `Annex A`) |
| **Back-up protection** | `backup` *(unhyphenated)* | **`back-up`** | 4 vs 0 `backup` in IEC 60947-2:2024 (`Cl. 1`, `Annex A.6`) |
| **Releases** | `under-voltage`, `shunt opening release` | **`undervoltage release`**, **`shunt release`**, **`closing release`** *(admitted: `closing coil`)* | `undervoltage` 36 vs 4; `shunt release` 25 vs 0; `closing release` 13 (`Cl. 3.19`) |
| **Life / cycle ratings** | `durability` *(attributed to IEC 60947-2)* | **`operational performance capability` / `operating cycles`** *(main std)*; **`endurance`** *(Annex B/M/R)* | 0 occurrences of `durability`; `operational performance` (40), `operating cycles` (23, `Cl. 8.2.4.2`, `Table 7`), `endurance` (9, e.g. `M.8.11`, `R.8.5`) |
| **Track 2 OEM legacy names** | Mixing US spelling into OEM phrases | Harmonized orthography around legacy OEM phrases *(1:1 maintenance of existing manuals only; new manuals use Track 1)*: **`Closed electromagnet (CEM)`**, **`Door Frame and Pad`**, **`Steel Cable Interlock`**, **`Keys and locks (KL)`**, **`Drawer seat`**, **`hole opener`** | Preserves 1:1 parity for previously published OEM manuals while enforcing IEC `circuit-breaker`, `undervoltage`, `withdrawable`, `utilization` |

---

## 6. MCCB & IEC 60947-2:2024 Annex False Friends & Specialized Terms

| Term / Symbol | Standard Ref | ❌ False Friend / Misleading Literal | ✅ Mandatory IEC 60947-2:2024 English | Distinction & Technical Boundary |
| :--- | :--- | :--- | :--- | :--- |
| **CBR** (带剩余电流保护断路器) | Annex B (`B.1`) | `Earth leakage breaker` / `ELCB` / `RCCB` | **Circuit-breaker incorporating residual current protection (CBR)** | `RCCB` is IEC 61008-1 (no overcurrent protection); `CBR` integrates overcurrent + residual current protection (`Types AC, A, B`). |
| **MRCD** (模块化剩余电流装置) | Annex M (`M.1`) | `External leakage relay` / `Separate RCD` | **Modular residual current device (MRCD)** *(without integral current breaking device)* | Associated with a circuit-breaker to break the circuit; adapts Annex B (`U_s`, `U_n`, `I_Δc`, `I_Δw`). |
| **CBI** (不满足过电流保护要求的断路器) | Annex L (`L.1`, `L.3`) | `Non-automatic breaker` / `Switch-disconnector` | **Circuit-breaker not fulfilling the requirements for overcurrent protection (CBI)** | Classes **W** ($I_{cu} = I_{cw}$), **X**, **Y** ($I_{cc}$ only); derived from an equivalent CB (`L.2.1`); cannot protect circuits alone (`Switch-disconnector` is IEC 60947-3). |
| **ICB** (瞬时脱扣断路器) | Annex O (`O.1`, `O.4`) | `Magnetic-only breaker` / `Motor circuit protector (MCP)` | **Instantaneous trip circuit-breaker (ICB)** | Active normative annex in Ed. 6.0; fulfils short-circuit protection only (no overload release); visibly marked `"ICB"`. `MCP` is a North American UL 489 term. |
| **PV DC circuit-breaker** (光伏直流断路器) | Annex P (`P.1`, `P.4`) | `Solar DC breaker` | **DC circuit-breaker for use in photovoltaic (PV) applications** *(up to `{{Ue_dc: V DC}}`, std ceiling 1 500 V DC)* | `8.2.4.1` overload tests waived (PV overcurrent is short-circuit only); must interrupt forward & reverse currents; marked `IEC 60947-2:2024, Annex P`. |
| **CBAR** (带自动重合闸剩余电流断路器) | Annex R (`R.1`, `R.3.2`) | `Auto-recloser leakage breaker` | **Circuit-breaker incorporating residual current protection with automatic reclosing functions (CBAR)** | Types **M** (earth leakage monitoring, $I_{\Delta\text{ar}}$) and **TD** (time-delay); AC circuits only. |
| **Cut-off current** (截断电流 / 允通电流) | Cl. 3.3 Note 2 | `Limited peak current` / `Truncation current` | **Let-through current / Cut-off current** | Prospective peak reduced by current-limiting circuit-breaker; graphical templates in `Fig. K.2–K.3`. |
| **Let-through energy ($I^2t$)** (允通能量) | Cl. 3.3, Cl. 3.13 | `Thermal energy pass-through` / `Joule integral value` | **Let-through energy ($I^2t$)** / **$I^2t$ characteristic** | Limited below half-cycle symmetrical prospective $I^2t$; graphical templates in `Fig. K.4–K.5`. |
| **Take-over current ($I_B$)** (交接电流) | Cl. 9.3.8, Annex A, Table K.1 | `Transfer current` / `Handover current` | **Take-over current ($I_B$)** | Current at which an associated fuse or back-up SCPD takes over interruption from the circuit-breaker. |
| **Selectivity limit current ($I_s$)** (选择性极限电流) | Cl. 8.2.7, Annex A, Table K.1 | `Discrimination limit` / `Selective threshold` | **Selectivity limit current ($I_s$)** | Upper prospective current limit up to which selectivity between upstream and downstream devices is maintained. |
| **Conditional short-circuit current ($I_{cc}$ vs $I_q$)** | Annex L (`L.4.2`), Annex M (`M.4.3.1`), Table K.1 | `Conditional breaking current` | **Rated conditional short-circuit current ($I_{cc}$)** *(IEC 60947-2:2024 CBIs/MRCDs)* / **($I_q$)** *(IEC 60947-1/3/4-1 switch-disconnectors & starters)* | Use **$I_{cc}$** (and **$I_{\Delta c}$** for residual in MRCDs) when citing IEC 60947-2:2024 Annex L/M; reserve **$I_q$** for IEC 60947-1 / 60947-3 / 60947-4-1 equipment. |
