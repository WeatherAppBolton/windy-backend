#!/bin/bash
set -e
set -x

REGION="eu-north-1"

# Get AWS Account ID
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# Set role name and ARN
LAMBDA_ROLE_NAME="LambdaBasicExecutionRole"
LAMBDA_ROLE_ARN="arn:aws:iam::${ACCOUNT_ID}:role/${LAMBDA_ROLE_NAME}"

# Step 1: Create role if it doesn't exist
if ! aws iam get-role --role-name "$LAMBDA_ROLE_NAME" >/dev/null 2>&1; then
  echo "⚠️ IAM role $LAMBDA_ROLE_NAME not found. Creating..."

  cat > trust-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

  aws iam create-role \
    --role-name "$LAMBDA_ROLE_NAME" \
    --assume-role-policy-document file://trust-policy.json

  aws iam attach-role-policy \
    --role-name "$LAMBDA_ROLE_NAME" \
    --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

  echo "✅ Created IAM role: $LAMBDA_ROLE_NAME"
  echo "⏳ Waiting 15 seconds for IAM role to propagate..."
  sleep 15
else
  echo "✅ IAM role already exists: $LAMBDA_ROLE_NAME"
fi

# Step 2: Define functions to deploy
declare -A FUNCTIONS=(
  [RegisterUser]="RegisterUser.zip register_user.lambda_handler"
  [LoginUser]="LoginUser.zip login_user.lambda_handler"
  [GetUserPreferences]="GetUserPreferences.zip get_user_prefs.lambda_handler"
  [UpdateUserPreferences]="UpdateUserPreferences.zip update_user_prefs.lambda_handler"
  [GetWeatherByLocation]="GetWeatherByLocation.zip get_weather.lambda_handler"
)

# Step 3: Loop through and deploy each function
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
