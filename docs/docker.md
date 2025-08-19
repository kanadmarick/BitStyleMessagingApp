# Docker Usage

This document explains how Docker is used in this project for containerization and setting up the CI/CD pipeline with Jenkins.

## Application Containerization (`Dockerfile`)

The `Dockerfile` is used to package the Python Flask application into a lightweight, secure, and portable container.

### Key Features:

*   **Multi-Stage Build**: The Dockerfile uses a multi-stage build to create an optimized production image. A temporary `builder` stage installs the Python dependencies, and the final image copies only the necessary application files and dependencies. This results in a smaller and more secure container.
*   **Security**: The application is run by a non-root user (`app`), which is a security best practice that limits the container's privileges.
*   **Health Check**: A `HEALTHCHECK` is configured to monitor the application's status and ensure it's running correctly.

## CI/CD with Jenkins (`docker-compose.jenkins.yml`)

The `docker-compose.jenkins.yml` file sets up a Jenkins container to automate the build, test, and deployment processes (CI/CD).

### Key Features:

*   **Jenkins Service**: This file defines a Jenkins service that runs in a Docker container, using the official Jenkins LTS image.
*   **Docker in Docker**: The Jenkins container has access to the host machine's Docker socket (`/var/run/docker.sock`). This allows Jenkins to build and manage Docker images directly from within its container, which is essential for an automated CI/CD pipeline.
*   **Persistent Data**: The `jenkins_home` directory is mounted as a volume, which means your Jenkins configuration, jobs, and plugins are saved even if the container is restarted.
