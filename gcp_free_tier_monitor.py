#!/usr/bin/env python3
"""
GCP Free Tier Monitor and Enforcer

This script monitors GCP resource usage to ensure it stays within free tier limits.
If any service approaches or exceeds the limits, it will automatically shut down
resources to prevent billing charges.

Free Tier Limits (Always Free):
- Compute Engine: 1 f1-micro instance (US regions only)
- Cloud Storage: 5 GB regional storage (US regions)
- BigQuery: 1 TB queries/month, 10 GB storage
- Cloud Functions: 2 million invocations/month
- App Engine: 28 instance hours/day
- Cloud SQL: None in always free
- Container Registry: 0.5 GB storage
- Cloud Build: 120 build minutes/day
"""

import os
import sys
import json
import logging
import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from google.cloud import compute_v1
from google.cloud import storage
from google.cloud import bigquery
from google.cloud import resource_manager
from google.cloud import billing_v1
import google.auth
from google.auth.exceptions import DefaultCredentialsError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('gcp_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class FreeTierLimits:
    """Free tier limits for various GCP services"""
    # Compute Engine
    compute_instances_max: int = 1
    compute_instance_type: str = "f1-micro"
    compute_allowed_zones: List[str] = None
    
    # Storage
    storage_gb_max: float = 5.0
    
    # BigQuery
    bigquery_storage_gb_max: float = 10.0
    bigquery_queries_tb_monthly: float = 1.0
    
    # Container Registry
    container_registry_gb_max: float = 0.5
    
    # Cloud Build
    build_minutes_daily_max: int = 120
    
    # App Engine
    appengine_instance_hours_daily: int = 28

    def __post_init__(self):
        if self.compute_allowed_zones is None:
            self.compute_allowed_zones = [
                "us-west1", "us-central1", "us-east1"
            ]

class GCPFreeTierMonitor:
    """Monitor and enforce GCP free tier limits"""
    
    def __init__(self, project_id: str, emergency_shutdown: bool = True):
        self.project_id = project_id
        self.emergency_shutdown = emergency_shutdown
        self.limits = FreeTierLimits()
        self.violations = []
        
        # Initialize clients
        try:
            self.credentials, _ = google.auth.default()
            self.compute_client = compute_v1.InstancesClient()
            self.zones_client = compute_v1.ZonesClient()
            self.storage_client = storage.Client(project=project_id)
            self.bigquery_client = bigquery.Client(project=project_id)
            self.billing_client = billing_v1.CloudBillingClient()
            logger.info(f"Initialized GCP monitoring for project: {project_id}")
        except DefaultCredentialsError:
            logger.error("GCP credentials not found. Please run 'gcloud auth application-default login'")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Failed to initialize GCP clients: {e}")
            sys.exit(1)

    def check_compute_engine(self) -> Dict[str, Any]:
        """Check Compute Engine instances against free tier limits"""
        logger.info("Checking Compute Engine usage...")
        
        violations = []
        instances = []
        
        try:
            # Get all zones in all regions
            zones_list = []
            for zone in self.zones_client.list(project=self.project_id):
                zones_list.append(zone.name)
            
            # Check instances in all zones
            for zone in zones_list:
                try:
                    zone_instances = list(self.compute_client.list(
                        project=self.project_id, 
                        zone=zone
                    ))
                    
                    for instance in zone_instances:
                        if instance.status == "RUNNING":
                            instances.append({
                                'name': instance.name,
                                'zone': zone,
                                'machine_type': instance.machine_type.split('/')[-1],
                                'status': instance.status,
                                'region': zone.rsplit('-', 1)[0]
                            })
                except Exception as e:
                    # Zone might not exist or have permissions issues
                    continue
            
            # Check violations
            running_instances = len(instances)
            
            # Check instance count
            if running_instances > self.limits.compute_instances_max:
                violations.append(f"Too many instances: {running_instances} > {self.limits.compute_instances_max}")
            
            # Check instance types and regions
            for instance in instances:
                if instance['machine_type'] != self.limits.compute_instance_type:
                    violations.append(f"Non-free tier instance type: {instance['name']} ({instance['machine_type']})")
                
                if instance['region'] not in self.limits.compute_allowed_zones:
                    violations.append(f"Instance in non-free region: {instance['name']} ({instance['region']})")
            
            logger.info(f"Found {running_instances} running instances")
            
            return {
                'service': 'compute_engine',
                'instances': instances,
                'violations': violations,
                'usage': running_instances,
                'limit': self.limits.compute_instances_max
            }
            
        except Exception as e:
            logger.error(f"Error checking Compute Engine: {e}")
            return {'service': 'compute_engine', 'error': str(e), 'violations': []}

    def check_cloud_storage(self) -> Dict[str, Any]:
        """Check Cloud Storage usage against free tier limits"""
        logger.info("Checking Cloud Storage usage...")
        
        violations = []
        total_size_gb = 0.0
        buckets_info = []
        
        try:
            for bucket in self.storage_client.list_buckets():
                try:
                    # Get bucket size (approximate)
                    bucket_size = 0
                    for blob in bucket.list_blobs():
                        if blob.size:
                            bucket_size += blob.size
                    
                    bucket_size_gb = bucket_size / (1024 ** 3)
                    total_size_gb += bucket_size_gb
                    
                    buckets_info.append({
                        'name': bucket.name,
                        'location': bucket.location,
                        'size_gb': round(bucket_size_gb, 4)
                    })
                    
                    # Check if bucket is in free tier region
                    if bucket.location not in ['US-WEST1', 'US-CENTRAL1', 'US-EAST1', 'US']:
                        violations.append(f"Bucket in non-free region: {bucket.name} ({bucket.location})")
                        
                except Exception as e:
                    logger.warning(f"Could not check bucket {bucket.name}: {e}")
                    continue
            
            # Check total storage limit
            if total_size_gb > self.limits.storage_gb_max:
                violations.append(f"Storage exceeds limit: {total_size_gb:.2f} GB > {self.limits.storage_gb_max} GB")
            
            logger.info(f"Total storage usage: {total_size_gb:.2f} GB")
            
            return {
                'service': 'cloud_storage',
                'buckets': buckets_info,
                'violations': violations,
                'usage_gb': total_size_gb,
                'limit_gb': self.limits.storage_gb_max
            }
            
        except Exception as e:
            logger.error(f"Error checking Cloud Storage: {e}")
            return {'service': 'cloud_storage', 'error': str(e), 'violations': []}

    def check_bigquery(self) -> Dict[str, Any]:
        """Check BigQuery usage against free tier limits"""
        logger.info("Checking BigQuery usage...")
        
        violations = []
        datasets_info = []
        total_storage_gb = 0.0
        
        try:
            # Check datasets and storage
            for dataset in self.bigquery_client.list_datasets():
                dataset_ref = self.bigquery_client.get_dataset(dataset.reference)
                
                # Get dataset size (approximate)
                dataset_size = 0
                for table in self.bigquery_client.list_tables(dataset_ref):
                    table_ref = self.bigquery_client.get_table(table.reference)
                    if table_ref.num_bytes:
                        dataset_size += table_ref.num_bytes
                
                dataset_size_gb = dataset_size / (1024 ** 3)
                total_storage_gb += dataset_size_gb
                
                datasets_info.append({
                    'id': dataset.dataset_id,
                    'location': dataset_ref.location,
                    'size_gb': round(dataset_size_gb, 4)
                })
            
            # Check storage limit
            if total_storage_gb > self.limits.bigquery_storage_gb_max:
                violations.append(f"BigQuery storage exceeds limit: {total_storage_gb:.2f} GB > {self.limits.bigquery_storage_gb_max} GB")
            
            logger.info(f"BigQuery storage usage: {total_storage_gb:.2f} GB")
            
            return {
                'service': 'bigquery',
                'datasets': datasets_info,
                'violations': violations,
                'usage_gb': total_storage_gb,
                'limit_gb': self.limits.bigquery_storage_gb_max
            }
            
        except Exception as e:
            logger.error(f"Error checking BigQuery: {e}")
            return {'service': 'bigquery', 'error': str(e), 'violations': []}

    def shutdown_compute_instances(self, instances: List[Dict]) -> bool:
        """Emergency shutdown of compute instances"""
        logger.warning("EMERGENCY SHUTDOWN: Stopping compute instances...")
        
        success = True
        for instance in instances:
            try:
                logger.warning(f"Stopping instance: {instance['name']} in {instance['zone']}")
                
                operation = self.compute_client.stop(
                    project=self.project_id,
                    zone=instance['zone'],
                    instance=instance['name']
                )
                
                logger.info(f"Stop operation initiated for {instance['name']}: {operation.name}")
                
            except Exception as e:
                logger.error(f"Failed to stop instance {instance['name']}: {e}")
                success = False
        
        return success

    def delete_storage_buckets(self, buckets: List[Dict], keep_empty: bool = True) -> bool:
        """Delete or empty storage buckets that exceed limits"""
        logger.warning("EMERGENCY ACTION: Cleaning up storage buckets...")
        
        success = True
        for bucket_info in buckets:
            try:
                bucket = self.storage_client.bucket(bucket_info['name'])
                
                if keep_empty:
                    # Delete all objects in bucket
                    logger.warning(f"Emptying bucket: {bucket_info['name']}")
                    for blob in bucket.list_blobs():
                        blob.delete()
                else:
                    # Delete entire bucket
                    logger.warning(f"Deleting bucket: {bucket_info['name']}")
                    bucket.delete(force=True)
                    
            except Exception as e:
                logger.error(f"Failed to clean bucket {bucket_info['name']}: {e}")
                success = False
        
        return success

    def generate_report(self, results: List[Dict]) -> str:
        """Generate a detailed usage report"""
        report = ["=" * 60]
        report.append(f"GCP FREE TIER MONITORING REPORT")
        report.append(f"Generated: {datetime.datetime.now()}")
        report.append(f"Project: {self.project_id}")
        report.append("=" * 60)
        
        total_violations = 0
        
        for result in results:
            if 'error' in result:
                report.append(f"\n❌ {result['service'].upper()}: ERROR")
                report.append(f"   Error: {result['error']}")
                continue
            
            service = result['service']
            violations = result.get('violations', [])
            total_violations += len(violations)
            
            status = "✅ OK" if not violations else f"❌ {len(violations)} VIOLATIONS"
            report.append(f"\n{status} {service.upper().replace('_', ' ')}")
            
            if service == 'compute_engine':
                usage = result.get('usage', 0)
                limit = result.get('limit', 0)
                report.append(f"   Instances: {usage}/{limit}")
                
                for instance in result.get('instances', []):
                    report.append(f"   - {instance['name']} ({instance['machine_type']}) in {instance['zone']}")
            
            elif service == 'cloud_storage':
                usage_gb = result.get('usage_gb', 0)
                limit_gb = result.get('limit_gb', 0)
                report.append(f"   Storage: {usage_gb:.2f}/{limit_gb} GB")
                
                for bucket in result.get('buckets', []):
                    report.append(f"   - {bucket['name']}: {bucket['size_gb']} GB ({bucket['location']})")
            
            elif service == 'bigquery':
                usage_gb = result.get('usage_gb', 0)
                limit_gb = result.get('limit_gb', 0)
                report.append(f"   Storage: {usage_gb:.2f}/{limit_gb} GB")
            
            if violations:
                report.append("   VIOLATIONS:")
                for violation in violations:
                    report.append(f"   ⚠️  {violation}")
        
        report.append(f"\n{'=' * 60}")
        report.append(f"TOTAL VIOLATIONS: {total_violations}")
        
        if total_violations > 0 and self.emergency_shutdown:
            report.append("⚠️  EMERGENCY SHUTDOWN MODE ENABLED")
        
        report.append(f"{'=' * 60}")
        
        return "\n".join(report)

    def run_monitoring(self) -> bool:
        """Run complete monitoring check"""
        logger.info("Starting GCP Free Tier monitoring...")
        
        results = []
        emergency_actions = []
        
        # Check all services
        compute_result = self.check_compute_engine()
        results.append(compute_result)
        
        storage_result = self.check_cloud_storage()
        results.append(storage_result)
        
        bigquery_result = self.check_bigquery()
        results.append(bigquery_result)
        
        # Generate report
        report = self.generate_report(results)
        print(report)
        
        # Save report to file
        with open(f'gcp_monitoring_report_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.txt', 'w') as f:
            f.write(report)
        
        # Check for violations and take emergency action
        has_violations = False
        
        for result in results:
            violations = result.get('violations', [])
            if violations:
                has_violations = True
                self.violations.extend(violations)
        
        if has_violations and self.emergency_shutdown:
            logger.critical("VIOLATIONS DETECTED - INITIATING EMERGENCY SHUTDOWN")
            
            # Shutdown compute instances
            if compute_result.get('violations'):
                instances = compute_result.get('instances', [])
                if instances:
                    self.shutdown_compute_instances(instances)
            
            # Clean up storage if over limit
            if storage_result.get('violations'):
                buckets = storage_result.get('buckets', [])
                if buckets:
                    # Only empty buckets, don't delete them
                    self.delete_storage_buckets(buckets, keep_empty=True)
            
            logger.critical("Emergency actions completed. Check logs for details.")
            return False
        
        elif has_violations:
            logger.warning("Violations detected but emergency shutdown is disabled")
            return False
        
        else:
            logger.info("All services within free tier limits")
            return True

def main():
    """Main function to run the monitor"""
    import argparse
    
    parser = argparse.ArgumentParser(description='GCP Free Tier Monitor')
    parser.add_argument('--project-id', required=True, help='GCP Project ID')
    parser.add_argument('--no-shutdown', action='store_true', 
                       help='Disable emergency shutdown (monitoring only)')
    parser.add_argument('--continuous', action='store_true',
                       help='Run continuously every 5 minutes')
    parser.add_argument('--interval', type=int, default=300,
                       help='Monitoring interval in seconds (default: 300)')
    
    args = parser.parse_args()
    
    monitor = GCPFreeTierMonitor(
        project_id=args.project_id,
        emergency_shutdown=not args.no_shutdown
    )
    
    if args.continuous:
        import time
        logger.info(f"Starting continuous monitoring (interval: {args.interval}s)")
        
        while True:
            try:
                monitor.run_monitoring()
                logger.info(f"Sleeping for {args.interval} seconds...")
                time.sleep(args.interval)
            except KeyboardInterrupt:
                logger.info("Monitoring stopped by user")
                break
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
                time.sleep(60)  # Wait 1 minute before retrying
    else:
        success = monitor.run_monitoring()
        sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
