# Cloud Data Warehouse: BigQuery vs Snowflake

## How the two compare for this project

| Aspect | BigQuery | Snowflake | Project use |
|---|---|---|---|
| **Type** | Cloud SQL DW | Cloud SQL DW | Identical architecture |
| **SQL dialect** | ANSI SQL + functions | ANSI SQL + functions | Same DDL/views here |
| **Scalability** | Auto, petabyte-scale | Auto, petabyte-scale | Both handle 180k rows easily |
| **RBAC** | IAM (Google) | Grants/roles (Snowflake) | Same access patterns |
| **Cost model** | Per query ($1.25/TB) | Per-compute-second | Both cost-effective at scale |
| **Free tier** | 1 TB query data/month + 10 GB storage | 30-day trial, $2/credit | BQ free tier used here |

## Design portability

The Snowflake reference DDL (`snowflake_sql/`) and the BigQuery model
(`bigquery_sql/`) express the same dimensional design. The dialects,
partitioning/clustering mechanics, permissions models, and billing differ
between platforms — porting is a real (if modest) engineering task — but
the design itself (staging -> curated facts -> dims -> views, governed
access, cost-aware BI) transfers directly.

## Interview narrative

**"We use Snowflake here. Why is your project on BigQuery?"**

"BigQuery serves as the cloud warehouse layer for this portfolio project
and demonstrates warehouse concepts that also apply to Snowflake: staging,
curated facts, dimensions, SQL views, governance, and cost-aware BI access.
Its free tier (1 TB processed query data/month) made the project fully
runnable without a corporate account.

In a Snowflake-based enterprise environment, the same design could be
ported using Snowflake tables, views, clustering, and RBAC patterns — the
dialects and operational details differ, and I'd expect to adapt those,
but the design thinking is what transfers."

**"Show me your warehouse."**

Pull up the BigQuery console:
https://console.cloud.google.com/bigquery?project=YOUR_PROJECT_ID

Show:
1. The dataset and fact tables (fct_order_items, fct_weekly_demand)
2. The analytical views (v_forecast_accuracy, v_monthly_otif, v_category_performance)
3. Query history showing run timestamps and scan volume
4. Cost tracking: "$0.XX spent this month, well within free tier"

Interviewer sees: a working cloud warehouse, proper dimensional design,
and cost-awareness — all the signals that matter.
