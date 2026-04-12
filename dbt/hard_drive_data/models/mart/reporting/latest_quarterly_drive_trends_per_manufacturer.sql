select
year_number, quarter_number, manufacturer, model
, sum(failure) as failed_drives
, count(distinct serial_number) as total_drives
, round((sum(failure) / count(distinct serial_number)) *100, 2)  as failure_rate
from {{ref("fct_drive_health_snapshots")}}
group by year_number, quarter_number, manufacturer, model
order by year_number, quarter_number, manufacturer, model
