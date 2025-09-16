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
  st.title('Weather x Crime x Baseball')

  with st.sidebar:
    analysis_city = st.selectbox(
      "City",
      cities,
      index=None,
      placeholder="Select city..."
    )
  if analysis_city is None:
    st.write('[Select a city from the sidebar]')
  if analysis_city is not None:
    st.header(analysis_city)
    sql_script = get_sql_script(analysis_city)
    city_table = conn.execute(sql_script).fetchdf()

    team_name = city_table['team'].mode()[0]
    analysis_start = city_table['entry_date'].min().strftime('%Y-%m-%d')
    analysis_end = city_table['entry_date'].max().strftime('%Y-%m-%d')

    with st.sidebar:
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

      with st.sidebar:
        analysis_start, analysis_end = st.select_slider(
        "Date Range",
        options=options,
        value=(f'{analysis_year}-01-01',f'{analysis_year}-12-31')
        )
      
      city_table = city_table[
        (city_table['entry_date'] >= datetime.strptime(analysis_start, '%Y-%m-%d')) &
        (city_table['entry_date'] <= datetime.strptime(analysis_end, '%Y-%m-%d'))]
      
    # The join with baseball creates duplicate entries for days with double headers
    city_table_deduped = city_table.drop_duplicates(subset='entry_date', keep='last')
    city_table_deduped_bb_season = city_table[city_table['team_current_record_wins_lag'].notnull()]

    #WEATHER X CRIME
    st.header(body='Weather x Crime')
    if city_table['total_incidents'].sum() == 0:
      st.write('No Crime Data Available For Timeframe')
    else:
      avg_incidents = city_table_deduped['total_incidents_per_100k'].mean()

      avg_incidents_hot = city_table_deduped[
        city_table_deduped['max_temp_deg_f'] > city_table_deduped['avg_max_temp_deg_f']
      ]['total_incidents_per_100k'].mean()

      avg_incidents_cold = city_table_deduped[
        city_table_deduped['min_temp_deg_f'] < city_table_deduped['avg_min_temp_deg_f']
      ]['total_incidents_per_100k'].mean()
        
      st.metric(
        label=f'Average Daily Incidents per 100k residents ({analysis_start} - {analysis_end})',
        value=round(avg_incidents, 2)
      )

      crime_hot, crime_cold = st.columns(2)
      with crime_hot:
        st.metric(
          label=f'with Daily Max Temp > Avg Daily Max Temp',
          value=round(avg_incidents_hot,2),
          delta=round(avg_incidents_hot - avg_incidents, 2),
          delta_color='inverse'
        )
      with crime_cold:
        st.metric(
          label=f'with Daily Min Temp < Avg Daily Min Temp',
          value=round(avg_incidents_cold,2),
          delta=round(avg_incidents_cold - avg_incidents, 2),
          delta_color='inverse'
        )

      avg_violent = city_table_deduped['violent_crime_per_100k'].mean()

      avg_violent_hot = city_table_deduped[
        city_table_deduped['max_temp_deg_f'] > city_table_deduped['avg_max_temp_deg_f']
      ]['violent_crime_per_100k'].mean()

      avg_violent_cold = city_table_deduped[
        city_table_deduped['min_temp_deg_f'] < city_table_deduped['avg_min_temp_deg_f']
      ]['violent_crime_per_100k'].mean()
        
      st.metric(
        label=f'Average Daily Violent Crime per 100k residents ({analysis_start} - {analysis_end})',
        value=round(avg_violent, 2)
      )

      violent_hot, violent_cold = st.columns(2)
      with violent_hot:
        st.metric(
          label=f'with Daily Max Temp > Avg Daily Max Temp',
          value=round(avg_violent_hot,2),
          delta=round(avg_violent_hot - avg_violent, 2),
          delta_color='inverse'
        )
      with violent_cold:
        st.metric(
          label=f'with Daily Min Temp < Avg Daily Min Temp',
          value=round(avg_violent_cold,2),
          delta=round(avg_violent_cold - avg_violent, 2),
          delta_color='inverse'
        )

      if analysis_year is not None:
        st.line_chart(city_table_deduped, x="entry_date", y=["total_incidents_per_100k", "violent_crime_per_100k"], x_label='Date', y_label='Daily Incidents')
    #CRIME X BASEBALL
    st.header(body=f'Crime x {team_name}')
    if city_table['total_incidents'].sum() == 0:
      st.write('No Crime Data Available For Timeframe')
    else:
      avg_incidents = city_table_deduped_bb_season['total_incidents_per_100k'].mean()

      avg_incidents_500up = city_table_deduped_bb_season[
        city_table_deduped_bb_season['team_current_record_wins_lag'] > city_table_deduped_bb_season['team_current_record_losses_lag']
      ]['total_incidents_per_100k'].mean()
      avg_incidents_500down = city_table_deduped_bb_season[
        city_table_deduped_bb_season['team_current_record_wins_lag'] < city_table_deduped_bb_season['team_current_record_losses_lag']
      ]['total_incidents_per_100k'].mean()

      avg_incidents_w4plus = city_table_deduped_bb_season[
          city_table_deduped_bb_season['team_current_streak'] >= 4
        ]['total_incidents_per_100k'].mean()
      avg_incidents_l4plus = city_table_deduped_bb_season[
          city_table_deduped_bb_season['team_current_streak'] <= -4
        ]['total_incidents_per_100k'].mean()
      
      if avg_incidents > 0:
        st.metric(label=f'Avg Daily Incidents per 100k residents during baseball season ({analysis_start} - {analysis_end})', value=round(avg_incidents,2))
        up500, down500 = st.columns(2)
        with up500:
          st.metric(
            label=f'with Win Pct > .500',
            value=round(avg_incidents_500up,2),
            delta=round(avg_incidents_500up-avg_incidents, 2),
            delta_color='inverse')
        with down500:
          st.metric(
            label='with Win Pct < .500',
            value=round(avg_incidents_500down,2)
              if not np.isnan(avg_incidents_500down)
              else 'NA',
            delta=round(avg_incidents_500down-avg_incidents, 2)
              if not np.isnan(avg_incidents_500down)
              else 'NA',
            delta_color='inverse')
        w4plus, l4plus = st.columns(2)
        with w4plus:
          st.metric(
            label='with Winning Streak 4+',
            value=round(avg_incidents_w4plus,2),
            delta=round(avg_incidents_w4plus-avg_incidents, 2),
            delta_color='inverse')
        with l4plus:
          st.metric(
            label='with Losing Streak 4+',
            value=round(avg_incidents_l4plus,2),
            delta=round(avg_incidents_l4plus-avg_incidents, 2),
            delta_color='inverse')
    
    # WEATHER X BASEBALL
    st.header(f'Weather x {team_name}')

    city_table_home_games = city_table[city_table['home_game']]

    wins_table = city_table_home_games[city_table['team_outcome'] == 'win']
    losses_table = city_table_home_games[city_table['team_outcome'] == 'loss']
    wins_all = len(wins_table)
    losses_all = len(losses_table)
    win_pct_all = round(wins_all/(wins_all + losses_all), 3)

    wins_hot = len(wins_table[
      wins_table['max_temp_deg_f'] > wins_table['avg_max_temp_deg_f']
    ])
    losses_hot = len(losses_table[
      losses_table['max_temp_deg_f'] > losses_table['avg_max_temp_deg_f']
    ])
    win_pct_hot = round(wins_hot/(wins_hot + losses_hot), 3)

    wins_cold = len(wins_table[
      wins_table['min_temp_deg_f'] < wins_table['avg_min_temp_deg_f']
    ])
    losses_cold = len(losses_table[
      losses_table['min_temp_deg_f'] < losses_table['avg_min_temp_deg_f']
    ])
    win_pct_cold = round(wins_cold/(wins_cold + losses_cold), 3)
    
    st.metric(
      label=f'{team_name} Home Win-Loss (Win %) ({analysis_start} - {analysis_end})',
      value=f'{len(wins_table)} - {len(losses_table)} ({win_pct_all})'
    )

    wlhot, wlcold = st.columns(2)
    with wlhot:
      st.metric(
        label=f'with Daily Max Temp > Avg Daily Max Temp',
        value=f'{wins_hot} - {losses_hot} ({win_pct_hot})',
        delta=round(win_pct_hot-win_pct_all, 3)
      )
    with wlcold:
      st.metric(
        label=f'with Daily Min Temp < Avg Daily Min Temp',
        value=f'{wins_cold} - {losses_cold} ({win_pct_cold})',
        delta=round(win_pct_cold-win_pct_all, 3)
      )

    if analysis_year is not None:
      st.line_chart(
        city_table_deduped.rename(columns={
          "avg_max_temp_deg_f": "Avg Daily Max Temp",
          "avg_min_temp_deg_f": "Avg Daily Min Temp",
          "max_temp_deg_f": "Daily Max Temp",
          "min_temp_deg_f": "Daily Min Temp",
        }), x="entry_date", y=[ "Avg Daily Max Temp", "Avg Daily Min Temp", "Daily Max Temp", "Daily Min Temp"], color=["#f78674","#64c5fa","#f72a0a","#0f67f5"], y_label="Temp (F)", x_label='')
      st.write(f'{team_name} Home Games {analysis_year}')
      st.bar_chart(city_table_deduped[city_table_deduped['home_game']], x='entry_date', y='team', y_label='', x_label='')
