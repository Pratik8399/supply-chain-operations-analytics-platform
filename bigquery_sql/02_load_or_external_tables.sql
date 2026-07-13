-- Load patterns. The Python loader (etl/load_to_bigquery.py) uses batch
-- load jobs (FREE — load jobs do not consume query bytes). Alternative
-- shown here: external tables over GCS for schema-on-read staging.

-- Option A (used by this project): batch load via Python client
--   client.load_table_from_file(..., LoadJobConfig(source_format=CSV))
--   Cost: $0 (load jobs are free); storage billed after free 10 GB.

-- Option B: external table over Google Cloud Storage (schema-on-read)
-- CREATE OR REPLACE EXTERNAL TABLE `supply_chain.ext_order_items`
-- OPTIONS (
--   format = 'CSV',
--   uris = ['gs://YOUR_BUCKET/processed/transactions_augmented.csv'],
--   skip_leading_rows = 1
-- );
-- Note: external-table queries scan the full file every time (no
-- partition pruning) — fine for exploration, wrong for repeated marts.

-- Promote staging -> fact after quality gates pass.
-- CTAS (CREATE OR REPLACE TABLE AS SELECT) instead of TRUNCATE+INSERT:
-- idempotent, atomic, and sandbox-friendly — the BigQuery sandbox does
-- not support DML statements, but CTAS works everywhere.
DROP TABLE IF EXISTS `supply_chain.fct_order_items`;
CREATE OR REPLACE TABLE `supply_chain.fct_order_items` AS
SELECT
  order_item_id,
  order_id,
  DATE(order_date) AS order_dt,
  DATE(shipping_date) AS shipping_dt,
  order_date,
  shipping_date,
  ship_days_actual,
  ship_days_scheduled,
  delivery_status,
  late_delivery_risk,
  order_status,
  shipping_mode,
  customer_id,
  customer_segment,
  market,
  order_region,
  order_country,
  category_name,
  product_name,
  product_price,
  quantity,
  discount,
  sales,
  order_item_total,
  order_profit,
  benefit_per_order
FROM `supply_chain.stg_order_items`
WHERE order_item_id IS NOT NULL;     -- gate-failed rows stay in staging

-- Derive dims from facts (conformed)
DROP TABLE IF EXISTS `supply_chain.dim_category`;
CREATE OR REPLACE TABLE `supply_chain.dim_category` AS
SELECT
  category_name,
  MIN(order_dt) AS first_seen,
  MAX(order_dt) AS last_seen,
  COUNT(DISTINCT product_name) AS n_products
FROM `supply_chain.fct_order_items`
GROUP BY 1;

CREATE OR REPLACE TABLE `supply_chain.dim_date` AS
SELECT d          AS date_key,
       EXTRACT(YEAR FROM d)    AS year,
       EXTRACT(QUARTER FROM d) AS quarter,
       EXTRACT(MONTH FROM d)   AS month,
       DATE_TRUNC(d, WEEK(MONDAY)) AS week_start,
       EXTRACT(QUARTER FROM d) = 4 AS is_q4
FROM UNNEST(GENERATE_DATE_ARRAY('2015-01-01', '2018-12-31')) AS d;
