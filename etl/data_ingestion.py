"""
Ingestion: load the raw DataCo CSV and standardize it.

Real file:   data/raw/DataCoSupplyChainDataset.csv  (download per data/raw/README.md)
Dev sample:  data/sample/sample_dataco_5k.csv       (schema-compatible smoke-test data)

The loader automatically falls back to the sample (with a loud warning) so
the pipeline is runnable before the Kaggle download — but all reported
metrics should come from the real file.

Usage:
    python etl/data_ingestion.py
"""

from __future__ import annotations

import sys

import pandas as pd

from config import (COLUMN_MAP, PROCESSED_DIR, RAW_FILE, SAMPLE_FILE)


def load_raw() -> tuple[pd.DataFrame, str]:
    """Load real DataCo file if present, else the dev sample."""
    if RAW_FILE.exists():
        # DataCo ships latin-1 encoded
        df = pd.read_csv(RAW_FILE, encoding="latin-1", low_memory=False)
        source = "real"
    elif SAMPLE_FILE.exists():
        print("WARNING: real Kaggle file not found at data/raw/. "
              "Falling back to the 5k DEV SAMPLE. Metrics from this run "
              "are for smoke-testing only.")
        df = pd.read_csv(SAMPLE_FILE)
        source = "sample"
    else:
        sys.exit("No data found. See data/raw/README.md for download steps.")
    return df, source


def standardize(df: pd.DataFrame) -> pd.DataFrame:
    """Rename to canonical schema, parse types, keep only mapped columns."""
    present = {k: v for k, v in COLUMN_MAP.items() if k in df.columns}
    missing = set(COLUMN_MAP) - set(present)
    if missing:
        print(f"NOTE: {len(missing)} expected raw columns absent "
              f"(fine for the dev sample): {sorted(missing)[:5]}...")
    out = df[list(present)].rename(columns=present).copy()

    for col in ("order_date", "shipping_date"):
        if col in out:
            out[col] = pd.to_datetime(out[col], errors="coerce")

    for col in ("sales", "quantity", "product_price", "order_item_total",
                "order_profit", "discount", "ship_days_actual",
                "ship_days_scheduled", "benefit_per_order"):
        if col in out:
            out[col] = pd.to_numeric(out[col], errors="coerce")

    # Normalize obvious string messiness (real DataCo has trailing spaces)
    for col in ("category_name", "customer_segment", "market",
                "order_region", "delivery_status", "order_status"):
        if col in out:
            out[col] = out[col].astype(str).str.strip()

    return out


def main() -> pd.DataFrame:
    df, source = load_raw()
    print(f"Loaded {len(df):,} rows from {source} data "
          f"({df.shape[1]} raw columns)")
    std = standardize(df)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    out_path = PROCESSED_DIR / "standardized.parquet"
    try:
        std.to_parquet(out_path, index=False)
    except Exception:                       # pyarrow not installed -> CSV
        out_path = PROCESSED_DIR / "standardized.csv"
        std.to_csv(out_path, index=False)
    print(f"Standardized {len(std):,} rows x {std.shape[1]} cols -> {out_path.name}")
    print(f"Date range: {std['order_date'].min():%Y-%m-%d} -> "
          f"{std['order_date'].max():%Y-%m-%d}")
    return std


if __name__ == "__main__":
    main()
