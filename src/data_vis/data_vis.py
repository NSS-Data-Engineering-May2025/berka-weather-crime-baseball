import os
import numpy as np
import polars as pl
import pandas as pd
import streamlit as st
import duckdb
from datetime import datetime, timedelta

today = datetime.now()
database_years = list(range(2000, today.year + 1))

cities = ['Detroit', 'Philadelphia']

def get_sql_script(city):
  current_path = os.path.dirname(os.path.abspath(__file__))
  sql_file_path = f'{current_path}/sql/{city.lower()}.sql'
  with open(sql_file_path, 'r') as file:
    sql_script = file.read()
    return sql_script

with duckdb.connect('sqlmesh/db.db') as conn:
  analysis_city = st.selectbox(
    "City",
    cities,
    index=None,
    placeholder="Select city..."
  )

  if analysis_city is not None:
    sql_script = get_sql_script(analysis_city)
    city_table = conn.execute(sql_script).fetchdf()

    analysis_year = st.selectbox(
      "Year",
      options=database_years,
      index=None,
      placeholder="Select year..."
    )

    if analysis_year is not None:
      city_table = city_table[city_table['report_date'].dt.year == analysis_year]

      start_date = datetime(analysis_year, 1, 1)
      end_date = datetime(analysis_year + 1, 1, 1)
      options = [(start_date + timedelta(days=i)).strftime('%Y-%m-%d') for i in range((end_date - start_date).days)]

      analysis_start, analysis_end = st.select_slider(
      "Time Range",
      options=options,
      value=(f'{analysis_year}-01-01',f'{analysis_year}-12-31')
      )
      
      city_table = city_table[
        (city_table['entry_date'] >= datetime.strptime(analysis_start, '%Y-%m-%d')) &
        (city_table['entry_date'] <= datetime.strptime(analysis_end, '%Y-%m-%d'))]
      
      # The join with baseball creates duplicate entries for days with double headers
      city_table_deduped = city_table.drop_duplicates(subset='entry_date', keep='last')
      city_table_home_games = city_table[city_table['home_game'] == True]

      st.line_chart(city_table_deduped, x="entry_date", y=["max_temp_deg_f", "min_temp_deg_f"])
      st.bar_chart(city_table_deduped, x="entry_date", y=["total_incidents_per_100000", "burglary_per_100000"])

      city_table_home_games[['report_date', 'team', 'home_game']]
      st.bar_chart(city_table_home_games, x='entry_date', y=['team'])
      len(city_table_home_games)
