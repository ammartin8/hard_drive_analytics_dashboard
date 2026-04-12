with hard_drive_data as (
    select * from {{ ref("stg_hard_drive_data")}}
)
select
    {{ dbt_utils.generate_surrogate_key([
        'report_date',
        'serial_number',
        'model',
        'capacity_bytes',
        'datacenter',
        'cluster_id',
        'vault_id',
        'pod_id',
        'pod_slot_num'
    ]) }} as unique_device_event_id,
    -- dates
    report_date,

    -- datacenter/location identifiers
    datacenter,
    cluster_id,
    vault_id,
    pod_id,
    pod_slot_num,
    
    -- device identifiers

    serial_number,
    model,
    FLOOR((capacity_bytes/1000000000)) as capacity_gigabytes,
    capacity_bytes,

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

from hard_drive_data