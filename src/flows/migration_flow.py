import os
import sys
import time
import subprocess
from prefect import flow, task

current_path = os.path.dirname(os.path.abspath(__file__))
root_path = os.path.abspath(os.path.join(current_path, "..", ".."))
sys.path.append(root_path)
from src.logger import initialize_logger

@task(retries=3, retry_delay_seconds=10)
def task_run_sqlmesh(log):
  log.info('Executing task_run_sqlmesh')
  start_time = time.time()
  try:
    result = subprocess.run(
      ["sqlmesh", "run"],
      cwd=f'{root_path}/sqlmesh',
      capture_output=True,
      text=True,
      encoding='utf-8',
      errors="replace"
    )
    if result.returncode != 0:
        raise Exception(f"sqlmesh run failed: {result.stderr}")
    print(result.stdout)
  except Exception as e:
    log.error('ERROR in task_run_sqlmesh')
    raise e
  end_time = time.time()
  elapsed = end_time - start_time
  log.info(f'task_run_sqlmesh completed in {elapsed:.2f} seconds')

@flow
def migration_flow(ingestion_status = 'success'):
  if ingestion_status == 'success':
    local_logger = initialize_logger(log_destination='orchestrator.log', logger_name='orchestrator_log')

    local_logger.info('Executing ingestion_flow')
    try:
      task_run_sqlmesh(local_logger)
    except Exception as e:
      local_logger.error(f'ERROR: {e}')
      raise
    local_logger.info('migration_flow completed successfully')
  
  return 'success'

if __name__ == "__main__":
    migration_flow.serve(
    name="migration_flow",
    cron="0 11 * * *"
  )
