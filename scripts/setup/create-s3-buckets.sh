#!/bin/bash

# AWS Multi-Region S3 Bucket Setup
# This script creates S3 buckets in multiple regions for migration testing

set -e  # Exit on any error

# Configuration
PROJECT_NAME="migration-demo"
RANDOM_SUFFIX=$(date +%s | tail -c 6)
SOURCE_REGION="us-east-1"
TARGET_REGIONS=("us-west-2" "eu-west-1")

echo "🚀 Setting up S3 buckets for multi-region migration project..."

# Create source bucket
SOURCE_BUCKET="${PROJECT_NAME}-source-${RANDOM_SUFFIX}"
echo "Creating source bucket: ${SOURCE_BUCKET} in ${SOURCE_REGION}"

aws s3 mb s3://${SOURCE_BUCKET} --region ${SOURCE_REGION}
aws s3api put-bucket-versioning \
    --bucket ${SOURCE_BUCKET} \
    --versioning-configuration Status=Enabled

echo "✅ Source bucket created: ${SOURCE_BUCKET}"

# Create target buckets
for region in "${TARGET_REGIONS[@]}"; do
    TARGET_BUCKET="${PROJECT_NAME}-target-${region}-${RANDOM_SUFFIX}"
    echo "Creating target bucket: ${TARGET_BUCKET} in ${region}"
    
    aws s3 mb s3://${TARGET_BUCKET} --region ${region}
    aws s3api put-bucket-versioning \
        --bucket ${TARGET_BUCKET} \
        --versioning-configuration Status=Enabled
    
    echo "✅ Target bucket created: ${TARGET_BUCKET}"
done

# Save bucket names for later use
echo "📝 Saving bucket information..."
cat > bucket-info.txt << EOF
SOURCE_BUCKET=${SOURCE_BUCKET}
SOURCE_REGION=${SOURCE_REGION}
TARGET_BUCKETS=(
EOF

for region in "${TARGET_REGIONS[@]}"; do
    echo "    ${PROJECT_NAME}-target-${region}-${RANDOM_SUFFIX}" >> bucket-info.txt
done

echo ")" >> bucket-info.txt

echo "🎉 All S3 buckets created successfully!"
echo "📄 Bucket information saved to bucket-info.txt"