import unittest
from unittest.mock import patch
from lambda_functions.LoginUser.login_user import lambda_handler

class TestLoginUserHandler(unittest.TestCase):

    @patch("lambda_functions.LoginUser.login_user.boto3.client")
    def test_invalid_credentials(self, mock_boto_client):
        # Setup mock to simulate user not found in DynamoDB
        mock_client = mock_boto_client.return_value
        mock_client.get_item.return_value = {}  # No 'Item' key = user not found

        event = {
            "body": '{"email": "fake@example.com", "password": "Fake123!"}'
        }
        result = lambda_handler(event, None)
        assert result["statusCode"] in [400, 401, 404]

if __name__ == "__main__":
    unittest.main()