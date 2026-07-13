# 5-Day Push Plan (one commit per day, exact file lists)

Pre-req (local, before Day 1, never committed): download the Kaggle file to
data/raw/ per data/raw/README.md, run `python etl/pipeline_orchestration.py`
against it, and confirm outputs come from the real 180k-row data.

## Day 1 — Foundation: ingestion, hybrid augmentation, quality gates
git add: README.md requirements.txt .gitignore data/raw/README.md
         data/sample/sample_dataco_5k.csv etl/config.py
         etl/data_ingestion.py etl/make_dev_sample.py etl/augment_data.py
         etl/data_quality_framework.py data/processed/injection_manifest.csv
         docs/project_charter.md docs/stakeholder_requirements.md
Message: "Add ingestion, hybrid augmentation with injection manifest,
          audit-logged quality gates, and project charter"
Rationale visible to a reviewer: scoping docs land WITH the foundation —
requirements before build, like a real engagement.

## Day 2 — Demand forecasting
git add: etl/demand_forecast.py outputs/forecast_accuracy.csv
         outputs/forecast_results.csv docs/methodology.md
Message: "Add walk-forward demand forecasting (Prophet/HW/fallback tiers)
          with WMAPE and bias reporting"

## Day 3 — Anomaly detection + validation
git add: etl/anomaly_detector.py outputs/anomaly_alerts.csv
         outputs/detection_scorecard.csv
         notebooks/01_end_to_end_walkthrough.ipynb
Message: "Add 7-detector anomaly ensemble with ground-truth validation
          against the injection manifest"

## Day 4 — Automation, insights, governance, cloud warehouse
git add: etl/pipeline_orchestration.py etl/generate_business_insights.py
         etl/data_governance.py etl/load_to_bigquery.py bigquery_sql/
         outputs/executive_summary.md outputs/stakeholder_action_items.csv
         governance/pipeline_runs.csv governance/access_audit.csv
         docs/bigquery_setup.md docs/bigquery_cost_controls.md
         docs/warehouse_comparison.md
Message: "Add 9-stage orchestration, narrative insight generation, RBAC
          governance, and BigQuery warehouse layer (partitioned/clustered
          model + KPI views)"

## Day 5 — BI layer, dashboards, CI, enablement docs
git add: etl/export_for_bi.py etl/verify_bigquery.py .env.example
         snowflake_sql/ dashboards/
         .github/workflows/ci.yml tests/check_detection_recall.py
         docs/bigquery_looker_runbook.md
         docs/architecture.md docs/dashboard_adoption_guide.md
         docs/dashboard_wireframe.md docs/looker_studio_guide.md
         docs/resume_bullets.md docs/interview_talking_points.md
Message: "Add BI exports, Snowflake reference DDL, Looker Studio guide,
          dashboard wireframes, and CI with detection-recall regression gate"
(Complete docs/bigquery_looker_runbook.md first: run the loader against
your GCP project, run verify_bigquery.py, build the Looker Studio report,
save the four screenshots to dashboards/screenshots/, and uncomment the
Dashboards section in README before this commit.)

Never commit: data/raw/*.csv (size + Kaggle license),
data/processed/transactions_augmented.csv (large, regenerable),
data/processed/standardized.* , .env.
Before each push: rerun the touched stage on real data, skim the diff,
and confirm `git status` shows nothing under data/raw.
