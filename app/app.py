import json
import yfinance as yf
import pandas as pd
import numpy as np
from io import StringIO

def lambda_handler(event, context):
    # Extract parameters
    max_time_window = event.get("max_time_window", 1)
    ticker_symbol = event.get("ticker_symbol", "AAPL")
    interval = event.get("interval", "1h")

    # Fetch stock data
    stock_data = yf.download(
        ticker_symbol, period=f"{max_time_window}d", interval=interval
    )

    # Convert stock data to JSON
    stock_data_json = stock_data.to_json()

    # Load stock data JSON to DataFrame
    stock_data_df = pd.read_json(StringIO(stock_data_json))

    # Change column names
    stock_data_df.columns = [
        "Open",
        "High",
        "Low",
        "Close",
        "Volume",
    ]

    # Ensure the index is a datetime index
    stock_data_df.index = pd.to_datetime(stock_data_df.index)

    # Handle missing values by forward and backward filling
    stock_data_df = stock_data_df.ffill().bfill()

    # Remove any duplicate entries in case the data is irregular
    stock_data_df = stock_data_df.loc[~stock_data_df.index.duplicated(keep='first')]

    # Remove extreme outliers using IQR-based filtering
    Q1 = stock_data_df['Close'].quantile(0.25)
    Q3 = stock_data_df['Close'].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    stock_data_df = stock_data_df[(stock_data_df['Close'] >= lower_bound) & (stock_data_df['Close'] <= upper_bound)]

    # Remove NaN values
    clean_data = stock_data_df.dropna()

    # Convert DataFrame to JSON for response
    clean_data_json = clean_data.to_json(orient='records', indent=4)

    return {
        "statusCode": 200,
        "body": {
                "ticker_symbol": ticker_symbol,
                "max_time_window": max_time_window,
                "interval": interval,
                "data": json.loads(clean_data_json)
            },
    }
