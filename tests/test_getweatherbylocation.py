import unittest
from lambda_functions.GetWeatherByLocation.handler import lambda_handler

class TestGetWeatherByLocation(unittest.TestCase):
    def test_valid_city(self):
        event = { "queryStringParameters": {"location": "Madrid"} }
        result = lambda_handler(event, None)
        assert result["statusCode"] == 200
