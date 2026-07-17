# Supply Chain Operations Analytics Platform

Hybrid supply chain BI platform with forecasting, anomaly detection, governance, BigQuery warehousing, and automated insight generation.

---

## The Problem

Real operational data gives business credibility, but it never ships with labeled anomalies. Most analytics projects point at charts and **claim** anomalies without measurable validation.

This project takes a different approach: real transaction data as the operational base, augmented with simulated planning columns (forecasts, inventory cover) and controlled anomaly injection with ground-truth validation.

---

## Approach

**Hybrid data strategy:**
- Real DataCo supply chain transactions (180,519 records)
- Controlled anomaly injection across 5 classes (SLA breaches, cost spikes, duplicates, missing values, demand shocks)
- Injection manifest as ground truth
- 7-detector ensemble scored against the manifest

**Result:** Anomaly detection validated with measured recall and precision, not eyeballed.

---

## Full Reference Run Results

Processing 180,519 raw order records:

- **181,241** transaction rows (after controlled duplicate injection)
- **3,419** category-week demand forecasts + actuals
- **13,607** operational anomaly alerts (7 detector types)
- **8** BigQuery analytics views
- **100%** audit trail for governance compliance

**Key Validation:**
- Deterministic injected anomalies (cost spikes, duplicates, missing values) recovered with near-perfect/perfect recall/precision
- Demand-level anomalies reported separately (real organic volatility legitimately triggers alerts outside injected set)

---

## Dashboards & Outputs

### Executive Overview Dashboard
![Executive Overview](./dashboards/screenshots/tableau_executive_overview.png)

High-level KPIs: orders, revenue, OTIF trend, category performance. Demonstrated on 5K development sample: 4,800 orders | $3.84M revenue | 39% OTIF | 9 categories | 156 weeks.

---

### Forecast Accuracy Dashboard
![Forecast Accuracy](./dashboards/screenshots/tableau_forecast_accuracy.png)

Weekly demand forecasting by category with walk-forward validation (12-week backtesting windows). WMAPE metric for accuracy, bias analysis for systematic over/under-forecasting.

**Top Performers (5K sample):**

| Category | WMAPE % | Bias % |
|----------|---------|--------|
| Electronics | 15.06 | -2.99 |
| Camping & Hiking | 14.60 | 206.53 |
| Cleats | 16.84 | 103.37 |

---

### Anomaly Detection Dashboard
![Anomaly Monitoring](./dashboards/screenshots/tableau_anomaly_monitoring.png)

7-detector ensemble with ground-truth validation.

**Detectors & Validation (Full Run):**

| Detector | Approach | Validation |
|----------|----------|------------|
| SLA Breach | Contractual rule (ship_days_actual - scheduled >= 4) | Perfect recall/precision |
| Cost Spike | Per-line robust z-score vs catalog price | Perfect recall/precision |
| Duplicate Transactions | Exact order_item_id match | Perfect recall/precision |
| Missing Values | Critical field NULL checks | Perfect recall/precision |
| Multivariate Outliers | IsolationForest on [total, qty, discount, delay] | Measured against manifest |
| Demand Shock | Rolling-median robust z-score (window=9 weeks) | Separated from real volatility |
| Forecast Drift | \|actual - forecast\| / forecast > 15% | Operational alert (not precision-scored) |

---

### BigQuery Warehouse
![BigQuery Schema](./dashboards/screenshots/bigquery_dataset_tables.png)

**Star Schema (Full Run):**

**Fact Tables:**
- fct_order_items — 181,241 records
- fct_weekly_demand — 3,419 category-week records
- fct_anomaly_alerts — 13,607 alert records

**Dimension Tables:**
- dim_category
- dim_date

**Analytics Views (8 total):**
- vw_executive_kpi_scorecard
- vw_otif_by_region
- vw_late_delivery_risk
- vw_inventory_cover
- vw_forecast_accuracy_by_category
- vw_forecast_drift
- vw_anomaly_alert_summary
- vw_cost_spike_alerts

---

## Architecture

```
Raw Data (180K transactions)
    ↓
ETL Pipeline
├─ Data ingestion & standardization
├─ Anomaly injection (ground-truth manifest)
├─ Quality gates (completeness, validity, accuracy, duplication, consistency)
└─ Feature engineering (forecasts, inventory, augmentation)
    ↓
Analytics & Validation Layer
├─ Walk-forward demand forecasting (Holt-Winters)
├─ 7-detector anomaly ensemble (rules + statistics + IsolationForest)
├─ Manifest-based precision/recall scoring
└─ KPI aggregation
    ↓
Governance & Audit
├─ Role-based access control (RBAC)
├─ 100% execution audit trail
└─ Data lineage tracking
    ↓
BigQuery Warehouse (Star schema)
├─ Partitioned fact tables
├─ Clustered for query optimization
└─ 8 materialized views
    ↓
BI & Exports
├─ Tableau dashboards (4 demonstrated)
└─ CSV exports (7 data files)
```

