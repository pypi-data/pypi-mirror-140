#----- 1st Mar 2022 -----------#
#----- ZhangLe ----------------#
#----- Feature Engineering-----#

import pandas as pd
from ds_common_tool import suite_data

def sg_longterm(df, brent_df, gas_df, weather_df, filter_columns, target_column):
  if (df.shape[0] < 100) or (df.shape[1] < 4):
    print('please check usep dataframe shape')
    return None
  if (brent_df.shape[0] < 100) or (brent_df.shape[1] < 6):
    print('please check brent dataframe shape')
    return None
  if (gas_df.shape[0] < 100) or (gas_df.shape[1] < 5):
    print('please check gas future dataframe shape')
    return None
  if (weather_df.shape[0] < 100) or (weather_df.shape[1] < 7):
    print('please check weather future dataframe shape')
    return None
  new_df = suite_data.add_period_to_time(df, 'DATE', 'PERIOD', 30)
  new_df.set_index('DATE', inplace=True)
  new_df = suite_data.remove_outlier(new_df, 'USEP ($/MWh)', n_outlier=0.25)
  new_df = new_df.resample('D').mean()
  new_df = suite_data.get_n_rolling(new_df, 'USEP ($/MWh)', n=30, method='mean')
  brent_data   = suite_data.read_data_external(brent_df, new_df, 'Date', 5)
  gas_data     = suite_data.read_data_external(gas_df, new_df, 'DATE', 5)
  weather_data = suite_data.read_data_external(weather_df, new_df, 'DATE', 5)
  all_data = suite_data.merge_dfs(df_list = [new_df, brent_data, gas_data, weather_data], on_column = 'DATE')
  df1 = all_data[['DATE', 'RNGC1']]
  df2 = all_data[['DATE', 'Open']]
  df3 = all_data[['DATE', 'humidity']]
  df1 = suite_data.shift_row(df1, target_columns='RNGC1', shift_n_list = [-30])
  df2 = suite_data.shift_row(df2, target_columns='Open', shift_n_list = [-30])
  df3 = suite_data.shift_row(df3, target_columns='humidity', shift_n_list = [-30])
  all_data = suite_data.merge_dfs(df_list = [all_data, 
                                             df1[['DATE', 'RNGC1_-30']], 
                                             df2[['DATE', 'Open_-30']], 
                                             df3[['DATE', 'humidity_-30']]], on_column = 'DATE')
  all_data = all_data[filter_columns]
  all_data = suite_data.get_trend_mean(all_data, date_column_name = 'DATE')
  all_data = suite_data.switch_y_column(all_data, column_name=target_column)
  if (all_data.shape[0] < 100) or (all_data.shape[1] < 80):
    print('please check data processing function... data_shape is now :', all_data.shape)
  return all_data

