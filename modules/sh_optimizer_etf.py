import pandas as pd
import numpy as np
import datetime as dt
import scipy as sc

# Calculate portfolio performance
def portfolio_perform(weights, mean_returns, cov_matrix):  
    returns = np.sum(mean_returns*weights)*252
    std = np.sqrt( np.dot(pd.DataFrame(weights).T.values.tolist(), np.dot(cov_matrix, weights)) ) * np.sqrt(252)
    return returns, std

def port_std(weights, cov_matrix):
    std = np.sqrt( np.dot(pd.DataFrame(weights).T.values.tolist(), np.dot(cov_matrix, weights)) ) * np.sqrt(252)
    return std

def neg_sharperatio(weights, mean_returns, cov_matrix, riskfreerate = .03):
    preturns, pstd = portfolio_perform(weights, mean_returns, cov_matrix)
    return - (preturns- riskfreerate)/pstd
    
def max_sf(mean_returns, cov_matrix, bench_std, riskfreerate = .03, constraint_set=(.01,.40)):
    # Minimizing the negative SR by alering the weights of the portfolio
    num_assets = len(mean_returns)
    args = (mean_returns, cov_matrix, riskfreerate)
    # Use no risk constraint or constraint set up by user
    if 1==1:
        constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
    else:
        constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1},
                       {'type': 'eq', 'fun': lambda x: (np.sqrt( np.dot(pd.DataFrame(x).T.values.tolist(), np.dot(cov_matrix, x)) ) * np.sqrt(252))-(bench_std*.95)})

    bound = constraint_set
    bounds = tuple(bound for asset in range(num_assets))
    result = sc.optimize.minimize(neg_sharperatio, num_assets*[1/num_assets], args=args,
                        method='SLSQP', bounds=bounds, constraints=constraints)
    return result