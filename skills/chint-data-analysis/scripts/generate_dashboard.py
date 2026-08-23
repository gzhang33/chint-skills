#!/usr/bin/env python3
"""
generate_dashboard.py — 断路器产品经理全响应式极简 HTML 仪表盘生成器 (保持顶部 KPI 看板恒定全球总览)

功能特性：
  1. 真实 CHINT 品牌 Logo2 (`chint_logo2.png`) 嵌入 (Base64 极简 100% 便携方案)。
  2. 顶部双行 KPI 看板：
     - 恒定保持全球全量总销售额、全量总数量、6 大大区（中国区+5海外洲区）完整构成不变。
  3. 极简 Pill 过滤控制条：
     - 年份 Pill (2026/2025/2024)
     - 全域视角 Pill ([全球 | 中国区 | 海外区]) -> 专属控制下方 4 大分析卡片
     - 季度 Pill (Q1/Q2/Q3/Q4)
     - 月份 Pill (多选)
  4. 卡片高级交互功能：
     - 半圆弧右上角图表/表格视角切卡按钮。
     - 全屏放大弹窗 (Fullscreen Modal) 按钮。
     - 无级拖拽缩放 (Stepless Resizing via ResizeObserver 动态调图)。
"""

import sys
import json
import base64
import argparse
from pathlib import Path
import duckdb

CURRENT_DIR = Path(__file__).resolve().parent

def _find_project_root(start_dir: Path) -> Path:
    curr = start_dir.resolve()
    for parent in [curr] + list(curr.parents):
        if (parent / "pyproject.toml").exists() or (parent / "README.md").exists() or (parent / "data" / "data.duckdb").exists():
            return parent
    return start_dir.parent


PROJECT_ROOT = _find_project_root(CURRENT_DIR)


for p in [str(PROJECT_ROOT), str(CURRENT_DIR)]:
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    from config_loader import get_excel_title_mappings, get_product_category_rules, get_common_rules
except ImportError:
    try:
        from etl.config_loader import get_excel_title_mappings, get_product_category_rules, get_common_rules
    except ImportError:
        def get_excel_title_mappings(): return {}
        def get_product_category_rules(cat=None): return {}
        def get_common_rules(): return {}


def get_duckdb_path():
    candidates = [
        CURRENT_DIR.parent / "data" / "sales.duckdb",
        PROJECT_ROOT / ".agents" / "skills" / "chint-data-analysis" / "data" / "sales.duckdb",
        PROJECT_ROOT / "data" / "database" / "acb.duckdb",
        PROJECT_ROOT / "data" / "database" / "data.duckdb",
        PROJECT_ROOT / "data" / "database" / "chint_analytics.duckdb",
        CURRENT_DIR.parent / "database" / "acb.duckdb",
        Path.cwd() / "data" / "database" / "acb.duckdb",
    ]
    for p in candidates:
        if p.exists():
            return p
    return candidates[0]



def load_chint_logo():
    """读取正泰 chint_logo2.png 转化为 Base64 HTML 图片标签"""
    possible_paths = [
        CURRENT_DIR.parent / "resources" / "chint_logo2.png",
        PROJECT_ROOT / ".agents" / "skills" / "chint-data-analysis" / "resources" / "chint_logo2.png",
        Path.home() / "Documents" / "chint" / "resources" / "品牌资产" / "chint_logo2.png",
        PROJECT_ROOT / "resources" / "chint_logo2.png"
    ]
    for p in possible_paths:
        if p.exists():
            b64 = base64.b64encode(p.read_bytes()).decode("utf-8")
            return f'<img src="data:image/png;base64,{b64}" alt="CHINT Logo" style="height:36px; width:auto; vertical-align:middle;" />'
    return """<div style="background:#1E50E6; color:#FFF; font-weight:900; font-size:18px; padding:4px 12px; border-radius:6px;">CHINT 正泰</div>"""


def build_preaggregated_payload(conn):
    """提取精简预聚合 JSON 荷载，包含中国区与海外区数据"""
    q_brand = """
    SELECT 'cn' as scope, year, month,
           CASE WHEN property_type = '本体' THEN 'benti' ELSE 'non_benti' END as property,
           CASE WHEN report_source LIKE '%诺雅克%' THEN '诺雅克' ELSE '正泰' END as brand,
           SUM(net_revenue / 10000.0) as rev, SUM(invoice_qty_benti) as qty
    FROM v_chint_cn_sales_all GROUP BY 1,2,3,4,5
    UNION ALL
    SELECT 'intl' as scope, year, month,
           CASE WHEN property_type = '本体' THEN 'benti' ELSE 'non_benti' END as property,
           CASE WHEN report_source LIKE '%诺雅克%' THEN '诺雅克' ELSE '正泰' END as brand,
           SUM(net_revenue / 10000.0) as rev, SUM(invoice_qty_benti) as qty
    FROM v_chint_intl_sales GROUP BY 1,2,3,4,5;
    """
    r_brand = conn.execute(q_brand).fetchdf().to_dict(orient="records")

    q_region_intl = """
    SELECT 'intl' as scope, year, month,
           CASE WHEN property_type = '本体' THEN 'benti' ELSE 'non_benti' END as property,
           region, SUM(net_revenue / 10000.0) as rev, SUM(invoice_qty_benti) as qty
    FROM v_chint_intl_sales GROUP BY 1,2,3,4,5;
    """
    r_region_intl = conn.execute(q_region_intl).fetchdf().to_dict(orient="records")

    q_region_cn = """
    SELECT 'cn' as scope, year, month,
           CASE WHEN property_type = '本体' THEN 'benti' ELSE 'non_benti' END as property,
           '中国区' as region, SUM(net_revenue / 10000.0) as rev, SUM(invoice_qty_benti) as qty
    FROM v_chint_cn_sales_all GROUP BY 1,2,3,4,5;
    """
    r_region_cn = conn.execute(q_region_cn).fetchdf().to_dict(orient="records")

    q_series = """
    SELECT 'cn' as scope, year, month,
           CASE WHEN property_type = '本体' THEN 'benti' ELSE 'non_benti' END as property,
           COALESCE(product_series, '其它') as series,
           SUM(net_revenue / 10000.0) as rev, SUM(invoice_qty_benti) as qty
    FROM v_chint_cn_sales_all GROUP BY 1,2,3,4,5
    UNION ALL
    SELECT 'intl' as scope, year, month,
           CASE WHEN property_type = '本体' THEN 'benti' ELSE 'non_benti' END as property,
           COALESCE(product_series, '其它') as series,
           SUM(net_revenue / 10000.0) as rev, SUM(invoice_qty_benti) as qty
    FROM v_chint_intl_sales GROUP BY 1,2,3,4,5;
    """
    r_series = conn.execute(q_series).fetchdf().to_dict(orient="records")

    q_team = """
    SELECT 'cn' as scope, year, month,
           CASE WHEN property_type = '本体' THEN 'benti' ELSE 'non_benti' END as property,
           COALESCE(sales_team, '其它') as team,
           SUM(net_revenue / 10000.0) as rev, SUM(invoice_qty_benti) as qty
    FROM v_chint_cn_sales_all GROUP BY 1,2,3,4,5
    UNION ALL
    SELECT 'intl' as scope, year, month,
           CASE WHEN property_type = '本体' THEN 'benti' ELSE 'non_benti' END as property,
           COALESCE(region, '海外区') as team,
           SUM(net_revenue / 10000.0) as rev, SUM(invoice_qty_benti) as qty
    FROM v_chint_intl_sales GROUP BY 1,2,3,4,5;
    """
    r_team = conn.execute(q_team).fetchdf().to_dict(orient="records")

    q_country = """
    SELECT year, month,
           CASE WHEN property_type = '本体' THEN 'benti' ELSE 'non_benti' END as property,
           COALESCE(country, '其它') as country, COALESCE(region, '其它') as region,
           SUM(net_revenue / 10000.0) as rev, SUM(invoice_qty_benti) as qty
    FROM v_chint_intl_sales GROUP BY 1,2,3,4,5;
    """
    r_country = conn.execute(q_country).fetchdf().to_dict(orient="records")

    return {
        "brands": r_brand,
        "regions": r_region_intl + r_region_cn,
        "series": r_series,
        "teams": r_team,
        "countries": r_country
    }


def build_dashboard_html(payload_data: dict, year: int = 2026) -> str:
    payload_json = json.dumps(payload_data, ensure_ascii=False)
    logo_tag = load_chint_logo()

    template = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>正泰电气 - 配电断路器多维分析仪表盘</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <style>
    @font-face {
      font-family: 'CHINTinno';
      src: local('CHINTinno'), local('正泰拓新体');
    }

    :root {
      --chint-primary: #1E50E6;
      --chint-primary-hover: #1640B8;
      --noark-primary: #5cb531;
      --bg-base: #090D16;
      --bg-surface: rgba(21, 29, 46, 0.92);
      --border-color: rgba(255, 255, 255, 0.1);
      --text-main: #F8FAFC;
      --text-muted: #94A3B8;
      --font-family: 'CHINTinno', 'PingFang SC', 'Microsoft YaHei', sans-serif;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; font-family: var(--font-family); }
    body { background: var(--bg-base); color: var(--text-main); min-height: 100vh; padding: 16px; }

    .dashboard-navbar {
      display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 16px;
      padding: 12px 20px; background: var(--bg-surface); backdrop-filter: blur(12px);
      border: 1px solid var(--border-color); border-radius: 12px; margin-bottom: 14px;
    }
    .brand-wrap { display: flex; align-items: center; gap: 14px; }
    .svg-logo-box img { height: 36px; width: auto; vertical-align: middle; }
    .nav-title h1 { font-size: 18px; font-weight: 800; color: #FFF; }

    .filter-section { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; background: var(--bg-surface); border: 1px solid var(--border-color); border-radius: 12px; padding: 10px 16px; margin-bottom: 14px; }
    .pill-label { font-size: 12px; font-weight: 700; color: var(--text-muted); margin-right: 2px; }
    .pill-group { display: flex; background: rgba(10, 15, 26, 0.8); border: 1px solid var(--border-color); border-radius: 8px; padding: 3px; gap: 2px; flex-wrap: wrap; }
    
    .pill-btn {
      background: transparent; border: none; color: var(--text-muted); padding: 5px 12px; border-radius: 6px;
      font-size: 12px; font-weight: 600; cursor: pointer; transition: all 0.15s; outline: none;
    }
    .pill-btn:hover { color: #FFF; background: rgba(255,255,255,0.05); }
    .pill-btn.active { background: var(--chint-primary); color: #FFF; box-shadow: 0 2px 8px rgba(30,80,230,0.4); }
    .pill-btn.scope-active { background: #00A3FF; color: #FFF; box-shadow: 0 2px 8px rgba(0,163,255,0.4); }
    .pill-btn.multi-active { background: rgba(30, 80, 230, 0.3); color: #60A5FA; border: 1px solid rgba(30,80,230,0.5); }

    .kpi-banner-wrap { display: flex; flex-direction: column; gap: 12px; margin-bottom: 14px; }
    .kpi-hero-row { display: grid; grid-template-columns: 310px 1fr; gap: 10px; background: var(--bg-surface); border: 1px solid var(--border-color); border-radius: 12px; overflow: hidden; }

    .hero-main-card {
      background: linear-gradient(135deg, #1E50E6 0%, #0044B8 100%); padding: 16px; color: #FFF;
      display: flex; flex-direction: column; justify-content: space-between;
    }
    .hero-main-card.qty-theme { background: linear-gradient(135deg, #00A3FF 0%, #0055B8 100%); }
    .hero-title { font-size: 15px; font-weight: 800; opacity: 0.95; }
    .hero-num-badge-wrap { display: flex; justify-content: space-between; align-items: center; margin: 8px 0; }
    .hero-main-num { font-size: 28px; font-weight: 900; letter-spacing: -0.5px; }
    
    .circle-badge {
      width: 62px; height: 62px; border-radius: 50%; border: 2px solid rgba(255, 255, 255, 0.4);
      display: flex; flex-direction: column; justify-content: center; align-items: center;
      background: rgba(255, 255, 255, 0.15); backdrop-filter: blur(4px); text-align: center;
    }
    .circle-badge-label { font-size: 9px; opacity: 0.8; line-height: 1.1; }
    .circle-badge-val { font-size: 12px; font-weight: 800; }

    .hero-sub-brands { font-size: 11px; opacity: 0.9; display: flex; flex-direction: column; gap: 3px; border-top: 1px solid rgba(255, 255, 255, 0.2); padding-top: 6px; }

    .hero-region-grid-wrap { display: flex; flex-direction: column; justify-content: space-between; padding: 10px 12px; background: rgba(10, 15, 26, 0.5); }
    .hero-region-grid { display: grid; grid-template-columns: repeat(6, 1fr); gap: 6px; }
    .region-card {
      background: rgba(21, 29, 46, 0.8); border: 1px solid var(--border-color); border-radius: 8px; padding: 8px; text-align: center;
    }
    .region-card-title { font-size: 11px; font-weight: 700; color: #60A5FA; margin-bottom: 2px; border-bottom: 1px solid rgba(255,255,255,0.06); padding-bottom: 2px; }
    .region-card-num { font-size: 15px; font-weight: 800; color: #FFF; margin: 3px 0; }
    .region-card-meta { font-size: 10px; color: var(--text-muted); line-height: 1.2; }

    .overseas-summary-strip {
      margin-top: 6px; background: rgba(30, 80, 230, 0.12); border: 1px solid rgba(30, 80, 230, 0.25);
      padding: 5px 12px; border-radius: 6px; font-size: 11px; display: flex; justify-content: space-around; align-items: center; font-weight: 600;
    }

    .cards-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 14px; }
    @media (max-width: 1024px) { .cards-grid { grid-template-columns: 1fr; } .hero-region-grid { grid-template-columns: repeat(3, 1fr); } }

    /* 支持无级拖拽缩放 (Stepless Resizing) */
    .chart-card {
      background: var(--bg-surface); border: 1px solid var(--border-color); border-radius: 12px; padding: 14px;
      position: relative; resize: both; overflow: auto; min-width: 320px; min-height: 280px;
    }
    .chart-card::-webkit-resizer {
      background-color: rgba(30, 80, 230, 0.6);
      border-radius: 0 0 10px 0;
    }

    .chart-card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
    .chart-card-title { font-size: 14px; font-weight: 700; display: flex; align-items: center; gap: 6px; color: #FFF; }
    .chart-card-title::before { content: ""; display: inline-block; width: 4px; height: 13px; background: var(--chint-primary); border-radius: 2px; }

    .btn-group-right { display: flex; align-items: center; gap: 6px; }

    .arc-switch-btn {
      width: 32px; height: 32px; border-radius: 50% 10px 50% 50%;
      background: rgba(30, 80, 230, 0.25); border: 1px solid rgba(30, 80, 230, 0.5);
      color: #60A5FA; display: flex; justify-content: center; align-items: center;
      cursor: pointer; transition: all 0.2s ease; outline: none; padding: 0;
    }
    .arc-switch-btn:hover {
      background: var(--chint-primary); color: #FFF; transform: rotate(15deg) scale(1.08);
      box-shadow: 0 4px 12px rgba(30,80,230,0.5);
    }
    .arc-switch-btn svg { width: 16px; height: 16px; fill: currentColor; }

    .comp-table { width: 100%; border-collapse: collapse; text-align: center; font-size: 12px; }
    .comp-table th { background: #1E50E6; color: #FFF; padding: 8px 6px; border: 1px solid rgba(255,255,255,0.15); font-weight: 700; }
    .comp-table th.sub-th { background: #1640B8; font-size: 11px; }
    .comp-table td { padding: 7px 5px; border: 1px solid rgba(255,255,255,0.06); color: #E2E8F0; }
    .comp-table tr.total-row td { background: rgba(94, 114, 140, 0.35); font-weight: 800; color: #FFF; }
    .comp-table tr:hover td { background: rgba(30, 80, 230, 0.15); }

    /* 全屏放大弹窗 modal */
    .modal-overlay {
      display: none; position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
      background: rgba(9, 13, 22, 0.88); backdrop-filter: blur(16px); z-index: 9999;
      justify-content: center; align-items: center; padding: 24px;
    }
    .modal-card {
      background: var(--bg-surface); border: 1px solid rgba(255, 255, 255, 0.2);
      border-radius: 16px; width: 92vw; height: 88vh; padding: 20px;
      display: flex; flex-direction: column; position: relative; box-shadow: 0 20px 50px rgba(0,0,0,0.8);
    }
    .modal-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; padding-bottom: 12px; border-bottom: 1px solid var(--border-color); }
    .modal-title { font-size: 18px; font-weight: 800; color: #FFF; }
    .modal-close-btn {
      background: rgba(255,255,255,0.1); border: none; color: #FFF; width: 36px; height: 36px;
      border-radius: 50%; font-size: 18px; font-weight: 700; cursor: pointer; transition: all 0.2s;
    }
    .modal-close-btn:hover { background: #E63946; transform: scale(1.1); }
    .modal-body { flex: 1; overflow: auto; display: flex; justify-content: center; align-items: center; }
  </style>
</head>
<body>

  <!-- Minimalist Top Navbar -->
  <header class="dashboard-navbar">
    <div class="brand-wrap">
      <div class="svg-logo-box">__LOGO_TAG__</div>
      <div class="nav-title">
        <h1>正泰电气 - 配电断路器分析仪表盘</h1>
      </div>
    </div>
  </header>

  <!-- 极简 Pill 过滤控制条 -->
  <section class="filter-section">
    <span class="pill-label">卡片视角切片:</span>
    <div class="pill-group" id="scopePillGroup">
      <button class="pill-btn scope-active" onclick="setScope('global', this)">全 球</button>
      <button class="pill-btn" onclick="setScope('cn', this)">中国区</button>
      <button class="pill-btn" onclick="setScope('intl', this)">海外区</button>
    </div>

    <span class="pill-label" style="margin-left:8px;">年份:</span>
    <div class="pill-group" id="yearPillGroup">
      <button class="pill-btn active" onclick="setYear(2026, this)">2026年</button>
      <button class="pill-btn" onclick="setYear(2025, this)">2025年</button>
      <button class="pill-btn" onclick="setYear(2024, this)">2024年</button>
    </div>

    <span class="pill-label" style="margin-left:8px;">季度:</span>
    <div class="pill-group" id="quarterPillGroup">
      <button class="pill-btn active" onclick="setQuarter('all', this)">全季度</button>
      <button class="pill-btn" onclick="setQuarter('Q1', this)">Q1 (1-3月)</button>
      <button class="pill-btn" onclick="setQuarter('Q2', this)">Q2 (4-6月)</button>
      <button class="pill-btn" onclick="setQuarter('Q3', this)">Q3 (7-9月)</button>
      <button class="pill-btn" onclick="setQuarter('Q4', this)">Q4 (10-12月)</button>
    </div>

    <span class="pill-label" style="margin-left:8px;">月份:</span>
    <div class="pill-group" id="monthPillGroup">
      <button class="pill-btn active" onclick="resetMonths(this)">全月份</button>
      <button class="pill-btn" onclick="toggleMonth(1, this)">1月</button>
      <button class="pill-btn" onclick="toggleMonth(2, this)">2月</button>
      <button class="pill-btn" onclick="toggleMonth(3, this)">3月</button>
      <button class="pill-btn" onclick="toggleMonth(4, this)">4月</button>
      <button class="pill-btn" onclick="toggleMonth(5, this)">5月</button>
      <button class="pill-btn" onclick="toggleMonth(6, this)">6月</button>
      <button class="pill-btn" onclick="toggleMonth(7, this)">7月</button>
      <button class="pill-btn" onclick="toggleMonth(8, this)">8月</button>
      <button class="pill-btn" onclick="toggleMonth(9, this)">9月</button>
      <button class="pill-btn" onclick="toggleMonth(10, this)">10月</button>
      <button class="pill-btn" onclick="toggleMonth(11, this)">11月</button>
      <button class="pill-btn" onclick="toggleMonth(12, this)">12月</button>
    </div>
  </section>

  <!-- ═══ 恒定全球总览双行 KPI 看板 (包含完整中国区与海外区) ═══ -->
  <section class="kpi-banner-wrap">
    <div class="kpi-hero-row">
      <div class="hero-main-card">
        <div class="hero-title">大盘销售总额 (全量属性)</div>
        <div class="hero-num-badge-wrap">
          <div class="hero-main-num" id="heroRevNum">¥0 元</div>
          <div class="circle-badge">
            <div class="circle-badge-label">增长率</div>
            <div class="circle-badge-val" id="heroRevYoy">0%</div>
          </div>
        </div>
        <div class="hero-sub-brands">
          <div id="subChintRev">正泰 --元  同比--  占比--</div>
          <div id="subNoarkRev">诺雅克 --元  同比--  占比--</div>
        </div>
      </div>

      <div class="hero-region-grid-wrap">
        <div class="hero-region-grid" id="revRegionGrid"></div>
        <div class="overseas-summary-strip" id="revOverseasStrip"></div>
      </div>
    </div>

    <div class="kpi-hero-row">
      <div class="hero-main-card qty-theme">
        <div class="hero-title">大盘销售数量 (本体台数)</div>
        <div class="hero-num-badge-wrap">
          <div class="hero-main-num" id="heroQtyNum">0 台</div>
          <div class="circle-badge">
            <div class="circle-badge-label">增长率</div>
            <div class="circle-badge-val" id="heroQtyYoy">0%</div>
          </div>
        </div>
        <div class="hero-sub-brands">
          <div id="subChintQty">正泰 --台  同比--  占比--</div>
          <div id="subNoarkQty">诺雅克 --台  同比--  占比--</div>
        </div>
      </div>

      <div class="hero-region-grid-wrap">
        <div class="hero-region-grid" id="qtyRegionGrid"></div>
        <div class="overseas-summary-strip" id="qtyOverseasStrip"></div>
      </div>
    </div>
  </section>

  <!-- ═══ 4 大分析卡片 Grid (受卡片视角切片控制，支持无级缩放与全屏弹窗) ═══ -->
  <main class="cards-grid">
    <div class="chart-card" id="c1_card">
      <div class="chart-card-header">
        <div class="chart-card-title" id="c1_title">主力产品系列销售表现</div>
        <div class="btn-group-right">
          <button class="arc-switch-btn" title="切卡视角" onclick="toggleCardView('c1', this)">
            <svg viewBox="0 0 24 24"><path d="M4 5h16v2H4V5zm0 6h16v2H4v-2zm0 6h16v2H4v-2z"/></svg>
          </button>
          <button class="arc-switch-btn" title="全屏放大" onclick="openFullscreenModal('c1')">
            <svg viewBox="0 0 24 24"><path d="M7 14H5v5h5v-2H7v-3zm-2-4h2V7h3V5H5v5zm12 7h-3v2h5v-5h-2v3zM14 5v2h3v3h2V5h-5z"/></svg>
          </button>
        </div>
      </div>
      <div id="c1_chart_box"><canvas id="cnSeriesChart" height="210"></canvas></div>
      <div id="c1_table_box" style="display:none;" class="comparison-table-wrap"></div>
    </div>

    <div class="chart-card" id="c2_card">
      <div class="chart-card-header">
        <div class="chart-card-title" id="c2_title">行业团队与区域渠道销售分布</div>
        <div class="btn-group-right">
          <button class="arc-switch-btn" title="切卡视角" onclick="toggleCardView('c2', this)">
            <svg viewBox="0 0 24 24"><path d="M4 5h16v2H4V5zm0 6h16v2H4v-2zm0 6h16v2H4v-2z"/></svg>
          </button>
          <button class="arc-switch-btn" title="全屏放大" onclick="openFullscreenModal('c2')">
            <svg viewBox="0 0 24 24"><path d="M7 14H5v5h5v-2H7v-3zm-2-4h2V7h3V5H5v5zm12 7h-3v2h5v-5h-2v3zM14 5v2h3v3h2V5h-5z"/></svg>
          </button>
        </div>
      </div>
      <div id="c2_chart_box"><canvas id="teamChart" height="210"></canvas></div>
      <div id="c2_table_box" style="display:none;" class="comparison-table-wrap"></div>
    </div>

    <div class="chart-card" id="c3_card">
      <div class="chart-card-header">
        <div class="chart-card-title" id="c3_title">海外出口 Top 10 国家分布</div>
        <div class="btn-group-right">
          <button class="arc-switch-btn" title="切卡视角" onclick="toggleCardView('c3', this)">
            <svg viewBox="0 0 24 24"><path d="M4 5h16v2H4V5zm0 6h16v2H4v-2zm0 6h16v2H4v-2z"/></svg>
          </button>
          <button class="arc-switch-btn" title="全屏放大" onclick="openFullscreenModal('c3')">
            <svg viewBox="0 0 24 24"><path d="M7 14H5v5h5v-2H7v-3zm-2-4h2V7h3V5H5v5zm12 7h-3v2h5v-5h-2v3zM14 5v2h3v3h2V5h-5z"/></svg>
          </button>
        </div>
      </div>
      <div id="c3_chart_box"><canvas id="intlCountryChart" height="210"></canvas></div>
      <div id="c3_table_box" style="display:none;" class="comparison-table-wrap"></div>
    </div>

    <div class="chart-card" id="c4_card">
      <div class="chart-card-header">
        <div class="chart-card-title" id="c4_title">各品类系列营收与对比明细</div>
        <div class="btn-group-right">
          <button class="arc-switch-btn" title="切卡视角" onclick="toggleCardView('c4', this)">
            <svg viewBox="0 0 24 24"><path d="M5 9h3v12H5V9zm6-4h3v16h-3V5zm6 7h3v9h-3v-9z"/></svg>
          </button>
          <button class="arc-switch-btn" title="全屏放大" onclick="openFullscreenModal('c4')">
            <svg viewBox="0 0 24 24"><path d="M7 14H5v5h5v-2H7v-3zm-2-4h2V7h3V5H5v5zm12 7h-3v2h5v-5h-2v3zM14 5v2h3v3h2V5h-5z"/></svg>
          </button>
        </div>
      </div>
      <div id="c4_chart_box" style="display:none;"><canvas id="seriesBarChart" height="210"></canvas></div>
      <div id="c4_table_box" class="comparison-table-wrap"></div>
    </div>
  </main>

  <!-- 全屏放大 Modal 弹窗 -->
  <div class="modal-overlay" id="fullscreenModal">
    <div class="modal-card">
      <div class="modal-header">
        <div class="modal-title" id="modalTitle">全屏卡片视图</div>
        <button class="modal-close-btn" onclick="closeFullscreenModal()">✕</button>
      </div>
      <div class="modal-body" id="modalBody"></div>
    </div>
  </div>

  <script>
    const PAYLOAD = __PAYLOAD_JSON__;
    
    let state = {
      scope: "global",
      year: __EVAL_YEAR__,
      quarter: "all",
      selectedMonths: []
    };

    let cardViews = { c1: "chart", c2: "chart", c3: "chart", c4: "table" };
    let chartObjs = {};

    const QUARTER_MONTHS = {
      Q1: [1, 2, 3], Q2: [4, 5, 6], Q3: [7, 8, 9], Q4: [10, 11, 12]
    };

    function setScope(scope, btn) {
      state.scope = scope;
      setActivePill("scopePillGroup", btn, "scope-active");
      recalculateAndRender();
    }
    function setYear(y, btn) {
      state.year = y;
      setActivePill("yearPillGroup", btn);
      recalculateAndRender();
    }
    function setQuarter(q, btn) {
      state.quarter = q;
      state.selectedMonths = [];
      setActivePill("quarterPillGroup", btn);
      resetMonthPillsUI();
      recalculateAndRender();
    }
    function toggleMonth(m, btn) {
      state.quarter = "custom";
      setActivePill("quarterPillGroup", null);
      
      const idx = state.selectedMonths.indexOf(m);
      if (idx > -1) {
        state.selectedMonths.splice(idx, 1);
        btn.classList.remove("multi-active");
      } else {
        state.selectedMonths.push(m);
        btn.classList.add("multi-active");
      }
      document.querySelector("#monthPillGroup .pill-btn").classList.remove("active");
      recalculateAndRender();
    }
    function resetMonths(btn) {
      state.quarter = "all";
      state.selectedMonths = [];
      setActivePill("quarterPillGroup", document.querySelector("#quarterPillGroup .pill-btn"));
      resetMonthPillsUI();
      recalculateAndRender();
    }

    function setActivePill(groupId, btn, activeClass = "active") {
      const group = document.getElementById(groupId);
      if (!group) return;
      group.querySelectorAll(".pill-btn").forEach(b => b.classList.remove("active", "scope-active"));
      if (btn) btn.classList.add(activeClass);
    }

    function resetMonthPillsUI() {
      const group = document.getElementById("monthPillGroup");
      group.querySelectorAll(".pill-btn").forEach(b => b.classList.remove("multi-active", "active"));
      group.querySelector(".pill-btn").classList.add("active");
    }

    function toggleCardView(cardId, btn) {
      const chartBox = document.getElementById(cardId + "_chart_box");
      const tableBox = document.getElementById(cardId + "_table_box");

      if (cardViews[cardId] === "chart") {
        cardViews[cardId] = "table";
        chartBox.style.display = "none";
        tableBox.style.display = "block";
        btn.innerHTML = `<svg viewBox="0 0 24 24"><path d="M5 9h3v12H5V9zm6-4h3v16h-3V5zm6 7h3v9h-3v-9z"/></svg>`;
      } else {
        cardViews[cardId] = "chart";
        tableBox.style.display = "none";
        chartBox.style.display = "block";
        btn.innerHTML = `<svg viewBox="0 0 24 24"><path d="M4 5h16v2H4V5zm0 6h16v2H4v-2zm0 6h16v2H4v-2z"/></svg>`;
        if (chartObjs[cardId]) {
          setTimeout(() => chartObjs[cardId].resize(), 50);
        }
      }
    }

    function openFullscreenModal(cardId) {
      const modal = document.getElementById("fullscreenModal");
      const titleElem = document.getElementById("c" + cardId.replace("c","") + "_title");
      document.getElementById("modalTitle").innerText = (titleElem ? titleElem.innerText : "卡片全屏视图");
      
      const modalBody = document.getElementById("modalBody");
      modalBody.innerHTML = "";

      if (cardViews[cardId] === "table") {
        const tableBox = document.getElementById(cardId + "_table_box");
        modalBody.innerHTML = `<div style="width:100%; overflow:auto;">${tableBox.innerHTML}</div>`;
      } else {
        const canvas = document.createElement("canvas");
        canvas.id = "modalCanvas";
        modalBody.appendChild(canvas);
        
        modal.style.display = "flex";
        setTimeout(() => {
          const srcChart = chartObjs[cardId];
          if (srcChart) {
            new Chart(canvas.getContext("2d"), {
              type: srcChart.config.type,
              data: JSON.parse(JSON.stringify(srcChart.config.data)),
              options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { labels: { color: "#FFF", font: { size: 14 } } } } }
            });
          }
        }, 100);
        return;
      }
      modal.style.display = "flex";
    }

    function closeFullscreenModal() {
      document.getElementById("fullscreenModal").style.display = "none";
    }

    // 通用记录过滤（ignoreScope=true 时忽略 scope，专门用于顶部 KPI 看板恒定呈现全球完整数据）
    function filterRecords(records, targetYear, propertyFilter = null, ignoreScope = false) {
      return records.filter(r => {
        if (!ignoreScope && state.scope !== "global" && r.scope && r.scope !== state.scope) return false;
        if (r.year !== targetYear) return false;
        if (propertyFilter && r.property !== propertyFilter) return false;
        
        if (state.selectedMonths.length > 0) {
          if (!state.selectedMonths.includes(r.month)) return false;
        } else if (state.quarter !== "all") {
          const qMonths = QUARTER_MONTHS[state.quarter] || [];
          if (!qMonths.includes(r.month)) return false;
        }
        return true;
      });
    }

    function recalculateAndRender() {
      const currYear = state.year;
      const prevYear = currYear - 1;

      // ═══ 1. 顶部 KPI 看板：恒定过滤全球完整数据 (ignoreScope = true) ═══
      const bCurrAll = filterRecords(PAYLOAD.brands, currYear, null, true);
      const bPrevAll = filterRecords(PAYLOAD.brands, prevYear, null, true);
      const bCurrBenti = filterRecords(PAYLOAD.brands, currYear, "benti", true);
      const bPrevBenti = filterRecords(PAYLOAD.brands, prevYear, "benti", true);

      let chintRev = 0, noarkRev = 0;
      bCurrAll.forEach(r => {
        if (r.brand === "诺雅克") { noarkRev += r.rev; }
        else { chintRev += r.rev; }
      });

      let chintRevP = 0, noarkRevP = 0;
      bPrevAll.forEach(r => {
        if (r.brand === "诺雅克") { noarkRevP += r.rev; }
        else { chintRevP += r.rev; }
      });

      let chintQty = 0, noarkQty = 0;
      bCurrBenti.forEach(r => {
        if (r.brand === "诺雅克") { noarkQty += r.qty; }
        else { chintQty += r.qty; }
      });

      let chintQtyP = 0, noarkQtyP = 0;
      bPrevBenti.forEach(r => {
        if (r.brand === "诺雅克") { noarkQtyP += r.qty; }
        else { chintQtyP += r.qty; }
      });

      const rCurrAll = filterRecords(PAYLOAD.regions, currYear, null, true);
      const rPrevAll = filterRecords(PAYLOAD.regions, prevYear, null, true);
      const rCurrBenti = filterRecords(PAYLOAD.regions, currYear, "benti", true);
      const rPrevBenti = filterRecords(PAYLOAD.regions, prevYear, "benti", true);

      const overseasRegions = ["欧洲区", "亚太区", "西亚非洲区", "北美区", "拉美洲区"];
      let regRevCurrDict = {}, regRevPrevDict = {};
      let regQtyCurrDict = {}, regQtyPrevDict = {};

      rCurrAll.forEach(r => {
        if (!regRevCurrDict[r.region]) regRevCurrDict[r.region] = 0;
        regRevCurrDict[r.region] += r.rev;
      });
      rPrevAll.forEach(r => {
        if (!regRevPrevDict[r.region]) regRevPrevDict[r.region] = 0;
        regRevPrevDict[r.region] += r.rev;
      });

      rCurrBenti.forEach(r => {
        if (!regQtyCurrDict[r.region]) regQtyCurrDict[r.region] = 0;
        regQtyCurrDict[r.region] += r.qty;
      });
      rPrevBenti.forEach(r => {
        if (!regQtyPrevDict[r.region]) regQtyPrevDict[r.region] = 0;
        regQtyPrevDict[r.region] += r.qty;
      });

      let cnRev = regRevCurrDict["中国区"] || 0;
      let cnQty = regQtyCurrDict["中国区"] || 0;
      let cnRevP = regRevPrevDict["中国区"] || 0;
      let cnQtyP = regQtyPrevDict["中国区"] || 0;

      let intlRev = 0, intlQty = 0, intlRevP = 0, intlQtyP = 0;
      overseasRegions.forEach(reg => {
        if (regRevCurrDict[reg]) intlRev += regRevCurrDict[reg];
        if (regRevPrevDict[reg]) intlRevP += regRevPrevDict[reg];
        if (regQtyCurrDict[reg]) intlQty += regQtyCurrDict[reg];
        if (regQtyPrevDict[reg]) intlQtyP += regQtyPrevDict[reg];
      });

      let totRev = cnRev + intlRev;
      let totQty = cnQty + intlQty;
      let totRevP = cnRevP + intlRevP;
      let totQtyP = cnQtyP + intlQtyP;

      let yoyTotRev = totRevP > 0 ? ((totRev - totRevP) / totRevP * 100.0) : 0;
      let yoyTotQty = totQtyP > 0 ? ((totQty - totQtyP) / totQtyP * 100.0) : 0;

      document.getElementById("heroRevNum").innerText = "¥" + totRev.toLocaleString(undefined, {maximumFractionDigits:2}) + " 万";
      document.getElementById("heroRevYoy").innerText = (yoyTotRev >= 0 ? "+" : "") + yoyTotRev.toFixed(1) + "%";

      let cRevShare = totRev > 0 ? (chintRev / totRev * 100).toFixed(1) : "0.0";
      let nRevShare = totRev > 0 ? (noarkRev / totRev * 100).toFixed(1) : "0.0";
      let cRevYoY = chintRevP > 0 ? ((chintRev - chintRevP) / chintRevP * 100).toFixed(1) : "0.0";
      let nRevYoY = noarkRevP > 0 ? ((noarkRev - noarkRevP) / noarkRevP * 100).toFixed(1) : "0.0";

      document.getElementById("subChintRev").innerText = `正泰 ¥${chintRev.toLocaleString(undefined,{maximumFractionDigits:2})}万  同比${cRevYoY>=0?'+':''}${cRevYoY}%  占比${cRevShare}%`;
      document.getElementById("subNoarkRev").innerText = `诺雅克 ¥${noarkRev.toLocaleString(undefined,{maximumFractionDigits:2})}万  同比${nRevYoY>=0?'+':''}${nRevYoY}%  占比${nRevShare}%`;

      document.getElementById("heroQtyNum").innerText = totQty.toLocaleString() + " 台";
      document.getElementById("heroQtyYoy").innerText = (yoyTotQty >= 0 ? "+" : "") + yoyTotQty.toFixed(1) + "%";

      let cQtyShare = totQty > 0 ? (chintQty / totQty * 100).toFixed(1) : "0.0";
      let nQtyShare = totQty > 0 ? (noarkQty / totQty * 100).toFixed(1) : "0.0";
      let cQtyYoY = chintQtyP > 0 ? ((chintQty - chintQtyP) / chintQtyP * 100).toFixed(1) : "0.0";
      let nQtyYoY = noarkQtyP > 0 ? ((noarkQty - noarkQtyP) / noarkQtyP * 100).toFixed(1) : "0.0";

      document.getElementById("subChintQty").innerText = `正泰 ${chintQty.toLocaleString()}台  同比${cQtyYoY>=0?'+':''}${cQtyYoY}%  占比${cQtyShare}%`;
      document.getElementById("subNoarkQty").innerText = `诺雅克 ${noarkQty.toLocaleString()}台  同比${nQtyYoY>=0?'+':''}${nQtyYoY}%  占比${nQtyShare}%`;

      const revGrid = document.getElementById("revRegionGrid");
      const qtyGrid = document.getElementById("qtyRegionGrid");
      revGrid.innerHTML = "";
      qtyGrid.innerHTML = "";

      const all6Regions = ["中国区", ...overseasRegions];
      all6Regions.forEach(reg => {
        let rv = regRevCurrDict[reg] || 0;
        let qt = regQtyCurrDict[reg] || 0;
        let rvP = regRevPrevDict[reg] || 0;
        let qtP = regQtyPrevDict[reg] || 0;

        let yR = rvP > 0 ? ((rv - rvP) / rvP * 100).toFixed(1) : "0.0";
        let yQ = qtP > 0 ? ((qt - qtP) / qtP * 100).toFixed(1) : "0.0";
        let sR = totRev > 0 ? (rv / totRev * 100).toFixed(1) : "0.0";
        let sQ = totQty > 0 ? (qt / totQty * 100).toFixed(1) : "0.0";

        revGrid.innerHTML += `
          <div class="region-card">
            <div class="region-card-title">${reg}</div>
            <div class="region-card-num">¥${rv.toLocaleString(undefined,{maximumFractionDigits:2})}元</div>
            <div class="region-card-meta">增长率: ${yR>=0?'+':''}${yR}%<br>销售占比: ${sR}%</div>
          </div>
        `;

        qtyGrid.innerHTML += `
          <div class="region-card">
            <div class="region-card-title">${reg}</div>
            <div class="region-card-num">${qt.toLocaleString()}台</div>
            <div class="region-card-meta">增长率: ${yQ>=0?'+':''}${yQ}%<br>销售占比: ${sQ}%</div>
          </div>
        `;
      });

      let intlRevYoY = intlRevP > 0 ? ((intlRev - intlRevP) / intlRevP * 100).toFixed(1) : "0.0";
      let intlQtyYoY = intlQtyP > 0 ? ((intlQty - intlQtyP) / intlQtyP * 100).toFixed(1) : "0.0";
      let intlRevShare = totRev > 0 ? (intlRev / totRev * 100).toFixed(1) : "0.0";
      let intlQtyShare = totQty > 0 ? (intlQty / totQty * 100).toFixed(1) : "0.0";

      document.getElementById("revOverseasStrip").innerHTML = `
        <span>海外洲区总计: ¥${intlRev.toLocaleString(undefined,{maximumFractionDigits:2})}元</span>
        <span>总增长率: ${intlRevYoY>=0?'+':''}${intlRevYoY}%</span>
        <span>销售占比: ${intlRevShare}%</span>
      `;
      document.getElementById("qtyOverseasStrip").innerHTML = `
        <span>海外洲区总计: ${intlQty.toLocaleString()}台</span>
        <span>总增长率: ${intlQtyYoY>=0?'+':''}${intlQtyYoY}%</span>
        <span>销售占比: ${intlQtyShare}%</span>
      `;

      // ═══ 2. 下方 4 大分析卡片：受切片控制 (ignoreScope = false) ═══
      const scopeTitleMap = { global: "全球", cn: "中国区", intl: "海外区" };
      document.getElementById("c1_title").innerText = `${scopeTitleMap[state.scope]}主力产品系列销售表现`;

      const sCurrAll = filterRecords(PAYLOAD.series, currYear, null);
      const sPrevAll = filterRecords(PAYLOAD.series, prevYear, null);
      const sCurrBenti = filterRecords(PAYLOAD.series, currYear, "benti");
      const sPrevBenti = filterRecords(PAYLOAD.series, prevYear, "benti");

      let sCurrMap = {}, sPrevMap = {};
      sCurrAll.forEach(r => { sCurrMap[r.series] = (sCurrMap[r.series] || 0) + r.rev; });
      sPrevAll.forEach(r => { sPrevMap[r.series] = (sPrevMap[r.series] || 0) + r.rev; });

      let sCurrQtyMap = {}, sPrevQtyMap = {};
      sCurrBenti.forEach(r => { sCurrQtyMap[r.series] = (sCurrQtyMap[r.series] || 0) + r.qty; });
      sPrevBenti.forEach(r => { sPrevQtyMap[r.series] = (sPrevQtyMap[r.series] || 0) + r.qty; });

      const allSeriesKeys = Array.from(new Set([...Object.keys(sCurrMap), ...Object.keys(sPrevMap)]));
      allSeriesKeys.sort((a, b) => (sCurrMap[b] || 0) - (sCurrMap[a] || 0));

      let c1TableHTML = `
        <table class="comp-table">
          <thead>
            <tr>
              <th>产品系列</th>
              <th>销售收入 (元)</th>
              <th>同比增长</th>
              <th>销售占比</th>
              <th>发票数量 (台)</th>
              <th>数量占比</th>
            </tr>
          </thead>
          <tbody>
      `;
      allSeriesKeys.slice(0, 10).forEach(s => {
        let r26 = sCurrMap[s] || 0;
        let r25 = sPrevMap[s] || 0;
        let q26 = sCurrQtyMap[s] || 0;
        let rYoY = r25 > 0 ? ((r26 - r25) / r25 * 100).toFixed(1) : "0.0";
        let rS26 = totRev > 0 ? (r26 / totRev * 100).toFixed(1) : "0.0";
        let qS26 = totQty > 0 ? (q26 / totQty * 100).toFixed(1) : "0.0";
        c1TableHTML += `
          <tr>
            <td style="font-weight:700;">${s}</td>
            <td>¥${r26.toLocaleString(undefined,{maximumFractionDigits:2})}</td>
            <td>${rYoY>=0?'+':''}${rYoY}%</td>
            <td>${rS26}%</td>
            <td>${q26.toLocaleString()}</td>
            <td>${qS26}%</td>
          </tr>
        `;
      });
      c1TableHTML += `</tbody></table>`;
      document.getElementById("c1_table_box").innerHTML = c1TableHTML;

      const tCurrAll = filterRecords(PAYLOAD.teams, currYear, null);
      const tPrevAll = filterRecords(PAYLOAD.teams, prevYear, null);
      const tCurrBenti = filterRecords(PAYLOAD.teams, currYear, "benti");

      let tCurrMap = {}, tPrevMap = {}, tQtyMap = {};
      tCurrAll.forEach(r => { tCurrMap[r.team] = (tCurrMap[r.team] || 0) + r.rev; });
      tPrevAll.forEach(r => { tPrevMap[r.team] = (tPrevMap[r.team] || 0) + r.rev; });
      tCurrBenti.forEach(r => { tQtyMap[r.team] = (tQtyMap[r.team] || 0) + r.qty; });

      const allTeamKeys = Array.from(new Set([...Object.keys(tCurrMap), ...Object.keys(tPrevMap)]));
      allTeamKeys.sort((a, b) => (tCurrMap[b] || 0) - (tCurrMap[a] || 0));

      let c2TableHTML = `
        <table class="comp-table">
          <thead>
            <tr>
              <th>销售团队/渠道</th>
              <th>销售收入 (元)</th>
              <th>同比增长</th>
              <th>销售占比</th>
              <th>发票数量 (台)</th>
            </tr>
          </thead>
          <tbody>
      `;
      allTeamKeys.slice(0, 10).forEach(t => {
        let r26 = tCurrMap[t] || 0;
        let r25 = tPrevMap[t] || 0;
        let q26 = tQtyMap[t] || 0;
        let rYoY = r25 > 0 ? ((r26 - r25) / r25 * 100).toFixed(1) : "0.0";
        let rS26 = totRev > 0 ? (r26 / totRev * 100).toFixed(1) : "0.0";
        c2TableHTML += `
          <tr>
            <td style="font-weight:700;">${t}</td>
            <td>¥${r26.toLocaleString(undefined,{maximumFractionDigits:2})}</td>
            <td>${rYoY>=0?'+':''}${rYoY}%</td>
            <td>${rS26}%</td>
            <td>${q26.toLocaleString()}</td>
          </tr>
        `;
      });
      c2TableHTML += `</tbody></table>`;
      document.getElementById("c2_table_box").innerHTML = c2TableHTML;

      const cCurrAll = filterRecords(PAYLOAD.countries, currYear, null);
      const cPrevAll = filterRecords(PAYLOAD.countries, prevYear, null);
      const cCurrBenti = filterRecords(PAYLOAD.countries, currYear, "benti");

      let cCurrMap = {}, cPrevMap = {}, cQtyMap = {}, cRegionMap = {};
      cCurrAll.forEach(r => {
        cCurrMap[r.country] = (cCurrMap[r.country] || 0) + r.rev;
        cRegionMap[r.country] = r.region;
      });
      cPrevAll.forEach(r => { cPrevMap[r.country] = (cPrevMap[r.country] || 0) + r.rev; });
      cCurrBenti.forEach(r => { cQtyMap[r.country] = (cQtyMap[r.country] || 0) + r.qty; });

      const allCtryKeys = Array.from(new Set(Object.keys(cCurrMap)));
      allCtryKeys.sort((a, b) => (cCurrMap[b] || 0) - (cCurrMap[a] || 0));

      let c3TableHTML = `
        <table class="comp-table">
          <thead>
            <tr>
              <th>出口国家</th>
              <th>所属洲区</th>
              <th>出口金额 (元)</th>
              <th>同比增长</th>
              <th>出口数量 (台)</th>
            </tr>
          </thead>
          <tbody>
      `;
      allCtryKeys.slice(0, 10).forEach(c => {
        let r26 = cCurrMap[c] || 0;
        let r25 = cPrevMap[c] || 0;
        let q26 = cQtyMap[c] || 0;
        let reg = cRegionMap[c] || "海外区";
        let rYoY = r25 > 0 ? ((r26 - r25) / r25 * 100).toFixed(1) : "0.0";
        c3TableHTML += `
          <tr>
            <td style="font-weight:700;">${c}</td>
            <td>${reg}</td>
            <td>¥${r26.toLocaleString(undefined,{maximumFractionDigits:2})}</td>
            <td>${rYoY>=0?'+':''}${rYoY}%</td>
            <td>${q26.toLocaleString()}</td>
          </tr>
        `;
      });
      c3TableHTML += `</tbody></table>`;
      document.getElementById("c3_table_box").innerHTML = c3TableHTML;

      let c4TableHTML = `
        <table class="comp-table">
          <thead>
            <tr>
              <th rowspan="2">产品类别</th>
              <th colspan="4">销售收入 (全量)</th>
              <th colspan="4">销售数量 (本体台数)</th>
            </tr>
            <tr>
              <th class="sub-th">${currYear}年 (累计金额)</th>
              <th class="sub-th">同比增长</th>
              <th class="sub-th">${prevYear}年 销售占比</th>
              <th class="sub-th">${currYear}年 销售占比</th>
              <th class="sub-th">${currYear}年 (累计台数)</th>
              <th class="sub-th">同比增长</th>
              <th class="sub-th">${prevYear}年 销售占比</th>
              <th class="sub-th">${currYear}年 销售占比</th>
            </tr>
          </thead>
          <tbody>
            <tr class="total-row">
              <td>汇总</td>
              <td>¥${totRev.toLocaleString(undefined,{maximumFractionDigits:2})}</td>
              <td>${yoyTotRev>=0?'+':''}${yoyTotRev.toFixed(1)}%</td>
              <td>100%</td>
              <td>100%</td>
              <td>${totQty.toLocaleString()}</td>
              <td>${yoyTotQty>=0?'+':''}${yoyTotQty.toFixed(1)}%</td>
              <td>100%</td>
              <td>100%</td>
            </tr>
      `;

      allSeriesKeys.forEach(s => {
        let r26 = sCurrMap[s] || 0;
        let r25 = sPrevMap[s] || 0;
        let q26 = sCurrQtyMap[s] || 0;
        let q25 = sPrevQtyMap[s] || 0;

        let rYoY = r25 > 0 ? ((r26 - r25) / r25 * 100).toFixed(1) : "0.0";
        let qYoY = q25 > 0 ? ((q26 - q25) / q25 * 100).toFixed(1) : "0.0";
        let rS25 = totRevP > 0 ? (r25 / totRevP * 100).toFixed(1) : "0.0";
        let rS26 = totRev > 0 ? (r26 / totRev * 100).toFixed(1) : "0.0";
        let qS25 = totQtyP > 0 ? (q25 / totQtyP * 100).toFixed(1) : "0.0";
        let qS26 = totQty > 0 ? (q26 / totQty * 100).toFixed(1) : "0.0";

        c4TableHTML += `
          <tr>
            <td style="font-weight:700;">${s}</td>
            <td>¥${r26.toLocaleString(undefined,{maximumFractionDigits:2})}</td>
            <td>${rYoY>=0?'+':''}${rYoY}%</td>
            <td>${rS25}%</td>
            <td>${rS26}%</td>
            <td>${q26.toLocaleString()}</td>
            <td>${qYoY>=0?'+':''}${qYoY}%</td>
            <td>${qS25}%</td>
            <td>${qS26}%</td>
          </tr>
        `;
      });
      c4TableHTML += `</tbody></table>`;
      document.getElementById("c4_table_box").innerHTML = c4TableHTML;

      renderCharts(sCurrAll, filterRecords(PAYLOAD.teams, currYear, null), filterRecords(PAYLOAD.countries, currYear, null), allSeriesKeys, sCurrMap);
    }

    function renderCharts(seriesRecs, teamRecs, countryRecs, seriesKeys, seriesRevMap) {
      let serAgg = {};
      seriesRecs.forEach(r => { serAgg[r.series] = (serAgg[r.series] || 0) + r.rev; });
      let topSeries = Object.entries(serAgg).sort((a,b) => b[1] - a[1]).slice(0, 8);

      const ctx1 = document.getElementById("cnSeriesChart").getContext("2d");
      if (chartObjs.c1) chartObjs.c1.destroy();
      chartObjs.c1 = new Chart(ctx1, {
        type: "bar",
        data: {
          labels: topSeries.map(x => x[0]),
          datasets: [{ label: "销售额 (元)", data: topSeries.map(x => x[1]), backgroundColor: "#1E50E6" }]
        },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { labels: { color: "#F8FAFC" } } } }
      });

      let teamAgg = {};
      teamRecs.forEach(r => { teamAgg[r.team] = (teamAgg[r.team] || 0) + r.rev; });
      let topTeams = Object.entries(teamAgg).sort((a,b) => b[1] - a[1]).slice(0, 8);

      const ctx2 = document.getElementById("teamChart").getContext("2d");
      if (chartObjs.c2) chartObjs.c2.destroy();
      chartObjs.c2 = new Chart(ctx2, {
        type: "pie",
        data: {
          labels: topTeams.map(x => x[0]),
          datasets: [{ data: topTeams.map(x => x[1]), backgroundColor: ["#1E50E6", "#5CB531", "#F59E0B", "#8A2BE2", "#00B4D8", "#E63946"] }]
        },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { labels: { color: "#F8FAFC" } } } }
      });

      let ctryAgg = {};
      countryRecs.forEach(r => { ctryAgg[r.country] = (ctryAgg[r.country] || 0) + r.rev; });
      let topCountries = Object.entries(ctryAgg).sort((a,b) => b[1] - a[1]).slice(0, 10);

      const ctx3 = document.getElementById("intlCountryChart").getContext("2d");
      if (chartObjs.c3) chartObjs.c3.destroy();
      chartObjs.c3 = new Chart(ctx3, {
        type: "bar",
        data: {
          labels: topCountries.map(x => x[0]),
          datasets: [{ label: "出口额 (元)", data: topCountries.map(x => x[1]), backgroundColor: "#5CB531" }]
        },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { labels: { color: "#F8FAFC" } } } }
      });

      const ctx4 = document.getElementById("seriesBarChart").getContext("2d");
      if (chartObjs.c4) chartObjs.c4.destroy();
      chartObjs.c4 = new Chart(ctx4, {
        type: "bar",
        data: {
          labels: seriesKeys.slice(0, 8),
          datasets: [{ label: "营收 (元)", data: seriesKeys.slice(0, 8).map(k => seriesRevMap[k] || 0), backgroundColor: "#00A3FF" }]
        },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { labels: { color: "#F8FAFC" } } } }
      });
    }

    // 绑定 ResizeObserver 监听卡片无级缩放
    function initCardResizeListeners() {
      if (typeof ResizeObserver !== "undefined") {
        const ro = new ResizeObserver(entries => {
          for (let entry of entries) {
            const cardId = entry.target.id.replace("_card", "");
            if (chartObjs[cardId]) {
              chartObjs[cardId].resize();
            }
          }
        });
        document.querySelectorAll(".chart-card").forEach(card => ro.observe(card));
      }
    }

    window.onload = function() {
      recalculateAndRender();
      initCardResizeListeners();
    };
  </script>
</body>
</html>
"""
    return template.replace("__LOGO_TAG__", logo_tag).replace("__PAYLOAD_JSON__", payload_json).replace("__EVAL_YEAR__", str(year))


def main():
    parser = argparse.ArgumentParser(description="生成断路器产品经理多维全响应式可视化仪表盘")
    parser.add_argument("--year", type=int, default=2026, help="评估年份")
    default_out = str(Path.home() / "Downloads" / "dashboard.html")
    parser.add_argument("--output", default=default_out, help="输出 HTML 文件路径")
    args = parser.parse_args()

    db_path = get_duckdb_path()
    if not db_path.exists():
        print(f"[Error] DuckDB 数据文件不存在: {db_path}")
        sys.exit(1)

    conn = duckdb.connect(str(db_path), read_only=True)
    try:
        payload = build_preaggregated_payload(conn)
    finally:
        conn.close()

    out_path = Path(args.output)
    if not out_path.parent.exists():
        out_path.parent.mkdir(parents=True, exist_ok=True)
    
    html_content = build_dashboard_html(payload, args.year)
    out_path.write_text(html_content, encoding="utf-8")
    print(f"[SUCCESS] Standalone dashboard with constant header KPI generated at {out_path.resolve()}")

if __name__ == "__main__":
    main()
