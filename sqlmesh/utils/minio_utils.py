import os
from dotenv import load_dotenv
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

def get_latest_minio_records_by_timestamp(prefix) -> list[str]:
  records = minio_client.list_objects(MINIO_BUCKET_NAME, prefix=prefix)
  record_names = [record.object_name for record in records if not record.object_name.endswith("/")]
  latest = datetime.min

  for name in record_names:
    try:
      *_, stamp_with_ext = name.split("_")
      stamp, ext = stamp_with_ext.split(".")
      stamp_comparator = datetime.strptime(stamp, "%Y-%m-%d")
      if stamp_comparator > latest:
        latest = stamp_comparator
    except:
      continue

  import_records = [record for record in record_names if latest.strftime("%Y-%m-%d") in record]

  return import_records
