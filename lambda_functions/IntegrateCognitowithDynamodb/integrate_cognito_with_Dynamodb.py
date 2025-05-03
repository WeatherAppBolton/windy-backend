import boto3
from datetime import datetime
from logger import log_to_s3  # Your existing utility

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("RegisteredUsers")

def lambda_handler(event, context):
    print("📥 POST-CONFIRM EVENT:", event)

    try:
        user_attrs = event["request"]["userAttributes"]
        email = user_attrs.get("email")
        name = user_attrs.get("name")

        if not email or not name:
            log_to_s3(
                {"error": "Missing name or email from Cognito trigger", "event": event},
                prefix="logs/postconfirmation"
            )
            raise ValueError("Missing required user attributes")

        # Check if user already exists
        existing = table.get_item(Key={"email": email})
        if "Item" in existing:
            log_to_s3(
                {"email": email, "warning": "User already exists in DynamoDB"},
                prefix="logs/postconfirmation"
            )
            return event  # Already exists, allow Cognito flow to continue

        # Insert default record
        table.put_item(
            Item={
                "email": email,
                "name": name,
                "password": None,
                "theme": "default",
                "favorites": [],
                "createdAt": datetime.utcnow().isoformat()
            }
        )

        log_to_s3(
            {"email": email, "name": name, "status": "Inserted via PostConfirmation"},
            prefix="logs/postconfirmation"
        )

        return event  # Allow Cognito sign-up to complete

    except Exception as e:
        log_to_s3(
            {
                "error": str(e),
                "context": "PostConfirmation",
                "event": event
            },
            prefix="logs/postconfirmation"
        )
        raise e
