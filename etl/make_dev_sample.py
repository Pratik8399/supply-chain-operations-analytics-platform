"""
Build a 5,000-row DEV SAMPLE that mirrors the raw DataCo column layout.

Purpose: smoke-test the pipeline end-to-end before the Kaggle download.
This file is synthetic and clearly labeled as such — it is NOT the real
dataset, and project metrics must be reported from real-data runs.

Usage:
    python etl/make_dev_sample.py
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from config import SAMPLE_DIR, SEED

rng = np.random.default_rng(SEED)
N = 5_000

CATEGORIES = ["Cleats", "Men's Footwear", "Women's Apparel", "Fishing",
              "Camping & Hiking", "Cardio Equipment", "Electronics",
              "Water Sports", "Indoor/Outdoor Games"]
SEGMENTS = ["Consumer", "Corporate", "Home Office"]
MARKETS = ["LATAM", "Europe", "Pacific Asia", "USCA", "Africa"]
REGIONS = ["Central America", "Western Europe", "South America",
           "Southeast Asia", "US Center", "West Africa", "Oceania"]
MODES = ["Standard Class", "Second Class", "First Class", "Same Day"]
STATUSES = ["COMPLETE", "PENDING", "CLOSED", "PENDING_PAYMENT",
            "PROCESSING", "ON_HOLD"]
DELIVERY = ["Advance shipping", "Late delivery", "Shipping on time",
            "Shipping canceled"]


def main() -> None:
    # Seasonal weighting (Q4 peak) so the dev sample has learnable structure
    days = np.arange(1085)
    weights = 1 + 0.45 * np.sin(2 * np.pi * (days % 365) / 365 - 1.5)
    weights /= weights.sum()
    order_dates = pd.to_datetime("2015-01-01") + pd.to_timedelta(
        rng.choice(days, N, p=weights), unit="D")
    sched = rng.choice([1, 2, 4, 6], N, p=[0.1, 0.25, 0.45, 0.2])
    actual = np.clip(sched + rng.integers(-1, 4, N), 0, None)
    price = np.round(rng.uniform(10, 500, N), 2)
    qty = rng.integers(1, 6, N)
    discount = np.round(price * qty * rng.uniform(0, 0.15, N), 2)
    total = np.round(price * qty - discount, 2)

    df = pd.DataFrame({
        "Order Id": rng.integers(1, 60_000, N),
        "Order Item Id": np.arange(1, N + 1),
        "order date (DateOrders)": order_dates.strftime("%m/%d/%Y %H:%M"),
        "shipping date (DateOrders)": (order_dates + pd.to_timedelta(actual, unit="D")
                                       ).strftime("%m/%d/%Y %H:%M"),
        "Days for shipping (real)": actual,
        "Days for shipment (scheduled)": sched,
        "Delivery Status": rng.choice(DELIVERY, N, p=[0.24, 0.55, 0.18, 0.03]),
        "Late_delivery_risk": (actual > sched).astype(int),
        "Order Status": rng.choice(STATUSES, N),
        "Shipping Mode": rng.choice(MODES, N, p=[0.6, 0.2, 0.15, 0.05]),
        "Customer Id": rng.integers(1, 12_000, N),
        "Customer Segment": rng.choice(SEGMENTS, N, p=[0.52, 0.3, 0.18]),
        "Market": rng.choice(MARKETS, N),
        "Order Region": rng.choice(REGIONS, N),
        "Order Country": "SampleLand",
        "Category Name": rng.choice(CATEGORIES, N),
        "Product Name": "Sample Product",
        "Product Price": price,
        "Order Item Quantity": qty,
        "Order Item Discount": discount,
        "Sales": np.round(price * qty, 2),
        "Order Item Total": total,
        "Order Profit Per Order": np.round(total * rng.uniform(-0.1, 0.35, N), 2),
        "Benefit per order": np.round(total * rng.uniform(-0.1, 0.35, N), 2),
    })

    SAMPLE_DIR.mkdir(parents=True, exist_ok=True)
    out = SAMPLE_DIR / "sample_dataco_5k.csv"
    df.to_csv(out, index=False)
    print(f"Wrote {out} ({len(df):,} rows) — DEV SAMPLE ONLY")


if __name__ == "__main__":
    main()
