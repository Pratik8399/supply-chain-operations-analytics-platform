# Looker Studio Dashboard Guide (free, native BigQuery connection)

Looker Studio complements Tableau here: Tableau demonstrates BI-tool depth
from the exported CSVs; Looker Studio demonstrates cloud-native reporting
directly on the BigQuery warehouse — no exports, live views.

## Connect (3 clicks)
1. https://lookerstudio.google.com -> Create -> Data source
2. Pick the **BigQuery** connector -> your project -> `supply_chain` dataset
3. Select a VIEW (not a base table — views are small, pre-aggregated, cheap
   to scan): start with `vw_executive_kpi_scorecard`

Add the other views as additional data sources on the same report:
`vw_otif_by_region`, `vw_forecast_accuracy_by_category`,
`vw_anomaly_alert_summary`, `vw_inventory_cover`.

## Suggested 2-page report
**Page 1 — Executive Overview**: scorecard tiles from
vw_executive_kpi_scorecard; OTIF% by market (map or bar) from
vw_otif_by_region with a month filter control.
**Page 2 — Planning & Alerts**: WMAPE by category (bar, conditional color
> 30%) from vw_forecast_accuracy_by_category; alert summary table
(severity color-coded) from vw_anomaly_alert_summary.

## Cost discipline in Looker Studio
- Connect to VIEWS, never `stg_order_items`/`fct_order_items` directly —
  charts re-query on every filter interaction, and views keep scans tiny.
- Turn on data freshness = 12h (Resource > Manage data sources) so
  dashboards don't re-query on every viewer load.
- One screenshot of each page into dashboards/screenshots/ for the README.
