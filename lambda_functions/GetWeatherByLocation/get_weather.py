import json
import requests
import os

def lambda_handler(event, context):
    params = event.get("queryStringParameters", {})
    location = params.get("location")
    lat = params.get("lat")
    lon = params.get("lon")
    api_key = os.environ.get("WEATHER_API_KEY")

    try:
        if lat and lon:
            # 🌟 Directly fetch weather using lat/lon
            weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"
        elif location:
            # 🌟 Otherwise fetch by city name
            weather_url = f"https://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&units=metric"
        else:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "No valid location provided"})
            }

        weather_resp = requests.get(weather_url, timeout=3)
        weather_data = weather_resp.json()

        temp = weather_data['main']['temp']
        condition = weather_data['weather'][0]['main']

        # 🌟 Set the city name properly (whether from GPS or city search)
        if lat and lon:
            location_name = weather_data['name']
        else:
            location_name = location

        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Content-Type": "application/json"
            },
            "body": json.dumps({
                "location": location_name,
                "temperature": temp,
                "condition": condition
            })
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
