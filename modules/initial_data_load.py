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

# Load modules for ETFs and Econ Data
from modules.get_etfs_mod import get_etf_data
from modules.econ_mod import get_econ_data


def refresh_data_tables():
    # what is today?
    today = dt.date.today()

    # Checks to see if the files have already been updated today
    if not exists(f"csv_files/trade_dates_{today}.csv"):
        # remove old files from the folder to make room for new files
        files_list = os.listdir("csv_files")
        for i in files_list:
            if i[-3:] == 'csv':
                os.remove(f"csv_files/{i}")

        # function that pull the list of active trading days, and creates flags for end and month and end of week.
        def get_trading_days():
            # what is today?
            today = dt.date.today()
            end = dt.date.today().strftime('%Y-%m-%d')
            start = (today - dt.timedelta(days=20*365)).strftime('%Y-%m-%d')
            
            nyse = mcal.get_calendar('NYSE')
            schedule = nyse.schedule(start_date=start, end_date=end)
            trading_days = nyse.valid_days(start_date=schedule.index[0], end_date=schedule.index[-1])
            def makethisdate(date):
                new = date.date()
                new = str(new)
                new = pd.to_datetime(new)
                return new
            trading_days = list(map(makethisdate, trading_days))
            trading_days = pd.DataFrame(trading_days, columns=["dates"])
            trading_days['weekday'] = trading_days['dates'].dt.dayofweek
            trading_days["end_of_week"] = np.where(trading_days['dates'].dt.dayofweek == 4, True,False)
            trading_days = trading_days.drop(columns=['weekday'])
            trading_days["end_of_month"] = np.where(((trading_days['dates'].dt.month != trading_days['dates'].shift(-1).dt.month) |
                                                     (trading_days['dates']==(trading_days['dates'].iloc[-2]))) &
                                                     (trading_days['dates']!=trading_days['dates'].max()), True,False)
        
        # Export to csv file
            csv_path = f"csv_files/trade_dates_{today}.csv"
            trading_days.to_csv(csv_path)

            return trading_days
        
        def get_spy_data():          
        # Get the list of SPY stocks
            def getsp_list():
                # what is today?
                today = dt.date.today()
            
                # Get list of S&P stocks from wiki
                sp500url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
                data_table = pd.read_html(sp500url)
                # Place list of stocks in a table
                snp_list = data_table[0]
                # remove unneeded columns
                snp_list = snp_list.drop(columns=["CIK","Founded","Headquarters Location"], inplace=False)
                # set index
                snp_list = snp_list.set_index("Symbol",inplace=False)
                # set convert add dates to datetime format
                snp_list['Date added'] = pd.to_datetime(snp_list['Date added'], errors='coerce')
                full_list = snp_list.index.T.to_list()
                return full_list

            # Pull the SPY Stock Data
            # define list
            stocks = getsp_list()
            stocks.append('FLOT')
            stocks.append('SPY')
            # start date is 20 years ago
            end = dt.date.today().strftime('%Y-%m-%d')
            start = (dt.date.today()- dt.timedelta(days=20*365)).strftime('%Y-%m-%d')

            # call api
            stock_data = pdr.get_data_yahoo(stocks, start=start, end=end)
            stock_data = stock_data['Adj Close']

            # Convert datetimes to dates
            dates = stock_data.index.tolist()
            def makethisdate(date):
                new = date.date()
                new = str(new)
                new = pd.to_datetime(new)
                return new
            dates = list(map(makethisdate, dates))
            stock_data.index = dates

        # Export to csv file
            csv_path = f"csv_files/snp_500_stocks_{today}.csv"
            stock_data.to_csv(csv_path)

            return stock_data
            
        def monthly_return_table(stock_data, trading_days):
            # what is today?
            today = dt.date.today()

            # filter trading days to month end
            month_end = trading_days[trading_days['end_of_month']==True]["dates"]

            # filter stock prices on month end dates
            stock_data = stock_data[stock_data.index.isin(month_end)]

            # get monthly returns
            monthly_returns = stock_data.pct_change()
            monthly_returns = monthly_returns.dropna(axis=1, how="all")
            monthly_returns = monthly_returns.dropna(axis=0, how="all")

        # Export to csv file
            csv_path = f"csv_files/monthly_returns_{today}.csv"
            monthly_returns.to_csv(csv_path)

            return monthly_returns

        # run all modules and export
        trading_days = get_trading_days()
        print("trading dates have been loaded")
        stock_data = get_spy_data()
        print("stock data has finished loading")
        monthly_returns = monthly_return_table(stock_data, trading_days)
        print("monthly returns are calculated")
        etf_data = get_etf_data()
        print("ETF data has finished loading")
        econ_data = get_econ_data()
        print("Econ data has loaded")
        
    else:
        print("Data is already up for today.")