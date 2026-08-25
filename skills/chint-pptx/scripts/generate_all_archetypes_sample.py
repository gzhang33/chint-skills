#!/usr/bin/env python3
"""
CHINT PPTX Comprehensive Sample Generator (2026 VI Standard Edition)

Validates all 34 Archetype layouts with:
- Plan A: Dynamic Reflow (Auto-fit font size, 2-6 slice doughnut, N-column card grids, multi-module matrix grids).
- Plan C: High-definition Vector Charts (Radar, Dual-Axis Combo, Diverging Bar, Capability Matrix).
"""

import os
import json
import subprocess
from chint_pptx_engine import ChintPresentationEngine

payload = {
    "slides": [
        # 1. Master Frames
        {"archetype": "ARCH_01_COVER", "title": "正泰 2026 VI 全场景版式全景重构展示", "subtitle": "企业级标准化交付与 2026 VI 视觉规范引擎", "date": "2026年08月", "author": "正泰智能电气产业生态群 PM团队"},
        {"archetype": "ARCH_02_TOC", "items": [{"title": "母版与框架类组件规范"}, {"title": "数据量化与矢量图表看板类"}, {"title": "战略认知与管理诊断类"}, {"title": "流程流水线与漏斗模型类"}, {"title": "项目排期与平台生态类"}]},
        {"archetype": "ARCH_03_CHAPTER", "title": "第一篇：母版框架与基础视觉组件", "subtitle": "MASTER FRAMES & VISUAL BASICS"},
        {"archetype": "ARCH_15_CONTACT_US", "title": "全球联系方式与办事处网络", "category": "服务网络"},

        # 2. Data & KPIs (Reflow Tested: 4 KPI cards)
        {"archetype": "ARCH_04_KPI_DASHBOARD", "title": "核心经营与质量 KPI 看板 (4卡片自适应)", "category": "数据量化", "kpi_cards": [
            {"number": "99.98%", "label": "核心供电可靠率", "details": ["连续安全运行 3000+ 天", "毫秒级自愈切换"]},
            {"number": "32.5%", "label": "综合能效提升率", "details": ["全周期智慧能效管理", "降低碳排放 12 万吨"]},
            {"number": "140+", "label": "全球服务国家与地区", "details": ["本地化服务网络", "7×24 小时极速响应"]},
            {"number": "48 h", "label": "柔性定制交付周期", "details": ["数字化灯塔工厂支撑", "全自动化柔性产线"]}
        ]},
        
        # Native Bar & 5-Slice Doughnut (Reflow Tested: 5 Slices)
        {"archetype": "ARCH_16_CHART_BAR_TREND", "title": "核心业务收入与战略新品对比", "category": "量化看板"},
        {"archetype": "ARCH_17_CHART_PIE_DONUT", "title": "业务板块与营收占比分布 (5切片自适应)", "category": "结构拆解", "slices": [
            {"label": "新能源与绿色电工", "value": 38, "desc": "光伏、储能与智能配电方案高速增长"},
            {"label": "智能电气核心主业", "value": 30, "desc": "低压元器件与成套设备稳健支撑"},
            {"label": "工业自动化与物联", "value": 16, "desc": "智慧能效管理与工业物联软件平台"},
            {"label": "海外新兴市场拓展", "value": 10, "desc": "一带一路沿线及欧美战略新兴市场"},
            {"label": "综合能源智慧运维", "value": 6, "desc": "微网云边端一体化全生命周期服务"}
        ]},
        
        # Plan C: High-Resolution Vector Charts
        {"archetype": "ARCH_16_RADAR", "title": "新一代 NXA 竞品与技术能力对标雷达", "category": "能力雷达", "chart_title": "六维技术与商业能力对标", "categories": ["极限分断能力", "温升控制性能", "智能化边缘感知", "低功耗表现", "结构紧凑度", "数字化云边运维"], "series": [
            {"name": "正泰 NXA 新一代", "values": [96, 92, 90, 88, 95, 94], "color": "#1E50E6"},
            {"name": "行业主流标杆 A", "values": [80, 82, 75, 72, 78, 70], "color": "#50C8FF"}
        ], "insights": [
            "极限分断与结构紧凑度达到 95+ 分，全面领跑行业同级产品",
            "内置智能化边缘感知算法，支持微秒级自愈与预警联动",
            "温升控制与低功耗表现优化 18%，显著延长元器件使用寿命"
        ]},
        
        {"archetype": "ARCH_16_COMBO", "title": "业务营收规模与同比增速双轴复合看板", "category": "双轴看板", "chart_title": "2022-2026E 营收与增长走势", "categories": ["2022", "2023", "2024", "2025", "2026E"], "bar_series": {
            "name": "主营业务收入", "values": [120, 155, 195, 245, 320], "unit": "亿", "color": "#1E50E6"
        }, "line_series": {
            "name": "同比复合增速", "values": [16.5, 29.1, 25.8, 25.6, 30.6], "unit": "%", "color": "#14C832"
        }, "insights": [
            "2026E 预期营收突破 320 亿元，复合增长率维持在 25% 以上高位",
            "战略新品与行业定制化方案营收贡献率已超过总盘的 45%",
            "规模效应逐步释放，边际履约成本同比下降 12.4%"
        ]},

        {"archetype": "ARCH_16_DIVERGING", "title": "行业细分赛道渗透率正负增长对比", "category": "行业分岔", "chart_title": "各行业赛道年度增长与承压对比 (%)", "categories": ["新能源光伏", "智能电网", "算力中心", "高端制造", "传统工商业", "高耗能冶金"], "values": [45.2, 32.0, 28.5, 19.4, -6.8, -15.2], "insights": [
            "新能源光伏与算力中心成为核心增长引擎，增速分别高达 +45.2% 与 +28.5%",
            "传统工商业与高耗能冶金赛道承压，正加速向绿色化与能效改造转型",
            "建议集中研发与营销资源全力深耕新能源与算力基础设施"
        ]},

        {"archetype": "ARCH_16_HEATMAP", "title": "核心产品系列与垂直行业场景适配矩阵", "category": "适配矩阵", "chart_title": "行业场景适配与成熟度热力图", "row_labels": ["NXA 万能式", "NA8 高端系列", "NM8N 塑壳", "NXM 标配系列"], "col_labels": ["集中式光伏", "储能电站", "智算中心", "轨道交通", "重工冶金"], "data_matrix": [
            [96, 94, 98, 95, 90],
            [92, 90, 95, 96, 88],
            [88, 95, 90, 85, 94],
            [82, 86, 80, 78, 90]
        ], "insights": [
            "NXA 系列在智算中心与集中式光伏适配度高达 98 分，为首选主打方案",
            "NA8 高端系列在轨道交通关键回路具备卓越的可靠性与抗震性能",
            "NM8N 与 NXM 系列形成了高低搭配、深度覆盖重工与储能的完整产品梯队"
        ]},

        {"archetype": "ARCH_16_WATERFALL", "title": "年度低压电器净利润变动与归因桥接", "category": "利润归因", "chart_title": "2025-2026E 净利润驱动因素拆解 (万元)", "categories": ["2025基准利润", "光伏储能增量", "高端新品溢价", "大宗铜材涨价", "智能化研发投入", "2026E净利润"], "values": [2600.0, 850.0, 420.0, -320.0, -280.0, 3270.0], "unit": "万", "insights": [
            "新能源与储能板块贡献最大正向增量，带动利润增长 +850 万元",
            "大宗原材料铜材价格波动带来 -320 万元承压，需通过套保平抑风险",
            "2026E 目标净利润达 3270 万元，同比净增 25.8%"
        ]},

        {"archetype": "ARCH_16_SANKEY", "title": "智能低压电力供应链流向与流转拓扑", "category": "价值流向", "chart_title": "清洁能源与智慧配电端到端流向 (MW)", "flows": [
            {"source": "集中式光伏", "target": "特高压并网", "value": 350, "color": "#1E50E6"},
            {"source": "集中式光伏", "target": "工商业配电", "value": 180, "color": "#50C8FF"},
            {"source": "分布式风电", "target": "工商业配电", "value": 220, "color": "#2378FF"},
            {"source": "工商业配电", "target": "绿色算力中心", "value": 260, "color": "#14C832"},
            {"source": "工商业配电", "target": "智能微电网", "value": 140, "color": "#14C8B4"},
            {"source": "特高压并网", "target": "城市骨干电网", "value": 350, "color": "#1437AA"}
        ], "unit": "MW", "insights": [
            "集中光伏与风电清洁电力占比突破 68%，成为核心电源供给侧",
            "绿色算力中心与工业微电网消纳能力持续提升，流转损耗降至 2.1% 以下",
            "全链路数字化感知支持潮流双向自愈与毫秒级负荷调度"
        ]},

        {"archetype": "ARCH_16_FUNNEL", "title": "重大电力工程招投标履约与转化漏斗", "category": "商机转化", "chart_title": "2026 年度重点项目全周期转化 (个)", "stages": ["市场线索获取", "技术方案交流", "标杆 PoC 试点", "招投标入围", "商务签约履约"], "values": [1280, 820, 460, 290, 210], "unit": "个", "insights": [
            "技术方案交流到 PoC 试点转化率达 56.1%，彰显过硬技术底座",
            "招投标入围到最终签约转化率高达 72.4%，头部项目胜率行业领先",
            "建议进一步优化前期线索清洗机制，提升第一阶段漏斗开口质量"
        ]},

        {"archetype": "ARCH_16_GAUGE", "title": "灯塔工厂智能制造 OEE 综合达成看板", "category": "生产效能", "chart_title": "全自动化柔性产线综合设备效率 (OEE)", "current_val": 94.6, "target_val": 90.0, "min_val": 0.0, "max_val": 100.0, "subtitle": "超额达成 105.1% (卓越区间)", "unit": "%", "insights": [
            "产线综合稼动率稳定在 94.6%，大幅超越 90.0% 行业标杆目标线",
            "全自动视觉检测与 AI 预防性维护将突发停机时间缩减 78%",
            "连续 180 天保持零重大设备事故与零不良品批量流出"
        ]},

        {"archetype": "ARCH_16_STACKED_AREA", "title": "三大核心业务板块规模演进与未来预测", "category": "业务演进", "chart_title": "2021-2026E 业务结构演进趋势 (亿元)", "categories": ["2021", "2022", "2023", "2024", "2025", "2026E"], "series": [
            {"name": "新能源与储能配电", "values": [45, 72, 110, 165, 230, 310], "color": "#1E50E6"},
            {"name": "传统工业与建筑电气", "values": [120, 130, 138, 145, 150, 158], "color": "#50C8FF"},
            {"name": "算力中心与高精设备", "values": [15, 28, 48, 78, 120, 182], "color": "#14C832"}
        ], "unit": "亿", "insights": [
            "新能源与算力中心双轮驱动，业务占比从 2021 年的 33% 提升至 2026E 的 75%",
            "总体业务规模突破 650 亿元，年均复合增长率 (CAGR) 高达 26.3%",
            "产品结构向高毛利、高技术壁垒的绿色数智化产品全面升级"
        ]},

        # Metric & Hero Grids
        {"archetype": "ARCH_18_KPI_METRIC_GRID", "title": "高密度经营指标矩阵看板", "category": "指标网格"},
        {"archetype": "ARCH_19_HERO_METRIC_SPLIT", "title": "超级单指标里程碑突破", "category": "核心突破"},

        # Strategic & Diagnostic Cards (Reflow Tested: 4-Column Cards)
        {"archetype": "ARCH_05_MULTI_COLUMN_CARDS", "title": "业务定位与四大核心战略职责 (4列自适应)", "category": "战略认知", "columns": [
            {"header": "技术创新驱动", "bullets": ["坚持核心技术自主研发", "打造全球核心专利壁垒"]},
            {"header": "卓越品质立业", "bullets": ["践行零缺陷质量管理体系", "全制程质量追溯与闭环"]},
            {"header": "绿色低碳引领", "bullets": ["100% 绿色电力生产制造", "打造国家级零碳示范工厂"]},
            {"header": "生态开放共赢", "bullets": ["全面赋能渠道与生态伙伴", "共建能源互联网产业联盟"]}
        ]},
        {"archetype": "ARCH_07_PROBLEM_SOLUTION_SWOT", "title": "传统模式挑战 vs 正泰方案剖析", "category": "战略对比", "pain_points": ["运维成本高昂且故障定位困难", "传统断路器无数字化通讯能力", "被动响应导致停电损失扩大"], "solutions": ["全链路 AI 预测性维护与健康度诊断", "内置标准物联协议秒级数据上云", "微秒级自愈切换与远程故障闭环"]},
        {"archetype": "ARCH_20_SWOT_TOWS_MATRIX", "title": "SWOT 战略态势诊断矩阵", "category": "战略诊断"},
        {"archetype": "ARCH_21_BEFORE_AFTER_DIFF", "title": "系统升级前后对比与价值跃升", "category": "对比革新", 
            "before_title": "传统模式 / 改造前 (Before)",
            "before_items": [
                "响应延迟：人工巡检维护，响应与排障周期长达 24-48 小时",
                "数据孤岛：系统割裂严重，各子回路无法跨系统互通互联",
                "粗放用能：缺乏实时负荷监测，存在大额隐形电力与能耗浪费",
                "被动抢修：缺乏前置预警机制，设备发生故障后被动抢修"
            ],
            "before_summary": "故障平均响应 > 24h | 年均额外运维成本超 120 万元 | 故障被动抢修",
            "after_title": "正泰智能方案 / 升级后 (After)",
            "after_items": [
                "预测维护：AI 预测性健康度维护，分钟级主动告警与远程诊断",
                "统一底座：统一云边物联底座，全域设备无缝秒级接入上云",
                "精细节能：精细化动态负荷调优，全厂综合能耗降低 30%+",
                "数字孪生：全生命周期资产数字孪生，故障自愈率超过 90%"
            ],
            "after_summary": "综合能耗降低 30%+ | 设备故障预警率 99.5% | 全域资产数字孪生"
        },
        {"archetype": "ARCH_22_PROBLEM_IMPROVE_SPLIT", "title": "核心短板剖析与针对性改进举措", "category": "改善行动",
            "problem_title": "当前现存主要问题与短板 (Diagnosis)",
            "problems": [
                "交付瓶颈：非标定制订单链路长，响应与交付周期偏长",
                "供应链承压：部分关键电子元器件供货面临波动与短缺风险",
                "数字渗透不足：部分一线现场依赖纸质记录，实时性与追溯欠缺"
            ],
            "problem_summary": "影响重大项目敏捷履约，面临供应链波动与现场协同交付风险",
            "improve_title": "系统化改善对策与推进计划 (Actions)",
            "improvements": [
                "柔性制造升级：引入自动化柔性装配岛，交付周期压缩至 48h 内",
                "战略安全库存：建立核心关键元器件双供应商机制与安全备库",
                "移动数字赋能：推行移动 APP 实时巡检、电子看板与全链路追溯"
            ],
            "improve_summary": "交付准时率提升至 99.2% | 核心物料双供覆盖率 100% | 48h 极速交付"
        },
        {"archetype": "ARCH_23_RISK_MATRIX_RESPONSE", "title": "项目风险识别与应对响应预案", "category": "风险防控", "risks": [
            {"level": "高风险", "title": "技术集成与接口兼容风险", "desc": "异构系统协议标准不统一，存在通信与指令丢包风险", "impact": "★★★★★ 极高", "probability": "高 (35%)", "response": "制定标准化网关协议中间件与统一物模型", "prevent": "建立多方联合架构评审与跨系统联调联试机制", "owner": "研发与技术 PMO", "timeline": "T+30 天闭环"},
            {"level": "中风险", "title": "工期排程与多方协同延误", "desc": "涉及土建、弱电与电气多个施工方交叉密集作业", "impact": "★★★★☆ 显著", "probability": "中 (20%)", "response": "设立联合现场 PMO 与每日跨专业站会协调机制", "prevent": "推行关键路径动态甘特图预警与施工资源动态调配", "owner": "工程管理部", "timeline": "全程常态化"},
            {"level": "低风险", "title": "运维人员数智系统操作门槛", "desc": "传统电工对新型云端监控与 APP 操作存在习惯惯性", "impact": "★★☆☆☆ 轻微", "probability": "低 (10%)", "response": "编制标准化图文/微课教程与现场实操实训体系", "prevent": "上线模拟演练考核系统，全面推行持证上岗机制", "owner": "客户成功部", "timeline": "交付前 2 周"}
        ]},
        {"archetype": "ARCH_24_MISSION_VISION_VALUES", "title": "企业文化与战略基石", "category": "文化基石", "pillars": [
            {"en_title": "MISSION", "cn_title": "企业使命", "slogan": "让电力能源更安全、绿色、便捷、高效", "details": ["以客户为中心，提供高品质全场景智慧能源解决方案", "赋能全球清洁能源转型与工业数智化绿色升级", "推动零碳微网与全生命周期综合能效管理服务"], "commitment": "2030 绿色低碳战略承诺  |  赋能产业转型"},
            {"en_title": "VISION", "cn_title": "企业愿景", "slogan": "成为全球领先的智慧能源解决方案提供商", "details": ["打造绿色低碳与数字化双轮驱动的产业生态集群", "成为备受全球信赖与尊重的可持续发展标杆企业", "构建开放协同、万物互联的智慧能源互联网生态"], "commitment": "全球 140+ 国家业务覆盖  |  世界一流品牌"},
            {"en_title": "VALUES", "cn_title": "核心价值观", "slogan": "客户导向、创新驱动、诚信立业、共创共享", "details": ["始终以客户价值创造为一切业务战略的出发点与落脚点", "坚持科技自主创新与组织活力，引领行业技术迭代", "恪守诚信合规经营底线，与全球生态伙伴共创共享共赢"], "commitment": "客户第一  |  创新驱动  |  共赢未来"}
        ]},

        # Process & Sequential (Reflow Tested: 5-Step Process & 5-Stage Roadmap)
        {"archetype": "ARCH_25_PROCESS_STEP_HORIZONTAL", "title": "五阶段标准化交付流程 (5步骤自适应)", "category": "流程管道", "steps": [
            {"phase": "01", "title": "现场调研", "subtitle": "需求摸底与配电勘测", "actions": ["电力拓扑实地测绘与摸底", "用电设备安全隐患排查", "全天候能耗负荷数据采集"], "deliverable": "《现场勘测诊断报告》", "duration": "1-2 周"},
            {"phase": "02", "title": "系统设计", "subtitle": "元器件选型与图纸深化", "actions": ["断路器与配电设备精准选型", "BIM 3D 机房布局深化设计", "定制化通信协议拓扑规划"], "deliverable": "《电气系统深化设计蓝图》", "duration": "2-3 周"},
            {"phase": "03", "title": "智能排产", "subtitle": "灯塔工厂柔性定制生产", "actions": ["智能制造全流程自动化装配", "100% 关键元器件质量质检", "全链路数字化追溯码生成"], "deliverable": "《产品出厂合格质检报告》", "duration": "1 周"},
            {"phase": "04", "title": "现场联调", "subtitle": "通电联调与云平台接入", "actions": ["现场设备安装与母排搭接", "边缘网关数据采集上云联调", "保护定值校验与带电试运行"], "deliverable": "《系统联调验收签署单》", "duration": "1 周"},
            {"phase": "05", "title": "智慧运营", "subtitle": "全生命周期云端运维", "actions": ["7x24h 智能能效与负荷优化", "AI 故障预测性维护与预警", "定期巡检与主动式备件保障"], "deliverable": "《年度智慧能效运营报告》", "duration": "长效运营"}
        ]},
        {"archetype": "ARCH_26_FUNNEL_CONVERSION", "title": "营销转化与客户全生命周期漏斗", "category": "漏斗模型"},
        {"archetype": "ARCH_27_STEP_LADDER_MATURITY", "title": "技术成熟度与演进阶梯", "category": "演进阶梯"},
        {"archetype": "ARCH_28_WATERFALL_DIAMOND", "title": "IPD 研发门禁与双钻流程", "category": "研发门禁"},
        {"archetype": "ARCH_06_TIMELINE_ROADMAP", "title": "五年实施路线与战略演进 (5阶段自适应)", "category": "路线演进", "stages": [
            {"phase": "2022 基础筑基", "title": "技术攻坚", "desc": "攻克核心分断与传感器专利"},
            {"phase": "2023 平台融合", "title": "数智上云", "desc": "发布智慧配电边缘网关平台"},
            {"phase": "2024 生态共建", "title": "行业深耕", "desc": "新能源与算力中心示范落地"},
            {"phase": "2025 全球突破", "title": "全球交付", "desc": "海外 140+ 国家营销网络覆盖"},
            {"phase": "2026 全面领航", "title": "零碳自愈", "desc": "打造全球领先智慧能源解决方案"}
        ]},
        {"archetype": "ARCH_29_GANTT_SCHEDULE_TABLE", "title": "项目排期与推进进度甘特表", "category": "甘特排期"},
        {"archetype": "ARCH_30_MILESTONE_LIST_BADGE", "title": "大事记与里程碑纪事", "category": "大事纪事"},

        # Architecture, Pillars & Ecosystem
        {"archetype": "ARCH_08_PLATFORM_ARCHITECTURE", "title": "分层系统架构与技术底座", "category": "技术架构", "layers": [
            {"layer_name": "应用服务层", "headline": "智慧能效与资产管理APP", "modules": ["能效大盘", "设备巡检", "告警中心", "碳足迹分析"]},
            {"layer_name": "核心能力层", "headline": "AI 诊断与调度微服务", "modules": ["算法引擎", "规则链", "数据中台", "拓扑识别"]},
            {"layer_name": "物联接入层", "headline": "多协议智能边缘网关", "modules": ["Modbus", "MQTT", "OPC-UA", "IEC 61850"]},
            {"layer_name": "深蓝底座层", "headline": "正泰安全可信云边 OS", "modules": ["硬件加密", "实时 OS", "安全芯片", "自愈引擎"]}
        ]},
        {"archetype": "ARCH_31_THREE_PILLARS_PLATFORM", "title": "三支柱与平台底座支撑体系", "category": "平台支撑"},
        {"archetype": "ARCH_32_ECOSYSTEM_CIRCULAR", "title": "产业协同与 4 方生态拓扑", "category": "生态拓扑"},
        {"archetype": "ARCH_14_CONCENTRIC_HUB", "title": "核心战略闭环体系", "category": "战略闭环"},

        # Grids & Endorsement (Reflow Tested: 8-Module Solution Grid)
        {"archetype": "ARCH_09_SOLUTION_GRID", "title": "八大垂直行业定制化解决方案 (8模块自适应)", "category": "行业方案", "modules": [
            {"title": "集中式光伏方案", "desc": "1500V 高压直流分断与智能汇流"},
            {"title": "工商业储能方案", "desc": "毫秒级快速切断与温升主动防护"},
            {"title": "绿色算力中心", "desc": "2N 高可用供电与极速自愈联动"},
            {"title": "轨道交通配电", "desc": "抗震防冲击与严苛环境高可靠"},
            {"title": "智慧医院建筑", "desc": "连续供电保障与医疗隔离电源"},
            {"title": "高端重工制造", "desc": "大容量电动机保护与能效管控"},
            {"title": "海上风电并网", "desc": "高盐雾防腐与抗雷击浪涌设计"},
            {"title": "海外基建工程", "desc": "IEC/UL 双重认证与宽温域运行"}
        ]},
        {"archetype": "ARCH_10_CASE_STUDY", "title": "国家电网示范项目案例", "category": "标杆案例", "client_name": "国家电网某特高压换流站", "hero_metric": "35% 能效提升", "hero_desc": "定制化高可靠变配电成套设备落地", "bullets": ["故障自愈切除时间 < 10ms", "全生命周期运维成本降低 40%", "实现连续安全运行 1200+ 天零故障"]},
        {"archetype": "ARCH_33_HONOR_CERTIFICATION", "title": "权威认证与企业荣誉背书", "category": "荣誉背书"},
        {"archetype": "ARCH_34_PARTNER_LOGO_WALL", "title": "战略合作伙伴与产业生态墙", "category": "生态伙伴"},

        # Profile & Footprint
        {"archetype": "ARCH_12_TEAM_PROFILE", "title": "专家团队与核心资历", "category": "专家团队", "members": [
            {"name": "张博士", "title": "首席架构师", "role": "技术带头人", "credentials": ["精通电力物联网架构", "主持国家级重大科技专项"]},
            {"name": "李总监", "title": "低压产品线负责人", "role": "产品专家", "credentials": ["20年配电产品研发经验", "主导 NXA 系列战略落地"]},
            {"name": "王总工", "title": "智能制造首席工程师", "role": "制造专家", "credentials": ["灯塔工厂数字化总设计师", "精益六西格玛黑带大师"]}
        ]},
        {"archetype": "ARCH_13_GLOBAL_FOOTPRINT", "title": "全球业务覆盖与区域网络", "category": "全球布局"},
        {"archetype": "ARCH_11_CLOSING", "tagline": "正泰 - 汇聚光亮 赋能未来", "team": "正泰智能电气 PM 团队 2026"}
    ]
}

os.makedirs("/Users/gianni/Documents/chint/dist", exist_ok=True)
out_pptx = "/Users/gianni/Documents/chint/dist/正泰企业级全场景版式全景测试样本.pptx"

engine = ChintPresentationEngine()
engine.build_from_payload(payload, out_pptx)
print(f"Successfully generated full archetype sample deck at: {out_pptx}")
