MODEL (
  name stg.philadelphia_ncei,
  kind INCREMENTAL_BY_TIME_RANGE(
    time_column "report_date"
  ),
  gateway duckdb
);

SELECT
  "date" as report_date,
  "tavg (degrees fahrenheit)" as avg_temp_deg_f,
  "tmax (degrees fahrenheit)" as max_temp_deg_f,
  "tmin (degrees fahrenheit)" as min_temp_deg_f,
  "prcp (inches)" as total_precip_inches
FROM raw.philadelphia_ncei;
