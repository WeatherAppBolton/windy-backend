#!/bin/bash

REGION="eu-north-1"
LAMBDA_ROLE_ARN="arn:aws:iam::746669220952:role/LambdaBasicExecutionRole"

declare -A FUNCTIONS=(
  [RegisterUser]="RegisterUser.zip register_user.lambda_handler"
  [LoginUser]="LoginUser.zip login_user.lambda_handler"
  [GetUserPreferences]="GetUserPreferences.zip get_user_prefs.lambda_handler"
  [UpdateUserPreferences]="UpdateUserPreferences.zip update_user_prefs.lambda_handler"
  [GetWeatherByLocation]="GetWeatherByLocation.zip get_weather.lambda_handler"
)

for name in "${!FUNCTIONS[@]}"; do
  IFS=' ' read -r zip_file handler <<< "${FUNCTIONS[$name]}"
  echo "→ Deploying $name..."

  if aws lambda get-function --function-name "$name" --region "$REGION" >/dev/null 2>&1; then
    echo "✅ Updating $name"
    aws lambda update-function-code \
      --function-name "$name" \
      --zip-file "fileb://${zip_file}" \
      --region "$REGION"
  else
    echo "🆕 Creating $name"
    aws lambda create-function \
      --function-name "$name" \
      --runtime python3.11 \
      --role "$LAMBDA_ROLE_ARN" \
      --handler "$handler" \
      --zip-file "fileb://${zip_file}" \
      --region "$REGION"
  fi
done
