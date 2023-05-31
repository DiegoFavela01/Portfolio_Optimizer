# General libraries
import pandas as pd
import numpy as np
import datetime as dt
import matplotlib.pyplot as plt

# API Based Libraries
import pandas_market_calendars as mcal
from pandas_datareader import data as pdr
import yfinance as yf
import scipy as sc
yf.pdr_override()

# Get modules
from initial_data_load import refresh_data_tables
from econ_mod import get_econ_data
from get_etfs_mod import get_etf_data

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

# turn off warning signs for cleaner code
from warnings import filterwarnings
filterwarnings("ignore")

def prep_and_train(stock_data, x):
    K.clear_session()
    tf.keras.backend.clear_session()
    np.random.seed(42)
    tf.random.set_seed(42)
    
    temp_table = stock_data
    temp_table = temp_table[:x]
    
    # Set up Test & Train Data
    train = temp_table[:-1]
    test = temp_table[-1:]
    
    # create x and y tables
    X_train = train.iloc[:,:-11]
    y_train = train.iloc[:,-11:]
    X_test = test.iloc[:,:-11]
    y_test = test.iloc[:,-11:]
    
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
            nn.add(Dense(units=150, input_dim=66, activation="relu"))
            # add first hidden layer
            nn.add(Dense(units=250, activation="relu"))
            # Output layer
            nn.add(Dense(units=11, activation="linear"))
            # Compile the model
            nn.compile(loss="mean_squared_error", optimizer='adam', metrics=['mean_squared_error'])
            try:
                # Fit the model
                nn_model = nn.fit(X_train_scaled, y_train, validation_split = 0.1, epochs=300, batch_size=3, callbacks = call, verbose=0)
                b = nn_model.history['loss'][-1]
                i = nn_model.history['val_loss'][-1]
            except:
                # Fit the model
                nn_model = nn.fit(X_train_scaled, y_train, validation_split = 0.1, epochs=300, batch_size=3, callbacks = call, verbose=0)
                b = nn_model.history['loss'][-1]
                i = nn_model.history['val_loss'][-1]

        # load a saved model
        saved_nn_model = load_model('best_nn_model.h5')

        return saved_nn_model, nn_model
    
    saved_nn_model, nn_model = nn_reg_model(X_train_scaled, y_train)
    
    prediction = saved_nn_model.predict(X_test_scaled)
        
    return prediction