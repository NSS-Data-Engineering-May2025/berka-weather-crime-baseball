import os
import sys
from sqlmesh import model

current_path = os.path.dirname(os.path.abspath(__file__))
parent_path = os.path.abspath(os.path.join(current_path, "..", ".."))
sys.path.append(parent_path)
from utils.ncei_bronze_model import get_ncei_bronze_table, ncei_schema

@model(
  name="raw.detroit_ncei",
  kind="FULL",
  gateway="duckdb",
  columns=ncei_schema
)
def execute(context, **kwargs):
  bronze_table = get_ncei_bronze_table('detroit')

  return bronze_table
