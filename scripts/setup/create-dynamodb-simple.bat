@echo off
echo Creating DynamoDB tables...

echo Creating source table in us-east-1...
aws dynamodb create-table ^
    --table-name migration-demo-user-data ^
    --attribute-definitions AttributeName=UserID,AttributeType=S AttributeName=Timestamp,AttributeType=N ^
    --key-schema AttributeName=UserID,KeyType=HASH AttributeName=Timestamp,KeyType=RANGE ^
    --billing-mode PAY_PER_REQUEST ^
    --stream-specification StreamEnabled=true,StreamViewType=NEW_AND_OLD_IMAGES ^
    --region us-east-1

echo Waiting for table to be active...
aws dynamodb wait table-exists --table-name migration-demo-user-data --region us-east-1

echo Creating target table in us-west-2...
aws dynamodb create-table ^
    --table-name migration-demo-target-us-west-2-user-data ^
    --attribute-definitions AttributeName=UserID,AttributeType=S AttributeName=Timestamp,AttributeType=N ^
    --key-schema AttributeName=UserID,KeyType=HASH AttributeName=Timestamp,KeyType=RANGE ^
    --billing-mode PAY_PER_REQUEST ^
    --region us-west-2

echo Creating target table in eu-west-1...
aws dynamodb create-table ^
    --table-name migration-demo-target-eu-west-1-user-data ^
    --attribute-definitions AttributeName=UserID,AttributeType=S AttributeName=Timestamp,AttributeType=N ^
    --key-schema AttributeName=UserID,KeyType=HASH AttributeName=Timestamp,KeyType=RANGE ^
    --billing-mode PAY_PER_REQUEST ^
    --region eu-west-1

echo All tables created successfully!