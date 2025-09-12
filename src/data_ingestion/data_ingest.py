import os
import io
import sys
import json
import zipfile
import requests
from dotenv import load_dotenv
from minio import Minio
from datetime import datetime, timedelta
from data_consolidation import metar_to_parquet

current_path = os.path.dirname(os.path.abspath(__file__))
parent_path = os.path.abspath(os.path.join(current_path, "..", ".."))
sys.path.append(parent_path)
from src.logger import initialize_logger


load_dotenv()

DETROIT_CRIME_START_YEAR = 2017
DETROIT_CRIME_INGESTION_DELAY = int(os.getenv("DETROIT_CRIME_INGESTION_DELAY"))
DETROIT_CRIME_INGESTION_LIMIT = 2000

PHILADELPHIA_CRIME_START_YEAR = 2006
PHILADELPHIA_CRIME_FULL_IMPORT_DAY = 1

HISTORICAL_BASEBALL_START_YEAR = 2000
HISTORICAL_BASEBALL_INGESTION_MONTH = 1

NCEI_WEATHER_DATASETS=[
  {'station':'USW00014822', 'city':'detroit'},
  {'station':'USW00013739', 'city':'philadelphia'}
]

METAR_WEATHER_STATIONS=[
  {'ids':'KDET', 'city':'detroit'},
  {'ids':'KPHL', 'city':'philadelphia'}
]

MINIO_URL = os.getenv("MINIO_URL")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY")
MINIO_BUCKET_NAME = os.getenv("MINIO_BUCKET_NAME")

logging = initialize_logger()

minio_client = Minio(
    MINIO_URL,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=False
  )

def send_to_minio(data: bytes, filename):
  try:
    if not minio_client.bucket_exists(MINIO_BUCKET_NAME):
      minio_client.make_bucket(MINIO_BUCKET_NAME)
      logging.info(f"Created bucket {MINIO_BUCKET_NAME} in MinIO.")

    minio_client.put_object(
      bucket_name=MINIO_BUCKET_NAME,
      object_name=filename,
      data=io.BytesIO(data),
      length=len(data),
      content_type=f"application/{filename.split(".")[1]}"
    )

    logging.info(f"{filename} saved to MinIO of size {len(data)} bytes")
  except Exception as e:
    raise

# Daily ingestion w/ compilation to yearly parquet file
def import_weather_metar():
  for station in METAR_WEATHER_STATIONS:
    today = datetime.today()
    ingest_day = today - timedelta(days=1)
    try:
      url = f"https://aviationweather.gov/api/data/metar?ids={station["ids"]}&format=json&taf=false&hours=24&date={today.strftime("%Y%m%d")}0000"
      response = requests.get(url)
      response.raise_for_status()

      logging.info(f"API METAR retrieval successful for {station["ids"]} in {station["city"]} for {ingest_day.strftime('%Y-%m-%d')}.")
      
      minio_file_path = f"weather/{station["city"]}/metar/{ingest_day.year}/{station["city"]}_weather_report_metar_{ingest_day.strftime("%Y-%m-%d")}.json"

      logging.info("Saving JSON to MinIO")
      send_to_minio(response.content, minio_file_path)

      logging.info("Appending daily METAR data to yearly parquet")
      consolidated_metar = metar_to_parquet(station["city"], response.json())

      minio_file_path_parquet = f"weather/{station["city"]}/metar/{ingest_day.year}/{station["city"]}_yearly_metar_{ingest_day.year}.parquet"

      send_to_minio(consolidated_metar, minio_file_path_parquet)

    except Exception as e:
      logging.error(f"Error in METAR weather data retrieval for station={station["ids"]}, city={station["city"]}: {e}")

# Daily ingestion, single file with all history
def import_weather_ncei():
  for dataset in NCEI_WEATHER_DATASETS:
    try:
      url = f"https://www.ncei.noaa.gov/access/past-weather/{dataset["station"]}/data.csv"
      response = requests.get(url)
      response.raise_for_status()

      logging.info(f"CSV retrieval successful for {dataset["station"]} in {dataset["city"]}.")
      
      minio_file_path = f"weather/{dataset["city"]}/ncei/{datetime.now().strftime("%Y-%m-%d")}/{dataset["city"]}_weather_report_ncei.csv"

      logging.info("Saving CSV to MinIO")
      send_to_minio(response.content, minio_file_path)

    except Exception as e:
      logging.error(f"Error in NCEI weather data retrieval for station={dataset["station"]}, city={dataset["city"]}: {e}")

# Daily ingestion, 1 file per year
def import_philadelphia_crime():
  import_year = PHILADELPHIA_CRIME_START_YEAR
  if datetime.now().day != PHILADELPHIA_CRIME_FULL_IMPORT_DAY:
    import_year = datetime.now().year
  while import_year <= datetime.now().year:
    logging.info(f"Retrieving Philadelphia crime data for year {import_year}")
    try:
      url = f"https://phl.carto.com/api/v2/sql?q=SELECT * FROM incidents_part1_part2 WHERE dispatch_date LIKE '{import_year}-%25'"
      response = requests.get(url)
      response.raise_for_status()

      annual_crime_data = response.json()
      if annual_crime_data["total_rows"] > 0:
        logging.info(f"API retrieval successful for {import_year}. Rows returned: {annual_crime_data["total_rows"]}")

        minio_file_path = f"crime/philadelphia/{datetime.now().year}/{datetime.now().strftime("%Y-%m-%d")}/philadelphia_crime_report_{import_year}.json"
        if datetime.now().year != import_year:
          minio_file_path = f"crime/philadelphia/{datetime.now().year}/past/philadelphia_crime_report_{import_year}.json"

        logging.info("Saving data as JSON in MinIO")
        send_to_minio(response.content, minio_file_path)
      else:
        logging.info(f"0 results returned for {import_year}")

    except Exception as e:
      logging.error(f"Error in Philadelphia crime data retrieval for year={import_year}: {e}")
    finally:
      import_year += 1

# Daily ingestion of deltas from DETROIT_INGESTION_CRIME_DELAY days prior, also uses manual seed data for historical
def import_detroit_crime():
  import_day = (datetime.today() - timedelta(days=DETROIT_CRIME_INGESTION_DELAY)).strftime("%Y-%m-%d")
  result_offset = 0
  while True:
    logging.info(f"Retrieving Detroit crime data updates for {import_day}")
    try:
      url = f"https://services2.arcgis.com/qvkbeam7Wirps6zC/arcgis/rest/services/RMS_Crime_Incidents/FeatureServer/0/query?where=updated_at%20LIKE%20%27{import_day}%25%27&resultOffset={result_offset}&outFields=*&outSR=4326&f=json"
      response = requests.get(url)
      response.raise_for_status()

      annual_crime_data = response.json()
      if len(annual_crime_data["features"]) > 0:
        logging.info(f"API retrieval successful for {import_day}. Rows returned: {len(annual_crime_data["features"])}")
      
        minio_file_path = f"crime/detroit/{import_day}/detroit_crime_deltas_{result_offset + 1}_to_{result_offset + len(annual_crime_data["features"])}.json"

        logging.info("Saving data as JSON in MinIO")
        send_to_minio(response.content, minio_file_path)
      else:
        break

    except Exception as e:
      logging.error(f"Error in Detroit crime data retrieval for day={import_day}: {e}")
    finally:
      result_offset += DETROIT_CRIME_INGESTION_LIMIT

# Daily ingestion of regular season scores for the year
def import_current_baseball():
  try:
    logging.info(f"Retrieving MLB current season scores.")

    url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&season=2025&gameType=R"
    response = requests.get(url)
    response.raise_for_status()

    score_data = response.json()

    logging.info(f"API retrieval successful. Games returned: {score_data["totalGames"]}")
  
    minio_file_path = f"baseball/current/{datetime.now().strftime("%Y-%m-%d")}/mlb_regular_season_scores_{datetime.now().year}.json"

    logging.info("Saving data as JSON in MinIO")
    send_to_minio(response.content, minio_file_path)
    
  except Exception as e:
    logging.error(f"Error in MLB current season data transfer: {e}")

# Data updated infrequently, only needs ingestion annually
def import_historical_baseball():
  import_year = HISTORICAL_BASEBALL_START_YEAR
  while import_year < datetime.now().year:
    logging.info(f"Retrieving historical baseball data for year={import_year}")
    try:
      url = f"https://www.retrosheet.org/gamelogs/gl{import_year}.zip"
      response = requests.get(url)
      response.raise_for_status()

      with zipfile.ZipFile(io.BytesIO(response.content)) as unzipped:
        for filename in unzipped.namelist():
          logging.info(f"Zip retrieval successful for {filename}")

          with unzipped.open(filename) as gamelogs:
            minio_file_path = f'baseball/historical/gamelogs/mlb_gamelogs_{import_year}.csv'

            logging.info("Saving data as CSV in MinIO")
            send_to_minio(gamelogs.read(), minio_file_path)
    except Exception as e:
      logging.error(f"Error in historical baseball data transfer for year={import_year}: {e}")
    finally:
      import_year += 1

def ingest_from_data_sources():
  import_weather_metar()
  import_weather_ncei()
  import_philadelphia_crime()
  import_detroit_crime()
  import_current_baseball()
  if datetime.now().month == HISTORICAL_BASEBALL_INGESTION_MONTH:
    import_historical_baseball()

if __name__ == "__main__":
  ingest_from_data_sources()
