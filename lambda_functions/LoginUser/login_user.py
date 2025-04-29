import json
import boto3
import bcrypt
from logger import log_to_s3


dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("RegisteredUsers")


def lambda_handler(event, context):
    print("📥 EVENT:", json.dumps(event))

    try:
        if "body" not in event:
            log_to_s3({"error": "Missing body", "event": event}, prefix="logs/login")
            return error_response("Missing request body", 400)

        body = json.loads(event["body"])
        email = body.get("email")
        password = body.get("password")

        if not email or not password:
            log_to_s3(
                {"error": "Missing email or password", "body": body},
                prefix="logs/login",
            )
            return error_response("Missing email or password", 400)

        # Fetch user from DynamoDB
        response = table.get_item(Key={"email": email})
        item = response.get("Item")

        if not item:
            log_to_s3({"email": email, "error": "User not found"}, prefix="logs/login")
            return error_response("User not found", 404)

        if not bcrypt.checkpw(
            password.encode("utf-8"), item["password"].encode("utf-8")
        ):
            log_to_s3(
                {"email": email, "error": "Incorrect password"}, prefix="logs/login"
            )
            return error_response("Incorrect password", 401)

        # ✅ Login successful
        log_to_s3({"email": email, "action": "Login successful"}, prefix="logs/login")
        return success_response("Login successful")

    except Exception as e:
        log_to_s3(
            {
                "email": email if "email" in locals() else "unknown",
                "exception": str(e),
                "event": event,
            },
            prefix="logs/login",
        )
        print("❌ Exception:", str(e))
        return error_response(f"Server error: {str(e)}", 500)


def success_response(message):
    return {
        "statusCode": 200,
        "headers": {"Access-Control-Allow-Origin": "*"},
        "body": json.dumps({"message": message}),
    }


def error_response(message, code):
    return {
        "statusCode": code,
        "headers": {"Access-Control-Allow-Origin": "*"},
        "body": json.dumps({"error": message}),
    }
