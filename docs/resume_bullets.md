# Resume Bullets

Replace bracketed numbers with YOUR real-run figures before using.

- Built an end-to-end supply chain analytics platform (Python ETL, Google
  BigQuery data warehouse, Power BI / Tableau BI) on 180k real order records,
  with automated data-quality gates across 5 dimensions and append-only audit
  logging on every run.

- Designed a hybrid validation strategy: augmented real Kaggle data with
  simulated planning columns and [140+] injected, manifest-logged anomalies
  (SLA breaches, cost spikes, duplicates, missing values, demand shocks),
  achieving 100% recall and 100% transaction-level precision against ground
  truth.

- Implemented walk-forward demand forecasting (Prophet, with Holt-Winters
  and seasonal-naive fallbacks behind one evaluation harness), reporting
  WMAPE [x.x]% and bias [x.x]% per category across a 12-week backtest.

- Engineered a 7-detector anomaly ensemble mixing business rules (SLA,
  catalog-price reconciliation) with statistical methods (rolling-median
  robust z-scores, IsolationForest), routing alerts by severity to
  Logistics, Finance Ops, and Demand Planning.

- Automated narrative insight generation (template-based NLP-style)
  converting anomaly and forecast outputs into executive summaries and
  team-routed action items with SLA enforcement (critical 24h, high 3 days).

- Implemented data governance framework: role-based access with
  least-privilege grants, confidentiality classification, and 100% audit
  trail including denied access attempts — mirroring Snowflake RBAC + 
  ACCESS_HISTORY patterns.

- Modeled a BigQuery cloud data warehouse (partitioned + clustered fact
  tables, derived dimensions, KPI/accuracy/alert views) loaded via free
  batch jobs, with Looker Studio reporting live on warehouse views and a
  documented cost-control policy — architecture directly portable to
  Snowflake (reference DDL included).

- Set up GitHub Actions CI running the full pipeline on a schema-compatible
  dev sample with a detection-recall regression gate, so detector changes
  cannot silently degrade validated recall.
