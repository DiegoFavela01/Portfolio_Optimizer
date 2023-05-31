# General packages
import pandas as pd
import numpy as np
import datetime as dt
from os.path import exists
import os

# Packages related to API
from pandas_datareader import data as pdr
import pandas_market_calendars as mcal
import yfinance as yf
import scipy as sc
yf.pdr_override()

#turn off warning signs for cleaner code
from warnings import filterwarnings
filterwarnings("ignore")

def get_etf_data():
    # Get today's date
    today = dt.date.today()

    # List of ETF. Each ETF represents one of 11 sectors
    etf_list = ['XLE','XLB','XLI','XLU','VHT','XLF','XLY','VDC','VGT','VOX','IYR']

    # Set Start and End Dates
    end = dt.date.today().strftime('%Y-%m-%d')
    start = (dt.date.today()- dt.timedelta(days=20*365)).strftime('%Y-%m-%d')

    # Use yahoo finance to pull data
    etf_data = pdr.get_data_yahoo(etf_list, start=start, end=end)
    etf_data = etf_data['Adj Close']

    # Convert datetimes to dates
    dates = etf_data.index.tolist()
    def makethisdate(date):
        new = date.date()
        new = str(new)
        new = pd.to_datetime(new)
        return new
    dates = list(map(makethisdate, dates))
    etf_data.index = dates

    learning_df = pd.DataFrame()
    learning_df.index = etf_data.index
    future_y_df = pd.DataFrame()
    future_y_df.index = etf_data.index

    # Create fundamentals for each stock
    for etf in etf_list:
        # Get etf prices
        temp = etf
        future_y_df[temp] = etf_data[etf]
        
        # get 3 day moving average for etf
        temp = etf+'_3ma_pct'
        learning_df[temp] = (etf_data[etf].rolling(window=3).mean()/etf_data[etf]) - 1

        # get 100 day moving average for etf
        temp = etf+'_100ma_pct'
        learning_df[temp] = (etf_data[etf].rolling(window=100).mean()/etf_data[etf]) - 1

        # get upper and lower bollinger bands
        temp = etf+'_top_boll_pct'
        learning_df[temp] = ((etf_data[etf].rolling(window=60).mean()+etf_data[etf].rolling(window=60).std()*2)/etf_data[etf]) - 1
        temp = etf+'_bot_boll_pct'
        learning_df[temp] = ((etf_data[etf].rolling(window=60).mean()-etf_data[etf].rolling(window=60).std()*2)/etf_data[etf]) - 1

        # get monthly fibonacci
        temp = etf+'_fib'
        learning_df[temp] = (etf_data[etf]-etf_data[etf].rolling(window=21).min())/(etf_data[etf].rolling(window=21).max()-etf_data[etf].rolling(window=21).min())

        # Get recent returns
        temp_change = etf_data[etf].pct_change()
        temp = etf+'_cum_month'
        learning_df[temp] = ((temp_change+1).rolling(window=21).apply(np.prod, raw=True)-1)
        
    learning_df = learning_df.append(future_y_df)
    learning_df = learning_df.dropna()

    # Export to csv file
    csv_path = f"../csv_files/etf_{today}.csv"
    learning_df.to_csv(csv_path)

    return learning_df