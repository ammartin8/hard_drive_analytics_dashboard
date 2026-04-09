select
    -- dates
    DATE(TIMESTAMP_MICROS(CAST(FLOOR(date / 1000) AS INT64))) as report_date,

    -- identifiers
    datacenter,
    cluster_id,
    vault_id,
    pod_id,
    pod_slot_num,
    
    -- device identifiers
    serial_number,
    model,
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
from {{ source('raw_data', 'hard_drive_data_tbl_ext') }}