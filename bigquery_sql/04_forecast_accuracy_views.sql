-- Forecast accuracy marts. WMAPE headline (sum|err|/sum(actual)) —
-- robust to low-volume weeks where plain MAPE explodes.

CREATE OR REPLACE VIEW `supply_chain.vw_forecast_accuracy_by_category` AS
SELECT
    category_name,
    DATE_TRUNC(week, MONTH) AS month,
    COUNT(*) AS weeks,
    SUM(demand_units)   AS actual_units,
    SUM(forecast_units) AS forecast_units,
    ROUND(SAFE_DIVIDE(SUM(ABS(demand_units - forecast_units)),
                      SUM(demand_units)) * 100, 2) AS wmape_pct,
    ROUND(AVG(SAFE_DIVIDE(forecast_units - demand_units,
                          NULLIF(demand_units, 0))) * 100, 2) AS bias_pct
FROM `supply_chain.fct_weekly_demand`
GROUP BY category_name, month;

CREATE OR REPLACE VIEW `supply_chain.vw_forecast_drift` AS
SELECT
    category_name,
    week,
    demand_units,
    forecast_units,
    ROUND(SAFE_DIVIDE(ABS(demand_units - forecast_units),
                      NULLIF(forecast_units, 0)) * 100, 1) AS drift_pct
FROM `supply_chain.fct_weekly_demand`
WHERE SAFE_DIVIDE(ABS(demand_units - forecast_units),
                  NULLIF(forecast_units, 0)) > 0.15;
