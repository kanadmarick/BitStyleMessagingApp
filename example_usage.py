#!/usr/bin/env python3

"""
Example usage of the updated DevOps Pipeline with GCP container deployment.
This demonstrates how to use the new features in a real project.
"""

from devops_automation import DevOpsPipeline
import os

def main():
    """Example of using the updated DevOps Pipeline for GCP deployment."""
    
    print("🚀 ByteChat GCP Container Deployment Example")
    print("=" * 50)
    
    # Initialize the pipeline with your GCP project
    project_root = os.path.dirname(os.path.abspath(__file__))
    gcp_project_id = "your-bytechat-project"  # Replace with your actual project ID
    
    pipeline = DevOpsPipeline(
        project_root=project_root,
        gcp_project_id=gcp_project_id,
        gcp_region="us-central1"
    )
    
    print(f"📋 Initialized DevOps Pipeline")
    print(f"   Project: {gcp_project_id}")
    print(f"   Region: {pipeline.gcp_region}")
    
    # Example 1: Complete GCP Deployment Workflow
    print(f"\n🎯 Example 1: Complete GCP Deployment")
    print("To deploy ByteChat to GCP containers, you would run:")
    print()
    print("# Step 1: Validate prerequisites")
    print("pipeline.validate_deployment_prerequisites()")
    print()
    print("# Step 2: Build the GCP-optimized container")
    print("pipeline.docker_build_gcp('bytechat', 'v1.0.0')")
    print()
    print("# Step 3: Push to Google Container Registry")
    print("pipeline.docker_push_gcr('bytechat', 'v1.0.0')")
    print()
    print("# Step 4: Deploy to GCP (automated)")
    print("pipeline.deploy_to_gcp_containers()")
    print()
    print("# Step 5: Check deployment status")
    print("pipeline.deploy_gcp_status()")
    
    # Example 2: Using Ansible directly
    print(f"\n🎯 Example 2: Direct Ansible Deployment")
    print("To use Ansible playbooks directly:")
    print()
    print("# Deploy using Ansible with custom config")
    print("pipeline.ansible_playbook_gcp('gcp_deploy_config.yml')")
    
    # Example 3: Manual GKE cluster management
    print(f"\n🎯 Example 3: Manual GKE Cluster Management")
    print("To manage GKE clusters manually:")
    print()
    print("# Create a GKE cluster")
    print("pipeline.create_gke_cluster('my-cluster', node_count=3, machine_type='e2-standard-2')")
    print()
    print("# Get cluster credentials")
    print("pipeline.get_gke_credentials('my-cluster')")
    print()
    print("# Deploy application to existing cluster")
    print("pipeline.kube_apply()")
    print()
    print("# Clean up cluster when done")
    print("pipeline.delete_gke_cluster('my-cluster')")
    
    # Example 4: Custom deployment workflow
    print(f"\n🎯 Example 4: Custom Deployment Class")
    print("Create a custom deployment class:")
    print()
    
    example_code = '''
class ByteChatDeployment(DevOpsPipeline):
    def deploy_full_stack(self):
        """Deploy the complete ByteChat application."""
        print("🚀 Starting ByteChat deployment...")
        
        # Validate environment
        if not self.validate_deployment_prerequisites():
            print("❌ Prerequisites not met")
            return False
        
        # Build and push container
        if not self.docker_build_gcp('bytechat', 'latest'):
            print("❌ Container build failed")
            return False
            
        if not self.docker_push_gcr('bytechat', 'latest'):
            print("❌ Container push failed")
            return False
        
        # Deploy to GCP
        if not self.deploy_to_gcp_containers():
            print("❌ GCP deployment failed")
            return False
        
        print("✅ ByteChat deployed successfully!")
        return True

# Usage
bytechat = ByteChatDeployment(
    project_root='/path/to/bytechat',
    gcp_project_id='my-project-123'
)
bytechat.deploy_full_stack()
    '''
    
    print(example_code)
    
    # Example 5: Integration with CI/CD
    print(f"\n🎯 Example 5: CI/CD Integration")
    print("Integrate with CI/CD pipelines:")
    print()
    
    cicd_example = '''
# In your CI/CD pipeline (Jenkins, GitHub Actions, etc.)
pipeline = DevOpsPipeline(
    project_root=os.getcwd(),
    gcp_project_id=os.getenv('GCP_PROJECT_ID')
)

# Build and test
if pipeline.docker_build_gcp('bytechat', os.getenv('BUILD_NUMBER', 'latest')):
    print("✅ Build successful")
    
    # Deploy to staging
    if pipeline.ansible_playbook_gcp('staging_config.yml'):
        print("✅ Staging deployment successful")
        
        # Deploy to production
        if pipeline.deploy_to_gcp_containers():
            print("✅ Production deployment successful")
    '''
    
    print(cicd_example)
    
    print(f"\n📚 Documentation")
    print("For more details, see:")
    print("- devops_automation_readme.md")
    print("- GCP_CONTAINER_DEPLOYMENT.md")
    print("- ansible/gcp_deploy_config.yml.example")
    
    print(f"\n✨ Ready to deploy ByteChat to GCP!")

if __name__ == "__main__":
    main()
