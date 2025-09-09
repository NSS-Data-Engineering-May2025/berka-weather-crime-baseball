import os
import io
import sys
import logging
import polars as pl
from dotenv import load_dotenv
from minio import Minio
from datetime import datetime, timedelta

current_path = os.path.dirname(os.path.abspath(__file__))
parent_path = os.path.abspath(os.path.join(current_path, "..", ".."))
sys.path.append(parent_path)
from src.logger import initialize_logger

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

class MetarObservation:
  def __init__(
    self,
    icaoId: str = None,
    receiptTime: str = None,
    obsTime: int = None,
    reportTime: str = None,
    temp: float = None,
    dewp: float = None,
    wdir: str = None,
    wspd: int = None,
    wgst: int = None,
    visib: str = None,
    altim: float = None,
    slp: float = None,
    wxString: str = None,
    presTend: float = None,
    maxT: float = None,
    minT: float = None,
    maxT24: float = None,
    minT24: float = None,
    precip: float = None,
    pcp3hr: float = None,
    pcp6hr: float = None,
    pcp24hr: float = None,
    snow: float = None,
    vertVis: int = None,
    metarType: str = None,
    rawOb: str = None,
    lat: float = None,
    lon: float = None,
    elev: int = None,
    name: str = None,
    fltCat: str = None,
    **kwargs
  ):
    self.icaoId = icaoId
    self.receiptTime = receiptTime
    self.obsTime = obsTime
    self.reportTime = reportTime
    self.temp = temp
    self.dewp = dewp
    self.wdir = wdir
    self.wspd = wspd
    self.wgst = wgst
    self.visib = visib
    self.altim = altim
    self.slp = slp
    self.wxString = wxString
    self.presTend = presTend
    self.maxT = maxT
    self.minT = minT
    self.maxT24 = maxT24
    self.minT24 = minT24
    self.precip = precip
    self.pcp3hr = pcp3hr
    self.pcp6hr = pcp6hr
    self.pcp24hr = pcp24hr
    self.snow = snow
    self.vertVis = vertVis
    self.metarType = metarType
    self.rawOb = rawOb
    self.lat = lat
    self.lon = lon
    self.elev = elev
    self.name = name
    self.fltCat = fltCat

  def to_dict(self):
    return {
      "icaoId": self.icaoId,
      "receiptTime": self.receiptTime,
      "obsTime": self.obsTime,
      "reportTime": self.reportTime,
      "temp": self.temp,
      "dewp": self.dewp,
      "wdir": self.wdir,
      "wspd": self.wspd,
      "wgst": self.wgst,
      "visib": self.visib,
      "altim": self.altim,
      "slp": self.slp,
      "wxString": self.wxString,
      "presTend": self.presTend,
      "maxT": self.maxT,
      "minT": self.minT,
      "maxT24": self.maxT24,
      "minT24": self.minT24,
      "precip": self.precip,
      "pcp3hr": self.pcp3hr,
      "pcp6hr": self.pcp6hr,
      "pcp24hr": self.pcp24hr,
      "snow": self.snow,
      "vertVis": self.vertVis,
      "metarType": self.metarType,
      "rawOb": self.rawOb,
      "lat": self.lat,
      "lon": self.lon,
      "elev": self.elev,
      "name": self.name,
      "fltCat": self.fltCat
    }

def metar_to_parquet(
    city: str,
    ingested_metar: list[dict],
    ingest_day = datetime.now() - timedelta(days=1),
    existing_metar = b''
  ) -> bytes:
  ingest_year = ingest_day.year

  consolidation_logging = logging.getLogger('consolidation_log')
  if not consolidation_logging.hasHandlers():
    consolidation_logging = initialize_logger(log_destination='data_consolidation.log', logger_name='consolidation_log')
  consolidation_logging.info(f"Consolidating {city} {ingest_day.strftime("%Y-%m-%d")} METAR data into yearly parquet")

  daily_metar = [MetarObservation(**observation).to_dict() for observation in ingested_metar]
  daily_metar_concat = pl.DataFrame(daily_metar)

  daily_metar_concat = daily_metar_concat.with_columns([
    pl.col("icaoId").cast(pl.Utf8),
    pl.col("receiptTime").cast(pl.Utf8),
    pl.col("obsTime").cast(pl.Int64),
    pl.col("reportTime").str.strptime(pl.Datetime, "%Y-%m-%dT%H:%M:%S%.3fZ"),
    pl.col("temp").cast(pl.Float64),
    pl.col("dewp").cast(pl.Float64),
    pl.col("wdir").cast(pl.Utf8),
    pl.col("wspd").cast(pl.Int64),
    pl.col("wgst").cast(pl.Int64),
    pl.col("visib").cast(pl.Utf8),
    pl.col("altim").cast(pl.Float64),
    pl.col("slp").cast(pl.Float64),
    pl.col("wxString").cast(pl.Utf8),
    pl.col("presTend").cast(pl.Float64),
    pl.col("maxT").cast(pl.Float64),
    pl.col("minT").cast(pl.Float64),
    pl.col("maxT24").cast(pl.Float64),
    pl.col("minT24").cast(pl.Float64),
    pl.col("precip").cast(pl.Float64),
    pl.col("pcp3hr").cast(pl.Float64),
    pl.col("pcp6hr").cast(pl.Float64),
    pl.col("pcp24hr").cast(pl.Float64),
    pl.col("snow").cast(pl.Float64),
    pl.col("vertVis").cast(pl.Int64),
    pl.col("metarType").cast(pl.Utf8),
    pl.col("rawOb").cast(pl.Utf8),
    pl.col("lat").cast(pl.Float64),
    pl.col("lon").cast(pl.Float64),
    pl.col("elev").cast(pl.Int64),
    pl.col("name").cast(pl.Utf8),
    pl.col("fltCat").cast(pl.Utf8)
  ])

  reporting_start = daily_metar_concat["reportTime"].min()

  try:
    if not existing_metar:
      consolidation_logging.info(f"Retrieving {city} yearly METAR parquet")
      with minio_client.get_object(MINIO_BUCKET_NAME, object_name=f"weather/{city}/metar/{ingest_year}/{city}_yearly_metar_{ingest_year}.parquet") as response:
        existing_metar = response.read()
    existing_metar_concat = pl.read_parquet(io.BytesIO(existing_metar))

    existing_metar_concat_filtered = existing_metar_concat.filter(pl.col("reportTime") < reporting_start)

    full_metar = pl.concat([daily_metar_concat, existing_metar_concat_filtered])
  except Exception as e:
    if existing_metar:
      raise e
    else:
      full_metar = daily_metar_concat

  metar_buffer = io.BytesIO()
  full_metar.write_parquet(metar_buffer)

  return metar_buffer.getvalue()

def recompile_metar_parquet_for_year(year: int, city: str):
  consolidation_logger = initialize_logger(log_destination='data_consolidation.log', logger_name='consolidation_log')
  consolidation_logger.info(f"Recompiling METAR parquet for {city} {year}")
  compiled_parquet_file_name = f"weather/{city}/metar/{year}/{city}_yearly_metar_{year}.parquet"
  try:
    minio_client.remove_object(
      MINIO_BUCKET_NAME,
      compiled_parquet_file_name
    )
  except Exception as e:
    consolidation_logger.info("No existing parquet found")
  try:
    yearly_records = minio_client.list_objects(MINIO_BUCKET_NAME, prefix=f"weather/{city}/metar/{year}/")
    record_list = [record.object_name for record in yearly_records]

    check_day = datetime(year, 1, 1)
    compiled_metar = None
    while check_day.year == year:
      check_file = f"weather/{city}/metar/{year}/{city}_weather_report_metar_{check_day.strftime("%Y-%m-%d")}.json"
      if check_file in record_list:
        with minio_client.get_object(MINIO_BUCKET_NAME, object_name=check_file) as response:
          daily_metar = response.json()
        compiled_metar = metar_to_parquet(city, daily_metar, ingest_day=check_day, existing_metar=compiled_metar)
      check_day += timedelta(days=1)
    
    if compiled_metar:
      consolidation_logger.info(f"{year} {city} METAR collected as parquet. Writing to MinIO")
      minio_client.put_object(
        bucket_name=MINIO_BUCKET_NAME,
        object_name=compiled_parquet_file_name,
        data=io.BytesIO(compiled_metar),
        length=len(compiled_metar),
        content_type=f"application/parquet"
      )
      consolidation_logger.info(f"Recompiled METAR successfully written to MinIO at {compiled_parquet_file_name}")
  except Exception as e:
    consolidation_logger.info(f"Error occurred in recompilation of {city} {year} parquet: {e}")
    raise

if __name__ == "__main__":
  recompile_metar_parquet_for_year(2025, "detroit")
