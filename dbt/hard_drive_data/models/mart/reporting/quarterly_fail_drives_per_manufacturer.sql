select
year_number, quarter_number, manufacturer
, sum(failure) as failed_drives
, count(distinct serial_number) as total_drives
, sum(failure) / count(distinct serial_number) * 100 as failure_rate
from {{ref("fct_drive_health_snapshots")}}
group by year_number, quarter_number, manufacturer
order by year_number, quarter_number, manufacturer
