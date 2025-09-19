#!/usr/bin/env python3

import boto3
from botocore.exceptions import ClientError

def delete_all_object_versions(bucket_name, region):
    """Delete all object versions and delete markers from a bucket"""
    s3 = boto3.client('s3', region_name=region)
    
    try:
        # List all object versions
        response = s3.list_object_versions(Bucket=bucket_name)
        
        # Delete all versions
        if 'Versions' in response:
            for version in response['Versions']:
                s3.delete_object(
                    Bucket=bucket_name,
                    Key=version['Key'],
                    VersionId=version['VersionId']
                )
                print(f"Deleted version: {version['Key']} ({version['VersionId']})")
        
        # Delete all delete markers
        if 'DeleteMarkers' in response:
            for marker in response['DeleteMarkers']:
                s3.delete_object(
                    Bucket=bucket_name,
                    Key=marker['Key'],
                    VersionId=marker['VersionId']
                )
                print(f"Deleted marker: {marker['Key']} ({marker['VersionId']})")
        
        # Now delete the bucket
        s3.delete_bucket(Bucket=bucket_name)
        print(f"Deleted bucket: {bucket_name}")
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchBucket':
            print(f"Bucket {bucket_name} already deleted")
        else:
            print(f"Error deleting {bucket_name}: {e}")

def delete_iam_role():
    """Delete the replication IAM role"""
    iam = boto3.client('iam')
    role_name = "S3-Replication-Role"
    
    try:
        # Detach policies
        iam.detach_role_policy(
            RoleName=role_name,
            PolicyArn="arn:aws:iam::aws:policy/service-role/AWSS3ReplicationServiceRolePolicy"
        )
        
        # Delete role
        iam.delete_role(RoleName=role_name)
        print(f"Deleted IAM role: {role_name}")
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchEntity':
            print(f"IAM role {role_name} already deleted")
        else:
            print(f"Error deleting IAM role: {e}")

def main():
    print("Cleaning up AWS resources...")
    
    # Delete S3 buckets
    buckets = [
        ("migration-demo-source-36714", "us-east-1"),
        ("migration-demo-target-us-west-2-36714", "us-west-2"),
        ("migration-demo-target-eu-west-1-36714", "eu-west-1")
    ]
    
    for bucket, region in buckets:
        delete_all_object_versions(bucket, region)
    
    # Delete IAM role
    delete_iam_role()
    
    print("Cleanup completed!")

if __name__ == "__main__":
    main()