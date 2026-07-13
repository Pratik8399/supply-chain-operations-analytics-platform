-- BigQuery DDL: pragmatic dimensional model for the DataCo order-items data.
-- Design note: DataCo is a single flat order-items file, so the schema is
-- deliberately lean — one staging table, two facts, two small dims — rather
-- than a fabricated full star schema. Partitioning + clustering are the
-- cost levers: BigQuery bills by bytes scanned, and both cut scan volume.

-- Dataset (also created automatically by etl/load_to_bigquery.py)
-- CREATE SCHEMA IF NOT EXISTS `PROJECT_ID.supply_chain`;

-- Staging: raw standardized order items, as loaded from Python ETL


-- Dimensions (dim_category, dim_date) are likewise created by CTAS in 02.

-- Fact: anomaly alerts (loaded by etl/load_to_bigquery.py from
-- outputs/anomaly_alerts.csv — created here so the load target exists
-- before file 05's views reference it)
CREATE OR REPLACE TABLE `supply_chain.fct_anomaly_alerts` (
  issue STRING,
  key STRING,
  detail STRING,
  severity STRING,
  route_to STRING
);
