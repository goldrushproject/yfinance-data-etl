import json
import yfinance as yf
import pandas as pd
import numpy as np
from io import StringIO
import time
from requests.exceptions import HTTPError

def lambda_handler(event, context):
    # Extract parameters
    state_payload = event.get("StatePayload")
    max_time_window = state_payload["max_time_window"]
    ticker_symbol = state_payload["ticker_symbol"]
    interval = state_payload["interval"]

    # Fetch stock data with exponential backoff
    stock_data = safe_yf_download(ticker_symbol, max_time_window, interval)

    # Extract fundamental information
    ticker = yf.Ticker(ticker_symbol)
    company_info = ticker.info
    pe_ratio = company_info.get('trailingPE', 'N/A')
    eps = company_info.get('trailingEps', 'N/A')
    market_cap = company_info.get('marketCap', 'N/A')
    beta = company_info.get('beta', 'N/A')
    dividend_yield = company_info.get('dividendYield', 'N/A')
    sector = company_info.get('sector', 'N/A')
    industry = company_info.get('industry', 'N/A')
    country = company_info.get('country', 'N/A')

    # Technical Indicators
    stock_data['MA50'] = stock_data['Close'].rolling(window=50).mean()  # 50-period moving average
    stock_data['MA200'] = stock_data['Close'].rolling(window=200).mean()  # 200-period moving average
    stock_data['RSI'] = compute_rsi(stock_data['Close'], window=14)  # 14-period RSI

    # Convert stock data to JSON
    stock_data_json = stock_data.to_json()

    # Load stock data JSON to DataFrame
    stock_data_df = pd.read_json(StringIO(stock_data_json))

    # Clean DataFrame
    stock_data_df.columns = ["Open", "High", "Low", "Close", "Volume", "MA50", "MA200", "RSI"]
    stock_data_df.index = pd.to_datetime(stock_data_df.index)
    stock_data_df = stock_data_df.ffill().bfill()
    stock_data_df = stock_data_df.loc[~stock_data_df.index.duplicated(keep='first')]

    # Remove outliers and NaN values
    Q1 = stock_data_df['Close'].quantile(0.25)
    Q3 = stock_data_df['Close'].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    stock_data_df = stock_data_df[(stock_data_df['Close'] >= lower_bound) & (stock_data_df['Close'] <= upper_bound)]
    clean_data = stock_data_df.dropna()

    # Return additional information with stock data
    clean_data_json = clean_data.to_json(orient='records', indent=4)
    
    # Gather all useful data
    response_data = {
        "ticker_symbol": ticker_symbol,
        "max_time_window": max_time_window,
        "interval": interval,
        "pe_ratio": pe_ratio,
        "eps": eps,
        "market_cap": market_cap,
        "beta": beta,
        "dividend_yield": dividend_yield,
        "sector": sector,
        "industry": industry,
        "country": country,
        "data": json.loads(clean_data_json)
    }

    return {
        "statusCode": 200,
        "body": response_data,
    }

# Helper function to compute RSI (Relative Strength Index)
def compute_rsi(series, window=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# Helper function to safely download stock data with exponential backoff
def safe_yf_download(ticker_symbol, max_time_window, interval, retries=5, delay=5):
    for attempt in range(retries):
        try:
            stock_data = yf.download(ticker_symbol, period=f"{max_time_window}d", interval=interval)
            return stock_data
        except HTTPError as e:
            if "TooManyRequests" in str(e):
                print(f"Rate limit hit for {ticker_symbol}. Retrying in {delay} seconds...")
                time.sleep(delay)
                delay *= 2  # Exponential backoff
            else:
                raise  # Re-raise if not related to rate limiting
    raise Exception(f"Max retries exceeded for downloading {ticker_symbol} data.")

