# 🌤️ Weather App Backend
This is the backend of the Weather App, a serverless weather forecast application that processes requests and fetches real-time weather data using OpenWeather API. The backend is built with AWS Lambda and API Gateway to ensure high availability, scalability, and low-cost operations.

## 🌍 Live API Endpoint
🔗 Base API URL: https://j69ymxtksk.execute-api.eu-north-1.amazonaws.com/weather

## 🏗️ Project Structure
```
/src
├── handlers          # Lambda function handlers for API requests
├── services         # Business logic and integration with OpenWeather API
├── utils            # Utility functions for data processing and error handling
├── config           # Environment variables and API keys management
├── tests            # Unit and integration tests
```

## ⚡ Technologies Used
- **Backend Framework:** Node.js (Express-like routing with AWS Lambda)
- **API Gateway:** AWS API Gateway for routing and request handling
- **Serverless Compute:** AWS Lambda for executing backend logic
- **Weather Data Source:** OpenWeatherMap API
- **Database (Optional):** DynamoDB (for storing user preferences or historical data)
- **CI/CD:** GitHub Actions + AWS CodePipeline

## 🛠️ Installation & Setup
### 1️⃣ Clone the repository
```sh
git clone https://github.com/YOUR_USERNAME/weather-app-backend.git
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
DYNAMODB_TABLE=your_dynamodb_table_name (if using a database)
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
| GET | `/weather?city=London` | Fetches weather data for the given city |
| POST | `/preferences` | Saves user preferences (if applicable) |
| GET | `/preferences/:userId` | Retrieves user preferences (if applicable) |

## ✅ Testing
Run unit tests using:
```sh
npm test
```

## 🚀 Deployment & CI/CD
The backend is deployed using AWS CodePipeline with GitHub Actions automating the deployment process. Ensure AWS credentials are set up in your CI/CD pipeline for smooth deployment.

---
### 🔥 Contributors & Support
Feel free to contribute or raise issues in the repository!
📧 Contact: antonio, bilal, prateek, mohit, raj




