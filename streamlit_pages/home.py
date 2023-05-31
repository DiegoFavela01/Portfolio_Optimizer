import streamlit as st

def render_home():
    # Get strategies
    from modules.etf_strategy_loop import etf_strategy
    from modules.optimizer_strategy_loop import optimizer_strategy

    st.title("Strategy Selection")
    st.write("Please select a portfolio optimization strategy")
    
    strategy = st.selectbox("Strategies",['S&P 500 Optimization Strategy', 'Predictive ETF Portfolio Strategy'])
    st.write('Strategy Definition:')
    if strategy == 'S&P 500 Optimization Strategy':
        st.write("The S&P 500 Optimization Strategy takes a 6 month lookback at the performance of the S&P 500 stocks. It then calculate the most optimal portfolio by adjusting the weights of each stock until the sharpe ratio for that period has been maximized.")
        st.write("The strategy is reblanced on a monthly basis and individual stock weights are rebalanced between 0%-5%. In addition, volatility is limited so as not to exceed the S&P.")
    else:
        st.write("The predictive ETF portfolio strategy utilizes predictive machine learning. Using 20 years of historical stock and economic data, the monthly returns for 11 ETFs, representing S&P 500 market sectors, are predicted. These predictions are then used to calculate the most efficent portfolio by finding the optimal portfolio weights, which will maximize the portfolio's sharpe ratio.")
        st.write("The strategy is reblanced on a monthly basis and individual ETF weights are rebalanced between 1%-40%. In addition, volatility is limited so as not ot exceed the S&P 500")
        
    run_it = st.button("Run Strategy")
    
    if run_it and strategy == 'S&P 500 Optimization Strategy':
        opt_pct = 0
        st.progress(opt_pct, text="Renning Model")
        portfolio_returns = optimizer_strategy()
    elif run_it and strategy == 'Predictive ETF Portfolio Strategy':
        portfolio_returns = etf_strategy()
        
        
        st.write("All Done")