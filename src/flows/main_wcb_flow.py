import os
import sys
from prefect import flow

current_path = os.path.dirname(os.path.abspath(__file__))
parent_path = os.path.abspath(os.path.join(current_path, "..", ".."))
sys.path.append(parent_path)
from src.flows.migration_flow import migration_flow
from src.flows.ingestion_flow import ingestion_flow

@flow(name='main_wcb_flow')
def main_wcb_flow():
  ingestion = ingestion_flow()
  migration_flow(ingestion)

if __name__ == "__main__":
    main_wcb_flow.serve(
    name="main_wcb_flow",
    cron="0 11 * * *"
  )
