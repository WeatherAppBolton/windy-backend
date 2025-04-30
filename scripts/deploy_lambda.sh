#!/bin/bash
set -e
set -x

REGION="eu-north-1"
LAMBDA_ROLE_ARN="arn:aws:iam::746669220952:role/LambdaBasicExecutionRole"

declare -A FUNCTIONS=(
  [RegisterUser]="RegisterUser.zip register_user.lambda_handler"
  [LoginUser]="LoginUser.zip login_user.lambda_handler"
  [GetUserPreferences]="GetUserPreferences.zip get_user_prefs.lambda_handler"
  [UpdateUserPreferences]="UpdateUserPreferences.zip update_user_prefs.lambda_handler"
  [GetWeatherByLocation]="GetWeatherByLocation.zip get_weather.lambda_handler"
)

# Check if role ARN is valid
if ! aws iam get-role --role-name "$(basename $LAMBDA_ROLE_ARN)" --region $REGION >/dev/null 2>&1; then
  echo "❌ ERROR: IAM role $LAMBDA_ROLE_ARN not found in this account/region."
  exit 1
fi

for name in "${!FUNCTIONS[@]}"; do
  IFS=' ' read -r zip_file handler <<< "${FUNCTIONS[$name]}"
  echo "→ Deploying $name..."

  # Check if ZIP file exists
  if [[ ! -f "$zip_file" ]]; then
    echo "❌ ERROR: Zip file $zip_file not found. Skipping $name."
    continue
  fi

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
