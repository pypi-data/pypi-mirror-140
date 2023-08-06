#----- 16th Feb 2022 -----#
#----- ZhangLe -----------#
#----- Modeling ----------#

from tensorflow import keras
from tensorflow.keras.models import Sequential
from keras.models import load_model
from sklearn.model_selection import KFold
from tensorflow.keras.layers import LSTM, Dropout, Dense, Layer, Concatenate, LayerNormalization, Conv1D, GlobalAveragePooling1D
from tensorflow.keras import Input, Model
from tcn import TCN
from keras.callbacks import EarlyStopping
import tensorflow as tf
import numpy as np
import time
from sklearn.model_selection import train_test_split
import sklearn.linear_model
import sklearn.metrics
import xgboost as xgb
import joblib
import pickle
import optuna
from optuna.integration import TFKerasPruningCallback
from optuna.trial import TrialState
from optuna.visualization import plot_intermediate_values
from optuna.visualization import plot_optimization_history
from optuna.visualization import plot_param_importances
from optuna.visualization import plot_contour
import pandas as pd
from ds_common_tool import suite_data


# 1. lstm (simple)
# update support lstm,tcn,transformer
def model_with_data_split(df, label_column, train_start, train_end,  look_back, look_forward, column_set_index = 0, split_n = 30, n_neurons = [128],
                          transformer_args = [5, 256, 256, 256], print_model_summary = True, dropout = 0.5, epochs = 30, patience = 5, early_stop = True,
                          save_model = False, model_path = 'model.hdf5', checkpoint_path = 'model.ckpt', model_name = 'lstm', enable_optuna = False, epochs_each_try = 10,
                          n_trials = 10, show_loss = True):
  start_time = time.time()
  df = suite_data.switch_y_column(df, column_name=label_column)
  if column_set_index:
    df.set_index(column_set_index, inplace=True)
  train_data = df[train_start : train_end]
  X_train_seq, y_train_seq = suite_data.split_sequence(train_data.values, look_back = look_back, look_forward = look_forward)
  X_train_seq, y_train_seq, X_val_seq, y_val_seq = suite_data.time_split_dataset(X_train_seq, y_train_seq, split_n = split_n)
  n_features = X_train_seq.shape[2]

  def create_lstm_model(trial):
        n_layers = trial.suggest_int("n_layers", 1, 5)
        model = Sequential()
        n_units = np.zeros(n_layers, dtype=np.int64)
        n_units[0] = trial.suggest_int("units_L1", 32, 256)
        dropout = trial.suggest_uniform(f"dropout", 0.01, 0.5)
        if n_layers == 1:
          model.add(LSTM(n_units[0], input_shape=(look_back, n_features), return_sequences=False))
        else:
          model.add(LSTM(n_units[0], input_shape=(look_back, n_features), return_sequences=True))
        for i in range(1, n_layers - 1):
          n_units[i] = trial.suggest_int("units_L"+str(i+1), 32, 256)
          model.add(LSTM(n_units[i], input_shape=(n_units[i - 1], n_features), return_sequences=True))
          model.add(Dropout(dropout))
        if n_layers > 1:
          n_units[-1] = trial.suggest_int("units_L"+str(n_layers), 32, 256)
          model.add(LSTM(n_units[-1], input_shape=(n_units[-2], n_features), return_sequences=False))
        model.add(Dropout(dropout))
        model.add(Dense(look_forward))
        model.compile(loss='mean_squared_error', optimizer='adam', metrics=['mse'])
        return model
  
  def create_tcn_model(trial):
    tcn_batch_size = None
    n_layers = trial.suggest_int("n_layers", 1, 5)
    n_units = np.zeros(n_layers, dtype=np.int64)
    layer_names = []
    for index in range(n_layers):
        layer_names.append('x'+str(index)+'_')
    input_ = Input(batch_shape=(tcn_batch_size, look_back, n_features), name='Input_Layer')
    n_units[0] = trial.suggest_int("units_L1", 32, 256)
    dropout = trial.suggest_uniform(f"dropout", 0.01, 0.5)
    if n_layers == 1:
        layer_names[0] = TCN(nb_filters=n_units[0], kernel_size=2, nb_stacks=2, dilations=[1, 2, 4, 8, 16, 32], 
                           padding='causal', use_skip_connections=True, dropout_rate=dropout, return_sequences=False, 
                           activation='relu', kernel_initializer='he_normal', name = 'TCN_Layer_1', use_batch_norm=True)(input_)
    else:
        layer_names[0] = TCN(nb_filters=n_units[0], kernel_size=2, nb_stacks=2, dilations=[1, 2, 4, 8, 16, 32], 
                           padding='causal', use_skip_connections=True, dropout_rate=dropout, return_sequences=True, 
                           activation='relu', kernel_initializer='he_normal', name = 'TCN_Layer_1', use_batch_norm=True)(input_)
    for index in range(1, n_layers - 1):
        n_units[index] = trial.suggest_int("units_L"+str(index + 1), 32, 256)
        layer_names[index] = TCN(nb_filters=n_units[index], kernel_size=2, nb_stacks=2, dilations=[1, 2, 4, 8, 16, 32], 
                  padding='causal', use_skip_connections=True, dropout_rate=dropout, return_sequences=True, 
                  activation='relu', kernel_initializer='he_normal', name = 'TCN_Layer_' + str(index + 1), use_batch_norm=True)(layer_names[index - 1])  # The TCN layer .
    if n_layers > 1:
        n_units[-1] = trial.suggest_int("units_L"+str(n_layers), 32, 256)
        layer_names[-1] = TCN(nb_filters=n_units[-1], kernel_size=2, nb_stacks=2, dilations=[1, 2, 4, 8, 16, 32], 
                  padding='causal', use_skip_connections=True, dropout_rate=dropout, return_sequences=False, 
                  activation='relu', kernel_initializer='he_normal',
                  name = 'TCN_Layer_' + str(n_layers), use_batch_norm=True)(layer_names[-2])  # The TCN layer .
    output_ = Dense(look_forward, name='Dense_Layer')(layer_names[-1])
    model = Model(inputs=[input_], outputs=[output_], name='TCN_Model_trail')
    model.compile(loss='mean_squared_error', optimizer='adam', metrics=['mse'])
    return model

  def create_transformer_model(trial):
    time_embedding = Time2Vector(look_back)
    n_heads = trial.suggest_int("n_heads", 1, 16)
    d_k =    trial.suggest_int("d_k", 32, 256)
    d_v =    trial.suggest_int("d_v", 32, 256)
    ff_dim = trial.suggest_int("ff_dim", 32, 256)
    attn_layer1 = TransformerEncoder(d_k, d_v, n_heads, ff_dim)
    attn_layer2 = TransformerEncoder(d_k, d_v, n_heads, ff_dim)
    attn_layer3 = TransformerEncoder(d_k, d_v, n_heads, ff_dim)
    in_seq = Input(shape=(look_back, n_features))
    x = time_embedding(in_seq)
    x = Concatenate(axis=-1)([in_seq, x])
    x = attn_layer1((x, x, x))
    x = attn_layer2((x, x, x))
    x = attn_layer3((x, x, x))
    x = GlobalAveragePooling1D(data_format='channels_first')(x)
    dropout = trial.suggest_uniform(f"dropout", 0.01, 0.5)
    x = Dropout(dropout)(x)
    num_hidden = int(trial.suggest_loguniform("hidden", 4, 512))
    # active_func = trial.suggest_categorical('active_function', ['relu', 'entropy'])
    x = Dense(num_hidden, activation='relu')(x)
    x = Dropout(dropout)(x)
    out = Dense(look_forward, activation='linear')(x)
    model = Model(inputs=in_seq, outputs=out)
    model.compile(loss='mse', optimizer='adam', metrics=['mse']) #, 'mape'])
    return model

  def objective(trial):
    keras.backend.clear_session()   # Clear clutter from previous session graphs.
    if model_name == 'lstm':
      model = create_lstm_model(trial)     # Generate our trial model.
    elif model_name == 'tcn':
      model = create_tcn_model(trial)
    elif model_name == 'transformer':
      model = create_transformer_model(trial)
    else:
      model = create_lstm_model(trial)
    history = model.ﬁt(X_train_seq, y_train_seq, epochs=epochs_each_try, batch_size=None, 
             validation_data=(X_val_seq, y_val_seq),
             callbacks=[TFKerasPruningCallback(trial, "val_loss")],
             verbose=1)
    # score = model.evaluate(X_val_seq, y_val_seq, verbose=0)   # Evaluate the model accuracy on the validation set.
    score = history.history["val_mse"][0]  # Evaluate the model loss.
    return score

  if enable_optuna:
      study = optuna.create_study(direction="minimize", sampler=optuna.samplers.TPESampler(), pruner=optuna.pruners.HyperbandPruner())
      study.optimize(objective, n_trials=n_trials)   
      pruned_trials = study.get_trials(deepcopy=False, states=[TrialState.PRUNED])
      complete_trials = study.get_trials(deepcopy=False, states=[TrialState.COMPLETE])
      print("Study statistics: ")
      print("  Number of finished trials: ", len(study.trials))
      print("  Number of pruned trials: ", len(pruned_trials))
      print("  Number of complete trials: ", len(complete_trials))
      if len(complete_trials) == 0: 
        print('No trails are completed yet, please increate the n_trials or epochs_each_try and run again.')
        return None
      else:
        print("Best trial: Value :", study.best_trial.value)
        print("  Params: ")
        for key, value in study.best_trial.params.items():
          print("    {}: {}".format(key, value))

      if model_name in ['lstm', 'tcn']:
        n_neurons = np.zeros(study.best_trial.params['n_layers'], dtype=np.int64)
        for i in range(len(n_neurons)):
          column_name = 'units_L'+str(i+1)
          n_neurons[i] = study.best_trial.params[column_name]
          dropout = study.best_trial.params['dropout']
          # plot_optimization_history(study) # plot_intermediate_values(study) # plot_contour(study) # plot_param_importances(study)
      if model_name in ['transformer']:
        dropout = study.best_trial.params['dropout']
        transformer_args = [study.best_trial.params['n_heads'], study.best_trial.params['d_k'], study.best_trial.params['d_v'], study.best_trial.params['ff_dim'], study.best_trial.params['hidden']]

  if model_name == 'lstm':
    l_Model = lstm_model_custmize(look_back=look_back, look_forward=look_forward, n_features=n_features, dropout=dropout, print_summary=print_model_summary, n_neurons = n_neurons)
  elif model_name == 'tcn':
    l_Model = tcn_model(look_back=look_back, look_forward=look_forward, n_features=n_features, dropout=dropout, print_summary=print_model_summary, n_neurons = n_neurons)
  elif model_name == 'transformer':
    l_Model = transformer_model_custmize(look_back, look_forward, n_features=n_features, n_heads=transformer_args[0], d_k =transformer_args[1], d_v=transformer_args[2], ff_dim=transformer_args[3], dropout=dropout, num_hidden=64, print_summary=True)
  else:
    l_Model = lstm_model_custmize(look_back=look_back, look_forward=look_forward, n_features=n_features, dropout=dropout, print_summary=print_model_summary, n_neurons = n_neurons)
  
  if early_stop == False:
    patience = epochs

  if save_model:
    model_train = train_model(l_Model, X_train_seq, y_train_seq, X_val_seq, y_val_seq, epochs=epochs, early_stop = early_stop, patience=patience, save_model = save_model, model_path=model_path, checkpoint_path=checkpoint_path, show_loss = show_loss)
  else:
    model_train = train_model(l_Model, X_train_seq, y_train_seq, X_val_seq, y_val_seq, epochs=epochs, early_stop = early_stop, patience=patience, save_model = save_model, show_loss = show_loss)
  end_time = time.time()
  print('time cost : ', round((end_time - start_time) / 60, 2), 'min')
  return l_Model


# 2. lstm (customize)
def lstm_model_custmize(look_back, look_forward, n_features, dropout=0.5, print_summary=False, n_neurons = [128]):
  modelLSTM = Sequential(name='LSTM_Model_customized')
  modelLSTM.add(LSTM(n_neurons[0], input_shape=(look_back, n_features), name='LSTM_layer_1', return_sequences=True))
  # modelLSTM.add(Dropout(dropout, name='dropout_layer_1'))
  if len(n_neurons) == 1:
    modelLSTM.add(LSTM(look_forward, name='LSTM_layer_2'))
  for layer_i in range(1, len(n_neurons) - 1):
    modelLSTM.add(LSTM(n_neurons[layer_i], input_shape=(n_neurons[layer_i - 1], n_features), name='LSTM_layer_'+str(layer_i + 1), return_sequences=True))
    # modelLSTM.add(Dropout(dropout, name='dropout_layer_'+str(layer_i + 1)))
  if len(n_neurons) > 1:
    modelLSTM.add(LSTM(n_neurons[-1], input_shape=(n_neurons[-2], 1), name='LSTM_layer_'+str(len(n_neurons))+''))
  modelLSTM.add(Dense(look_forward, name='dense_output_layer'))
  modelLSTM.compile(loss='mean_squared_error', optimizer='adam')
  if print_summary:
    print(modelLSTM.summary())
  return modelLSTM

# 3. train model
# tested
def train_model(model, X_train_seq, y_train_seq, X_val_seq, y_val_seq, 
                epochs=100, early_stop = True, patience=10, 
                save_model = False, model_path='', checkpoint_path='',
                show_loss = True):
  if not early_stop:
    patience = epochs
  early_stopping = EarlyStopping(monitor='val_loss', 
                              min_delta=0, 
                              patience=patience, 
                              verbose=0, 
                              mode='auto', 
                              baseline=None, 
                              restore_best_weights=False)
  if save_model:
    cp_callback = tf.keras.callbacks.ModelCheckpoint(model_path, 
                                                 monitor='val_loss', 
                                                 save_best_only=True, 
                                                 # save_weights_only=True,
                                                 verbose=1)
    history = model.fit(X_train_seq, y_train_seq,
                    epochs=epochs,
                    validation_data=(X_val_seq, y_val_seq),
                    shuffle=True,
                    batch_size=32,
                    verbose=1,
                    callbacks=[early_stopping, cp_callback])
    model.save_weights(checkpoint_path)
    save_model_to_path = tf.keras.callbacks.ModelCheckpoint(model_path, monitor='val_loss', save_best_only=True, verbose=1)
  else:
    history = model.fit(X_train_seq, y_train_seq,
                    epochs=epochs,
                    validation_data=(X_val_seq, y_val_seq),
                    shuffle=True,
                    batch_size=32,
                    verbose=1,
                    callbacks=[early_stopping])
  if show_loss:
    label_list = [i for i in range(0, len(history.history['loss']))]
    suite_data.show_draft_plot(datas = [history.history['loss'], history.history['val_loss']], x_label = label_list, title = 'Loss of Model', legend=['loss', 'val loss'])
  return model

# 4. check matric mae, mape accuracy, mse, rmse
def check_result_metric(y_true, y_pred, methods=['mae'], print_result=True):
  mae, mape, smape = 0, 0, 0
  if 'mae' in methods:
    mae = np.mean(np.abs(y_true - y_pred))
    if print_result:
      print('MAE :', round(mae, 2))
  if 'mape' in methods:
    mape = 100 - np.mean(np.abs(y_true - y_pred) / y_true) * 100
    if print_result:
      print('MAPE accuracy:', round(mape, 2), '%')
  if 'smape' in methods:
    smape = 100 - 2.0 * np.mean(np.abs(y_pred - y_true) / (np.abs(y_pred) + np.abs(y_true))) * 100
    if print_result:
      print('SMAPE accuracy:', round(smape, 2), '%')
  return mae, mape, smape

# 5. tcn model
# add dropout
def tcn_model(look_back, n_features, look_forward, batch_size=None, print_summary=True, n_neurons=[128], dropout=0.5):
  tcn_units = []
  for index in range(len(n_neurons)):
    tcn_units.append('x'+str(index)+'_')
  
  input_ = Input(batch_shape=(batch_size, look_back, n_features), name='Input_Layer')
  if len(n_neurons) == 1:
    tcn_units[0] = TCN(nb_filters=n_neurons[0], kernel_size=2, nb_stacks=2, dilations=[1, 2, 4, 8, 16, 32], 
                   padding='causal', use_skip_connections=True, dropout_rate=dropout, return_sequences=False, 
                   activation='relu', kernel_initializer='he_normal', name = 'TCN_Layer_1', use_batch_norm=True)(input_)
  else:
    tcn_units[0] = TCN(nb_filters=n_neurons[0], kernel_size=2, nb_stacks=2, dilations=[1, 2, 4, 8, 16, 32], 
                   padding='causal', use_skip_connections=True, dropout_rate=dropout, return_sequences=True, 
                   activation='relu', kernel_initializer='he_normal', name = 'TCN_Layer_1', use_batch_norm=True)(input_)
  for index in range(len(tcn_units) - 2):
    tcn_units[index + 1] = TCN(nb_filters=n_neurons[index + 1], kernel_size=2, nb_stacks=2, dilations=[1, 2, 4, 8, 16, 32], 
                  padding='causal', use_skip_connections=True, dropout_rate=dropout, return_sequences=True, 
                  activation='relu', kernel_initializer='he_normal',
                  name = 'TCN_Layer_' + str(index + 2), use_batch_norm=True)(tcn_units[index])  # The TCN layer .
  if len(n_neurons) > 1:
    tcn_units[-1] = TCN(nb_filters=n_neurons[-1], kernel_size=2, nb_stacks=2, dilations=[1, 2, 4, 8, 16, 32], 
                  padding='causal', use_skip_connections=True, dropout_rate=dropout, return_sequences=False, 
                  activation='relu', kernel_initializer='he_normal',
                  name = 'TCN_Layer_' + str(len(n_neurons) + 1), use_batch_norm=True)(tcn_units[-2])  # The TCN layer .
  output_ = Dense(look_forward, name='Dense_Layer')(tcn_units[-1])
  modelTCN = Model(inputs=[input_], outputs=[output_], name='TCN_Model_customized')
  modelTCN.compile(optimizer='adam', loss='mse')
  if print_summary:
    print(modelTCN.summary())
  return modelTCN

# 6. optuna in lstm 
# update model_name
def optuna_nn(epochs_each_try, n_trials, look_back, look_forward, n_features, X_train_seq, y_train_seq, X_val_seq, y_val_seq, print_best_trail = True, model_name = 'lstm'):
  start_time = time.time()
  # model_name in ['lstm', 'tcn']
  BATCH_SIZE = None
  def create_lstm_model(trial):
    n_layers = trial.suggest_int("n_layers", 1, 5)
    model = Sequential()
    n_units = np.zeros(n_layers, dtype=np.int64)
    n_units[0] = trial.suggest_int("units_L1", 32, 256)
    dropout = trial.suggest_uniform(f"dropout", 0.01, 0.5)
    if n_layers == 1:
        model.add(LSTM(n_units[0], input_shape=(look_back, n_features), return_sequences=False))
    else:
        model.add(LSTM(n_units[0], input_shape=(look_back, n_features), return_sequences=True))
    for i in range(1, n_layers - 1):
        # LSTM
        n_units[i] = trial.suggest_int("units_L"+str(i+1), 32, 256)
        model.add(LSTM(n_units[i], input_shape=(n_units[i - 1], n_features), return_sequences=True))
        model.add(Dropout(dropout))
    if n_layers > 1:
        n_units[-1] = trial.suggest_int("units_L"+str(n_layers), 32, 256)
        model.add(LSTM(n_units[-1], input_shape=(n_units[-2], n_features), return_sequences=False))
    model.add(Dropout(dropout))
    model.add(Dense(look_forward))
    model.compile(loss='mean_squared_error', optimizer='adam', metrics=['mse'])
    return model

  def create_tcn_model(trial):
    tcn_batch_size = None
    n_layers = trial.suggest_int("n_layers", 1, 5)
    n_units = np.zeros(n_layers, dtype=np.int64)
    
    layer_names = []
    for index in range(n_layers):
        layer_names.append('x'+str(index)+'_')
    
    input_ = Input(batch_shape=(tcn_batch_size, look_back, n_features), name='Input_Layer')
    n_units[0] = trial.suggest_int("units_L1", 32, 256)
    dropout = trial.suggest_uniform(f"dropout", 0.01, 0.5)
    if n_layers == 1:
        layer_names[0] = TCN(nb_filters=n_units[0], kernel_size=2, nb_stacks=2, dilations=[1, 2, 4, 8, 16, 32], 
                           padding='causal', use_skip_connections=True, dropout_rate=dropout, return_sequences=False, 
                           activation='relu', kernel_initializer='he_normal', name = 'TCN_Layer_1', use_batch_norm=True)(input_)
    else:
        layer_names[0] = TCN(nb_filters=n_units[0], kernel_size=2, nb_stacks=2, dilations=[1, 2, 4, 8, 16, 32], 
                           padding='causal', use_skip_connections=True, dropout_rate=dropout, return_sequences=True, 
                           activation='relu', kernel_initializer='he_normal', name = 'TCN_Layer_1', use_batch_norm=True)(input_)
    
    for index in range(1, n_layers - 1):
        n_units[index] = trial.suggest_int("units_L"+str(index + 1), 32, 256)
        layer_names[index] = TCN(nb_filters=n_units[index], kernel_size=2, nb_stacks=2, dilations=[1, 2, 4, 8, 16, 32], 
                  padding='causal', use_skip_connections=True, dropout_rate=dropout, return_sequences=True, 
                  activation='relu', kernel_initializer='he_normal', name = 'TCN_Layer_' + str(index + 1), use_batch_norm=True)(layer_names[index - 1])  # The TCN layer .
    
    if n_layers > 1:
        n_units[-1] = trial.suggest_int("units_L"+str(n_layers), 32, 256)
        layer_names[-1] = TCN(nb_filters=n_units[-1], kernel_size=2, nb_stacks=2, dilations=[1, 2, 4, 8, 16, 32], 
                  padding='causal', use_skip_connections=True, dropout_rate=dropout, return_sequences=False, 
                  activation='relu', kernel_initializer='he_normal',
                  name = 'TCN_Layer_' + str(n_layers), use_batch_norm=True)(layer_names[-2])  # The TCN layer .
    
    output_ = Dense(look_forward, name='Dense_Layer')(layer_names[-1])
    model = Model(inputs=[input_], outputs=[output_], name='TCN_Model_trail')
    model.compile(loss='mean_squared_error', optimizer='adam', metrics=['mse'])
    return model

  def create_transformer_model(trial):
    '''Initialize time and transformer layers'''
    time_embedding = Time2Vector(look_back)
    n_heads = trial.suggest_int("n_heads", 1, 16)
    d_k =    trial.suggest_int("d_k", 32, 256)
    d_v =    trial.suggest_int("d_v", 32, 256)
    ff_dim = trial.suggest_int("ff_dim", 32, 256)
    attn_layer1 = TransformerEncoder(d_k, d_v, n_heads, ff_dim)
    attn_layer2 = TransformerEncoder(d_k, d_v, n_heads, ff_dim)
    attn_layer3 = TransformerEncoder(d_k, d_v, n_heads, ff_dim)
    '''Construct model'''
    in_seq = Input(shape=(look_back, n_features))
    x = time_embedding(in_seq)
    x = Concatenate(axis=-1)([in_seq, x])
    x = attn_layer1((x, x, x))
    x = attn_layer2((x, x, x))
    x = attn_layer3((x, x, x))
    x = GlobalAveragePooling1D(data_format='channels_first')(x)
    dropout = trial.suggest_uniform(f"dropout", 0.01, 0.5)
    x = Dropout(dropout)(x)
    num_hidden = int(trial.suggest_loguniform("hidden", 4, 512))
    # active_func = trial.suggest_categorical('active_function', ['relu', 'entropy'])
    x = Dense(num_hidden, activation='relu')(x)
    x = Dropout(dropout)(x)
    out = Dense(look_forward, activation='linear')(x)

    model = Model(inputs=in_seq, outputs=out)
    model.compile(loss='mse', optimizer='adam', metrics=['mse']) #, 'mape'])
    return model

  def objective(trial):
    keras.backend.clear_session()   # Clear clutter from previous session graphs.
    if model_name == 'lstm':
      model = create_lstm_model(trial)     # Generate our trial model.
    elif model_name == 'tcn':
      model = create_tcn_model(trial)
    elif model_name == 'transformer':
      model = create_transformer_model(trial)
    else:
      model = create_lstm_model(trial)
    history = model.ﬁt(X_train_seq, y_train_seq, epochs=epochs_each_try, batch_size=BATCH_SIZE, 
             validation_data=(X_val_seq, y_val_seq),
             callbacks=[TFKerasPruningCallback(trial, "val_loss")],
             verbose=1)
    # score = model.evaluate(X_val_seq, y_val_seq, verbose=0)   # Evaluate the model accuracy on the validation set.
    score = history.history["val_mse"][0]  # Evaluate the model loss.
    return score
  
  study = optuna.create_study(direction="minimize",
                            sampler=optuna.samplers.TPESampler(), 
                            pruner=optuna.pruners.HyperbandPruner())
  study.optimize(objective, n_trials=n_trials)   
  pruned_trials = study.get_trials(deepcopy=False, states=[TrialState.PRUNED])
  complete_trials = study.get_trials(deepcopy=False, states=[TrialState.COMPLETE])
  if print_best_trail:
    print("Study statistics: ")
    print("  Number of finished trials: ", len(study.trials))
    print("  Number of pruned trials: ", len(pruned_trials))
    print("  Number of complete trials: ", len(complete_trials))
  if len(complete_trials) == 0: 
    print('No trails are completed yet, please increate the n_trials or epochs_each_try and run again.')
    end_time = time.time()
    print('time cost : ', round((end_time - start_time) / 60, 2), 'min')
    return [0], 0
  else:
    if print_best_trail:
      print("Best trial: Value :", study.best_trial.value)
      print("  Params: ")
      for key, value in study.best_trial.params.items():
        print("    {}: {}".format(key, value))
    n_neurons = [0]
    dropout, n_heads, d_k, d_v, ff_dim, hidden   = 0, 0,0,0,0,0
    if model_name in ['lstm', 'tcn']:
      n_neurons = np.zeros(study.best_trial.params['n_layers'], dtype=np.int64)
      for i in range(len(n_neurons)):
        column_name = 'units_L'+str(i+1)
        n_neurons[i] = study.best_trial.params[column_name]
        dropout = study.best_trial.params['dropout']
        # plot_optimization_history(study) # plot_intermediate_values(study) # plot_contour(study) # plot_param_importances(study)
    if model_name in ['transformer']:
        dropout = study.best_trial.params['dropout']
        n_heads, d_k, d_v, ff_dim, hidden = study.best_trial.params['n_heads'], study.best_trial.params['d_k'], study.best_trial.params['d_v'], study.best_trial.params['ff_dim'], study.best_trial.params['hidden']
    end_time = time.time()
    print('time cost : ', round((end_time - start_time) / 60, 2), 'min')
    return n_neurons, dropout, n_heads, d_k, d_v, ff_dim, hidden

class Time2Vector(Layer):
    def __init__(self, seq_len, **kwargs):
        super(Time2Vector, self).__init__()
        self.seq_len = seq_len

    def build(self, input_shape):
        '''Initialize weights and biases with shape (batch, seq_len)'''
        self.weights_linear = self.add_weight(name='weight_linear',
                                shape=(int(self.seq_len),),
                                initializer='uniform',
                                trainable=True)
        self.bias_linear = self.add_weight(name='bias_linear',
                                shape=(int(self.seq_len),),
                                initializer='uniform',
                                trainable=True)

        self.weights_periodic = self.add_weight(name='weight_periodic',
                                shape=(int(self.seq_len),),
                                initializer='uniform',
                                trainable=True)
        self.bias_periodic = self.add_weight(name='bias_periodic',
                                shape=(int(self.seq_len),),
                                initializer='uniform',
                                trainable=True)

    def call(self, x):
        '''Calculate linear and periodic time features'''
        x = tf.math.reduce_mean(x[:,:,1:], axis=-1) 
        time_linear = self.weights_linear * x + self.bias_linear # Linear time feature
        time_linear = tf.expand_dims(time_linear, axis=-1) # Add dimension (batch, seq_len, 1)
        time_periodic = tf.math.sin(tf.multiply(x, self.weights_periodic) + self.bias_periodic)
        time_periodic = tf.expand_dims(time_periodic, axis=-1) # Add dimension (batch, seq_len, 1)
        return tf.concat([time_linear, time_periodic], axis=-1) # shape = (batch, seq_len, 2)
        
    def get_config(self): # Needed for saving and loading model with custom layer
        config = super().get_config().copy()
        config.update({'seq_len': self.seq_len})
        return config

class SingleAttention(Layer):
    def __init__(self, d_k, d_v):
        super(SingleAttention, self).__init__()
        self.d_k = d_k
        self.d_v = d_v

    def build(self, input_shape):
        self.query = Dense(self.d_k, 
                       input_shape=input_shape, 
                       kernel_initializer='glorot_uniform', 
                       bias_initializer='glorot_uniform')
        self.key = Dense(self.d_k, 
                     input_shape=input_shape, 
                     kernel_initializer='glorot_uniform', 
                     bias_initializer='glorot_uniform')
        self.value = Dense(self.d_v, 
                       input_shape=input_shape, 
                       kernel_initializer='glorot_uniform', 
                       bias_initializer='glorot_uniform')

    def call(self, inputs): # inputs = (in_seq, in_seq, in_seq)
        q = self.query(inputs[0])
        k = self.key(inputs[1])

        attn_weights = tf.matmul(q, k, transpose_b=True)
        attn_weights = tf.map_fn(lambda x: x/np.sqrt(self.d_k), attn_weights)
        attn_weights = tf.nn.softmax(attn_weights, axis=-1)
    
        v = self.value(inputs[2])
        attn_out = tf.matmul(attn_weights, v)
        return attn_out

class MultiAttention(Layer):
    def __init__(self, d_k, d_v, n_heads):
        super(MultiAttention, self).__init__()
        self.d_k = d_k
        self.d_v = d_v
        self.n_heads = n_heads
        self.attn_heads = list()

    def build(self, input_shape):
        for n in range(self.n_heads):
            self.attn_heads.append(SingleAttention(self.d_k, self.d_v))  
    
        # input_shape[0]=(batch, seq_len, 7), input_shape[0][-1]=7 
        self.linear = Dense(input_shape[0][-1], 
                        input_shape=input_shape, 
                        kernel_initializer='glorot_uniform', 
                        bias_initializer='glorot_uniform')

    def call(self, inputs):
        attn = [self.attn_heads[i](inputs) for i in range(self.n_heads)]
        concat_attn = tf.concat(attn, axis=-1)
        multi_linear = self.linear(concat_attn)
        return multi_linear 

class TransformerEncoder(Layer):
    def __init__(self, d_k, d_v, n_heads, ff_dim, dropout=0.1, **kwargs):
        super(TransformerEncoder, self).__init__()
        self.d_k = d_k
        self.d_v = d_v
        self.n_heads = n_heads
        self.ff_dim = ff_dim
        self.attn_heads = list()
        self.dropout_rate = dropout

    def build(self, input_shape):
        self.attn_multi = MultiAttention(self.d_k, self.d_v, self.n_heads)
        self.attn_dropout = Dropout(self.dropout_rate)
        self.attn_normalize = LayerNormalization(input_shape=input_shape, epsilon=1e-6)

        self.ff_conv1D_1 = Conv1D(filters=self.ff_dim, kernel_size=1, activation='relu')
        # input_shape[0]=(batch, seq_len, 7), input_shape[0][-1] = 7 
        self.ff_conv1D_2 = Conv1D(filters=input_shape[0][-1], kernel_size=1) 
        self.ff_dropout = Dropout(self.dropout_rate)
        self.ff_normalize = LayerNormalization(input_shape=input_shape, epsilon=1e-6)    

    def call(self, inputs): # inputs = (in_seq, in_seq, in_seq)
        attn_layer = self.attn_multi(inputs)
        attn_layer = self.attn_dropout(attn_layer)
        attn_layer = self.attn_normalize(inputs[0] + attn_layer)

        ff_layer = self.ff_conv1D_1(attn_layer)
        ff_layer = self.ff_conv1D_2(ff_layer)
        ff_layer = self.ff_dropout(ff_layer)
        ff_layer = self.ff_normalize(inputs[0] + ff_layer)
        return ff_layer 

    def get_config(self): # Needed for saving and loading model with custom layer
        config = super().get_config().copy()
        config.update({'d_k': self.d_k,
                   'd_v': self.d_v,
                   'n_heads': self.n_heads,
                   'ff_dim': self.ff_dim,
                   'attn_heads': self.attn_heads,
                   'dropout_rate': self.dropout_rate})
        return config

def transformer_model_custmize(look_back, look_forward, n_features, n_heads = 5, d_k = 256, d_v = 256, ff_dim = 256, dropout = 0.5, num_hidden = 64, print_summary=True):
    '''Initialize time and transformer layers'''
    time_embedding = Time2Vector(look_back)
    attn_layer1 = TransformerEncoder(d_k, d_v, n_heads, ff_dim)
    attn_layer2 = TransformerEncoder(d_k, d_v, n_heads, ff_dim)
    attn_layer3 = TransformerEncoder(d_k, d_v, n_heads, ff_dim)
    '''Construct model'''
    in_seq = Input(shape=(look_back, n_features))
    x = time_embedding(in_seq)
    x = Concatenate(axis=-1)([in_seq, x])
    x = attn_layer1((x, x, x))
    x = attn_layer2((x, x, x))
    x = attn_layer3((x, x, x))
    x = GlobalAveragePooling1D(data_format='channels_first')(x)
    x = Dropout(dropout)(x)
    # active_func = trial.suggest_categorical('active_function', ['relu', 'entropy'])
    x = Dense(num_hidden, activation='relu')(x)
    x = Dropout(dropout)(x)
    out = Dense(look_forward, activation='linear')(x)
    model = Model(inputs=in_seq, outputs=out)
    model.compile(loss='mse', optimizer='adam', metrics=['mse']) #, 'mape'])
    if print_summary:
      print(model.summary())
    return model

def linear_model_with_optuna(df, label_column, column_set_index = 0, start_index = '', end_index = '', print_data_shape = True, save_model = False, model_path = '', enable_optuna = True, n_trials = 20, model_name = 'elasticnet', alpha = 0.1, l1 = 0.5):
  start_time = time.time()
  df = suite_data.switch_y_column(df, column_name=label_column)
  if column_set_index:
    df.set_index(column_set_index, inplace=True)
    df = df[start_index : end_index]
  X_train, X_val, y_train, y_val = train_test_split(df.iloc[:,:-1].values, df.iloc[:][label_column].values, train_size = 0.8, test_size = 0.2)
  if print_data_shape:
    print("X shape: ",df.iloc[:,:-1].shape,",  X train shape: ", X_train.shape,", X validation shape: ", X_val.shape)
    print("y shape:",df[label_column].shape,", Y train shape:", y_train.shape,", Y validation shape: ",y_val.shape)
  if enable_optuna:
    def objective(trial):
      regression_method = trial.suggest_categorical('regression_method', ('ridge', 'lasso', 'elasticnet'))
      alpha = trial.suggest_uniform('alpha', 0.0, 200.0)
      l1_ratio = trial.suggest_uniform('l1_ratio', 0.0, 1.0)
      if regression_method == 'ridge':
        model = sklearn.linear_model.Ridge(alpha=alpha)
      elif regression_method == 'lasso':
        model = sklearn.linear_model.Lasso(alpha=alpha)
      else:
        model = sklearn.linear_model.ElasticNetCV(alphas=[0, alpha], l1_ratio=[0, l1_ratio], normalize=True)
      model.fit(X_train, y_train)
      y_pred = model.predict(X_val)
      error = sklearn.metrics.mean_squared_error(y_val, y_pred)
      return error
    study = optuna.create_study(direction='minimize')
    study.optimize(objective, n_trials=n_trials)
    print('Minimum mean squared error: ' + str(study.best_value))
    print('Best parameter: ' + str(study.best_params))
    model_name = study.best_params['regression_method']
    alpha = study.best_params['alpha']
    l1 = study.best_params['l1_ratio']
  model = linear_model_customize(X_train, X_val, y_train, y_val, save_model = save_model, model_path = model_path, model_name = model_name, alpha = alpha, l1 = l1)
  end_time = time.time()
  print('time cost : ', round((end_time - start_time) / 60, 2), 'min')
  return model

def linear_model_customize(X_train, X_val, y_train, y_val, save_model = False, model_path = '', model_name = 'lasso', alpha = 1.0, l1 = 0.5):
  if model_name == 'lasso':
    model = sklearn.linear_model.Lasso(alpha=alpha)
  elif model_name == 'ridge':
    model = sklearn.linear_model.Ridge(alpha=alpha)
  else:
    model = sklearn.linear_model.ElasticNetCV(alphas=[alpha], l1_ratio=[l1], normalize=True)
  model.fit(X_train, y_train)
  score =model.score(X_val,y_val) 
  print('score: ', score)
  if save_model:
    pickle.dump(model, open(model_path, 'wb')) # .sav
  return model

def xgb_with_optuna(df, label_column, column_set_index = 0, start_index = '0', end_index = '1', save_model = False, model_path = '', enable_optuna = True, n_trials =10):
  start_time = time.time()
  if column_set_index:
    df.set_index(column_set_index, inplace=True)
    df = df[start_index : end_index]
  df = suite_data.switch_y_column(df, column_name=label_column)
  X_train, X_val, y_train, y_val = train_test_split(df.iloc[:,:-1].values, df.iloc[:][label_column].values, train_size = 0.8, test_size = 0.2)
  colsample_bytree = 0.6
  learning_rate = 0.01
  max_depth = 3
  min_child_weight = 1
  n_estimators = 1000
  subsample = 0.95
  nthread = 30
  if enable_optuna:
    def objective(trial):
      colsample_bytree = trial.suggest_uniform(f"colsample_bytree", 0.01, 0.5)
      learning_rate = trial.suggest_uniform(f"learning_rate", 0.01, 1)
      max_depth  = trial.suggest_int("max_depth", 1, 20)
      min_child_weight = trial.suggest_int("min_child_weight", 1, 20)
      n_estimators = trial.suggest_int("n_estimators", 1, 2000)
      subsample = trial.suggest_uniform(f"subsample", 0.01, 1)
      nthread = trial.suggest_int("nthread", 1, 30)
      model = xgb.XGBRegressor(nthread = nthread,
                               colsample_bytree = colsample_bytree, 
                               gamma = 0,                 
                               learning_rate = learning_rate,
                               max_depth = max_depth,
                               min_child_weight = min_child_weight,
                               n_estimators = n_estimators,                                                                    
                               subsample = subsample,
                               seed = 42)
      folds = KFold(n_splits=5, shuffle=False)
      for fold_, (trn_idx, val_idx) in enumerate(folds.split(X_train)):
        model.fit(X_train[trn_idx], y_train[trn_idx])
      y_pred = model.predict(X_val)
      error = sklearn.metrics.mean_squared_error(y_val, y_pred)
      return error
    study = optuna.create_study(direction='minimize')
    study.optimize(objective, n_trials=n_trials)
    print('Minimum mean squared error: ' + str(study.best_value))
    print('Best parameter: ' + str(study.best_params))
    colsample_bytree = study.best_params['colsample_bytree']
    learning_rate = study.best_params['learning_rate']
    max_depth = study.best_params['max_depth']
    min_child_weight = study.best_params['min_child_weight']
    n_estimators = study.best_params['n_estimators']
    subsample = study.best_params['subsample']
    nthread = study.best_params['nthread']
  model = xgb.XGBRegressor(nthread = nthread,
                           colsample_bytree = colsample_bytree, 
                           gamma = 0,                 
                           learning_rate = learning_rate,
                           max_depth = max_depth,
                           min_child_weight = min_child_weight,
                           n_estimators = n_estimators,                                                                    
                           subsample = subsample,
                           seed = 42)
  evalset = [(X_train, y_train), (X_val, y_val)]
  model.fit(X_train, y_train, eval_set=evalset)
  if save_model:
    joblib.dump(model, model_path) # '.pkl' 
  end_time = time.time()
  print('time cost : ', round((end_time - start_time) / 60, 2), 'min')
  return model

# test and show some result
def test_result(df, target_column , model_path=[], model_type=[], look_back = 1, look_forward = 1, display_metrix = True, display_plot = True, display_title = '', display_legend = ['pred', 'real']):
  df = suite_data.switch_y_column(df, target_column)
  x_test, y_test = suite_data.split_sequence(df.values, look_back = look_back, look_forward = look_forward, print_shape = True)
  pred_list = []
  metrix_list = []
  real_label = df[-look_forward:]
  for index in range(len(model_path)):
    if model_type[index] in ['lstm', 'tcn', 'transformer']:
      model_file = model_path[index]
      pred_y = model_file.predict(x_test)
      df_base = pd.DataFrame(np.zeros(look_forward, dtype=np.int64))
      for i in range(0, look_forward):
        df_base[i] = pd.DataFrame(pred_y[-1-i])
      df_base['sum'] = df_base.sum(axis = 1)
      df_base['pred'] = df_base['sum'] / look_forward
      pred_list.append(df_base['pred'])
      if display_metrix:
        print('metrix of ', display_legend[index])
      mae, mape, smape = check_result_metric(real_label[target_column].values, df_base['pred'].values, methods=['mae', 'mape', 'smape'], print_result=display_metrix)
      metrix_list.append({'mae': mae, 'mape': mape, 'smape': smape})  
  for index in range(len(model_path)):
    if model_type[index] in ['linear', 'xgb']:
      model_file = model_path[index]
      pred = model_file.predict(df.iloc[-look_forward:, :-1].values)
      pred_list.append(pred)
      if display_metrix:
        print('metrix of ', display_legend[index])
      mae, mape, smape = check_result_metric(pred, df.iloc[-look_forward:, -1].values, methods=['mae', 'mape', 'smape'], print_result=display_metrix)
      metrix_list.append({'mae': mae, 'mape': mape, 'smape': smape})  
  pred_list.append(real_label[target_column])
  # print(len(pred_list))
  if display_plot:
    suite_data.show_draft_plot(datas = pred_list, 
                           x_label = real_label.index, 
                           title = display_title, 
                           legend = display_legend, 
                           picture_size=[18, 5])
  return pred_list, metrix_list

# type can be: lstm, tcn, transformer, linear, xgb
def load_model_by_type(model_path = '', model_type = 'lstm'):
  if model_type in ['lstm', 'tcn', 'transformer']:
    model_file  = load_model(model_path, custom_objects={'TCN': TCN, 'Time2Vector': Time2Vector, 'TransformerEncoder': TransformerEncoder})
  if model_type in ['linear', 'xgb']:
    model_file = pickle.load(open(model_path, "rb"))
  return model_file


def predict_result(predict_data_list = [] , model_path=[], model_type=['lstm']):
  predict_list = []
  for index in range(len(model_path)):
    if model_type[index] in ['lstm', 'tcn', 'transformer']:
      model_file = model_path[index]
      prediction = model_file.predict(predict_data_list[index])
      predict_list.append(prediction[-1])
    if model_type[index] in ['linear', 'xgb']:
      model_file = model_path[index]
      prediction = model_file.predict(predict_data_list[index])
      predict_list.append(prediction)
  return predict_list

