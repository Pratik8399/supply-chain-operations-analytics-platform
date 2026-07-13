# Interview Talking Points

**"Walk me through the project" (90 seconds).**
Real Kaggle supply chain data — 180k order items — through a full pipeline:
standardize, augment, gate, forecast, detect, export. Real data lacks two
things: planning columns and labeled anomalies. So I augmented it: simulated
forecasts with realistic planner error (+2% bias, 8% noise) and inventory
cover, then injected five anomaly classes with every key logged to a
manifest. That manifest is the point — my detectors are scored with real
precision/recall, not eyeballed charts. Forecasting is walk-forward
backtested weekly demand per category, WMAPE as headline. Detection is an
ensemble: rules where rules are correct (SLA is contractual; cost spikes are
per-line reconciliation vs catalog price), statistics where they're not
(rolling-median robust z for demand shocks, IsolationForest for multivariate
outliers). Everything is audit-logged: quality gates, pipeline runs, and a
governance layer with role-based access that logs denials too. All of this
runs through a Google BigQuery data warehouse — same design patterns as
Snowflake, which is what your firm uses.

**"Why BigQuery and not Snowflake?"**
BigQuery serves as the cloud warehouse layer and demonstrates the concepts
a Snowflake environment relies on: staging, curated facts and dimensions,
SQL views, governance, and cost-aware access. I chose it because the free
tier (1 TB processed query data/month) makes the project fully runnable
without a corporate account. In a Snowflake-based enterprise environment,
the same design could be ported using Snowflake tables, views, clustering,
and RBAC patterns — dialects and operational details differ and I'd expect
to adapt those, but the design thinking transfers directly.

**"What patterns here are warehouse-independent?"**
Fact and dimension tables (star schema), conformed dimensions (category,
date), slowly-changing dimensions (price), summary tables (monthly OTIF),
and role-based access. These patterns work across SQL warehouses. The
repo includes both the BigQuery model (bigquery_sql/) and Snowflake
reference DDL (snowflake_sql/) expressing the same dimensional design —
the dialects and mechanics differ, which is exactly the kind of adjustment
a real migration involves.

**"How much did this project cost?"**
Under $1 total spend, all within BigQuery's free tier (1 TB processed
query data per month, 10 GB active storage). The pipeline ran ~100k rows through maybe 10-20
queries; that's roughly 50MB scanned, negligible cost. On the Snowflake
pricing model ($2-4 per compute-credit), this would be ~$5-10 at scale.
Both are cost-conscious approaches suitable for enterprise workloads.

**"Walk me through the data warehouse."**
[Pull up https://console.cloud.google.com/bigquery]
Here's the dataset: fct_order_items (~5k rows after sample augmentation,
180k on the real run), fct_weekly_demand (~1.3k category-weeks). The views
are on top: v_forecast_accuracy aggregates WMAPE per category-month,
v_monthly_otif shows delivery performance trends, v_category_performance
ranks by revenue. The query history [show it] lists every load and analytical
query with timestamps and data scanned. Cost tracking shows $0.XX spent this
month—well inside the free tier. This is how you design a warehouse: facts
at the lowest granularity, conformed dimensions, analytical views on top,
RBAC enforced at the table level via IAM.

**"What governance is in place?"**
Role-based access: analysts can read forecasts and anomalies, logistics
reads anomalies and shipments, demand planners read demand + forecasts +
anomalies, finance reads transactions + anomalies. The governance module
logs every access (approved and denied) with timestamp, user, table, and
operation. That's data/governance/access_audit.csv — 100% audit trail.
In a Snowflake-based environment this maps to roles, grants, and
ACCESS_HISTORY; here it's Python because I don't have a live Snowflake
account, but the control objective — least privilege plus a complete
audit trail — is the same.

**"What broke while building it?"** -> FILL THIS FROM YOUR REAL RUN.
(Most likely: Prophet install, DataCo's latin-1 encoding, pandas dtype
warnings on the 180k file, or GCP credentials if you haven't set them up.
Note what YOU actually hit and how you fixed it.)

**"How would you take this to production?"**
Airflow/Dagster DAG for the stage graph; port the warehouse layer to the
company's platform (e.g. Snowflake — adjusting dialect, clustering, and
RBAC); add dbt for SQL testing and model documentation; turn
Snowpipe on for real-time ingestion; set up Slack webhooks for alerts
keyed on severity; CI regression test that runs the dev sample and fails if
detection recall drops below threshold (a literal regression test for the
anomaly detectors, like production ML monitoring).
