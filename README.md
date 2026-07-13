# Enterprise Operations Analytics & Automation Suite

### Hybrid Supply Chain BI Platform with Forecasting, Anomaly Detection, Governance, BigQuery Warehousing, and Automated Insight Generation

An end-to-end data engineering and analytics project built around the **DataCo Smart Supply Chain schema**. The repository includes a 5k reproducible development sample for smoke testing, and the pipeline is compatible with the full DataCo Kaggle dataset when downloaded separately into `data/raw/`.

The full reference run processed the real DataCo dataset with **180,519 raw order records**, generated **181,241 transaction rows after controlled duplicate injection**, produced **3,419 category-week demand records**, raised **13,607 operational anomaly alerts**, and loaded curated warehouse tables/views into BigQuery.

The system standardizes order-item data, injects controlled anomalies for measurable detection, runs audit-logged quality gates, forecasts weekly demand with walk-forward validation, detects operational anomalies with a 7-detector ensemble validated against ground truth, generates narrative insights, enforces role-based governance, exports BI-ready datasets, and loads curated tables and views into BigQuery.

---

## The idea

Real operational data gives business credibility, but it rarely ships with labeled anomalies. Most analytics projects point at charts and claim anomalies without measurable validation.

This project takes a hybrid route: real transaction data is used as the operational base, then augmented with simulated planning columns such as forecasts, inventory cover, and five classes of manifest-logged injected anomalies:

- SLA breaches
- Cost spikes
- Duplicate transactions
- Missing values
- Demand shocks

The injection manifest acts as ground truth, so anomaly detection can be scored with measured recall and precision rather than visual inspection.

In the full DataCo run, deterministic injected anomalies such as cost spikes, duplicate transactions, and missing values were recovered with near-perfect or perfect recall/precision against the manifest. Demand-level anomalies are reported separately because real organic volatility can legitimately trigger operational alerts outside the injected set. See `docs/methodology.md` for the full treatment.

---

## Pipeline

```text
Kaggle CSV
    -> ingestion
    -> standardization
    -> augmentation with forecasts, inventory, and injected anomaly manifest
    -> quality gates and audit log
    -> walk-forward demand forecasting
    -> anomaly detection ensemble
    -> BI-ready exports
    -> automated business insights
    -> BigQuery warehouse tables and views
    -> governance access audit