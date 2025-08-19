# Makefile for Messaging App CI/CD Pipeline

.PHONY: help setup build deploy test clean destroy

# Variables
PROJECT_ID ?= your-messaging-app-project
REGION ?= us-central1
ZONE ?= us-central1-a

# Colors for output
RED=\033[0;31m
GREEN=\033[0;32m
YELLOW=\033[1;33m
NC=\033[0m # No Color

help: ## Show this help message
	@echo "Messaging App CI/CD Pipeline Commands:"
	@echo ""
	@awk 'BEGIN {FS = ":.*##"; printf "Usage: make \033[36m<target>\033[0m\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) }' $(MAKEFILE_LIST)

##@ Setup Commands
setup: ## Initial setup - install dependencies and configure GCP
	@echo "$(YELLOW)Setting up development environment...$(NC)"
	@which gcloud >/dev/null || (echo "$(RED)Please install Google Cloud SDK first$(NC)" && exit 1)
	@which terraform >/dev/null || (echo "$(RED)Please install Terraform first$(NC)" && exit 1)
	@which ansible >/dev/null || (echo "$(RED)Please install Ansible first$(NC)" && exit 1)
	@echo "$(GREEN)Installing Python dependencies...$(NC)"
	pip install -r requirements.txt
	pip install ansible kubernetes
	@echo "$(GREEN)Setup completed!$(NC)"

setup-gcp: ## Setup GCP project and enable APIs
	@echo "$(YELLOW)Setting up GCP project...$(NC)"
	gcloud config set project $(PROJECT_ID)
	gcloud services enable compute.googleapis.com
	gcloud services enable container.googleapis.com
	gcloud services enable containerregistry.googleapis.com
	@echo "$(GREEN)GCP project setup completed!$(NC)"

create-sa: ## Create service account and download key
	@echo "$(YELLOW)Creating service account...$(NC)"
	gcloud iam service-accounts create messaging-app-ci --description="CI/CD service account" --display-name="Messaging App CI" || true
	gcloud projects add-iam-policy-binding $(PROJECT_ID) --member="serviceAccount:messaging-app-ci@$(PROJECT_ID).iam.gserviceaccount.com" --role="roles/compute.admin"
	gcloud projects add-iam-policy-binding $(PROJECT_ID) --member="serviceAccount:messaging-app-ci@$(PROJECT_ID).iam.gserviceaccount.com" --role="roles/container.admin"
	gcloud projects add-iam-policy-binding $(PROJECT_ID) --member="serviceAccount:messaging-app-ci@$(PROJECT_ID).iam.gserviceaccount.com" --role="roles/storage.admin"
	gcloud iam service-accounts keys create ./terraform/gcp-key.json --iam-account=messaging-app-ci@$(PROJECT_ID).iam.gserviceaccount.com
	@echo "$(GREEN)Service account created and key saved to terraform/gcp-key.json$(NC)"

ssh-keys: ## Generate SSH key pair for VM access
	@echo "$(YELLOW)Generating SSH key pair...$(NC)"
	ssh-keygen -t rsa -b 4096 -f ~/.ssh/messaging-app-key -N "" -q
	@echo "$(GREEN)SSH keys generated:$(NC)"
	@echo "Public key: ~/.ssh/messaging-app-key.pub"
	@echo "Private key: ~/.ssh/messaging-app-key"
	@echo "$(YELLOW)Add the private key content to GitHub Secrets as SSH_PRIVATE_KEY$(NC)"

##@ Testing Commands
test: ## Run all tests locally
	@echo "$(YELLOW)Running unit tests...$(NC)"
	python -m pytest test_app.py test_app_detailed.py -v
	@echo "$(YELLOW)Running integration tests...$(NC)"
	python test_integration.py
	@echo "$(GREEN)All tests passed!$(NC)"

test-docker: ## Build and test Docker image locally
	@echo "$(YELLOW)Building Docker image...$(NC)"
	docker build -t messaging-app:test .
	@echo "$(YELLOW)Testing Docker image...$(NC)"
	docker run -d -p 5000:5000 --name messaging-app-test messaging-app:test
	sleep 5
	curl -f http://localhost:5000 || (echo "$(RED)Docker test failed$(NC)" && exit 1)
	docker stop messaging-app-test
	docker rm messaging-app-test
	@echo "$(GREEN)Docker image test passed!$(NC)"

##@ Infrastructure Commands
init-terraform: ## Initialize Terraform
	@echo "$(YELLOW)Initializing Terraform...$(NC)"
	cd terraform && terraform init
	@echo "$(GREEN)Terraform initialized!$(NC)"

plan: ## Plan Terraform deployment
	@echo "$(YELLOW)Planning Terraform deployment...$(NC)"
	cd terraform && terraform plan
	@echo "$(GREEN)Terraform plan completed!$(NC)"

deploy-infra: ## Deploy infrastructure with Terraform
	@echo "$(YELLOW)Deploying infrastructure...$(NC)"
	cd terraform && terraform apply -auto-approve
	@echo "$(GREEN)Infrastructure deployed!$(NC)"

get-ip: ## Get VM IP address
	@cd terraform && terraform output -raw master_external_ip

update-inventory: ## Update Ansible inventory with VM IP
	@echo "$(YELLOW)Updating Ansible inventory...$(NC)"
	@VM_IP=$$(cd terraform && terraform output -raw master_external_ip); \
	echo "[k8s_master]" > ansible/inventory; \
	echo "k8s-master ansible_host=$$VM_IP" >> ansible/inventory
	@echo "$(GREEN)Ansible inventory updated!$(NC)"

##@ Configuration Commands
setup-k8s: ## Setup Kubernetes cluster with Ansible
	@echo "$(YELLOW)Setting up Kubernetes cluster...$(NC)"
	@echo "$(YELLOW)Waiting for VM to be ready...$(NC)"
	sleep 60
	cd ansible && ANSIBLE_HOST_KEY_CHECKING=False ansible-playbook -i inventory playbook.yml
	@echo "$(GREEN)Kubernetes cluster setup completed!$(NC)"

##@ Deployment Commands
build: ## Build and push Docker image
	@echo "$(YELLOW)Building Docker image...$(NC)"
	docker build -t gcr.io/$(PROJECT_ID)/messaging-app:latest .
	@echo "$(YELLOW)Pushing to Google Container Registry...$(NC)"
	gcloud auth configure-docker
	docker push gcr.io/$(PROJECT_ID)/messaging-app:latest
	@echo "$(GREEN)Image built and pushed!$(NC)"

deploy-app: ## Deploy application to Kubernetes
	@echo "$(YELLOW)Deploying application to Kubernetes...$(NC)"
	@VM_IP=$$(cd terraform && terraform output -raw master_external_ip); \
	sed -i.bak "s/PROJECT_ID/$(PROJECT_ID)/g" k8s/deployment.yaml; \
	scp -o StrictHostKeyChecking=no -i ~/.ssh/messaging-app-key k8s/*.yaml ubuntu@$$VM_IP:/home/ubuntu/; \
	ssh -o StrictHostKeyChecking=no -i ~/.ssh/messaging-app-key ubuntu@$$VM_IP "kubectl apply -f /home/ubuntu/configmap.yaml && kubectl apply -f /home/ubuntu/deployment.yaml"; \
	mv k8s/deployment.yaml.bak k8s/deployment.yaml
	@echo "$(GREEN)Application deployed!$(NC)"

status: ## Check application status
	@echo "$(YELLOW)Checking application status...$(NC)"
	@VM_IP=$$(cd terraform && terraform output -raw master_external_ip); \
	ssh -o StrictHostKeyChecking=no -i ~/.ssh/messaging-app-key ubuntu@$$VM_IP "kubectl get pods -n messaging-app && kubectl get services -n messaging-app"

logs: ## View application logs
	@VM_IP=$$(cd terraform && terraform output -raw master_external_ip); \
	ssh -o StrictHostKeyChecking=no -i ~/.ssh/messaging-app-key ubuntu@$$VM_IP "kubectl logs -n messaging-app deployment/messaging-app --tail=50"

##@ Jenkins CI/CD Commands
setup-jenkins: ## Setup Jenkins with Docker Compose
	@echo "$(YELLOW)Setting up Jenkins CI/CD server...$(NC)"
	./jenkins/setup-jenkins.sh
	@echo "$(GREEN)Jenkins setup completed!$(NC)"

start-jenkins: ## Start Jenkins server
	@echo "$(YELLOW)Starting Jenkins server...$(NC)"
	cd ~ && docker-compose -f docker-compose.jenkins.yml up -d
	@echo "$(GREEN)Jenkins started at http://localhost:8080$(NC)"

stop-jenkins: ## Stop Jenkins server
	@echo "$(YELLOW)Stopping Jenkins server...$(NC)"
	cd ~ && docker-compose -f docker-compose.jenkins.yml down
	@echo "$(GREEN)Jenkins stopped$(NC)"

jenkins-logs: ## View Jenkins logs
	cd ~ && docker-compose -f docker-compose.jenkins.yml logs -f jenkins

jenkins-password: ## Get Jenkins initial admin password
	@echo "$(YELLOW)Jenkins Initial Admin Password:$(NC)"
	@docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword || echo "Jenkins not running"

##@ Pipeline Commands  
full-deploy: test build deploy-infra update-inventory setup-k8s helm-deploy ## Full deployment pipeline
	@echo "$(GREEN)Full deployment completed!$(NC)"
	@echo "$(YELLOW)Application URL: http://$$(cd terraform && terraform output -raw master_external_ip)$(NC)"

helm-deploy: ## Deploy application with Helm
	@echo "$(YELLOW)Deploying application with Helm...$(NC)"
	@VM_IP=$$(cd terraform && terraform output -raw master_external_ip); \
	scp -o StrictHostKeyChecking=no -i ~/.ssh/messaging-app-key -r helm/messaging-app ubuntu@$$VM_IP:/home/ubuntu/; \
	ssh -o StrictHostKeyChecking=no -i ~/.ssh/messaging-app-key ubuntu@$$VM_IP "helm upgrade --install messaging-app ./messaging-app --namespace messaging-app --create-namespace --wait --timeout=300s"
	@echo "$(GREEN)Application deployed with Helm!$(NC)"

redeploy: build helm-deploy ## Redeploy just the application
	@echo "$(GREEN)Application redeployed!$(NC)"

##@ Utility Commands
ssh: ## SSH into the VM
	@VM_IP=$$(cd terraform && terraform output -raw master_external_ip); \
	ssh -i ~/.ssh/messaging-app-key ubuntu@$$VM_IP

port-forward: ## Port forward from VM to local machine
	@VM_IP=$$(cd terraform && terraform output -raw master_external_ip); \
	ssh -i ~/.ssh/messaging-app-key -L 8080:localhost:80 ubuntu@$$VM_IP

scale: ## Scale application (usage: make scale REPLICAS=3)
	@VM_IP=$$(cd terraform && terraform output -raw master_external_ip); \
	ssh -o StrictHostKeyChecking=no -i ~/.ssh/messaging-app-key ubuntu@$$VM_IP "kubectl scale deployment messaging-app --replicas=${REPLICAS:-2} -n messaging-app"

##@ Cleanup Commands
clean: ## Clean local Docker images
	@echo "$(YELLOW)Cleaning local Docker images...$(NC)"
	docker rmi messaging-app:test || true
	docker rmi gcr.io/$(PROJECT_ID)/messaging-app:latest || true
	docker system prune -f
	@echo "$(GREEN)Docker cleanup completed!$(NC)"

destroy: ## Destroy all infrastructure
	@echo "$(RED)WARNING: This will destroy all infrastructure!$(NC)"
	@echo "$(YELLOW)Press Ctrl+C to cancel, or wait 10 seconds to continue...$(NC)"
	@sleep 10
	@echo "$(YELLOW)Destroying infrastructure...$(NC)"
	cd terraform && terraform destroy -auto-approve
	@echo "$(GREEN)Infrastructure destroyed!$(NC)"

clean-gcp: ## Clean GCP resources (images, etc.)
	@echo "$(YELLOW)Cleaning GCP resources...$(NC)"
	gcloud container images list-tags gcr.io/$(PROJECT_ID)/messaging-app --format="get(digest)" --limit=10 | xargs -I {} gcloud container images delete gcr.io/$(PROJECT_ID)/messaging-app@{} --force-delete-tags --quiet || true
	@echo "$(GREEN)GCP cleanup completed!$(NC)"

##@ Development Commands
dev-setup: setup ssh-keys setup-gcp create-sa init-terraform ## Complete development setup
	@echo "$(GREEN)Development environment setup completed!$(NC)"
	@echo "$(YELLOW)Next steps:$(NC)"
	@echo "1. Copy terraform/gcp-key.json content to GitHub Secrets as GCP_SA_KEY"
	@echo "2. Copy ~/.ssh/messaging-app-key content to GitHub Secrets as SSH_PRIVATE_KEY"  
	@echo "3. Add your project ID to GitHub Secrets as GCP_PROJECT_ID"
	@echo "4. Push to main branch to trigger CI/CD pipeline"

local-dev: ## Run application locally for development
	@echo "$(YELLOW)Starting local development server...$(NC)"
	python app.py

##@ Information Commands
info: ## Show deployment information
	@echo "$(GREEN)Messaging App Deployment Information:$(NC)"
	@echo ""
	@echo "Project ID: $(PROJECT_ID)"
	@echo "Region: $(REGION)"
	@echo "Zone: $(ZONE)"
	@echo ""
	@if [ -f terraform/terraform.tfstate ]; then \
		echo "VM IP: $$(cd terraform && terraform output -raw master_external_ip 2>/dev/null || echo 'Not deployed')"; \
		echo "Static IP: $$(cd terraform && terraform output -raw static_ip 2>/dev/null || echo 'Not deployed')"; \
	else \
		echo "Infrastructure not deployed yet"; \
	fi
