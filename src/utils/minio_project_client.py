import os
from typing import Tuple
from minio import Minio
from dotenv import load_dotenv

load_dotenv()

def minio_client_setup() -> Tuple[Minio, str]:
  """
  Returns:
    Tuple[Minio, str]: A Minio client and the MINIO_BUCKET_NAME, as defined by parameters in .env
  """

  MINIO_URL = os.getenv("MINIO_URL")
  MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY")
  MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY")

  MINIO_BUCKET_NAME = os.getenv("MINIO_BUCKET_NAME")

  return (Minio(
      MINIO_URL,
      access_key=MINIO_ACCESS_KEY,
      secret_key=MINIO_SECRET_KEY,
      secure=False
    ), MINIO_BUCKET_NAME)
