import streamlit as st
import plotly.graph_objects as go
import yfinance as yf
import pandas as pd
from st_click_detector import click_detector

# Ideas for improvement:
# 1. Add more stock tickers to the list.  #E
# 2. Allow users to input a custom date range for the stock data. #E
# 3. Allow users to provide their own tickers, with error handling for tickers not in the S&P500. (Remove the ability to click on the icons) #M
# 4. Show information about the stock (e.g., market cap, P/E ratio) alongside the chart. #M
# 5. Investment portfolio tracker: Allow users to input multiple stocks and return their portfolio's current worth. #H
# 6. Add a news section to show the latest news related to the selected stock (you can use the news attribute of yfinance.Ticker). #H

st.title("Stock Market Dashboard")

# Create the images as a href elements with tickers as IDs
def show_tickers():
    content = """
        <a href='#' id='MSFT'><img height='60px' width='60px' src='https://banner2.cleanpng.com/20180609/jq/aa8dbj2or.webp'></a>
        <a href='#' id='AAPL'><img height='60px' width='60px' src='https://upload.wikimedia.org/wikipedia/commons/f/fa/Apple_logo_black.svg'></a>
        <a href='#' id='GOOG'><img height='60px' width='60px' src='https://upload.wikimedia.org/wikipedia/commons/2/2f/Google_2015_logo.svg'></a>
        <a href='#' id='NFLX'><img height='60px' width='60px' src='https://upload.wikimedia.org/wikipedia/commons/0/08/Netflix_2015_logo.svg'></a>
        <a href='#' id='AMZN'><img height='30px' width='90px' src='https://upload.wikimedia.org/wikipedia/commons/a/a9/Amazon_logo.svg'></a>
        <a href='#' id='TSLA'><img height='60px' width='60px' src='https://upload.wikimedia.org/wikipedia/commons/b/bd/Tesla_Motors.svg'></a>
        <a href='#' id='META'><img height='30px' width='120px' src='https://upload.wikimedia.org/wikipedia/commons/7/7b/Meta_Platforms_Inc._logo.svg'></a>
    """
    return content

# Make the images clickable using st_click_detector
def get_ticker():
    content = show_tickers()
    clicked = click_detector(content)
    return clicked

# Get the stock dataframe for the given ticker using yfinance
def get_dataframe(ticker):
    stock_data = yf.Ticker(ticker)
    df = stock_data.history(period="1y")
    df.reset_index(inplace=True)  # This moves the date from index to a column
    return df

# Create a candlestick chart using plotly
def plot_candlestick(df, ticker):
    fig = go.Figure(data=[go.Candlestick(x=df['Date'],
                                         open=df['Open'],
                                         high=df['High'],
                                         low=df['Low'],
                                         close=df['Close'])])
    fig.update_layout(title=f'{ticker} Stock Price', xaxis_title='Date', yaxis_title='Price (USD)')
    return fig

# Show a plotly chart in Streamlit
def show_plot(fig):
    st.plotly_chart(fig, use_container_width=True)

# Main Streamlit app
ticker = get_ticker()

# Create two columns
col1, col2 = st.columns([3, 2])

# Every time something happens, Streamlit reruns the script so when an image is clicked, the script will rerun and the ticker will not be empty.
if ticker != "":
    df = get_dataframe(ticker)
    fig = plot_candlestick(df, ticker)

    with col1:
        show_plot(fig)

        # Get key stock info (market cap and P/E ratio) to display 
        info = yf.Ticker(ticker).info
        market_cap = info.get("marketCap", "N/A")
        pe_ratio = info.get("trailingPE", "N/A")

        # Display info
        st.write(f"**Market Cap:** {market_cap}")
        st.write(f"**P/E Ratio:** {pe_ratio}")

else:
    with col1:
        st.write("Click a company logo to see its stock data.")

with col2:
        st.header("Investment Portfolio Tracker")

        tickers_input = st.text_area(
            "Enter stock tickers separated by commas (e.g. AAPL, MSFT, TSLA):"
        )
        shares_input = st.text_area(
            "Enter corresponding number of shares separated by commas (e.g. 10, 5, 3):"
        )

        if tickers_input and shares_input:
            tickers = [t.strip().upper() for t in tickers_input.split(",")]
            try:
                shares = [int(s.strip()) for s in shares_input.split(",")]
            except ValueError:
                st.error("Please enter valid integers for shares.")
                shares = []

            if len(tickers) != len(shares):
                st.error("Number of tickers and shares must match!")
            elif shares:
                portfolio = {}
                total_value = 0
                for ticker_, share in zip(tickers, shares):
                    stock = yf.Ticker(ticker_)
                    price = stock.info.get("regularMarketPrice")
                    if price is None:
                        st.warning(f"Could not fetch price for {ticker_}")
                        continue
                    value = price * share
                    portfolio[ticker_] = {"shares": share, "price": price, "value": value}
                    total_value += value
                
                st.write(f"### Portfolio Value: ${total_value:,.2f}")
                df_portfolio = pd.DataFrame.from_dict(portfolio, orient="index")
                st.dataframe(df_portfolio)