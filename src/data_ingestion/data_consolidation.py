import os
import io
import sys
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
    wdir: int = None,
    wspd: int = None,
    wgst: int = None,
    visib: float = None,
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

def metar_to_parquet(city: str, ingested_metar: list[dict]) -> bytes:
  ingest_year = (datetime.now() - timedelta(days=1)).year
  logging = initialize_logger(logger_name='consolidation_log')
  logging.info(f"Consolidating {city} METAR data to yearly parquet")

  daily_metar = [MetarObservation(**observation).to_dict() for observation in ingested_metar]
  daily_metar_concat = pl.DataFrame(daily_metar)

  daily_metar_concat = daily_metar_concat.with_columns(pl.col("reportTime").str.strptime(pl.Datetime, "%Y-%m-%dT%H:%M:%S%.3fZ"))

  reporting_start = daily_metar_concat["reportTime"].min()

  existing_metar = b''
  try:
    logging.info(f"Retrieving {city} yearly METAR parquet")
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

  # records = minio_client.list_objects(MINIO_BUCKET_NAME, prefix=f"weather/{city}/metar/")
  # record_names = [record.object_name for record in records if not record.object_name.endswith("/")]
  # latest = datetime.min

  # for name in record_names:
  #   try:
  #     *_, stamp_with_ext = name.split("_")
  #     stamp, ext = stamp_with_ext.split(".")
  #     stamp_comparator = datetime.strptime(stamp, "%Y-%m-%d")
  #     if stamp_comparator > latest:
  #       latest = stamp_comparator
  #   except:
  #     continue

# metar_to_parquet(city="TEST")
