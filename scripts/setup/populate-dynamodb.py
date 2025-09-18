#!/usr/bin/env python3

import boto3
import json
import time
from datetime import datetime
from decimal import Decimal

def populate_source_table():
    """Populate source DynamoDB table with sample data"""
    
    # Initialize DynamoDB resource
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table_name = 'migration-demo-user-data'
    
    try:
        table = dynamodb.Table(table_name)
        
        print(f"📝 Populating {table_name} with sample data...")
        
        # Sample user data
        sample_users = [
            {
                'UserID': 'user001',
                'Timestamp': int(time.time()),
                'Name': 'John Doe',
                'Email': 'john.doe@example.com',
                'Department': 'Engineering',
                'JoinDate': '2023-01-15',
                'Status': 'Active',
                'LastLogin': int(time.time()) - 3600
            },
            {
                'UserID': 'user002', 
                'Timestamp': int(time.time()) + 1,
                'Name': 'Jane Smith',
                'Email': 'jane.smith@example.com',
                'Department': 'Marketing',
                'JoinDate': '2023-03-20',
                'Status': 'Active',
                'LastLogin': int(time.time()) - 7200
            },
            {
                'UserID': 'user003',
                'Timestamp': int(time.time()) + 2,
                'Name': 'Bob Johnson',
                'Email': 'bob.johnson@example.com', 
                'Department': 'Sales',
                'JoinDate': '2023-06-10',
                'Status': 'Active',
                'LastLogin': int(time.time()) - 1800
            },
            {
                'UserID': 'user004',
                'Timestamp': int(time.time()) + 3,
                'Name': 'Alice Brown',
                'Email': 'alice.brown@example.com',
                'Department': 'HR',
                'JoinDate': '2023-08-05',
                'Status': 'Inactive',
                'LastLogin': int(time.time()) - 86400
            },
            {
                'UserID': 'user005',
                'Timestamp': int(time.time()) + 4,
                'Name': 'Charlie Wilson',
                'Email': 'charlie.wilson@example.com',
                'Department': 'Engineering',
                'JoinDate': '2024-01-12',
                'Status': 'Active', 
                'LastLogin': int(time.time()) - 600
            }
        ]
        
        # Insert items
        with table.batch_writer() as batch:
            for user in sample_users:
                batch.put_item(Item=user)
                print(f"✅ Added user: {user['Name']} ({user['UserID']})")
        
        print("📊 Verifying data insertion...")
        response = table.scan()
        print(f"Total items in table: {response['Count']}")
        
        print("🎉 Sample data populated successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error populating table: {str(e)}")
        return False

if __name__ == "__main__":
    populate_source_table()