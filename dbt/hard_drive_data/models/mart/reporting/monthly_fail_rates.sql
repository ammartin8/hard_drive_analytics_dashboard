select
year_number, month_number, month_name, quarter_number, year_month, month_year_name
, sum(failure) as failed_drives
, count(distinct serial_number) as total_drives
, sum(failure) / count(distinct serial_number) * 100 as failure_rate
from {{ref("fct_drive_health_snapshots")}}
group by year_number, month_number, month_name, quarter_number, year_month, month_year_name
order by year_number, month_number
