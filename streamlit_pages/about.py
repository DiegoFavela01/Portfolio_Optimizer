import streamlit as st

def render_about():
    st.title("About")
    st.markdown(
        """
        Our program, developed by Diego Favela, Michael Roth, and Rachel Phillips, is designed to analyze and optimize the performance of individual stocks from the S&P 500 index. By leveraging data gathering, machine learning, and optimization techniques, we aim to provide valuable insights and help users make informed investment decisions.
        """
    )

    st.header("How it Works")

    st.subheader("1. Data Gathering & Prep")
    st.markdown(
        """
        We start by collecting historical data for individual stocks in the S&P 500 index. This data includes daily stock prices, volumes, and other relevant information. We pull data for a span of 10 years and organize it into a convenient CSV format. Additionally, we identify the first day and last day of each month for further analysis.
        """
    )

    st.subheader("2. Optimizer 1")
    st.markdown(
        """
        Our first optimization step is performed using the Sci-Pie optimizer. This optimizer allows us to bound the weight of each stock between 0% and 5% and ensures that the total weight of stocks in the portfolio remains at 100%. We can also choose to constrain the standard deviation of the portfolio. The optimizer takes into account variable inputs to generate optimized weights for the stocks.
        """
    )

    st.subheader("3. Machine Learning Loop")
    st.markdown(
        """
        In this stage, we employ a machine learning loop to analyze each stock individually. We create a list of stocks using the column names from the stock table. The loop filters the data based on specified start and stop dates, which are initially set for testing purposes. Our machine learning expert utilizes various algorithms and techniques to extract meaningful insights from the stock data. This includes calculating indicators such as returns, moving averages, standard deviations, and Bollinger bands. We focus on end-of-month data for improved accuracy. Machine learning models like neural regression and SLTM are applied, and the results are exported to a table.
        """
    )

    st.subheader("4. Optimizer 2")
    st.markdown(
        """
        After gathering insights from the machine learning loop, we proceed to our second optimization step. Again, we utilize the Sci-Pie optimizer to calculate weights for the stocks based on the optimized returns obtained from the machine learning loop. By averaging the weights derived from optimizer 1 and optimizer 2, we further optimize the portfolio allocation.
        """
    )

    st.subheader("5. Historical Date Loop")
    st.markdown(
        """
        To evaluate the performance of the portfolio over time, we set up a historical date loop. This loop considers the prior 6 months and prior 10 years. It iterates through the month-end table, determining the start and end dates for each iteration. We filter the data accordingly, focusing on relevant time periods.
        """
    )

    st.subheader("6. Historical Performance Table")
    st.markdown(
        """
        Finally, we track the historical performance of the portfolio using the optimized weights and cumulative returns of individual stocks. By multiplying the cumulative return of each stock by its corresponding weight, we generate a historical performance table. This table provides a comprehensive view of the portfolio's performance over the specified time periods.
        """
   
    )