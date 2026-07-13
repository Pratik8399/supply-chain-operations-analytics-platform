"""
Hybrid augmentation + controlled anomaly injection.

Real operational datasets (DataCo included) lack two things this project
needs: (1) planning columns — demand forecasts, inventory positions —
and (2) labeled anomalies to validate detection against. This module adds
both, on top of the REAL transactional data:

Augmentation (realistic, seeded):
  * weekly demand forecast per category  = actual demand * (1 + bias + noise)
  * inventory position per category-week = demand cover of 12-35 days
  * holding cost derived from price and cover

Injection (every injected key logged to injection_manifest.csv):
  * sla_breach              shipping days pushed 4-10 days past schedule
  * cost_spike              order_item_total inflated 2.5-5x
  * duplicate_transactions  exact duplicate order-item rows appended
  * missing_values          sales/quantity nulled on critical rows
  * demand_shock            whole category-weeks shifted +/-45-80%

The manifest is the ground truth that turns "my charts look anomalous"
into "precision 0.9 / recall 0.95, measured".

Usage:
    python etl/augment_data.py
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from config import AUGMENT, INJECTION, PROCESSED_DIR, SEED

rng = np.random.default_rng(SEED)
_manifest: list[dict] = []


def log(issue: str, level: str, keys) -> None:
    for k in keys:
        _manifest.append({"issue": issue, "level": level, "key": str(k)})


def load_standardized() -> pd.DataFrame:
    pq = PROCESSED_DIR / "standardized.parquet"
    csv = PROCESSED_DIR / "standardized.csv"
    if pq.exists():
        return pd.read_parquet(pq)
    if csv.exists():
        return pd.read_csv(csv, parse_dates=["order_date", "shipping_date"])
    raise SystemExit("Run etl/data_ingestion.py first.")


# ----------------------------------------------------------------- injection
def inject_transaction_anomalies(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # SLA breaches: actual shipping blows past schedule
    idx = df.sample(frac=INJECTION["sla_breach"], random_state=SEED).index
    df.loc[idx, "ship_days_actual"] = (df.loc[idx, "ship_days_scheduled"]
                                       + rng.integers(4, 11, len(idx)))
    df.loc[idx, "delivery_status"] = "Late delivery"
    df.loc[idx, "late_delivery_risk"] = 1
    log("sla_breach", "order_item", df.loc[idx, "order_item_id"])

    # Cost spikes: billing errors inflate the line total
    idx = df.sample(frac=INJECTION["cost_spike"], random_state=SEED + 1).index
    df.loc[idx, "order_item_total"] = (df.loc[idx, "order_item_total"]
                                       * rng.uniform(2.5, 5.0, len(idx))).round(2)
    log("cost_spike", "order_item", df.loc[idx, "order_item_id"])

    # Duplicate transactions: same order item appended again
    dupes = df.sample(frac=INJECTION["duplicate_transactions"],
                      random_state=SEED + 2)
    df = pd.concat([df, dupes], ignore_index=True)
    log("duplicate_transactions", "order_item", dupes["order_item_id"])

    # Missing values on critical fields
    idx = df.sample(frac=INJECTION["missing_values"], random_state=SEED + 3).index
    half = len(idx) // 2
    df.loc[idx[:half], "sales"] = np.nan
    df.loc[idx[half:], "quantity"] = np.nan
    log("missing_values", "order_item", df.loc[idx, "order_item_id"])

    return df


# ------------------------------------------------------------- augmentation
def build_weekly_demand(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate real transactions to category-week demand, then augment."""
    wk = (df.dropna(subset=["order_date", "sales"])
            .assign(week=lambda d: d["order_date"].dt.to_period("W").dt.start_time)
            .groupby(["category_name", "week"], as_index=False)
            .agg(demand_units=("quantity", "sum"),
                 demand_value=("sales", "sum"),
                 orders=("order_id", "nunique"),
                 avg_price=("product_price", "mean")))

    # Demand shocks BEFORE forecast generation: the "forecast" was made
    # against expected demand, so a shocked actual creates real drift.
    shocked = wk.sample(INJECTION["demand_shock_weeks"], random_state=SEED + 4)
    factor = rng.choice([-1, 1], len(shocked)) * rng.uniform(0.45, 0.80, len(shocked))
    keys = shocked["category_name"] + "|" + shocked["week"].dt.strftime("%Y-%m-%d")
    base = wk.loc[shocked.index, "demand_units"].copy()

    # forecast built from PRE-shock demand + planner noise/bias
    noise = rng.normal(AUGMENT["forecast_bias"], AUGMENT["forecast_noise_sigma"], len(wk))
    wk["forecast_units"] = np.maximum(1, wk["demand_units"] * (1 + noise)).round(0)

    wk.loc[shocked.index, "demand_units"] = np.maximum(
        1, base * (1 + factor)).round(0)
    log("demand_shock", "category_week", keys)

    # Inventory position: cover of 12-35 days of average weekly demand
    cover_days = rng.uniform(*AUGMENT["inventory_cover_days"], len(wk))
    wk["inventory_units"] = (wk["demand_units"] * cover_days / 7).round(0)
    wk["holding_cost"] = (wk["inventory_units"] * wk["avg_price"].fillna(50)
                          * AUGMENT["unit_holding_cost_rate"] / 52).round(2)
    return wk


def main() -> None:
    df = load_standardized()
    n0 = len(df)
    df = inject_transaction_anomalies(df)
    weekly = build_weekly_demand(df)

    df.to_csv(PROCESSED_DIR / "transactions_augmented.csv", index=False)
    weekly.to_csv(PROCESSED_DIR / "weekly_demand_augmented.csv", index=False)
    manifest = pd.DataFrame(_manifest)
    manifest.to_csv(PROCESSED_DIR / "injection_manifest.csv", index=False)

    print(f"Transactions: {n0:,} -> {len(df):,} rows (after duplicate injection)")
    print(f"Weekly demand grid: {len(weekly):,} category-weeks")
    print(f"Injection manifest: {len(manifest):,} ground-truth rows")
    print(manifest.groupby('issue').size().to_string())


if __name__ == "__main__":
    main()
