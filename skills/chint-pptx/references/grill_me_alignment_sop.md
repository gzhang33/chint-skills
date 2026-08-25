# CHINT PPTX Requirement Alignment SOP (/grill-me Protocol)

This document specifies the standard interactive alignment procedure that an AI Agent must follow before generating corporate PowerPoint presentations. It enforces the `/grill-me` protocol to resolve ambiguities and map requirements to optimal slide archetypes.

---

## 1. Core Principles

1. **Pragmatic Non-Technical PM Persona**:
   - The user is a Product Manager. All interaction must focus on business objectives, target audience, key narrative points, and presentation length.
   - Never expose raw code, Python exceptions, or XML structures in chat.
2. **Interactive UI Modals via `ask_question`**:
   - For every key decision point, the Agent invokes the `ask_question` tool.
   - Recommended options are always listed first and prefixed with `(Recommended)`.
   - Ask **one question at a time** to walk down the decision tree systematically.
3. **Dynamic Pacing (No Cookie-Cutter Slides)**:
   - Determine slide count and structure based on actual input content density.
   - Only select the necessary layout archetypes; never generate redundant placeholder slides.

---

## 2. Interactive Decision Tree (Step-by-Step)

```
[PM Input / Topic] ──► [Q1: Goal & Audience] ──► [Q2: Target Slide Count & Pacing]
                                                            │
[Generate PPTX] ◄── [Q4: Confirm Deck Outline] ◄── [Q3: Theme & Domain Focus]
```

### Step 1: Clarify Goal & Audience

*Agent invokes `ask_question` to determine presentation context:*
- **Question**: "请问本次 PPT 汇报的核心目标与受众场景是？"
- **Options**:
  - `(Recommended) 方案评审与业务汇报（面向部门总监/业务评审委员会，聚焦架构方案与实施路径）`
  - `客户拜访与行业解决方案宣讲（面向电网/工商业客户，聚焦产品优势与标杆案例）`
  - `战略规划与年度复盘（面向高管团队，聚焦核心业务指标、增长成效与战略演进）`
  - `新品发布与技术规格宣贯（面向渠道商/售前团队，聚焦产品电气参数与差异化卖点）`

---

### Step 2: Determine Pacing & Slide Count

*Agent evaluates input content and suggests appropriate pacing:*
- **Question**: "基于输入的内容规模，建议的 PPT 篇幅结构为？"
- **Options**:
  - `(Recommended) 精炼汇报版（5–8 页：封面、目录、核心背景、核心方案/架构、成效指标、推进计划、致谢）`
  - `标准方案版（10–14 页：包含痛点剖析、架构分层、4大核心模块、标杆案例与时间轴）`
  - `深度宣讲版（15–22 页：包含多维度对比矩阵、完整生态链图谱、各行业解决方案九宫格）`

---

### Step 3: Confirm Visual Theme & Business Domain Focus

*For Low-Voltage Power Distribution PMs, default to Classic Blue:*
- **Question**: "PPT 主题视觉配色与产品线聚焦："
- **Options**:
  - `(Recommended) 正泰极光蓝（#1E50E6）：低压配电/智能电气标准色系，严谨科技风`
  - `绿色能源与低碳光储（#14C832 + #1E50E6）：适用于微电网、新能源储能与绿电方案`
  - `数智化与物联网平台（#14C8B4 + #1E50E6）：适用于正泰云、配电能效 SaaS 与智慧运维平台`

---

### Step 4: Outline & Layout Archetype Mapping

Before invoking the Python generation engine, synthesize the input into a structured slide mapping plan and present it to the PM for quick sign-off:

```markdown
### 推荐幻灯片大纲与版式映射：
1. **第 1 页 [ARCH_01 封面]**：主标题 + 副标题 + 汇报人/日期
2. **第 2 页 [ARCH_02 目录]**：4 大核心章节导航
3. **第 3 页 [ARCH_04 KPI 看板]**：核心业务现状与三大关键指标
4. **第 4 页 [ARCH_07 痛点与对策]**：当前痛点 vs 正泰对策双分栏
5. **第 5 页 [ARCH_08 平台架构]**：端-边-云 3 层智能化体系
6. **第 6 页 [ARCH_05 多列卡片]**：3 大核心产品/功能矩阵
7. **第 7 页 [ARCH_06 时间轴]**：4 阶段实施路线图与里程碑
8. **第 8 页 [ARCH_11 致谢联络]**：品牌标语与服务联系方式
```

---

## 3. Autonomous Execution & Quality Gate

Once the PM confirms the outline:
1. The Agent silently formats the structured deck payload into JSON / Python builder calls.
2. The Agent runs `python3 scripts/chint_pptx_engine.py --config payload.json --output /path/to/output.pptx`.
3. The Agent verifies the generated PPTX with `scripts/inspect_pptx.py`.
4. The Agent returns the clickable file link `[output.pptx](file:///path/to/output.pptx)` along with an executive summary in Chinese.
