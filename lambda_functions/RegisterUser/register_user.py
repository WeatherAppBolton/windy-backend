import json
import boto3
import bcrypt
import re
from datetime import datetime
from logger import log_to_s3


dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("RegisteredUsers")


def lambda_handler(event, context):
    print("📥 EVENT:", json.dumps(event))

    try:
        if "body" not in event:
            log_to_s3(
                {"error": "Missing body", "event": event}, prefix="logs/registeruser"
            )
            return error_response("Missing request body", 400)

        body = json.loads(event["body"])
        email = body.get("email")
        password = body.get("password")
        name = body.get("name")

        if not name or not email or not password:
            log_to_s3(
                {"error": "Missing required fields", "body": body},
                prefix="logs/registeruser",
            )
            return error_response("All fields are required", 400)

        if not validate_password(password):
            log_to_s3(
                {"email": email, "error": "Password format invalid"},
                prefix="logs/registeruser",
            )
            return error_response(
                "Password must be 8–12 chars, include upper, lower, digit, special", 400
            )

        # Check if user already exists
        response = table.get_item(Key={"email": email})
        if "Item" in response:
            log_to_s3(
                {"email": email, "error": "User already exists"},
                prefix="logs/registeruser",
            )
            return error_response("User already exists", 409)

        # Hash and save
        hashed_pw = bcrypt.hashpw(
            password.encode("utf-8"), bcrypt.gensalt(rounds=8)
        ).decode("utf-8")

        table.put_item(
            Item={
                "email": email,
                "name": name,
                "password": hashed_pw,
                "createdAt": datetime.utcnow().isoformat(),
            }
        )

        log_to_s3(
            {"email": email, "name": name, "action": "User registered successfully"},
            prefix="logs/registeruser",
        )

        return success_response("User registered successfully")

    except Exception as e:
        log_to_s3(
            {
                "email": email if "email" in locals() else "unknown",
                "exception": str(e),
                "event": event,
            },
            prefix="logs/registeruser",
        )

        print("❌ Exception:", str(e))
        return error_response("Server error: " + str(e), 500)


def validate_password(pw):
    return bool(re.match(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^\w\s]).{8,12}$", pw))


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
