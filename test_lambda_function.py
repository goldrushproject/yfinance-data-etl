import unittest
from lambda_function import lambda_handler


class TestLambdaFunction(unittest.TestCase):
    def test_lambda_function(self):
        event = {"max_time_window": 10, "ticker_symbol": "AAPL"}
        context = {}
        response = lambda_handler(event, context)
        self.assertEqual(response["statusCode"], 200)
        self.assertIn("Hello from Lambda!", response["body"])
        self.assertIn("AAPL", response["body"])
        self.assertIn("10", response["body"])


if __name__ == "__main__":
    unittest.main()
