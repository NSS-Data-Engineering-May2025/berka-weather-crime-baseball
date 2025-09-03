import os
import io
import sys
import zipfile
import requests
from dotenv import load_dotenv
from minio import Minio
from datetime import datetime, timedelta

current_path = os.path.dirname(os.path.abspath(__file__))
parent_path = os.path.abspath(os.path.join(current_path, "..", ".."))
sys.path.append(parent_path)
from src.logger import initialize_logger

load_dotenv()

PHILADELPHIA_CRIME_START_YEAR = 2021
PHILADELPHIA_CRIME_END_YEAR = datetime.now().year

IMPORT_DELAY_DAYS = 7

BASEBALL_DAILY_STOP_MONTH = 2

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

def import_philadelphia_crime():
  import_year = PHILADELPHIA_CRIME_START_YEAR
  while import_year <= PHILADELPHIA_CRIME_END_YEAR:
    logging.info(f"Retrieving Philadelphia crime data for year={import_year}")
    try:
      url = f"https://phl.carto.com/api/v2/sql?q=SELECT * FROM incidents_part1_part2 WHERE dispatch_date LIKE '{import_year}-%25'"
      response = requests.get(url)
      response.raise_for_status()

      annual_crime_data = response.json()
      logging.info(f"API retrieval successful. Rows returned: {annual_crime_data["total_rows"]}")

      minio_file_path = f"crime/philadelphia/philadelphia_crime_report_{import_year}_{datetime.now().strftime("%Y-%m-%d")}.json"

      logging.info("Saving data as JSON in MinIO")
      send_to_minio(response.content, minio_file_path)

    except Exception as e:
      logging.error(f"Error in Philadelphia crime data transfer for year={import_year}: {e}")
    finally:
      import_year += 1

def import_daily_baseball():
  import_day = datetime.now() - timedelta(days=IMPORT_DELAY_DAYS)

  DAILY_BASEBALL_PREFIX = f"baseball/daily/{import_day.year}/"

  imported_files = minio_client.list_objects(MINIO_BUCKET_NAME, prefix=DAILY_BASEBALL_PREFIX)
  imported_dates = [file.object_name[-15:-5] for file in imported_files]

  while import_day.month > BASEBALL_DAILY_STOP_MONTH:
    if import_day.strftime("%Y-%m-%d") in imported_dates:
      import_day -= timedelta(days=1)
      continue

    try:
      logging.info(f"Retrieving MLB daily scores for day={import_day.strftime("%Y-%m-%d")}")
      
      url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={import_day.strftime("%Y-%m-%d")}"
      response = requests.get(url)
      response.raise_for_status()
    
      minio_file_path = f"{DAILY_BASEBALL_PREFIX}mlb_scores_{import_day.strftime("%Y-%m-%d")}.json"

      logging.info("Saving data as JSON in MinIO")
      send_to_minio(response.content, minio_file_path)
      
    except Exception as e:
      logging.error(f"Error in MLB daily stats transfer for date={import_day}: {e}")
    finally:
      import_day -= timedelta(days=1)
  

def import_historical_baseball():
  import_year = 2000
  while import_year < datetime.now().year:
    logging.info(f"Retrieving historical baseball data for year={import_year}")
    try:
      url = f"https://www.retrosheet.org/gamelogs/gl{import_year}.zip"
      response = requests.get(url)
      response.raise_for_status()

      with zipfile.ZipFile(io.BytesIO(response.content)) as z:
        for filename in z.namelist():
          logging.info(f"ZIP retrieval successful for {filename}")

          with z.open(filename) as gamelogs:
            minio_file_path = f'baseball/historical/mlb_gamelogs_{import_year}_{datetime.now().strftime("%Y-%m-%d")}.csv'

            logging.info("Saving data as CSV in MinIO")
            send_to_minio(gamelogs.read(), minio_file_path)
    except Exception as e:
      logging.error(f"Error in historical baseball data transfer for year={import_year}: {e}")
    finally:
      import_year += 1

import_daily_baseball()
