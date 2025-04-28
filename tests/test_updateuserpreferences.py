import unittest
from lambda_functions.UpdateUserPreferences.update_user_prefs import lambda_handler

class TestUpdateUserPreferences(unittest.TestCase):
    def test_missing_email(self):
        event = { "body": '{"theme": "night"}' }
        result = lambda_handler(event, None)
        assert result["statusCode"] == 400
