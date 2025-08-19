# DevOps Automation Module

This module provides a reusable `DevOpsPipeline` class that encapsulates the DevOps logic for this project. It is designed to be inherited and customized for other projects.

## `DevOpsPipeline` Class

The `DevOpsPipeline` class provides methods for handling Docker, Kubernetes, Terraform, Ansible, and Helm.

### Usage

To use this class in another project, you can import it and create an instance, passing the project's root directory to the constructor.

```python
from devops_automation import DevOpsPipeline

# Initialize the pipeline with the project's root directory
project_path = '/path/to/your/project'
pipeline = DevOpsPipeline(project_root=project_path)

# Build a Docker image
pipeline.docker_build('my-app')

# Apply Kubernetes configurations
pipeline.kube_apply()

# Initialize and apply Terraform
pipeline.terraform_init()
pipeline.terraform_apply()

# Run an Ansible playbook
pipeline.ansible_playbook()

# Install a Helm chart
pipeline.helm_install('my-app-release')
```

### Extending the Class

You can extend the `DevOpsPipeline` class to add custom logic for your project. For example, you could override the `docker_build` method to add custom build arguments.

```python
from devops_automation import DevOpsPipeline

class MyDevOpsPipeline(DevOpsPipeline):
    def docker_build(self, image_name, tag='latest'):
        print(f"Building custom Docker image: {image_name}:{tag}")
        # Add custom build logic here
        super().docker_build(image_name, tag)

# Initialize your custom pipeline
project_path = '/path/to/your/project'
my_pipeline = MyDevOpsPipeline(project_root=project_path)

# Build your custom Docker image
my_pipeline.docker_build('my-custom-app')
