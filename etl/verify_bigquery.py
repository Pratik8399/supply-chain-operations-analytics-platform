"""
Verify the BigQuery warehouse after loading.

Run AFTER etl/load_to_bigquery.py. Confirms every table and view is live,
prints row counts and headline KPI results, and reports **bytes processed
per query** — the number BigQuery actually bills on. The final summary is
designed to be screenshotted for the repo/interview: it proves the cloud
warehouse is real and that the whole run cost effectively $0.

Usage:
    export GCP_PROJECT_ID='your-project-id'
    python etl/verify_bigquery.py
"""

from __future__ import annotations

import os
import sys

from config import GCP_PROJECT_ID

DATASET = "supply_chain"

TABLES = ["stg_order_items", "fct_order_items", "fct_weekly_demand",
          "fct_anomaly_alerts", "dim_category", "dim_date"]

VIEW_CHECKS = {
    "vw_executive_kpi_scorecard":
        "SELECT total_revenue, total_orders, overall_otif_pct "
        "FROM `{d}.vw_executive_kpi_scorecard`",
    "vw_forecast_accuracy_by_category":
        "SELECT category_name, wmape_pct, bias_pct "
        "FROM `{d}.vw_forecast_accuracy_by_category` "
        "ORDER BY month DESC, wmape_pct LIMIT 5",
    "vw_anomaly_alert_summary":
        "SELECT severity, route_to, issue, alerts "
        "FROM `{d}.vw_anomaly_alert_summary` LIMIT 5",
    "vw_otif_by_region":
        "SELECT market, month, otif_pct FROM `{d}.vw_otif_by_region` "
        "ORDER BY month DESC LIMIT 5",
}


def main() -> int:
    try:
        from google.cloud import bigquery
    except ImportError:
        print("SKIP: google-cloud-bigquery not installed "
              "(pip install -r requirements-optional.txt)")
        return 0
    if not GCP_PROJECT_ID:
        print("SKIP: GCP_PROJECT_ID not set (see .env.example / "
              "docs/bigquery_setup.md)")
        return 0

    client = bigquery.Client(project=GCP_PROJECT_ID)
    d = f"{GCP_PROJECT_ID}.{DATASET}"
    total_bytes = 0
    failures = 0

    print(f"=== Verifying warehouse {d} ===\n")

    print("Tables:")
    for t in TABLES:
        try:
            tbl = client.get_table(f"{d}.{t}")
            print(f"  OK  {t:<24} {tbl.num_rows:>8,} rows"
                  + (f"  [partitioned: {tbl.time_partitioning.field}]"
                     if tbl.time_partitioning else "")
                  + (f" [clustered: {','.join(tbl.clustering_fields)}]"
                     if tbl.clustering_fields else ""))
        except Exception as e:
            print(f"  FAIL {t}: {e}")
            failures += 1

    print("\nViews (live query results + bytes billed):")
    for name, sql in VIEW_CHECKS.items():
        try:
            job = client.query(sql.format(d=d))
            rows = list(job.result())
            total_bytes += job.total_bytes_processed or 0
            mb = (job.total_bytes_processed or 0) / 1e6
            print(f"\n  {name}  ({len(rows)} rows, {mb:.2f} MB scanned)")
            for r in rows[:3]:
                print(f"    {dict(r)}")
        except Exception as e:
            print(f"  FAIL {name}: {e}")
            failures += 1

    est_cost = total_bytes / 1e12 * 6.25   # on-demand $6.25/TiB (2024+ pricing)
    print(f"\n=== Summary ===")
    print(f"Tables verified: {len(TABLES) - failures}/{len(TABLES)}"
          f" | Views queried: {len(VIEW_CHECKS)}")
    print(f"Total bytes scanned this verification: {total_bytes/1e6:.2f} MB")
    print(f"Estimated cost if billed (no free tier): ${est_cost:.6f}")
    print(f"Free tier covers 1 TB/month -> this run used "
          f"{total_bytes/1e12*100:.6f}% of it.")
    print(f"\nConsole: https://console.cloud.google.com/bigquery"
          f"?project={GCP_PROJECT_ID}")
    print("Next: connect Looker Studio to these views "
          "(docs/bigquery_looker_runbook.md, step 5).")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
