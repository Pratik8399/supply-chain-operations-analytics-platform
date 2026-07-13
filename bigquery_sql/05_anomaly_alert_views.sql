-- Anomaly alert views (table DDL lives in 01_create_dataset_and_tables.sql;
-- data loaded from outputs/anomaly_alerts.csv by etl/load_to_bigquery.py)

CREATE OR REPLACE VIEW `supply_chain.vw_anomaly_alert_summary` AS
SELECT
    severity,
    route_to,
    issue,
    COUNT(*) AS alerts
FROM `supply_chain.fct_anomaly_alerts`
GROUP BY severity, route_to, issue
ORDER BY CASE severity WHEN 'critical' THEN 0
                       WHEN 'high' THEN 1 ELSE 2 END, alerts DESC;

CREATE OR REPLACE VIEW `supply_chain.vw_cost_spike_alerts` AS
SELECT issue, key AS order_item_id, detail, severity, route_to
FROM `supply_chain.fct_anomaly_alerts`
WHERE issue = 'cost_spike';
