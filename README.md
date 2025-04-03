# 🌤️ Weather App Backend
This is the backend of the Weather App, a serverless weather forecast application that processes requests and fetches real-time weather data using OpenWeather API. The backend is built with AWS Lambda and API Gateway to ensure high availability, scalability, and low-cost operations.

## 🌍 Live API Endpoint
🔗 Base API URL: https://j69ymxtksk.execute-api.eu-north-1.amazonaws.com/weather

🔗unique API URL : https://j69ymxtksk.execute-api.eu-north-1.amazonaws.com/weather?location=London
## 🏗️ Project Structure
```
/src
├──.gitignore 
├── README.md
├── lamda functions
├── requirements.txt
```

## ⚡ Technologies Used
- **Backend Framework:** python (Express-like routing with AWS Lambda)
- **API Gateway:**  API Gateway for routing and request handling
- **Serverless Compute:** AWS Lambda for executing backend logic
- **Weather Data Source:** OpenWeatherMap API
- **Database (Optional):** 
- **CI/CD:** 

## 🛠️ Installation & Setup
### 1️⃣ Clone the repository
```sh
git clone https://github.com/WeatherAppBolton/Back-End.git
cd weather-app-backend
```

### 2️⃣ Install dependencies
```sh
npm install
```

### 3️⃣ Set up environment variables
Create a `.env` file in the root directory and add the following:
```
OPENWEATHER_API_KEY=your_openweather_api_key
AWS_REGION=your_aws_region
python=your_python_table_name (if using a database)
```

### 4️⃣ Run the application locally
You can use AWS SAM CLI or Serverless Framework to test locally:
```sh
sam local start-api
```
Or, if using Serverless Framework:
```sh
serverless offline
```

### 5️⃣ Deploy to AWS
```sh
serverless deploy
```

## 📌 API Endpoints
| Method | Endpoint | Description |
|--------|-------------|-------------------------|
| GET | `/weather?location=London` | Fetches weather data for the given city |

## ✅ Testing

```

## 🚀 Deployment & CI/CD


---
### 🔥 Contributors & Support
Feel free to contribute or raise issues in the repository!
📧 Contact: antonio, bilal, prateek, mohit, raj, sb16crt




