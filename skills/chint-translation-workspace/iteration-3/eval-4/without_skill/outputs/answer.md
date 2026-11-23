# MCCB 及特种派生系列技术规格英文翻译与 IEC 60947-2:2024（第 6 版）条款标注

---

## 一、英文翻译（IEC 60947-2:2024 国际样本册语体 · Track 1）

Designed in accordance with **IEC 60947-2:2024**, this series of moulded-case circuit-breakers (MCCBs), including withdrawable versions, supports terminals intended for the connection of unprepared round aluminium conductors and can be paired with an external relay to form a circuit-breaker derivative not fulfilling the requirements for overcurrent protection (**CBI**) with utilization category **AC-22**.

1. **Circuit-Breakers Incorporating Residual Current Protection (CBR):** Provide **Type B** residual current protection covering rated residual operating current ($I_{\Delta n}$) and rated residual short-circuit making and breaking capacity ($I_{\Delta m}$). Where a test push-button marked **"T"** is provided, the colour of the push-button shall not be red or green.
2. **IT System Version:** Verified in accordance with the individual pole short-circuit test sequence for IT systems and marked with the IT system individual pole short-circuit current symbol **$I_{\text{IT}}$**; for rated operational voltage levels where the circuit-breaker is not suitable for IT systems, the crossed-out **IT** symbol (~~IT~~) shall be marked.
3. **Photovoltaic (PV) DC Version:** Dedicated to photovoltaic d.c. circuits up to the maximum standard voltage limit of **1 500 V d.c.**, supporting non-polarized (bi-directional) breaking of both forward and reverse currents and verified in accordance with the critical d.c. load current test sequence.
4. **Upstream/Downstream Selectivity and Back-up Protection Co-ordination:** Provides selectivity limit current (**$I_s$**) curves and specifies the take-over current (**$I_B$**) in co-ordination with an upstream fuse or back-up short-circuit protective device (SCPD).

---

## 二、核心技术特性与 IEC 60947-2:2024（第 6 版）条款及标准符号对照表

| 序号 | 原文核心技术特性 | 英文规范表达（Track 1） | IEC 60947-2:2024（Ed. 6）准确条款 / 附录 | 标准符号 / 标识 | 核验要点 |
| :---: | :--- | :--- | :--- | :---: | :--- |
| 0-1 | 塑壳断路器（MCCB）按 IEC 60947-2:2024 设计 | Moulded-case circuit-breaker (MCCB) designed in accordance with IEC 60947-2:2024 | **Clause 1**（适用范围：交流 ≤ 1 000 V / 直流 ≤ 1 500 V）；**Clause 3**（术语定义，原 Ed. 5 为 Clause 2） | `MCCB` | 第 6 版与 IEC 60947-1:2020 对齐，标准正文条款号自 Clause 2 起顺延一位 |
| 0-2 | 抽出式安装型 | Withdrawable version / Withdrawable circuit-breaker | **Clause 3**（引用 IEC 60947-1:2020, 3.2.15 抽出式定义）；**Clause 8.1**（抽出式断路器结构附加要求，原 Ed. 5 为 7.1）；**Clause 9**（试验验证） | — | 涵盖抽出式位置指示、机械联锁与隔离位置等结构与操作要求 |
| 0-3 | 铝导体接线端子（未经预处理的圆铝导线） | Terminals for the connection of unprepared round aluminium conductors | **Clause 8.1.7**（接线端子结构要求）& **Clause 9.2.4**（接线端子验证试验），规范引用 **IEC 60947-1:2020, Clause 8.1.7 & Clause 9.2.4**；**Clause 6.2**（端子标识） | `Al` 或 `Al/Cu` | 默认端子仅针对铜导体；支持未经预处理圆铝导线时须通过铝导体专项温升/电流循环及机械试验，并按规定标识 `Al` 或 `Al/Cu` |
| 0-4 | 匹配外部继电器构成使用类别 AC-22 的无过电流保护派生型号（CBI） | Circuit-breaker not fulfilling the requirements for overcurrent protection (CBI), paired with an external relay, utilization category AC-22 | **Annex L**（规范性附录：*Circuit-breakers not fulfilling the requirements for overcurrent protection*）；使用类别与试验条款引用 **Annex L** 及 **IEC 60947-3**（混合阻性与感性负载，含适度过载） | `CBI`、`AC-22` | 须区分 **Annex L（CBI，无过电流保护要求）** 与 **Annex O（ICB，仅瞬时脱扣断路器）**；原文仅给定 `AC-22`，未擅自补写 `AC-22A`/`AC-22B` 后缀 |
| 1-1 | 剩余电流保护派生型（CBR）· B 型剩余电流保护 | Circuit-breakers incorporating residual current protection (CBR) — Type B residual current protection | **Annex B**（规范性附录：*Circuit-breakers incorporating residual current protection (CBR)*；按直流分量特性分类及 B 型动作特性试验，参照 IEC 62423 协调要求） | `CBR`、**Type B** 图形符号（正弦交流 + 脉动直流 + 平滑直流/复合频率组合符号，见 **Annex B & Annex K**） | B 型覆盖正弦交流、脉动直流及平滑直流剩余电流保护 |
| 1-2 | 额定剩余动作电流 & 额定剩余短路接通和分断能力 | Rated residual operating current & rated residual short-circuit making and breaking capacity | **Annex B**（特性参数与型式试验条款）；**Annex K**（符号汇编） | $I_{\Delta n}$、$I_{\Delta m}$ | 原文未给出具体安培/千安额定值，严格留空不编造 |
| 1-3 | 测试按钮 T，颜色不得为红色或绿色 | Test push-button marked "T"; colour shall not be red or green | **Annex B**（产品信息/标识与试验装置结构要求条款，规定标识字母 `T` 或 `Test` 且按钮颜色不得为红、绿色） | `T` | 防止与分/合闸主操作机构或紧急状态指示颜色（红/绿）混淆 |
| 2-1 | IT 系统适用型 · IT 系统单极短路试验程序验证及符号 | Verified in accordance with the individual pole short-circuit test sequence for IT systems | **Annex H**（规范性附录：*Test sequence for circuit-breakers for IT systems*）；单极短路试验通用方法另见 **Annex C**；符号汇编见 **Annex K** | $I_{\text{IT}}$ | 验证 IT 系统发生异相双接地故障时，单极在线电压 $U_e$ 下分断 $I_{\text{IT}}$ 的能力 |
| 2-2 | 不适用电压等级标示带叉 IT 符号 | Crossed-out "IT" symbol marked for non-applicable voltage levels | **Annex H**（标志要求）& **Clause 6.2**（标志，原 Ed. 5 为 5.2）& **Annex K** | 带斜杠/叉号的 **IT** 符号（~~IT~~） | 须与不适用的具体额定工作电压并列标示；原文未给出具体电压等级，不作预设 |
| 3-1 | 光伏直流派生型 · 最高标准上限 1 500 V DC | Photovoltaic (PV) d.c. version up to the maximum standard limit of 1 500 V d.c. | **Annex P**（规范性附录：*Circuit-breakers for direct current for use in photovoltaic (PV) applications*）；**Clause 1**（直流适用范围上限 1 500 V d.c.） | `1 500 V d.c.` / `⎓`（IEC 60417-5031 直流符号） | 原文明确表述为“最高适用标准上限为 1500V DC”，译文保持“maximum standard voltage limit”措辞，不将其曲解为单一壳架实测额定工作电压 $U_e$ |
| 3-2 | 正向与反向电流无极性分断 | Non-polarized (bi-directional) breaking of both forward and reverse currents | **Annex P**（光伏直流断路器无极性/双向电流分断要求及正反向接线验证试验） | 无极性（不标注单向 `+`/`-` 极性限制） | 针对光伏并联组串故障时可能出现的反向馈电电流，要求正反两个电流方向均能可靠分断 |
| 3-3 | 临界直流负载电流试验程序 | Critical d.c. load current test sequence | **Annex P**（光伏直流断路器专用临界直流负载电流试验程序） | — | 验证直流低电流区（磁吹力较弱、电弧熄灭困难区间）的可靠分断性能 |
| 4-1 | 上下级选择性 · 选择性极限电流曲线 | Upstream/downstream selectivity — selectivity limit current curves | **Annex A**（资料性附录：*Co-ordination under short-circuit conditions between a circuit-breaker and another short-circuit protective device associated in the same circuit*）；**Clause 3**（选择性术语定义）；**Annex K** | $I_s$ | IEC 60947-2 新版统一采用 **selectivity** 替代旧版术语 *discrimination* |
| 4-2 | 后备保护配合（上游熔断器或后备保护电器）· 交接电流 | Back-up protection co-ordination with an upstream fuse or back-up SCPD — take-over current | **Annex A**（后备保护配合及交接电流定义与验证）；**Annex K** | $I_B$ | $I_B$ 为上下级保护电器时间-电流特性曲线交点对应的预期电流，用于界定下游断路器独立分断与上游后备保护电器（SCPD/熔断器）接管分断的分界点 |

---

## 三、简短术语与标准依据说明

1. **IEC 60947-2:2024（第 6 版）结构与条款变化说明**
   - IEC 60947-2:2024（Edition 6.0）与 **IEC 60947-1:2020** 完成全面结构对齐，按 ISO/IEC 导则第 2 部分将“规范性引用文件”独立为 **Clause 2**，“术语和定义”顺延为 **Clause 3**，此后各主章（Classification → Clause 4、Characteristics → Clause 5、Product information → Clause 6、Normal service conditions → Clause 7、Constructional and performance requirements → Clause 8、Tests → Clause 9）均较第 5 版（2016+A1:2019）顺延一位；核心专项附录编号（**Annex A / B / C / H / K / L / P**）保持连续。

2. **国际样本册语体（Track 1）拼写与术语规范**
   - 遵循 IEC / ISO 英文规范体例（英式拼写结合 Oxford `-ize` 词尾）：采用 `moulded-case circuit-breaker`、`aluminium`、`colour`、`co-ordination`、`utilization`、`non-polarized`、`1 500 V d.c.`（千位空格分隔）。
   - 选择性保护统一使用 IEC 现行标准术语 **selectivity**（及 `selectivity limit current` $I_s$），不再沿用早期版本中的 *discrimination*；交接电流统一译为 **take-over current**（$I_B$），而非字面直译 *handover current*。

3. **特种派生系列关键标准边界辨析**
   - **CBI（Annex L）**：指“不满足过电流保护要求的断路器（circuit-breakers not fulfilling the requirements for overcurrent protection）”，典型应用即外配保护继电器并按 AC-22 等使用类别执行通断；须与仅带瞬时短路脱扣的 **ICB（Annex O）** 区分。
   - **CBR（Annex B）**：B 型剩余电流保护覆盖平滑直流分量，测试按钮强制要求标注 `T`（或 `Test`）且禁用红/绿两色，避免人机误操作。
   - **IT 系统（Annex H）**：针对 IT 系统双点异相接地故障工况验证单极耐受与分断电流 $I_{\text{IT}}$，凡未通过验证的额定电压等级须强制加注带叉 IT 标识（~~IT~~）。
   - **光伏直流（Annex P）**：IEC 60947-2 直流上限为 1 500 V d.c.，光伏派生型核心差异在于无极性正/反向电流分断能力及针对小电流拉弧风险的临界直流负载电流试验程序。

4. **参数完整性与防编造声明**
   - 译文与对照表严格忠实于原文信息，**未编造**原文未提供的任何具体额定值或壳架参数（如额定电流 $I_n$、极限/运行短路分断能力 $I_{cu}/I_{cs}$、$I_{\Delta n}$ 具体档位、$I_{\Delta m}$ 与 $I_{\text{IT}}$ 具体千安值、不适用 IT 系统的具体电压等级、以及 AC-22A/AC-22B 频度细分后缀）。上述字段如用于正式样本发布，须待产品规格书与型式试验报告补齐。
