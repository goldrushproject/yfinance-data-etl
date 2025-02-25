import json


def lambda_handler(event, context):
    print("Received event: " + json.dumps(event, indent=2))

    # Extract parameters
    max_time_window = event.get("max_time_window")
    ticker_symbol = event.get("ticker_symbol")

    print(f"Max Time Window: {max_time_window}")
    print(f"Ticker Symbol: {ticker_symbol}")

    # Example processing
    message = f"Hello from Lambda! Received ticker {ticker_symbol} with a time window of {max_time_window}."

    # Return a response
    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "message": message,
                "max_time_window": max_time_window,
                "ticker_symbol": ticker_symbol,
            }
        ),
    }
