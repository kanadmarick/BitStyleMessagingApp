#!/bin/bash
# Jenkins setup script for messaging app CI/CD pipeline

set -e

echo "🚀 Setting up Jenkins for Messaging App CI/CD Pipeline"

# Check if running as root
if [ "$EUID" -eq 0 ]; then
  echo "❌ Please don't run this script as root"
  exit 1
fi

# Function to check if command exists
command_exists() {
  command -v "$1" >/dev/null 2>&1
}

# Install Docker if not present
if ! command_exists docker; then
  echo "🐳 Installing Docker..."
  curl -fsSL https://get.docker.com -o get-docker.sh
  sudo sh get-docker.sh
  sudo usermod -aG docker $USER
  rm get-docker.sh
  echo "✅ Docker installed"
else
  echo "✅ Docker already installed"
fi

# Install Docker Compose if not present
if ! command_exists docker-compose; then
  echo "🔧 Installing Docker Compose..."
  sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
  sudo chmod +x /usr/local/bin/docker-compose
  echo "✅ Docker Compose installed"
else
  echo "✅ Docker Compose already installed"
fi

# Install Terraform if not present
if ! command_exists terraform; then
  echo "🏗️ Installing Terraform..."
  wget -O- https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
  echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
  sudo apt update && sudo apt install terraform
  echo "✅ Terraform installed"
else
  echo "✅ Terraform already installed"
fi

# Install Ansible if not present
if ! command_exists ansible; then
  echo "🔧 Installing Ansible..."
  sudo apt update
  sudo apt install -y ansible
  echo "✅ Ansible installed"
else
  echo "✅ Ansible already installed"
fi

# Install Helm if not present
if ! command_exists helm; then
  echo "⛵ Installing Helm..."
  curl https://baltocdn.com/helm/signing.asc | gpg --dearmor | sudo tee /usr/share/keyrings/helm.gpg > /dev/null
  echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/helm.gpg] https://baltocdn.com/helm/stable/debian/ all main" | sudo tee /etc/apt/sources.list.d/helm-stable-debian.list
  sudo apt update && sudo apt install helm
  echo "✅ Helm installed"
else
  echo "✅ Helm already installed"
fi

# Create Jenkins directories
echo "📁 Creating Jenkins directories..."
mkdir -p ~/jenkins_home
mkdir -p ~/jenkins_home/plugins
mkdir -p ~/jenkins_home/jobs
sudo chown -R 1000:1000 ~/jenkins_home

# Create Jenkins Docker Compose file
echo "📝 Creating Jenkins Docker Compose configuration..."
cat > ~/docker-compose.jenkins.yml << 'EOF'
version: '3.8'
services:
  jenkins:
    image: jenkins/jenkins:lts
    container_name: jenkins
    restart: unless-stopped
    ports:
      - "8080:8080"
      - "50000:50000"
    volumes:
      - ~/jenkins_home:/var/jenkins_home
      - /var/run/docker.sock:/var/run/docker.sock
      - /usr/bin/docker:/usr/bin/docker
      - /usr/local/bin/docker-compose:/usr/local/bin/docker-compose
      - /usr/bin/terraform:/usr/bin/terraform
      - /usr/bin/ansible:/usr/bin/ansible
      - /usr/local/bin/helm:/usr/local/bin/helm
      - /usr/bin/kubectl:/usr/bin/kubectl
      - ~/.ssh:/var/jenkins_home/.ssh:ro
      - ~/google-cloud-sdk:/var/jenkins_home/google-cloud-sdk:ro
    environment:
      - JAVA_OPTS=-Djenkins.install.runSetupWizard=false
      - JENKINS_OPTS=--httpPort=8080
    user: root
    
  jenkins-agent:
    image: jenkins/inbound-agent:latest
    container_name: jenkins-agent
    restart: unless-stopped
    depends_on:
      - jenkins
    volumes:
      - ~/jenkins_home:/var/jenkins_home
      - /var/run/docker.sock:/var/run/docker.sock
      - /usr/bin/docker:/usr/bin/docker
    environment:
      - JENKINS_URL=http://jenkins:8080
      - JENKINS_AGENT_NAME=docker-agent
EOF

# Create Jenkins init script
echo "🔧 Creating Jenkins initialization script..."
cat > ~/jenkins-init.sh << 'EOF'
#!/bin/bash
# Jenkins initialization script

echo "🚀 Starting Jenkins..."

# Start Jenkins with Docker Compose
cd ~
docker-compose -f docker-compose.jenkins.yml up -d

echo "⏳ Waiting for Jenkins to start..."
sleep 30

# Get initial admin password
echo "📋 Jenkins Initial Setup:"
echo "=================================="
echo "🌐 Jenkins URL: http://localhost:8080"
echo "🔑 Initial Admin Password:"
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
echo "=================================="
echo ""
echo "📖 Next Steps:"
echo "1. Open http://localhost:8080 in your browser"
echo "2. Use the password above to unlock Jenkins"
echo "3. Install suggested plugins"
echo "4. Create an admin user"
echo "5. Configure the messaging app pipeline"
echo ""
echo "🔧 Required Jenkins Plugins:"
echo "- Pipeline"
echo "- Git"
echo "- Docker Pipeline"
echo "- Google Container Registry Auth Plugin"
echo "- SSH Agent Plugin"
echo "- Terraform Plugin"
echo ""
echo "🔐 Required Credentials (Add in Jenkins):"
echo "- gcp-service-account-key (Secret file: terraform/gcp-key.json)"
echo "- gcp-vm-ssh-key (SSH Username with private key: ~/.ssh/messaging-app-key)"
echo ""
echo "Jenkins is ready! 🎉"
EOF

chmod +x ~/jenkins-init.sh

# Create pipeline job configuration
echo "📋 Creating pipeline job configuration..."
mkdir -p ~/jenkins_home/jobs/messaging-app-pipeline
cat > ~/jenkins_home/jobs/messaging-app-pipeline/config.xml << 'EOF'
<?xml version='1.1' encoding='UTF-8'?>
<flow-definition plugin="workflow-job@2.40">
  <actions/>
  <description>Messaging App CI/CD Pipeline - GitHub → Docker Build → Terraform → Ansible → Helm Deploy</description>
  <keepDependencies>false</keepDependencies>
  <properties>
    <org.jenkinsci.plugins.workflow.job.properties.PipelineTriggersJobProperty>
      <triggers>
        <com.cloudbees.jenkins.GitHubPushTrigger plugin="github@1.34.0">
          <spec></spec>
        </com.cloudbees.jenkins.GitHubPushTrigger>
      </triggers>
    </org.jenkinsci.plugins.workflow.job.properties.PipelineTriggersJobProperty>
  </properties>
  <definition class="org.jenkinsci.plugins.workflow.cps.CpsScmFlowDefinition" plugin="workflow-cps@2.92">
    <scm class="hudson.plugins.git.GitSCM" plugin="git@4.8.2">
      <configVersion>2</configVersion>
      <userRemoteConfigs>
        <hudson.plugins.git.UserRemoteConfig>
          <url>https://github.com/kanadmarick/BitStyleMessagingApp.git</url>
        </hudson.plugins.git.UserRemoteConfig>
      </userRemoteConfigs>
      <branches>
        <hudson.plugins.git.BranchSpec>
          <name>*/main</name>
        </hudson.plugins.git.BranchSpec>
      </branches>
      <doGenerateSubmoduleConfigurations>false</doGenerateSubmoduleConfigurations>
      <submoduleCfg class="list"/>
      <extensions/>
    </scm>
    <scriptPath>jenkins/Jenkinsfile</scriptPath>
    <lightweight>true</lightweight>
  </definition>
  <triggers/>
  <disabled>false</disabled>
</flow-definition>
EOF

# Create Jenkins plugins list
echo "🔌 Creating Jenkins plugins list..."
cat > ~/jenkins_home/plugins.txt << 'EOF'
ant:1.13
antisamy-markup-formatter:2.7
build-timeout:1.24
credentials-binding:1.27
email-ext:2.87
git:4.8.2
github:1.34.0
gradle:1.36
ldap:2.7
mailer:1.34
matrix-auth:2.6.7
pam-auth:1.6
pipeline-github-lib:1.0
pipeline-stage-view:2.21
ssh-slaves:1.32
timestamper:1.13
workflow-aggregator:2.6
ws-cleanup:0.39
docker-workflow:1.28
google-container-registry-auth:0.3
ssh-agent:1.23
terraform:1.0.10
kubernetes:1.30.0
helm:1.1.0
EOF

echo "✅ Jenkins setup completed!"
echo ""
echo "🚀 To start Jenkins, run:"
echo "  ~/jenkins-init.sh"
echo ""
echo "📖 After Jenkins starts, you'll need to:"
echo "1. Configure Jenkins with the initial admin password"
echo "2. Install the required plugins"
echo "3. Add the required credentials:"
echo "   - gcp-service-account-key (terraform/gcp-key.json)"
echo "   - gcp-vm-ssh-key (~/.ssh/messaging-app-key)"
echo "4. The pipeline job will be automatically created"
echo ""
echo "🌐 Jenkins will be available at: http://localhost:8080"
