# ByteChat GCP Container Deployment Guide

## Overview
This guide explains how to deploy ByteChat to Google Cloud Platform using containers and Kubernetes.

## Prerequisites

### Required Tools
- **gcloud CLI**: Google Cloud command-line tool
- **Docker**: For building container images
- **kubectl**: Kubernetes command-line tool
- **Ansible**: For deployment automation

### Installation Commands (macOS)
```bash
# Install gcloud CLI
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# Install Docker Desktop
brew install --cask docker

# Install kubectl
brew install kubectl

# Install Ansible
brew install ansible
```

### GCP Setup
1. Create or select a GCP project
2. Enable required APIs:
   ```bash
   gcloud services enable container.googleapis.com
   gcloud services enable containerregistry.googleapis.com
   ```
3. Set up billing (required for GKE)

## Deployment Options

### Option 1: Quick Deploy (Recommended)
Use the automated deployment script:

```bash
# Deploy to GCP
./deploy_gcp_containers.sh deploy

# Check status
./deploy_gcp_containers.sh status

# Clean up resources
./deploy_gcp_containers.sh cleanup
```

### Option 2: Manual Ansible Deploy
```bash
# 1. Copy and configure deployment settings
cp ansible/gcp_deploy_config.yml.example ansible/gcp_deploy_config.yml
# Edit gcp_deploy_config.yml with your settings

# 2. Run deployment
ansible-playbook ansible/playbook_deploy_gcp_containers.yml \
  -e gcp_project_id=YOUR_PROJECT_ID \
  -e @ansible/gcp_deploy_config.yml
```

## Configuration

### Key Settings in `ansible/gcp_deploy_config.yml`
```yaml
# GCP Configuration
gcp_project_id: "your-gcp-project-id"
gcp_region: "us-central1"
gcp_zone: "us-central1-a"

# Cluster Configuration
gke_cluster_name: "bytechat-cluster"
gke_node_count: 3
gke_machine_type: "e2-standard-2"

# Application Configuration
app_name: "bytechat"
app_namespace: "bytechat"
docker_image_tag: "latest"
```

## Deployment Architecture

### Container Structure
- **Multi-stage Dockerfile** (`Dockerfile.gcp`)
  - Stage 1: React frontend build
  - Stage 2: Flask backend with built frontend
  - Production-optimized with health checks

### Kubernetes Resources
- **Namespace**: `bytechat`
- **Deployment**: 3 replicas with auto-scaling
- **Service**: LoadBalancer for external access
- **ConfigMap**: Environment configuration

### GCP Services Used
- **Google Kubernetes Engine (GKE)**: Container orchestration
- **Container Registry (GCR)**: Docker image storage
- **Cloud Load Balancer**: External access

## Access Your Application

After deployment, find your application URL:

```bash
# Get external IP
kubectl get service bytechat-service -n bytechat

# Or use the status command
./deploy_gcp_containers.sh status
```

The application will be available at: `http://[EXTERNAL_IP]:3000`

## Monitoring and Logs

```bash
# Check pod status
kubectl get pods -n bytechat

# View logs
kubectl logs -n bytechat deployment/bytechat-app -f

# Describe pods for troubleshooting
kubectl describe pods -n bytechat
```

## Scaling

```bash
# Scale replicas
kubectl scale deployment bytechat-app --replicas=5 -n bytechat

# Auto-scaling (if needed)
kubectl autoscale deployment bytechat-app --cpu-percent=70 --min=3 --max=10 -n bytechat
```

## Cost Management

### Expected Costs (approximate)
- **GKE Cluster**: ~$70-100/month for 3 e2-standard-2 nodes
- **Load Balancer**: ~$18/month
- **Container Registry**: Minimal for small images

### Cost Optimization
- Use smaller machine types for development
- Scale down replicas when not in use
- Clean up unused resources regularly

## Security Considerations

- GKE cluster uses Google's security defaults
- Private container registry (GCR)
- Network policies can be added for additional isolation
- HTTPS can be configured with Ingress and certificates

## Troubleshooting

### Common Issues
1. **Authentication Error**: Run `gcloud auth login`
2. **Project Not Found**: Verify project ID and billing
3. **API Not Enabled**: Enable Container and GKE APIs
4. **Resource Limits**: Check GCP quotas

### Debug Commands
```bash
# Check cluster status
gcloud container clusters describe bytechat-cluster --zone=us-central1-a

# Check node status
kubectl get nodes

# View events
kubectl get events -n bytechat --sort-by='.lastTimestamp'
```

## Cleanup

To remove all resources and avoid charges:

```bash
./deploy_gcp_containers.sh cleanup
```

This will delete:
- GKE cluster and all nodes
- LoadBalancer and external IP
- Container images in GCR
- All Kubernetes resources

## Support

For issues:
1. Check the deployment logs
2. Verify GCP quotas and billing
3. Review Kubernetes events
4. Check application logs in pods
