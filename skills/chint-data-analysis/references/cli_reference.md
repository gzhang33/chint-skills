# CLI 调用命令与场景字典参考 (CLI Reference)

本文档汇总了 `query_sales.py` 的全部 CLI 运行参数、动态筛选机制以及高频业务场景的调用命令模板。

---

## 1. CLI 参数速查表 (CLI Arguments)

| 参数 | 缩写 | 类型 / 格式 | 说明 | 示例 |
| :--- | :--- | :--- | :--- | :--- |
| `--group-by` | `-g` | 字符串 (英文逗号分隔) | 聚合维度（支持 56 列表头中的任意字段组合） | `-g "产品系列"` / `-g "省份,产品系列"` / `-g "终端客户"` |
| `--filter` | `-f` | 字符串 (分号分隔条件) | 通用动态筛选器（支持多值枚举、比较、否定） | `-f "省份=江苏,浙江;属性=本体"` / `-f "月份>=3;产品系列!=NXA"` |
| `--months` | `-m` | 整数列表 (英文逗号分隔) | 月份切片范围（默认全月） | `-m 1,2,3,4,5,6,7` 或 `-m 7` |
| `--year` | `-y` | 整数 | 目标年份（默认 2026） | `-y 2026` |
| `--category` | `-c` | 字符串 (`acb`, `mccb`, `mcb`, `intl`, `all`) | 品类隔离（框架、塑壳、微断、海外、全量） | `-c acb` |
| `--property` | `-p` | 字符串 (`benti`, `non_benti`, `all`) | 属性口径（默认 `benti` 本体；`non_benti` 附件；`all` 全量） | `-p benti` |
| `--replace-rate` | `-r` | 字符串 (`新产品:老产品`) | 计算新老产品发票实物台数替换率 | `-r "NXA:NA1"` 或 `-r "昆仑:1系列"` |
| `--top` | `-n` | 整数 | 限制返回前 N 条记录（按销售额降序，默认 10） | `-n 10` |
| `--all` | `-a` | 标志 (Flag) | 返回全量记录，不截断 Top N | `-a` |
| `--yoy` | 无 | 标志 (Flag) | 开启当前年份与去年同期 (YoY) 对比模式 | `--yoy` |
| `--query` | `-q` | 字符串 (`overview`) | 快捷查询模式（如大盘概览速报） | `-q overview` |

---

## 2. 常见高频业务场景调用字典

### 2.1 整体大盘与多维趋势
- **看大盘概览与品牌拆解**：
  ```bash
  python3 .agents/skills/chint-data-analysis/scripts/query_sales.py -q overview -y 2026
  ```
- **看当年累计（如 1-7 月）各产品系列销售额及同比**：
  ```bash
  python3 .agents/skills/chint-data-analysis/scripts/query_sales.py -g "产品系列" -y 2026 -m 1,2,3,4,5,6,7 --yoy -a
  ```
- **看主力产品型号表现（Top 15）**：
  ```bash
  python3 .agents/skills/chint-data-analysis/scripts/query_sales.py -g "产品型号" -y 2026 --yoy -n 15
  ```

### 2.2 新老产品替换率分析 (台数口径)
- **分析昆仑系列对 1 系列在各省份的台数替换率**：
  ```bash
  python3 .agents/skills/chint-data-analysis/scripts/query_sales.py -g "省份" -y 2026 -m 1,2,3,4,5,6,7 -r "昆仑:1系列" -n 10
  ```
- **分析 NXA 对 NA1 框架断路器在各大区的替换率**：
  ```bash
  python3 .agents/skills/chint-data-analysis/scripts/query_sales.py -g "大区" -c acb -y 2026 -r "NXA:NA1" -a
  ```

### 2.3 行业客户与渠道分析
- **分析框架断路器在哪些终端行业客户下滑最严重（行业归因）**：
  ```bash
  python3 .agents/skills/chint-data-analysis/scripts/query_sales.py -g "终端客户" -c acb -y 2026 --yoy -n 10
  ```
- **分析渠道经销商客户在特定省份的销售分布（渠道下钻）**：
  ```bash
  python3 .agents/skills/chint-data-analysis/scripts/query_sales.py -g "客户名称,省份" -y 2026 -f "省份=江苏,浙江" --yoy -n 10
  ```

### 2.4 区域与条件组合过滤
- **查询江苏和浙江两省 NXA 断路器本体销量与销售额**：
  ```bash
  python3 .agents/skills/chint-data-analysis/scripts/query_sales.py -g "省份,产品系列" -y 2026 -f "省份=江苏,浙江;产品系列=NXA;属性=本体" -a
  ```
- **海外大区整体表现与国家分布**：
  ```bash
  python3 .agents/skills/chint-data-analysis/scripts/query_sales.py -g "洲区,国家" -y 2026 --yoy -a
  ```

---

## 3. 报表与自动化 PPT 导出命令

- **导出指定产品大类的标准分析 PPT 报告**：
  ```bash
  python3 .agents/skills/chint-data-analysis/scripts/pptx_generator.py --category 框架 --year 2026 --months 1,2,3,4,5,6,7 --output reports/框架业务分析汇报.pptx
  ```
  *(注：`--category` 支持 `框架`、`塑壳` 等配电品类名称)*
- **生成交互式可拖拽 HTML 数据看板**：
  ```bash
  python3 .agents/skills/chint-data-analysis/scripts/generate_dashboard.py --output reports/dashboard.html
  ```
