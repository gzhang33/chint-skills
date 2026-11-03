# CHINT 内容页版式契约（2026-11 起）

内容页只有一种版式：**表格**。其余历史版式已在 `_validate_slide_payload` 处停用。

## 允许的 archetype

| archetype | 用途 | 必需字段 |
|---|---|---|
| `ARCH_01_COVER` | 封面 | `title`；可选 `subtitle`、`date`、`author` |
| `ARCH_02_TOC` | 目录（模板原生，单页；条目上限见引擎校验） | `items` |
| `ARCH_03_CHAPTER` | 章节过渡（不加 logo） | `title`；可选 `subtitle` |
| `ARCH_TABLE` | 内容页 | `title`、`headers`、`rows` |
| `ARCH_11_CLOSING` | 尾页 | 可选 `tagline`、`team`、`call_to_action`、`contact` |
| `ARCH_16_CHART_BAR_TREND` | 随时间趋势 | `title`、`categories`、`series`、`summary_bullets` |
| `ARCH_17_CHART_PIE_DONUT` | 构成占比 | `title`、`center_metric`、`center_label`、`slices` |
| `ARCH_16_RADAR` | 多维能力对标 | `title`、`categories`、`series` |

选用其它 archetype 会直接报错，并给出对应的表格迁移写法（见引擎里的 `ARCHETYPE_MIGRATION`）。

## 选型规则（由人判断，校验脚本不判）

- **分类对比、明细清单、口径说明** → `ARCH_TABLE`
- **随时间变化的趋势** → `ARCH_16_CHART_BAR_TREND`
- **构成占比** → `ARCH_17_CHART_PIE_DONUT`
- **多维度能力对标**（维度数受雷达图可读性约束） → `ARCH_16_RADAR`

表格与图表不是互斥项：一段数据既可以用表格逐行列出，也可以用图表呈现走势。先判断读者要「查数」还是「看势」，再选形式。

## `ARCH_TABLE` 载荷

```json
{
  "archetype": "ARCH_TABLE",
  "title": "标题（必填）",
  "category": "可选，显示在标题前的中括号标签",
  "headers": ["年度", "净收入（亿元）", "同比"],
  "rows": [["<年度>", "<数值>", "<同比>"], ["<年度>", "<数值>", "<同比>"]],
  "align": ["center", "right", "center"],
  "note": "可选，表格下方口径说明"
}
```

| 字段 | 规则 |
|---|---|
| `headers` | 非空字符串数组，决定列数 |
| `rows` | 每行长度必须等于 `headers` 长度；超出引擎单页行数上限直接报错，请拆页（上限见 `TABLE_MAX_ROWS`） |
| `align` | 可选，长度等于列数，取值 `center` / `left` / `right`；**缺省居中** |
| `note` | 可选，落款口径 |

### 多层表头

需要跨列合并时提供 `levels` + `header_tree` + `merge_groups`：

```json
{
  "levels": [2, 1],
  "header_tree": [["区域", "2026 净收入", null, "占比"],
                  [null, "亿元", "同比", null]],
  "merge_groups": [{"row": 0, "columns": [1, 2]}],
  "headers": ["区域", "亿元", "同比", "占比"],
  "rows": [["<区域>", "<数值>", "<同比>", "<占比>"]]
}
```

- `levels` 是每一层表头的高度权重，当前只支持两层。
- `header_tree[r][c]` 为该格文字，`null` 表示留空（仍填品牌蓝，与合并块连成一片）。
- `merge_groups[].row` 为表头层号，`columns` 必须是**连续列区间**。
- `headers` 仍是扁平数组，用于确定列数；多层时它不直接渲染。

## 表格样式（生成器固定，校验器核对；色值以 `spec/brand_tokens.json` 为准）

| 项 | 规格 |
|---|---|
| 表头 | `theme.blue` 底、`theme.white` 字、加粗；字号取表头档 |
| 正文 | `theme.white` / `theme.light_bg` 隔行交替；字号按可用高度自适应，不低于正文下限 |
| 对齐 | 缺省居中，可按列覆盖 |
| 内边距 | 单元格上下与左右留白固定（见 `_render_table`） |
| 安全区 | 全部形状必须落在画布内 |

## 校验

```bash
python3 scripts/check_deck_compliance.py <deck.pptx>
```

引擎保存前会自动跑同一份检查，未通过则报错并列出问题项。检查覆盖：

1. 封面 / 目录 / 尾页是否存在；
2. 内容页与目录页各有且仅有右上角 CHINT 徽标；章节页按设计不加；
3. 表格表头为品牌蓝、白字加粗、字号在范围内；
4. 正文行做隔行浅底且使用品牌浅色；
5. 行数不超过引擎单页上限，形状不越出画布。

对比度、留白美观度、文案正确性不在自动检查范围，需人工过目。
