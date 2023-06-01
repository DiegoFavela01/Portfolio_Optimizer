import streamlit as st
import pandas as pd
import pyfolio as pf
import matplotlib
import matplotlib.pyplot as plt

# turn off warning signs for cleaner code
from warnings import filterwarnings
filterwarnings("ignore")

def render_home():
    # Get strategies
    from modules.etf_strategy_loop import etf_strategy
    from modules.optimizer_strategy_loop import optimizer_strategy

    def get_metrics(portfolio_returns):
        port_metrics = pf.timeseries.perf_stats(portfolio_returns['port_return'], factor_returns = portfolio_returns['bench_return'])
        port_metrics[:3] = round(port_metrics[:3]*100,2)
        port_metrics[-3], port_metrics[6] = round(port_metrics[-3]*100,2), round(port_metrics[6]*100,2)
        port_metrics = round(port_metrics,2)
        port_metrics = pd.DataFrame(port_metrics, columns = ['Metric Values'])

        bench_metrics = pf.timeseries.perf_stats(portfolio_returns['bench_return'],)
        bench_metrics[:3] = round(bench_metrics[:3]*100,2)
        bench_metrics[-1], bench_metrics[6] = round(bench_metrics[-1]*100,2), round(bench_metrics[6]*100,2)
        bench_metrics = round(bench_metrics,2)
        bench_metrics = pd.DataFrame(bench_metrics, columns = ['Metric Values'])
        return port_metrics, bench_metrics

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
        # Get Strategy Returns
        portfolio_returns = optimizer_strategy()
        # Create Metrics
        port_metrics, bench_metrics = get_metrics(portfolio_returns)
        col1, col2 = st.columns(2)
        col1.write('Portfolio Metrics')
        col1.dataframe(port_metrics, height=570,use_container_width=True) 
        col2.write('Benchmark Metrics')
        col2.dataframe(bench_metrics, height=570,use_container_width=True)
        # Create Portfolio Return Graphs
        st.write("Return Based Graphs")
        return_graphs = plt.figure()
        plt.subplot(2,1,1)
        pf.plot_rolling_returns(portfolio_returns['port_return'], factor_returns = portfolio_returns['bench_return'])
        plt.subplot(2,1,2)
        pf.plot_annual_returns(portfolio_returns,  )
        plt.tight_layout()
        st.pyplot(return_graphs)
        # Create portfolio Risk Graphs
        st.write("Risk Based Graphs")
        risk_graph = plt.figure()
        plt.subplot(2,1,1)
        pf.plot_rolling_sharpe(portfolio_returns['port_return'], factor_returns = portfolio_returns['bench_return'], rolling_window = 252)
        plt.subplot(2,1,2)
        pf.plot_rolling_volatility(portfolio_returns['port_return'], factor_returns = portfolio_returns['bench_return'], rolling_window=126)
        plt.tight_layout()
        st.pyplot(risk_graph)
        # offer ability to save tear sheet
        tear = st.button("Save Tear Sheet")
        if tear:
            # Create tearsheet
            fig = pf.create_returns_tear_sheet(portfolio_returns['port_return'], benchmark_rets = portfolio_returns['bench_return'], return_fig=True)
            # Store plots in a file
            file_name = "images/S&P_500_Optimization_Strategy_tearsheet.pdf"
            fig.savefig(file_name, format="pdf")


    elif run_it and strategy == 'Predictive ETF Portfolio Strategy':
        # Get Strategy Returns
        portfolio_returns = etf_strategy()
        # Create Metrics
        port_metrics, bench_metrics = get_metrics(portfolio_returns)
        col1, col2 = st.columns(2)
        col1.write('Portfolio Metrics')
        col1.dataframe(port_metrics, height=570,use_container_width=True) 
        col2.write('Benchmark Metrics')
        col2.dataframe(bench_metrics, height=570,use_container_width=True)
        # Create Portfolio Return Graphs
        st.write("Return Based Graphs")
        return_graphs = plt.figure()
        plt.subplot(2,1,1)
        pf.plot_rolling_returns(portfolio_returns['port_return'], factor_returns = portfolio_returns['bench_return'])
        plt.subplot(2,1,2)
        pf.plot_annual_returns(portfolio_returns,  )
        plt.tight_layout()
        st.pyplot(return_graphs)
        # Create portfolio Risk Graphs
        st.write("Risk Based Graphs")
        risk_graph = plt.figure()
        plt.subplot(2,1,1)
        pf.plot_rolling_sharpe(portfolio_returns['port_return'], factor_returns = portfolio_returns['bench_return'], rolling_window = 252)
        plt.subplot(2,1,2)
        pf.plot_rolling_volatility(portfolio_returns['port_return'], factor_returns = portfolio_returns['bench_return'], rolling_window=126)
        plt.tight_layout()
        st.pyplot(risk_graph)
        # offer ability to save tear sheet
        tear = st.button("Save Tear Sheet")
        if tear:
            # Create tearsheet
            fig = pf.create_returns_tear_sheet(portfolio_returns['port_return'], benchmark_rets = portfolio_returns['bench_return'], return_fig=True)
            # Store plots in a file
            file_name = "images/S&P_500_Optimization_Strategy_tearsheet.pdf"
            fig.savefig(file_name, format="pdf")