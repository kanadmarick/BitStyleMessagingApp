# ByteChat - High-Level Architecture

## 1. Overview

ByteChat is a real-time, two-person chat application with a retro "hacker terminal" aesthetic. It features modern React frontend, Flask backend, end-to-end encryption using ECDH key exchange and AES-GCM, and automated deployment with Ansible.

The application prioritizes security and privacy through client-side encryption, where the server only handles encrypted message relay and never accesses plaintext content. The project includes a fully automated CI/CD pipeline for building, testing, and deploying to Kubernetes on Google Cloud Platform (GCP).

## 2. Application Architecture

The application is composed of two main components: a React frontend and a Flask backend, connected via WebSocket.

### 2.1. Frontend (React)

*   **Location:** `React/frontend/`
*   **Technology:** React.js, JavaScript ES6+
*   **Frameworks/Libraries:**
    *   **Socket.IO Client:** Real-time WebSocket communication with backend
    *   **Web Crypto API:** Browser-native ECDH key exchange and AES-GCM encryption
*   **Key Features:**
    *   **Dynamic Backend Detection:** Automatically tries ports 5001-5010 for backend connection
    *   **Terminal UI:** Retro green-on-black terminal aesthetic with ByteChat branding
    *   **ECDH Key Exchange:** P-256 curve key pair generation for secure communication
    *   **Real-time Messaging:** Instant message delivery with join/leave notifications
    *   **Mobile Responsive:** Optimized for desktop and mobile browsers

### 2.2. Backend (Flask)

*   **Technology:** Python 3.12+
*   **Frameworks/Libraries:**
    *   **Flask:** Micro web framework for HTTP handling
    *   **Flask-SocketIO:** WebSocket management for real-time communication
    *   **SQLite3:** Message persistence and history storage
*   **Key Features:**
    *   **Auto-Port Selection:** Tries ports 5001-5010 to avoid conflicts
    *   **Room Management:** Enforces two-user limit and unique usernames
    *   **Message Relay:** Handles encrypted message broadcasting between users
    *   **Join/Leave Notifications:** System messages for user presence updates
    *   **Debug Logging:** Comprehensive logging for troubleshooting

### 2.3. Automated Deployment

*   **Technology:** Ansible
*   **Location:** `ansible/playbook_start_bytechat.yml`
*   **Features:**
    *   **Failsafe Port Detection:** Automatically finds available ports for both services
    *   **Virtual Environment Management:** Python dependency isolation with `.venv/`
    *   **Service Orchestration:** Coordinated startup of React and Flask services
    *   **One-Command Deployment:** `ansible-playbook ansible/playbook_start_bytechat.yml`

## 3. Security Architecture

### 3.1. Encryption System
*   **Key Exchange:** Elliptic Curve Diffie-Hellman (ECDH) with P-256 curve
*   **Message Encryption:** AES-GCM 256-bit authenticated encryption
*   **Client-Side Only:** All cryptographic operations occur in the browser
*   **No Key Transmission:** Private keys never leave the client
*   **Plaintext Fallback:** Supports unencrypted mode for single-user scenarios

### 3.2. Server Security
*   **Message Relay Only:** Server never accesses plaintext message content
*   **User Validation:** Username uniqueness and room capacity enforcement
*   **Connection Security:** WebSocket with CORS support for secure communication

## 4. DevOps and Deployment Pipeline

The project includes both modern automated deployment (Ansible) and traditional CI/CD pipeline capabilities.

### 4.1. Local Development (Ansible)

*   **Technology:** Ansible playbooks
*   **Deployment:** `ansible-playbook ansible/playbook_start_bytechat.yml`
*   **Features:**
    *   Automated React and Flask service startup
    *   Virtual environment creation and dependency installation
    *   Dynamic port detection and conflict resolution
    *   Service health monitoring and logging

### 4.2. Containerization

*   **Technology:** Docker
*   **Implementation:** The application is containerized using a multi-stage `Dockerfile` to create a lightweight and secure production image. The container runs as a non-root user to minimize security risks.

### 4.3. CI/CD Pipeline

*   **Orchestration:** Jenkins (`Jenkinsfile`)
*   **Key Stages:**
    1.  **Checkout:** Pulls the latest code from the Git repository.
    2.  **Testing:** Runs automated unit and integration tests and generates code coverage reports.
    3.  **Build:** Builds the Docker image for the application.
    4.  **Push:** Pushes the Docker image to Google Container Registry (GCR).
    5.  **Infrastructure Provisioning:** Uses **Terraform** to create and manage the necessary infrastructure on GCP (e.g., a VM for the Kubernetes cluster).
    6.  **Configuration Management:** Uses **Ansible** to configure the provisioned infrastructure, installing a K3s Kubernetes cluster and Helm.
    7.  **Deployment:** Deploys the application to the Kubernetes cluster using a **Helm chart**.
    8.  **Cost Management:** Includes custom scripts to monitor GCP free tier usage before and after deployment to prevent unexpected costs.

### 4.4. Deployment Environment

*   **Cloud Provider:** Google Cloud Platform (GCP)
*   **Orchestration:** K3s (a lightweight Kubernetes distribution)
*   **Package Management:** Helm

## 5. Project Structure

```
.
├── React/
│   └── frontend/           # React.js frontend application
│       ├── src/
│       │   ├── App.js     # Main React component with messaging logic
│       │   └── App.css    # Terminal-style CSS
│       ├── public/        # Static React assets
│       └── package.json   # Node.js dependencies
├── ansible/
│   ├── playbook_start_bytechat.yml  # Automated deployment script
│   └── inventory          # Ansible inventory configuration
├── helm/                  # Helm chart for Kubernetes deployment
├── jenkins/               # Jenkinsfile for the CI/CD pipeline
├── k8s/                   # (Optional) Manual Kubernetes manifests
├── terraform/             # Terraform scripts for infrastructure provisioning
├── app.py                 # Flask backend with SocketIO and SQLite
├── index.html             # Legacy Flask-served frontend (deprecated)
├── messages.db            # SQLite database for message persistence
├── Dockerfile             # Docker configuration for containerizing the app
├── requirements.txt       # Python dependencies
├── .venv/                 # Python virtual environment (auto-created)
└── README.md              # Project documentation
```

## 6. Communication Flow

1. **User Access:** Users navigate to React frontend at `http://localhost:3000`
2. **Backend Detection:** React app attempts connection to Flask backend on ports 5001-5010
3. **Authentication:** Users enter username, React generates ECDH key pair
4. **Room Join:** Flask validates user and room capacity, broadcasts join notification
5. **Key Exchange:** (Optional) ECDH public keys exchanged for encryption setup
6. **Messaging:** Users send messages, encrypted client-side (if 2 users), relayed by Flask
7. **Real-time Updates:** All users receive messages and system notifications instantly
8. **Persistence:** Flask stores message history in SQLite database

## 4. Project Structure

```
.
├── ansible/              # Ansible playbooks for server configuration
├── helm/                 # Helm chart for Kubernetes deployment
├── jenkins/              # Jenkinsfile for the CI/CD pipeline
├── k8s/                  # (Optional) Manual Kubernetes manifests
├── terraform/            # Terraform scripts for infrastructure provisioning
├── app.py                # Backend Flask application
├── index.html            # Frontend HTML and JavaScript
├── Dockerfile            # Docker configuration for containerizing the app
├── requirements.txt      # Python dependencies
└── ...                   # Other configuration and documentation files
