import os
import subprocess
import json
import time

class DevOpsPipeline:
    def __init__(self, project_root, gcp_project_id=None, gcp_region='us-central1'):
        self.project_root = project_root
        self.dockerfile_path = os.path.join(project_root, 'Dockerfile')
        self.dockerfile_gcp_path = os.path.join(project_root, 'Dockerfile.gcp')
        self.kubernetes_path = os.path.join(project_root, 'k8s')
        self.terraform_path = os.path.join(project_root, 'terraform')
        self.ansible_path = os.path.join(project_root, 'ansible')
        self.helm_path = os.path.join(project_root, 'helm', 'messaging-app')
        
        # GCP specific configurations
        self.gcp_project_id = gcp_project_id
        self.gcp_region = gcp_region
        self.gcp_zone = f"{gcp_region}-a"
        self.gcr_hostname = 'gcr.io'
        self.deployment_script = os.path.join(project_root, 'deploy_gcp_containers.sh')
        self.validation_script = os.path.join(project_root, 'validate_deployment.sh')

    def _run_command(self, command, working_dir, capture_output=False):
        """Helper function to run a shell command."""
        try:
            if capture_output:
                process = subprocess.Popen(command, cwd=working_dir, stdout=subprocess.PIPE, 
                                         stderr=subprocess.PIPE, shell=True, text=True)
                stdout, stderr = process.communicate()
                return process.returncode == 0, stdout, stderr
            else:
                process = subprocess.Popen(command, cwd=working_dir, stdout=subprocess.PIPE, 
                                         stderr=subprocess.PIPE, shell=True)
                stdout, stderr = process.communicate()
                if process.returncode != 0:
                    print(f"Error executing command: {command}")
                    print(stderr.decode())
                    return False
                print(stdout.decode())
                return True
        except Exception as e:
            print(f"An exception occurred: {e}")
            return False

    def docker_build(self, image_name, tag='latest', dockerfile='Dockerfile'):
        """Builds a Docker image from the specified Dockerfile."""
        dockerfile_path = os.path.join(self.project_root, dockerfile)
        print(f"Building Docker image: {image_name}:{tag} using {dockerfile}")
        command = f"docker build -t {image_name}:{tag} -f {dockerfile_path} ."
        return self._run_command(command, self.project_root)

    def docker_build_gcp(self, image_name, tag='latest'):
        """Builds a Docker image using the GCP multi-stage Dockerfile."""
        print(f"Building GCP Docker image: {image_name}:{tag}")
        return self.docker_build(image_name, tag, 'Dockerfile.gcp')

    def docker_push_gcr(self, image_name, tag='latest'):
        """Pushes a Docker image to Google Container Registry."""
        if not self.gcp_project_id:
            print("Error: GCP Project ID not set")
            return False
            
        full_image_name = f"{self.gcr_hostname}/{self.gcp_project_id}/{image_name}:{tag}"
        print(f"Pushing image to GCR: {full_image_name}")
        
        # Configure Docker for GCR
        auth_success = self._run_command("gcloud auth configure-docker --quiet", self.project_root)
        if not auth_success:
            return False
            
        # Tag image for GCR
        tag_success = self._run_command(f"docker tag {image_name}:{tag} {full_image_name}", self.project_root)
        if not tag_success:
            return False
            
        # Push to GCR
        return self._run_command(f"docker push {full_image_name}", self.project_root)

    def kube_apply(self):
        """Applies the Kubernetes configurations."""
        print("Applying Kubernetes configurations...")
        command = f"kubectl apply -f {self.kubernetes_path}"
        return self._run_command(command, self.project_root)

    def terraform_init(self):
        """Initializes Terraform in the project."""
        print("Initializing Terraform...")
        return self._run_command("terraform init", self.terraform_path)

    def terraform_plan(self):
        """Creates a Terraform execution plan."""
        print("Creating Terraform plan...")
        return self._run_command("terraform plan", self.terraform_path)

    def terraform_apply(self):
        """Applies the Terraform plan."""
        print("Applying Terraform plan...")
        return self._run_command("terraform apply -auto-approve", self.terraform_path)

    def ansible_playbook(self, inventory_file='inventory', playbook_file='playbook.yml'):
        """Runs an Ansible playbook."""
        print(f"Running Ansible playbook: {playbook_file}")
        inventory_path = os.path.join(self.ansible_path, inventory_file)
        playbook_path = os.path.join(self.ansible_path, playbook_file)
        command = f"ansible-playbook -i {inventory_path} {playbook_path}"
        return self._run_command(command, self.ansible_path)

    def helm_install(self, release_name, chart_name='.'):
        """Installs a Helm chart."""
        print(f"Installing Helm chart: {release_name}")
        command = f"helm install {release_name} {chart_name}"
        return self._run_command(command, self.helm_path)

    # GCP Container Deployment Methods
    def validate_deployment_prerequisites(self):
        """Validates all prerequisites for deployment."""
        print("Validating deployment prerequisites...")
        if os.path.exists(self.validation_script):
            return self._run_command(self.validation_script, self.project_root)
        else:
            print("Warning: validation script not found, performing basic checks...")
            
            # Basic prerequisite checks
            checks = [
                ("docker", "Docker"),
                ("gcloud", "Google Cloud CLI"),
                ("kubectl", "Kubernetes CLI"),
                ("ansible-playbook", "Ansible")
            ]
            
            for command, name in checks:
                success, stdout, stderr = self._run_command(f"which {command}", self.project_root, capture_output=True)
                if success:
                    print(f"✅ {name} found")
                else:
                    print(f"❌ {name} not found")
                    return False
            return True

    def deploy_to_gcp_containers(self, project_id=None, config_file=None):
        """Deploys the application to GCP using containers via the deployment script."""
        if not os.path.exists(self.deployment_script):
            print("Error: GCP deployment script not found")
            return False
            
        project_id = project_id or self.gcp_project_id
        if not project_id:
            print("Error: GCP Project ID required for deployment")
            return False
        
        print(f"Deploying to GCP containers for project: {project_id}")
        
        # Set environment variable for project ID
        env_command = f"GCP_PROJECT_ID={project_id} {self.deployment_script} deploy"
        if config_file:
            env_command += f" --config {config_file}"
            
        return self._run_command(env_command, self.project_root)

    def deploy_gcp_status(self):
        """Checks the status of GCP deployment."""
        if not os.path.exists(self.deployment_script):
            print("Error: GCP deployment script not found")
            return False
            
        print("Checking GCP deployment status...")
        return self._run_command(f"{self.deployment_script} status", self.project_root)

    def cleanup_gcp_deployment(self):
        """Cleans up GCP deployment resources."""
        if not os.path.exists(self.deployment_script):
            print("Error: GCP deployment script not found")
            return False
            
        print("Cleaning up GCP deployment...")
        return self._run_command(f"{self.deployment_script} cleanup", self.project_root)

    def ansible_playbook_gcp(self, config_file=None, project_id=None):
        """Runs the GCP container deployment Ansible playbook."""
        print("Running GCP container deployment playbook...")
        
        playbook_file = 'playbook_deploy_gcp_containers.yml'
        playbook_path = os.path.join(self.ansible_path, playbook_file)
        
        if not os.path.exists(playbook_path):
            print(f"Error: GCP playbook not found at {playbook_path}")
            return False
        
        project_id = project_id or self.gcp_project_id
        if not project_id:
            print("Error: GCP Project ID required")
            return False
        
        # Build command with extra variables
        command = f"ansible-playbook {playbook_path} -e gcp_project_id={project_id}"
        
        if config_file:
            config_path = os.path.join(self.ansible_path, config_file)
            if os.path.exists(config_path):
                command += f" -e @{config_path}"
            else:
                print(f"Warning: Config file not found: {config_path}")
        
        return self._run_command(command, self.ansible_path)

    def create_gke_cluster(self, cluster_name="bytechat-cluster", node_count=1, machine_type="e2-micro"):
        """Creates a GKE cluster."""
        if not self.gcp_project_id:
            print("Error: GCP Project ID not set")
            return False
            
        print(f"Creating GKE cluster: {cluster_name}")
        command = f"""
        gcloud container clusters create {cluster_name} \
            --zone={self.gcp_zone} \
            --machine-type={machine_type} \
            --num-nodes={node_count} \
            --enable-autorepair \
            --enable-autoupgrade \
            --project={self.gcp_project_id}
        """
        return self._run_command(command, self.project_root)

    def get_gke_credentials(self, cluster_name="bytechat-cluster"):
        """Gets GKE cluster credentials for kubectl."""
        if not self.gcp_project_id:
            print("Error: GCP Project ID not set")
            return False
            
        print(f"Getting credentials for cluster: {cluster_name}")
        command = f"gcloud container clusters get-credentials {cluster_name} --zone={self.gcp_zone} --project={self.gcp_project_id}"
        return self._run_command(command, self.project_root)

    def delete_gke_cluster(self, cluster_name="bytechat-cluster"):
        """Deletes a GKE cluster."""
        if not self.gcp_project_id:
            print("Error: GCP Project ID not set")
            return False
            
        print(f"Deleting GKE cluster: {cluster_name}")
        command = f"gcloud container clusters delete {cluster_name} --zone={self.gcp_zone} --quiet --project={self.gcp_project_id}"
        return self._run_command(command, self.project_root)

if __name__ == '__main__':
    # Example usage:
    project_path = os.path.dirname(os.path.abspath(__file__))
    
    # Initialize with GCP project ID for container deployment
    gcp_project_id = "your-gcp-project-id"  # Replace with your actual project ID
    pipeline = DevOpsPipeline(project_root=project_path, gcp_project_id=gcp_project_id)

    # Traditional deployment methods
    print("=== Traditional Deployment Methods ===")
    # pipeline.docker_build('messaging-app')
    # pipeline.kube_apply()
    # pipeline.terraform_init()
    # pipeline.terraform_plan()
    # pipeline.terraform_apply()
    # pipeline.ansible_playbook()
    # pipeline.helm_install('messaging-app-release')
    
    print("\n=== New GCP Container Deployment Methods ===")
    # Validate deployment prerequisites
    # pipeline.validate_deployment_prerequisites()
    
    # Build and deploy to GCP using containers
    # pipeline.docker_build_gcp('bytechat', 'v1.0.0')
    # pipeline.docker_push_gcr('bytechat', 'v1.0.0')
    
    # Deploy using automated script (recommended)
    # pipeline.deploy_to_gcp_containers()
    
    # Or deploy using Ansible directly
    # pipeline.ansible_playbook_gcp('gcp_deploy_config.yml')
    
    # Manage GKE clusters manually
    # pipeline.create_gke_cluster()
    # pipeline.get_gke_credentials()
    
    # Check deployment status
    # pipeline.deploy_gcp_status()
    
    # Cleanup when done
    # pipeline.cleanup_gcp_deployment()
    
    print("DevOps Pipeline initialized successfully!")
    print(f"Project root: {pipeline.project_root}")
    print(f"GCP Project: {pipeline.gcp_project_id}")
    print(f"Available methods: {[method for method in dir(pipeline) if not method.startswith('_')]}")
