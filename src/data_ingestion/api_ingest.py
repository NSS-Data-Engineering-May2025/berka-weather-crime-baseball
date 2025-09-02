import os
import sys
import requests
from dotenv import load_dotenv
from minio import Minio
from datetime import datetime

current_path = os.path.dirname(os.path.abspath(__file__))
parent_path = os.path.abspath(os.path.join(current_path, "..", ".."))
sys.path.append(parent_path)
from src.logger import initialize_logger

load_dotenv()

PHILADELPHIA_CRIME_START_YEAR = 2021
PHILADELPHIA_CRIME_END_YEAR = datetime.now().year

logging = initialize_logger()

def import_philadelphia_crime():
  import_year = PHILADELPHIA_CRIME_START_YEAR
  while import_year <= PHILADELPHIA_CRIME_END_YEAR:
    logging.info(f"Retrieving Philadelphia crime data from {import_year}")
    try:
      url = f"https://phl.carto.com/api/v2/sql?q=SELECT * FROM incidents_part1_part2 WHERE dispatch_date LIKE '{import_year}-%25'"
      response = requests.get(url)
      response.raise_for_status()
      crime_data = response.json()
      logging.info(f"API retrieval successful. Rows returned: {crime_data["total_rows"]}")
      import_year += 1
    except Exception as e:
      logging.error(f"Error in data retrieval for year={import_year}: {e}")

import_philadelphia_crime()
