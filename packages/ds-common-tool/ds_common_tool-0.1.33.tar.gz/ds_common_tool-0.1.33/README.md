## Functions included in data processing:

### 1. remove outlier  
### suite_data.remove_outlier(df, column_name, n_outlier=0.25)    
|parameter|data type|description|default value|
|:---|:---|:---|:---| 
|**df**|dataframe|which need to filter the outlier|-|  
|**column_name**|string|column which need to filter the outlier|-|
|**n_outlier**|float|range (0, 1), quantile number|0.25|
|**return**|dataframe|new dataframe|-|  
  
example:  
```
from ds_common_tool import suite_data  
  
new_df = suite_data.remove_outlier(df, 'column_name', 0.25)
```  
  
### 2. Transfor period column into datetime   
### suite_data.add_period_to_time(df, date_column_name='DATE', period_column_name='PERIOD', period_minutes=30)  
|parameter|data type|description|default value|  
|:---|:---|:---|:---|  
|**df**|dataframe|which need to transfer period columns into datetime|-|  
|**date_column_name**|string|date column|'DATE'|  
|**period_column_name**|string|period column|'PERIOD'|  
|**period_minutes**|int|time period|30|  
|**return**|dataframe|new dataframe|-|  

example:  
```
from ds_common_tool import suite_data  
  
new_df = suite_data.add_period_to_time(df, date_column_name='DATE', period_column_name='PERIOD', period_minutes=30) 
```  
  
### 3. split sequences for lstm/tcn/transformer model  
### suite_data.split_sequence(sequence, look_back = 30, look_forward = 30, print_shape = True)  
  
|parameter|data type|description|default value|  
|:---|:---|:---|:---|  
|**sequence**||nparray data with [0:-2] columns as feature, [-1] column as label, all elements should be float only.|-|  
|**look_back**|int|input size|-|  
|**look_forward**|int|output size|-|  
|**print_shape**|boolean|True: print shape of seq_x and seq_y|True|    
|**return**|seq_x, seq_y||-|  
  
example:  
```
from ds_common_tool import suite_data  
  
lstmModel = suite_data.split_sequence(sequence, look_back = 31, look_forward = 28, print_shape = True)
```  
  
### 4. plot multiple data with label
### suite_data.show_draft_plot(datas, x_label, title, legend, picture_size=[18, 5])
  
|parameter|data type|description|default value|  
|:---|:---|:---|:---|  
|**datas**|nparray[]|list of data nparray , e.g [ real_data[], redict_data[], thrid_data[] ] |-|  
|**x_label**|nparray[]|index or label array, ***same length as the list in datas***, e.g date[] |-|  
|**title**|string|name of the plot|''|  
|**picture_size**|[int, int]|size of the plot|[18,5]|     
|**return**|-|no return|-|  
  
example:  
```
from ds_common_tool import suite_data  
  
lstmModel = dasuite_data.show_draft_plot(datas = [df['column1'], df['column2']], x_label = df.index, title='Compare 2 features values', legend=['column1_data', 'column2_data'], picture_size=[18, 5])
``` 
  
### 5. get N days rolling mean, max, min, median  
### suite_data.get_n_rolling(df, target_column_name, n = 30, method = 'mean')  
  
|parameter|data type|description|default value|  
|:---|:---|:---|:---|  
|**df**|DataFrame|dataframe need to do the rolling|-|  
|**target_column_name**|string|target column need to do rolling|-|  
|**n**|int|window size|30|  
|**method**|string|accept 'mean', 'max', 'min', 'median'|'mean'|     
|**return**|DataFrame|dataframe with new column|-|  
  
  
### 6. read external data files   
### suite_data.read_data_external(filepath_name,  main_df, date_column = 'DATE', fillna_limit_n = 5)  
  
|parameter|data type|description|default value|  
|:---|:---|:---|:---|  
|**filepath_name**|string|filename with path, e.g. 'data/Data1.csv'|-|  
|**main_df**|DataFrame|main dataframe which need to be merge the index with|-| 
|**date_column**|string[]|column which merge on, note: main_df and reading file need including the same column, e.g. 'DATE' |'DATE'|   
|**fillna_limit_n**|int|limit number when fillna by rows.|5|     
|**return**|DataFrame|merged dataframe|-| 
   
### 7. merge dataframe
### suite_data.merge_dfs(df_list = [], on_column = 'DATE')
  
|parameter|data type|description|default value|  
|:---|:---|:---|:---|  
|**df_list**|DataFrame[]|dataframes need to be merged, ***NOTE:*** first item should be the main target df, e.g. [df_main, df1, df2, df3, ...] |-|  
|**on_column**|string|column merge on|'DATE'|        
|**return**|DataFrame|merged dataframe|-| 
  
### 10. switch the label_columns to the last 
### suite_data.switch_y_column(df, column_name)  
  
  
## Functions included in model:
### 1. lstm model
### suite_model.lstm_model(look_back, look_forward, n_features, dropout=0.5, print_summary=False, size = 'small')  
  
|parameter|data type|description|default value|  
|:---|:---|:---|:---|  
|**size**|string|size of lstm model, [small, medium, large], small: 1 layer with neurons number 128, medium: 1 layer with neurons number 256, large: with 2 layers, first layer neurons number 258, second layer neurons number 128. |'small'|  
|**look_back**|int|input size|-|  
|**look_forward**|int|output size|-|  
|**n_features**|int|number of features|-|  
|**dropout**|float|range (0,1)|0.5|   
|**print_summary**|boolean|True: will print out model summary. |False|  
|**return**|Model|lstm model|-|  
  
example:  
```
from ds_common_tool import suite_model  
  
lstmModel = suite_model.lstm_model(look_back=30, look_forward=30, n_features=4, dropout=0.5, print_summary=False, size = 'small')
```  
### 2. lstm model customized  
### suite_model.lstm_model_custmize(look_back, look_forward, n_features, dropout=0.5, print_summary=False, n_neurons = [128])  
  
|parameter|data type|description|default value|  
|:---|:---|:---|:---|  
|**look_back**|int|input size|-|  
|**look_forward**|int|output size|-|  
|**n_features**|int|number of features|-|  
|**dropout**|float|range (0,1)|0.5| 
|**n_neurons**|int[]|neurons number of each layer, eg. [256, 128, 64]|[128]| 
|**print_summary**|boolean|True: will print out model summary. |False|    
|**return**|Model|lstm model|-|  
  
example:    
```
from ds_common_tool import suite_model  
  
lstmModel = suite_model.lstm_model_custmize(look_back=30, look_forward=30, n_features=4, dropout=0.5, print_summary=False, n_neurons = [128])
```  

### 3. train the model  
### suite_model.train_model(model, X_train_seq, y_train_seq, X_val_seq, y_val_seq, epochs=100, early_stop = True, patience=10, save_model = False, model_path='', checkpoint_path='', show_loss = True)  
   
|parameter|data type|description|default value|  
|:---|:---|:---|:---|  
|**model**|int|input size|-|  
|**X_train_seq**|same type as model||-|  
|**y_train_seq**|same type as model||-|  
|**X_val_seq**|same type as model||-| 
|**y_val_seq**|same type as model||-| 
|**epochs**|int epochs for traning||100|    
|**early_stop**|boolean|True: use early stop|True|     
|**patience**|int| range(10, +), patience if set the early_stop as True|10|  
|**save_model**|boolean|True: save model and weight|False|  
|**model_path**|string|path where save the model|''|  
|**checkpoint_path**|string|path where save the checkpoint(weight)|''|  
|**show_loss**|boolean|True: plot loss for each epoch|True|  
|**return**|Model|updated model|-|  
  
example:    
```
from ds_common_tool import suite_model  
  
lstmModel = suite_model.train_model(lstmModel, X_train_seq, y_train_seq, X_val_seq, y_val_seq, 
                          epochs=3, 
                          early_stop = True, 
                          patience=3, 
                          save_model = False, 
                          show_loss = True)
```  
  
## [pypi](https://pypi.org/project/ds-common-tool/#description)

