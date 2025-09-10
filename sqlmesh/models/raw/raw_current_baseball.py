import os
import sys
import json
import polars as pl
from datetime import datetime, timedelta
from minio import Minio
from dotenv import load_dotenv
from sqlmesh import model
from sqlmesh.core.model.kind import ModelKindName

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
    "gamePk": "int",
    "gameGuid": "str",
    "link": "str",
    "gameType": "str",
    "season": "str",
    "gameDate": "str",
    "officialDate": "str",
    "abstractGameState": "str",
    "codedGameState": "str",
    "detailedState": "str",
    "statusCode": "str",
    "startTimeTBD": "bool",
    "abstractGameCode": "str",
    "away_team_id": "int",
    "away_team_name": "str",
    "away_team_score": "int",
    "away_team_isWinner": "bool",
    "away_team_record_wins": "int",
    "away_team_record_losses": "int",
    "away_team_win_pct": "str",
    "home_team_id": "int",
    "home_team_name": "str",
    "home_team_score": "int",
    "home_team_isWinner": "bool",
    "home_team_record_wins": "int",
    "home_team_record_losses": "int",
    "home_team_win_pct": "str",
    "venue_id": "int",
    "venue_name": "str",
    "isTie": "bool",
    "gameNumber": "int",
    "publicFacing": "bool",
    "doubleHeader": "str",
    "gamedayType": "str",
    "tiebreaker": "str",
    "calendarEventID": "str",
    "seasonDisplay": "str",
    "dayNight": "str",
    "description": "str",
    "scheduledInnings": "int",
    "reverseHomeAwayStatus": "bool",
    "inningBreakLength": "int",
    "gamesInSeries": "int",
    "seriesGameNumber": "int",
    "seriesDescription": "str",
    "recordSource": "str",
    "ifNecessary": "str",
    "ifNecessaryDescription": "str"
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
          "gamePk": game.get("gamePk"),
          "gameGuid": game.get("gameGuid"),
          "link": game.get("link"),
          "gameType": game.get("gameType"),
          "season": game.get("season"),
          "gameDate": game.get("gameDate"),
          "officialDate": game.get("officialDate"),
          "abstractGameState": game["status"].get("abstractGameState"),
          "codedGameState": game["status"].get("codedGameState"),
          "detailedState": game["status"].get("detailedState"),
          "statusCode": game["status"].get("statusCode"),
          "startTimeTBD": game["status"].get("startTimeTBD"),
          "abstractGameCode": game["status"].get("abstractGameCode"),
          "away_team_id": game["teams"]["away"]["team"].get("id"),
          "away_team_name": game["teams"]["away"]["team"].get("name"),
          "away_team_score": game["teams"]["away"].get("score"),
          "away_team_isWinner": game["teams"]["away"].get("isWinner"),
          "away_team_record_wins": game["teams"]["away"]["leagueRecord"].get("wins"),
          "away_team_record_losses": game["teams"]["away"]["leagueRecord"].get("losses"),
          "away_team_win_pct": game["teams"]["away"]["leagueRecord"].get("pct"),
          "home_team_id": game["teams"]["home"]["team"].get("id"),
          "home_team_name": game["teams"]["home"]["team"].get("name"),
          "home_team_score": game["teams"]["home"].get("score"),
          "home_team_isWinner": game["teams"]["home"].get("isWinner"),
          "home_team_record_wins": game["teams"]["home"]["leagueRecord"].get("wins"),
          "home_team_record_losses": game["teams"]["home"]["leagueRecord"].get("losses"),
          "home_team_win_pct": game["teams"]["home"]["leagueRecord"].get("pct"),
          "venue_id": game["venue"].get("id"),
          "venue_name": game["venue"].get("name"),
          "isTie": game.get("isTie"),
          "gameNumber": game.get("gameNumber"),
          "publicFacing": game.get("publicFacing"),
          "doubleHeader": game.get("doubleHeader"),
          "gamedayType": game.get("gamedayType"),
          "tiebreaker": game.get("tiebreaker"),
          "calendarEventID": game.get("calendarEventID"),
          "seasonDisplay": game.get("seasonDisplay"),
          "dayNight": game.get("dayNight"),
          "description": game.get("description"),
          "scheduledInnings": game.get("scheduledInnings"),
          "reverseHomeAwayStatus": game.get("reverseHomeAwayStatus"),
          "inningBreakLength": game.get("inningBreakLength"),
          "gamesInSeries": game.get("gamesInSeries"),
          "seriesGameNumber": game.get("seriesGameNumber"),
          "seriesDescription": game.get("seriesDescription"),
          "recordSource": game.get("recordSource"),
          "ifNecessary": game.get("ifNecessary"),
          "ifNecessaryDescription": game.get("ifNecessaryDescription")
        }
        games.append(single_game)
  
  flattened_games = pl.DataFrame(games)

  return flattened_games.to_pandas()
