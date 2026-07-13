from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXPORT_DIR = PROJECT_ROOT / "dashboards" / "exports"
SCREENSHOT_DIR = PROJECT_ROOT / "dashboards" / "screenshots"
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def save_executive_overview():
    kpi = pd.read_csv(EXPORT_DIR / "kpi_summary.csv")
    monthly = pd.read_csv(EXPORT_DIR / "monthly_otif.csv")
    category = pd.read_csv(EXPORT_DIR / "category_performance.csv")

    monthly["month"] = pd.to_datetime(monthly["month"])

    total_revenue = float(kpi.loc[0, "total_revenue"])
    total_orders = int(kpi.loc[0, "total_orders"])
    overall_otif_pct = float(kpi.loc[0, "overall_otif_pct"])
    categories = int(kpi.loc[0, "categories"])
    weeks_covered = int(kpi.loc[0, "weeks_covered"])

    top_categories = category.sort_values(
        by="revenue", ascending=False
    ).head(10)

    fig = plt.figure(figsize=(16, 9))
    fig.suptitle(
        "Executive Overview - Supply Chain Operations",
        fontsize=20,
        fontweight="bold",
    )

    ax1 = fig.add_axes([0.05, 0.70, 0.18, 0.16])
    ax1.text(0.5, 0.62, f"{total_orders:,.0f}", ha="center", fontsize=23, fontweight="bold")
    ax1.text(0.5, 0.25, "Total Orders", ha="center", fontsize=12)
    ax1.axis("off")

    ax2 = fig.add_axes([0.25, 0.70, 0.18, 0.16])
    ax2.text(0.5, 0.62, f"${total_revenue:,.0f}", ha="center", fontsize=23, fontweight="bold")
    ax2.text(0.5, 0.25, "Total Revenue", ha="center", fontsize=12)
    ax2.axis("off")

    ax3 = fig.add_axes([0.45, 0.70, 0.18, 0.16])
    ax3.text(0.5, 0.62, f"{overall_otif_pct:.1f}%", ha="center", fontsize=23, fontweight="bold")
    ax3.text(0.5, 0.25, "Overall OTIF", ha="center", fontsize=12)
    ax3.axis("off")

    ax4 = fig.add_axes([0.65, 0.70, 0.13, 0.16])
    ax4.text(0.5, 0.62, f"{categories}", ha="center", fontsize=23, fontweight="bold")
    ax4.text(0.5, 0.25, "Categories", ha="center", fontsize=12)
    ax4.axis("off")

    ax5 = fig.add_axes([0.80, 0.70, 0.13, 0.16])
    ax5.text(0.5, 0.62, f"{weeks_covered}", ha="center", fontsize=23, fontweight="bold")
    ax5.text(0.5, 0.25, "Weeks Covered", ha="center", fontsize=12)
    ax5.axis("off")

    ax6 = fig.add_axes([0.07, 0.13, 0.40, 0.42])
    ax6.plot(monthly["month"], monthly["otif_pct"], marker="o")
    ax6.set_title("Monthly OTIF Trend")
    ax6.set_xlabel("Month")
    ax6.set_ylabel("OTIF %")
    ax6.tick_params(axis="x", rotation=45)

    ax7 = fig.add_axes([0.57, 0.13, 0.35, 0.42])
    ax7.barh(top_categories["category_name"], top_categories["revenue"])
    ax7.set_title("Top Categories by Revenue")
    ax7.set_xlabel("Revenue")
    ax7.invert_yaxis()

    output = SCREENSHOT_DIR / "tableau_executive_overview.png"
    plt.savefig(output, bbox_inches="tight", dpi=150)
    plt.close()
    print(f"Saved {output}")


def save_forecast_accuracy():
    accuracy = pd.read_csv(EXPORT_DIR / "forecast_accuracy.csv")
    results = pd.read_csv(EXPORT_DIR / "forecast_results.csv")

    results["week"] = pd.to_datetime(results["week"])

    best_accuracy = accuracy.sort_values("WMAPE_pct").head(15)
    bias_view = accuracy.sort_values("bias_pct", key=lambda s: s.abs()).head(15)

    sample_category = results["category_name"].value_counts().index[0]
    sample = results[results["category_name"] == sample_category].sort_values("week")

    fig = plt.figure(figsize=(16, 9))
    fig.suptitle("Forecast Accuracy Dashboard", fontsize=20, fontweight="bold")

    ax1 = fig.add_axes([0.07, 0.13, 0.38, 0.68])
    ax1.barh(best_accuracy["category_name"], best_accuracy["WMAPE_pct"])
    ax1.set_title("Best Categories by WMAPE")
    ax1.set_xlabel("WMAPE %")
    ax1.invert_yaxis()

    ax2 = fig.add_axes([0.56, 0.53, 0.36, 0.30])
    ax2.bar(bias_view["category_name"], bias_view["bias_pct"])
    ax2.set_title("Forecast Bias by Category")
    ax2.set_ylabel("Bias %")
    ax2.tick_params(axis="x", rotation=75)

    ax3 = fig.add_axes([0.56, 0.13, 0.36, 0.28])
    ax3.plot(sample["week"], sample["actual"], marker="o", label="Actual")
    ax3.plot(sample["week"], sample["predicted"], marker="o", label="Predicted")
    ax3.set_title(f"Actual vs Predicted Demand - {sample_category}")
    ax3.set_ylabel("Demand Units")
    ax3.tick_params(axis="x", rotation=45)
    ax3.legend()

    output = SCREENSHOT_DIR / "tableau_forecast_accuracy.png"
    plt.savefig(output, bbox_inches="tight", dpi=150)
    plt.close()
    print(f"Saved {output}")


def save_anomaly_monitoring():
    alerts = pd.read_csv(EXPORT_DIR / "anomaly_alerts.csv")
    detection = pd.read_csv(EXPORT_DIR / "detection_scorecard.csv")

    severity_counts = alerts["severity"].value_counts().reset_index()
    severity_counts.columns = ["severity", "alerts"]

    issue_counts = alerts["issue"].value_counts().reset_index()
    issue_counts.columns = ["issue", "alerts"]

    route_counts = alerts["route_to"].value_counts().reset_index()
    route_counts.columns = ["route_to", "alerts"]

    fig = plt.figure(figsize=(16, 9))
    fig.suptitle("Anomaly Monitoring Dashboard", fontsize=20, fontweight="bold")

    ax1 = fig.add_axes([0.07, 0.55, 0.25, 0.30])
    ax1.bar(severity_counts["severity"], severity_counts["alerts"])
    ax1.set_title("Alerts by Severity")
    ax1.set_ylabel("Alert Count")

    ax2 = fig.add_axes([0.40, 0.55, 0.25, 0.30])
    ax2.barh(issue_counts["issue"], issue_counts["alerts"])
    ax2.set_title("Alerts by Issue Type")
    ax2.set_xlabel("Alert Count")
    ax2.invert_yaxis()

    ax3 = fig.add_axes([0.72, 0.55, 0.23, 0.30])
    ax3.barh(route_counts["route_to"], route_counts["alerts"])
    ax3.set_title("Alerts by Routed Team")
    ax3.set_xlabel("Alert Count")
    ax3.invert_yaxis()

    ax4 = fig.add_axes([0.08, 0.08, 0.85, 0.32])
    ax4.axis("off")

    table_data = detection[
        ["issue", "injected", "detected_by_primary", "recall", "precision"]
    ].copy()

    table_data["recall"] = table_data["recall"].map(lambda x: f"{x:.3f}")
    table_data["precision"] = table_data["precision"].map(lambda x: f"{x:.3f}")

    table = ax4.table(
        cellText=table_data.values,
        colLabels=table_data.columns,
        loc="center",
        cellLoc="center",
    )
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 1.5)
    ax4.set_title("Detection Recall / Precision Scorecard", pad=20)

    output = SCREENSHOT_DIR / "tableau_anomaly_monitoring.png"
    plt.savefig(output, bbox_inches="tight", dpi=150)
    plt.close()
    print(f"Saved {output}")


if __name__ == "__main__":
    save_executive_overview()
    save_forecast_accuracy()
    save_anomaly_monitoring()