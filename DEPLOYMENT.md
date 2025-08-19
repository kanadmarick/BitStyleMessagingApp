# CI/CD Pipeline Setup Guide

This guide will help you set up the complete CI/CD pipeline with GCP free tier resources.

## Prerequisites

1. **GCP Account**: Sign up for Google Cloud Platform with $300 free credit
2. **GitHub Repository**: Your messaging app repository
3. **SSH Key Pair**: For accessing GCP VMs

## Step 1: GCP Project Setup

### 1.1 Create New Project
```bash
# Install gcloud CLI if not already installed
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# Login and create project
gcloud auth login
gcloud projects create your-messaging-app-project --name="Messaging App"
gcloud config set project your-messaging-app-project

# Enable billing (required for compute resources)
# Go to: https://console.cloud.google.com/billing
```

### 1.2 Enable Required APIs
```bash
gcloud services enable compute.googleapis.com
gcloud services enable container.googleapis.com
gcloud services enable containerregistry.googleapis.com
```

### 1.3 Create Service Account
```bash
# Create service account
gcloud iam service-accounts create messaging-app-ci \
    --description="CI/CD service account for messaging app" \
    --display-name="Messaging App CI"

# Grant necessary permissions
gcloud projects add-iam-policy-binding your-messaging-app-project \
    --member="serviceAccount:messaging-app-ci@your-messaging-app-project.iam.gserviceaccount.com" \
    --role="roles/compute.admin"

gcloud projects add-iam-policy-binding your-messaging-app-project \
    --member="serviceAccount:messaging-app-ci@your-messaging-app-project.iam.gserviceaccount.com" \
    --role="roles/container.admin"

gcloud projects add-iam-policy-binding your-messaging-app-project \
    --member="serviceAccount:messaging-app-ci@your-messaging-app-project.iam.gserviceaccount.com" \
    --role="roles/storage.admin"

# Create and download service account key
gcloud iam service-accounts keys create ~/gcp-key.json \
    --iam-account=messaging-app-ci@your-messaging-app-project.iam.gserviceaccount.com
```

## Step 2: GitHub Secrets Setup

Add the following secrets to your GitHub repository:
- Go to: `https://github.com/your-username/BitStyleMessagingApp/settings/secrets/actions`

### Required Secrets:
1. **GCP_PROJECT_ID**: `your-messaging-app-project`
2. **GCP_SA_KEY**: Content of `~/gcp-key.json` file
3. **SSH_PRIVATE_KEY**: Your private SSH key content

### Generate SSH Key:
```bash
# Generate SSH key pair
ssh-keygen -t rsa -b 4096 -f ~/.ssh/messaging-app-key -N ""

# Add public key content to terraform.tfvars
cat ~/.ssh/messaging-app-key.pub

# Add private key content to GitHub secrets
cat ~/.ssh/messaging-app-key
```

## Step 3: Local Development Setup

### 3.1 Create terraform.tfvars
```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars

# Edit terraform.tfvars with your values:
# project_id = "your-messaging-app-project"
# credentials_file = "../gcp-key.json"  # Copy from ~/gcp-key.json
# public_key_path = "~/.ssh/messaging-app-key.pub"
```

### 3.2 Test Terraform Locally (Optional)
```bash
# Initialize Terraform
terraform init

# Plan deployment
terraform plan

# Apply (optional - CI/CD will do this)
# terraform apply
```

## Step 4: Pipeline Architecture

### 4.1 Pipeline Stages
1. **Test Stage**: Run unit and integration tests
2. **Build Stage**: Build and push Docker image to GCR
3. **Infrastructure Stage**: Deploy GCP VM with Terraform
4. **Configuration Stage**: Setup Kubernetes with Ansible
5. **Deployment Stage**: Deploy app to Kubernetes cluster

### 4.2 Free Tier Resources Used
- **Compute Engine**: 1x e2-micro VM (always free)
- **Container Registry**: 0.5 GB storage (free tier)
- **Cloud Storage**: 5 GB (free tier)
- **Networking**: 1 GB egress per month (free tier)

### 4.3 Cost Optimization
- Uses `e2-micro` instances (always free)
- Kind (Kubernetes in Docker) instead of GKE
- Ephemeral IP addresses
- Standard persistent disks only

## Step 5: Deploy Pipeline

### 5.1 Commit and Push
```bash
git add .
git commit -m "Add CI/CD pipeline with GCP free tier resources"
git push origin main
```

### 5.2 Monitor Deployment
- Go to: `https://github.com/your-username/BitStyleMessagingApp/actions`
- Watch the pipeline execution
- Check each stage for any errors

### 5.3 Access Application
After successful deployment:
1. Check GitHub Actions summary for VM IP address
2. Access app at: `http://VM_IP_ADDRESS`
3. App runs on port 80 (proxied from internal port 5000)

## Step 6: Manual Operations

### 6.1 Access VM
```bash
# SSH to VM (replace with actual IP)
ssh -i ~/.ssh/messaging-app-key ubuntu@VM_IP_ADDRESS

# Check cluster status
kubectl get pods -n messaging-app
kubectl get services -n messaging-app

# Check application logs
kubectl logs -n messaging-app deployment/messaging-app
```

### 6.2 Update Application
```bash
# Just push to main branch
git add .
git commit -m "Update application"
git push origin main

# Pipeline will automatically:
# 1. Run tests
# 2. Build new image
# 3. Deploy to cluster
```

### 6.3 Scale Application
```bash
# SSH to VM and run:
kubectl scale deployment messaging-app --replicas=3 -n messaging-app
```

## Step 7: Cleanup

### 7.1 Destroy Infrastructure
```bash
# Locally
cd terraform
terraform destroy

# Or wait for auto-cleanup on pipeline failure
```

### 7.2 Clean Docker Images
```bash
# Remove old images from GCR
gcloud container images list-tags gcr.io/your-project/messaging-app
gcloud container images delete gcr.io/your-project/messaging-app:TAG
```

## Troubleshooting

### Common Issues:

1. **Permission Denied**
   - Check service account permissions
   - Verify GitHub secrets are correctly set

2. **VM Creation Failed**
   - Check GCP quotas and billing
   - Ensure APIs are enabled

3. **Ansible Connection Failed**
   - VM might still be initializing (wait 2-3 minutes)
   - Check SSH key format and permissions

4. **Kind Cluster Issues**
   - SSH to VM and check: `docker ps`
   - Restart with: `kind delete cluster --name=messaging-app && kind create cluster --config=kind-config.yaml --name=messaging-app`

5. **Application Not Accessible**
   - Check firewall rules: `gcloud compute firewall-rules list`
   - Verify ingress controller: `kubectl get pods -n ingress-nginx`

### Debug Commands:
```bash
# Check VM startup logs
gcloud compute instances get-serial-port-output k8s-master --zone=us-central1-a

# Check Kubernetes events
kubectl get events -n messaging-app

# Check pod logs
kubectl logs -n messaging-app deployment/messaging-app --follow
```

## Monitoring and Maintenance

### Daily Operations:
- Monitor GitHub Actions for failed deployments
- Check GCP billing dashboard
- Review application logs for errors

### Weekly Maintenance:
- Update base Docker image
- Review and rotate SSH keys
- Check for security updates

### Free Tier Limits:
- **Compute**: 1 f1-micro or e2-micro instance
- **Storage**: 30 GB standard persistent disk
- **Network**: 1 GB egress per month
- **Container Registry**: 0.5 GB storage

Stay within these limits to avoid charges!
