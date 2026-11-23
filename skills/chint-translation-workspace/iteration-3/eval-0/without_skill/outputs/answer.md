# 框架断路器（ACB）附件英文样本译文（IEC 国际通用版）

## 英文样本译文（Track 1 样本语体）

**Shunt Release**
- Enables remote opening of the circuit breaker.
- Operating voltage range: 70%–110% of rated control supply voltage.
- Operating time: ≤ 50 ms.
- *Duty cycle:* Both the closing release and shunt release operate on pulse-energized duty, requiring a pulse duration *t*₁ ≥ 200 ms and an energization interval *t*₂ > 15 s.

**Breaker-Mounted Keylock**
- Configuration: 3 locks, 2 keys.
- On-site installation requires a Ø28 mm cabinet door cutout using a hole cutter.

---

## 术语与数值处理说明

### 1. IEC 术语对齐

| 中文原文 | 英文译法 | 处理说明 |
| :--- | :--- | :--- |
| 分励脱扣器 | Shunt release | 采用 IEC 60947-2 标准术语，避免美标/UL 体系常见的 `shunt trip`。 |
| 闭合电磁铁 | Closing release | 与 `shunt release` 保持同一 IEC 术语体系，契合海外通用样本习惯。 |
| 远程分断 | remote opening | IEC 语境下“分断/分闸”规范用词，区别于故障保护触发的 `tripping`。 |
| 额定控制电源电压 | rated control supply voltage | IEC 标准全称；如样本同页参数表已定义符号，可简写为 `70%–110% Us`。 |
| 脉冲通电工作制 | pulse-energized duty | 明确瞬时脉冲激励特性，避免泛译为常规断续工作制（`intermittent duty`）。 |
| 断路器本体钥匙锁 | Breaker-Mounted Keylock | 突出锁具安装于断路器本体，与抽屉座（chassis/cradle）钥匙锁形成区分。 |
| 开孔器 | hole cutter | 中性工程术语，兼顾旋转开孔锯与液压开孔器，不额外限定现场工具形态。 |

### 2. 数值、符号与单位规范

- **范围连字符**：中文波浪号 `70%~110%` 替换为英文出版规范短破折号 `70%–110%`。
- **SI 单位空格**：数值与国际单位之间统一加空格（`50 ms`、`200 ms`、`15 s`、`28 mm`）；百分号沿用英文样本排版惯例紧跟数字。
- **边界条件保真**：严格区分“不大于”（`≤ 50 ms`）、“不小于”（`≥ 200 ms`）与严格“大于”（`> 15 s`），不改动任何阈值语义。
- **工程符号修正**：希腊字母 `Φ` 替换为 ISO/IEC 机械制图标准直径符号 `Ø`（`Ø28 mm`）；时间变量按 ISO 80000 规范采用斜体加下标（*t*₁、*t*₂）。

### 3. 样本语体（Track 1）处理

- **去说明书指令口吻**：将偏操作指导的“必须保证……”“现场安装需使用……”转为客观、紧凑的规格与安装前提陈述（`requiring ...`、`On-site installation requires ...`），避免 `You must...`、`Please use...` 等说明书句式。
- **条目化排版**：按两项独立附件拆分为标题加要点结构，满足海外经销商快速浏览功能定位、电气规格与开孔尺寸的检索需求。
