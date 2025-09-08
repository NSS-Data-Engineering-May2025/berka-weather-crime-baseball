MODEL(
  name stg.historical_baseball_ballparks,
  kind INCREMENTAL_BY_UNIQUE_KEY(
    unique_key park_id
  ),
  gateway duckdb
);

SELECT
  parkid as park_id,
  "name" as park_name,
  "city" as park_city,
  "state" as park_state
FROM raw.historical_baseball_ballparks;
