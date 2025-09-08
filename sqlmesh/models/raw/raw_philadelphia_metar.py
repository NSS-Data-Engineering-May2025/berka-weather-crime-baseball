import os
import sys
from sqlmesh import model

current_path = os.path.dirname(os.path.abspath(__file__))
parent_path = os.path.abspath(os.path.join(current_path, "..", ".."))
sys.path.append(parent_path)
from utils.metar_bronze_model import get_metar_bronze_table, metar_schema

@model(
  name="raw.philadelphia_metar",
  kind="FULL",
  gateway="duckdb",
  columns=metar_schema
)
def execute(context, **kwargs):
  bronze_table = get_metar_bronze_table('philadelphia')

  return bronze_table
