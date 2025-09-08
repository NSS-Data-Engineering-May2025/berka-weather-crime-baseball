MODEL(
  name stg.historical_baseball,
  kind INCREMENTAL_BY_TIME_RANGE (
    time_column game_date
  ),
  gateway duckdb
);

SELECT
  game_date,
  EXTRACT(YEAR FROM game_date) AS game_year,
  EXTRACT(MONTH FROM game_date) AS game_month,
  EXTRACT(DAY FROM game_date) AS game_day,
  visiting_team,
  visiting_team_game_number::INT,
  home_team,
  home_team_game_number::INT,
  visiting_team_score::INT,
  home_team_score::INT,
  day_night,
  park_id,
  time_of_game_minutes::INT
FROM raw.historical_baseball;
