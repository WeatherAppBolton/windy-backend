import boto3
import json
import os
from datetime import datetime


def log_to_s3(payload, prefix="logs"):
    s3 = boto3.client("s3")
    log_bucket = os.environ.get("LOG_BUCKET", "your-default-bucket-name")
    timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H-%M-%S")
    key = f"{prefix}/{timestamp}.json"
    s3.put_object(
        Bucket=log_bucket,
        Key=key,
        Body=json.dumps(payload),
        ContentType="application/json"
    )
