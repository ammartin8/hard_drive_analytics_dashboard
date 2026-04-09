/*
To do:
- One row per event
- Add primary key
*/

with draft_drive_data as (
    select
    report_date,
    datacenter,
    cluster_id,
    vault_id,
    pod_id,
    pod_slot_num,
    unique_device_event_id,
    serial_number,
    model,
    capacity_gigabytes,
    failure,
    smart_5_normalized,
    smart_5_raw,
    smart_187_normalized,
    smart_187_raw,
    smart_188_normalized,
    smart_188_raw,
    smart_197_normalized,
    smart_197_raw,
    smart_198_normalized,
    smart_198_raw
    from {{ref("int_fct_drive_add_cols")}}
)
, join_device_inv_and_dates as (
    select
    -- Date info 
    dda.report_date,
    dd.year_number,
    dd.month_number,
    dd.day_number,
    dd.day_of_week,
    dd.day_of_year,
    week_of_year,
    quarter_number,
    month_name,
    day_name,

    -- Datacenter/Location info
    dda.datacenter,
    dda.cluster_id,
    dda.vault_id,
    dda.pod_id,
    dda.pod_slot_num,

    -- Device info
    ddi.manufacturer,
    dda.model,
    dda.capacity_gigabytes,
    dda.serial_number,

    --SMART attrs & failed drive info
    dda.failure,
    dda.smart_5_normalized,
    dda.smart_5_raw,
    dda.smart_187_normalized,
    dda.smart_187_raw,
    dda.smart_188_normalized,
    dda.smart_188_raw,
    dda.smart_197_normalized,
    dda.smart_197_raw,
    dda.smart_198_normalized,
    dda.smart_198_raw
    from draft_drive_data as dda
    left join {{ref("dim_device_inventory")}} as ddi
    on dda.serial_number = ddi.serial_number
    left join {{ref("dim_date")}} as dd
    on dda.report_date = dd.date_day
)
select *
from join_device_inv_and_dates