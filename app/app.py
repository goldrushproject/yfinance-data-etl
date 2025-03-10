import json
import yfinance as yf
import pandas as pd
from io import StringIO


def lambda_handler(event, context):
    print("Received event: " + json.dumps(event, indent=2))

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
        "Close",
        "High",
        "Low",
        "Open",
        "Volume",
    ]

    # Convert DataFrame to JSON
    stock_data_json = stock_data_df.to_json(orient='records', indent=4)
    # print(stock_data_json)

    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "ticker_symbol": ticker_symbol,
                "max_time_window": max_time_window,
                "interval": interval,
                "data": json.loads(stock_data_json),
            },
            indent=4
        ),
    }
