# General libraries
import pandas as pd
import numpy as np
import datetime as dt
import matplotlib.pyplot as plt
import streamlit as st
from os.path import exists
import os

# API Based Libraries
import pandas_market_calendars as mcal
from pandas_datareader import data as pdr
import yfinance as yf
import scipy as sc
yf.pdr_override()

# module that refresh data
from modules.initial_data_load import refresh_data_tables
# import function for portfolio optimizer
from modules.sh_optimizer import portfolio_perform, port_std, neg_sharperatio, max_sf

#turn off warning signs for cleaner code
from warnings import filterwarnings
filterwarnings("ignore")

def optimizer_strategy():
    # Get today's date for reference
    today = dt.date.today()

    if not exists(f"csv_files/optimizer_strategy_returns_{today}.csv"):
        # Create a dataframe to store portfolio return data
        final_port_return = pd.DataFrame(columns=['port_return'])

        # Create Global variable to update on status
        global opt_pct
        opt_pct = 0
        my_bar = st.progress(0, text="Model Loading")

        # Check to see if data has been updated
        refresh_data_tables()

        # pull monthly returns
        monthly_returns_df = pd.read_csv(f"csv_files/monthly_returns_{today}.csv", index_col=0, parse_dates=True, infer_datetime_format=True)
        offset_returns = monthly_returns_df.shift(-1)

        # get full stock data
        stock_data = pd.read_csv(f"csv_files/snp_500_stocks_{today}.csv", index_col=0, parse_dates=True, infer_datetime_format=True)
        # Convert datetimes to dates
        dates = stock_data.index.tolist()
        def makethisdate(date):
            new = date.date()
            new = str(new)
            new = pd.to_datetime(new)
            return new
        dates = list(map(makethisdate, dates))
        stock_data.index = dates

        # Create a benchmark
        bench = stock_data[['SPY']].pct_change()

        # get list of trading dates
        trading_days = pd.read_csv(f"csv_files/trade_dates_{today}.csv", index_col=0)
        # get end of months for reference
        month_ends = trading_days[trading_days['end_of_month']==True]["dates"]

        month_ends = pd.to_datetime(month_ends)
        month_ends = month_ends[month_ends > (today-pd.DateOffset(months=37))]
        month_ends = month_ends[:-1]
        runs = len(month_ends)

        for i in month_ends:
            # Get the start date
            start = i-pd.DateOffset(months=6)

            # Define the SPY data to use for analysis
            temp_table = stock_data[start:i]
            temp_bench = bench[start:i]
            bench_std = bench.std()*np.sqrt(252)

            # Get Data for optimization
            def getData(stockdata):
                returns = stockdata.pct_change().dropna(how='all').dropna(axis=1)
                return_list = returns.columns.T.to_list()
                mean_returns = returns.mean()
                cov_matrix = returns.cov()
                return mean_returns, cov_matrix, return_list

            # Get data needed for optimizer
            mean_returns, cov_matrix, return_list = getData(stockdata=temp_table)

            # Run Optimizer
            results = max_sf(mean_returns, cov_matrix, bench_std)
            # pull otimimal weights and sharpe ratio
            max_sr, opt_weights = results['fun']*(-1),results['x']

            # Get list of optimal stocks weights
            stock_weights = pd.DataFrame(opt_weights, index = return_list).T

            # Get stock returns for following month
            next_month = i+pd.DateOffset(months=1)
            next_period = next_month.strftime('%Y-%m')

            returns = stock_data[start:next_month].pct_change().dropna(how='all').dropna(axis=1)
            returns = returns[next_period]

            # Calculate daily returns for the portfolio
            cum_returns = (returns+1).cumprod() # get the cumulative returns for all stocks
            weight_cum_returns = cum_returns.multiply(np.array(stock_weights), axis='columns') # multiply cumulative returns by weights
            portfolio_returns = pd.DataFrame(columns=['cum_return'])
            portfolio_returns['cum_return'] = weight_cum_returns.sum(axis=1) # sum up cumulative returns
            portfolio_returns['port_return'] = portfolio_returns.pct_change() # calculate daily returns
            portfolio_returns['port_return'].iloc[0] = portfolio_returns['cum_return'].iloc[0]-1 # fill in first day

            # Append data to final portfolio return table
            final_port_return = final_port_return.append(portfolio_returns[['port_return']])

            # Update the optimizer status
            opt_pct = min(opt_pct + (1/(runs)),1)
            bar_lang = round(opt_pct*100,2)
            my_bar.progress(opt_pct, text=f"Training Model - {bar_lang}% Complete")

        # Add benchmark values
        start = month_ends.iloc[0]
        final_port_return['bench_return'] = bench[start:]

        # Export to csv file
        csv_path = f"csv_files/optimizer_strategy_returns_{today}.csv"
        final_port_return.to_csv(csv_path)
    else:
        final_port_return = pd.read_csv(f"csv_files/optimizer_strategy_returns_{today}.csv", index_col=0, parse_dates=True, infer_datetime_format=True)

    return final_port_return