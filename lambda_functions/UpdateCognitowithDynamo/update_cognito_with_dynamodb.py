import json
import boto3
import hmac
import hashlib
import base64
from botocore.exceptions import ClientError
from logger import log_to_s3  # Make sure logger.py is available or layered

cognito = boto3.client('cognito-idp')
dynamo = boto3.resource('dynamodb')

USER_POOL_ID = 'eu-north-1_dogITdZlI'
CLIENT_ID = '2o0nmr5jkldo6ghja66ffvihra'
CLIENT_SECRET = 'l1remjan3uumvk4eim1up8jsh5s02mjc49a3fpt52i0a9om8n1l'
TABLE_NAME = 'RegisteredUsers'

def get_secret_hash(username):
    message = username + CLIENT_ID
    dig = hmac.new(
        CLIENT_SECRET.encode('utf-8'),
        msg=message.encode('utf-8'),
        digestmod=hashlib.sha256
    ).digest()
    return base64.b64encode(dig).decode()

def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])

        email = body.get('email')
        new_email = body.get('newEmail')
        name = body.get('name')
        password = body.get('password')
        current_password = body.get('currentPassword')

        if not email:
            return respond(400, "Missing required field: email")

        changed_fields = []

        # STEP 1: Update Cognito Attributes
        user_attributes = []
        if new_email:
            user_attributes.extend([
                {'Name': 'email', 'Value': new_email},
                {'Name': 'email_verified', 'Value': 'true'}
            ])
            changed_fields.append("email")
        if name:
            user_attributes.append({'Name': 'name', 'Value': name})
            changed_fields.append("name")

        if user_attributes:
            cognito.admin_update_user_attributes(
                UserPoolId=USER_POOL_ID,
                Username=email,
                UserAttributes=user_attributes
            )

        # STEP 2: Secure Password Change
        if password:
            if not current_password:
                return respond(400, "Current password is required to change password.")

            try:
                cognito.initiate_auth(
                    AuthFlow='USER_PASSWORD_AUTH',
                    AuthParameters={
                        'USERNAME': email,
                        'PASSWORD': current_password,
                        'SECRET_HASH': get_secret_hash(email)
                    },
                    ClientId=CLIENT_ID
                )
            except ClientError as auth_error:
                print("❌ Re-auth failed:", auth_error.response['Error'])
                return respond(401, "Current password is incorrect.")

            cognito.admin_set_user_password(
                UserPoolId=USER_POOL_ID,
                Username=email,
                Password=password,
                Permanent=True
            )
            changed_fields.append("password")

        # STEP 3: Update DynamoDB
        table = dynamo.Table(TABLE_NAME)

        if new_email:
            existing = table.get_item(Key={'email': email})
            if 'Item' not in existing:
                return respond(404, "User not found in DynamoDB")

            user = existing['Item']
            user['email'] = new_email
            table.put_item(Item=user)
            table.delete_item(Key={'email': email})
        elif name:
            table.update_item(
                Key={'email': email},
                UpdateExpression="SET #nm = :name",
                ExpressionAttributeNames={'#nm': 'name'},
                ExpressionAttributeValues={':name': name}
            )

        # ✅ Logging to S3
        log_to_s3({
            "email": new_email or email,
            "action": "Updated user profile",
            "fieldsChanged": changed_fields
        }, prefix="logs/userupdates")

        return respond(200, "✅ Cognito and DynamoDB updated successfully.")

    except ClientError as e:
        print("ClientError:", e.response['Error'])
        return respond(500, f"Client error: {e.response['Error']['Message']}")
    except Exception as e:
        print("Exception:", e)
        return respond(500, "Internal server error")

def respond(code, message):
    return {
        "statusCode": code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"message": message})
    }
