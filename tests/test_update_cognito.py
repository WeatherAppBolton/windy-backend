import unittest
from unittest.mock import patch, MagicMock
import json

from lambda_functions.UpdateCognitowithDynamo import update_cognito_with_dynamodb

class TestUpdateCognitoWithDynamo(unittest.TestCase):

    @patch("lambda_functions.UpdateCognitowithDynamo.update_cognito_with_dynamodb.cognito")
    @patch("lambda_functions.UpdateCognitowithDynamo.update_cognito_with_dynamodb.dynamo")
    @patch("lambda_functions.UpdateCognitowithDynamo.update_cognito_with_dynamodb.log_to_s3")
    def test_update_name_only(self, mock_log, mock_dynamo, mock_cognito):
        mock_table = MagicMock()
        mock_dynamo.Table.return_value = mock_table

        event = {
            "body": json.dumps({
                "email": "test@example.com",
                "name": "NewName"
            })
        }

        response = update_cognito_with_dynamodb.lambda_handler(event, None)
        self.assertEqual(response["statusCode"], 200)
        self.assertIn("✅", json.loads(response["body"])["message"])

        mock_cognito.admin_update_user_attributes.assert_called_once()
        mock_table.update_item.assert_called_once()

    @patch("lambda_functions.UpdateCognitowithDynamo.update_cognito_with_dynamodb.cognito")
    @patch("lambda_functions.UpdateCognitowithDynamo.update_cognito_with_dynamodb.dynamo")
    @patch("lambda_functions.UpdateCognitowithDynamo.update_cognito_with_dynamodb.log_to_s3")
    def test_change_email_and_password(self, mock_log, mock_dynamo, mock_cognito):
        mock_table = MagicMock()
        mock_dynamo.Table.return_value = mock_table
        mock_table.get_item.return_value = {"Item": {"email": "test@example.com", "name": "OldName"}}

        event = {
            "body": json.dumps({
                "email": "test@example.com",
                "newEmail": "new@example.com",
                "password": "NewPass123!",
                "currentPassword": "OldPass123!"
            })
        }

        mock_cognito.initiate_auth.return_value = {}

        response = update_cognito_with_dynamodb.lambda_handler(event, None)
        self.assertEqual(response["statusCode"], 200)

        mock_cognito.admin_update_user_attributes.assert_called()
        mock_cognito.admin_set_user_password.assert_called()
        mock_table.put_item.assert_called()
        mock_table.delete_item.assert_called()

    @patch("lambda_functions.UpdateCognitowithDynamo.update_cognito_with_dynamodb.cognito")
    @patch("lambda_functions.UpdateCognitowithDynamo.update_cognito_with_dynamodb.log_to_s3")
    def test_invalid_current_password(self, mock_log, mock_cognito):
        event = {
            "body": json.dumps({
                "email": "test@example.com",
                "password": "NewPass123!",
                "currentPassword": "WrongPass!"
            })
        }

        from botocore.exceptions import ClientError
        mock_cognito.initiate_auth.side_effect = ClientError(
            {"Error": {"Message": "Not Authorized"}}, "initiate_auth"
        )

        response = update_cognito_with_dynamodb.lambda_handler(event, None)
        self.assertEqual(response["statusCode"], 401)
        self.assertIn("incorrect", json.loads(response["body"])["message"].lower())

if __name__ == '__main__':
    unittest.main()
