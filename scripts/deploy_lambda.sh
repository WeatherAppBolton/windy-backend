#!/bin/bash
set -e
set -x

REGION="eu-north-1"

# Dynamically get the AWS Account ID
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# Set the correct role ARN for the current account
LAMBDA_ROLE_NAME="LambdaBasicExecutionRole"
LAMBDA_ROLE_ARN="arn:aws:iam::${ACCOUNT_ID}:role/${LAMBDA_ROLE_NAME}"

# Define function names, zip files, and handlers
declare -A FUNCTIONS=(
  [RegisterUser]="RegisterUser.zip register_user.lambda_handler"
  [LoginUser]="LoginUser.zip login_user.lambda_handler"
  [GetUserPreferences]="GetUserPreferences.zip get_user_prefs.lambda_handler"
  [UpdateUserPreferences]="UpdateUserPreferences.zip update_user_prefs.lambda_handler"
  [GetWeatherByLocation]="GetWeatherByLocation.zip get_weather.lambda_handler"
)

# Check if the role exists in this account
if ! aws iam get-role --role-name "$LAMBDA_ROLE_NAME" --region "$REGION" >/dev/null 2>&1; then
  echo "❌ ERROR: IAM role $LAMBDA_ROLE_ARN not found in this account ($ACCOUNT_ID) or region ($REGION)."
  exit 1
fi

# Loop through each function and deploy
for name in "${!FUNCTIONS[@]}"; do
  IFS=' ' read -r zip_file handler <<< "${FUNCTIONS[$name]}"
  echo "→ Deploying $name..."

  # Check for the existence of the zip file
  if [[ ! -f "$zip_file" ]]; then
    echo "❌ ERROR: Zip file $zip_file not found. Skipping $name."
    continue
  fi

  # Check if function exists → update or create
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
      --region "$REGION" || {
        echo "❌ ERROR: Failed to create function $name"
        exit 254
      }
  fi
done
