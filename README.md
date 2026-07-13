# Supply Chain Operations Analytics Platform

### Python ETL, Forecasting, Anomaly Detection, Governance, BigQuery Warehouse Modeling, and BI-Ready Exports

Supply Chain Operations Analytics Platform is an end-to-end data engineering and analytics project built around the **DataCo Smart Supply Chain schema**. The repository includes a reproducible development sample for local execution, and the pipeline is compatible with the full DataCo Kaggle dataset when downloaded separately into `data/raw/`.

The system standardizes order-item data, injects controlled anomalies for measurable detection, runs audit-logged quality gates, forecasts weekly demand, detects operational anomalies with a multi-detector ensemble validated against ground truth, generates narrative insights, simulates role-based governance, exports BI-ready datasets, and includes an optional BigQuery warehouse layer.

## Project Overview

Operational analytics teams need reliable visibility into delivery performance, demand changes, cost risks, and service-level failures. This project simulates that environment by turning supply chain order-item data into a structured analytics workflow.

The pipeline uses order-item transaction data as the operational base, augments it with planning fields such as forecasted demand and inventory cover, and injects five classes of manifest-logged anomalies:

- SLA breaches
- Cost spikes
- Duplicate transactions
- Missing values
- Demand shocks

The injection manifest acts as ground truth, allowing anomaly detection quality to be evaluated with precision and recall rather than visual inspection alone.

## Pipeline

```text
DataCo-compatible CSV / development sample
        ↓
ingestion
        ↓
augmentation
        ├── forecast and inventory planning fields
        └── injected anomalies with manifest
        ↓
quality gates with audit logging
        ↓
walk-forward weekly demand forecasting
        ├── Prophet if installed
        ├── Holt-Winters fallback
        └── seasonal naive fallback
        ↓
anomaly detection ensemble
        ├── rules
        ├── robust statistics
        └── IsolationForest
        ↓
BI exports
        ↓
automated narrative insights
        ↓
governance access audit
        ↓
optional BigQuery warehouse layer