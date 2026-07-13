"""
Data governance: role-based access simulation + audit trail.

Enforces least-privilege reads over the project's datasets and logs 100%
of access attempts (approved AND denied) with confidentiality labels.
This mirrors the control pattern an enterprise warehouse implements with
grants + access history; here it is expressed in Python so the repo can
demonstrate the policy without a live Snowflake account.

Usage:
    python etl/data_governance.py     # runs a demo access scenario
"""
from __future__ import annotations

from datetime import datetime

import pandas as pd

from config import GOVERNANCE_DIR, OUTPUT_DIR, PROCESSED_DIR

ROLES = {
    "analyst":        {"read": {"forecast", "anomalies", "weekly_demand"}},
    "logistics":      {"read": {"anomalies", "transactions"}},
    "demand_planner": {"read": {"forecast", "weekly_demand", "anomalies"}},
    "finance_ops":    {"read": {"transactions", "anomalies"}},
    "admin":          {"read": {"*"}},
}

CONFIDENTIALITY = {
    "transactions": "confidential",     # customer-level detail
    "weekly_demand": "internal",
    "forecast": "internal",
    "anomalies": "internal",
}

DATASETS = {
    "transactions": PROCESSED_DIR / "transactions_augmented.csv",
    "weekly_demand": PROCESSED_DIR / "weekly_demand_augmented.csv",
    "forecast": OUTPUT_DIR / "forecast_results.csv",
    "anomalies": OUTPUT_DIR / "anomaly_alerts.csv",
}


class GovernedAccess:
    def __init__(self):
        self.log_path = GOVERNANCE_DIR / "access_audit.csv"
        GOVERNANCE_DIR.mkdir(exist_ok=True)

    def _log(self, user, role, dataset, status, reason=""):
        row = pd.DataFrame([{
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "user": user, "role": role, "dataset": dataset,
            "confidentiality": CONFIDENTIALITY.get(dataset, "internal"),
            "status": status, "reason": reason,
        }])
        row.to_csv(self.log_path, mode="a", index=False,
                   header=not self.log_path.exists())

    def read(self, user: str, role: str, dataset: str) -> pd.DataFrame:
        allowed = ROLES.get(role, {}).get("read", set())
        if "*" not in allowed and dataset not in allowed:
            self._log(user, role, dataset, "DENIED", "insufficient role grants")
            raise PermissionError(
                f"role '{role}' has no read grant on '{dataset}'")
        self._log(user, role, dataset, "APPROVED")
        return pd.read_csv(DATASETS[dataset])


def main() -> None:
    gov = GovernedAccess()
    scenarios = [
        ("priya", "demand_planner", "forecast"),
        ("marco", "logistics", "anomalies"),
        ("intern01", "analyst", "transactions"),   # DENIED: confidential
        ("dora", "admin", "transactions"),
    ]
    for user, role, ds in scenarios:
        try:
            df = gov.read(user, role, ds)
            print(f"APPROVED  {user:<9} ({role}) read {ds}: {len(df):,} rows")
        except PermissionError as e:
            print(f"DENIED    {user:<9} ({role}) read {ds}: {e}")
        except FileNotFoundError:
            print(f"APPROVED  {user:<9} ({role}) read {ds}: (file not built yet)")
    print(f"\nAudit trail: {gov.log_path}")


if __name__ == "__main__":
    main()
