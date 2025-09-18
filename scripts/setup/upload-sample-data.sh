#!/bin/bash

# Upload sample data to source S3 bucket
set -e

# Source the bucket info
if [ -f "bucket-info.txt" ]; then
    source bucket-info.txt
else
    echo "❌ bucket-info.txt not found. Run create-s3-buckets.sh first."
    exit 1
fi

echo "📤 Uploading sample data to source bucket: ${SOURCE_BUCKET}"

# Upload all sample files
aws s3 sync examples/sample-files/ s3://${SOURCE_BUCKET}/sample-data/ \
    --region ${SOURCE_REGION}

# Create some folder structure
aws s3 cp examples/sample-files/user-data.json \
    s3://${SOURCE_BUCKET}/databases/user-data.json \
    --region ${SOURCE_REGION}

aws s3 cp examples/sample-files/application-logs.txt \
    s3://${SOURCE_BUCKET}/logs/2024/09/application-logs.txt \
    --region ${SOURCE_REGION}

aws s3 cp examples/sample-files/app-config.yaml \
    s3://${SOURCE_BUCKET}/configs/production/app-config.yaml \
    --region ${SOURCE_REGION}

echo "📊 Verifying upload..."
aws s3 ls s3://${SOURCE_BUCKET}/ --recursive --region ${SOURCE_REGION}

echo "✅ Sample data uploaded successfully!"