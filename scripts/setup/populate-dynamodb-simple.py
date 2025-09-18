#!/usr/bin/env python3

import boto3
import time
import json
from decimal import Decimal

def populate_source_table():
    """Populate source DynamoDB table with sample data"""
    
    try:
        # Initialize DynamoDB resource
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table_name = 'migration-demo-user-data'
        table = dynamodb.Table(table_name)
        
        print(f"📝 Populating {table_name} with sample data...")
        
        # Simple sample data (using strings and numbers only)
        sample_users = [
            {
                'UserID': 'user001',
                'Timestamp': 1695020400,  # Fixed timestamp
                'Name': 'John Doe',
                'Email': 'john.doe@example.com',
                'Department': 'Engineering'
            },
            {
                'UserID': 'user002', 
                'Timestamp': 1695020401,
                'Name': 'Jane Smith',
                'Email': 'jane.smith@example.com',
                'Department': 'Marketing'
            },
            {
                'UserID': 'user003',
                'Timestamp': 1695020402,
                'Name': 'Bob Johnson',
                'Email': 'bob.johnson@example.com', 
                'Department': 'Sales'
            }
        ]
        
        # Insert items one by one (more reliable)
        for user in sample_users:
            try:
                table.put_item(Item=user)
                print(f"✅ Added user: {user['Name']} ({user['UserID']})")
            except Exception as e:
                print(f"❌ Error adding {user['UserID']}: {e}")
        
        # Verify data
        print("📊 Verifying data insertion...")
        response = table.scan(Limit=10)
        print(f"Total items found: {response['Count']}")
        
        for item in response['Items']:
            print(f"  - {item['Name']} ({item['UserID']})")
        
        print("🎉 Sample data populated successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error populating table: {str(e)}")
        print("💡 Make sure the table exists and you have proper AWS credentials")
        return False

if __name__ == "__main__":
    # Check if boto3 is installed
    try:
        import boto3
        print("✅ boto3 is available")
    except ImportError:
        print("❌ boto3 not installed. Run: pip3 install boto3")
        exit(1)
    
    # Check AWS credentials
    try:
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        print(f"✅ AWS credentials working. Account: {identity['Account']}")
    except Exception as e:
        print(f"❌ AWS credentials issue: {e}")
        exit(1)
    
    populate_source_table()