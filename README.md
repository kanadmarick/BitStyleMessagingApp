# ByteChat - Real-time Messaging App

## Overview
Secure, real-time messaging with client-side ECDH key exchange, AES encryption, React frontend, Flask + SocketIO backend, and a retro terminal-style UI. Features automated deployment, GCP container deployment, and comprehensive DevOps automation.

**Key Features:**
- 🔐 **Security**: ECDH Key Exchange + AES-GCM End-to-End Encryption
- ⚛️ **Frontend**: Modern React with Dynamic Backend Detection
- 📱 **Mobile-First**: Touch-optimized UI with 16px fonts, responsive breakpoints
- 💻 **Design**: Matrix/ByteChat Terminal Aesthetic with PWA support
- ⚡ **Real-Time**: WebSocket Communication with Socket.IO
- 👥 **Rooms**: Two-User Limit with Join/Leave Notifications
- 💾 **Persistence**: SQLite Message Storage with usage analytics
- 📊 **Observability**: Complete Prometheus + Grafana monitoring stack
- 🔍 **Metrics**: Custom application metrics and system monitoring
- 🚨 **Alerting**: Multi-channel notifications (Email, Slack, Discord)
- 🤖 **Automation**: Ansible-Based Local & GCP Deployment
- 🔧 **Reliability**: Failsafe Port Detection (5001-5010 range)
- 🧪 **Testing**: Comprehensive Test Suite with Validation
- 🚀 **CI/CD**: Jenkins Pipeline with GCP Integration
- 🐳 **Containers**: Multi-stage Docker builds (React + Flask)
- ☸️ **Kubernetes**: GKE deployment with LoadBalancer
- 🏗️ **Infrastructure**: Terraform + Ansible automation
- ☁️ **Cloud**: Google Cloud Platform container deployment

---

## 🚀 Quick Start Options

### Option 1: Local Deployment (Ansible - Recommended)
```bash
# Start both React frontend and Flask backend automatically
ansible-playbook ansible/playbook_start_bytechat.yml
```
Access at **http://localhost:3000** (React frontend)

### Option 2: GCP Container Deployment (Production)
```bash
# Deploy to Google Cloud Platform using containers
./deploy_gcp_containers.sh deploy
```
Access at the external IP provided after deployment

### Option 3: Manual Local Development
```bash
# Start Flask backend
source .venv/bin/activate
python app.py

# In another terminal, start React frontend
cd React/frontend
npm start
```

### Option 4: Complete Monitoring Stack
```bash
# Start the full observability stack
./start_monitoring_stack.sh

# Access monitoring services:
# - Grafana: http://localhost:3000 (admin/admin)
# - Prometheus: http://localhost:9090
# - Flask App Metrics: http://localhost:5003/metrics
```

---

## 🏗️ Architecture Overview

### Frontend (React)
- **Location**: `React/frontend/`
- **Technology**: React.js with Socket.IO client
- **Features**:
  - Dynamic backend port detection (tries ports 5001-5010)
  - ECDH key pair generation for encryption
  - Retro terminal styling with ByteChat branding
  - Real-time message display with join/leave notifications
  - Automatic reconnection and error handling

### Backend (Flask)
- **Location**: `app.py`
- **Technology**: Flask + Flask-SocketIO + Prometheus
- **Features**:
  - Auto-port selection (5001-5010) to avoid conflicts
  - Two-user room management with overflow handling
  - Message persistence with SQLite database
  - Join/leave notifications as system messages
  - Prometheus metrics endpoint (`/metrics`)
  - Health check endpoint (`/health`)
  - Comprehensive debug logging for troubleshooting

### Monitoring Stack
- **Location**: `docker-compose.monitoring.yml`
- **Components**:
  - **Prometheus** (Port 9090): Metrics collection and querying
  - **Grafana** (Port 3000): Visualization dashboards
  - **Node Exporter** (Port 9100): System metrics (CPU, memory, disk)
  - **cAdvisor** (Port 8081): Container metrics
  - **Jenkins** (Port 8080): CI/CD with monitoring integration
- **Custom Metrics**:
  - `messages_total`: Total messages in database
  - `active_users`: Current connected users
  - `database_size_bytes`: SQLite database file size
  - `app_uptime_seconds`: Application runtime
  - `http_request_duration_seconds`: Response time histogram

### Notification System
- **Location**: `notification_manager.py`
- **Channels**: Email, Slack, Discord
- **Features**: HTML formatting, severity levels, rate limiting

### Analytics Dashboard
- **Location**: `gcp_analytics.py`
- **Features**: Usage patterns, peak hours analysis, user engagement metrics

### DevOps Automation
- **Location**: `devops_automation.py`
- **Technology**: Python automation class with 20+ methods
- **Features**:
  - Traditional DevOps (Docker, Kubernetes, Terraform, Ansible, Helm)
  - GCP container deployment automation
  - Multi-stage Docker builds with React + Flask
  - Google Container Registry integration
  - GKE cluster management and scaling

---

## 📁 File Structure & Documentation

### Core Application Files
- `app.py`: Flask + SocketIO backend with auto-port selection and SQLite persistence
- `React/frontend/`: React.js frontend with dynamic backend detection and terminal UI
- `messages.db`: SQLite database for message persistence
- `index.html`: Legacy Flask-served frontend (deprecated in favor of React)

### DevOps & Deployment
- `devops_automation.py`: **NEW** - Comprehensive DevOps automation class (290 lines)
- `deploy_gcp_containers.sh`: **NEW** - One-command GCP container deployment script
- `validate_deployment.sh`: **NEW** - Comprehensive deployment validation script
- `ansible/playbook_start_bytechat.yml`: Local development deployment automation
- `ansible/playbook_deploy_gcp_containers.yml`: **NEW** - GCP container deployment automation
- `ansible/gcp_deploy_config.yml.example`: **NEW** - GCP deployment configuration template

### Containerization
- `Dockerfile`: Original Flask-only container configuration
- `Dockerfile.gcp`: **NEW** - Multi-stage React + Flask production container
- `docker-compose.jenkins.yml`: Jenkins CI/CD container configuration

### Infrastructure as Code
- `terraform/`: GCP infrastructure provisioning (VMs, networking, storage)
- `k8s/`: Kubernetes manifests for container orchestration
- `helm/`: Helm charts for Kubernetes deployments
- `ansible/`: Configuration management and cluster setup

### CI/CD Pipeline
- `jenkins/Jenkinsfile`: Complete CI/CD pipeline with GCP integration
- `jenkins/setup-jenkins.sh`: Jenkins server setup automation
- `.github/workflows/`: GitHub Actions pipeline configurations

### Testing & Validation
- `test_app.py`: Basic Flask backend unit tests
- `test_app_extended.py`: Extended backend functionality tests
- `test_devops_pipeline.py`: **NEW** - DevOps automation class tests
- `test_end_to_end_system.py`: Full system integration tests
- `test_key_exchange.py`: Encryption and security tests

### Documentation
- `README.md`: This comprehensive project documentation
- `GCP_CONTAINER_DEPLOYMENT.md`: **NEW** - Complete GCP deployment guide
- `devops_automation_readme.md`: **UPDATED** - DevOps automation documentation
- `ARCHITECTURE.md`: Technical architecture and design decisions
- `DEPLOYMENT.md`: Traditional CI/CD pipeline setup guide
- `MESSAGING_APP_STATUS.md`: Current project status and roadmap

---

## ☁️ Cloud Deployment Options

### 🎯 GCP Container Deployment (Recommended for Production)

**One-Command Deployment:**
```bash
# Validates prerequisites, builds containers, deploys to GKE
./deploy_gcp_containers.sh deploy

# Check deployment status
./deploy_gcp_containers.sh status

# Clean up resources when done
./deploy_gcp_containers.sh cleanup
```

**Architecture:**
- **Container Registry**: Multi-stage Docker images (React + Flask)
- **Google Kubernetes Engine**: Managed Kubernetes with LoadBalancer
- **Auto-scaling**: Horizontal pod autoscaling based on CPU/memory
- **Health Checks**: Kubernetes liveness and readiness probes
- **Cost Optimized**: Uses free-tier eligible resources (e2-micro nodes)

**Prerequisites:**
- Google Cloud Project with billing enabled
- `gcloud`, `docker`, `kubectl`, `ansible-playbook` installed
- GCP authentication: `gcloud auth login`

### 🏗️ Traditional Infrastructure Deployment

**Using DevOps Automation:**
```bash
# Use the comprehensive DevOps pipeline class
python3 -c "
from devops_automation import DevOpsPipeline
pipeline = DevOpsPipeline('/path/to/bytechat', gcp_project_id='my-project')
pipeline.validate_deployment_prerequisites()
pipeline.deploy_to_gcp_containers()
"
```

**Manual Infrastructure:**
```bash
# Terraform infrastructure provisioning
cd terraform
terraform init && terraform apply

# Ansible configuration management
cd ansible
ansible-playbook playbook.yml -i inventory

# Kubernetes deployment
kubectl apply -f k8s/
---

## 🚀 CI/CD & DevOps Pipeline

### Automated Pipeline Stages

**Modern Jenkins Pipeline (jenkins/Jenkinsfile):**
1. **Checkout**: Code pulled from GitHub repository
2. **GCP Free Tier Check**: Pre-deployment cost validation
3. **Testing**: Comprehensive unit and integration tests
4. **Docker Build**: Multi-stage container creation and push to GCR
5. **Infrastructure**: Terraform provisioning of GCP resources
6. **Configuration**: Ansible setup of Kubernetes clusters
7. **Deployment**: Helm-based application deployment
8. **Health Checks**: Automated verification and monitoring
9. **Post-Deployment**: Cost monitoring with emergency shutdown

**DevOps Automation Class Integration:**
```bash
# Integrated with DevOps pipeline class
from devops_automation import DevOpsPipeline

pipeline = DevOpsPipeline(
    project_root=os.getcwd(),
    gcp_project_id=os.getenv('GCP_PROJECT_ID')
)

# Automated workflow
pipeline.validate_deployment_prerequisites()
pipeline.docker_build_gcp('bytechat', build_number)
pipeline.docker_push_gcr('bytechat', build_number)
pipeline.deploy_to_gcp_containers()
```

### Legacy Jenkins Setup (Freestyle)
For simple setups, access Jenkins at http://localhost:8080:

```bash
# Setup Jenkins with automation
cd jenkins && ./setup-jenkins.sh
```
- Run tests: `python3 -m pytest -q || true`
- Build image: `docker build -t bitstyle-messaging:$BUILD_NUMBER .`
- Run: `docker run -d --name messaging-app-$BUILD_NUMBER -p 500$BUILD_NUMBER:5000 bitstyle-messaging:$BUILD_NUMBER || true`
For full pipeline migration, you can switch to a Jenkinsfile once the Pipeline plugin is installed.

---

## Core Functionality

### 🔐 Advanced Encryption System
- **ECDH Key Exchange**: Elliptic Curve Diffie-Hellman for secure key agreement
- **AES-GCM Encryption**: 256-bit AES with Galois/Counter Mode for authenticated encryption
- **Client-Side Processing**: All cryptographic operations happen in the browser
- **Plaintext Fallback**: Supports unencrypted messages for single-user scenarios
- **Key Generation**: Automatic P-256 curve key pair generation per session

### ⚛️ Modern React Frontend
- **Dynamic Backend Detection**: Automatically tries multiple ports (5001-5010)
- **Real-Time Messaging**: Socket.IO integration with automatic reconnection
- **Terminal Aesthetics**: Retro green-on-black design with ByteChat branding
- **Join/Leave Notifications**: System messages when users enter or exit
- **Mobile Responsive**: Optimized for both desktop and mobile browsers

### 🤖 Automated Deployment
- **Ansible Integration**: One-command deployment with `ansible-playbook ansible/playbook_start_bytechat.yml`
- **Failsafe Port Detection**: Automatically finds available ports for both services
- **Virtual Environment Support**: Python dependencies managed in `.venv/`
- **Service Management**: Graceful start/stop of both React and Flask services

### 🔒 Security & Privacy Features

### 🔒 Security & Privacy Features
- **Two-User Room Limit**: Maximum concurrent users per session
- **Username Uniqueness**: Prevents duplicate usernames in the same room
- **Server-Side Validation**: Message integrity checks and user authentication
- **No Plaintext Storage**: Server only stores encrypted message content
- **Automatic Disconnection**: Handles room capacity and security violations

### ⚡ Real-Time Communication
- **WebSocket Technology**: Flask-SocketIO for instant message delivery
- **Cross-Origin Support**: CORS enabled for flexible deployment
- **Connection Resilience**: Auto-reconnection and error handling
- **Multiple Port Support**: Automatic failover if primary port unavailable
- **Debug Logging**: Comprehensive logging for troubleshooting

### 📱 Mobile & Desktop Optimization
- **Responsive Design**: Works seamlessly on desktop and mobile
- **Touch-Friendly Interface**: 44px minimum touch targets for mobile
- **Viewport Optimization**: Proper scaling for different screen sizes
- **Monospace Typography**: Authentic terminal font rendering
- Touch-action properties for smooth interaction
- Tested and verified on iOS Safari browser

### 👥 Smart Room Management
- Enforced two-user limit per room with immediate disconnect
- Message persistence across sessions using SQLite database
- Message history automatically loaded on user join
- Graceful handling of user disconnections
- Prevents duplicate connections from same user
- User color assignment for message identification
- Automatic cleanup of disconnected sessions
- Detailed backend logging for debugging and monitoring

---

## Technical Architecture

### Backend (`app.py`)
- **Framework**: Flask with Flask-SocketIO for WebSocket support
- **Database**: SQLite for message persistence with automatic table creation
- **Auto-Port Selection**: Automatically finds an open port (tries 5001-5010). Also honors `PORT` env var.
- **CORS Configuration**: Enabled for cross-origin requests (`cors_allowed_origins='*'`)
- **Event Handling**:
  - `join`: User authentication, room assignment, and history delivery
  - `message`: Encrypted message relay and database storage
  - `disconnect`: Cleanup and user removal from rooms
- **API Endpoints**:
  - `/history`: REST endpoint for retrieving message history
- **Room Management**: Strict two-user limit with immediate disconnect for third user
- **User Tracking**: Maintains active user lists and prevents duplicates
- **Logging**: Comprehensive backend logging for joins, disconnects, and errors

### Frontend (`index.html`)
- **Responsive Design**: Mobile-first approach with viewport optimization
- **Canvas Graphics**: ASCII art banner with dynamic terminal effects
- **CryptoJS Integration**: Client-side AES encryption/decryption
- **Touch Optimization**: 44px minimum touch targets for mobile devices
- **Theme System**: Terminal aesthetic with monospace fonts and green-on-black color scheme
- **SocketIO Client**: Real-time communication with automatic reconnection
- **Error Handling**: User-friendly error messages and connection status

### Testing Suite
- **Unit Tests** (`test_app_detailed.py`): Comprehensive backend functionality testing
- **Integration Tests** (`test_integration.py`): End-to-end messaging scenarios with edge cases
- **Negative Tests**: Invalid usernames, duplicate users, invalid message types, send after disconnect
- **Edge Cases**: Room full scenarios, missing fields, empty/long messages, rapid join/leave
- **Persistence Tests**: Message storage and retrieval across sessions
- **Test Coverage**: User authentication, room limits, message encryption, disconnect handling
- **Verbose Output**: Detailed logging and assertions for debugging
- **Automated Testing**: Run via unittest framework with comprehensive assertions

---

## Security Architecture

### 🔐 Encryption Implementation
- **Algorithm**: AES-256 with CryptoJS library
- **Client-Side Only**: All encryption/decryption happens in browser
- **Zero-Knowledge**: Server never accesses plaintext messages
- **Key Management**: Room key serves as encryption password
- **Message Persistence**: Encrypted messages stored in SQLite database
- **History Delivery**: Previous encrypted messages loaded on join

### 🛡️ Security Measures
- **Input Validation**: Sanitized user inputs prevent XSS attacks
- **CORS Policy**: Controlled cross-origin resource sharing
- **Session Management**: Secure WebSocket connections with session tracking
- **Error Handling**: No sensitive information leaked in error messages
- **Network Security**: All encryption keys remain client-side

### ⚠️ Security Considerations
- **Key Sharing**: Room key must be shared through secure channels
- **Browser Security**: Depends on client-side browser security
- **Local Storage**: Encryption keys stored temporarily in browser memory
- **Network Traffic**: Only encrypted messages transmitted over network

---

## 💻 Development & Testing

### Prerequisites
- **Python**: 3.12+ with pip package manager
- **Node.js**: 18+ with npm for React frontend
- **Docker**: For containerization and deployment
- **Git**: Version control and repository management
- **Cloud Tools**: `gcloud`, `kubectl`, `ansible-playbook` for cloud deployment

### Development Setup

**Local Development Environment:**
```bash
# 1. Clone repository
git clone https://github.com/kanadmarick/BitStyleMessagingApp.git
cd BitStyleMessagingApp

# 2. Backend setup
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 3. Frontend setup  
cd React/frontend
npm install
npm run build  # For production builds

# 4. Start development
cd ../..
ansible-playbook ansible/playbook_start_bytechat.yml
```

**Manual Development:**
```bash
# Terminal 1: Backend
source .venv/bin/activate
python app.py

# Terminal 2: Frontend  
cd React/frontend
npm start
```

### Comprehensive Testing Suite

**Automated Testing:**
```bash
# Run complete validation
./validate_deployment.sh

# Individual test suites
python test_app.py                    # Basic backend functionality
python test_app_extended.py          # Extended backend features  
python test_end_to_end_system.py     # Full system integration
python test_key_exchange.py          # Encryption and security
python test_devops_pipeline.py       # DevOps automation testing
```

**Testing Coverage:**
- ✅ **Backend Tests**: Flask server, SocketIO, database operations
- ✅ **Frontend Tests**: React components, encryption, WebSocket communication
- ✅ **Integration Tests**: End-to-end user workflows and edge cases
- ✅ **Security Tests**: ECDH key exchange, AES encryption validation
- ✅ **DevOps Tests**: Deployment automation, infrastructure validation
- ✅ **Performance Tests**: Load testing, concurrent user handling
- ✅ **Mobile Tests**: iOS Safari, responsive design verification

### DevOps Automation Testing

**Pipeline Validation:**
```bash
# Test DevOps automation class
from devops_automation import DevOpsPipeline
pipeline = DevOpsPipeline(project_root='.', gcp_project_id='test-project')

# Validate all components
pipeline.validate_deployment_prerequisites()

# Test container builds
pipeline.docker_build_gcp('bytechat-test', 'latest')

# Test deployment workflows  
pipeline.deploy_gcp_status()
```

### Run Tests
```bash
pytest -q || python -m unittest -v
```

### Test Coverage
- ✅ User authentication and validation
- ✅ Two-user room limit enforcement with immediate disconnect
- ✅ Message encryption/decryption
- ✅ Message persistence and history retrieval
- ✅ Real-time message delivery
- ✅ User disconnect handling
- ✅ Error handling and edge cases
- ✅ Integration with SocketIO clients
- ✅ Negative test cases (invalid inputs, duplicate users)
- ✅ Edge cases (room full, missing fields, empty/long messages)

---

## Mobile Usage (iPhone Safari)

### Accessing on iPhone
1. **Find Network IP**: Check server startup logs for network URL
2. **Open Safari**: Navigate to http://YOUR_NETWORK_IP:PORT
3. **Add to Home Screen**: Tap share button → "Add to Home Screen" for app-like experience
4. **Full Screen**: Website optimized for mobile viewport and touch interaction

### Touch-Optimized Features
- **Large Touch Targets**: 44px minimum size for all interactive elements
- **Smooth Scrolling**: Optimized message area scrolling
- **Keyboard Handling**: Proper input focus and virtual keyboard support
- **Responsive Layout**: Adapts to different screen orientations

### Sharing Options
- **Local Network**: Share network IP with others on same WiFi
- **External Access**: Use ngrok or similar tunneling service
- **Cloud Deployment**: Deploy to Heroku, AWS, or similar platforms

---

## Development & Customization

### Code Structure
```
BitStyleMessagingApp/
├── app.py                 # Flask server with SocketIO and SQLite
├── index.html            # Frontend with terminal theme
├── messages.db           # SQLite database for message persistence
├── test_app.py           # Basic unit tests
├── test_app_detailed.py  # Comprehensive tests
├── test_integration.py   # Integration and edge case testing
├── README.md             # Documentation
└── __pycache__/          # Python cache files
```

---

## 🛠️ Advanced Configuration & Customization

### Environment Configuration
```bash
# Development environment variables
export FLASK_ENV=development        # Enable debug mode
export GCP_PROJECT_ID=my-project   # Set GCP project for deployment
export BYTECHAT_PORT=5001          # Override auto port selection
export BYTECHAT_DEBUG=true         # Enable detailed logging
```

### Customization Options
- **Theme Colors**: Modify CSS variables in `React/frontend/src/App.css`
- **Room Capacity**: Update user limit in `app.py` (default: 2 users)
- **Port Range**: Modify auto-port selection range (5001-5010)
- **Container Resources**: Adjust memory/CPU limits in `Dockerfile.gcp`
- **GKE Scaling**: Configure node count in `ansible/gcp_deploy_config.yml`

### Performance Tuning
- **Database**: SQLite optimizations for message persistence
- **WebSocket**: Connection pooling and keep-alive settings
- **Container**: Multi-stage builds for optimal image size
- **Kubernetes**: Resource requests and limits for efficient scheduling
- **CDN**: Static asset optimization for faster loading

---

## 🐛 Troubleshooting & Debugging

### Common Issues

#### Deployment Failures
```bash
# Check prerequisites
./validate_deployment.sh

# Check GCP authentication
gcloud auth list

# Verify Docker daemon
docker version

# Test Ansible connectivity
ansible localhost -m ping
```

#### Container Build Issues
```bash
# Build with verbose output
docker build -f Dockerfile.gcp -t test-build . --no-cache --progress=plain

# Check multi-stage build layers
docker history test-build
```

#### GKE Deployment Issues
```bash
# Check cluster status
kubectl cluster-info

# Verify pod health
kubectl get pods -n bytechat -o wide

# Check service endpoints
kubectl get services -n bytechat

# View detailed events
kubectl get events -n bytechat --sort-by='.lastTimestamp'
```

#### Application Runtime Issues
```bash
# Check backend logs
kubectl logs -n bytechat deployment/bytechat-deployment -f

# Test health endpoints
curl http://EXTERNAL_IP/health

# Verify database connectivity
sqlite3 messages.db "SELECT * FROM messages LIMIT 5;"
```

### Debug Mode
```bash
# Local development with debug
export FLASK_ENV=development
python app.py

# Container debug build
docker build -f Dockerfile.gcp -t bytechat-debug . --target backend

# GCP deployment with verbose logging
GCP_PROJECT_ID=my-project ./deploy_gcp_containers.sh deploy -v
```

---

## 🤝 Contributing & Development Workflow

### Getting Started
1. **Fork** the repository on GitHub
2. **Clone** your fork: `git clone https://github.com/YOUR_USERNAME/BitStyleMessagingApp.git`
3. **Create** feature branch: `git checkout -b feature/amazing-feature`
4. **Setup** development environment: `ansible-playbook ansible/playbook_start_bytechat.yml`

### Development Standards
- **Python**: PEP 8 compliance, type hints recommended
- **JavaScript/React**: ESLint configuration, modern ES6+ syntax
- **CSS**: Mobile-first responsive design principles
- **Docker**: Multi-stage builds, security best practices
- **Kubernetes**: Resource limits, health checks, security contexts
- **Documentation**: Update README.md and relevant docs

### Testing Requirements
```bash
# Run full test suite before committing
./validate_deployment.sh                # Infrastructure validation
python test_app.py                     # Backend unit tests
python test_app_extended.py            # Extended functionality
python test_end_to_end_system.py       # Integration tests
python test_devops_pipeline.py         # DevOps automation tests
```

### Pull Request Process
1. **Test Coverage**: Ensure >90% test coverage
2. **Documentation**: Update relevant documentation files
3. **Security**: No credentials or sensitive data in commits
4. **Changelog**: Add entry to `MESSAGING_APP_STATUS.md`
5. **Review**: Address all feedback before merge

---

## 📚 Documentation & Resources

### Complete Documentation Set
- **README.md**: This comprehensive project overview
- **GCP_CONTAINER_DEPLOYMENT.md**: Complete GCP deployment guide
- **devops_automation_readme.md**: DevOps automation class documentation
- **ARCHITECTURE.md**: Technical architecture and design decisions
- **DEPLOYMENT.md**: Traditional CI/CD pipeline setup
- **MESSAGING_APP_STATUS.md**: Current status and development roadmap

### API References
- **Flask Backend**: RESTful endpoints and WebSocket events
- **React Frontend**: Component architecture and state management
- **DevOps Automation**: Python class methods and configuration
- **Kubernetes**: Manifests, services, and deployment specifications

### External Resources
- [Flask-SocketIO Documentation](https://flask-socketio.readthedocs.io/)
- [React.js Official Guide](https://reactjs.org/docs/)
- [Google Kubernetes Engine](https://cloud.google.com/kubernetes-engine/docs)
- [Docker Multi-stage Builds](https://docs.docker.com/develop/dev-best-practices/dockerfile_best-practices/)
- [Ansible Automation](https://docs.ansible.com/ansible/latest/user_guide/)

---

## 📋 Project Status & Roadmap

**Current Version**: 2.0 (GCP Container Deployment Ready)
**Status**: Production Ready ✅

### ✅ Completed Features
- End-to-end encrypted messaging with ECDH + AES-GCM
- React frontend with dynamic backend detection
- Flask backend with auto-port selection and SQLite persistence
- Comprehensive DevOps automation (290-line Python class)
- GCP container deployment with Kubernetes orchestration
- Multi-stage Docker builds for production optimization
- Complete CI/CD pipeline with Jenkins integration
- Comprehensive testing suite (8 test files)
- Mobile-optimized responsive design
- Ansible automation for local and cloud deployment

### 🚀 Upcoming Features
- **Enhanced Security**: Certificate-based authentication
- **Scalability**: Redis backend for multi-instance deployments
- **Monitoring**: Prometheus + Grafana integration
- **Logging**: Centralized logging with ELK stack
- **Performance**: WebRTC for peer-to-peer messaging
- **Features**: File sharing, voice messages, typing indicators

---

## 📞 Support & Contact

- **Issues**: [GitHub Issues](https://github.com/kanadmarick/BitStyleMessagingApp/issues)
- **Discussions**: [GitHub Discussions](https://github.com/kanadmarick/BitStyleMessagingApp/discussions)
- **Documentation**: All docs included in repository
- **Security**: Report vulnerabilities via GitHub Security tab

**License**: MIT - see LICENSE file for details

---

**Built with ❤️ using React, Flask, Docker, Kubernetes, and Google Cloud Platform**

## License & Contact

### Repository
- **GitHub**: [kanadmarick/BitStyleMessagingApp](https://github.com/kanadmarick/BitStyleMessagingApp)
- **Issues**: Report bugs and feature requests via GitHub Issues
- **Contributions**: Pull requests welcome!

### Technical Support
- Check existing GitHub Issues before creating new ones
- Include error messages and browser/OS information
- Test with minimal configuration before reporting

---

## Changelog

### v3.0.0 (Latest)
- ✅ Message persistence with SQLite database
- ✅ Message history loaded on user join
- ✅ REST API endpoint for message history
- ✅ Comprehensive edge case testing
- ✅ Negative test cases for invalid inputs
- ✅ Detailed backend logging for debugging
- ✅ Strict room limit enforcement with immediate disconnect
- ✅ Enhanced integration test suite

### v2.0.0
- ✅ Terminal theme with monospace fonts
- ✅ iPhone Safari optimization
- ✅ Touch-friendly interface
- ✅ Integration test suite
- ✅ Auto-port selection
- ✅ User disconnect handling
- ✅ CORS configuration
- ✅ Comprehensive documentation

### v1.0.0 (Initial)
- ✅ Basic messaging functionality
- ✅ End-to-end encryption
- ✅ Two-user room limit
- ✅ WebSocket real-time communication
- ✅ Unit test coverage
