import boto3
import json

dynamodb = boto3.client("dynamodb")

def lambda_handler(event, context):
    email = event.get("queryStringParameters", {}).get("email")

    if not email:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Missing email"})
        }

    try:
        response = dynamodb.get_item(
            TableName="RegisteredUsers",
            Key={"email": {"S": email}}
        )

        item = response.get("Item")

        if not item:
            return {
                "statusCode": 404,
                "body": json.dumps({"error": "User not found"})
            }

        # Extract values from DynamoDB format
        name = item.get("name", {}).get("S", "")
        theme = item.get("theme", {}).get("S", "default")
        favorites_raw = item.get("favorites", {}).get("L", [])

        favorites = [f.get("S", "") for f in favorites_raw]

        return {
            "statusCode": 200,
            "body": json.dumps({
                "email": email,
                "name": name,
                "theme": theme,
                "favorites": favorites
            })
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
