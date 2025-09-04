import os
import json
from dotenv import load_dotenv
from sqlmesh import model
import polars as pl
from datetime import datetime
from minio import Minio

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

@model(
  name="raw.philadelphia_crime_report",
  kind="FULL",
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
def execute():
  reports = minio_client.list_objects(MINIO_BUCKET_NAME, prefix="crime/philadelphia/")
  latest = datetime()
  for report in reports:
    name = report.object_name
    *_, stamp = name.split("_")
    stamp_comparator = datetime.strptime(stamp, "%Y-%m-%d")
    if year == "2021" and stamp_comparator > latest:
      latest = stamp_comparator
