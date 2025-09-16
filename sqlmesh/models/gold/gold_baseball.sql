MODEL (
  name gold.baseball,
  kind FULL,
  gateway duckdb
);

WITH
    hist_team_games AS (
        SELECT
            game_date,
            season,
            historical_game_id as game_id,
            CONCAT(city, ' ', nickname) AS team,
            CASE
                WHEN hist.is_tie THEN 'tie'
                WHEN hist.away_team_score = hist.home_team_score AND NOT hist.is_tie THEN null
                WHEN hist.home_team = teams.team AND hist.home_team_is_winner
                THEN 'win'
                WHEN hist.away_team = teams.team AND NOT hist.home_team_is_winner
                THEN 'win'
                ELSE 'loss' END AS outcome,
            CASE
                WHEN teams.team = hist.home_team THEN home_team_game_number
                ELSE away_team_game_number END AS game_number,
            CASE
                WHEN teams.team = hist.home_team THEN home_team_score
                ELSE away_team_score END AS score,
            CASE
                WHEN teams.team = hist.home_team THEN True
                ELSE False END AS home_team,
            night_game,
            time_of_game_minutes
        FROM stg.historical_baseball_teams teams
        INNER JOIN stg.historical_baseball hist
        ON teams.team = hist.home_team OR teams.team = hist.away_team
    ),
    curr_team_games AS (
        SELECT
            game_date,
            season,
            game_id,
            team,
            score,
            home_team,
            outcome,
            ROW_NUMBER()
                OVER(PARTITION BY team, season
                ORDER BY game_date, series_game_number) AS game_number,
            current_record_wins,
            current_record_losses,
            night_game
        FROM (
            SELECT
                game_date,
                game_id,
                season,
                away_team_name as team,
                away_team_score as score,
                False as home_team,
                away_team_record_wins AS current_record_wins,
                away_team_record_losses AS current_record_losses,
                series_game_number,
                CASE
                    WHEN is_tie THEN 'tie'
                    WHEN away_team_score = home_team_score AND NOT is_tie THEN null
                    WHEN home_team_is_winner
                    THEN 'loss'
                    ELSE 'win' END AS outcome,
                night_game
            FROM stg.current_baseball
            UNION
            SELECT
                game_date,
                game_id,
                season,
                home_team_name as team,
                home_team_score as score,
                True as home_team,
                home_team_record_wins AS current_record_wins,
                home_team_record_losses AS current_record_losses,
                series_game_number,
                CASE
                    WHEN is_tie THEN 'tie'
                    WHEN away_team_score = home_team_score AND NOT is_tie THEN null
                    WHEN home_team_is_winner
                    THEN 'loss'
                    ELSE 'win' END AS outcome,
                night_game
            FROM stg.current_baseball) as teams
    ),
    comb_team_games AS (
        SELECT
            COALESCE(curr.game_date, hist.game_date) AS game_date,
            COALESCE(curr.game_id::VARCHAR, hist.game_id) AS game_id,
            COALESCE(curr.season, hist.season) AS season,
            COALESCE(curr.team, hist.team) AS team,
            COALESCE(curr.score, hist.score) AS score,
            COALESCE(curr.home_team, hist.home_team) AS home_team,
            COALESCE(curr.outcome, hist.outcome) AS outcome,
            COALESCE(curr.game_number, hist.game_number) AS game_number,
            curr.current_record_wins,
            curr.current_record_losses,
            COALESCE(curr.night_game, hist.night_game) AS night_game,
            hist.time_of_game_minutes
        FROM hist_team_games hist
        FULL JOIN curr_team_games curr
        ON curr.game_date = hist.game_date AND curr.team = hist.team AND curr.game_number = hist.game_number
    ),
    team_games_with_streak_group AS (
        SELECT
            *,
            outcome || game_number - ROW_NUMBER() OVER(PARTITION BY season, team, outcome ORDER BY game_number) as streak_group
        FROM comb_team_games
    ),
    team_games_with_records AS (
        SELECT
            game_date,
            game_id,
            season,
            team,
            score,
            home_team,
            outcome,
            CASE WHEN outcome = 'win'
                THEN COUNT(game_number)
                        OVER(PARTITION BY season, team, streak_group
                        ORDER BY game_number
                        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)
                ELSE -1 * COUNT(game_number)
                        OVER(PARTITION BY season, team, streak_group
                        ORDER BY game_number
                        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)
                END AS current_streak,
            game_number,
            COALESCE(current_record_wins,
                     COUNT(team)
                        FILTER(WHERE outcome = 'win')
                            OVER(PARTITION BY season, team
                            ORDER BY game_number
                            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)
            ) AS current_record_wins,
            COALESCE(current_record_losses,
                     COUNT(team)
                     FILTER(WHERE outcome = 'loss')
                     OVER(PARTITION BY season, team ORDER BY game_number
                            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)
            ) AS current_record_losses,
            ROUND(AVG(CASE WHEN outcome = 'win' THEN 1 ELSE 0 END)
                OVER(PARTITION BY season, team
                    ORDER BY game_number
                    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW), 3) AS current_win_pct,
            ROUND(AVG(CASE WHEN outcome = 'win' THEN 1 ELSE 0 END)
                OVER(PARTITION BY season, team
                    ORDER BY game_number
                    ROWS BETWEEN 9 PRECEDING AND CURRENT ROW), 3) AS last_10_win_pct,
            ROUND(AVG(CASE WHEN outcome = 'win' THEN 1 ELSE 0 END)
                OVER(PARTITION BY season, team
                    ORDER BY game_number
                    ROWS BETWEEN 39 PRECEDING AND CURRENT ROW), 3) AS last_40_win_pct,
            night_game,
            time_of_game_minutes
        FROM team_games_with_streak_group
    )
SELECT
    home.game_date,
    home.game_id,
    home.season,
    home.team as home_team,
    home.score as home_team_score,
    home.outcome as home_team_outcome,
    home.current_streak as home_team_current_streak,
    home.game_number as home_team_game_number,
    home.current_record_wins as home_team_current_record_wins,
    home.current_record_losses as home_team_current_record_losses,
    home.current_win_pct as home_team_current_win_pct,
    home.last_10_win_pct as home_team_last_10_win_pct,
    home.last_40_win_pct as home_team_last_40_win_pct,
    away.team as away_team,
    away.score as away_team_score,
    away.outcome as away_team_outcome,
    away.current_streak as away_team_current_streak,
    away.game_number as away_team_game_number,
    away.current_record_wins as away_team_current_record_wins,
    away.current_record_losses as away_team_current_record_losses,
    away.current_win_pct as away_team_current_win_pct,
    away.last_10_win_pct as away_team_last_10_win_pct,
    away.last_40_win_pct as away_team_last_40_win_pct,
    home.night_game,
    home.time_of_game_minutes
FROM
(SELECT * FROM team_games_with_records WHERE home_team) home
INNER JOIN (SELECT * FROM team_games_with_records WHERE NOT home_team) away
ON home.game_date = away.game_date AND home.game_id = away.game_id;
