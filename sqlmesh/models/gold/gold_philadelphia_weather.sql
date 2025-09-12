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
    avg_temp_deg_f::DECIMAL(5,2) as avg_temp_deg_f,
    max_temp_deg_f::DECIMAL(5,2) as max_temp_deg_f,
    min_temp_deg_f::DECIMAL(5,2) as min_temp_deg_f,
    total_precip_inches::DECIMAL(5,3) as total_precip_inches
  FROM stg.philadelphia_ncei
), metar as (
  SELECT
    (report_time_est)::DATE as report_date,
    MAX(temp_deg_f) as max_temp_deg_f,
    ROUND(AVG(temp_deg_f), 2) as avg_temp_deg_f,
    MIN(temp_deg_f) as min_temp_deg_f,
    COALESCE(ROUND(SUM(precip_last_6hrs_inches),3),0) as total_precip_inches,
    COUNT(report_time_est) as daily_metar_count
  FROM stg.philadelphia_metar
  GROUP BY report_date
)
SELECT
  report_date,
  CASE WHEN daily_metar_count > 15
    THEN COALESCE(metar.avg_temp_deg_f, ncei.avg_temp_deg_f)
    ELSE COALESCE(ncei.avg_temp_deg_f, metar.avg_temp_deg_f) END as avg_temp_deg_f,
  CASE WHEN daily_metar_count > 15 AND metar.avg_temp_deg_f IS NOT NULL
    THEN 'METAR'
    WHEN ncei.avg_temp_deg_f IS NOT NULL
    THEN 'NCEI'
    WHEN metar.avg_temp_deg_f IS NOT NULL
    THEN 'METAR - INCOMPLETE'
    ELSE 'NA' END as avg_temp_deg_f_source,
  CASE WHEN daily_metar_count > 15
    THEN COALESCE(metar.max_temp_deg_f, ncei.max_temp_deg_f)
    ELSE COALESCE(ncei.max_temp_deg_f, metar.max_temp_deg_f) END as max_temp_deg_f,
  CASE WHEN daily_metar_count > 15 AND metar.max_temp_deg_f IS NOT NULL
    THEN 'METAR'
    WHEN ncei.max_temp_deg_f IS NOT NULL
    THEN 'NCEI'
    WHEN metar.max_temp_deg_f IS NOT NULL
    THEN 'METAR - INCOMPLETE'
    ELSE 'NA' END as max_temp_deg_f_source,
  CASE WHEN daily_metar_count > 15
    THEN COALESCE(metar.min_temp_deg_f, ncei.min_temp_deg_f)
    ELSE COALESCE(ncei.min_temp_deg_f, metar.min_temp_deg_f) END as min_temp_deg_f,
  CASE WHEN daily_metar_count > 15 AND metar.min_temp_deg_f IS NOT NULL
    THEN 'METAR'
    WHEN ncei.min_temp_deg_f IS NOT NULL
    THEN 'NCEI'
    WHEN metar.min_temp_deg_f IS NOT NULL
    THEN 'METAR - INCOMPLETE'
    ELSE 'NA' END as min_temp_deg_f_source,
  CASE WHEN daily_metar_count > 15
    THEN COALESCE(metar.total_precip_inches, ncei.total_precip_inches)
    ELSE COALESCE(ncei.total_precip_inches, metar.total_precip_inches) END as total_precip_inches,
  CASE WHEN daily_metar_count > 15 AND metar.total_precip_inches IS NOT NULL
    THEN 'METAR'
    WHEN ncei.total_precip_inches IS NOT NULL
    THEN 'NCEI'
    WHEN metar.total_precip_inches IS NOT NULL
    THEN 'METAR - INCOMPLETE'
    ELSE 'NA' END as total_precip_inches_source
FROM metar
FULL JOIN ncei
USING(report_date);
