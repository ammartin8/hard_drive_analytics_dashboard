WITH report_bounds AS (
    SELECT 
        MIN(report_date) as min_date,
        MAX(report_date) as max_date
    FROM {{ ref("int_fct_drive_add_cols") }}
)

SELECT 
    date_day,
    EXTRACT(YEAR FROM date_day) AS year_number,
    FORMAT('%02d', EXTRACT(MONTH FROM date_day)) AS month_number,
    FORMAT('%02d', EXTRACT(DAY FROM date_day)) AS day_number,
    EXTRACT(DAYOFWEEK FROM date_day) AS day_of_week,
    FORMAT('%03d', EXTRACT(DAYOFYEAR FROM date_day)) AS day_of_year,
    FORMAT('%02d', EXTRACT(WEEK FROM date_day)) AS week_of_year,     
    EXTRACT(QUARTER FROM date_day) AS quarter_number,
    FORMAT_DATE('%B', date_day) AS month_name,
    FORMAT_DATE('%A', date_day) AS day_name
FROM (
    SELECT d AS date_day
    FROM UNNEST(
        GENERATE_DATE_ARRAY(
            COALESCE((SELECT min_date FROM report_bounds), DATE '2023-01-01'),
            COALESCE((SELECT max_date FROM report_bounds), DATE '2025-12-31'),
            INTERVAL 1 DAY
        )
    ) AS d
) subquery

ORDER BY date_day