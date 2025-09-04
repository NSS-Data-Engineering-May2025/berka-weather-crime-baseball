import os
import sys
from dotenv import load_dotenv
from sqlmesh import model
import polars as pl
from minio import Minio

current_path = os.path.dirname(os.path.abspath(__file__))
parent_path = os.path.abspath(os.path.join(current_path, "..", ".."))
sys.path.append(parent_path)
from utils.minio_utils import get_latest_minio_records_by_timestamp

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

# @model(
#   name="raw.historical_baseball",
#   kind="FULL",
#   columns={
#     'game_date': 'str',
#     'game_number': 'str',
#     'day_of_week': 'str',
#     'visiting_team': 'str',
#     'visiting_league': 'str',
#     'visiting_team_game_number': 'str',
#     'home_team': 'str',
#     'home_league': 'str',
#     'home_team_game_number': 'str',
#     'visiting_team_score': 'str',
#     'home_team_score': 'str',
#     'number_of_outs': 'str',
#     'day_night': 'str',
#     'completion_info': 'str',
#     'forfeit_info': 'str',
#     'protest_info': 'str',
#     'park_id': 'str',
#     'attendance': 'str',
#     'time_of_game_minutes': 'str',
#     'visiting_team_line': 'str',
#     'home_team_line': 'str',
#     'visiting_ab': 'str',
#     'visiting_hit': 'str',
#     'visiting_2b': 'str',
#     'visiting_3b': 'str',
#     'visiting_hr': 'str',
#     'visiting_rbi': 'str',
#     'visiting_sac_hit': 'str',
#     'visiting_sac_fly': 'str',
#     'visiting_hbp': 'str',
#     'visiting_bb': 'str',
#     'visiting_ibb': 'str',
#     'visiting_k': 'str',
#     'visiting_sb': 'str',
#     'visiting_cs': 'str',
#     'visiting_gidp': 'str',
#     'visiting_catcher_interference': 'str',
#     'visiting_lob': 'str',
#     'visiting_pitchers_used': 'str',
#     'visiting_individual_earned_runs': 'str',
#     'visiting_team_earned_runs': 'str',
#     'visiting_wild_pitches': 'str',
#     'visiting_balks': 'str',
#     'visiting_putouts': 'str',
#     'visiting_assists': 'str',
#     'visiting_errors': 'str',
#     'visiting_passed_balls': 'str',
#     'visiting_double_plays': 'str',
#     'visiting_triple_plays': 'str',
#     'home_ab': 'str',
#     'home_hit': 'str',
#     'home_2b': 'str',
#     'home_3b': 'str',
#     'home_hr': 'str',
#     'home_rbi': 'str',
#     'home_sac_hit': 'str',
#     'home_sac_fly': 'str',
#     'home_hbp': 'str',
#     'home_bb': 'str',
#     'home_ibb': 'str',
#     'home_k': 'str',
#     'home_sb': 'str',
#     'home_cs': 'str',
#     'home_gidp': 'str',
#     'home_catcher_interference': 'str',
#     'home_lob': 'str',
#     'home_pitchers_used': 'str',
#     'home_individual_earned_runs': 'str',
#     'home_team_earned_runs': 'str',
#     'home_wild_pitches': 'str',
#     'home_balks': 'str',
#     'home_putouts': 'str',
#     'home_assists': 'str',
#     'home_errors': 'str',
#     'home_passed_balls': 'str',
#     'home_double_plays': 'str',
#     'home_triple_plays': 'str',
#     'home_plate_umpire_id': 'str',
#     'home_plate_umpire_name': 'str',
#     '1b_umpire_id': 'str',
#     '1b_umpire_name': 'str',
#     '2b_umpire_id': 'str',
#     '2b_umpire_name': 'str',
#     '3b_umpire_id': 'str',
#     '3b_umpire_name': 'str',
#     'lf_umpire_id': 'str',
#     'lf_umpire_name': 'str',
#     'rf_umpire_id': 'str',
#     'rf_umpire_name': 'str',
#     'visiting_manager_id': 'str',
#     'visiting_manager_name': 'str',
#     'home_manager_id': 'str',
#     'home_manager_name': 'str',
#     'winning_pitcher_id': 'str',
#     'winning_pitcher_name': 'str',
#     'losing_pitcher_id': 'str',
#     'losing_pitcher_name': 'str',
#     'saving_pitcher_id': 'str',
#     'saving_pitcher_name': 'str',
#     'gw_rbi_batter_id': 'str',
#     'gw_rbi_batter_name': 'str',
#     'visiting_starter_id': 'str',
#     'visiting_starter_name': 'str',
#     'home_starter_id': 'str',
#     'home_starter_name': 'str',
#     'visiting_starting_lineup_1_id': 'str',
#     'visiting_starting_lineup_1_name': 'str',
#     'visiting_starting_lineup_1_position': 'str',
#     'visiting_starting_lineup_2_id': 'str',
#     'visiting_starting_lineup_2_name': 'str',
#     'visiting_starting_lineup_2_position': 'str',
#     'visiting_starting_lineup_3_id': 'str',
#     'visiting_starting_lineup_3_name': 'str',
#     'visiting_starting_lineup_3_position': 'str',
#     'visiting_starting_lineup_4_id': 'str',
#     'visiting_starting_lineup_4_name': 'str',
#     'visiting_starting_lineup_4_position': 'str',
#     'visiting_starting_lineup_5_id': 'str',
#     'visiting_starting_lineup_5_name': 'str',
#     'visiting_starting_lineup_5_position': 'str',
#     'visiting_starting_lineup_6_id': 'str',
#     'visiting_starting_lineup_6_name': 'str',
#     'visiting_starting_lineup_6_position': 'str',
#     'visiting_starting_lineup_7_id': 'str',
#     'visiting_starting_lineup_7_name': 'str',
#     'visiting_starting_lineup_7_position': 'str',
#     'visiting_starting_lineup_8_id': 'str',
#     'visiting_starting_lineup_8_name': 'str',
#     'visiting_starting_lineup_8_position': 'str',
#     'visiting_starting_lineup_9_id': 'str',
#     'visiting_starting_lineup_9_name': 'str',
#     'visiting_starting_lineup_9_position': 'str',
#     'home_starting_lineup_1_id': 'str',
#     'home_starting_lineup_1_name': 'str',
#     'home_starting_lineup_1_position': 'str',
#     'home_starting_lineup_2_id': 'str',
#     'home_starting_lineup_2_name': 'str',
#     'home_starting_lineup_2_position': 'str',
#     'home_starting_lineup_3_id': 'str',
#     'home_starting_lineup_3_name': 'str',
#     'home_starting_lineup_3_position': 'str',
#     'home_starting_lineup_4_id': 'str',
#     'home_starting_lineup_4_name': 'str',
#     'home_starting_lineup_4_position': 'str',
#     'home_starting_lineup_5_id': 'str',
#     'home_starting_lineup_5_name': 'str',
#     'home_starting_lineup_5_position': 'str',
#     'home_starting_lineup_6_id': 'str',
#     'home_starting_lineup_6_name': 'str',
#     'home_starting_lineup_6_position': 'str',
#     'home_starting_lineup_7_id': 'str',
#     'home_starting_lineup_7_name': 'str',
#     'home_starting_lineup_7_position': 'str',
#     'home_starting_lineup_8_id': 'str',
#     'home_starting_lineup_8_name': 'str',
#     'home_starting_lineup_8_position': 'str',
#     'home_starting_lineup_9_id': 'str',
#     'home_starting_lineup_9_name': 'str',
#     'home_starting_lineup_9_position': 'str',
#     'addl_info': 'str',
#     'data_acquisition_code': 'str',
#   }
# )
def execute():
  files_to_import = get_latest_minio_records_by_timestamp(prefix="baseball/historical/")

  collected_years = []
  for file in files_to_import:
    with minio_client.get_object(MINIO_BUCKET_NAME, file) as response:
      single_year = pl.read_csv(response, infer_schema=False, has_header=False)
      collected_years.append(single_year)

  all_years = pl.concat(collected_years)

  print(len(all_years))

execute()
