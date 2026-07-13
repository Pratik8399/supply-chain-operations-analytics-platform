# Option B Runbook: Live BigQuery + Looker Studio (with screenshots)

Goal: turn the optional cloud layer into a PROVEN one — real BigQuery
tables/views, a live Looker Studio dashboard, and screenshots in the repo.
Total time: ~60-90 minutes. Total cost: $0 (free tier / sandbox).

## Step 1 — GCP project (10 min)
Follow docs/bigquery_setup.md steps 1-4:
create account -> create project -> enable BigQuery API -> note PROJECT_ID.
Sandbox (no credit card) is fine; honest caveat: sandbox tables expire
after 60 days — rerun the loader to refresh.

## Step 2 — Local auth + env (5 min)
    gcloud auth application-default login
    cp .env.example .env        # then set GCP_PROJECT_ID=your-project-id
    pip install -r requirements-optional.txt

## Step 3 — Load the warehouse (5 min)
Run on REAL data (Kaggle file in data/raw/), not the dev sample:
    python etl/pipeline_orchestration.py
The warehouse_load_bigquery stage now executes instead of skipping:
dataset created, DDL applied (partitioned/clustered), CSVs batch-loaded
(free), staging promoted to facts via CTAS, dims derived, views created.

## Step 4 — Verify + first screenshots (10 min)
    python etl/verify_bigquery.py
This prints: table row counts (with partition/cluster info), live view
results, MB scanned per query, and estimated cost (~$0.000x).
SCREENSHOT #1: this terminal summary.
SCREENSHOT #2: BigQuery console showing the supply_chain dataset tree
(tables + views) with one view's results tab open.
Save to dashboards/screenshots/ as:
    bigquery_verify_terminal.png
    bigquery_console_dataset.png

## Step 5 — Looker Studio dashboard (30-45 min)
Follow docs/looker_studio_guide.md:
1. lookerstudio.google.com -> Create -> Data source -> BigQuery connector
2. Add sources (VIEWS ONLY — never base tables):
   vw_executive_kpi_scorecard, vw_otif_by_region,
   vw_forecast_accuracy_by_category, vw_anomaly_alert_summary
3. Page 1 "Executive Overview": scorecard tiles (revenue, orders, OTIF%),
   OTIF by market bar chart, month filter control.
4. Page 2 "Planning & Alerts": WMAPE by category bar (conditional color
   >30%), alert summary table color-coded by severity.
5. Resource -> Manage data sources -> data freshness = 12 hours.
SCREENSHOT #3: looker_executive_overview.png
SCREENSHOT #4: looker_planning_alerts.png

## Step 6 — Wire screenshots into the README (5 min)
Uncomment the screenshot section in README.md (it references the four
filenames above). Commit screenshots + README together (push plan Day 5).

## Step 7 — Interview proof points you now own
- "Here's the live warehouse" -> console screenshot, partitioned/clustered
- "Here's what it cost" -> verify-script summary: X MB scanned, ~$0
- "Here's the BI layer on live views" -> Looker Studio pages
- "Loads are free batch jobs; queries prune partitions; BI hits
  pre-aggregated views" -> docs/bigquery_cost_controls.md
