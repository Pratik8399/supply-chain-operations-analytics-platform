"""
Pipeline orchestration: one command runs the full daily flow.

  ingest -> augment -> quality gates -> forecast -> anomalies -> exports
  -> automated insights -> BigQuery warehouse -> governance access audit

Each stage is timed and logged to governance/pipeline_runs.csv. A failed
stage aborts the run and records the error — the operational trail an
enterprise scheduler (Airflow/Dagster/cron) would consume.

Usage:
    python etl/pipeline_orchestration.py            # full run
    python etl/pipeline_orchestration.py --skip-forecast   # faster dev loop
"""
from __future__ import annotations

import sys
import time
from datetime import datetime

import pandas as pd

from config import GOVERNANCE_DIR

import data_ingestion
import augment_data
import data_quality_framework
import demand_forecast
import anomaly_detector
import export_for_bi
import generate_business_insights
import data_governance
import load_to_bigquery


STAGES = [
    ("ingest", data_ingestion.main),
    ("augment", augment_data.main),
    ("quality_gates", data_quality_framework.main),
    ("forecast", demand_forecast.main),
    ("anomaly_detection", anomaly_detector.main),
    ("bi_export", export_for_bi.main),
    ("insight_generation", generate_business_insights.main),
    ("warehouse_load_bigquery", load_to_bigquery.main),
    ("governance_access_audit", data_governance.main),
]


def main() -> None:
    skip_fc = "--skip-forecast" in sys.argv
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_rows = []
    print(f"=== Pipeline run {run_id} ===")
    for name, fn in STAGES:
        if skip_fc and name == "forecast":
            continue
        t0 = time.time()
        try:
            fn()
            status, err = "SUCCESS", ""
        except SystemExit as e:          # missing prerequisite etc.
            status, err = "FAILED", str(e)
        except Exception as e:
            status, err = "FAILED", repr(e)
        log_rows.append({"run_id": run_id, "stage": name, "status": status,
                         "seconds": round(time.time() - t0, 1), "error": err})
        print(f"[{status}] {name} ({log_rows[-1]['seconds']}s)")
        if status == "FAILED":
            break

    GOVERNANCE_DIR.mkdir(exist_ok=True)
    log_path = GOVERNANCE_DIR / "pipeline_runs.csv"
    pd.DataFrame(log_rows).to_csv(log_path, mode="a", index=False,
                                  header=not log_path.exists())
    print(f"Run log appended to {log_path}")


if __name__ == "__main__":
    main()
