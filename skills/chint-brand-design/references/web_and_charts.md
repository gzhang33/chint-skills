# CHINT Web UI, Dashboard & Chart Design Guidelines

This guide details the implementation of CHINT visual identity in Web applications, HTML dashboards, CSS frameworks, and chart rendering engines (Matplotlib, Seaborn, ECharts).

---

## 1. Web Frontend & CSS Token System

Include the core brand font and CSS properties:

```css
@import url('/assets/styles/chint-fonts.css');

:root {
  /* Brand Primary */
  --chint-primary: #1E50E6;
  --chint-primary-hover: #1E62DE;
  --chint-primary-dark: #1E50C8;
  --chint-primary-light: #50C8FF;
  --chint-gradient-banner: linear-gradient(90deg, #50C8FF 0%, #1E50C8 100%);

  /* Neutrals & Surfaces */
  --chint-bg-base: #F6F6F6;
  --chint-bg-surface: #FFFFFF;
  --chint-bg-subtle: #F3F6FE;
  --chint-border: #E2E8F0;
  --chint-border-input: #CBD5E1;

  /* Typography */
  --chint-text-dark: #191919;
  --chint-text-soft: #333333;
  --chint-text-muted: #666666;
  --font-chint: 'CHINTinno', 'Microsoft YaHei', 'PingFang SC', sans-serif;

  /* Semantic */
  --chint-status-success: #16A34A;
  --chint-status-warning: #D97706;
  --chint-status-error: #DC2626;
}

body {
  font-family: var(--font-chint);
  background-color: var(--chint-bg-base);
  color: var(--chint-text-dark);
  margin: 0;
  padding: 0;
}
```

---

## 2. Minimum UI & Copy Economy Rules

1. **Strict Zero-Emoji Policy**:
   - Never use non-professional decorative emojis in UI buttons, status tags, headers, or toasts.
   - Use unified vector icon libraries (such as `lucide-react` or `lucide`) for all visual state feedback and actions.
2. **High Information Density**:
   - Maintain compact paddings (`p-3` to `p-4`), tight gaps (`gap-3`), and crisp 1px borders (`border border-slate-200`).
3. **No Redundant Subtitles**:
   - Avoid self-evident subtitles under section headers.

---

## 3. Data Visualization Styling

### Matplotlib & Seaborn
Apply brand styling with one command using `scripts/chint_theme.py`:

```python
from scripts.chint_theme import apply_matplotlib_theme, get_chart_palette
import matplotlib.pyplot as plt

# 1. Apply global brand styling
apply_matplotlib_theme(plt)

# 2. Plot with official palette
palette = get_chart_palette()
fig, ax = plt.subplots(figsize=(10, 5), dpi=300)

categories = ['ACB (NXA)', 'MCCB (NXM)', 'Power Quality', 'ATS', 'Disconnector']
revenue = [480, 720, 210, 160, 95]

bars = ax.bar(categories, revenue, color=palette[0], width=0.55, edgecolor='none')
ax.set_title("2026 CHINT Low-Voltage Product Line Sales (Million RMB)", fontsize=14, fontweight='bold', pad=15)
ax.set_ylabel("Revenue (M)", fontsize=11)
ax.grid(axis='y', linestyle='--', alpha=0.5)

# Value labels on top of bars
for bar in bars:
    height = bar.get_height()
    ax.annotate(f'¥{height}',
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 3),
                textcoords="offset points",
                ha='center', va='bottom', fontsize=10, color='#191919')

plt.tight_layout()
plt.savefig("chint_sales_chart.png", dpi=300)
```

---

### Apache ECharts JSON Theme Configuration

```javascript
const chintEChartsTheme = {
  color: [
    "#1E50E6", // Electric Blue
    "#50C8FF", // Electric Cyan
    "#1E50C8", // Deep Blue
    "#0070C0", // Corporate Blue
    "#F59E0B", // Amber
    "#10B981", // Emerald Green
    "#6366F1", // Indigo
    "#EC4899"  // Pink
  ],
  backgroundColor: "#FFFFFF",
  textStyle: {
    fontFamily: "CHINTinno, 'Microsoft YaHei', 'PingFang SC', sans-serif",
    color: "#191919"
  },
  title: {
    textStyle: {
      color: "#191919",
      fontWeight: "bold",
      fontSize: 16
    }
  },
  line: {
    smooth: true,
    symbol: "circle",
    symbolSize: 6
  },
  grid: {
    top: 40,
    right: 20,
    bottom: 30,
    left: 50,
    borderColor: "#E2E8F0"
  },
  categoryAxis: {
    axisLine: { lineStyle: { color: "#CBD5E1" } },
    axisTick: { show: false },
    axisLabel: { color: "#666666" },
    splitLine: { show: false }
  },
  valueAxis: {
    axisLine: { show: false },
    axisTick: { show: false },
    axisLabel: { color: "#666666" },
    splitLine: { lineStyle: { color: "#E2E8F0", type: "dashed" } }
  }
};
```
