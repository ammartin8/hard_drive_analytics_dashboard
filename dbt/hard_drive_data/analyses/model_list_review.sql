with hard_drive_data as (
    select * from {{ ref("stg_hard_drive_data")}}
)
, model_info_list as (
select model
from hard_drive_data
group by model
order by model
)
select
*
from model_info_list

