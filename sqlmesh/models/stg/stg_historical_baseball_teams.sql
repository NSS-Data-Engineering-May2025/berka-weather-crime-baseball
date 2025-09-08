MODEL (
  name stg.historical_baseball_teams,
  kind INCREMENTAL_BY_UNIQUE_KEY (
    unique_key team
  ),
  gateway duckdb
);

SELECT
  team,
  city,
  nickname
FROM raw.historical_baseball_teams;
