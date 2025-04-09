import json
import boto3
import bcrypt

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('RegisteredUsers')

def lambda_handler(event, context):
    print("📥 EVENT:", json.dumps(event))
    
    try:
        if 'body' not in event:
            return error_response("Missing request body", 400)

        body = json.loads(event['body'])
        email = body.get('email')
        password = body.get('password')

        if not email or not password:
            return error_response("Missing email or password", 400)

        # Get user by email
        response = table.get_item(Key={'email': email})
        item = response.get('Item')

        if not item:
            return error_response("User not found", 404)

        if not bcrypt.checkpw(password.encode('utf-8'), item['password'].encode('utf-8')):
            return error_response("Incorrect password", 401)

        return success_response("Login successful")

    except Exception as e:
        print("❌ Exception:", str(e))
        return error_response(f"Server error: {str(e)}", 500)

def success_response(message):
    return {
        "statusCode": 200,
        "headers": { "Access-Control-Allow-Origin": "*" },
        "body": json.dumps({ "message": message })
    }

def error_response(message, code):
    return {
        "statusCode": code,
        "headers": { "Access-Control-Allow-Origin": "*" },
        "body": json.dumps({ "error": message })
    }
