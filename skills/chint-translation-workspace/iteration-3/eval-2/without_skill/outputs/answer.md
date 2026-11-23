# NZ7 系列双电源自动转换开关（ATS）安装与使用说明书节选英译

## 英文译文（产品说明书语体）

### 4.3 Transfer Modes

This product supports two transfer modes: break-before-make (BBM) and make-before-break (MBB). During closed-transition transfer, the momentary paralleling time of the two power sources does not exceed 100 ms. The operating transfer time is no greater than 1.5 s, and the return transfer delay can be set within the range of 0 s to 180 s.

### 4.4 Mechanical Interlock

The mechanical interlock mechanism shall ensure that the two power sources cannot be closed simultaneously.

---

## 术语说明

| 中文原文 | 英文译法 | 依据与语体说明 |
| :--- | :--- | :--- |
| 转换方式 | Transfer Modes | 说明书章节标题采用名词短语（Title Case），符合低压转换开关设备（ATSE）手册惯例。 |
| 先断后通（BBM） / 先通后断（MBB） | break-before-make (BBM) / make-before-break (MBB) | 国际开关电器通用标准术语，正文全小写并保留括号缩写。 |
| 闭路转换 | closed-transition transfer | IEC 60947-6-1 / UL 1008 中对应先通后断（MBB）的规范表述，区别于开路转换（open-transition transfer）。 |
| 短时并列时间 | momentary paralleling time | 准确表达双电源在闭路转换过程中的瞬时并列重叠时长，避免口语化直译。 |
| 转换动作时间 | operating transfer time | 对应 IEC 60947-6-1 标准术语，指触头完成主备电源切换动作本身的时间（不含延时）。 |
| 恢复转换延时 | return transfer delay | 对应主电源恢复正常后切回常用电源前的延时参数（亦可写作 retransfer delay）。 |
| 整定 | set (can be set within...) | 配电保护与控制器领域中“整定”对应工程动词 `set`（整定值即 setting），比泛化的 adjust 更贴合说明书技术语体。 |
| 机械联锁机构 | mechanical interlock mechanism | 标准机电结构术语。 |
| 应保证 | shall ensure | 按 IEC 技术文档编写规范，强制性安全/功能要求用 `shall`，与 4.3 节客观性能指标描述（`does not exceed` / `is no greater than`）区分语气层级。 |

---

## 数值与格式说明

1. **国际单位制（SI）空格规范**：原文无空格的 `100ms`、`1.5s`、`180s` 在英文技术说明书中按 ISO/IEC 规范在数值与单位间补空格，统一写作 `100 ms`、`1.5 s`、`0 s to 180 s`。
2. **数值区间格式**：原文中文波浪号区间 `0~180s` 转换为英文规范区间表达 `0 s to 180 s`（表格或紧凑排版场景亦可使用短破折号 `0–180 s`），避免在英文官方手册中残留中文习惯符号 `~`。
3. **边界限定词严格保真**：
   - `不超过 100ms` → `does not exceed 100 ms`（对应 `≤ 100 ms`）；
   - `不大于 1.5s` → `is no greater than 1.5 s`（对应 `≤ 1.5 s`）。
   两处均未擅自改写量纲或放宽边界条件。

---

## 原文技术一致性核对提示

- **4.3 与 4.4 存在潜在逻辑冲突**：4.3 节声明产品支持先通后断（MBB / 闭路转换）且两路电源可短时并列（≤ 100 ms），而 4.4 节要求机械联锁机构保证两路电源不能同时合闸。在纯机械互斥联锁结构下，两路电源无法同时闭合，与 MBB 闭路并列转换在物理上互斥。建议在定稿前与研发核实：4.4 节是否仅适用于 BBM（开路转换）规格或特定子型号；如属实，建议在中英文原文中补充适用条件（例如“For BBM models, the mechanical interlock mechanism shall ensure...”）。
