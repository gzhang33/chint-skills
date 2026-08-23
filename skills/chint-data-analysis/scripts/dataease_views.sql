-- ==============================================================================
-- DataEase 正泰内部 BI 与 OLAP 动态分析统一视图 DDL (CHINT Unified SQL Views)
-- 底层统一事实表: sales_data (根据 report_source 自动解构国内/国际地域维度)
-- ==============================================================================

-- 0.1 兼容旧物理表查询的动态视图 (Compatibility Views for Legacy Queries)
CREATE OR REPLACE VIEW china_data AS 
SELECT * FROM sales_data 
WHERE CAST(report_source AS VARCHAR) LIKE '%中国区%' OR CAST(report_source AS VARCHAR) IN ('中国区-正泰', '中国区-诺雅克', '中国区');

CREATE OR REPLACE VIEW overseas_data AS 
SELECT * FROM sales_data 
WHERE CAST(report_source AS VARCHAR) = '国际' OR CAST(report_source AS VARCHAR) LIKE '%国际%' OR CAST(report_source AS VARCHAR) LIKE '%海外%' OR CAST(report_source AS VARCHAR) = '海外区';

-- 1. 全局销售全量明细语义视图 (Unified Row-level Semantic View - 严格按 Excel 原始字段物理顺序对齐排列)
CREATE OR REPLACE VIEW v_sales_detailed AS
SELECT
    -- 1. 报表来源 (原始) 与 报表来源-rev (映射清洗)
    COALESCE(NULLIF(TRIM(s.report_source), ''), '中国区') AS report_source,
    CASE 
        WHEN s.report_source LIKE '%中国区%' OR s.report_source IN ('中国区-正泰', '中国区-诺雅克', '中国区') THEN '中国区'
        WHEN s.report_source = '国际' OR s.report_source LIKE '%国际%' OR s.report_source LIKE '%海外%' OR s.report_source = '海外区' THEN '国际'
        ELSE '中国区'
    END AS report_source_rev,

    -- 2. 产业 / 品牌板块
    COALESCE(NULLIF(TRIM(s.brand_sector), ''), '正泰电器') AS brand_sector,

    -- 3. 业务分类 (原始) 与 业务分类-rev (映射)
    COALESCE(NULLIF(TRIM(s.biz_category), ''), '渠道业务') AS biz_category,
    CASE 
        WHEN s.report_source LIKE '%中国区%' OR s.report_source IN ('中国区-正泰', '中国区-诺雅克', '中国区') THEN COALESCE(mbt.target_value, '渠道业务')
        ELSE NULL
    END AS biz_type_rev,

    -- 4. 洲区
    COALESCE(NULLIF(TRIM(s.continent), ''), '中国区') AS continent,

    -- 5. 国家 与 国家名称
    s.country,
    s.country_name,

    -- 6. 省份 (原始) 与 区域-rev (映射)
    COALESCE(NULLIF(TRIM(s.province), ''), '其他') AS province,
    CASE 
        WHEN s.report_source LIKE '%中国区%' OR s.report_source IN ('中国区-正泰', '中国区-诺雅克', '中国区') THEN COALESCE(NULLIF(TRIM(mr.target_value), ''), NULLIF(TRIM(s.province), ''), '其他')
        ELSE COALESCE(NULLIF(TRIM(s.continent), ''), '海外大区')
    END AS region_rev,

    -- 7. 年份、月份 (原始) 与 季度 (单一标准计算)
    s.year,
    s.month,
    CASE 
        WHEN CAST(s.month AS INTEGER) BETWEEN 1 AND 3 THEN 'Q1' 
        WHEN CAST(s.month AS INTEGER) BETWEEN 4 AND 6 THEN 'Q2' 
        WHEN CAST(s.month AS INTEGER) BETWEEN 7 AND 9 THEN 'Q3' 
        ELSE 'Q4' 
    END AS quarter,

    -- 8. 生产制造与物料组 (原始与映射-rev成对)
    s.mfg_unit_code,
    s.mfg_unit,
    s.material_group_code,
    s.material_group_desc,
    COALESCE(
        NULLIF(TRIM(mpm_mat_group.target_value), ''),
        NULLIF(TRIM(mpm_desc.target_value), ''),
        NULLIF(TRIM(mpm_code.target_value), ''),
        NULLIF(NULLIF(TRIM(s.product_model), '未解构型号'), ''),
        NULLIF(TRIM(s.material_group_desc), ''),
        ''
    ) AS material_group_desc_rev,

    -- 9. 物料编码、物料描述 (原始) 与 属性 (映射)
    s.material_code,
    s.material_desc,
    COALESCE(pm_desc.target_value, pm_code.target_value, s.property, '') AS property_type,

    -- 10. 客户与项目
    s.customer_nature,
    s.outlet_customer_no,
    s.outlet_customer_name,
    s.customer_no,
    s.customer_name,
    s.terminal_customer,
    s.project_no,
    s.project_name,

    -- 11. 组织与政策
    s.sales_org_code,
    s.sales_org,
    s.new_policy_category,

    -- 12. 数量与单价金额
    s.invoice_qty,
    s.billing_price_amount,
    s.settlement_price_amount,
    s.net_amount,
    s.discount_amount,
    s.expense_amount,
    s.net_revenue,
    s.pocket_price,
    s.product_cost,
    s.total_cost,
    s.gross_profit,
    CASE 
        WHEN s.net_revenue IS NOT NULL AND s.net_revenue != 0 
        THEN (s.gross_profit / s.net_revenue) * 100.0 
        ELSE NULL 
    END AS gross_margin_rate,

    -- 13. 币种与本地核算
    s.currency,
    s.exchange_rate,
    s.revenue_local_currency,
    s.cost_local_currency,

    -- 14. 团队、平台、系列与型号
    s.product_industry_category,
    s.sales_team,
    CASE 
        WHEN s.report_source LIKE '%中国区%' OR s.report_source IN ('中国区-正泰', '中国区-诺雅克', '中国区') THEN COALESCE(NULLIF(TRIM(mtr.target_value), ''), NULLIF(TRIM(s.sales_team), ''), '其他')
        ELSE COALESCE(NULLIF(TRIM(mtr.target_value), ''), '海外业务团队')
    END AS sales_team_rev,
    s.general_or_specialized,
    CASE 
        WHEN TRIM(s.product_platform) LIKE '新锐%' OR TRIM(s.product_platform) = '新锐(5)' THEN '新锐'
        WHEN TRIM(s.product_platform) LIKE '诺雅克%' OR TRIM(s.product_platform) = '诺雅克(9)' THEN '诺雅克'
        WHEN TRIM(s.product_platform) LIKE '昆仑%' THEN '昆仑'
        WHEN TRIM(s.product_platform) IN ('其他', '其它') OR TRIM(s.product_platform) LIKE '其它%' OR TRIM(s.product_platform) LIKE '其他%' THEN '其它'
        WHEN TRIM(s.product_platform) = '' OR s.product_platform IS NULL THEN '其它'
        ELSE TRIM(s.product_platform)
    END AS product_platform,
    CASE 
        WHEN s.product_series IN ('其他', '其它平台') THEN '其它'
        ELSE s.product_series 
    END AS product_series,
    s.product_manager_team,
    s.internal_customer_flag,
    s.product_category,
    COALESCE(
        NULLIF(TRIM(mpm_mat_group.target_value), ''),
        NULLIF(TRIM(mpm_desc.target_value), ''),
        NULLIF(TRIM(mpm_code.target_value), ''),
        NULLIF(NULLIF(TRIM(s.product_model), '未解构型号'), ''),
        NULLIF(TRIM(s.material_group_desc), ''),
        ''
    ) AS product_model,

    -- 15. 特征规格参数 (极数 ➡️ 分断能力 ➡️ 壳架电流 ➡️ 安装方式 ➡️ N极连接)
    s.pole_count,
    s.breaking_capacity,
    s.frame_current,
    s.operation_method,
    s.n_pole_type,

    -- 16. 数据血缘元数据
    s._ingested_at,
    s._source_file
FROM sales_data s
LEFT JOIN (
    SELECT source_value, target_value FROM (
        SELECT source_value, target_value,
               ROW_NUMBER() OVER (PARTITION BY source_value ORDER BY CASE WHEN department = 'common' THEN 2 ELSE 1 END, department, target_value) as rn
        FROM product_mappings WHERE mapping_type = 'region'
    ) WHERE rn = 1
) mr 
    ON s.province = mr.source_value
LEFT JOIN (
    SELECT source_value, target_value FROM (
        SELECT source_value, target_value,
               ROW_NUMBER() OVER (PARTITION BY source_value ORDER BY CASE WHEN department = 'common' THEN 2 ELSE 1 END, department, target_value) as rn
        FROM product_mappings WHERE mapping_type = 'sales_team_rev'
    ) WHERE rn = 1
) mtr 
    ON COALESCE(NULLIF(s.sales_team, ''), NULLIF(s.country, '')) = mtr.source_value
LEFT JOIN (
    SELECT source_value, target_value FROM (
        SELECT source_value, target_value,
               ROW_NUMBER() OVER (PARTITION BY source_value ORDER BY CASE WHEN department = 'common' THEN 2 ELSE 1 END, department, target_value) as rn
        FROM product_mappings WHERE mapping_type = 'biz_type'
    ) WHERE rn = 1
) mbt 
    ON s.sales_team = mbt.source_value
LEFT JOIN (
    SELECT source_value, target_value FROM (
        SELECT source_value, target_value,
               ROW_NUMBER() OVER (PARTITION BY source_value ORDER BY CASE WHEN department = 'common' THEN 2 ELSE 1 END, department, target_value) as rn
        FROM product_mappings WHERE mapping_type = 'product_model'
    ) WHERE rn = 1
) mpm_mat_group 
    ON s.material_group_desc = mpm_mat_group.source_value
LEFT JOIN (
    SELECT source_value, target_value FROM (
        SELECT source_value, target_value,
               ROW_NUMBER() OVER (PARTITION BY source_value ORDER BY CASE WHEN department = 'common' THEN 2 ELSE 1 END, department, target_value) as rn
        FROM product_mappings WHERE mapping_type = 'product_model'
    ) WHERE rn = 1
) mpm_desc 
    ON s.material_desc = mpm_desc.source_value
LEFT JOIN (
    SELECT source_value, target_value FROM (
        SELECT source_value, target_value,
               ROW_NUMBER() OVER (PARTITION BY source_value ORDER BY CASE WHEN department = 'common' THEN 2 ELSE 1 END, department, target_value) as rn
        FROM product_mappings WHERE mapping_type = 'product_model'
    ) WHERE rn = 1
) mpm_code 
    ON s.material_code = mpm_code.source_value
LEFT JOIN (
    SELECT source_value, target_value FROM (
        SELECT source_value, target_value,
               ROW_NUMBER() OVER (PARTITION BY source_value ORDER BY CASE WHEN department = 'common' THEN 2 ELSE 1 END, department, target_value) as rn
        FROM product_mappings WHERE mapping_type IN ('property', 'property_type')
    ) WHERE rn = 1
) pm_desc 
    ON s.material_desc = pm_desc.source_value
LEFT JOIN (
    SELECT source_value, target_value FROM (
        SELECT source_value, target_value,
               ROW_NUMBER() OVER (PARTITION BY source_value ORDER BY CASE WHEN department = 'common' THEN 2 ELSE 1 END, department, target_value) as rn
        FROM product_mappings WHERE mapping_type IN ('property', 'property_type')
    ) WHERE rn = 1
) pm_code 
    ON s.material_code = pm_code.source_value;

-- 2. 全局月度多维透视聚合视图 (Unified Monthly Pivot DWS View)
CREATE OR REPLACE VIEW v_sales_monthly AS
SELECT 
    report_source_rev AS market_channel,
    report_source_rev,
    year,
    month,
    quarter,
    region_rev,
    sales_team_rev,
    biz_type_rev,
    product_category,
    product_series,
    product_model,
    property_type,
    SUM(invoice_qty) AS total_invoice_qty,
    SUM(net_revenue) AS total_net_revenue,
    SUM(gross_profit) AS total_gross_profit,
    SUM(product_cost) AS total_cost,
    CASE 
        WHEN SUM(net_revenue) = 0 OR SUM(net_revenue) IS NULL THEN 0.0 
        ELSE (SUM(gross_profit) / NULLIF(SUM(net_revenue), 0)) * 100.0 
    END AS gross_margin_rate,
    CASE 
        WHEN SUM(net_revenue) = 0 OR SUM(net_revenue) IS NULL THEN 0.0 
        ELSE (SUM(gross_profit) / NULLIF(SUM(net_revenue), 0)) * 100.0 
    END AS gross_profit_rate
FROM v_sales_detailed
GROUP BY 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12;

-- 3. 分部门/品类隔离明细视图 (Category-Specific Views)
CREATE OR REPLACE VIEW v_sales_acb AS 
SELECT * FROM v_sales_detailed 
WHERE product_category IN ('框架类', '框架', 'ACB');

CREATE OR REPLACE VIEW v_sales_mccb AS 
SELECT * FROM v_sales_detailed 
WHERE product_category IN ('塑壳类', '塑壳', 'MCCB');

CREATE OR REPLACE VIEW v_sales_pq AS 
SELECT * FROM v_sales_detailed 
WHERE product_category IN ('电能质量', 'PQ');

CREATE OR REPLACE VIEW v_sales_atse AS 
SELECT * FROM v_sales_detailed 
WHERE product_category IN ('双电源', 'ATSE');

CREATE OR REPLACE VIEW v_sales_vf AS 
SELECT * FROM v_sales_detailed 
WHERE product_category IN ('虚拟工厂', 'VF', '微断', 'MCB');

CREATE OR REPLACE VIEW v_sales_mcb AS 
SELECT * FROM v_sales_vf;

-- 全量全品类视图
CREATE OR REPLACE VIEW v_sales_all AS 
SELECT * FROM v_sales_detailed;

-- 4. 兼容性旧视图别名 (Backwards Compatibility Layer)
CREATE OR REPLACE VIEW v_china_sales_monthly AS 
SELECT * FROM v_sales_monthly WHERE report_source_rev = '中国区';

CREATE OR REPLACE VIEW v_overseas_sales_monthly AS 
SELECT * FROM v_sales_monthly WHERE report_source_rev = '国际';

CREATE OR REPLACE VIEW v_chint_cn_sales_acb AS 
SELECT * FROM v_sales_acb WHERE report_source_rev = '中国区';

CREATE OR REPLACE VIEW v_chint_cn_sales_mccb AS 
SELECT * FROM v_sales_mccb WHERE report_source_rev = '中国区';

CREATE OR REPLACE VIEW v_chint_cn_sales_pq AS 
SELECT * FROM v_sales_pq WHERE report_source_rev = '中国区';

CREATE OR REPLACE VIEW v_chint_cn_sales_atse AS 
SELECT * FROM v_sales_atse WHERE report_source_rev = '中国区';

CREATE OR REPLACE VIEW v_chint_cn_sales_vf AS 
SELECT * FROM v_sales_vf WHERE report_source_rev = '中国区';

CREATE OR REPLACE VIEW v_chint_cn_sales_mcb AS 
SELECT * FROM v_sales_vf WHERE report_source_rev = '中国区';

CREATE OR REPLACE VIEW v_chint_cn_sales_all AS 
SELECT * FROM v_sales_all WHERE report_source_rev = '中国区';

CREATE OR REPLACE VIEW v_chint_intl_sales AS 
SELECT * FROM v_sales_all WHERE report_source_rev = '国际';

CREATE OR REPLACE VIEW v_chint_global_sales_summary AS
SELECT 
    report_source_rev AS region_scope, 
    year, 
    month, 
    product_category, 
    product_series,
    SUM(invoice_qty) AS total_qty_invoice,
    SUM(net_revenue) AS total_net_revenue,
    SUM(gross_profit) AS total_gross_profit
FROM v_sales_detailed
GROUP BY report_source_rev, year, month, product_category, product_series;
