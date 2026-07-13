-- Forecast accuracy metrics per category-month.
-- WMAPE (sum|err|/sum(actual)) is the headline metric: robust to
-- low-volume weeks where plain MAPE explodes.

CREATE OR REPLACE VIEW SUPPLY_CHAIN.V_FORECAST_ACCURACY AS
SELECT
    category_name,
    DATE_TRUNC('MONTH', week)                          AS month,
    COUNT(*)                                           AS weeks,
    SUM(demand_units)                                  AS actual_units,
    SUM(forecast_units)                                AS forecast_units,
    ROUND(SUM(ABS(demand_units - forecast_units))
          / NULLIF(SUM(demand_units), 0) * 100, 2)     AS wmape_pct,
    ROUND(AVG((forecast_units - demand_units)
          / NULLIF(demand_units, 0)) * 100, 2)         AS bias_pct
FROM SUPPLY_CHAIN.FCT_WEEKLY_DEMAND
GROUP BY 1, 2;

CREATE OR REPLACE VIEW SUPPLY_CHAIN.V_FORECAST_DRIFT AS
SELECT category_name, week, demand_units, forecast_units,
       ROUND(ABS(demand_units - forecast_units)
             / NULLIF(forecast_units, 0) * 100, 1) AS drift_pct
FROM SUPPLY_CHAIN.FCT_WEEKLY_DEMAND
WHERE ABS(demand_units - forecast_units)
      / NULLIF(forecast_units, 0) > 0.15
ORDER BY drift_pct DESC;
