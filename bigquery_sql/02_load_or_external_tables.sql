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
CREATE OR REPLACE TABLE `supply_chain.fct_order_items`
PARTITION BY DATE(order_date)
CLUSTER BY category_name, market AS
SELECT * FROM `supply_chain.stg_order_items`
WHERE sales IS NOT NULL
  AND quantity IS NOT NULL;      -- gate-failed rows stay in staging

-- Derive dims from facts (conformed)
CREATE OR REPLACE TABLE `supply_chain.dim_category` AS
SELECT category_name,
       MIN(DATE(order_date)) AS first_seen,
       MAX(DATE(order_date)) AS last_seen,
       COUNT(DISTINCT product_name) AS n_products
FROM `supply_chain.fct_order_items` GROUP BY 1;

CREATE OR REPLACE TABLE `supply_chain.dim_date` AS
SELECT d          AS date_key,
       EXTRACT(YEAR FROM d)    AS year,
       EXTRACT(QUARTER FROM d) AS quarter,
       EXTRACT(MONTH FROM d)   AS month,
       DATE_TRUNC(d, WEEK(MONDAY)) AS week_start,
       EXTRACT(QUARTER FROM d) = 4 AS is_q4
FROM UNNEST(GENERATE_DATE_ARRAY('2015-01-01', '2018-12-31')) AS d;
