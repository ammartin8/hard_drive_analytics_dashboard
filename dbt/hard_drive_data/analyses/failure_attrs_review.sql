with t1 as (
SELECT serial_number, failure, smart_5_raw, smart_5_normalized, smart_187_raw
, smart_187_normalized, smart_188_raw, smart_188_normalized,smart_197_raw
, smart_197_normalized, smart_198_raw, smart_198_normalized
FROM {{ref("int_fct_drive_add_cols")}}
where report_date = DATE '2025-01-01'
)
select failure
, count(distinct serial_number) as drives
, avg(smart_5_raw) as raw_5
, avg(smart_5_normalized) as norm_5
, avg(smart_187_raw) raw_187
, avg(smart_187_normalized) as norm_187
, avg(smart_188_raw) raw_188
, avg(smart_188_normalized) as norm_188
, avg(smart_197_raw) raw_197
, avg(smart_197_normalized) as norm_197
, avg(smart_198_raw) raw_198
, avg(smart_198_normalized) as norm_198
from t1
group by failure