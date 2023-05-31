{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 1,
   "id": "986747a2-23cb-4290-bae9-203e77c6bec8",
   "metadata": {},
   "outputs": [],
   "source": [
    "# General libraries\n",
    "import pandas as pd\n",
    "import numpy as np\n",
    "import datetime as dt\n",
    "import matplotlib.pyplot as plt\n",
    "\n",
    "# API Based Libraries\n",
    "import pandas_market_calendars as mcal\n",
    "from pandas_datareader import data as pdr\n",
    "import yfinance as yf\n",
    "import scipy as sc\n",
    "yf.pdr_override()\n",
    "\n",
    "#turn off warning signs for cleaner code\n",
    "from warnings import filterwarnings\n",
    "filterwarnings(\"ignore\")\n",
    "\n",
    "# import function for portfolio optimizer\n",
    "from sh_optimizer import portfolio_perform, port_std, neg_sharperatio, max_sf\n",
    "\n",
    "#import functions for grabbing and storing data\n",
    "from initial_data_load import refresh_data_tables"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "ef80e405-b3e5-463a-87f9-d2e5b1020bed",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "Data is already up for today.\n",
      "Optimizer is 0.027777777777777776% complete\n",
      "Optimizer is 0.05555555555555555% complete\n",
      "Optimizer is 0.08333333333333333% complete\n",
      "Optimizer is 0.1111111111111111% complete\n",
      "Optimizer is 0.1388888888888889% complete\n",
      "Optimizer is 0.16666666666666669% complete\n",
      "Optimizer is 0.19444444444444448% complete\n",
      "Optimizer is 0.22222222222222227% complete\n",
      "Optimizer is 0.25000000000000006% complete\n"
     ]
    }
   ],
   "source": [
    "# Create a dataframe to store portfolio return data\n",
    "final_port_return = pd.DataFrame(columns=['return'])\n",
    "\n",
    "# Create Global variable to update on status\n",
    "global opt_pct\n",
    "opt_pct = 0\n",
    "\n",
    "# Get today's date for reference\n",
    "today = dt.date.today()\n",
    "\n",
    "# Check to see if data has been updated\n",
    "refresh_data_tables()\n",
    "\n",
    "# pull monthly returns\n",
    "monthly_returns_df = pd.read_csv(f\"../csv_files/monthly_returns_{today}.csv\", index_col=0, parse_dates=True, infer_datetime_format=True)\n",
    "offset_returns = monthly_returns_df.shift(-1)\n",
    "\n",
    "# get full stock data\n",
    "stock_data = pd.read_csv(f\"../csv_files/snp_500_stocks_{today}.csv\", index_col=0, parse_dates=True, infer_datetime_format=True)\n",
    "# Convert datetimes to dates\n",
    "dates = stock_data.index.tolist()\n",
    "def makethisdate(date):\n",
    "    new = date.date()\n",
    "    new = str(new)\n",
    "    new = pd.to_datetime(new)\n",
    "    return new\n",
    "dates = list(map(makethisdate, dates))\n",
    "stock_data.index = dates\n",
    "\n",
    "# get list of trading dates\n",
    "trading_days = pd.read_csv(f\"../csv_files/trade_dates_{today}.csv\", index_col=0)\n",
    "# get end of months for reference\n",
    "month_ends = trading_days[trading_days['end_of_month']==True][\"dates\"]\n",
    "\n",
    "month_ends = pd.to_datetime(month_ends)\n",
    "month_ends = month_ends[month_ends > (today-pd.DateOffset(months=37))]\n",
    "month_ends = month_ends[:-1]\n",
    "\n",
    "for i in month_ends:\n",
    "    # Get the start date\n",
    "    start = i-pd.DateOffset(months=6)\n",
    "    \n",
    "    # Define the SPY data to use for analysis\n",
    "    temp_table = stock_data[start:i]\n",
    "    bench = temp_table[['SPY']].pct_change()\n",
    "    bench_std = bench.std()*np.sqrt(252)\n",
    "    \n",
    "    # Get Data for optimization\n",
    "    def getData(stockdata):\n",
    "        returns = stockdata.pct_change().dropna(how='all').dropna(axis=1)\n",
    "        return_list = returns.columns.T.to_list()\n",
    "        mean_returns = returns.mean()\n",
    "        cov_matrix = returns.cov()\n",
    "        return mean_returns, cov_matrix, return_list\n",
    "    \n",
    "    # Get data needed for optimizer\n",
    "    mean_returns, cov_matrix, return_list = getData(stockdata=temp_table)\n",
    "    \n",
    "    # Run Optimizer\n",
    "    results = max_sf(mean_returns, cov_matrix, bench_std)\n",
    "    # pull otimimal weights and sharpe ratio\n",
    "    max_sr, opt_weights = results['fun']*(-1),results['x']\n",
    "    \n",
    "    # Get list of optimal stocks weights\n",
    "    stock_weights = pd.DataFrame(opt_weights, index = return_list).T\n",
    "    \n",
    "    # Get stock returns for following month\n",
    "    next_month = i+pd.DateOffset(months=1)\n",
    "    next_period = next_month.strftime('%Y-%m')\n",
    "    \n",
    "    returns = stock_data[start:next_month].pct_change().dropna(how='all').dropna(axis=1)\n",
    "    returns = returns[next_period]\n",
    "    \n",
    "    # Calculate daily returns for the portfolio\n",
    "    cum_returns = (returns+1).cumprod() # get the cumulative returns for all stocks\n",
    "    weight_cum_returns = cum_returns.multiply(np.array(stock_weights), axis='columns') # multiply cumulative returns by weights\n",
    "    portfolio_returns = pd.DataFrame(columns=['cum_return'])\n",
    "    portfolio_returns['cum_return'] = weight_cum_returns.sum(axis=1) # sum up cumulative returns\n",
    "    portfolio_returns['return'] = portfolio_returns.pct_change() # calculate daily returns\n",
    "    portfolio_returns['return'].iloc[0] = portfolio_returns['cum_return'].iloc[0]-1 # fill in first day\n",
    "    \n",
    "    # Append data to final portfolio return table\n",
    "    final_port_return = final_port_return.append(portfolio_returns[['return']])\n",
    "    \n",
    "    # Update the optimizer status\n",
    "    opt_pct = opt_pct + (1/36)\n",
    "    print(f'Optimizer is {opt_pct}% complete')\n",
    "    \n",
    "final_port_return\n",
    "    "
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "e10cb5c8-0954-495c-9758-109508c48230",
   "metadata": {},
   "outputs": [],
   "source": [
    "final_port_return['cum_return'] = (final_port_return['return']+1).cumprod()\n",
    "final_port_return"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "735b3263-31c4-4456-b50c-927c50bbba24",
   "metadata": {},
   "outputs": [],
   "source": [
    "start = today-pd.DateOffset(months=24)\n",
    "end = today\n",
    "bench = pdr.get_data_yahoo(['SPY'], start=start, end=end)\n",
    "bench = bench[['Adj Close']]"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "a2111674-b730-4176-a0d5-e1dff7d43926",
   "metadata": {},
   "outputs": [],
   "source": [
    "bench['return']=bench['Adj Close'].pct_change()\n",
    "bench['cum_return'] = (bench['return']+1).cumprod()\n",
    "bench"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "d375239f-5eea-47b2-9b09-7d08f4cf24d0",
   "metadata": {},
   "outputs": [],
   "source": [
    "final_port_return['cum_return'].plot()\n",
    "bench['cum_return'].plot()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "837c8561-4097-417a-a90d-5d23a2f0343e",
   "metadata": {},
   "outputs": [],
   "source": []
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python (dev)",
   "language": "python",
   "name": "dev"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.9.13"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
