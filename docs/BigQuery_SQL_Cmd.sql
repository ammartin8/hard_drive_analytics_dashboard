-- Creating external tables from source parquet files
CREATE OR REPLACE EXTERNAL TABLE `my-project-name.hard_drive_dataset.hard_drive_data_tbl_ext` --UPDATE PROJECT NAME
OPTIONS (
  format = 'PARQUET',
  uris = ['gs://my-bucket-name/raw_data/*.parquet'] --UPDATE BUCKET NAME
);

-- Validate record counts
with t1 as (
SELECT date
, DATE(TIMESTAMP_MICROS(CAST(FLOOR(date / 1000) AS INT64))) as date_bq_fmt
, serial_number, model, capacity_bytes, failure, datacenter, cluster_id, vault_id, pod_id, pod_slot_num, is_legacy_format, smart_5_normalized, smart_5_raw, smart_187_normalized, smart_187_raw, smart_188_normalized, smart_188_raw, smart_197_normalized, smart_197_raw, smart_198_normalized, smart_198_raw
FROM `hard_drive_dataset.hard_drive_data_tbl_ext`
)
SELECT EXTRACT(YEAR FROM date_bq_fmt) as yr, COUNT(*)
FROM t1
GROUP BY yr
ORDER BY yr
;

-- Create materialized table
CREATE OR REPLACE TABLE `my-project-name.hard_drive_dataset.hard_drive_data_tbl` --UPDATE PROJECT NAME
PARTITION BY year_month AS
SELECT
date
, DATE(TIMESTAMP_MICROS(CAST(FLOOR(date / 1000) AS INT64))) as date_bq_fmt
, DATE_TRUNC(DATE(TIMESTAMP_MICROS(CAST(FLOOR(date / 1000) AS INT64))), MONTH) as year_month
, serial_number, model, capacity_bytes, failure, datacenter, cluster_id, vault_id, pod_id, pod_slot_num
, is_legacy_format, smart_5_normalized, smart_5_raw, smart_187_normalized, smart_187_raw, smart_188_normalized
, smart_188_raw, smart_197_normalized, smart_197_raw, smart_198_normalized, smart_198_raw 
FROM my-project-name.hard_drive_dataset.hard_drive_data_tbl_ext --UPDATE PROJECT NAME
;
