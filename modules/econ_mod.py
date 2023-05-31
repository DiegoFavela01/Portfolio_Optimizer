# needed for API
import pandas as pd
import numpy as np
import datetime as dt
import pandas_datareader as pdr
import requests
np.random.seed(42)

def get_econ_data ():
    # get today
    today = dt.date.today()
    
    # define dates for DataReader
    end_str = dt.date.today().strftime('%Y-%m-%d')
    start_str = (today - dt.timedelta(days=365*21)).strftime('%Y-%m-%d')

    # select tables, enter as dataframe
    list_of_pct_tables = ['EFFR', 'FEDFUNDS', 'CSUSHPINSA', 'T10YIEM', 'T5YIEM', 'PSAVERT', 'CIVPART', 'TB3MS', 'REAINTRATREARAT10Y', 'MORTGAGE30US']
    # AAA - BBB is spread
    lisf_of_val_tables = ['EFFR', 'IPUTIL', 'GASREGW', 'T10Y3MM', 'UNRATE', 'H8B1058NCBCMG','RECPROUSM156N', 'SAHMREALTIME', 'CSUSHPINSA', 'INDPRO', 'HOUST', 'TOTALSA', 'MSACSR', 'DSPIC96', 'RSXFS', 'PMSAVE']
    econ_df_pct = pdr.DataReader(list_of_pct_tables, 'fred', start_str, end_str)
    econ_df_val = pdr.DataReader(lisf_of_val_tables, 'fred', start_str, end_str)
    
    # filling blank values with prior value
    econ_df_pct.fillna(method='ffill', inplace=True)
    econ_df_val.fillna(method='ffill', inplace=True)
    
    # Drop daily table form value
    econ_df_val = econ_df_val.drop(columns=['EFFR'])
    
    # Get monthly dates
    trading_days = pd.read_csv(f"../csv_files/trade_dates_{today}.csv", index_col=0)
    # get end of months for reference
    month_ends = trading_days[trading_days['end_of_month']==True]["dates"]
    month_ends = pd.to_datetime(month_ends)
    month_ends = month_ends[:-1]
    
    # filter the econ data for monthly results
    econ_df_pct = econ_df_pct[econ_df_pct.index.isin(month_ends)]
    econ_df_val = econ_df_val[econ_df_val.index.isin(month_ends)]
    
    # calculate monthly changes
    temp_df = econ_df_val[['T10Y3MM', 'UNRATE', 'H8B1058NCBCMG','RECPROUSM156N', 'SAHMREALTIME']]
    econ_df_pct = econ_df_pct.diff()
    econ_df_val = econ_df_val.pct_change()
    
    # add back in unchange probability
    econ_df_val[['T10Y3MM', 'UNRATE', 'H8B1058NCBCMG','RECPROUSM156N', 'SAHMREALTIME']] = temp_df
    
    # combine data
    econ_df = pd.concat([econ_df_pct, econ_df_val], axis=1)
    
    # remove inf values
    econ_df[np.isinf(econ_df)] = 0
    # fill blanks
    temp_df = econ_df[['T10Y3MM', 'UNRATE', 'H8B1058NCBCMG','RECPROUSM156N', 'SAHMREALTIME']]
    temp_df.fillna(method='ffill', inplace=True)
    econ_df[['T10Y3MM', 'UNRATE', 'H8B1058NCBCMG','RECPROUSM156N', 'SAHMREALTIME']] = temp_df
    
    #drop blank columns
    econ_df = econ_df.dropna(subset=['EFFR'])
    
    # update index to date
    econ_df.index = econ_df.index.date
    
    # Export to csv file
    csv_path = f"../csv_files/econ_data_{today}.csv"
    econ_df.to_csv(csv_path)

    return econ_df