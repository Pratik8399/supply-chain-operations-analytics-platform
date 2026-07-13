"""
Central configuration for the supply chain analytics platform.

Everything tunable lives here: file paths, the DataCo -> canonical column
mapping, synthetic-augmentation parameters, and the controlled anomaly
injection rates (each rate maps 1:1 to a detector + a validation row in
the injection manifest).
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"
SAMPLE_DIR = PROJECT_ROOT / "data" / "sample"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
QUALITY_AUDIT_DIR = PROJECT_ROOT / "data" / "quality_audit"
OUTPUT_DIR = PROJECT_ROOT / "outputs"
GOVERNANCE_DIR = PROJECT_ROOT / "governance"

RAW_FILE = RAW_DIR / "DataCoSupplyChainDataset.csv"
SAMPLE_FILE = SAMPLE_DIR / "sample_dataco_5k.csv"

SEED = 42

# ---------------------------------------------------------------------
# DataCo raw column -> canonical snake_case mapping (subset we use).
# The raw file is latin-1 encoded; ingestion handles that.
# ---------------------------------------------------------------------
COLUMN_MAP = {
    "Order Id": "order_id",
    "Order Item Id": "order_item_id",
    "order date (DateOrders)": "order_date",
    "shipping date (DateOrders)": "shipping_date",
    "Days for shipping (real)": "ship_days_actual",
    "Days for shipment (scheduled)": "ship_days_scheduled",
    "Delivery Status": "delivery_status",
    "Late_delivery_risk": "late_delivery_risk",
    "Order Status": "order_status",
    "Shipping Mode": "shipping_mode",
    "Customer Id": "customer_id",
    "Customer Segment": "customer_segment",
    "Market": "market",
    "Order Region": "order_region",
    "Order Country": "order_country",
    "Category Name": "category_name",
    "Product Name": "product_name",
    "Product Price": "product_price",
    "Order Item Quantity": "quantity",
    "Order Item Discount": "discount",
    "Sales": "sales",
    "Order Item Total": "order_item_total",
    "Order Profit Per Order": "order_profit",
    "Benefit per order": "benefit_per_order",
}

CRITICAL_COLUMNS = ["order_id", "order_date", "sales", "quantity",
                    "category_name", "customer_id"]

# ---------------------------------------------------------------------
# Synthetic augmentation (columns real DataCo lacks)
# ---------------------------------------------------------------------
AUGMENT = {
    "forecast_noise_sigma": 0.08,   # baseline forecast error ~8% (realistic planner MAPE)
    "forecast_bias": 0.02,          # planners over-forecast slightly on average
    "inventory_cover_days": (12, 35),  # holding between ~2-5 weeks of demand
    "unit_holding_cost_rate": 0.18,    # annualized holding cost fraction of price
}

# ---------------------------------------------------------------------
# Controlled anomaly injection (fraction of eligible rows / groups).
# Every injected key is logged to data/processed/injection_manifest.csv
# ---------------------------------------------------------------------
INJECTION = {
    "sla_breach": 0.010,            # shipping blows past schedule by 4-10 days
    "cost_spike": 0.006,            # order_item_total inflated 2.5-5x (billing error)
    "duplicate_transactions": 0.004,  # exact duplicate order items re-appended
    "missing_values": 0.008,        # critical fields nulled (sales / quantity)
    "demand_shock_weeks": 6,        # category-weeks with demand shifted +/- 45-80%
}

# Forecast-drift alert threshold used by the anomaly detector
DRIFT_THRESHOLD_PCT = 15.0

# Database (local dev default: SQLite file; swap to Snowflake in prod)
DB_URL = f"sqlite:///{PROJECT_ROOT / 'data' / 'processed' / 'supply_chain.db'}"
