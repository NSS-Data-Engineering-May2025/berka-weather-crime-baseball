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

@model(
  name="raw.philadelphia_crime_report",
  kind="FULL",
  gateway="duckdb",
  columns={
    'cartodb_id': 'int',
    'the_geom': 'varchar',
    'the_geom_webmercator': 'varchar',
    'objectid': 'int',
    'dc_dist': 'str',
    'psa': 'str',
    'dispatch_date_time': 'str',
    'dispatch_date': 'str',
    'dispatch_time': 'str',
    'hour': 'int',
    'dc_key': 'numeric',
    'location_block': 'str',
    'ucr_general': 'str',
    'text_general_code': 'str',
    'point_x': 'float',
    'point_y': 'float'
  }
)
def execute(context, **kwargs):
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

  files_to_import = get_latest_minio_records_by_timestamp(minio_client=minio_client, prefix="crime/philadelphia/")

  collected_years = []
  for file in files_to_import:
    with minio_client.get_object(MINIO_BUCKET_NAME, file) as response:
      single_year = response.json()["rows"]
      collected_years.append(pl.DataFrame(single_year))

  all_years = pl.concat(collected_years)

  all_years = all_years.with_columns(
    pl.col("dispatch_date").str.strptime(pl.Date, "%Y-%m-%d")
  )

  return all_years.to_pandas()
