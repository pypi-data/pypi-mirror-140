#----- 16th Feb 2022 -----#
#----- ZhangLe -----------#
#----- Data processing----#


from datetime import timedelta
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import TimeSeriesSplit

# 1. remove outlier
# tested
def remove_outlier(df, column_name, n_outlier=0.25):
    q1 = df[column_name].quantile(n_outlier)
    q3 = df[column_name].quantile(1 - n_outlier)
    iqr = q3 - q1
    lower_tail = q1 - 1.5 * iqr
    upper_tail = q3 + 1.5 * iqr
    print('lower_tail : ', lower_tail, '  upper_tail:', upper_tail)
    def remove_map(data):
        if data > float(upper_tail) or data < float(lower_tail):
            return n_outlier
        else:
            return data
    df['new'] = df[column_name].apply(remove_map)
    df = df.drop(columns = [column_name])
    df.rename(columns={'new': column_name}, inplace=True)
    return df

# 2. transform period
# tested
def add_period_to_time(df, date_column_name='DATE', period_column_name='PERIOD', period_minutes=30):
    df['DATE'] = pd.to_datetime(df[date_column_name], infer_datetime_format=True)
    def modify_period(data):
        mins = (data[period_column_name] - 1) * period_minutes
        new_date = data['DATE'] + timedelta(minutes = mins)
        return new_date
    df['data_label'] = df.apply(modify_period, axis=1)
    df['data_label'] = pd.to_datetime(df['data_label'], infer_datetime_format=True)
    df.drop(columns=[date_column_name, 'DATE'], inplace=True)
    df.rename(columns={ 'data_label': 'DATE' }, inplace=True)
    df['DATE'] = pd.to_datetime(df[date_column_name], infer_datetime_format=True)
    df = df.sort_values(by='DATE')
    df.reset_index(inplace=True)
    df.drop(columns=['index'], inplace=True)
    return df

# 3. split sequences for lstm/tcn/transformer model
# tested
def split_sequence(sequence, look_back = 30, look_forward = 30, print_shape = True):
    X, y = list(), list()
    loop_len = sequence.shape[0]
    for i in range(1, loop_len):
        end_ix = i + look_back # fing the end of the x parten
        out_end_ix = end_ix + look_forward - 1
        if out_end_ix > loop_len:
            break
        seq_x, seq_y = sequence[i - 1 : end_ix-1,  :-1], sequence[end_ix-1 : out_end_ix, -1]
        X.append(seq_x)
        y.append(seq_y)
    if print_shape:
        print('shape of seq_x : ', np.array(X).shape)
        print('shape of seq_y : ', np.array(y).shape)
    return np.array(X), np.array(y)

# 4. plot multiple data with label
# tested
def show_draft_plot(datas, x_label, title, legend, picture_size=[18, 5]):
    plt.rcParams["figure.figsize"] = picture_size
    for i in range(len(datas)):
        plt.plot(x_label, datas[i], label=legend[i])
    plt.title(title)
    plt.legend(loc="best", shadow=True)
    plt.grid()
    plt.show()

# 5. get N days rolling mean, max, min, median  
# tested  
def get_n_rolling(df, target_column_name, n = 30, method = 'mean'):
    new_label = method + '_' + str(n)
    if method == 'mean':
        df[new_label] = df[target_column_name].rolling(window = n, min_periods = 1, center = False).mean()
    if method == 'max':
        df[new_label] = df[target_column_name].rolling(window = n, min_periods = 1, center = False).max()
    if method == 'min':
        df[new_label] = df[target_column_name].rolling(window = n, min_periods = 1, center = False).min()
    if method == 'median':
        df[new_label] = df[target_column_name].rolling(window = n, min_periods = 1, center = False).median()
    if method == 'std':
        df[new_label] = df[target_column_name].rolling(window = n, min_periods = 1, center = False).std()
    return df

# 6. read external data files
# tested
def read_data_external(df,  main_df, date_column = 'DATE', fillna_limit_n=5):
    columns_to_drop = main_df.columns.to_list()
    # df = pd.read_csv(filepath_name, thousands=',')
    df['DATE'] = pd.to_datetime(df[date_column], infer_datetime_format=True, format="%Y-%m-%d")
    df = df.sort_values(by='DATE')
    df_fillna = main_df.merge(df, how='outer', on='DATE')
    df_fillna = df_fillna.fillna(method='ffill', limit = fillna_limit_n)
    df_fillna = df_fillna.dropna(how = 'any')
    if date_column != 'DATE':
        df_fillna.drop(columns=[date_column], inplace=True)
    df_fillna.drop(columns=columns_to_drop, inplace=True)
    return df_fillna

# 7. merge dataframe
# # method_na in ['dropna', 'fill_customize']
def merge_dfs(df_list = [], on_column = 'DATE', method_na = 'dropna', fill_customize_value = 0):
    if len(df_list) == 0:
        return pd.DataFrame()
    if len(df_list) == 1:
        return df_list[0]
    main_df = df_list[0]
    vace_df = df_list[1]
    for item in df_list[2:]:
        vace_df = vace_df.merge(item, on = on_column)
    main_df = main_df.merge(vace_df, on = on_column)
    if method_na == 'dropna':
        main_df = main_df.dropna(axis=0, how='any')
    if method_na == 'fill_customize':
        main_df = main_df.fillna(fill_customize_value)
    return main_df

# 8. add shiftted column value 
# method_na in ['dropna', 'bfill', 'ffill']
def shift_row(df, target_columns, shift_n_list = [], method_na = 'dropna'):
    for index in range(len(shift_n_list)):
        column_name = target_columns + '_' + str(shift_n_list[index])
        df[column_name] = df[target_columns].shift(shift_n_list[index])
    if method_na == 'dropna':
        df = df.dropna(axis=0, how='any')
    if method_na in ['bfill', 'ffill']:
        df = df.fillna(method=method_na)
    return df

# 9. TimeSeriesSplit from test data into test and validation data
def time_split_dataset(X, y, split_n = 30, print_shape=True):
    tscv = TimeSeriesSplit(max_train_size = None, n_splits = split_n)
    for train_index, val_index in tscv.split(X):
        X_train_seq, X_val_seq = X[train_index], X[val_index]
        y_train_seq, y_val_seq = y[train_index], y[val_index]
    if print_shape:
        print('Training set shape', X_train_seq.shape, y_train_seq.shape)
        print('Validation set shape', X_val_seq.shape, y_val_seq.shape)
    return X_train_seq, y_train_seq, X_val_seq, y_val_seq

# 10. switch the label_columns to the last 
def switch_y_column(df, column_name):
    c = df[column_name]
    new_df = df.drop(columns=column_name, axis=1)
    new_df.insert(new_df.shape[1], column_name, c)
    return new_df

# 11. get data features
def get_trend_mean(df, date_column_name = 'DATE'):
    df['month'] = df[date_column_name].dt.month
    df['weekofyear'] = df[date_column_name].map(lambda x:x.isocalendar()[1])
    df['dayofweek'] = df[date_column_name].map(lambda x:x.dayofweek+1)
    raw_data_dummy = pd.get_dummies(df, columns=[ 'month', 'weekofyear', 'dayofweek'])
    return raw_data_dummy

# 12. get dummy data
def get_dummy(df, dummy_columns = ['PERIOD']):
    df_dummy = pd.get_dummies(df, columns = dummy_columns)
    return df_dummy








