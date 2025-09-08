import os
import sys
from sqlmesh import model
from sqlmesh.core.model.kind import ModelKindName

current_path = os.path.dirname(os.path.abspath(__file__))
parent_path = os.path.abspath(os.path.join(current_path, "..", ".."))
sys.path.append(parent_path)
from utils.metar_bronze_model import get_metar_bronze_table, metar_schema

@model(
  name="raw.philadelphia_metar",
  kind=dict(
    name=ModelKindName.INCREMENTAL_BY_TIME_RANGE,
    time_column="reportTime"
  ),
  gateway="duckdb",
  start='2025-01-01',
  columns=metar_schema
)
def execute(context, start, end, **kwargs):
  bronze_table = get_metar_bronze_table('philadelphia', start, end)

  if len(bronze_table) == 0:
    yield from ()
  else:
    yield bronze_table
