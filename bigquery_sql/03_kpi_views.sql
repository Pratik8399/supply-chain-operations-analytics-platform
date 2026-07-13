-- KPI views. Cost discipline: views select named columns (never SELECT *),
-- filter on the partition column where applicable, and aggregate small.

CREATE OR REPLACE VIEW `supply_chain.vw_otif_by_region` AS
SELECT
    market,
    order_region,
    DATE_TRUNC(DATE(order_date), MONTH) AS month,
    COUNT(DISTINCT order_id) AS orders,
    ROUND(SUM(sales), 2) AS revenue,
    ROUND(AVG(IF(ship_days_actual <= ship_days_scheduled, 1, 0)) * 100, 1)
        AS otif_pct,
    ROUND(AVG(ship_days_actual - ship_days_scheduled), 2) AS avg_delay_days
FROM `supply_chain.fct_order_items`
GROUP BY market, order_region, month;

CREATE OR REPLACE VIEW `supply_chain.vw_late_delivery_risk` AS
SELECT
    category_name,
    shipping_mode,
    COUNT(*) AS order_items,
    ROUND(AVG(late_delivery_risk) * 100, 1) AS late_risk_pct,
    ROUND(AVG(ship_days_actual - ship_days_scheduled), 2) AS avg_delay_days
FROM `supply_chain.fct_order_items`
GROUP BY category_name, shipping_mode;

CREATE OR REPLACE VIEW `supply_chain.vw_executive_kpi_scorecard` AS
SELECT
    ROUND(SUM(sales), 2)                       AS total_revenue,
    COUNT(DISTINCT order_id)                   AS total_orders,
    COUNT(DISTINCT category_name)              AS categories,
    ROUND(AVG(IF(ship_days_actual <= ship_days_scheduled, 1, 0)) * 100, 1)
                                               AS overall_otif_pct,
    ROUND(SUM(order_profit), 2)                AS total_profit
FROM `supply_chain.fct_order_items`;

CREATE OR REPLACE VIEW `supply_chain.vw_inventory_cover` AS
SELECT
    category_name,
    week,
    demand_units,
    inventory_units,
    ROUND(SAFE_DIVIDE(inventory_units, demand_units) * 7, 1) AS cover_days,
    holding_cost
FROM `supply_chain.fct_weekly_demand`;
