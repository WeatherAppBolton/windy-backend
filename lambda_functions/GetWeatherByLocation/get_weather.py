import json
import requests
import os

def lambda_handler(event, context):
    location = event.get("queryStringParameters", {}).get("location", "London")

    api_key = os.environ.get("WEATHER_API_KEY")
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
