# NXM-250S 塑壳断路器英文规格书初稿审查报告（Mode B · IEC 60947-2:2024 海外样本口径）

**审查对象**：NXM-250S 塑壳断路器英文规格书初稿（10 句）  
**审查基准**：IEC 60947-2:2024（第 6 版）、IEC 60947-1、ISO/IEC 80000-1（SI 量与单位格式）、ISO/IEC Directives, Part 2（国际电工标准英文编排规范）  
**审查范围**：仅输出术语核实、合规性审查意见、修改建议及待确认清单，**不代填任何原文未提供的技术参数**。

---

## 一、专项核实：`Frame size: 250A` vs. 同事建议 `Frame current Inm`

### 结论：**驳回同事修改意见，保留 `Frame size`，仅修正单位空格为 `Frame size: 250 A`**

| 对比维度 | 原稿 `Frame size: 250A` | 同事建议 `Frame current Inm` | 核实依据 |
|---|---|---|---|
| **IEC 60947-2:2024 原文匹配度** | **术语正确**（仅缺数字与单位间的空格） | **非标准术语，标准中无此符号** | IEC 60947-2 在术语定义章节（2024 版第 3 章，沿袭 2016 版 2.18 条）明确定义并使用 **`frame size`** |
| **海外 IEC 样本可读性** | 通用标准表达（欧洲、亚太、中东、拉美 IEC 市场通用） | 海外工程师与咨询机构无法在 IEC 60947-2 中查到 `Inm` | `Inm`（壳架等级额定电流）系中国国内标准及行业长期沿用的本土符号，并非 IEC 符号 |
| **处理结论** | 保留术语，格式改为 **`Frame size: 250 A`** | **不得写入海外 IEC 样本册** | 避免本土化符号反向污染海外 IEC 技术文档 |

**标准原文要点说明**：
- IEC 60947-2 对 **`frame size`** 的核心定义为：用于表征一组具有相同外形尺寸（同壳架下宽度可随极数变化）但覆盖不同额定电流等级的断路器，**以该组断路器的最大额定电流安培值表示**（*expressed in amperes corresponding to the highest current rating of the group*）。因此 `Frame size: 250 A` 完全符合 IEC 60947-2 原文语义与单位要求。
- IEC 60947-2:2024 电流类标准符号包括 *I*<sub>n</sub>（rated current）、*I*<sub>u</sub>（rated uninterrupted current）、*I*<sub>th</sub> / *I*<sub>the</sub>（conventional thermal current）、*I*<sub>r</sub>（current setting）等，**全文不存在 `Inm` 符号，也不存在 `frame current` 这一正式定义术语**。
- **提醒**：原文仅给了 `Frame size: 250 A`，漏列了额定电流 *I*<sub>n</sub>（后文 `Ir`、`Ii` 均引用了 *I*<sub>n</sub>）。应在核实产品规格后**另行补列 `Rated current (In)`**，而不是把 `Frame size` 改写成 `Frame current Inm`。

---

## 二、审查总览

初稿存在 **3 项高风险问题**（中式英语非标单位、美标 UL/ANSI 术语混入 IEC 体系、交流电符号 `~` 误作区间符）、**4 项中风险问题**（标准术语漏词、美式拼写与连字符不统一、SI 空格缺失、物理量符号未规范上下标）及 **2 项低风险格式/文风问题**；另识别出 **6 项缺失或需核实的关键工程参数**。

---

## 三、逐项问题清单与修改建议

### 1. 高优先级（术语体系错误 / 语义歧义 / 非标单位）

| 序号 | 原文片段 | 问题类型 | 规范依据与风险说明 | 修改建议 |
|---|---|---|---|---|
| **H1** | `Mechanical durability: 20000 times.`<br>`Electrical durability: 8000 times.` | 非标单位（中式直译） | `times` 系“次”的直译，不用于 IEC 开关设备寿命参数。IEC 60947-1 / 60947-2 规定机械与电气操作寿命的计量单位为 **`operating cycles`**（1 个操作循环 = 1 次闭合 + 1 次断开）。此外，IEV 441-16-14 / 441-16-15 对应的标准术语为 **`mechanical endurance` / `electrical endurance`**（部分样本亦写作 `durability`，须全册统一，但单位必须为 `operating cycles`）。 | 改为：<br>`Mechanical endurance: 20 000 operating cycles.`<br>`Electrical endurance: 8 000 operating cycles.`<br>（若样本体系已固定用 `durability`，至少须将 `times` 改为 `operating cycles`） |
| **H2** | `Short-time pickup Isd: 2~10Ir.`<br>`Instantaneous pickup Ii: 5~10In.`<br>`Overload setting Ir: 0.7~1.0In.` | 美标/IEC 术语体系混用 | **`pickup`** 属北美 IEEE/ANSI/UL 489 保护继电器与断路器体系习惯用词；IEC 60947-2 体系使用 **`current setting`** / **`tripping current setting`**（对应过载/长延时脱扣、短延时过电流脱扣、瞬时过电流脱扣）。`Overload setting` 亦宜补全 `current`。 | 改为：<br>`Long-time (overload) current setting (Ir)`<br>`Short-time delay current setting (Isd)`<br>`Instantaneous tripping current setting (Ii)` |
| **H3** | `0.7~1.0In`<br>`2~10Ir`<br>`5~10In` | 符号误用与乘号缺失 | 1. 在电工领域（IEC 60417-5032），波浪号 **`~`** 是**交流电（AC）**的专用符号，用作数值范围系典型中式排版错误，易造成阅读歧义。<br>2. ISO/IEC Directives, Part 2 规定正文区间优先使用 **`to`**，表格紧凑排版可用短破折号 **`–`**（en dash，非连字符 `-`）。<br>3. 数值系数与电流符号间缺少乘号 `×` 或空格（`1.0In` 不合规）。 | 正文建议：<br>`(0.7 to 1.0) × In`<br>`(2 to 10) × Ir`<br>`(5 to 10) × In`<br>（参数表紧凑列可用 `(0.7–1.0) × In`、`(2–10) × Ir`、`(5–10) × In`） |

### 2. 中优先级（IEC 标准术语完整性 / 拼写 / SI 与符号排版）

| 序号 | 原文片段 | 问题类型 | 规范依据与风险说明 | 修改建议 |
|---|---|---|---|---|
| **M1** | `Ultimate breaking capacity Icu: 36kA at 415V.`<br>`Service breaking capacity Ics: 100% Icu.` | IEC 术语缺省核心限定词 | IEC 60947-2 中 *I*<sub>cu</sub> 与 *I*<sub>cs</sub> 的完整标准名称为 **`Rated ultimate short-circuit breaking capacity`** 与 **`Rated service short-circuit breaking capacity`**。省去 `Rated` 与 `short-circuit` 在正式规格书中不够严谨。 | 补全为：<br>`Rated ultimate short-circuit breaking capacity (Icu): 36 kA at 415 V.`<br>`Rated service short-circuit breaking capacity (Ics): 100 % of Icu.`（或 `100 % Icu`） |
| **M2** | `Molded Case Circuit Breaker`<br>`This circuit breaker...` | 美式拼写及连字符不统一 | IEC 60947-2 遵循英式拼写规范，使用 **`moulded`**（`molded` 属美标 UL 拼写）和带连字符的 **`circuit-breaker`**。原稿首句首字母大写、末句小写且均无连字符。 | 统一为 IEC 拼写：<br>标题/名称：`Moulded-Case Circuit-Breaker (MCCB)`（或 `Moulded Case Circuit-Breaker`）<br>正文：`circuit-breaker` |
| **M3** | `250A`, `800V`, `8kV`, `36kA`, `415V`, `100%` | 数值与单位间缺少空格 | ISO/IEC 80000-1 强制要求数值与单位符号（含 `%`）之间保留一个空格（仅平面角符号 `° ′ ″` 例外）。 | 改为：`250 A`、`800 V`、`8 kV`、`36 kA`、`415 V`、`100 %` |
| **M4** | `Ui`, `Uimp`, `Icu`, `Ics`, `Ir`, `In`, `Isd`, `Ii` | 物理量符号排版不规范 | ISO/IEC 80000-1 与 IEC 60947-2 规定：代表物理量的主字母用**斜体**，角标用**正体下标**（如 *U*<sub>i</sub>、*U*<sub>imp</sub>、*I*<sub>cu</sub>、*I*<sub>cs</sub>、*I*<sub>r</sub>、*I*<sub>n</sub>、*I*<sub>sd</sub>、*I*<sub>i</sub>）。 | 排版交付稿统一设置斜体主符 + 正体下标 |

### 3. 低优先级（数字分节与地道表达）

| 序号 | 原文片段 | 问题类型 | 规范依据与风险说明 | 修改建议 |
|---|---|---|---|---|
| **L1** | `20000`、`8000` | 大数分节格式 | ISO/IEC 80000-1 规定五位及以上数字每三位以空格分节（IEC 禁用逗号分节，避免与欧陆小数点混淆）；四位数可不分节，但在同组参数中与五位数并列时建议统一分节以利对齐。 | 改为 `20 000` 与 `8 000` |
| **L2** | `This circuit breaker is suitable for distribution protection.` | 表达偏中式直译 | `distribution protection` 略显直译（“配电保护”）；海外 IEC 样本通常明确对象为配电系统/配电网络。 | 改为：`This circuit-breaker is designed for the protection of power distribution systems.`（或简化为 `Suitable for power distribution protection.`） |

---

## 四、逐句修订建议对照（仅基于原文已有信息，不代填缺失参数）

> 以下修订参考严格限定于原稿已出现的字段，未新增任何未经确认的技术数值；需补充的项目统一列于第五节「待确认清单」。

| 原稿 | 修订建议（IEC 60947-2 样本口径） |
|---|---|
| NXM-250S Molded Case Circuit Breaker (IEC 60947-2). | NXM-250S Moulded-Case Circuit-Breaker (IEC 60947-2). |
| Frame size: 250A. | Frame size: 250 A. |
| Rated insulation voltage Ui: 800V. | Rated insulation voltage (*U*<sub>i</sub>): 800 V. |
| Rated impulse withstand voltage Uimp: 8kV. | Rated impulse withstand voltage (*U*<sub>imp</sub>): 8 kV. |
| Ultimate breaking capacity Icu: 36kA at 415V. | Rated ultimate short-circuit breaking capacity (*I*<sub>cu</sub>): 36 kA at 415 V. |
| Service breaking capacity Ics: 100% Icu. | Rated service short-circuit breaking capacity (*I*<sub>cs</sub>): 100 % of *I*<sub>cu</sub>. |
| Mechanical durability: 20000 times. | Mechanical endurance: 20 000 operating cycles. |
| Electrical durability: 8000 times. | Electrical endurance: 8 000 operating cycles. |
| Overload setting Ir: 0.7~1.0In. Short-time pickup Isd: 2~10Ir. Instantaneous pickup Ii: 5~10In. | Long-time (overload) current setting (*I*<sub>r</sub>): (0.7 to 1.0) × *I*<sub>n</sub>. Short-time delay current setting (*I*<sub>sd</sub>): (2 to 10) × *I*<sub>r</sub>. Instantaneous tripping current setting (*I*<sub>i</sub>): (5 to 10) × *I*<sub>n</sub>. |
| This circuit breaker is suitable for distribution protection. | This circuit-breaker is suitable for the protection of power distribution systems. |

---

## 五、待确认与缺失关键信息清单（提交产品/研发核实，严禁代填）

以下信息在初稿中缺失或存在潜在工程矛盾，需产品工程师依据型式试验报告与正式规格书补齐或核对后，方可进入定稿排版：

1. **额定电流 *I*<sub>n</sub> 缺失**
   - 原文仅提供 `Frame size: 250 A`，未列出 *I*<sub>n</sub> 规格值或覆盖档位，但保护整定项（*I*<sub>r</sub>、*I*<sub>i</sub>）直接引用了 *I*<sub>n</sub>。须补充对应的 `Rated current (In)`。
2. **额定工作电压 *U*<sub>e</sub>、电流制式（AC/DC）、额定频率及极数缺失**
   - `at 415 V` 未标注 `AC`、`50/60 Hz` 及 *U*<sub>e</sub> 完整电压等级，亦未注明极数（如 3P / 4P）。
3. **脱扣器配置与三段保护参数一致性核查（重点）**
   - 原稿同时给出 *I*<sub>r</sub>、*I*<sub>sd</sub>、*I*<sub>i</sub>，属于典型**电子脱扣器（LSI）**配置。请核实 `NXM-250S` 型号本身是否配备短延时 *I*<sub>sd</sub> 功能，避免与热磁脱扣型号或电子式系列（如带 `E` 后缀型号）混淆。
   - 若确具备短延时功能，初稿缺失对应的**动作时间整定参数**（长延时时间 *t*<sub>r</sub>、短延时时间 *t*<sub>sd</sub>）以及**使用类别（Utilization category A / B）**；若属 B 类，还须核实额定短时耐受电流 ***I*<sub>cw</sub>**。
   - **整定区间交叉提醒**：原稿中 *I*<sub>sd</sub> 上限为 `10 × Ir`、*I*<sub>i</sub> 下限为 `5 × In`，当 *I*<sub>r</sub> 设为 `0.7–1.0 × In` 时，*I*<sub>sd</sub> 上限（`7–10 × In`）会高于 *I*<sub>i</sub> 下限（`5 × In`）。请核对原规格书，确认 *I*<sub>sd</sub> 与 *I*<sub>i</sub> 的基准电流（*I*<sub>r</sub> vs. *I*<sub>n</sub>）及倍率范围无抄录误差，并确认整定方式为分档可调还是连续可调。
4. **电气耐久性测试条件未注明**
   - `8 000 operating cycles` 需核实对应的试验条件（如测试电压 *U*<sub>e</sub>、电流 *I*<sub>n</sub> 及负载类型），IEC 样本通常在注释或表格副标中明确标注。
5. **标准年代号（`:2024`）合规确认**
   - 原稿仅标注 `(IEC 60947-2)`。若需在样本册中明确宣称符合 `IEC 60947-2:2024`，须先核对产品的 CB/KEMA/TUV 等第三方认证与型式试验报告是否已按 2024 版完成覆盖，未确认前建议保留不带年代号的 `IEC 60947-2` 或以证书版本为准。
6. **IEC 60947-2 常规强制/推荐声明项核对**
   - 如需作为完整规格页发布，建议同步核实并确认是否补充：隔离功能适用性（`Suitability for isolation`）、污染等级（`Pollution degree`）、额定短路接通能力（*I*<sub>cm</sub>）及额定工作电压范围。
