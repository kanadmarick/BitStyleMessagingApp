# DevOps Automation Module

This module provides a reusable `DevOpsPipeline` class that encapsulates the DevOps logic for this project. It includes both traditional deployment methods and modern GCP container deployment capabilities.

## `DevOpsPipeline` Class

The `DevOpsPipeline` class provides methods for handling Docker, Kubernetes, Terraform, Ansible, Helm, and Google Cloud Platform container deployments.

### Features

- **Traditional DevOps**: Docker, Kubernetes, Terraform, Ansible, Helm
- **GCP Container Deployment**: Automated container deployment to Google Kubernetes Engine
- **Multi-stage Docker Builds**: Optimized React + Flask containerization
- **Google Container Registry**: Image management and deployment
- **Validation and Monitoring**: Comprehensive deployment validation
- **Cost Optimization**: Free-tier optimized configurations

### Basic Usage

```python
from devops_automation import DevOpsPipeline

# Initialize the pipeline with the project's root directory
project_path = '/path/to/your/project'
pipeline = DevOpsPipeline(project_root=project_path)

# Traditional methods
pipeline.docker_build('my-app')
pipeline.kube_apply()
pipeline.terraform_init()
pipeline.terraform_apply()
pipeline.ansible_playbook()
pipeline.helm_install('my-app-release')
```

### GCP Container Deployment Usage

```python
from devops_automation import DevOpsPipeline

# Initialize with GCP project ID
project_path = '/path/to/your/project'
gcp_project_id = 'your-gcp-project-123'
pipeline = DevOpsPipeline(
    project_root=project_path, 
    gcp_project_id=gcp_project_id,
    gcp_region='us-central1'
)

# Validate prerequisites
pipeline.validate_deployment_prerequisites()

# Build and push to Google Container Registry
pipeline.docker_build_gcp('bytechat', 'v1.0.0')
pipeline.docker_push_gcr('bytechat', 'v1.0.0')

# Deploy to GCP using automated script (recommended)
pipeline.deploy_to_gcp_containers()

# Or use Ansible directly
pipeline.ansible_playbook_gcp('gcp_deploy_config.yml')

# Check deployment status
pipeline.deploy_gcp_status()

# Manage GKE clusters
pipeline.create_gke_cluster('my-cluster')
pipeline.get_gke_credentials('my-cluster')

# Cleanup resources
pipeline.cleanup_gcp_deployment()
```

### Available Methods

#### Traditional DevOps Methods
- `docker_build(image_name, tag, dockerfile)` - Build Docker images with custom Dockerfiles
- `kube_apply()` - Apply Kubernetes configurations
- `terraform_init()`, `terraform_plan()`, `terraform_apply()` - Terraform operations
- `ansible_playbook(inventory_file, playbook_file)` - Run Ansible playbooks
- `helm_install(release_name, chart_name)` - Install Helm charts

#### GCP Container Deployment Methods
- `validate_deployment_prerequisites()` - Validate all deployment prerequisites
- `docker_build_gcp(image_name, tag)` - Build using multi-stage Dockerfile.gcp
- `docker_push_gcr(image_name, tag)` - Push images to Google Container Registry
- `deploy_to_gcp_containers(project_id, config_file)` - Automated GCP deployment
- `ansible_playbook_gcp(config_file, project_id)` - Run GCP Ansible playbook
- `deploy_gcp_status()` - Check GCP deployment status
- `cleanup_gcp_deployment()` - Clean up GCP resources

#### GKE Cluster Management
- `create_gke_cluster(cluster_name, node_count, machine_type)` - Create GKE cluster
- `get_gke_credentials(cluster_name)` - Get cluster credentials for kubectl
- `delete_gke_cluster(cluster_name)` - Delete GKE cluster

### Configuration Parameters

When initializing the pipeline, you can customize:

```python
pipeline = DevOpsPipeline(
    project_root='/path/to/project',       # Required: Project directory
    gcp_project_id='my-project-123',       # GCP Project ID for cloud deployment
    gcp_region='us-central1'               # GCP region (default: us-central1)
)
```

### Extending the Class

You can extend the `DevOpsPipeline` class to add custom logic for your project:

```python
from devops_automation import DevOpsPipeline

class MyCustomPipeline(DevOpsPipeline):
    def __init__(self, project_root, **kwargs):
        super().__init__(project_root, **kwargs)
        self.custom_config = "my-custom-setting"
    
    def custom_deployment_method(self):
        """Add your custom deployment logic here."""
        print("Running custom deployment...")
        # Combine existing methods for custom workflow
        if not self.validate_deployment_prerequisites():
            return False
        
        if not self.docker_build_gcp('my-app', 'latest'):
            return False
            
        return self.deploy_to_gcp_containers()

# Use your custom pipeline
project_path = '/path/to/your/project'
custom_pipeline = MyCustomPipeline(project_root=project_path, gcp_project_id='my-project')
custom_pipeline.custom_deployment_method()
```

### Integration with Existing Workflows

The updated class integrates seamlessly with:

- **Ansible Playbooks**: `playbook_deploy_gcp_containers.yml`
- **Deployment Scripts**: `deploy_gcp_containers.sh`
- **Validation Scripts**: `validate_deployment.sh`
- **Configuration Files**: `ansible/gcp_deploy_config.yml`
- **Multi-stage Dockerfiles**: `Dockerfile.gcp`

### Error Handling and Logging

All methods include comprehensive error handling and logging:

```python
# Methods return boolean success/failure
success = pipeline.deploy_to_gcp_containers()
if success:
    print("Deployment successful!")
else:
    print("Deployment failed - check logs for details")

# Use capture_output for programmatic access to results
success, stdout, stderr = pipeline._run_command("kubectl get pods", ".", capture_output=True)
```
project_path = '/path/to/your/project'
my_pipeline = MyDevOpsPipeline(project_root=project_path)

# Build your custom Docker image
my_pipeline.docker_build('my-custom-app')
