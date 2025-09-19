#!/usr/bin/env python3

import boto3
import json
import time
from botocore.exceptions import ClientError
from decimal import Decimal

class DynamoDBStreamSync:
    def __init__(self, source_table, source_region, target_configs):
        self.source_table = source_table
        self.source_region = source_region
        self.target_configs = target_configs
        self.source_dynamodb = boto3.client('dynamodb', region_name=source_region)
        
    def enable_streams(self):
        """Enable DynamoDB Streams on source table"""
        try:
            response = self.source_dynamodb.update_table(
                TableName=self.source_table,
                StreamSpecification={
                    'StreamEnabled': True,
                    'StreamViewType': 'NEW_AND_OLD_IMAGES'
                }
            )
            
            # Wait for table to be updated
            waiter = self.source_dynamodb.get_waiter('table_exists')
            waiter.wait(TableName=self.source_table)
            
            # Get stream ARN
            table_description = self.source_dynamodb.describe_table(
                TableName=self.source_table
            )
            
            stream_arn = table_description['Table'].get('LatestStreamArn')
            if stream_arn:
                print(f"✅ DynamoDB Streams enabled")
                print(f"📝 Stream ARN: {stream_arn}")
                return stream_arn
            else:
                print("❌ No stream ARN found")
                return None
                
        except ClientError as e:
            print(f"❌ Error enabling streams: {e}")
            return None
    
    def simulate_real_time_sync(self):
        """Simulate real-time synchronization manually"""
        print("🔄 Starting manual sync simulation...")
        
        # Get all records from source
        source_resource = boto3.resource('dynamodb', region_name=self.source_region)
        source_table = source_resource.Table(self.source_table)
        
        try:
            response = source_table.scan()
            source_items = response['Items']
            print(f"📊 Found {len(source_items)} items in source table")
            
            # Sync to each target
            for target_config in self.target_configs:
                self._sync_to_target(source_items, target_config)
            
            return True
            
        except ClientError as e:
            print(f"❌ Error during sync: {e}")
            return False
    
    def _sync_to_target(self, items, target_config):
        """Sync items to a specific target table"""
        target_table = target_config['table']
        target_region = target_config['region']
        
        print(f"🎯 Syncing to {target_table} in {target_region}")
        
        try:
            target_resource = boto3.resource('dynamodb', region_name=target_region)
            table = target_resource.Table(target_table)
            
            # Batch write to target
            with table.batch_writer() as batch:
                for item in items:
                    # Convert float to Decimal for DynamoDB
                    converted_item = self._convert_floats_to_decimal(item)
                    batch.put_item(Item=converted_item)
                    
            print(f"✅ Synced {len(items)} items to {target_table}")
            
        except ClientError as e:
            print(f"❌ Error syncing to {target_table}: {e}")
    
    def _convert_floats_to_decimal(self, item):
        """Convert float values to Decimal for DynamoDB compatibility"""
        if isinstance(item, dict):
            return {k: self._convert_floats_to_decimal(v) for k, v in item.items()}
        elif isinstance(item, list):
            return [self._convert_floats_to_decimal(v) for v in item]
        elif isinstance(item, float):
            return Decimal(str(item))
        else:
            return item
    
    def test_sync_by_adding_data(self):
        """Test sync by adding new data and verifying replication"""
        print("🧪 Testing real-time sync by adding new data...")
        
        # Add test record to source
        test_item = {
            'UserID': 'test-sync-user',
            'Timestamp': int(time.time()),
            'Name': 'Sync Test User',
            'Email': 'synctest@example.com',
            'Department': 'Testing',
            'SyncTest': True
        }
        
        try:
            source_resource = boto3.resource('dynamodb', region_name=self.source_region)
            source_table = source_resource.Table(self.source_table)
            
            source_table.put_item(Item=test_item)
            print(f"✅ Added test item to source: {test_item['UserID']}")
            
            # Wait a moment, then manually sync
            time.sleep(2)
            self.simulate_real_time_sync()
            
            # Verify in targets
            for target_config in self.target_configs:
                self._verify_item_in_target(test_item['UserID'], target_config)
                
        except ClientError as e:
            print(f"❌ Error during sync test: {e}")
    
    def _verify_item_in_target(self, user_id, target_config):
        """Verify item exists in target table"""
        target_table = target_config['table']
        target_region = target_config['region']
        
        try:
            target_resource = boto3.resource('dynamodb', region_name=target_region)
            table = target_resource.Table(target_table)
            
            # Query for the test item
            response = table.query(
                KeyConditionExpression=boto3.dynamodb.conditions.Key('UserID').eq(user_id)
            )
            
            if response['Items']:
                print(f"✅ Verified sync to {target_table}: Found {len(response['Items'])} items")
            else:
                print(f"❌ Sync verification failed for {target_table}: No items found")
                
        except ClientError as e:
            print(f"❌ Error verifying {target_table}: {e}")

def main():
    """Main function for DynamoDB sync setup"""
    
    # Load configuration
    try:
        with open('dynamodb-info.txt', 'r') as f:
            content = f.read()
            
        for line in content.split('\n'):
            if line.startswith('SOURCE_TABLE='):
                source_table = line.split('=')[1]
            elif line.startswith('SOURCE_REGION='):
                source_region = line.split('=')[1]
        
        target_configs = [
            {
                "table": "migration-demo-target-us-west-2-user-data",
                "region": "us-west-2"
            },
            {
                "table": "migration-demo-target-eu-west-1-user-data", 
                "region": "eu-west-1"
            }
        ]
        
    except Exception as e:
        print(f"❌ Error loading configuration: {e}")
        return False
    
    # Setup sync
    sync_manager = DynamoDBStreamSync(source_table, source_region, target_configs)
    
    # Enable streams (for real-world Lambda integration)
    stream_arn = sync_manager.enable_streams()
    
    # Simulate real-time sync
    success = sync_manager.simulate_real_time_sync()
    
    # Test with new data
    sync_manager.test_sync_by_adding_data()
    
    return success

if __name__ == "__main__":
    main()