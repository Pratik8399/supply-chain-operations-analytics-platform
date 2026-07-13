-- Operational KPIs + alert routing views for the BI layer.

CREATE OR REPLACE VIEW SUPPLY_CHAIN.V_MONTHLY_OTIF AS
SELECT
    DATE_TRUNC('MONTH', order_date)                            AS month,
    COUNT(DISTINCT order_id)                                   AS orders,
    ROUND(SUM(sales), 2)                                       AS revenue,
    ROUND(AVG(IFF(ship_days_actual <= ship_days_scheduled, 1, 0)) * 100, 1)
                                                               AS otif_pct,
    ROUND(AVG(ship_days_actual - ship_days_scheduled), 2)      AS avg_delay_days
FROM SUPPLY_CHAIN.FCT_ORDER_ITEMS
GROUP BY 1;

CREATE OR REPLACE VIEW SUPPLY_CHAIN.V_CATEGORY_PERFORMANCE AS
SELECT category_name,
       ROUND(SUM(sales), 2)        AS revenue,
       COUNT(DISTINCT order_id)    AS orders,
       ROUND(SUM(order_profit), 2) AS profit,
       ROUND(AVG(IFF(ship_days_actual <= ship_days_scheduled, 1, 0)) * 100, 1)
                                   AS otif_pct
FROM SUPPLY_CHAIN.FCT_ORDER_ITEMS
GROUP BY 1 ORDER BY revenue DESC;

CREATE OR REPLACE VIEW SUPPLY_CHAIN.V_OPEN_ALERTS AS
SELECT severity, route_to, issue, COUNT(*) AS alerts
FROM SUPPLY_CHAIN.ANOMALY_ALERTS
GROUP BY 1, 2, 3
ORDER BY CASE severity WHEN 'critical' THEN 0
                       WHEN 'high' THEN 1 ELSE 2 END, alerts DESC;
