MODEL (
  name stg.current_baseball,
  kind INCREMENTAL_BY_TIME_RANGE(
    time_column "game_date"
  ),
  gateway duckdb
);

SELECT
  "date" as game_date,
  game_pk as game_id,
  away_team_name,
  away_team_score,
  away_team_record_wins,
  away_team_record_losses,
  home_team_name,
  home_team_score,
  home_team_record_wins,
  home_team_record_losses,
  home_team_is_winner,
  CASE WHEN day_night = 'night'
    THEN True
    ELSE False END as night_game,
  is_tie
FROM raw.current_baseball
WHERE coded_game_state == 'F';
