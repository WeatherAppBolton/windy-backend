#!/bin/bash
set -e
set -x

REGION="eu-north-1"

# Get AWS Account ID
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# Define the pre-existing IAM role ARN
LAMBDA_ROLE_NAME="LambdaBasicExecutionRole"
LAMBDA_ROLE_ARN="arn:aws:iam::${ACCOUNT_ID}:role/${LAMBDA_ROLE_NAME}"

echo "🔐 Using existing Lambda execution role: $LAMBDA_ROLE_ARN"

# Define functions to deploy
declare -A FUNCTIONS=(
  [RegisterUser]="RegisterUser.zip register_user.lambda_handler"
  [LoginUser]="LoginUser.zip login_user.lambda_handler"
  [GetUserPreferences]="GetUserPreferences.zip get_user_prefs.lambda_handler"
  [UpdateUserPreferences]="UpdateUserPreferences.zip update_user_prefs.lambda_handler"
  [GetWeatherByLocation]="GetWeatherByLocation.zip get_weather.lambda_handler"
)

# Deploy each function
for name in "${!FUNCTIONS[@]}"; do
  IFS=' ' read -r zip_file handler <<< "${FUNCTIONS[$name]}"
  echo "→ Deploying Lambda function: $name"

  if [[ ! -f "$zip_file" ]]; then
    echo "❌ ERROR: Missing zip file: $zip_file. Skipping $name"
    continue
  fi

  if aws lambda get-function --function-name "$name" --region "$REGION" >/dev/null 2>&1; then
    echo "✅ Updating existing Lambda: $name"
    aws lambda update-function-code \
      --function-name "$name" \
      --zip-file "fileb://${zip_file}" \
      --region "$REGION"
  else
    echo "🆕 Creating new Lambda: $name"
    if ! aws lambda create-function \
      --function-name "$name" \
      --runtime python3.11 \
      --role "$LAMBDA_ROLE_ARN" \
      --handler "$handler" \
      --zip-file "fileb://${zip_file}" \
      --region "$REGION"; then
        echo "❌ ERROR: Failed to create function $name"
        echo "📦 ZIP File: $zip_file"
        echo "📄 Handler: $handler"
        echo "🔐 Role ARN: $LAMBDA_ROLE_ARN"
        echo "🌍 Region: $REGION"
        exit 254
    fi
  fi
done

echo "✅ All Lambda functions deployed successfully."
