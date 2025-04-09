import unittest
from lambda_functions.GetUserPreferences.handler import lambda_handler

class TestGetUserPreferences(unittest.TestCase):
    def test_missing_email(self):
        event = { "queryStringParameters": {} }
        result = lambda_handler(event, None)
        assert result["statusCode"] == 400
