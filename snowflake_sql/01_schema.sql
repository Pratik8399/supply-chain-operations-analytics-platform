-- Snowflake schema for the supply chain analytics platform.
-- Local dev uses SQLite/pandas; this DDL is the production target.

CREATE SCHEMA IF NOT EXISTS SUPPLY_CHAIN;

CREATE OR REPLACE TABLE SUPPLY_CHAIN.FCT_ORDER_ITEMS (
    order_item_id       NUMBER PRIMARY KEY,
    order_id            NUMBER,
    order_date          TIMESTAMP_NTZ,
    shipping_date       TIMESTAMP_NTZ,
    ship_days_actual    NUMBER,
    ship_days_scheduled NUMBER,
    delivery_status     VARCHAR,
    late_delivery_risk  NUMBER(1),
    order_status        VARCHAR,
    shipping_mode       VARCHAR,
    customer_id         NUMBER,
    customer_segment    VARCHAR,
    market              VARCHAR,
    order_region        VARCHAR,
    category_name       VARCHAR,
    product_name        VARCHAR,
    product_price       NUMBER(12,2),
    quantity            NUMBER,
    discount            NUMBER(12,2),
    sales               NUMBER(12,2),
    order_item_total    NUMBER(12,2),
    order_profit        NUMBER(12,2)
);

CREATE OR REPLACE TABLE SUPPLY_CHAIN.FCT_WEEKLY_DEMAND (
    category_name   VARCHAR,
    week            DATE,
    demand_units    NUMBER,
    demand_value    NUMBER(14,2),
    forecast_units  NUMBER,
    inventory_units NUMBER,
    holding_cost    NUMBER(12,2),
    PRIMARY KEY (category_name, week)
);

CREATE OR REPLACE TABLE SUPPLY_CHAIN.ANOMALY_ALERTS (
    alert_id    NUMBER IDENTITY PRIMARY KEY,
    issue       VARCHAR,
    key         VARCHAR,
    detail      VARCHAR,
    severity    VARCHAR,
    route_to    VARCHAR,
    detected_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Governance: rely on Snowflake RBAC in production
-- (CREATE ROLE demand_planner; GRANT SELECT ON FCT_WEEKLY_DEMAND TO ROLE ...)
-- plus ACCESS_HISTORY for the audit trail this repo simulates in Python.
