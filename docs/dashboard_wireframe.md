# Dashboard Wireframes (text spec until screenshots are added)

## Page 1 — Executive Overview
+-------------------------------------------------------------+
| [Revenue $X.XM] [Orders XX,XXX] [OTIF XX%] [Critical: N]    |
|-------------------------------------------------------------|
| Monthly Revenue (line)          | OTIF % trend (line)       |
|-------------------------------------------------------------|
| Auto-generated narrative panel (executive_summary.md)       |
+-------------------------------------------------------------+

## Page 2 — SLA / OTIF Performance
KPI row: avg delay days | late-shipment count | worst category
Left: OTIF% by category (bar, target line 85%)
Right: delay-days monthly trend; Market + Shipping Mode filters

## Page 3 — Forecast vs Actual
Per-category small multiples: actual vs predicted lines (backtest window)
Tiles: WMAPE% and bias% per category, conditional color (>30% amber)

## Page 4 — Anomaly Detection Center
Top: alert counts by severity (critical/high/medium cards)
Main: alert table [severity | issue | key | detail | route_to]
Side: action items panel (what_we_saw, recommended_action, review_sla)

## Page 5 — Data Quality & Governance
Quality gates: check x status matrix, failure-rate bars by dimension
Governance: access events by role (stacked, APPROVED vs DENIED),
pipeline run history with stage durations

Screenshots: add PNGs to dashboards/screenshots/ after building in
Tableau Public / Power BI and link them from the README.
