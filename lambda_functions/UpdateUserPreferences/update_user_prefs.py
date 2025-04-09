import boto3
import json
import bcrypt

def lambda_handler(event, context):
    body = json.loads(event['body'])

    previous_email = body.get('previousEmail') or body.get('email')
    new_email = body.get('email')
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('RegisteredUsers')

    if not previous_email:
        return {"statusCode": 400, "body": json.dumps({"error": "Missing email"})}

    response = table.get_item(Key={'email': previous_email})
    if 'Item' not in response:
        return {"statusCode": 404, "body": json.dumps({"error": "User not found"})}

    item = response['Item']

    # Update other fields
    for k in ['name', 'theme', 'favorites']:
        if k in body:
            item[k] = body[k]

    # Securely hash password
    if 'password' in body:
        item['password'] = bcrypt.hashpw(body['password'].encode(), bcrypt.gensalt()).decode()

    # Change email logic
    item['email'] = new_email
    table.put_item(Item=item)

    if previous_email != new_email:
        table.delete_item(Key={'email': previous_email})

    return {
        "statusCode": 200,
        "body": json.dumps({"message": "Update successful"})
    }
