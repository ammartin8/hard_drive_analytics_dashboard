with hard_drive_data as (
    select * from {{ ref("stg_hard_drive_data")}}
)
, grp_model_info as (
select model, serial_number, capacity_bytes
from hard_drive_data
group by model, serial_number, capacity_bytes
)
select
count(distinct model) as models
, count(distinct serial_number) as serial_nums
from grp_model_info
