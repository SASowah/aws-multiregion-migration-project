#!/usr/bin/env python3

import boto3
import json
from botocore.exceptions import ClientError

class S3ReplicationSetup:
    def __init__(self, source_bucket, source_region):
        self.source_bucket = source_bucket
        self.source_region = source_region
        self.s3_client = boto3.client('s3', region_name=source_region)
        self.iam_client = boto3.client('iam', region_name=source_region)
        
    def create_replication_role(self):
        """Create IAM role for S3 Cross-Region Replication"""
        
        role_name = "S3-Replication-Role"
        
        # Trust policy for S3 service
        trust_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "s3.amazonaws.com"
                    },
                    "Action": "sts:AssumeRole"
                }
            ]
        }
        
        try:
            # Create role
            response = self.iam_client.create_role(
                RoleName=role_name,
                AssumeRolePolicyDocument=json.dumps(trust_policy),
                Description="Role for S3 Cross-Region Replication"
            )
            
            print(f"✅ Created IAM role: {role_name}")
            
            # Attach AWS managed policy
            self.iam_client.attach_role_policy(
                RoleName=role_name,
                PolicyArn="arn:aws:iam::aws:policy/service-role/AWSS3ReplicationServiceRolePolicy"
            )
            
            role_arn = response['Role']['Arn']
            print(f"✅ Role ARN: {role_arn}")
            return role_arn
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'EntityAlreadyExists':
                # Role already exists, get its ARN
                response = self.iam_client.get_role(RoleName=role_name)
                role_arn = response['Role']['Arn']
                print(f"✅ Using existing role: {role_arn}")
                return role_arn
            else:
                print(f"❌ Error creating role: {e}")
                return None
    
    def enable_versioning(self, bucket, region):
        """Enable versioning on bucket (required for replication)"""
        try:
            s3_client = boto3.client('s3', region_name=region)
            s3_client.put_bucket_versioning(
                Bucket=bucket,
                VersioningConfiguration={'Status': 'Enabled'}
            )
            print(f"✅ Enabled versioning on {bucket}")
            return True
        except ClientError as e:
            print(f"❌ Error enabling versioning on {bucket}: {e}")
            return False
    
    def setup_replication_configuration(self, target_configs, role_arn):
        """Setup Cross-Region Replication configuration with updated schema"""
        
        replication_config = {
            'Role': role_arn,
            'Rules': []
        }
        
        # Create replication rule for each target
        for i, target in enumerate(target_configs):
            rule = {
                'ID': f'ReplicationRule{i+1}',
                'Status': 'Enabled',
                'Priority': i + 1,
                'Filter': {'Prefix': ''},  # Replicate all objects
                'DeleteMarkerReplication': {'Status': 'Enabled'},  # Required field
                'Destination': {
                    'Bucket': f"arn:aws:s3:::{target['bucket']}",
                    'StorageClass': 'STANDARD_IA',  # Cost optimization
                    'ReplicationTime': {
                        'Status': 'Enabled',
                        'Time': {
                            'Minutes': 15
                        }
                    },
                    'Metrics': {
                        'Status': 'Enabled',
                        'EventThreshold': {
                            'Minutes': 15
                        }
                    }
                }
            }
            replication_config['Rules'].append(rule)
        
        try:
            self.s3_client.put_bucket_replication(
                Bucket=self.source_bucket,
                ReplicationConfiguration=replication_config
            )
            print(f"✅ Configured replication for {self.source_bucket}")
            return True
            
        except ClientError as e:
            print(f"❌ Error setting up replication: {e}")
            # Print more detailed error information
            print(f"🔍 Error details: {e.response.get('Error', {})}")
            return False
    
    def setup_complete_replication(self, target_configs):
        """Complete replication setup process"""
        print(f"🔄 Setting up S3 Cross-Region Replication...")
        
        # Step 1: Create replication role
        role_arn = self.create_replication_role()
        if not role_arn:
            return False
        
        # Step 2: Enable versioning on all buckets
        if not self.enable_versioning(self.source_bucket, self.source_region):
            return False
            
        for target in target_configs:
            if not self.enable_versioning(target['bucket'], target['region']):
                return False
        
        # Step 3: Setup replication configuration
        # Wait a moment for role to be ready
        import time
        print("⏳ Waiting for IAM role to be ready...")
        time.sleep(10)
        
        if not self.setup_replication_configuration(target_configs, role_arn):
            return False
        
        print("🎉 S3 Cross-Region Replication setup completed!")
        print("📝 Note: New objects will automatically replicate to target buckets")
        return True

def main():
    """Main function to setup S3 replication"""
    
    # Load configuration
    try:
        with open('bucket-info.txt', 'r') as f:
            content = f.read()
            
        for line in content.split('\n'):
            if line.startswith('SOURCE_BUCKET='):
                source_bucket = line.split('=')[1]
            elif line.startswith('SOURCE_REGION='):
                source_region = line.split('=')[1]
                
        target_configs = [
            {
                "bucket": source_bucket.replace('source', 'target-us-west-2'),
                "region": "us-west-2"
            },
            {
                "bucket": source_bucket.replace('source', 'target-eu-west-1'),
                "region": "eu-west-1"
            }
        ]
        
    except Exception as e:
        print(f"❌ Error loading configuration: {e}")
        return False
    
    # Setup replication
    replication_setup = S3ReplicationSetup(source_bucket, source_region)
    return replication_setup.setup_complete_replication(target_configs)

if __name__ == "__main__":
    main()