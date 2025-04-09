import unittest
from lambda_functions.UpdateUserPreferences.handler import lambda_handler

class TestUpdateUserPreferences(unittest.TestCase):
    def test_missing_email(self):
        event = { "body": '{"theme": "night"}' }
        result = lambda_handler(event, None)
        assert result["statusCode"] == 400
