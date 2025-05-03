import boto3
import json
import bcrypt
from logger import log_to_s3


dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("RegisteredUsers")


def lambda_handler(event, context):
    try:
        if "body" not in event:
            log_to_s3(
                {"error": "Missing request body", "event": event},
                prefix="logs/updateuserpreferences",
            )
            return error_response("Missing request body", 400)

        body = json.loads(event["body"])

        previous_email = body.get("previousEmail") or body.get("email")
        new_email = body.get("email")

        if not previous_email or not new_email:
            log_to_s3(
                {"error": "Missing email", "body": body},
                prefix="logs/updateuserpreferences",
            )
            return error_response("Missing email", 400)

        # Fetch current user data
        response = table.get_item(Key={"email": previous_email})
        if "Item" not in response:
            log_to_s3(
                {"email": previous_email, "error": "User not found"},
                prefix="logs/updateuserpreferences",
            )
            return error_response("User not found", 404)

        item = response["Item"]

        # Update name, theme, favorites
        for k in ["name", "theme", "favorites"]:
            if k in body:
                item[k] = body[k]

        # Update password if present
        if "password" in body:
            item["password"] = bcrypt.hashpw(
                body["password"].encode(), bcrypt.gensalt()
            ).decode()

        # Update email
        item["email"] = new_email
        table.put_item(Item=item)

        # Delete old record if email changed
        if previous_email != new_email:
            table.delete_item(Key={"email": previous_email})

        log_to_s3(
            {
                "email": new_email,
                "action": "User updated",
                "changed": list(body.keys()),
            },
            prefix="logs/updateuserpreferences",
        )

        return success_response("Update successful")

    except Exception as e:
        log_to_s3(
            {"error": str(e), "event": event}, prefix="logs/updateuserpreferences"
        )

        return error_response("Server error: " + str(e), 500)


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
