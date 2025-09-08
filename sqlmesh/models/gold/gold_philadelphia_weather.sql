MODEL (
  name gold.philadelphia_weather,
  kind INCREMENTAL_BY_TIME_RANGE(
    time_column "report_date"
  ),
  gateway duckdb
);

WITH ncei AS (
  SELECT
    "report_date"::DATE as report_date,
    avg_temp_deg_f::DECIMAL as avg_temp_deg_f,
    max_temp_deg_f::DECIMAL as max_temp_deg_f,
    min_temp_deg_f::DECIMAL as min_temp_deg_f,
    total_precip_inches::DECIMAL as total_precip_inches
  FROM stg.philadelphia_ncei
), metar as (
  SELECT
    (report_time_est)::DATE as report_date,
    MAX(temp_deg_f) as max_temp_deg_f,
    ROUND(AVG(temp_deg_f), 2) as avg_temp_deg_f,
    MIN(temp_deg_f) as min_temp_deg_f,
    COALESCE(ROUND(SUM(precip_last_6hrs_inches),3),0) as total_precip_inches
  FROM stg.philadelphia_metar
  GROUP BY report_date
)
SELECT
  report_date,
  COALESCE(metar.avg_temp_deg_f, ncei.avg_temp_deg_f) as avg_temp_deg_f,
  COALESCE(metar.max_temp_deg_f, ncei.max_temp_deg_f) as max_temp_deg_f,
  COALESCE(metar.min_temp_deg_f, ncei.min_temp_deg_f) as min_temp_deg_f,
  COALESCE(metar.total_precip_inches, ncei.total_precip_inches) as total_precip_inches
FROM metar
FULL JOIN ncei
USING(report_date);
