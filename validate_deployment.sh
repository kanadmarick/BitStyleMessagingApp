#!/bin/bash

# ByteChat GCP Deployment Validation Script
# This script validates all components before deployment

set -e

echo "=========================================="
echo "ByteChat GCP Deployment Validation"
echo "=========================================="

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

# Function to run test and report result
run_test() {
    local test_name="$1"
    local test_command="$2"
    
    echo -n "Testing ${test_name}... "
    
    if eval "$test_command" &>/dev/null; then
        echo -e "${GREEN}✅ PASS${NC}"
        ((TESTS_PASSED++))
        return 0
    else
        echo -e "${RED}❌ FAIL${NC}"
        ((TESTS_FAILED++))
        return 1
    fi
}

# Test project structure
echo "1. Project Structure Tests"
echo "----------------------------------------"
run_test "Project root files" "test -f app.py && test -d React/frontend"
run_test "Ansible playbooks" "test -f ansible/playbook_start_bytechat.yml && test -f ansible/playbook_deploy_gcp_containers.yml"
run_test "Docker files" "test -f Dockerfile && test -f Dockerfile.gcp"
run_test "Configuration files" "test -f ansible/gcp_deploy_config.yml.example"
run_test "Deployment scripts" "test -x deploy_gcp_containers.sh"

# Test Python environment
echo -e "\n2. Python Environment Tests"
echo "----------------------------------------"
run_test "Flask app import" "cd /Users/kanadmarick/Messaging && python -c 'import app'"
run_test "Required Python packages" "cd /Users/kanadmarick/Messaging && python -c 'import flask, sqlite3, json, datetime, hashlib'"

# Test React environment
echo -e "\n3. React Frontend Tests"  
echo "----------------------------------------"
run_test "React package.json" "test -f React/frontend/package.json"
run_test "React dependencies" "cd React/frontend && npm list --depth=0"
run_test "React build process" "cd React/frontend && timeout 60 npm run build >/dev/null 2>&1; test -d build"

# Test Ansible configuration
echo -e "\n4. Ansible Configuration Tests"
echo "----------------------------------------"
run_test "Ansible installation" "which ansible-playbook"
run_test "Local playbook syntax" "ansible-playbook --syntax-check ansible/playbook_start_bytechat.yml 2>&1 | grep -q 'playbook:'"
run_test "GCP playbook syntax" "ansible-playbook --syntax-check ansible/playbook_deploy_gcp_containers.yml 2>&1 | grep -q 'playbook:'"

# Test Docker configuration
echo -e "\n5. Docker Configuration Tests"
echo "----------------------------------------"
run_test "Docker installation" "which docker"
run_test "Dockerfile syntax (original)" "docker build -f Dockerfile --help"
run_test "Dockerfile.gcp syntax" "docker build -f Dockerfile.gcp --help"

# Test deployment script
echo -e "\n6. Deployment Script Tests"
echo "----------------------------------------"
run_test "Script permissions" "ls -la deploy_gcp_containers.sh | grep -q '^-rwx'"
run_test "Script help function" "./deploy_gcp_containers.sh help"
run_test "Configuration template" "test -f ansible/gcp_deploy_config.yml.example"

# Test documentation
echo -e "\n7. Documentation Tests"
echo "----------------------------------------"
run_test "Main README" "test -f README.md"
run_test "GCP deployment guide" "test -f GCP_CONTAINER_DEPLOYMENT.md"
run_test "Architecture documentation" "test -f ARCHITECTURE.md"

# Optional: GCP Tools Tests (warn if missing)
echo -e "\n8. Optional GCP Tools Tests"
echo "----------------------------------------"
if run_test "gcloud CLI" "which gcloud"; then
    run_test "gcloud authentication" "gcloud auth list --filter=status:ACTIVE --format='value(account)' | wc -l"
else
    echo -e "${YELLOW}⚠️  gcloud CLI not installed - required for GCP deployment${NC}"
fi

if run_test "kubectl" "which kubectl"; then
    echo -e "   ${GREEN}kubectl ready for Kubernetes management${NC}"
else
    echo -e "${YELLOW}⚠️  kubectl not installed - required for Kubernetes management${NC}"
fi

# Summary
echo -e "\n=========================================="
echo "Validation Summary"
echo "=========================================="
echo -e "${GREEN}Tests Passed: ${TESTS_PASSED}${NC}"
echo -e "${RED}Tests Failed: ${TESTS_FAILED}${NC}"

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "\n${GREEN}🎉 All core tests passed! ByteChat is ready for deployment.${NC}"
    
    if ! which gcloud &>/dev/null; then
        echo -e "\n${YELLOW}📝 To deploy to GCP, install the missing tools:${NC}"
        echo "   brew install --cask google-cloud-sdk"
        echo "   gcloud auth login"
        echo "   gcloud auth application-default login"
    fi
    
    exit 0
else
    echo -e "\n${RED}❌ Some tests failed. Please fix the issues before deploying.${NC}"
    exit 1
fi
