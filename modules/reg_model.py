# General packages
import pandas as pd
import numpy as np
import datetime as dt

# Packages related to API
from pandas_datareader import data as pdr
import yfinance as yf
import scipy as sc
yf.pdr_override()

# Packages related to machine learning and for nueral networs
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
import tensorflow.keras.backend as K
from keras.models import load_model
from sklearn.preprocessing import StandardScaler

# fix random seed for same reproducibility as my results due to stochastic nature of start point
K.clear_session()
tf.keras.backend.clear_session()
np.random.seed(42)
tf.random.set_seed(42)

def prep_and_train(stock_data, x):
    K.clear_session()
    tf.keras.backend.clear_session()
    np.random.seed(42)
    tf.random.set_seed(42)
    
    temp_table = pd.DataFrame()
    temp_table['price'] = stock_data[[x]]
    temp_table['return'] = temp_table['price'].pct_change()
    temp_table['monthly_std'] = temp_table.groupby(temp_table.index.month)['return'].transform(lambda x: x.std())
    temp_table['4sma_pct_price'] = (temp_table['price'].rolling(window=4).mean()/temp_table['price']) - 1
    temp_table['100sma_pct_price'] = (temp_table['price'].rolling(window=100).mean()/temp_table['price']) - 1
    temp_table['bolling_top_pct'] = ((temp_table['price'].rolling(window=22).mean()+temp_table['price'].rolling(window=22).std()*2)/temp_table['price']) - 1
    temp_table['bolling_bot_pct'] = ((temp_table['price'].rolling(window=22).mean()-temp_table['price'].rolling(window=22).std()*2)/temp_table['price']) - 1

    # Convert datetimes to dates
    dates = temp_table['price'].index.tolist()
    def makethisdate(date):
        new = date.date()
        new = str(new)
        new = pd.to_datetime(new)
        return new
    dates = list(map(makethisdate, dates))
    temp_table.index = dates
    
    # filter dates for only end of month
    today = dt.date.today()
    month_filter = pd.read_csv(f"../csv_files/trade_dates_{today}.csv")
    month_filter = month_filter[month_filter['end_of_month']==True][['dates']]
    temp_table = temp_table[temp_table.index.isin(month_filter["dates"])]
    
    # Create y predictor value
    temp_table['monthly_return'] = temp_table['price'].pct_change()
    temp_table = temp_table.dropna()
    temp_table['y'] = temp_table['monthly_return'].shift(-1)
    
    # Set up Test & Train Data
    end = (temp_table.index.max() - dt.timedelta(days=1)).strftime('%Y-%m-%d')
    
    # Break out test & train by dates
    train = temp_table[:end]
    test = temp_table[end:]
    
    # create x and y tables
    X_train = train.drop(columns=['y','price'])
    y_train = train['y']
    X_test = test.drop(columns=['y','price'])
    y_test = test['y']
    
    # Create a data scaler
    X_train.std(ddof=1)
    scaler = StandardScaler()
    X_scaler = scaler.fit(X_train)
    X_scaler = X_scaler.transform
    
    # Scale train and test
    X_train_scaled = X_scaler(X_train)
    X_test_scaled = X_scaler(X_test)
    
    def nn_reg_model (X_train_scaled, y_train):
        # Set Training epoch end limits, save model with the best fit during epoch testing.
        call = [tf.keras.callbacks.EarlyStopping(monitor='loss', 
                                                      mode='min', 
                                                      patience=35, 
                                                      verbose=0,
                                                     ),
                     tf.keras.callbacks.ModelCheckpoint(filepath='best_nn_model.h5', 
                                                        monitor='loss', 
                                                        mode='min',
                                                        save_best_only=True, 
                                                        initil_value_threshold = .04
                                                        )
                    ]
        # create a loop to ensure that the fit of the machine learning model meets certain requirements
        i=10
        b=10
        while (i >= 1.39) or (b >= .04):
            # fix random seed for same reproducibility as my results due to stochastic nature of start point
            K.clear_session()
            tf.keras.backend.clear_session()
            np.random.seed(42)
            tf.random.set_seed(42)

            # Create nueral network
            nn = Sequential()

            # add input layer
            nn.add(Dense(units=100, input_dim=7, activation="relu"))
            # add first hidden layer
            nn.add(Dense(units=150, activation="relu"))
            # add third hidden layer
            nn.add(Dense(units=5, activation="relu"))
            # Output layer
            nn.add(Dense(units=1, activation="linear"))
            # Compile the model
            nn.compile(loss="mean_squared_error", optimizer='adam', metrics=['mean_squared_error'])
            try:
                # Fit the model
                nn_model = nn.fit(X_train_scaled, y_train, validation_split = 0.2, epochs=300, batch_size=24, callbacks = call, verbose=0)
                b = nn_model.history['loss'][-1]
                i = nn_model.history['val_loss'][-1]
            except:
                # Fit the model
                nn_model = nn.fit(X_train_scaled, y_train, validation_split = 0.2, epochs=300, batch_size=24, callbacks = call, verbose=0)
                b = nn_model.history['loss'][-1]
                i = nn_model.history['val_loss'][-1]

        # load a saved model
        saved_nn_model = load_model('best_nn_model.h5')

        return saved_nn_model, nn_model
    
    saved_nn_model, nn_model = nn_reg_model(X_train_scaled, y_train)
    
    prediction = saved_nn_model.predict(X_test_scaled)
        
    return prediction