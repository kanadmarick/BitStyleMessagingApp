#!/usr/bin/env python3
"""
GCP Free Tier Monitor - Lightweight Version

A simplified monitoring script that focuses on the most critical free tier limits
and uses basic GCP API calls without heavy dependencies.
"""

import os
import sys
import json
import logging
import datetime
import subprocess
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('gcp_monitor_simple.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class FreeTierLimits:
    """Free tier limits for GCP services"""
    compute_instances_max: int = 1
    compute_instance_type: str = "f1-micro"
    compute_allowed_regions: List[str] = None
    storage_gb_max: float = 5.0
    
    def __post_init__(self):
        if self.compute_allowed_regions is None:
            self.compute_allowed_regions = ["us-west1", "us-central1", "us-east1"]

class GCPSimpleMonitor:
    """Lightweight GCP Free Tier Monitor using gcloud CLI"""
    
    def __init__(self, project_id: str, emergency_shutdown: bool = True):
        self.project_id = project_id
        self.emergency_shutdown = emergency_shutdown
        self.limits = FreeTierLimits()
        self.violations = []
        
        # Check if gcloud is available
        try:
            result = subprocess.run(['gcloud', '--version'], 
                                  capture_output=True, text=True, check=True)
            logger.info("gcloud CLI is available")
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.error("gcloud CLI is not installed or not in PATH")
            sys.exit(1)
    
    def run_gcloud_command(self, command: List[str]) -> Optional[Dict]:
        """Run gcloud command and return JSON result"""
        try:
            cmd = ['gcloud'] + command + ['--project', self.project_id, '--format=json']
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            if result.stdout.strip():
                return json.loads(result.stdout)
            return {}
            
        except subprocess.CalledProcessError as e:
            logger.error(f"gcloud command failed: {' '.join(command)}")
            logger.error(f"Error: {e.stderr}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse gcloud output: {e}")
            return None
    
    def check_compute_instances(self) -> Dict[str, Any]:
        """Check compute instances using gcloud CLI"""
        logger.info("Checking Compute Engine instances...")
        
        instances = self.run_gcloud_command(['compute', 'instances', 'list'])
        if instances is None:
            return {'service': 'compute', 'error': 'Failed to list instances', 'violations': []}
        
        violations = []
        running_instances = []
        
        for instance in instances:
            if instance.get('status') == 'RUNNING':
                machine_type = instance.get('machineType', '').split('/')[-1]
                zone = instance.get('zone', '').split('/')[-1]
                region = '-'.join(zone.split('-')[:-1]) if zone else 'unknown'
                
                instance_info = {
                    'name': instance.get('name'),
                    'zone': zone,
                    'region': region,
                    'machine_type': machine_type,
                    'status': instance.get('status')
                }
                
                running_instances.append(instance_info)
                
                # Check machine type
                if machine_type != self.limits.compute_instance_type:
                    violations.append(f"Non-free instance type: {instance_info['name']} ({machine_type})")
                
                # Check region
                if region not in self.limits.compute_allowed_regions:
                    violations.append(f"Instance in non-free region: {instance_info['name']} ({region})")
        
        # Check instance count
        if len(running_instances) > self.limits.compute_instances_max:
            violations.append(f"Too many instances: {len(running_instances)} > {self.limits.compute_instances_max}")
        
        logger.info(f"Found {len(running_instances)} running instances")
        
        return {
            'service': 'compute',
            'instances': running_instances,
            'violations': violations,
            'usage': len(running_instances),
            'limit': self.limits.compute_instances_max
        }
    
    def check_storage_buckets(self) -> Dict[str, Any]:
        """Check storage buckets using gcloud CLI"""
        logger.info("Checking Cloud Storage buckets...")
        
        buckets = self.run_gcloud_command(['storage', 'buckets', 'list'])
        if buckets is None:
            return {'service': 'storage', 'error': 'Failed to list buckets', 'violations': []}
        
        violations = []
        total_size_gb = 0.0
        bucket_info = []
        
        for bucket in buckets:
            bucket_name = bucket.get('name', '')
            location = bucket.get('location', '')
            
            # Get bucket size (rough estimation using gsutil)
            try:
                du_result = subprocess.run([
                    'gsutil', 'du', '-s', f'gs://{bucket_name}'
                ], capture_output=True, text=True, timeout=30)
                
                if du_result.returncode == 0:
                    size_bytes = int(du_result.stdout.split()[0])
                    size_gb = size_bytes / (1024 ** 3)
                else:
                    size_gb = 0.0
                    
            except (subprocess.TimeoutExpired, ValueError, IndexError):
                size_gb = 0.0
            
            bucket_data = {
                'name': bucket_name,
                'location': location,
                'size_gb': round(size_gb, 4)
            }
            
            bucket_info.append(bucket_data)
            total_size_gb += size_gb
            
            # Check location
            if location not in ['US-WEST1', 'US-CENTRAL1', 'US-EAST1', 'US']:
                violations.append(f"Bucket in non-free region: {bucket_name} ({location})")
        
        # Check total storage
        if total_size_gb > self.limits.storage_gb_max:
            violations.append(f"Storage exceeds limit: {total_size_gb:.2f} GB > {self.limits.storage_gb_max} GB")
        
        logger.info(f"Total storage usage: {total_size_gb:.2f} GB")
        
        return {
            'service': 'storage',
            'buckets': bucket_info,
            'violations': violations,
            'usage_gb': total_size_gb,
            'limit_gb': self.limits.storage_gb_max
        }
    
    def emergency_shutdown_instances(self, instances: List[Dict]) -> bool:
        """Stop compute instances"""
        logger.critical("EMERGENCY SHUTDOWN: Stopping compute instances...")
        
        success = True
        for instance in instances:
            try:
                logger.warning(f"Stopping instance: {instance['name']} in {instance['zone']}")
                
                result = subprocess.run([
                    'gcloud', 'compute', 'instances', 'stop', instance['name'],
                    '--zone', instance['zone'],
                    '--project', self.project_id,
                    '--quiet'
                ], capture_output=True, text=True, timeout=60)
                
                if result.returncode == 0:
                    logger.info(f"Successfully initiated stop for {instance['name']}")
                else:
                    logger.error(f"Failed to stop {instance['name']}: {result.stderr}")
                    success = False
                    
            except subprocess.TimeoutExpired:
                logger.error(f"Timeout stopping instance {instance['name']}")
                success = False
            except Exception as e:
                logger.error(f"Error stopping instance {instance['name']}: {e}")
                success = False
        
        return success
    
    def emergency_cleanup_storage(self, buckets: List[Dict]) -> bool:
        """Clean up storage buckets"""
        logger.critical("EMERGENCY CLEANUP: Removing storage content...")
        
        success = True
        for bucket in buckets:
            try:
                bucket_name = bucket['name']
                logger.warning(f"Cleaning bucket: {bucket_name}")
                
                # Remove all objects from bucket (but keep bucket)
                result = subprocess.run([
                    'gsutil', '-m', 'rm', '-r', f'gs://{bucket_name}/*'
                ], capture_output=True, text=True, timeout=300)
                
                if result.returncode == 0:
                    logger.info(f"Successfully cleaned bucket {bucket_name}")
                else:
                    logger.warning(f"Bucket {bucket_name} might be empty or cleanup failed: {result.stderr}")
                    
            except subprocess.TimeoutExpired:
                logger.error(f"Timeout cleaning bucket {bucket['name']}")
                success = False
            except Exception as e:
                logger.error(f"Error cleaning bucket {bucket['name']}: {e}")
                success = False
        
        return success
    
    def send_alert(self, violations: List[str]) -> None:
        """Send alert about violations (could be extended to email/SMS)"""
        alert_message = f"""
🚨 GCP FREE TIER VIOLATION ALERT 🚨
Project: {self.project_id}
Time: {datetime.datetime.now()}

Violations:
{chr(10).join(f"- {v}" for v in violations)}

{'Emergency shutdown initiated!' if self.emergency_shutdown else 'Emergency shutdown disabled - manual action required!'}
        """
        
        print(alert_message)
        logger.critical(alert_message)
        
        # Write alert to file
        alert_file = f"gcp_alert_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(alert_file, 'w') as f:
            f.write(alert_message)
    
    def generate_report(self, results: List[Dict]) -> str:
        """Generate monitoring report"""
        report_lines = [
            "=" * 60,
            "GCP FREE TIER MONITORING REPORT",
            f"Generated: {datetime.datetime.now()}",
            f"Project: {self.project_id}",
            f"Emergency Mode: {'ENABLED' if self.emergency_shutdown else 'DISABLED'}",
            "=" * 60
        ]
        
        total_violations = 0
        
        for result in results:
            if 'error' in result:
                report_lines.extend([
                    f"\n❌ {result['service'].upper()}: ERROR",
                    f"   {result['error']}"
                ])
                continue
            
            violations = result.get('violations', [])
            total_violations += len(violations)
            
            service = result['service']
            status = "✅ OK" if not violations else f"❌ {len(violations)} VIOLATIONS"
            
            if service == 'compute':
                usage = result.get('usage', 0)
                limit = result.get('limit', 0)
                report_lines.extend([
                    f"\n{status} COMPUTE ENGINE",
                    f"   Running Instances: {usage}/{limit}"
                ])
                
                for instance in result.get('instances', []):
                    report_lines.append(f"   - {instance['name']} ({instance['machine_type']}) in {instance['zone']}")
            
            elif service == 'storage':
                usage_gb = result.get('usage_gb', 0)
                limit_gb = result.get('limit_gb', 0)
                report_lines.extend([
                    f"\n{status} CLOUD STORAGE",
                    f"   Storage Usage: {usage_gb:.2f}/{limit_gb} GB"
                ])
                
                for bucket in result.get('buckets', []):
                    report_lines.append(f"   - {bucket['name']}: {bucket['size_gb']} GB ({bucket['location']})")
            
            if violations:
                report_lines.append("   VIOLATIONS:")
                for violation in violations:
                    report_lines.append(f"   ⚠️  {violation}")
        
        report_lines.extend([
            f"\n{'=' * 60}",
            f"TOTAL VIOLATIONS: {total_violations}",
            f"{'=' * 60}"
        ])
        
        return "\n".join(report_lines)
    
    def run_monitoring(self) -> bool:
        """Run complete monitoring cycle"""
        logger.info(f"Starting GCP monitoring for project: {self.project_id}")
        
        results = []
        
        # Check compute instances
        compute_result = self.check_compute_instances()
        results.append(compute_result)
        
        # Check storage
        storage_result = self.check_storage_buckets()
        results.append(storage_result)
        
        # Generate and display report
        report = self.generate_report(results)
        print(report)
        
        # Save report
        report_file = f"gcp_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(report_file, 'w') as f:
            f.write(report)
        
        # Check for violations
        all_violations = []
        emergency_needed = False
        
        for result in results:
            violations = result.get('violations', [])
            if violations:
                all_violations.extend(violations)
                emergency_needed = True
        
        if emergency_needed:
            self.send_alert(all_violations)
            
            if self.emergency_shutdown:
                logger.critical("INITIATING EMERGENCY SHUTDOWN PROCEDURES")
                
                # Stop violating compute instances
                if compute_result.get('violations'):
                    instances = compute_result.get('instances', [])
                    if instances:
                        self.emergency_shutdown_instances(instances)
                
                # Clean storage if needed
                if storage_result.get('violations'):
                    buckets = storage_result.get('buckets', [])
                    if buckets:
                        self.emergency_cleanup_storage(buckets)
                
                logger.critical("Emergency procedures completed")
                return False
            else:
                logger.warning("Violations found but emergency shutdown disabled")
                return False
        
        else:
            logger.info("✅ All services within free tier limits")
            return True

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='GCP Free Tier Monitor (Simple)')
    parser.add_argument('--project-id', required=True, help='GCP Project ID')
    parser.add_argument('--no-shutdown', action='store_true',
                       help='Disable emergency shutdown (monitoring only)')
    parser.add_argument('--continuous', action='store_true',
                       help='Run continuously')
    parser.add_argument('--interval', type=int, default=300,
                       help='Check interval in seconds (default: 300)')
    
    args = parser.parse_args()
    
    monitor = GCPSimpleMonitor(
        project_id=args.project_id,
        emergency_shutdown=not args.no_shutdown
    )
    
    if args.continuous:
        logger.info(f"Starting continuous monitoring (interval: {args.interval}s)")
        
        while True:
            try:
                monitor.run_monitoring()
                logger.info(f"Next check in {args.interval} seconds...")
                time.sleep(args.interval)
            except KeyboardInterrupt:
                logger.info("Monitoring stopped by user")
                break
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
                time.sleep(60)  # Wait before retry
    else:
        success = monitor.run_monitoring()
        sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
