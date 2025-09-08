MODEL (
  name stg.philadelphia_metar,
  kind FULL,
  gateway duckdb
);

SELECT
  reportTime as report_time_utc,
  reportTime::timestamp - INTERVAL '4 hours' as report_time_edt,
  reportTime::timestamp - INTERVAL '5 hours' as report_time_est,
  temp as temp_deg_c,
  ROUND((temp * (9 / 5)) + 32, 2) as temp_deg_f,
  pcp6hr as precip_last_6hrs_inches,
  pcp24hr as precip_last_24hrs_inches
FROM raw.philadelphia_metar;
