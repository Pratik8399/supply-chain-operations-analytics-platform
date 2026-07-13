"""
Export curated tables for the BI layer (Power BI / Tableau).

Produces dashboard-ready CSVs in dashboards/exports/:
  kpi_summary, monthly_otif, forecast_vs_actual, anomaly_alerts,
  category_performance, detection_scorecard

Usage:
    python etl/export_for_bi.py
"""
from __future__ import annotations

import pandas as pd

from config import OUTPUT_DIR, PROCESSED_DIR, PROJECT_ROOT

EXPORT_DIR = PROJECT_ROOT / "dashboards" / "exports"


def main() -> None:
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    tx = pd.read_csv(PROCESSED_DIR / "transactions_augmented.csv",
                     parse_dates=["order_date"])
    wk = pd.read_csv(PROCESSED_DIR / "weekly_demand_augmented.csv",
                     parse_dates=["week"])

    tx["on_time"] = tx["ship_days_actual"] <= tx["ship_days_scheduled"]
    tx["month"] = tx["order_date"].dt.to_period("M").dt.start_time

    monthly = (tx.groupby("month")
                 .agg(orders=("order_id", "nunique"),
                      revenue=("sales", "sum"),
                      otif_pct=("on_time", "mean"),
                      avg_ship_delay=("ship_days_actual", "mean"))
                 .round(3).reset_index())
    monthly["otif_pct"] = (monthly["otif_pct"] * 100).round(1)
    monthly.to_csv(EXPORT_DIR / "monthly_otif.csv", index=False)

    cat = (tx.groupby("category_name")
             .agg(revenue=("sales", "sum"), orders=("order_id", "nunique"),
                  profit=("order_profit", "sum"), otif_pct=("on_time", "mean"))
             .round(2).reset_index()
             .sort_values("revenue", ascending=False))
    cat["otif_pct"] = (cat["otif_pct"] * 100).round(1)
    cat.to_csv(EXPORT_DIR / "category_performance.csv", index=False)

    for name in ("forecast_results", "forecast_accuracy",
                 "anomaly_alerts", "detection_scorecard"):
        src = OUTPUT_DIR / f"{name}.csv"
        if src.exists():
            pd.read_csv(src).to_csv(EXPORT_DIR / f"{name}.csv", index=False)

    kpi = pd.DataFrame([{
        "total_revenue": round(tx["sales"].sum(), 2),
        "total_orders": tx["order_id"].nunique(),
        "overall_otif_pct": round(tx["on_time"].mean() * 100, 1),
        "categories": tx["category_name"].nunique(),
        "weeks_covered": wk["week"].nunique(),
    }])
    kpi.to_csv(EXPORT_DIR / "kpi_summary.csv", index=False)
    print(f"BI exports written to {EXPORT_DIR}")


if __name__ == "__main__":
    main()
