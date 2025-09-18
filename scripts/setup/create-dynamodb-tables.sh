#!/bin/bash

# Create DynamoDB tables for migration testing
set -e

PROJECT_NAME="migration-demo"
RANDOM_SUFFIX=$(tail -c 6 /dev/urandom | base64 | tr -d '/' | tr -d '+')
SOURCE_REGION="us-east-1"
TARGET_REGIONS=("us-west-2" "eu-west-1")

echo "🗄️  Creating DynamoDB tables for migration testing..."

# Create source table
SOURCE_TABLE="${PROJECT_NAME}-user-data"
echo "Creating source table: ${SOURCE_TABLE} in ${SOURCE_REGION}"

aws dynamodb create-table \
    --table-name ${SOURCE_TABLE} \
    --attribute-definitions \
        AttributeName=UserID,AttributeType=S \
        AttributeName=Timestamp,AttributeType=N \
    --key-schema \
        AttributeName=UserID,KeyType=HASH \
        AttributeName=Timestamp,KeyType=RANGE \
    --billing-mode PAY_PER_REQUEST \
    --stream-specification StreamEnabled=true,StreamViewType=NEW_AND_OLD_IMAGES \
    --region ${SOURCE_REGION} \
    --tags Key=Project,Value=MigrationDemo Key=Environment,Value=Source

echo "⏳ Waiting for source table to be active..."
aws dynamodb wait table-exists --table-name ${SOURCE_TABLE} --region ${SOURCE_REGION}

# Create target tables
for region in "${TARGET_REGIONS[@]}"; do
    TARGET_TABLE="${PROJECT_NAME}-target-${region}-user-data"
    echo "Creating target table: ${TARGET_TABLE} in ${region}"
    
    aws dynamodb create-table \
        --table-name ${TARGET_TABLE} \
        --attribute-definitions \
            AttributeName=UserID,AttributeType=S \
            AttributeName=Timestamp,AttributeType=N \
        --key-schema \
            AttributeName=UserID,KeyType=HASH \
            AttributeName=Timestamp,KeyType=RANGE \
        --billing-mode PAY_PER_REQUEST \
        --region ${region} \
        --tags Key=Project,Value=MigrationDemo Key=Environment,Value=Target-${region}
    
    echo "⏳ Waiting for target table in ${region} to be active..."
    aws dynamodb wait table-exists --table-name ${TARGET_TABLE} --region ${region}
    echo "✅ Target table created: ${TARGET_TABLE} in ${region}"
done

echo "📝 Saving DynamoDB table information..."
cat > dynamodb-info.txt << EOF
SOURCE_TABLE=${SOURCE_TABLE}
SOURCE_REGION=${SOURCE_REGION}
TARGET_TABLES=(
EOF

for region in "${TARGET_REGIONS[@]}"; do
    echo "    ${PROJECT_NAME}-target-${region}-user-data" >> dynamodb-info.txt
done

echo ")" >> dynamodb-info.txt

echo "✅ All DynamoDB tables created successfully!"
echo "📄 Table information saved to dynamodb-info.txt"