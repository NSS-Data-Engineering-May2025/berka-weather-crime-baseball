import os
import sys
import json
import polars as pl
from datetime import datetime, timedelta
from minio import Minio
from dotenv import load_dotenv
from sqlmesh import model
from sqlmesh.core.model.kind import ModelKindName
from sqlglot.expressions import to_column

@model(
  name="raw.current_baseball",
  kind=dict(
    name=ModelKindName.INCREMENTAL_BY_TIME_RANGE,
    time_column="date"
  ),
  gateway="duckdb",
  start='2000-01-01',
  columns={
    "date": "datetime",
    "game_pk": "int",
    "game_guid": "str",
    "link": "str",
    "game_type": "str",
    "season": "str",
    "game_date": "str",
    "official_date": "str",
    "abstract_game_state": "str",
    "coded_game_state": "str",
    "detailed_state": "str",
    "status_code": "str",
    "start_time_tbd": "bool",
    "abstract_game_code": "str",
    "away_team_id": "int",
    "away_team_name": "str",
    "away_team_score": "int",
    "away_team_is_winner": "bool",
    "away_team_record_wins": "int",
    "away_team_record_losses": "int",
    "away_team_win_pct": "str",
    "home_team_id": "int",
    "home_team_name": "str",
    "home_team_score": "int",
    "home_team_is_winner": "bool",
    "home_team_record_wins": "int",
    "home_team_record_losses": "int",
    "home_team_win_pct": "str",
    "venue_id": "int",
    "venue_name": "str",
    "is_tie": "bool",
    "game_number": "int",
    "public_facing": "bool",
    "double_header": "str",
    "gameday_type": "str",
    "tiebreaker": "str",
    "calendar_event_id": "str",
    "season_display": "str",
    "day_night": "str",
    "description": "str",
    "scheduled_innings": "int",
    "reverse_home_away_status": "bool",
    "inning_break_length": "int",
    "games_in_series": "int",
    "series_game_number": "int",
    "series_description": "str",
    "record_source": "str",
    "if_necessary": "str",
    "if_necessary_description": "str"
  }
)
def execute(context, start, end, **kwargs):
  load_dotenv()

  MINIO_URL = os.getenv("MINIO_URL")
  MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY")
  MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY")
  MINIO_BUCKET_NAME = os.getenv("MINIO_BUCKET_NAME")

  minio_client = Minio(
    MINIO_URL,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=False
  )

  # Find most recent current year import and collect
  check_day = datetime.now()
  current_season_stats = None
  while check_day + timedelta(days=30) >= datetime.now() and current_season_stats is None:
    try:
      with minio_client.get_object(MINIO_BUCKET_NAME, f"baseball/current/{check_day.strftime("%Y-%m-%d")}/mlb_regular_season_scores_{check_day.year}.json") as response:
        data = response.read()
        current_season_stats = json.loads(data.decode("utf-8"))["dates"]
        break
    except:
      check_day -= timedelta(days=1)
      continue

  games = []
  if current_season_stats is None:
    raise Exception("Current MLB data is either missing or needs to be updated. Re-ingest and try again")
  
  for date in current_season_stats:
    compare_date = datetime.strptime(date["date"], "%Y-%m-%d")
    if compare_date >= start.replace(tzinfo=None) and compare_date < end.replace(tzinfo=None):
      for game in date.get("games"):
        single_game = {
          "date": compare_date,
          "game_pk": game.get("gamePk"),
          "game_guid": game.get("gameGuid"),
          "link": game.get("link"),
          "game_type": game.get("gameType"),
          "season": game.get("season"),
          "game_date": game.get("gameDate"),
          "official_date": game.get("officialDate"),
          "abstract_game_state": game["status"].get("abstractGameState"),
          "coded_game_state": game["status"].get("codedGameState"),
          "detailed_state": game["status"].get("detailedState"),
          "status_code": game["status"].get("statusCode"),
          "start_time_tbd": game["status"].get("startTimeTBD"),
          "abstract_game_code": game["status"].get("abstractGameCode"),
          "away_team_id": game["teams"]["away"]["team"].get("id"),
          "away_team_name": game["teams"]["away"]["team"].get("name"),
          "away_team_score": game["teams"]["away"].get("score"),
          "away_team_is_winner": game["teams"]["away"].get("isWinner"),
          "away_team_record_wins": game["teams"]["away"]["leagueRecord"].get("wins"),
          "away_team_record_losses": game["teams"]["away"]["leagueRecord"].get("losses"),
          "away_team_win_pct": game["teams"]["away"]["leagueRecord"].get("pct"),
          "home_team_id": game["teams"]["home"]["team"].get("id"),
          "home_team_name": game["teams"]["home"]["team"].get("name"),
          "home_team_score": game["teams"]["home"].get("score"),
          "home_team_is_winner": game["teams"]["home"].get("isWinner"),
          "home_team_record_wins": game["teams"]["home"]["leagueRecord"].get("wins"),
          "home_team_record_losses": game["teams"]["home"]["leagueRecord"].get("losses"),
          "home_team_win_pct": game["teams"]["home"]["leagueRecord"].get("pct"),
          "venue_id": game["venue"].get("id"),
          "venue_name": game["venue"].get("name"),
          "is_tie": game.get("isTie"),
          "game_number": game.get("gameNumber"),
          "public_facing": game.get("publicFacing"),
          "double_header": game.get("doubleHeader"),
          "gameday_type": game.get("gamedayType"),
          "tiebreaker": game.get("tiebreaker"),
          "calendar_event_id": game.get("calendarEventID"),
          "season_display": game.get("seasonDisplay"),
          "day_night": game.get("dayNight"),
          "description": game.get("description"),
          "scheduled_innings": game.get("scheduledInnings"),
          "reverse_home_away_status": game.get("reverseHomeAwayStatus"),
          "inning_break_length": game.get("inningBreakLength"),
          "games_in_series": game.get("gamesInSeries"),
          "series_game_number": game.get("seriesGameNumber"),
          "series_description": game.get("seriesDescription"),
          "record_source": game.get("recordSource"),
          "if_necessary": game.get("ifNecessary"),
          "if_necessary_description": game.get("ifNecessaryDescription")
        }
        games.append(single_game)
  
  flattened_games = pl.DataFrame(games)

  return flattened_games.to_pandas()
