"""
CI regression gate for the anomaly detectors.

Fails the build if any injected transaction-level anomaly class is not
fully recalled, or if demand shocks are missed — i.e. detector changes
cannot silently degrade recall against the ground-truth manifest.
Run after the pipeline on the dev sample (see .github/workflows/ci.yml).
"""
import sys
from pathlib import Path

import pandas as pd

SCORECARD = Path(__file__).resolve().parent.parent / "outputs" / "detection_scorecard.csv"

TRANSACTION_CLASSES = {"sla_breach", "cost_spike",
                       "duplicate_transactions", "missing_values"}
MIN_RECALL = 1.0            # deterministic injections must be fully recovered
MIN_DEMAND_RECALL = 0.8     # demand shocks: allow slight statistical slack


def main() -> int:
    if not SCORECARD.exists():
        print(f"FAIL: {SCORECARD} missing — did the pipeline run?")
        return 1
    sc = pd.read_csv(SCORECARD).set_index("issue")
    failures = []
    for issue in TRANSACTION_CLASSES:
        r = sc.loc[issue, "recall"]
        if r < MIN_RECALL:
            failures.append(f"{issue}: recall {r} < {MIN_RECALL}")
    if "demand_shock" in sc.index:
        r = sc.loc["demand_shock", "recall"]
        if r < MIN_DEMAND_RECALL:
            failures.append(f"demand_shock: recall {r} < {MIN_DEMAND_RECALL}")
    if failures:
        print("DETECTION REGRESSION:\n  " + "\n  ".join(failures))
        return 1
    print("Detection recall gate PASSED:")
    print(sc[["injected", "recall", "precision"]].to_string())
    return 0


if __name__ == "__main__":
    sys.exit(main())
