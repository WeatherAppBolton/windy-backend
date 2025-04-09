import json
import requests

def lambda_handler(event, context):
    location = event.get("queryStringParameters", {}).get("location", "London")

    api_key = "3e1551bf87cae22bfd3014698a68ece2"  # my personal key
    url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&units=metric"
    
    try:
        response = requests.get(url)
        data = response.json()
        temp = data['main']['temp']

        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",  # enables browser access
                "Content-Type": "application/json"
            },
            "body": json.dumps({
                "location": location,
                "temperature": temp
            })
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
