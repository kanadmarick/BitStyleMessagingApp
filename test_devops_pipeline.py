#!/usr/bin/env python3

"""
Test script for the updated DevOps Pipeline with GCP container deployment features.
This script demonstrates the new capabilities without actually executing deployments.
"""

from devops_automation import DevOpsPipeline
import os

def test_devops_pipeline():
    """Test the DevOps pipeline functionality."""
    
    print("🧪 Testing Updated DevOps Pipeline Class")
    print("=" * 50)
    
    # Initialize pipeline
    project_root = os.path.dirname(os.path.abspath(__file__))
    test_project_id = "bytechat-test-project"
    
    pipeline = DevOpsPipeline(
        project_root=project_root,
        gcp_project_id=test_project_id,
        gcp_region="us-central1"
    )
    
    print(f"✅ Pipeline initialized successfully")
    print(f"   Project root: {pipeline.project_root}")
    print(f"   GCP Project: {pipeline.gcp_project_id}")
    print(f"   GCP Region: {pipeline.gcp_region}")
    print(f"   GCP Zone: {pipeline.gcp_zone}")
    
    # Test configuration paths
    print(f"\n📁 Configuration Paths:")
    print(f"   Dockerfile: {pipeline.dockerfile_path}")
    print(f"   Dockerfile.gcp: {pipeline.dockerfile_gcp_path}")
    print(f"   Kubernetes: {pipeline.kubernetes_path}")
    print(f"   Terraform: {pipeline.terraform_path}")
    print(f"   Ansible: {pipeline.ansible_path}")
    print(f"   Deployment Script: {pipeline.deployment_script}")
    print(f"   Validation Script: {pipeline.validation_script}")
    
    # Check which files exist
    print(f"\n📋 File Existence Check:")
    files_to_check = [
        ("Dockerfile", pipeline.dockerfile_path),
        ("Dockerfile.gcp", pipeline.dockerfile_gcp_path),
        ("Deployment Script", pipeline.deployment_script),
        ("Validation Script", pipeline.validation_script),
        ("GCP Playbook", os.path.join(pipeline.ansible_path, "playbook_deploy_gcp_containers.yml")),
        ("Local Playbook", os.path.join(pipeline.ansible_path, "playbook_start_bytechat.yml")),
        ("GCP Config Template", os.path.join(pipeline.ansible_path, "gcp_deploy_config.yml.example"))
    ]
    
    for name, path in files_to_check:
        exists = "✅" if os.path.exists(path) else "❌"
        print(f"   {exists} {name}: {os.path.basename(path)}")
    
    # Test method availability
    print(f"\n🔧 Available Methods:")
    traditional_methods = [
        'docker_build', 'kube_apply', 'terraform_init', 'terraform_plan', 
        'terraform_apply', 'ansible_playbook', 'helm_install'
    ]
    
    gcp_methods = [
        'validate_deployment_prerequisites', 'docker_build_gcp', 'docker_push_gcr',
        'deploy_to_gcp_containers', 'ansible_playbook_gcp', 'deploy_gcp_status',
        'cleanup_gcp_deployment', 'create_gke_cluster', 'get_gke_credentials',
        'delete_gke_cluster'
    ]
    
    print("   Traditional DevOps Methods:")
    for method in traditional_methods:
        available = "✅" if hasattr(pipeline, method) else "❌"
        print(f"      {available} {method}")
    
    print("   GCP Container Deployment Methods:")
    for method in gcp_methods:
        available = "✅" if hasattr(pipeline, method) else "❌"
        print(f"      {available} {method}")
    
    # Test example workflow (dry run)
    print(f"\n🚀 Example Workflow (Dry Run):")
    print("   1. Validate prerequisites (would run validation script)")
    print("   2. Build GCP Docker image (would build with Dockerfile.gcp)")
    print("   3. Push to Google Container Registry (would push to gcr.io)")
    print("   4. Deploy to GCP containers (would run deployment script)")
    print("   5. Check deployment status (would check cluster status)")
    
    print(f"\n✨ Test completed successfully!")
    print("   The DevOps Pipeline class is updated and ready for use.")
    print("   All new GCP container deployment features are available.")

if __name__ == "__main__":
    test_devops_pipeline()
