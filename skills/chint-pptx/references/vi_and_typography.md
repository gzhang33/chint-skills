# CHINT 2026 VI Standard & Typography Reference (`vi_and_typography.md`)

This guide specifies the official **CHINT 2026 VI Design Standard**, font hierarchy, and color tokens matching **26年模板拓新体.pptx** (109-page master presentation).

---

## 1. Official Color Palette Tokens (2026 VI Standard)

| 语义角色 | 2026 VI 官方标准 Token | 十六进制色值 | RGB 色值 | 适用界面元素与组件场景 |
| :--- | :--- | :--- | :--- | :--- |
| **品牌主色 (Primary Blue)** | `C_BLUE` (正泰极光蓝) | `#1E50E6` | `(30, 80, 230)` | 幻灯片大标题、主行动按钮、卡片主色标头、核心数字高亮 |
| **辅助主色 (Light Cyan)** | `C_CYAN` (正泰亮青) | `#50C8FF` | `(80, 200, 255)` | 辅助副标题、流向箭头、节点光晕、装饰线条、副指标 |
| **警示/痛点色 (Alert Red)** | `C_RED_TEXT` (警示红) | `#D70A32` | `(215, 10, 50)` | 痛点挑战标题、风险卡片、负向指标、SWOT 劣势/威胁标签 |
| **痛点背景色 (Alert BG)** | `C_RED_BG` (柔和浅红) | `#FFEBEB` | `(255, 235, 238)` | 痛点卡片底色、问题清单容器背景 |
| **绿色能源/增长 (Growth Green)** | `C_GREEN` (正泰生态绿) | `#14C832` | `(20, 200, 50)` | 节能减排、良率达成、正向增长率、SWOT 机会标签 |
| **生态绿背景 (Green BG)** | `C_GREEN_BG` (柔和浅绿) | `#E8F8EE` | `(232, 248, 238)` | 机会卡片背景、正向增长标签底色 |
| **智慧青 (Smart Teal)** | `C_TEAL` (智慧青) | `#14C8B4` | `(20, 200, 180)` | 物联网、智能诊断、扩展图表系列 |
| **深蓝底座 (Deep Corporate Blue)** | `C_DEEP_BLUE` (企业深蓝) | `#1437AA` | `(20, 55, 170)` | 平台架构底座层、深色容器标题、大盘统计左侧卡片 |
| **浅蓝卡片底色 (Soft Blue BG)** | `C_BLUE_BG` (浅蓝容器) | `#EBF3FF` | `(235, 243, 255)` | 解决方案卡片背景、举措容器底色、高亮胶囊填充 |
| **冰蓝高亮 (Ice Blue)** | `C_ICE_BLUE` (冰蓝点缀) | `#D7F0FF` | `(215, 240, 255)` | 方案矩阵卡片头部装饰条、标签药丸 |
| **预警黄 (Warning Orange)** | `C_ORANGE` (预警黄) | `#F59E0B` | `(245, 158, 11)` | 中度风险标签、预警提醒 |
| **主标题深色文字 (Dark Text)** | `C_DARK` (正泰黑) | `#1E2024` | `(30, 32, 36)` | 卡片内一级标题、模块名称、表格表头文字 |
| **正文次级文字 (Muted Text)** | `C_MUTED` (深石板灰) | `#5A5A5A` | `(90, 90, 90)` | 正文内容、要点清单、描述性说明文字 |
| **容器轻浅底色 (Canvas Light)** | `C_LIGHT_BG` (浅灰容器) | `#F6F8FA` | `(246, 248, 250)` | 标准卡片背景填充底色 |
| **卡片浅灰边框 (Card Border)** | `C_BORDER` (标准描边) | `#D0D7DE` | `(208, 215, 222)` | 1pt 卡片边框、分隔线、表格内部网格线 |
| **纯白底色 (Pure White)** | `C_WHITE` (纯白) | `#FFFFFF` | `(255, 255, 255)` | 悬浮卡片主体、反白文字 |

---

## 2. Multi-series Data Chart 8-stage Palette (图表 8 阶色系)

在柱状图、条形图、折线图、环形图中，多系列数据严格按照以下顺序自动着色：
1. 系列 1 (主指标): `#1E50E6` (正泰蓝)
2. 系列 2 (对比指标): `#50C8FF` (亮青色)
3. 系列 3 (正向/增长): `#14C832` (生态绿)
4. 系列 4 (智能/物联): `#14C8B4` (智慧青)
5. 系列 5 (扩展蓝): `#2378FF`
6. 系列 6 (浅草绿): `#5ADC19`
7. 系列 7 (预警/重点): `#F59E0B`
8. 系列 8 (警示/风险): `#D70A32`

---

## 3. Typography Rules (正泰拓新体 / CHINTinno)

* **Primary Font Family**: `正泰拓新体` (CHINTinno) for all headers, body copy, numbers, and labels.
* **Hierarchy Standards**:
  - Slide Header Title: `20–22pt` Bold, `#1E50E6`
  - Cover Title: `28–34pt` Bold, `#FFFFFF`
  - Cover Subtitle: `13–15pt` Regular, `#FFFFFF`
  - Card Header / Section Subtitle: `13–15pt` Bold, `#1E50E6` or `#1E2024`
  - Body Text / Bullet Points: `11–12pt` Regular, `#5A5A5A`
  - Hero Metric Numbers: `32–42pt` Bold, `#FFFFFF` or `#1E50E6`
  - Footer Metadata: `9pt` Regular, `#A0A0A0`

---

## 4. Professional Visual Display Standards (60-30-10 & Spacing Hygiene)

* **60-30-10 Color Weight Law**:
  - 60% Dominant Canvas (`C_WHITE` #FFFFFF, `C_LIGHT_BG` #F6F8FA)
  - 30% Structural Brand Tone (`C_BLUE` #1E50E6, `C_BLUE_BG` #EBF3FF, `C_DARK` #1E2024)
  - 10% Sharp Focus/Accent (`C_CYAN` #50C8FF, `C_RED_TEXT` #D70A32, `C_GREEN` #14C832, `C_ORANGE` #F59E0B)

* **Spacing & Margin Hygiene**:
  - Slide Margins: Left/Right 0.8" minimum, Top 1.6" (leaving 0.8" for Header), Bottom 0.8"
  - Card Gap: 0.25" to 0.4" consistent spacing across horizontal/vertical arrays
  - Text Frame Margins: Always enforce strict internal padding `tf.margin_left = Pt(8)`, `tf.margin_right = Pt(8)`, `tf.margin_top = Pt(6)`, `tf.margin_bottom = Pt(6)` to eliminate text clipping.
  - Paragraph Spacing: Use `p.space_before = Pt(4~10)` instead of blank lines or empty text runs.

* **Anti-Pattern Prohibitions**:
  - No generic underlines under titles (use whitespace or subtle card backgrounds).
  - No single-side decorative borders or arbitrary color bands.
  - No text-only slides: always anchor content with card containers, KPI metric callouts, or structured multi-column blocks.



