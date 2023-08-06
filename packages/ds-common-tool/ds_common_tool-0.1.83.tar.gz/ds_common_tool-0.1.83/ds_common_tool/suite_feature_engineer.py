#----- 1st Mar 2022 -----------#
#----- ZhangLe ----------------#
#----- Feature Engineering-----#

import pandas as pd
from ds_common_tool import suite_data

def sg_long_term_feature_engineering(df, brent_df, gas_df, weather_df, filter_columns, target_column):
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


def sg_short_term_feature_engineering(dpr_df, reg_df, advisory_df_dummy, targetvariable, main_features):
    divideby =10
    if targetvariable == 'USEP':
        becomefeature = 'REG'
    elif targetvariable == 'REG':
        becomefeature = 'USEP'
    dpr_df['DATE'] = pd.to_datetime(dpr_df['DATE'])
    dpr_df = suite_data.add_period_to_time(dpr_df, 'DATE', 'PERIOD', 30)
    dpr_df = dpr_df.drop(columns=['PERIOD'])
    dpr_df.set_index('DATE', inplace=True)
    if dpr_df.shape[1] < 2:
        print('please check dpr_df dataframe shape')
        return None
    reg_df['DATE'] = pd.to_datetime(reg_df['DATE'])
    reg_df = suite_data.add_period_to_time(reg_df, 'DATE', 'PERIOD', 30)
    if reg_df.shape[1] < 3:
        print('please check reg_df dataframe shape')
        return None
    advisory_df_dummy['DATE'] = pd.to_datetime(advisory_df_dummy['DATE'])
    advisory_df_dummy = suite_data.add_period_to_time(advisory_df_dummy, 'DATE', 'PERIOD', 30)
    advisory_df_dummy = suite_data.read_data_external(advisory_df_dummy, dpr_df, 'DATE', 5) #dropna
    if advisory_df_dummy.shape[1] < 16:
        print('please check advisory_df_dummy dataframe shape')
        return None
    reg_df = suite_data.read_data_external(reg_df, dpr_df, 'DATE', 5) #dropna
    merged_df = dpr_df.merge(advisory_df_dummy, on=['DATE'], how='left').fillna(0) # original
    merged_df = merged_df.groupby(['DATE']).max().reset_index()
    merged_df = merged_df.merge(reg_df, on=['DATE'], how='left').fillna(0) #original
    merged_df['DAYOFWEEK'] = merged_df.DATE.map(lambda x:x.dayofweek+1)
    merged_df = merged_df.drop(columns=['PERIOD_y'])
    merged_df = merged_df.rename(columns={'PERIOD_x': 'PERIOD'})
    try:
        merged_df = merged_df[['DATE','PERIOD', 'DEMAND', 'USEP_ACTUAL', 'REG_PRICE', 'DAYOFWEEK', 'energy_shortfall_amt', 'reserve_shortfall_amt',
                           'regulation_shortfall_amt',
                          'abnormal_condition_type_Major Equipment Outage', 'abnormal_condition_type_Other',
                           'load_scenario_High', 'load_scenario_Low', 'load_scenario_Medium']]
    except:
        merged_df = merged_df[['DATE','PERIOD', 'DAYOFWEEK', 'DEMAND', 'USEP_ACTUAL', 'energy_shortfall_amt',
                           'abnormal_condition_type_Major Equipment Outage', 'abnormal_condition_type_Other',
                           'regulation_shortfall_amt', 'reserve_shortfall_amt']]
        merged_df['load_scenario_High'] = 0
        merged_df['load_scenario_Medium'] = 0
        merged_df['load_scenario_Low'] = 0
    merged_df.columns = [
    "DATE",
    "PERIOD",
    "DEMAND",
    "USEP",
    "REG",
    "DAYOFWEEK",
    "LOAD_SHORTFALL",
    "RES_SHORTFALL",
    "REG_SHORTFALL",
    "ABNORMAL_OUTAGE",
    "ABNORMAL_OTHER",
    "PRICE_WARNING",
    "PRICE_REVISION",
    "PROVISIONAL_PRICES"
    ]
    merged_df['PERIOD1'] = merged_df['PERIOD']
    merged_df['DAYOFWEEK1'] = merged_df['DAYOFWEEK']
    merged_df = suite_data.get_dummy(merged_df, dummy_columns=['PERIOD', 'DAYOFWEEK'])
    merged_df['year'] = merged_df.DATE.map(lambda x:x.year-2019)
    merged_df['month'] = merged_df.DATE.map(lambda x:x.month)
    merged_df['day'] = merged_df.DATE.map(lambda x:x.day)
    merged_df['Value_ewm'] = merged_df['REG'].ewm(com=0.5).mean()
    no_of_period = 12
    for period in range(no_of_period + 1):
        suite_data.shift_row(merged_df, 'REG', [period + 1], method_na='bfill')
    merged_df = merged_df.fillna(method='bfill')
    merged_df = suite_data.get_n_rolling(merged_df, 'REG', n=12, method='max') 
    merged_df = suite_data.get_n_rolling(merged_df, 'REG', n=12, method='min')
    merged_df = suite_data.get_n_rolling(merged_df, 'REG', n=12, method='mean')
    merged_df = suite_data.get_n_rolling(merged_df, 'REG', n=12, method='std')
    merged_df['Value_mean_12_diff'] = merged_df['mean_12'].diff(1).fillna(method='bfill')
    merged_df['DEMAND'] = merged_df['DEMAND']/2000
    merged_df[targetvariable] = merged_df[targetvariable]/divideby
    merged_df = merged_df.drop(columns=['PERIOD_0.0'])
    main_features = [targetvariable, becomefeature] + main_features  # [a, b] + [1,1,1,1] => [a,b,1,1,1,1,1]
    merged_df = merged_df[main_features]
    if merged_df.shape[1] < 13:
        print('please check data processing function... data_shape is now :', merged_df.shape)
        return None
    return merged_df


def shandong_feature_engineering(data, feature_columns, start_index, end_index, predict=False):
  data = data[feature_columns]
  data['出清前_竞价空间1'] = (data['出清前_直调负荷(MW)'] - data['出清前_联络线受电负荷(MW)'] - data['出清前_风电总加(MW)']
                         - data['出清前_光伏总加(MW)'] - data['出清前_地方电厂发电总加(MW)']
                         - data['出清前_试验机组总加(MW)'] - data['出清前_自备机组总加(MW)'])
  data['出清前_竞价空间2'] = (data['出清前_直调负荷(MW)'] - data['出清前_联络线受电负荷(MW)'] - data['出清前_风电总加(MW)']
                         - data['出清前_光伏总加(MW)'] - data['出清前_地方电厂发电总加(MW)'])
  data['出清前_新能源预测'] = data['出清前_风电总加(MW)'] + data['出清前_光伏总加(MW)']
  if predict==False:
        # data['date'] = data.index.date
        data['hour'] = data.index.hour
        data['time'] = (data.index.minute + data.index.hour * 60) / 15
        for day, data_day in data.resample('D'):
            date = str(day.date())
            if len(data.loc[date]) > 0:
                data.loc[date, '出清前_竞价空间1_max'] = data_day['出清前_竞价空间1'].max()
                data.loc[date, '出清前_竞价空间1_min'] = data_day['出清前_竞价空间1'].min()
                data.loc[date, '出清前_竞价空间1_mean'] = data_day['出清前_竞价空间1'].mean()
  else:
        data['hour']=data['时期']//4
        data['time']=data['时期']
        data['出清前_竞价空间1_max']=data['出清前_竞价空间1'].max()
        data['出清前_竞价空间1_min'] = data['出清前_竞价空间1'].min()
        data['出清前_竞价空间1_mean'] = data['出清前_竞价空间1'].mean()
  result_df = data[start_index : end_index]
  if result_df.shape[1] < 16:
      print('please check data processing function... data_shape is now :', result_df.shape)
      return None
  return result_df




