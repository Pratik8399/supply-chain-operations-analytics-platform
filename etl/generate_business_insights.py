"""
Automated narrative insight generation (NLP-style rule templates).

Converts pipeline outputs into stakeholder-ready language: an executive
summary in markdown plus a routable action-item table. Template-based by
design — deterministic, auditable, zero API cost — with the structure an
LLM could later slot into (each template is effectively a prompt contract).

Reads:   outputs/anomaly_alerts.csv, outputs/forecast_accuracy.csv,
         dashboards/exports/kpi_summary.csv, dashboards/exports/monthly_otif.csv
Writes:  outputs/executive_summary.md
         outputs/stakeholder_action_items.csv

Usage:
    python etl/generate_business_insights.py
"""

from __future__ import annotations

from datetime import date

import pandas as pd

from config import OUTPUT_DIR, PROJECT_ROOT

EXPORT_DIR = PROJECT_ROOT / "dashboards" / "exports"

SEVERITY_SLA = {"critical": "within 24 hours",
                "high": "within 3 business days",
                "medium": "within 2 weeks"}

ISSUE_NARRATIVE = {
    "cost_spike": ("billing amounts far above catalog-expected totals",
                   "Reconcile flagged order totals against contract pricing "
                   "before month-end close."),
    "sla_breach": ("shipments delivered 4+ days past the scheduled window",
                   "Review carrier and route performance for the flagged "
                   "orders; escalate repeat lanes."),
    "duplicate_transactions": ("exact duplicate order-item records",
                               "De-duplicate before revenue reporting; add a "
                               "uniqueness constraint at the curated layer."),
    "missing_values": ("orders missing critical fields (sales/quantity)",
                       "Trace to the source extract; block at ingestion once "
                       "root cause is fixed."),
    "multivariate_outlier": ("unusual combinations of amount, quantity, "
                             "discount and delay",
                             "Analyst review; label outcomes to tune the model."),
    "demand_shock": ("weekly demand far outside the category's local baseline",
                     "Confirm drivers (promo, stockout, market event) and "
                     "adjust replenishment plans."),
    "forecast_drift": ("actual demand diverging >15% from plan",
                       "Review planner assumptions for the flagged "
                       "category-weeks; re-baseline if drift persists."),
}


def load(name: str, folder=OUTPUT_DIR) -> pd.DataFrame:
    p = folder / name
    return pd.read_csv(p) if p.exists() else pd.DataFrame()


def build_action_items(alerts: pd.DataFrame) -> pd.DataFrame:
    if alerts.empty:
        return pd.DataFrame()
    grp = (alerts.groupby(["route_to", "issue", "severity"])
                 .size().rename("alert_count").reset_index())
    grp["what_we_saw"] = grp["issue"].map(lambda i: ISSUE_NARRATIVE[i][0])
    grp["recommended_action"] = grp["issue"].map(lambda i: ISSUE_NARRATIVE[i][1])
    grp["review_sla"] = grp["severity"].map(SEVERITY_SLA)
    order = {"critical": 0, "high": 1, "medium": 2}
    return grp.sort_values(["severity", "alert_count"],
                           key=lambda s: s.map(order) if s.name == "severity" else s,
                           ascending=[True, False])


def build_summary(alerts, acc, kpi, otif) -> str:
    lines = [f"# Executive Summary — Operations Analytics",
             f"*Generated {date.today():%d %b %Y} by the automated insight "
             f"module (template-based narrative generation).*", ""]

    if not kpi.empty:
        k = kpi.iloc[0]
        lines += ["## Business at a glance",
                  f"Revenue of ${k['total_revenue']:,.0f} across "
                  f"{int(k['total_orders']):,} orders and {int(k['categories'])} "
                  f"categories, with overall on-time-in-full at "
                  f"{k['overall_otif_pct']:.1f}%.", ""]

    if not otif.empty and len(otif) >= 2:
        last, prev = otif.iloc[-1], otif.iloc[-2]
        direction = "improved" if last["otif_pct"] >= prev["otif_pct"] else "declined"
        lines += [f"OTIF {direction} in the latest month "
                  f"({last['otif_pct']:.1f}% vs {prev['otif_pct']:.1f}% prior), "
                  f"with average shipping delay of "
                  f"{last['avg_ship_delay']:.1f} days.", ""]

    if not alerts.empty:
        crit = (alerts["severity"] == "critical").sum()
        high = (alerts["severity"] == "high").sum()
        top_team = alerts["route_to"].value_counts().idxmax()
        top_issue = alerts["issue"].value_counts().idxmax()
        lines += ["## Alert posture",
                  f"{len(alerts):,} open alerts ({crit} critical, {high} high). "
                  f"The largest queue routes to **{top_team}**, driven "
                  f"primarily by {ISSUE_NARRATIVE[top_issue][0]}.",
                  f"Recommended first action: {ISSUE_NARRATIVE[top_issue][1]}", ""]

    if not acc.empty:
        best, worst = acc.iloc[0], acc.iloc[-1]
        lines += ["## Forecast health",
                  f"Demand forecast WMAPE ranges from "
                  f"{best['WMAPE_pct']:.1f}% ({best['category_name']}) to "
                  f"{worst['WMAPE_pct']:.1f}% ({worst['category_name']}). "
                  f"Categories above 30% WMAPE should be prioritized for "
                  f"planner review; persistent positive bias indicates "
                  f"systematic over-forecasting and excess inventory risk.", ""]

    lines += ["## Where to act",
              "Detailed, team-routed items with review SLAs: "
              "`outputs/stakeholder_action_items.csv` (also surfaced on the "
              "Anomaly Detection Center dashboard page)."]
    return "\n".join(lines)


def main() -> None:
    alerts = load("anomaly_alerts.csv")
    acc = load("forecast_accuracy.csv")
    kpi = load("kpi_summary.csv", EXPORT_DIR)
    otif = load("monthly_otif.csv", EXPORT_DIR)

    actions = build_action_items(alerts)
    actions.to_csv(OUTPUT_DIR / "stakeholder_action_items.csv", index=False)
    summary = build_summary(alerts, acc, kpi, otif)
    (OUTPUT_DIR / "executive_summary.md").write_text(summary, encoding="utf-8")

    print(f"Wrote executive_summary.md and stakeholder_action_items.csv "
          f"({len(actions)} routed action groups)")


if __name__ == "__main__":
    main()
