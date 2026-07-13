"""
BigQuery loader: push processed CSVs into the cloud warehouse and apply
the SQL model from bigquery_sql/.

Flow (mirrors an enterprise staging pattern):
  processed CSVs -> stg_order_items / fct_weekly_demand / fct_anomaly_alerts
  -> promote staging to fct_order_items (gate-failed rows stay in staging)
  -> derive dims -> create KPI / accuracy / alert views

Cost profile: batch load jobs are FREE in BigQuery (no query bytes);
the promotion + view DDL scans only this project's few MB. Tables are
partitioned by date and clustered by category/market so downstream BI
queries prune scans. See docs/bigquery_cost_controls.md.

Graceful degradation (important for CI): if google-cloud-bigquery is not
installed or GCP_PROJECT_ID is unset, this stage prints a SKIP and returns
successfully — the local pipeline and GitHub Actions run without cloud
credentials.

Setup: docs/bigquery_setup.md   |   Usage: python etl/load_to_bigquery.py
"""

from __future__ import annotations

import os
import re

from config import OUTPUT_DIR, PROCESSED_DIR, PROJECT_ROOT

SQL_DIR = PROJECT_ROOT / "bigquery_sql"
DATASET = "supply_chain"

try:
    from google.cloud import bigquery
    BQ_INSTALLED = True
except ImportError:
    BQ_INSTALLED = False


def _qualify(sql: str, project_id: str) -> str:
    """Prefix `supply_chain.x` references with the project id."""
    return re.sub(r"`supply_chain\.", f"`{project_id}.{DATASET}.", sql)


def _run_sql_file(client, path, project_id) -> None:
    raw = path.read_text()
    # split on semicolons that end statements; skip comment-only chunks
    for stmt in raw.split(";"):
        body = "\n".join(l for l in stmt.splitlines()
                         if not l.strip().startswith("--")).strip()
        if not body:
            continue
        client.query(_qualify(body, project_id)).result()
    print(f"  applied {path.name}")


def _load_csv(client, csv_path, table, project_id, write="WRITE_TRUNCATE"):
    if not csv_path.exists():
        print(f"  skip {table}: {csv_path.name} not found")
        return
    job_config = bigquery.LoadJobConfig(
        autodetect=True, skip_leading_rows=1,
        source_format=bigquery.SourceFormat.CSV,
        write_disposition=write)
    with open(csv_path, "rb") as f:
        job = client.load_table_from_file(
            f, f"{project_id}.{DATASET}.{table}", job_config=job_config)
    job.result()
    print(f"  loaded {job.output_rows:,} rows -> {table}")


def main() -> None:
    project_id = os.getenv("GCP_PROJECT_ID")
    if not BQ_INSTALLED:
        print("SKIP BigQuery load: google-cloud-bigquery not installed "
              "(pip install google-cloud-bigquery). Local pipeline continues.")
        return
    if not project_id:
        print("SKIP BigQuery load: GCP_PROJECT_ID not set. "
              "See docs/bigquery_setup.md. Local pipeline continues.")
        return

    client = bigquery.Client(project=project_id)
    ds = bigquery.Dataset(f"{project_id}.{DATASET}")
    ds.location = "US"
    client.create_dataset(ds, exists_ok=True)
    print(f"Dataset {project_id}.{DATASET} ready")

    print("Applying DDL (tables, partitioning, clustering)...")
    _run_sql_file(client, SQL_DIR / "01_create_dataset_and_tables.sql", project_id)

    print("Loading processed data (batch load jobs — free)...")
    _load_csv(client, PROCESSED_DIR / "transactions_augmented.csv",
              "stg_order_items", project_id)
    _load_csv(client, PROCESSED_DIR / "weekly_demand_augmented.csv",
              "fct_weekly_demand", project_id)
    _load_csv(client, OUTPUT_DIR / "anomaly_alerts.csv",
              "fct_anomaly_alerts", project_id)

    print("Promoting staging -> facts, deriving dims...")
    _run_sql_file(client, SQL_DIR / "02_load_or_external_tables.sql", project_id)

    print("Creating analytical views...")
    for f in ("03_kpi_views.sql", "04_forecast_accuracy_views.sql",
              "05_anomaly_alert_views.sql"):
        _run_sql_file(client, SQL_DIR / f, project_id)

    print(f"\nWarehouse ready: https://console.cloud.google.com/bigquery"
          f"?project={project_id} — connect Looker Studio per "
          f"docs/looker_studio_guide.md")


if __name__ == "__main__":
    main()
