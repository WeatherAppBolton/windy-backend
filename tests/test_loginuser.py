import unittest
import json
from unittest.mock import patch, MagicMock
from lambda_functions.LoginUser.login_user import lambda_handler  # adjust path if needed

@patch('lambda_functions.LoginUser.login_user.boto3.resource')
def test_invalid_credentials(self, mock_dynamodb):
    # Simulate user not found
    table_mock = MagicMock()
    table_mock.get_item.return_value = {}  # No user returned
    mock_dynamodb.return_value.Table.return_value = table_mock

    event = {"body": json.dumps({"email": "fake@example.com", "password": "Fake123!"})}
    result = lambda_handler(event, None)

    self.assertIn(result["statusCode"], [400, 401, 404])
