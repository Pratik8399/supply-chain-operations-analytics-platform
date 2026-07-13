-- BigQuery DDL: pragmatic dimensional model for the DataCo order-items data.
-- Design note: DataCo is a single flat order-items file, so the schema is
-- deliberately lean — one staging table, two facts, two small dims — rather
-- than a fabricated full star schema. Partitioning + clustering are the
-- cost levers: BigQuery bills by bytes scanned, and both cut scan volume.

-- Dataset (also created automatically by etl/load_to_bigquery.py)
-- CREATE SCHEMA IF NOT EXISTS `PROJECT_ID.supply_chain`;

-- Staging: raw standardized order items, as loaded from Python ETL
CREATE TABLE IF NOT EXISTS `supply_chain.stg_order_items` (
    order_item_id        INT64,
    order_id             INT64,
    order_date           TIMESTAMP,
    shipping_date        TIMESTAMP,
    ship_days_actual     INT64,
    ship_days_scheduled  INT64,
    delivery_status      STRING,
    late_delivery_risk   INT64,
    order_status         STRING,
    shipping_mode        STRING,
    customer_id          INT64,
    customer_segment     STRING,
    market               STRING,
    order_region         STRING,
    order_country        STRING,
    category_name        STRING,
    product_name         STRING,
    product_price        FLOAT64,
    quantity             FLOAT64,
    discount             FLOAT64,
    sales                FLOAT64,
    order_item_total     FLOAT64,
    order_profit         FLOAT64
)
PARTITION BY DATE(order_date)
CLUSTER BY category_name, market;

-- Fact: curated order items is created by CTAS in
-- 02_load_or_external_tables.sql (CREATE OR REPLACE TABLE ... AS SELECT),
-- which is sandbox-friendly: the BigQuery sandbox does not support DML
-- (TRUNCATE/INSERT), but DDL + CTAS work.

-- Fact: weekly demand grid with forecast + inventory augmentation
CREATE TABLE IF NOT EXISTS `supply_chain.fct_weekly_demand` (
    category_name    STRING,
    week             DATE,
    demand_units     FLOAT64,
    demand_value     FLOAT64,
    orders           INT64,
    avg_price        FLOAT64,
    forecast_units   FLOAT64,
    inventory_units  FLOAT64,
    holding_cost     FLOAT64
)
PARTITION BY week
CLUSTER BY category_name;

-- Dimensions (dim_category, dim_date) are likewise created by CTAS in 02.

-- Fact: anomaly alerts (loaded by etl/load_to_bigquery.py from
-- outputs/anomaly_alerts.csv — created here so the load target exists
-- before file 05's views reference it)
CREATE TABLE IF NOT EXISTS `supply_chain.fct_anomaly_alerts` (
    issue     STRING,
    key       STRING,
    detail    STRING,
    severity  STRING,
    route_to  STRING
);
