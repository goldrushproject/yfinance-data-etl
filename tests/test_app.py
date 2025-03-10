import unittest
import json
from app.app import lambda_handler


class TestApp(unittest.TestCase):
    def test_app(self):
        event = {"max_time_window": 2, "ticker_symbol": "AAPL", "interval": "1m"}
        context = {}
        response = lambda_handler(event, context)
        try:
            self.assertEqual(response["statusCode"], 200)
            self.assertIn("AAPL", response["body"])
            self.assertIn("2", response["body"])
        except AssertionError as e:
            self.fail(f"Test failed: {e}")
        else:
            # Write response to a JSON file if the test succeeds
            response_body = json.loads(response['body'])
            with open('sample_data.json', 'w') as f:
                json.dump(response_body, f, indent=4)


if __name__ == "__main__":
    unittest.main()
