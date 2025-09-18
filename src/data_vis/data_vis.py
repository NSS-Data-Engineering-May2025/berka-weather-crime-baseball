import os
import numpy as np
import polars as pl
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st
import duckdb
from datetime import datetime, timedelta

today = datetime.now()
database_years = list(range(2000, today.year + 1))

cities = ['Detroit', 'Philadelphia']

weather_options = {
  'Daily Max Temp (F)': 'Max Temp',
  'Daily Min Temp (F)': 'Min Temp',
  'Daily Max Temp Deviation\nFrom Avg Daily Max (F)': 'Max Temp Deviation',
  'Daily Min Temp Deviation\nFrom Avg Daily Min (F)': 'Min Temp Deviation'
}

crime_options={
  'Incidents per 100k': 'Total Incidents',
  'Violent Crime per 100k': 'Violent Crime',
  'Assaults per 100k': 'Assault',
  'Homicides per 100k': 'Homicide',
  'Thefts per 100k': 'Theft'
}

baseball_options_daily={
  'Runs Scored': 'Runs Scored',
  'Win/Loss': 'Win/Loss'
}

baseball_options_ongoing={
  'Current Win/Loss Streak\n(Loss < 0)': 'Streak',
  'Current Win %': 'Win %',
  'Current Win %\n(Last 10 Games)': 'Win % (10)',
  'Current Win %\n(Last 40 Games)': 'Win % (40)'
}

def get_sql_script(city):
  current_path = os.path.dirname(os.path.abspath(__file__))
  sql_file_path = f'{current_path}/sql/{city.lower()}.sql'
  with open(sql_file_path, 'r') as file:
    sql_script = file.read()
    return sql_script
  
def regression_model(data, x_options, y_options, model_key, swap_xy_option = False):
  with st.expander('Regression Analysis'):
    st.subheader('Linear Regression Model')

    axes, model = st.columns(2)
    with axes:
      x_select = st.pills(
        "X-Axis",
        options=x_options.keys(),
        format_func=lambda choice: x_options[choice],
        selection_mode='single',
        key=f'x_{model_key}'
      )
      y_select = st.pills(
        "Y-Axis",
        options=y_options.keys(),
        format_func=lambda choice: y_options[choice],
        selection_mode='single',
        key=f'y_{model_key}'
      )
      swap_xy = False
      tog1, tog2, tog3 = st.columns(3)
      with tog1:
        averages = st.toggle('Show Averages', key=f'toggle_avg_{model_key}')
      with tog2:
        binary = st.toggle('Fit Binary', key=f'toggle_log_{model_key}')
      if swap_xy_option:
        with tog3:
          swap_xy = st.toggle('Swap axes', key=f'toggle_xy_{model_key}')
      if x_select is not None and y_select is not None:
        correlation = round(data[x_select].corr(data[y_select]), 3)
        pcc_message = f"_Pearson's Correlation Coefficient_: {correlation}"
        if abs(correlation) < 0.3:
          st.error(pcc_message)
        elif abs(correlation) < 0.7:
          st.warning(pcc_message)
        else:
          st.success(pcc_message)
      else:
        st.caption('_Select x- and y- axes to display model_')
    
    with model:
      if x_select is not None and y_select is not None:
        fig, ax = plt.subplots(figsize=(7,4))      
        sns.regplot(
          x=x_select if not swap_xy else y_select,
          x_estimator=np.mean if averages else None,
          y=y_select if not swap_xy else x_select,
          data=data,
          ax=ax,
          color='black',
          marker='.',
          line_kws=dict(color='r'),
          logistic=binary if binary else False
        )
        st.pyplot(fig)

def correlation_matrix(data):
  fields = []
  if city_table['report_date'].count() == 0:
    st.write('_No Weather Data For Timeframe_')
  else:
    fields.extend(weather_options)
  if city_table['total_incidents'].sum() == 0:
      st.write('_No Crime Data For Timeframe_')
  else:
    fields.extend(crime_options)
  if city_table['team_game_number'].count() == 0:
    st.write('_No Baseball Data For Timeframe_')
  else:
    fields.extend(baseball_options_daily)
    fields.extend(baseball_options_ongoing)
  if len(fields) > 0:
    data_filtered = data[fields]
    fig, ax = plt.subplots(figsize=(11, 9))
    corr = data_filtered.corr()
    mask = np.triu(np.ones_like(corr, dtype=bool))
    cmap = sns.diverging_palette(230, 20, as_cmap=True, center='dark')
    sns.heatmap(
      corr,
      mask=mask,
      cmap=cmap,
      vmax=.8,
      center=0,
      square=True,
      linewidths=1,
      cbar_kws={"shrink": .5},
      ax = ax,
      annot=True,
      annot_kws={'size': 10},
      fmt='.2f')
    plt.xticks(rotation=85, fontsize=10)
    plt.yticks(rotation=0, fontsize=10)

    st.pyplot(fig)


st.set_page_config(layout='wide')

with duckdb.connect('sqlmesh/db.db') as conn:

  with st.sidebar:
    analysis_city = st.selectbox(
      "City",
      cities,
      index=None,
      placeholder="Select city..."
    )

  st.title('Weather x Crime x Baseball')
  if analysis_city is None:
    st.caption('_[Select a city from the sidebar]_')
  if analysis_city is not None:
    st.header(analysis_city)
    sql_script = get_sql_script(analysis_city)
    city_table = conn.execute(sql_script).fetchdf()

    city_table = city_table.rename(columns={
      'max_temp_deg_f': 'Daily Max Temp (F)',
      'daily_max_temp_deviation_from_max': 'Daily Max Temp Deviation\nFrom Avg Daily Max (F)',
      'daily_min_temp_deviation_from_min': 'Daily Min Temp Deviation\nFrom Avg Daily Min (F)',
      'min_temp_deg_f': 'Daily Min Temp (F)',
      'total_precip_inches': 'Precipitation (in)',
      'total_incidents_per_100k': 'Incidents per 100k',
      'violent_crime_per_100k': 'Violent Crime per 100k',
      'assault_per_100k': 'Assaults per 100k',
      'homicide_per_100k': 'Homicides per 100k',
      'theft_per_100k': 'Thefts per 100k',
      'team_current_streak': 'Current Win/Loss Streak\n(Loss < 0)',
      'team_outcome': 'Win/Loss (Text)',
      'team_outcome_as_value': 'Win/Loss',
      'team_score': 'Runs Scored',
      'team_current_record_wins': 'Current Record Wins',
      'team_current_record_losses': 'Current Record Losses',
      'team_current_win_pct': 'Current Win %',
      'team_last_10_win_pct': 'Current Win %\n(Last 10 Games)',
      'team_last_40_win_pct': 'Current Win %\n(Last 40 Games)'
    })

    team_name = city_table['team'].mode()[0]
    analysis_start = city_table['entry_date'].min().strftime('%Y-%m-%d')
    analysis_end = city_table['entry_date'].max().strftime('%Y-%m-%d')

    analysis_start_year = None
    analysis_end_year = None
    with st.sidebar:
      analysis_year = st.selectbox(
        "Year",
        options=database_years,
        index=None,
        placeholder="Select year..."
      )
    if analysis_year is None:
      start_year = city_table['entry_date'].min().year
      end_year = city_table['entry_date'].max().year
      year_options = list(range(start_year, end_year + 1))
      with st.sidebar:
        st.write('OR')
        analysis_start_year, analysis_end_year = st.select_slider(
        "Timeframe",
        options=year_options,
        value=(start_year, end_year)
        )
    
    if analysis_year is not None:
      start_date = datetime(analysis_year, 1, 1)
      end_date = datetime(analysis_year + 1, 1, 1)
      options = [(start_date + timedelta(days=i)).strftime('%Y-%m-%d') for i in range((end_date - start_date).days)]

      with st.sidebar:
        analysis_start, analysis_end = st.select_slider(
        "Timeframe",
        options=options,
        value=(f'{analysis_year}-01-01',f'{analysis_year}-12-31')
        )
    else:
      if analysis_start_year != int(analysis_start.split('-')[0]):
        analysis_start = datetime(analysis_start_year, 1, 1).strftime('%Y-%m-%d')
      if analysis_end_year != int(analysis_end.split('-')[0]):
        analysis_end = datetime(analysis_end_year, 12, 31).strftime('%Y-%m-%d')
      
    city_table = city_table[
      (city_table['entry_date'] >= datetime.strptime(analysis_start, '%Y-%m-%d')) &
      (city_table['entry_date'] <= datetime.strptime(analysis_end, '%Y-%m-%d'))]
      
    # The join with baseball creates duplicate entries for days with double headers
    city_table_deduped = city_table.drop_duplicates(subset='entry_date', keep='last')
    city_table_deduped_bb_season = city_table[city_table['team_current_record_wins_lag'].notnull()]

    with st.expander('Correlation Matrix'):
      correlation_matrix(city_table)

    #WEATHER X CRIME
    st.header(body='Weather x Crime')
    if city_table['total_incidents'].sum() == 0:
      st.write('_No Crime Data For Timeframe_')
    elif city_table['report_date'].count() == 0:
      st.write('_No Weather Data For Timeframe_')
    else:

      crime_metric = st.pills(
        "Metric",
        label_visibility='collapsed',
        options=crime_options.keys(),
        format_func=lambda choice: crime_options[choice],
        selection_mode='single',
        default='Incidents per 100k'
      )

      if crime_metric is None:
        crime_metric = 'Incidents per 100k'

      avg_incidents = city_table_deduped[crime_metric].mean()

      avg_incidents_hot = city_table_deduped[
        city_table_deduped['Daily Max Temp (F)'] > city_table_deduped['avg_max_temp_deg_f']
      ][crime_metric].mean()

      avg_incidents_cold = city_table_deduped[
        city_table_deduped['Daily Min Temp (F)'] < city_table_deduped['avg_min_temp_deg_f']
      ][crime_metric].mean()

      avg_incidents_rainy = city_table_deduped[
        city_table_deduped['Precipitation (in)'] >= 1
      ][crime_metric].mean()
        
      st.metric(
        label=f'Avg Daily {crime_metric} residents ({analysis_start} - {analysis_end})',
        value=round(avg_incidents, 2)
      )

      crime_hot, crime_cold, crime_rainy = st.columns(3)
      with crime_hot:
        st.metric(
          label=f'with Daily Max Temp > Avg Daily Max Temp',
          value=round(avg_incidents_hot,2),
          delta=round(avg_incidents_hot - avg_incidents, 2),
          delta_color='inverse'
        )
      with crime_cold:
        st.metric(
          label='with Daily Min Temp < Avg Daily Min Temp',
          value=round(avg_incidents_cold,2),
          delta=round(avg_incidents_cold - avg_incidents, 2),
          delta_color='inverse'
        )
      with crime_rainy:
        st.metric(
          label='with Daily Precipitation > 1in',
          value=round(avg_incidents_rainy,2),
          delta=round(avg_incidents_rainy - avg_incidents, 2),
          delta_color='inverse'
        )
      
      if analysis_year is not None:
        st.line_chart(city_table_deduped, x="entry_date", y=crime_metric, x_label='', y_label=f'Daily {crime_metric}')
    

      regression_model(
        data=city_table_deduped,
        x_options=weather_options,
        y_options=crime_options,
        model_key='crimexweather'
      )          

    st.divider()

    #CRIME X BASEBALL
    st.header(body=f'Crime x {team_name}')
    if city_table['total_incidents'].sum() == 0:
      st.write('_No Crime Data Available For Timeframe_')
    elif city_table['team_game_number'].sum() == 0:
      st.write(f'_No {team_name} Data For Timeframe_')
    else:
      avg_incidents = city_table_deduped_bb_season['Incidents per 100k'].mean()

      avg_incidents_500up = city_table_deduped_bb_season[
        city_table_deduped_bb_season['team_current_record_wins_lag'] > city_table_deduped_bb_season['team_current_record_losses_lag']
      ]['Incidents per 100k'].mean()
      avg_incidents_500down = city_table_deduped_bb_season[
        city_table_deduped_bb_season['team_current_record_wins_lag'] < city_table_deduped_bb_season['team_current_record_losses_lag']
      ]['Incidents per 100k'].mean()

      avg_incidents_w4plus = city_table_deduped_bb_season[
          city_table_deduped_bb_season['Current Win/Loss Streak\n(Loss < 0)'] >= 4
        ]['Incidents per 100k'].mean()
      avg_incidents_l4plus = city_table_deduped_bb_season[
          city_table_deduped_bb_season['Current Win/Loss Streak\n(Loss < 0)'] <= -4
        ]['Incidents per 100k'].mean()
      
      if avg_incidents > 0:
        st.metric(label=f'Avg Daily Incidents per 100k residents during baseball season ({analysis_start} - {analysis_end})', value=round(avg_incidents,2))
        up500, down500, w4plus, l4plus = st.columns(4)
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
          
      regression_model(
        data=city_table_deduped,
        x_options=baseball_options_ongoing,
        y_options=crime_options,
        model_key='crimexbaseball',
        swap_xy_option=True
      )  
    
    st.divider()

    # WEATHER X BASEBALL
    st.header(f'Weather x {team_name} (at Home)')

    city_table_home_games = city_table[city_table['home_game']]
    if len(city_table_home_games) == 0:
      st.write(f'_No {team_name} Home Games For Timeframe_')
    elif city_table_home_games['report_date'].count() == 0:
      st.write('_No Weather Data For Timeframe_')
    else:
      wins_table = city_table_home_games[city_table_home_games['Win/Loss (Text)'] == 'win']
      losses_table = city_table_home_games[city_table_home_games['Win/Loss (Text)'] == 'loss']
      wins_all = len(wins_table)
      losses_all = len(losses_table)
      win_pct_all = round(wins_all/(wins_all + losses_all), 3)

      wins_hot = len(wins_table[
        wins_table['Daily Max Temp (F)'] > wins_table['avg_max_temp_deg_f']
      ])
      losses_hot = len(losses_table[
        losses_table['Daily Max Temp (F)'] > losses_table['avg_max_temp_deg_f']
      ])
      win_pct_hot = round(wins_hot/(wins_hot + losses_hot), 3)

      wins_cold = len(wins_table[
        wins_table['Daily Min Temp (F)'] < wins_table['avg_min_temp_deg_f']
      ])
      losses_cold = len(losses_table[
        losses_table['Daily Min Temp (F)'] < losses_table['avg_min_temp_deg_f']
      ])
      win_pct_cold = round(wins_cold/(wins_cold + losses_cold), 3)

      wins_rainy = len(wins_table[wins_table['Precipitation (in)'] > 1])
      losses_rainy = len(losses_table[losses_table['Precipitation (in)'] > 1])
      win_pct_rainy = round(wins_rainy/(wins_rainy + losses_rainy), 3)
      
      st.metric(
        label=f'{team_name} Home Win-Loss (Win %) ({analysis_start} - {analysis_end})',
        value=f'{wins_all} - {len(losses_table)} ({win_pct_all})'
      )

      wlhot, wlcold, wlrainy = st.columns(3)
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
      with wlrainy:
        st.metric(
          label=f'with Daily Precipitation > 1in',
          value=f'{wins_rainy} - {losses_rainy} ({win_pct_rainy})',
          delta=round(win_pct_rainy-win_pct_all, 3)
        )

      regression_model(
        data=city_table_home_games,
        x_options=weather_options,
        y_options=baseball_options_daily,
        model_key='weatherxbaseball'
      )

      if analysis_year is not None:
        st.line_chart(
          city_table_deduped.rename(columns={
            "avg_max_temp_deg_f": "Avg Daily Max Temp",
            "avg_min_temp_deg_f": "Avg Daily Min Temp",
          }), x="entry_date", y=["Avg Daily Max Temp", "Avg Daily Min Temp", "Daily Max Temp (F)", "Daily Min Temp (F)"], color=["#f78674","#64c5fa","#f72a0a","#0f67f5"], y_label="Temp (F)", x_label='')
        st.write(f'{team_name} Home Games {analysis_year}')
        st.bar_chart(city_table_deduped[city_table_deduped['home_game']], x='entry_date', y='team', y_label='', x_label='')
