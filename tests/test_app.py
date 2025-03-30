import unittest
import json
from app.app import lambda_handler


class TestApp(unittest.TestCase):
    def test_app(self):
        event = {"max_time_window": 1, "ticker_symbol": "TSLA", "interval": "1m"}
        context = {}
        response = lambda_handler(event, context)
        try:
            self.assertEqual(response["statusCode"], 200)
        except AssertionError as e:
            self.fail(f"Test failed: {e}")
        else:
            # Write response to a JSON file if the test succeeds
            response_body = response['body']
            with open('sample_data.json', 'w') as f:
                json.dump(response_body, f, indent=4)


if __name__ == "__main__":
    unittest.main()
