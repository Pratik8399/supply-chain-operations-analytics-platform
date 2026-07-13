# Dashboard Adoption Guide (Low-Code / No-Code Enablement)

Purpose: make the BI layer something business users OWN, not just view.
The pipeline produces flat, documented CSVs (dashboards/exports/) precisely
so the dashboard can be built and maintained in Tableau / Power BI with no
code — connect to the folder, refresh, done.

## Dashboard pages (build spec)
1. **Executive Overview** — KPI cards (revenue, orders, OTIF%, open critical
   alerts) from kpi_summary.csv; monthly revenue + OTIF dual-axis trend.
2. **SLA / OTIF Performance** — monthly_otif.csv + category_performance.csv;
   OTIF by category bar, delay-days trend, Market filter.
3. **Forecast vs Actual** — forecast_results.csv line pairs per category;
   WMAPE/bias tiles from forecast_accuracy.csv.
4. **Anomaly Detection Center** — anomaly_alerts.csv table with severity
   color coding, route_to filter; stakeholder_action_items.csv as the
   action panel.
5. **Data Quality & Governance** — quality audit pass/fail matrix;
   access_audit.csv volume by role incl. denials; pipeline run history.

## How business users work with it
- **Filters:** every page carries Market, Category, Date. Regional teams
  (Americas/EMEA/APAC) self-serve by filtering Market — one model, all
  regions.
- **KPI cards:** green/amber/red thresholds documented on-canvas (OTIF
  target >= 85%; WMAPE watchlist > 30%; critical alerts target = 0).
- **Alert review:** sort Anomaly Center by severity; work items owned by
  your team (route_to = your group); review SLAs: critical 24h, high 3
  business days, medium 2 weeks.
- **Refresh (no code):** run `python etl/pipeline_orchestration.py` (or the
  scheduled job) -> in Tableau: Data > Refresh; in Power BI: Home >
  Refresh. The folder connection picks up new CSVs automatically.

## Training plan (stakeholder enablement)
- Session 1 (45 min, all groups): platform tour, filters, KPI definitions.
- Session 2 (30 min, per team): your alert queue, review SLAs, action
  workflow using stakeholder_action_items.csv.
- Session 3 (30 min, planners): reading WMAPE/bias, drift alerts, when to
  re-baseline.
- Artifacts: this guide + executive_summary.md circulated each cycle;
  office hours during weeks 1-2 of rollout.
- Success measure: >= 80% of high-severity alerts actioned within SLA by
  week 4; dashboard MAU across all four stakeholder groups.
