with model_manufacturer_lookup as (
    select
        model,
        manufacturer
    from {{ ref('2026_04_11_model_manufacturer_lookup') }}
)
, serial_number_list as (
select serial_number, model
from {{ ref("int_fct_drive_add_cols") }}
group by serial_number, model
)
, joined_data as (
    select snl.serial_number, snl.model, mml.manufacturer
    from serial_number_list as snl
    left join model_manufacturer_lookup mml
    on snl.model = mml.model
)
select serial_number, model, COALESCE(manufacturer, 'Unknown') as manufacturer
from joined_data