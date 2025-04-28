import unittest
from lambda_functions.RegisterUser.register_user import lambda_handler

class TestRegisterUserHandler(unittest.TestCase):
    def test_missing_fields(self):
        event = { "body": '{"email": "test@example.com"}' }
        result = lambda_handler(event, None)
        assert result["statusCode"] == 400
