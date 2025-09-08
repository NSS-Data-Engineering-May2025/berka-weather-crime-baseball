import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

MINIO_BUCKET_NAME = os.getenv("MINIO_BUCKET_NAME")

def get_latest_minio_records_by_timestamp(minio_client, prefix) -> list[str]:
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
