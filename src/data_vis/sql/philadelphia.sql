WITH philly_ball AS (
    SELECT
        game_date,
        game_id,
        season,
        CASE
            WHEN home_team = 'Philadelphia Phillies' THEN home_team
            ELSE away_team
            END AS team,
        CASE
            WHEN home_team = 'Philadelphia Phillies' THEN True
            WHEN away_team = 'Philadelphia Phillies' THEN False
            END AS home_game,
        CASE
            WHEN home_team = 'Philadelphia Phillies' THEN home_team_score
            ELSE away_team_score
            END AS team_score,
        CASE
            WHEN home_team = 'Philadelphia Phillies' THEN home_team_outcome
            ELSE away_team_outcome
            END AS team_outcome,
        CASE
            WHEN home_team = 'Philadelphia Phillies' THEN home_team_current_streak
            ELSE away_team_current_streak
            END AS team_current_streak,
        CASE
            WHEN home_team = 'Philadelphia Phillies' THEN home_team_game_number
            ELSE away_team_game_number
            END AS team_game_number,
        CASE
            WHEN home_team = 'Philadelphia Phillies' THEN home_team_current_record_wins
            ELSE away_team_current_record_wins
            END AS team_current_record_wins,
        CASE
            WHEN home_team = 'Philadelphia Phillies' THEN home_team_current_record_losses
            ELSE away_team_current_record_losses
            END AS team_current_record_losses,
        CASE
            WHEN home_team = 'Philadelphia Phillies' THEN home_team_current_win_pct
            ELSE away_team_current_win_pct
            END AS team_current_win_pct,
        CASE
            WHEN home_team = 'Philadelphia Phillies' THEN home_team_last_10_win_pct
            ELSE away_team_last_10_win_pct
            END AS team_last_10_win_pct,
        CASE
            WHEN home_team = 'Philadelphia Phillies' THEN home_team_last_40_win_pct
            ELSE away_team_last_40_win_pct
            END AS team_last_40_win_pct,
      night_game,
      time_of_game_minutes
    FROM gold.baseball
    WHERE home_team = 'Philadelphia Phillies' OR away_team = 'Philadelphia Phillies'
)
SELECT
    COALESCE(crime.dispatch_date, weather.report_date, baseball.game_date) AS entry_date,
    *,
    ROUND(AVG(weather.max_temp_deg_f) OVER (
      PARTITION BY EXTRACT(month from weather.report_date), EXTRACT(day from weather.report_date)), 2)
      AS avg_max_temp_deg_f,
    ROUND(AVG(weather.min_temp_deg_f) OVER (
      PARTITION BY EXTRACT(month from weather.report_date), EXTRACT(day from weather.report_date)), 2)
      AS avg_min_temp_deg_f,
    CASE
        WHEN team_game_number IS NULL
            THEN MAX(team_current_record_wins) OVER (ORDER BY entry_date ROWS BETWEEN 9 PRECEDING AND CURRENT ROW)
        ELSE team_current_record_wins END AS team_current_record_wins_lag,
    CASE
        WHEN team_game_number IS NULL
            THEN MAX(team_current_record_losses) OVER (ORDER BY entry_date ROWS BETWEEN 9 PRECEDING AND CURRENT ROW)
        ELSE team_current_record_losses END AS team_current_record_losses_lag
FROM gold.philadelphia_crime crime
FULL OUTER JOIN gold.philadelphia_weather weather
ON crime.dispatch_date = weather.report_date
FULL OUTER JOIN philly_ball baseball
ON crime.dispatch_date = baseball.game_date OR weather.report_date = baseball.game_date
ORDER BY entry_date;
