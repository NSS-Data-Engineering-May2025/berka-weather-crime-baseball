import os
import io
from dotenv import load_dotenv
import polars as pl
from minio import Minio

metar_schema = {
  'icaoId': 'str',
  'receiptTime': 'str',
  'obsTime': 'int',
  'reportTime': 'datetime',
  'temp': 'float',
  'dewp': 'float',
  'wdir': 'str',
  'wspd': 'int',
  'wgst': 'int',
  'visib': 'str',
  'altim': 'float',
  'slp': 'float',
  'wxString': 'str',
  'presTend': 'float',
  'maxT': 'float',
  'minT': 'float',
  'maxT24': 'float',
  'minT24': 'float',
  'precip': 'float',
  'pcp3hr': 'float',
  'pcp6hr': 'float',
  'pcp24hr': 'float',
  'snow': 'float',
  'vertVis': 'int',
  'metarType': 'str',
  'rawOb': 'str',
  'lat': 'float',
  'lon': 'float',
  'elev': 'int',
  'name': 'str',
  'fltCat': 'str',
}

def get_metar_bronze_table(city: str):
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

  years = [folder.object_name.split("/")[-2]
           for folder
           in minio_client.list_objects(MINIO_BUCKET_NAME, prefix=f"weather/{city}/metar/")]
  
  collected_yearly_metar = []
  for year in years:
    with minio_client.get_object(
      MINIO_BUCKET_NAME,
      f"weather/{city}/metar/{year}/{city}_yearly_metar_{year}.parquet"
      ) as response:
      yearly_metar_report = pl.read_parquet(io.BytesIO(response.read()))
      collected_yearly_metar.append(yearly_metar_report)
  
  all_yearly_metar = pl.concat(collected_yearly_metar)

  return all_yearly_metar.to_pandas()
