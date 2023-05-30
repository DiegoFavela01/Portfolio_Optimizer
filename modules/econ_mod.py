# needed for API
import pandas as pd
import numpy as np
import datetime as dt
import pandas_datareader as pdr
import requests
np.random.seed(42)

def get_econ_data ():
    # define data for DataReader
    today = dt.date.today()
    start_str = (today - dt.timedelta(days=365*21)).strftime('%Y-%m-%d')
    end_str = today.strftime('%Y-%m-%d')

    # select tables, enter as dataframe
    list_of_pct_tables = ['SOFR30DAYAVG', 'SOFR', 'EFFR', 'AAA', 'DBAA', 'T10YIE', 'T5YIE', 'MORTGAGE30US', 'DGS30', 'DGS1','BAMLH0A0HYM2EY']
    # AAA - BBB is spread
    lisf_of_val_tables = ['SOFRVOL', 'RECPROUSM156N', 'SAHMREALTIME']
    econ_df_pct = pdr.DataReader(list_of_pct_tables, 'fred', start_str, end_str)
    econ_df_val = pdr.DataReader(lisf_of_val_tables, 'fred', start_str, end_str)
    
    #filling blank values with prior value
    econ_df_pct.fillna(method='ffill', inplace=True)
    econ_df_val.fillna(method='ffill', inplace=True)
    
    #create spread metrics
    spread_df = pd.DataFrame()
    spread_df['ab_bond_spread'] = econ_df_pct["DBAA"] - econ_df_pct["AAA"]
    spread_df['junk_bond_spread'] = econ_df_pct["BAMLH0A0HYM2EY"] - econ_df_pct["AAA"]
    spread_df['int_spread'] = econ_df_pct["DGS30"] - econ_df_pct["DGS1"]
    
    # calculate daily changes
    temp_df = econ_df_val[['RECPROUSM156N','SAHMREALTIME']]
    econ_df_pct = econ_df_pct.diff()
    econ_df_val = econ_df_val.pct_change()
    
    # add back in unchange probability
    econ_df_val[['RECPROUSM156N','SAHMREALTIME']] = temp_df
    
    # combine data
    econ_df = pd.concat([econ_df_pct, econ_df_val, spread_df], axis=1)
    
    # remove inf values
    econ_df[np.isinf(econ_df)] = 0
    # fill blanks
    temp_df = econ_df[['RECPROUSM156N','SAHMREALTIME']]
    temp_df.fillna(method='ffill', inplace=True)
    econ_df[['RECPROUSM156N','SAHMREALTIME']] = temp_df
    
    #drop blank columns
    econ_df = econ_df.dropna(subset=['EFFR'])
    
    # update index to date
    econ_df.index = econ_df.index.date
    
    # Export to csv file
    csv_path = f"../csv_files/econ_data_{today}.csv"
    econ_df.to_csv(csv_path)

    return econ_df