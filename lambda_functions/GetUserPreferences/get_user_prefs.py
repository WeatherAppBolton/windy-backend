import boto3
import json
from logger import log_to_s3


dynamodb = boto3.client("dynamodb")


def lambda_handler(event, context):
    email = event.get("queryStringParameters", {}).get("email")

    if not email:
        log_to_s3(
            {"error": "Missing email in request", "event": event},
            prefix="logs/userprefs",
        )

        return {"statusCode": 400, "body": json.dumps({"error": "Missing email"})}

    try:
        response = dynamodb.get_item(
            TableName="RegisteredUsers", Key={"email": {"S": email}}
        )

        item = response.get("Item")

        if not item:
            log_to_s3(
                {"email": email, "error": "User not found"}, prefix="logs/userprefs"
            )

            return {"statusCode": 404, "body": json.dumps({"error": "User not found"})}

        # Extract user data
        name = item.get("name", {}).get("S", "")
        theme = item.get("theme", {}).get("S", "default")
        favorites_raw = item.get("favorites", {}).get("L", [])
        favorites = [f.get("S", "") for f in favorites_raw]

        # ✅ Optional: Log successful read (optional, can be removed)
        log_to_s3(
            {
                "email": email,
                "action": "Fetched user preferences",
                "data": {
                    "name": name,
                    "theme": theme,
                    "favorites_count": len(favorites),
                },
            },
            prefix="logs/userprefs",
        )

        return {
            "statusCode": 200,
            "body": json.dumps(
                {"email": email, "name": name, "theme": theme, "favorites": favorites}
            ),
        }

    except Exception as e:
        log_to_s3(
            {"email": email, "exception": str(e), "event": event},
            prefix="logs/userprefs",
        )

        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Internal server error"}),
        }
