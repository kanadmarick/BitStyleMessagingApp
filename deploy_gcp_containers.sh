#!/bin/bash

# ByteChat GCP Container Deployment Script
# This script deploys ByteChat to Google Cloud Platform using containers

set -e  # Exit on any error

echo "=========================================="
echo "ByteChat GCP Container Deployment"
echo "=========================================="

# Configuration
PROJECT_ID=${GCP_PROJECT_ID:-""}
CONFIG_FILE="ansible/gcp_deploy_config.yml"

# Check prerequisites
check_prerequisites() {
    echo "Checking prerequisites..."
    
    # Check if running from project root
    if [[ ! -f "app.py" ]] || [[ ! -d "React/frontend" ]]; then
        echo "❌ Error: Please run this script from the ByteChat project root directory"
        exit 1
    fi
    
    # Check required tools
    local required_tools=("gcloud" "docker" "kubectl" "ansible-playbook")
    for tool in "${required_tools[@]}"; do
        if ! command -v "$tool" &> /dev/null; then
            echo "❌ Error: $tool is not installed or not in PATH"
            echo "Please install: $tool"
            exit 1
        fi
    done
    
    echo "✅ Prerequisites check passed"
}

# Get GCP project ID
get_project_id() {
    if [[ -z "$PROJECT_ID" ]]; then
        # Try to get from gcloud config
        PROJECT_ID=$(gcloud config get-value project 2>/dev/null || echo "")
        
        if [[ -z "$PROJECT_ID" ]]; then
            echo "Please enter your GCP Project ID:"
            read -r PROJECT_ID
            
            if [[ -z "$PROJECT_ID" ]]; then
                echo "❌ Error: GCP Project ID is required"
                exit 1
            fi
        fi
    fi
    
    echo "Using GCP Project: $PROJECT_ID"
}

# Create config file if it doesn't exist
setup_config() {
    if [[ ! -f "$CONFIG_FILE" ]]; then
        echo "Creating deployment configuration..."
        cp "${CONFIG_FILE}.example" "$CONFIG_FILE"
        
        # Update project ID in config
        sed -i.bak "s/your-gcp-project-id/$PROJECT_ID/g" "$CONFIG_FILE"
        rm "${CONFIG_FILE}.bak"
        
        echo "✅ Configuration file created: $CONFIG_FILE"
        echo "You can edit this file to customize your deployment"
    fi
}

# Authenticate with GCP
authenticate_gcp() {
    echo "Checking GCP authentication..."
    
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q "@"; then
        echo "Please authenticate with GCP:"
        gcloud auth login
        gcloud auth application-default login
    fi
    
    echo "✅ GCP authentication verified"
}

# Deploy using Ansible
deploy() {
    echo "=========================================="
    echo "Starting ByteChat deployment to GCP..."
    echo "=========================================="
    
    ansible-playbook \
        ansible/playbook_deploy_gcp_containers.yml \
        --extra-vars "gcp_project_id=$PROJECT_ID" \
        --extra-vars "@$CONFIG_FILE" \
        -v
}

# Cleanup function
cleanup() {
    echo "=========================================="
    echo "Cleaning up ByteChat GCP deployment..."
    echo "=========================================="
    
    read -p "This will DELETE all ByteChat resources in GCP. Continue? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # Delete Kubernetes resources
        kubectl delete namespace bytechat --ignore-not-found=true
        
        # Delete GKE cluster
        gcloud container clusters delete bytechat-cluster \
            --zone=us-central1-a \
            --quiet || true
        
        # Delete Docker images from GCR
        gcloud container images delete "gcr.io/$PROJECT_ID/bytechat" \
            --force-delete-tags \
            --quiet || true
            
        echo "✅ Cleanup completed"
    else
        echo "Cleanup cancelled"
    fi
}

# Status check
status() {
    echo "=========================================="
    echo "ByteChat GCP Deployment Status"
    echo "=========================================="
    
    echo "Kubernetes Pods:"
    kubectl get pods -n bytechat 2>/dev/null || echo "No ByteChat pods found"
    
    echo -e "\nKubernetes Services:"
    kubectl get services -n bytechat 2>/dev/null || echo "No ByteChat services found"
    
    echo -e "\nGKE Clusters:"
    gcloud container clusters list --filter="name:bytechat*" 2>/dev/null || echo "No ByteChat clusters found"
    
    echo -e "\nContainer Images:"
    gcloud container images list --filter="name:bytechat" 2>/dev/null || echo "No ByteChat images found"
}

# Show help
show_help() {
    echo "ByteChat GCP Container Deployment Script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  deploy    Deploy ByteChat to GCP (default)"
    echo "  status    Check deployment status"
    echo "  cleanup   Remove all ByteChat resources from GCP"
    echo "  help      Show this help message"
    echo ""
    echo "Environment Variables:"
    echo "  GCP_PROJECT_ID    Your GCP Project ID"
    echo ""
    echo "Examples:"
    echo "  GCP_PROJECT_ID=my-project-123 $0 deploy"
    echo "  $0 status"
    echo "  $0 cleanup"
}

# Main execution
main() {
    case "${1:-deploy}" in
        "deploy")
            check_prerequisites
            get_project_id
            authenticate_gcp
            setup_config
            deploy
            ;;
        "status")
            get_project_id
            status
            ;;
        "cleanup")
            get_project_id
            cleanup
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            echo "❌ Unknown command: $1"
            show_help
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
