import os
import sys
from prefect import flow, task
from datetime import datetime
import time

current_path = os.path.dirname(os.path.abspath(__file__))
parent_path = os.path.abspath(os.path.join(current_path, "..", ".."))
sys.path.append(parent_path)
from src.logger import initialize_logger
import src.data_ingestion.data_ingest as data

HISTORICAL_BASEBALL_INGESTION_MONTH = 2

@task(retries=3, retry_delay_seconds=10)
def task_ingest_ncei(log):
  log.info('Executing task_ingest_ncei')
  start_time = time.time()
  try:
    data.ingest_weather_ncei()
  except Exception as e:
    log.error('ERROR in task_ingest_ncei')
    raise e
  end_time = time.time()
  elapsed = end_time - start_time
  log.info(f'task_ingest_ncei completed in {elapsed:.2f} seconds')

@task(retries=3, retry_delay_seconds=10)
def task_ingest_metar(log):
  log.info('Executing task_ingest_metar')
  start_time = time.time()
  try:
    data.ingest_weather_metar()
  except Exception as e:
    log.error('ERROR in task_ingest_weather_metar')
    raise e
  end_time = time.time()
  elapsed = end_time - start_time
  log.info(f'task_ingest_metar completed in {elapsed:.2f} seconds')

@task(retries=3, retry_delay_seconds=10)
def task_ingest_philadelphia_crime(log):
  log.info('Executing task_ingest_philadelphia_crime')
  start_time = time.time()
  try:
    data.ingest_philadelphia_crime()
  except Exception as e:
    log.error('ERROR in task_ingest_philadelphia_crime')
    raise e
  end_time = time.time()
  elapsed = end_time - start_time
  log.info(f'task_ingest_philadelphia_crime completed in {elapsed:.2f} seconds')

@task(retries=3, retry_delay_seconds=10)
def task_ingest_detroit_crime(log):
  log.info('Executing task_ingest_detroit_crime')
  start_time = time.time()
  try:
    data.ingest_detroit_crime()
  except Exception as e:
    log.error('ERROR in task_ingest_detroit_crime')
    raise e
  end_time = time.time()
  elapsed = end_time - start_time
  log.info(f'task_ingest_detroit_crime completed in {elapsed:.2f} seconds')

@task(retries=3, retry_delay_seconds=10)
def task_ingest_current_baseball(log):
  log.info('Executing task_ingest_current_baseball')
  start_time = time.time()
  try:
    data.ingest_current_baseball()
  except Exception as e:
    log.error('ERROR in task_ingest_current_baseball')
    raise e
  end_time = time.time()
  elapsed = end_time - start_time
  log.info(f'task_ingest_current_baseball completed in {elapsed:.2f} seconds')

@task(retries=3, retry_delay_seconds=10)
def task_ingest_historical_baseball(log):
  log.info('Executing task_ingest_historical_baseball')
  start_time = time.time()
  try:
    data.ingest_historical_baseball()
  except Exception as e:
    log.error('ERROR in task_ingest_historical_baseball')
    raise e
  end_time = time.time()
  elapsed = end_time - start_time
  log.info(f'task_ingest_historical_baseball completed in {elapsed:.2f} seconds')


@flow
def ingestion_flow():
  local_logger = initialize_logger(log_destination='orchestrator.log', logger_name='orchestrator_log')

  local_logger.info('Executing ingestion_flow')
  try:
    task_ingest_ncei(local_logger)
    task_ingest_metar(local_logger)
    task_ingest_detroit_crime(local_logger)
    task_ingest_philadelphia_crime(local_logger)
    task_ingest_current_baseball(local_logger)
    if datetime.now().month == HISTORICAL_BASEBALL_INGESTION_MONTH:
      task_ingest_historical_baseball(local_logger)
  except Exception as e:
    local_logger.error(f'ERROR: {e}')
    raise
  local_logger.info('ingestion_flow completed successfully')

  return 'success'

if __name__ == "__main__":
  ingestion_flow.serve(
    name="ingestion_flow",
    cron="0 10 * * *"
  )
