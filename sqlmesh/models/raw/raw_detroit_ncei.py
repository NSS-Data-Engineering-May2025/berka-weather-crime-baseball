import os
import sys
from sqlmesh import model
from sqlmesh.core.model.kind import ModelKindName

current_path = os.path.dirname(os.path.abspath(__file__))
parent_path = os.path.abspath(os.path.join(current_path, "..", ".."))
sys.path.append(parent_path)
from utils.ncei_bronze_model import get_ncei_bronze_table, ncei_schema

@model(
  name="raw.detroit_ncei",
  kind=dict(
    name=ModelKindName.INCREMENTAL_BY_TIME_RANGE,
    time_column="Date"
  ),
  start='2000-01-01',
  gateway="duckdb",
  columns=ncei_schema
)
def execute(context, start, end, **kwargs):
  bronze_table = get_ncei_bronze_table('detroit', start, end)

  if len(bronze_table) == 0:
    yield from ()
  else:
    yield bronze_table
