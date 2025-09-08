MODEL (
  name stg.philadelphia_crime,
  kind FULL,
  gateway duckdb
);

SELECT
  cartodb_id as id,
  dispatch_date,
  EXTRACT(year from dispatch_date) as dispatch_year,
  EXTRACT(month from dispatch_date) as dispatch_month,
  EXTRACT(day from dispatch_date) as dispatch_day,
  text_general_code as incident_type
FROM raw.philadelphia_crime;
