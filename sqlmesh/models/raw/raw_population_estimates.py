import os
import sys
from dotenv import load_dotenv
from sqlmesh import model
import polars as pl
from minio import Minio

current_path = os.path.dirname(os.path.abspath(__file__))
parent_path = os.path.abspath(os.path.join(current_path, "..", ".."))
sys.path.append(parent_path)

@model(
  name="raw.population_estimates",
  kind="FULL",
  gateway="duckdb",
  columns={
    'geographic_area': 'str',
    'year': 'int',
    'population': 'int'
  }
)
def execute(context, **kwargs):
  load_dotenv()

  POP_ESTIMATES_2000s = 'population/us_census_bureau_pop_estimates_2000-2009.csv'
  POP_ESTIMATES_2010s = 'population/us_census_bureau_pop_estimates_2010-2019.csv'
  POP_ESTIMATES_2020s = 'population/us_census_bureau_pop_estimates_2020-2024.csv'

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
  
  collected_years = []
  with minio_client.get_object(MINIO_BUCKET_NAME, POP_ESTIMATES_2000s) as response:
    pop_2000s = pl.read_csv(response, infer_schema=False, has_header=True)
    pop_2000s = pop_2000s.with_columns(
      (pl.col("NAME") + ', ' + pl.col("STNAME")).alias("geographic_area")
    )
    pop_2000s_narrow = pop_2000s.unpivot(
      on=[
        "POPESTIMATE2000",
        "POPESTIMATE2001",
        "POPESTIMATE2002",
        "POPESTIMATE2003",
        "POPESTIMATE2004",
        "POPESTIMATE2005",
        "POPESTIMATE2006",
        "POPESTIMATE2007",
        "POPESTIMATE2008",
        "POPESTIMATE2009"
      ],
      index=["geographic_area"],
      variable_name="year_text",
      value_name="population_text"
    )
    
    len(pop_2000s_narrow)
    collected_years.append(pop_2000s_narrow)

  with minio_client.get_object(MINIO_BUCKET_NAME, POP_ESTIMATES_2010s) as response:
    pop_2010s = pl.read_csv(response, infer_schema=False, has_header=True, skip_lines=3)
    pop_2010s = pop_2010s.rename({"_duplicated_0": "geographic_area"})
    
    pop_2010s_narrow = pop_2010s.unpivot(
      on=['2010', '2011', '2012', '2013', '2014', '2015', '2016', '2017', '2018', '2019'],
      index=["geographic_area"],
      variable_name="year_text",
      value_name="population_text"
    )

    collected_years.append(pop_2010s_narrow)

  with minio_client.get_object(MINIO_BUCKET_NAME, POP_ESTIMATES_2020s) as response:
    pop_2020s = pl.read_csv(response, infer_schema=False, has_header=True, skip_lines=4)
    pop_2020s = pop_2020s.rename({"_duplicated_0": "geographic_area"})

    pop_2020s_narrow = pop_2020s.unpivot(
      on=['2020', '2021', '2022', '2023', '2024'],
      index=["geographic_area"],
      variable_name="year_text",
      value_name="population_text"
    )

    collected_years.append(pop_2020s_narrow)

  pop_all_years = pl.concat(collected_years)

  pop_all_years = pop_all_years.with_columns(
    pl.col("year_text").str.replace('POPESTIMATE','').cast(pl.Int64).alias("year"),
    pl.col("population_text").str.replace_all(',','').cast(pl.Int64).alias("population")
  )

  pop_all_years = pop_all_years.drop(['year_text', 'population_text'])

  pop_all_years = pop_all_years.filter(pl.col('geographic_area').is_not_null())

  return pop_all_years.to_pandas()
