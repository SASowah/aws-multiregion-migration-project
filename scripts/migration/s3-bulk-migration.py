#!/usr/bin/env python3

import boto3
import threading
import time
import os
import hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed
from botocore.exceptions import ClientError
import json
from datetime import datetime

class S3BulkMigrator:
    def __init__(self, source_bucket, source_region, target_configs):
        """
        Initialize S3 Bulk Migrator
        
        target_configs: [
            {"bucket": "target-bucket-1", "region": "us-west-2"},
            {"bucket": "target-bucket-2", "region": "eu-west-1"}
        ]
        """
        self.source_bucket = source_bucket
        self.source_region = source_region
        self.target_configs = target_configs
        self.source_s3 = boto3.client('s3', region_name=source_region)
        
        # Statistics tracking
        self.stats = {
            'total_objects': 0,
            'successful_copies': 0,
            'failed_copies': 0,
            'bytes_transferred': 0,
            'start_time': None,
            'errors': []
        }
        
        # Thread lock for statistics
        self.stats_lock = threading.Lock()
        
    def list_all_objects(self):
        """List all objects in source bucket"""
        print(f"📋 Scanning source bucket: {self.source_bucket}")
        objects = []
        
        try:
            paginator = self.source_s3.get_paginator('list_objects_v2')
            for page in paginator.paginate(Bucket=self.source_bucket):
                if 'Contents' in page:
                    for obj in page['Contents']:
                        objects.append({
                            'key': obj['Key'],
                            'size': obj['Size'],
                            'last_modified': obj['LastModified'],
                            'etag': obj['ETag']
                        })
                        
            self.stats['total_objects'] = len(objects)
            print(f"📊 Found {len(objects)} objects to migrate")
            return objects
            
        except ClientError as e:
            print(f"❌ Error listing objects: {e}")
            return []
    
    def copy_object_to_target(self, obj_info, target_config):
        """Copy single object to target bucket with metadata preservation"""
        key = obj_info['key']
        target_bucket = target_config['bucket']
        target_region = target_config['region']
        
        try:
            target_s3 = boto3.client('s3', region_name=target_region)
            
            # Get object metadata from source
            head_response = self.source_s3.head_object(
                Bucket=self.source_bucket, 
                Key=key
            )
            
            # Copy source for cross-region copy
            copy_source = {
                'Bucket': self.source_bucket,
                'Key': key,
                'Region': self.source_region
            }
            
            # Perform the copy with metadata preservation
            target_s3.copy_object(
                CopySource=copy_source,
                Bucket=target_bucket,
                Key=key,
                MetadataDirective='COPY'
            )
            
            # Update statistics
            with self.stats_lock:
                self.stats['successful_copies'] += 1
                self.stats['bytes_transferred'] += obj_info['size']
            
            print(f"✅ Copied {key} to {target_bucket} ({self._format_bytes(obj_info['size'])})")
            return True
            
        except ClientError as e:
            error_msg = f"Failed to copy {key} to {target_bucket}: {e}"
            print(f"❌ {error_msg}")
            
            with self.stats_lock:
                self.stats['failed_copies'] += 1
                self.stats['errors'].append(error_msg)
            
            return False
    
    def migrate_object_to_all_targets(self, obj_info):
        """Migrate single object to all target buckets"""
        results = []
        for target_config in self.target_configs:
            success = self.copy_object_to_target(obj_info, target_config)
            results.append(success)
        return all(results)
    
    def run_migration(self, max_workers=5):
        """Execute bulk migration with parallel processing"""
        print(f"🚀 Starting bulk migration with {max_workers} workers")
        self.stats['start_time'] = datetime.now()
        
        # Get all objects to migrate
        objects = self.list_all_objects()
        if not objects:
            print("❌ No objects found to migrate")
            return False
        
        # Parallel migration
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(self.migrate_object_to_all_targets, obj): obj 
                for obj in objects
            }
            
            completed = 0
            for future in as_completed(futures):
                completed += 1
                obj = futures[future]
                
                try:
                    success = future.result()
                    if completed % 10 == 0 or completed == len(objects):
                        self._print_progress(completed, len(objects))
                        
                except Exception as e:
                    print(f"❌ Unexpected error with {obj['key']}: {e}")
        
        # Final statistics
        self._print_final_stats()
        return self.stats['failed_copies'] == 0
    
    def _print_progress(self, completed, total):
        """Print migration progress"""
        percentage = (completed / total) * 100
        print(f"📊 Progress: {completed}/{total} objects ({percentage:.1f}%)")
    
    def _print_final_stats(self):
        """Print final migration statistics"""
        end_time = datetime.now()
        duration = (end_time - self.stats['start_time']).total_seconds()
        
        print("\n" + "="*50)
        print("📊 MIGRATION COMPLETED")
        print("="*50)
        print(f"Total Objects: {self.stats['total_objects']}")
        print(f"Successful Copies: {self.stats['successful_copies']}")
        print(f"Failed Copies: {self.stats['failed_copies']}")
        print(f"Data Transferred: {self._format_bytes(self.stats['bytes_transferred'])}")
        print(f"Duration: {duration:.2f} seconds")
        print(f"Average Speed: {self._format_bytes(self.stats['bytes_transferred'] / duration if duration > 0 else 0)}/sec")
        
        if self.stats['errors']:
            print(f"\n❌ Errors ({len(self.stats['errors'])}):")
            for error in self.stats['errors'][:5]:  # Show first 5 errors
                print(f"  - {error}")
            if len(self.stats['errors']) > 5:
                print(f"  ... and {len(self.stats['errors']) - 5} more")
    
    def _format_bytes(self, bytes_count):
        """Format bytes in human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_count < 1024.0:
                return f"{bytes_count:.2f} {unit}"
            bytes_count /= 1024.0
        return f"{bytes_count:.2f} TB"

def main():
    """Main execution function"""
    
    # Load bucket configuration
    try:
        with open('bucket-info.txt', 'r') as f:
            content = f.read()
            
        # Parse source bucket info
        for line in content.split('\n'):
            if line.startswith('SOURCE_BUCKET='):
                source_bucket = line.split('=')[1]
            elif line.startswith('SOURCE_REGION='):
                source_region = line.split('=')[1]
                
        # Define target configurations
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
        
        print(f"🎯 Source: {source_bucket} ({source_region})")
        for config in target_configs:
            print(f"🎯 Target: {config['bucket']} ({config['region']})")
            
    except Exception as e:
        print(f"❌ Error reading bucket configuration: {e}")
        return False
    
    # Create migrator and run
    migrator = S3BulkMigrator(source_bucket, source_region, target_configs)
    success = migrator.run_migration(max_workers=3)  # Conservative thread count
    
    if success:
        print("🎉 Migration completed successfully!")
    else:
        print("⚠️  Migration completed with some errors. Check logs above.")
    
    return success

if __name__ == "__main__":
    main()