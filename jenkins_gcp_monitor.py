#!/usr/bin/env python3
"""
Jenkins Pipeline Integration for GCP Free Tier Monitor

This script is designed to run as part of the Jenkins CI/CD pipeline
to ensure deployments don't exceed free tier limits.
"""

import os
import sys
import json
import subprocess
import logging
from pathlib import Path

# Configure logging for Jenkins
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [JENKINS-GCP-MONITOR] %(levelname)s: %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

class JenkinsGCPMonitor:
    """GCP monitoring specifically for Jenkins pipeline integration"""
    
    def __init__(self, project_id: str):
        self.project_id = project_id
        
        # Jenkins environment variables
        self.build_number = os.environ.get('BUILD_NUMBER', 'unknown')
        self.job_name = os.environ.get('JOB_NAME', 'unknown')
        self.workspace = os.environ.get('WORKSPACE', '/var/jenkins_home')
        
        logger.info(f"Jenkins Build: {self.job_name} #{self.build_number}")
        logger.info(f"GCP Project: {self.project_id}")
    
    def pre_deployment_check(self) -> bool:
        """Run before deployment to ensure we can proceed"""
        logger.info("=== PRE-DEPLOYMENT GCP FREE TIER CHECK ===")
        
        try:
            # Run the simple monitor
            result = subprocess.run([
                sys.executable, 
                os.path.join(self.workspace, 'gcp_free_tier_monitor_simple.py'),
                '--project-id', self.project_id,
                '--no-shutdown'
            ], capture_output=True, text=True, timeout=300)
            
            logger.info("Monitor Output:")
            logger.info(result.stdout)
            
            if result.stderr:
                logger.warning("Monitor Warnings/Errors:")
                logger.warning(result.stderr)
            
            if result.returncode == 0:
                logger.info("✅ PRE-DEPLOYMENT CHECK PASSED")
                return True
            else:
                logger.error("❌ PRE-DEPLOYMENT CHECK FAILED")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("❌ Monitor check timed out")
            return False
        except Exception as e:
            logger.error(f"❌ Monitor check failed: {e}")
            return False
    
    def post_deployment_check(self) -> bool:
        """Run after deployment to verify we're still within limits"""
        logger.info("=== POST-DEPLOYMENT GCP FREE TIER CHECK ===")
        
        try:
            # Run with emergency shutdown enabled
            result = subprocess.run([
                sys.executable,
                os.path.join(self.workspace, 'gcp_free_tier_monitor_simple.py'),
                '--project-id', self.project_id
                # Emergency shutdown is enabled by default
            ], capture_output=True, text=True, timeout=300)
            
            logger.info("Monitor Output:")
            logger.info(result.stdout)
            
            if result.stderr:
                logger.warning("Monitor Warnings/Errors:")
                logger.warning(result.stderr)
            
            if result.returncode == 0:
                logger.info("✅ POST-DEPLOYMENT CHECK PASSED")
                return True
            else:
                logger.error("❌ POST-DEPLOYMENT CHECK FAILED - EMERGENCY ACTION MAY HAVE BEEN TAKEN")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("❌ Monitor check timed out")
            return False
        except Exception as e:
            logger.error(f"❌ Monitor check failed: {e}")
            return False
    
    def check_deployment_size(self) -> bool:
        """Estimate if current deployment will fit in free tier"""
        logger.info("=== DEPLOYMENT SIZE ESTIMATION ===")
        
        # Check if Docker image size is reasonable for free tier
        try:
            # Look for Dockerfile to estimate image size
            dockerfile_path = os.path.join(self.workspace, 'Dockerfile')
            if os.path.exists(dockerfile_path):
                logger.info("Dockerfile found - checking for free tier compatibility")
                
                with open(dockerfile_path, 'r') as f:
                    dockerfile_content = f.read()
                
                # Basic checks for free tier compatibility
                warnings = []
                
                if 'FROM ubuntu' in dockerfile_content or 'FROM debian' in dockerfile_content:
                    warnings.append("Large base image detected - consider using alpine or slim variants")
                
                if 'RUN apt-get install' in dockerfile_content:
                    warnings.append("Heavy package installation detected")
                
                if len(dockerfile_content.split('\n')) > 50:
                    warnings.append("Complex Dockerfile - may result in large image")
                
                if warnings:
                    logger.warning("Dockerfile warnings:")
                    for warning in warnings:
                        logger.warning(f"  - {warning}")
                
                logger.info("✅ Dockerfile check completed")
                return True
            else:
                logger.info("No Dockerfile found - skipping image size check")
                return True
                
        except Exception as e:
            logger.error(f"Error checking deployment size: {e}")
            return True  # Don't fail the build for this
    
    def set_jenkins_properties(self, success: bool) -> None:
        """Set Jenkins build properties"""
        try:
            properties = {
                'GCP_MONITOR_STATUS': 'PASS' if success else 'FAIL',
                'GCP_PROJECT_ID': self.project_id,
                'FREE_TIER_CHECK_TIME': subprocess.check_output(['date'], text=True).strip()
            }
            
            # Write properties file for Jenkins
            props_file = os.path.join(self.workspace, 'gcp_monitor.properties')
            with open(props_file, 'w') as f:
                for key, value in properties.items():
                    f.write(f"{key}={value}\n")
            
            logger.info(f"Jenkins properties written to {props_file}")
            
        except Exception as e:
            logger.warning(f"Could not write Jenkins properties: {e}")

def main():
    """Main function for Jenkins integration"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Jenkins GCP Free Tier Integration')
    parser.add_argument('--project-id', required=True, help='GCP Project ID')
    parser.add_argument('--stage', choices=['pre', 'post', 'size'], required=True,
                       help='Pipeline stage: pre-deployment, post-deployment, or size check')
    
    args = parser.parse_args()
    
    monitor = JenkinsGCPMonitor(args.project_id)
    
    success = False
    
    if args.stage == 'pre':
        success = monitor.pre_deployment_check()
    elif args.stage == 'post':
        success = monitor.post_deployment_check()
    elif args.stage == 'size':
        success = monitor.check_deployment_size()
    
    # Set Jenkins properties
    monitor.set_jenkins_properties(success)
    
    if success:
        logger.info(f"🎉 {args.stage.upper()} CHECK COMPLETED SUCCESSFULLY")
        sys.exit(0)
    else:
        logger.error(f"💥 {args.stage.upper()} CHECK FAILED")
        sys.exit(1)

if __name__ == '__main__':
    main()
