import os
import sys
import json
from dotenv import load_dotenv
from sqlmesh import model
from sqlmesh.core.model.kind import ModelKindName
from datetime import datetime, timedelta
import polars as pl
from minio import Minio

current_path = os.path.dirname(os.path.abspath(__file__))
parent_path = os.path.abspath(os.path.join(current_path, "..", ".."))
sys.path.append(parent_path)

@model(
  name="raw.philadelphia_crime_report",
  kind=dict(
    name=ModelKindName.INCREMENTAL_BY_UNIQUE_KEY,
    time_column="dispatch_date"
  ),
  start='2000-01-01',
  gateway="duckdb",
  columns={
    'cartodb_id': 'int',
    'the_geom': 'varchar',
    'the_geom_webmercator': 'varchar',
    'objectid': 'int',
    'dc_dist': 'str',
    'psa': 'str',
    'dispatch_date_time': 'str',
    'dispatch_date': 'datetime',
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

  collected_years = []

  # Collect past records
  for report in minio_client.list_objects(MINIO_BUCKET_NAME, prefix=f"crime/philadelphia/{datetime.now().year}/past/"):
    with minio_client.get_object(MINIO_BUCKET_NAME, report.object_name) as response:
      data = response.read()
      single_year = json.loads(data.decode("utf-8"))["rows"]
      collected_years.append(pl.DataFrame(single_year))

  # Find most recent current year import and collect
  check_day = datetime.now() + timedelta(days=3)
  while check_day.year == datetime.now().year:
    try:
      with minio_client.get_object(MINIO_BUCKET_NAME, f"crime/philadelphia/{check_day.year}/{check_day.strftime("%Y-%m-%d")}/philadelphia_crime_report_{check_day.year}.json") as response:
        data = response.read()
        current_year = json.loads(data.decode("utf-8"))["rows"]
        collected_years.append(pl.DataFrame(current_year))
        break
    except:
      check_day -= timedelta(days=1)
      continue

  all_years = pl.concat(collected_years)

  all_years = all_years.with_columns(
    pl.col("dispatch_date").str.strptime(pl.Date, "%Y-%m-%d")
  )

  filtered_for_incremental = all_years.filter(
    (pl.col("dispatch_date") >= start.replace(tzinfo=None)) & 
    (pl.col("dispatch_date") < end.replace(tzinfo=None))
  )

  if len(filtered_for_incremental) == 0:
    yield from ()
  else:
    yield filtered_for_incremental
