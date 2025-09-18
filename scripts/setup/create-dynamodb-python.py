#!/usr/bin/env python3

import boto3
import time
from botocore.exceptions import ClientError

def create_dynamodb_table(table_name, region):
    """Create a DynamoDB table in specified region"""
    
    try:
        dynamodb = boto3.client('dynamodb', region_name=region)
        
        print(f"Creating table: {table_name} in {region}")
        
        # Create table
        response = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {
                    'AttributeName': 'UserID',
                    'KeyType': 'HASH'  # Partition key
                },
                {
                    'AttributeName': 'Timestamp', 
                    'KeyType': 'RANGE'  # Sort key
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'UserID',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'Timestamp',
                    'AttributeType': 'N'
                }
            ],
            BillingMode='PAY_PER_REQUEST',  # On-demand pricing
            Tags=[
                {
                    'Key': 'Project',
                    'Value': 'MigrationDemo'
                },
                {
                    'Key': 'Environment', 
                    'Value': f'Target-{region}' if 'target' in table_name else 'Source'
                }
            ]
        )
        
        print(f"⏳ Waiting for {table_name} to be active...")
        
        # Wait for table to be created
        waiter = dynamodb.get_waiter('table_exists')
        waiter.wait(TableName=table_name)
        
        print(f"✅ Table {table_name} created successfully in {region}")
        return True
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            print(f"⚠️  Table {table_name} already exists in {region}")
            return True
        else:
            print(f"❌ Error creating table {table_name}: {e}")
            return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    """Main function to create all DynamoDB tables"""
    
    project_name = "migration-demo"
    source_region = "us-east-1"
    target_regions = ["us-west-2", "eu-west-1"]
    
    print("🗄️  Creating DynamoDB tables for migration testing...")
    
    # Create source table
    source_table = f"{project_name}-user-data"
    success = create_dynamodb_table(source_table, source_region)
    
    if not success:
        print("❌ Failed to create source table. Exiting.")
        return
    
    # Create target tables
    for region in target_regions:
        target_table = f"{project_name}-target-{region}-user-data"
        create_dynamodb_table(target_table, region)
    
    # Save table information
    print("📝 Saving DynamoDB table information...")
    with open('dynamodb-info.txt', 'w') as f:
        f.write(f"SOURCE_TABLE={source_table}\n")
        f.write(f"SOURCE_REGION={source_region}\n")
        f.write("TARGET_TABLES=(\n")
        for region in target_regions:
            f.write(f"    {project_name}-target-{region}-user-data\n")
        f.write(")\n")
    
    print("🎉 All DynamoDB setup completed!")
    
    # Verify tables
    print("📊 Verifying created tables:")
    for region in [source_region] + target_regions:
        try:
            dynamodb = boto3.client('dynamodb', region_name=region)
            tables = dynamodb.list_tables()['TableNames']
            migration_tables = [t for t in tables if 'migration-demo' in t]
            print(f"  {region}: {migration_tables}")
        except Exception as e:
            print(f"  {region}: Error listing tables - {e}")

if __name__ == "__main__":
    main()