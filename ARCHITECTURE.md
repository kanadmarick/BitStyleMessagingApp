# BitStyle Messaging App - High-Level Architecture

## 1. Overview

The BitStyle Messaging App is a real-time, two-person chat application designed with a retro "hacker terminal" aesthetic. It prioritizes security and privacy through end-to-end encryption, where the server has no access to the unencrypted content of the messages.

The project is built with a modern DevOps toolchain, featuring a fully automated CI/CD pipeline for building, testing, and deploying the application to a Kubernetes cluster on Google Cloud Platform (GCP).

## 2. Application Architecture

The application is composed of two main components: a frontend web interface and a backend server.

### 2.1. Frontend

*   **Technology:** HTML, CSS, JavaScript
*   **Frameworks/Libraries:**
    *   **Socket.IO Client:** For real-time communication with the backend.
    *   **CryptoJS:** For client-side AES encryption and decryption of all message content.
*   **Functionality:**
    *   **User Interface:** A single-page application with a retro, terminal-like design.
    *   **Login:** Users provide a username and a secret key to enter the chat.
    *   **End-to-End Encryption:** Messages are encrypted in the browser before being sent to the server and decrypted upon receipt. The secret key never leaves the client.

### 2.2. Backend

*   **Technology:** Python
*   **Frameworks/Libraries:**
    *   **Flask:** A micro web framework for serving the application and handling HTTP requests.
    *   **Flask-SocketIO:** Manages the real-time WebSocket connections for the chat.
*   **Functionality:**
    *   **Real-time Messaging:** Relays encrypted messages between the two users in the chat room.
    *   **Room Management:** Enforces a two-user limit per chat room and ensures unique usernames.
    *   **Persistence:** Stores the encrypted message history in a **SQLite** database (`messages.db`).

## 3. DevOps and Deployment Pipeline

The project is underpinned by a robust, automated CI/CD pipeline managed by Jenkins.

### 3.1. Containerization

*   **Technology:** Docker
*   **Implementation:** The application is containerized using a multi-stage `Dockerfile` to create a lightweight and secure production image. The container runs as a non-root user to minimize security risks.

### 3.2. CI/CD Pipeline

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

### 3.3. Deployment Environment

*   **Cloud Provider:** Google Cloud Platform (GCP)
*   **Orchestration:** K3s (a lightweight Kubernetes distribution)
*   **Package Management:** Helm

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
