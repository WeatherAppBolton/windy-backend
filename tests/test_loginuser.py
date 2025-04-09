import unittest
from lambda_functions.LoginUser.handler import lambda_handler

class TestLoginUserHandler(unittest.TestCase):
    def test_invalid_credentials(self):
        event = { "body": '{"email": "fake@example.com", "password": "Fake123!"}' }
        result = lambda_handler(event, None)
        assert result["statusCode"] in [400, 401, 404]
