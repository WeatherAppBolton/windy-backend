import unittest
import json
import requests
from unittest.mock import patch, MagicMock
from lambda_functions.GetWeatherByLocation.get_weather import lambda_handler


class TestLambdaFunction(unittest.TestCase):

    @patch('lambda_functions.GetWeatherByLocation.get_weather.log_to_s3')  # ✅ Patch where it's used!
    @patch('lambda_functions.GetWeatherByLocation.get_weather.requests.get')
    @patch.dict('os.environ', {'WEATHER_API_KEY': 'dummy-key'})
    def test_lambda_returns_success_for_city(self, mock_requests_get, mock_log_to_s3):
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "main": {"temp": 20},
            "weather": [{"main": "Cloudy"}],
            "name": "London"
        }
        mock_requests_get.return_value = mock_response

        event = {"queryStringParameters": {"location": "London"}}
        result = lambda_handler(event, None)

        self.assertEqual(result["statusCode"], 200)
        body = json.loads(result["body"])
        self.assertEqual(body["location"], "London")
        self.assertEqual(body["temperature"], 20)
        self.assertEqual(body["condition"], "Cloudy")

    @patch('lambda_functions.GetWeatherByLocation.get_weather.log_to_s3')  # ✅
    @patch('lambda_functions.GetWeatherByLocation.get_weather.requests.get')
    @patch.dict('os.environ', {'WEATHER_API_KEY': 'dummy-key'})
    def test_lambda_returns_error_without_location(self, mock_requests_get, mock_log_to_s3):
        event = {"queryStringParameters": {}}
        result = lambda_handler(event, None)

        self.assertEqual(result["statusCode"], 400)
        body = json.loads(result["body"])
        self.assertEqual(body["error"], "No location or coordinates provided")
        mock_requests_get.assert_not_called()

    @patch('lambda_functions.GetWeatherByLocation.get_weather.log_to_s3')  # ✅
    @patch('lambda_functions.GetWeatherByLocation.get_weather.requests.get')
    def test_lambda_returns_500_missing_api_key(self, mock_requests_get, mock_log_to_s3):
        event = {"queryStringParameters": {"location": "London"}}
        with patch.dict('os.environ', {}, clear=True):
            result = lambda_handler(event, None)

        self.assertEqual(result["statusCode"], 500)
        body = json.loads(result["body"])
        self.assertEqual(body["error"], "Missing WEATHER_API_KEY in environment")
        mock_requests_get.assert_not_called()
        mock_log_to_s3.assert_called()

    @patch('lambda_functions.GetWeatherByLocation.get_weather.log_to_s3')  # ✅
    @patch('lambda_functions.GetWeatherByLocation.get_weather.requests.get')
    @patch.dict('os.environ', {'WEATHER_API_KEY': 'dummy-key'})
    def test_lambda_handles_weather_api_failure(self, mock_requests_get, mock_log_to_s3):
        mock_requests_get.side_effect = requests.exceptions.RequestException("simulated error")

        event = {"queryStringParameters": {"location": "Paris"}}
        result = lambda_handler(event, None)

        self.assertEqual(result["statusCode"], 502)
        body = json.loads(result["body"])
        self.assertIn("Weather service error", body["error"])

    @patch('lambda_functions.GetWeatherByLocation.get_weather.log_to_s3')  # ✅
    @patch('lambda_functions.GetWeatherByLocation.get_weather.requests.get')
    @patch.dict('os.environ', {'WEATHER_API_KEY': 'dummy-key'})
    def test_lambda_handles_timeout(self, mock_requests_get, mock_log_to_s3):
        mock_requests_get.side_effect = requests.exceptions.Timeout("simulated timeout")

        event = {"queryStringParameters": {"location": "Berlin"}}
        result = lambda_handler(event, None)

        self.assertEqual(result["statusCode"], 504)
        body = json.loads(result["body"])
        self.assertIn("timed out", body["error"])


if __name__ == '__main__':
    unittest.main()
