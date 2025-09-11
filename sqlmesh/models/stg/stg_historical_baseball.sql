MODEL(
  name stg.historical_baseball,
  kind INCREMENTAL_BY_TIME_RANGE (
    time_column game_date
  ),
  audits (
    assert_unique_values(unique_key := historical_game_id)
  ),
  gateway duckdb
);

SELECT
  game_date,
  EXTRACT(YEAR FROM game_date) AS season,
  CONCAT(season, home_team, home_team_game_number, visiting_team, visiting_team_game_number) as historical_game_id,
  visiting_team AS away_team,
  visiting_team_game_number::INT AS away_team_game_number,
  home_team,
  home_team_game_number::INT AS home_team_game_number,
  visiting_team_score::INT AS away_team_score,
  home_team_score::INT AS home_team_score,
  CASE WHEN home_team_score::INT > away_team_score::INT
    THEN True
    ELSE False END AS home_team_is_winner,
  CASE WHEN home_team_score::INT = away_team_score::INT
    THEN True
    ELSE False END AS is_tie,
  CASE WHEN day_night = 'N'
    THEN True
    ELSE False END as night_game,
  park_id,
  time_of_game_minutes::INT
FROM raw.historical_baseball;
