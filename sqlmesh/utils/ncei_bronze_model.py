import os
import io
from dotenv import load_dotenv
import polars as pl
from datetime import datetime, timedelta
from minio import Minio

ncei_schema = {
  'Date': 'str',
  'TAVG (Degrees Fahrenheit)': 'str',
  'TMAX (Degrees Fahrenheit)': 'str',
  'TMIN (Degrees Fahrenheit)': 'str',
  'PRCP (Inches)': 'str',
  'SNOW (Inches)': 'str',
  'SNWD (Inches)': 'str'
}

def get_ncei_bronze_table(city: str):
  load_dotenv()

  NCEI_EXPIRY_SPAN = 30

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

  check_day = datetime.now() + timedelta(days=1)
  ncei_report = None

  while check_day > (datetime.now() - timedelta(days=NCEI_EXPIRY_SPAN)) and ncei_report is None:
    try:
      with minio_client.get_object(
      MINIO_BUCKET_NAME,
      f"weather/{city}/ncei/{check_day.strftime("%Y-%m-%d")}/{city}_weather_report_ncei.csv"
      ) as response:
        ncei_report = pl.read_csv(io.BytesIO(response.read()),skip_rows=1,has_header=True)
    except Exception as e:
      continue
    finally:
      check_day -= timedelta(days=1)
  
  if ncei_report is None:
    raise Exception("NCEI data is either missing or needs to be updated. Re-ingest and try again")
  
  ncei_report = ncei_report.with_columns([
    pl.col('Date').cast(pl.Utf8),
    pl.col('TAVG (Degrees Fahrenheit)').cast(pl.Utf8),
    pl.col('TMAX (Degrees Fahrenheit)').cast(pl.Utf8),
    pl.col('TMIN (Degrees Fahrenheit)').cast(pl.Utf8),
    pl.col('PRCP (Inches)').cast(pl.Utf8),
    pl.col('SNOW (Inches)').cast(pl.Utf8),
    pl.col('SNWD (Inches)').cast(pl.Utf8)
  ])

  return ncei_report.to_pandas()
