import os
import subprocess

class DevOpsPipeline:
    def __init__(self, project_root):
        self.project_root = project_root
        self.dockerfile_path = os.path.join(project_root, 'Dockerfile')
        self.kubernetes_path = os.path.join(project_root, 'k8s')
        self.terraform_path = os.path.join(project_root, 'terraform')
        self.ansible_path = os.path.join(project_root, 'ansible')
        self.helm_path = os.path.join(project_root, 'helm', 'messaging-app')

    def _run_command(self, command, working_dir):
        """Helper function to run a shell command."""
        try:
            process = subprocess.Popen(command, cwd=working_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
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

    def docker_build(self, image_name, tag='latest'):
        """Builds a Docker image from the Dockerfile."""
        print(f"Building Docker image: {image_name}:{tag}")
        command = f"docker build -t {image_name}:{tag} -f {self.dockerfile_path} ."
        return self._run_command(command, self.project_root)

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

if __name__ == '__main__':
    # Example usage:
    project_path = os.path.dirname(os.path.abspath(__file__))
    pipeline = DevOpsPipeline(project_root=project_path)

    # Uncomment the following lines to test the pipeline
    # pipeline.docker_build('messaging-app')
    # pipeline.kube_apply()
    # pipeline.terraform_init()
    # pipeline.terraform_plan()
    # pipeline.terraform_apply()
    # pipeline.ansible_playbook()
    # pipeline.helm_install('messaging-app-release')
