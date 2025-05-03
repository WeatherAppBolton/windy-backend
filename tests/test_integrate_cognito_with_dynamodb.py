import pytest
import boto3
from moto import mock_dynamodb2 as mock_dynamodb
from datetime import datetime
from unittest.mock import patch

from lambda_functions.IntegrateCognitowithDynamodb import integrate_cognito_with_Dynamodb

TABLE_NAME = "RegisteredUsers"

@pytest.fixture
def dynamodb_mock():
    with mock_dynamodb():
        # Set up mock DynamoDB
        dynamo = boto3.resource("dynamodb", region_name="eu-north-1")
        table = dynamo.create_table(
            TableName=TABLE_NAME,
            KeySchema=[{"AttributeName": "email", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "email", "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST"
        )
        table.wait_until_exists()
        yield table

@patch("lambda_functions.IntegrateCognitowithDynamodb.integrate_cognito_with_Dynamodb.log_to_s3")
def test_new_user_inserted(mock_log, dynamodb_mock):
    # Mock event from Cognito post-confirm trigger
    event = {
        "request": {
            "userAttributes": {
                "email": "testuser@example.com",
                "name": "Test User"
            }
        }
    }

    # Run lambda
    result = integrate_cognito_with_Dynamodb.lambda_handler(event, None)

    # Validate return (should match original event)
    assert result == event

    # Verify record was inserted
    response = dynamodb_mock.get_item(Key={"email": "testuser@example.com"})
    assert "Item" in response
    assert response["Item"]["name"] == "Test User"
    assert response["Item"]["theme"] == "default"
    assert response["Item"]["favorites"] == []
    assert response["Item"]["password"] is None
    assert "createdAt" in response["Item"]

@patch("lambda_functions.IntegrateCognitowithDynamodb.integrate_cognito_with_Dynamodb.log_to_s3")
def test_existing_user_skips_insert(mock_log, dynamodb_mock):
    # Pre-insert a record
    dynamodb_mock.put_item(Item={
        "email": "existing@example.com",
        "name": "Old User",
        "theme": "dark",
        "favorites": ["Paris"],
        "password": None,
        "createdAt": datetime.utcnow().isoformat()
    })

    event = {
        "request": {
            "userAttributes": {
                "email": "existing@example.com",
                "name": "Old User"
            }
        }
    }

    result = integrate_cognito_with_Dynamodb.lambda_handler(event, None)

    # Should still return original event
    assert result == event

    # Record must not be overwritten
    item = dynamodb_mock.get_item(Key={"email": "existing@example.com"})["Item"]
    assert item["name"] == "Old User"
    assert item["theme"] == "dark"
    assert item["favorites"] == ["Paris"]
