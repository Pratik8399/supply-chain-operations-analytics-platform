"""
Data quality framework: validation gates + audit logging.

Every ingestion run passes through gate checks before analytics consume
the data. Each check returns PASS/FAIL with row counts, and every run is
appended to an audit log (data/quality_audit/) — the compliance trail an
enterprise pipeline is expected to keep.

Gates implemented:
  completeness  critical columns non-null
  uniqueness    no duplicate order_item_id
  validity      quantities/prices/sales positive; ship days sane
  timeliness    no order dated after today; shipping >= order date
  consistency   sales ~= price * quantity (within discount tolerance)

Usage:
    python etl/data_quality_framework.py
"""

from __future__ import annotations

from datetime import datetime

import numpy as np
import pandas as pd

from config import CRITICAL_COLUMNS, PROCESSED_DIR, QUALITY_AUDIT_DIR


class DataQualityGates:
    def __init__(self, df: pd.DataFrame, source: str):
        self.df = df
        self.source = source
        self.results: list[dict] = []

    def _log(self, check: str, dimension: str, failed: int, detail: str = "") -> None:
        self.results.append({
            "check": check,
            "dimension": dimension,
            "failed_rows": int(failed),
            "total_rows": len(self.df),
            "failure_rate": round(failed / max(len(self.df), 1), 5),
            "status": "PASS" if failed == 0 else "FAIL",
            "detail": detail,
        })

    def check_critical_nulls(self) -> None:
        cols = [c for c in CRITICAL_COLUMNS if c in self.df.columns]
        nulls = self.df[cols].isnull().any(axis=1).sum()
        worst = self.df[cols].isnull().sum().idxmax() if nulls else ""
        self._log("critical_nulls", "completeness", nulls,
                  f"worst column: {worst}" if nulls else "")

    def check_duplicate_items(self) -> None:
        if "order_item_id" not in self.df.columns:
            return
        dupes = self.df.duplicated(subset=["order_item_id"]).sum()
        self._log("duplicate_order_items", "uniqueness", dupes)

    def check_value_ranges(self) -> None:
        bad_qty = (self.df.get("quantity", pd.Series(dtype=float)) <= 0).sum()
        self._log("non_positive_quantity", "validity", bad_qty)
        bad_sales = (self.df.get("sales", pd.Series(dtype=float)) < 0).sum()
        self._log("negative_sales", "validity", bad_sales)
        if "ship_days_actual" in self.df.columns:
            bad_ship = ((self.df["ship_days_actual"] < 0)
                        | (self.df["ship_days_actual"] > 60)).sum()
            self._log("implausible_ship_days", "validity", bad_ship)

    def check_timeliness(self) -> None:
        if "order_date" in self.df.columns:
            future = (self.df["order_date"] > pd.Timestamp.today()).sum()
            self._log("future_order_dates", "timeliness", future)
        if {"order_date", "shipping_date"} <= set(self.df.columns):
            backwards = (self.df["shipping_date"] < self.df["order_date"]).sum()
            self._log("ship_before_order", "timeliness", backwards)

    def check_sales_consistency(self, tolerance: float = 0.35) -> None:
        """sales should approximate price*qty; wide tolerance for discounts."""
        needed = {"sales", "product_price", "quantity"}
        if not needed <= set(self.df.columns):
            return
        expected = self.df["product_price"] * self.df["quantity"]
        with np.errstate(divide="ignore", invalid="ignore"):
            rel = np.abs(self.df["sales"] - expected) / expected.replace(0, np.nan)
        bad = (rel > tolerance).sum()
        self._log("sales_price_qty_mismatch", "consistency", bad,
                  f"tolerance={tolerance:.0%}")

    def run_all(self) -> pd.DataFrame:
        self.check_critical_nulls()
        self.check_duplicate_items()
        self.check_value_ranges()
        self.check_timeliness()
        self.check_sales_consistency()

        report = pd.DataFrame(self.results)
        report.insert(0, "run_ts", datetime.now().isoformat(timespec="seconds"))
        report.insert(1, "source", self.source)

        QUALITY_AUDIT_DIR.mkdir(parents=True, exist_ok=True)
        audit_path = QUALITY_AUDIT_DIR / "quality_audit_log.csv"
        report.to_csv(audit_path, mode="a", index=False,
                      header=not audit_path.exists())
        return report


def main() -> None:
    path = PROCESSED_DIR / "transactions_augmented.csv"
    if not path.exists():
        raise SystemExit("Run etl/augment_data.py first.")
    df = pd.read_csv(path, parse_dates=["order_date", "shipping_date"])
    report = DataQualityGates(df, source=path.name).run_all()
    print(report[["check", "dimension", "failed_rows", "failure_rate",
                  "status"]].to_string(index=False))
    fails = (report["status"] == "FAIL").sum()
    print(f"\n{fails}/{len(report)} gates failed. "
          f"Audit appended to data/quality_audit/quality_audit_log.csv")


if __name__ == "__main__":
    main()
