import unittest
from unittest.mock import patch, Mock
from lambda_functions.GetWeatherByLocation.get_weather import lambda_handler

class TestGetWeatherByLocation(unittest.TestCase):

    @patch("lambda_functions.GetWeatherByLocation.get_weather.requests.get")
    def test_valid_city(self, mock_get):
        # Simulate OpenWeatherMap successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "name": "Madrid",
            "weather": [{"main": "Clear", "description": "clear sky"}],
            "main": {"temp": 295.15}
        }
        mock_get.return_value = mock_response

        # Simulated Lambda event
        event = { "queryStringParameters": {"location": "Madrid"} }

        result = lambda_handler(event, None)

        # Now test should pass!
        self.assertEqual(result["statusCode"], 200)
        self.assertIn("Madrid", result["body"])
