import pandas as pd
import glob
import os
from datetime import datetime
import pickle
import random
import matplotlib.pyplot as plt
import numpy as np
import re
from datetime import timedelta


# 
# def get_all_files(path_to_measurements):
#   # 
#   list_files = glob.glob(path_to_measurements)
#   # 
#   df_list = []
#   for i in range(len(list_files)):
#     df_temp = pd.read_csv(list_files[i],sep='\t',skiprows=(0,1,2),header=(30))
#     df_list.append(df_temp)
  # 
#   return df_list, list_files

def find_header_value(field, filename):
  # Get first 6 lines
  with open(filename) as file:
      lines = [next(file) for x in range(30)]
  value = None
  for line in lines:
      if line.startswith(field):
          # Get the part of the string after the field name
          end_of_string = line[len(field):]
          string = end_of_string[:-1]
  return string
  

def data_formatting(list_all_exp_with_target):
  # 
  df_all = pd.concat(list_all_exp_with_target)
  x_columns, y_columns = column_selection()
  X = df_all[x_columns]
  y = df_all[y_columns]
  # 
  return X, y






def get_exp_stage(time, dpps=4, baseline=2, absorb=7, pause=1, desorb=5, flush=23):
    
    # dpps: data point per second

    baseline_time = baseline*dpps
    if time <= baseline_time:
        return 'baseline'
    absorb_time = baseline_time + absorb*dpps
    if time <= absorb_time:
        return 'absorb'
    pause_time = absorb_time + pause*dpps
    if time <= pause_time:
        return 'pause'
    desorb_time = pause_time + desorb*dpps
    if time <= desorb_time:
        return 'desorb'
    flush_time = desorb_time + flush*dpps
    if time <= flush_time:
        return 'flush'
    wait_time = flush_time + flush*dpps
    if time <= wait_time:
        return 'wait'


def rename_columns(df, has_label=False):
    for col in df.columns:
        if 'Sen' in col:
        # print(col[4:])
            new_col = re.findall('\d+', col)[0]
            # print(new_col)
            df.rename(columns={col:f'sensor_{new_col}'}, inplace=True)
    df.rename(columns={'Data Points': 'timesteps'}, inplace=True)
    df.rename(columns={'Humidity (%r.h.)':'humidity'}, inplace=True)
    if has_label:
        df['exp_type'] = df['exp_type'].apply(lambda x: 'Covid' if x == 'COVID' else x)
    return df







def get_label(f):
    exp_name = find_header_value('Name of the experiment =', f)
    if 'Neg' in exp_name:
      return 'Control'
    else:
      return 'Covid'

def get_exp_stage_duration(f):
    baseline = float(find_header_value('Baseline = ', f))
    absorb = float(find_header_value('Absorb = ', f))
    pause = float(find_header_value('Pause = ', f))
    desorb = float(find_header_value('Desorb = ', f))
    flush = float(find_header_value('Flush = ', f))

    return baseline, absorb, pause, desorb, flush

def preprocess_single_file(f, parse_time=True, parse_filename=True, rename_column=True):

    df_temp = pd.read_csv(f,sep='\t',header=(37))
    baseline, absorb, pause, desorb, flush = get_exp_stage_duration(f)
    df_temp['measurement_stage'] = df_temp['Data Points'].apply(get_exp_stage)
    
    if parse_time:
      date = find_header_value('Date = ', f)
      df_temp['date_exp'] = find_header_value('Date = ', f)
      # df_temp['time_start'] = find_header_value('Time = ', f)
      df_temp['time_elapsed'] = df_temp.index / 4
      time_start = find_header_value('Time = ', f)
      time_elapsed = df_temp.index / 4
      timestamp = pd.to_datetime(date + " " + time_start)
      # df_temp['timestamp'] = pd.to_datetime(date + " " + df_temp['time_start'])
      df_temp['datetime_exp'] = pd.to_datetime(date + " " + time_start) + pd.to_timedelta(time_elapsed, unit='s')

    if parse_filename:
      df_temp['filename'] = f.split('/')[-1]
    

    df_temp['result'] = get_label(f)
    
    df_temp['exp_name'] = find_header_value('Name of the experiment = ', f)[1:-1]

    

    if rename_column:
      df = rename_columns(df_temp)

    return df_temp



def preprocess_all_files(path_to_measurements, parse_time=True, parse_filename=True, concat_files=True, rename_column=True):
  # 
  list_files = glob.glob(path_to_measurements)
  # 
  df_list = []
  for i, f in enumerate(list_files):

    df_temp = preprocess_single_file(f, parse_time=parse_time, parse_filename=parse_filename)
    df_temp['exp_unique_id'] = i

    # print(df_list)
    df_list.append(df_temp)

  
  if concat_files:
      df = pd.concat(df_list)
      col_list = df.columns.tolist()
      new_col_list = [col_list[-1]] + [col_list[-2]]  + col_list[:-2] 
      # print(new_col_list)
      df = df[new_col_list]
      return df

  else: 
      return df_list








  