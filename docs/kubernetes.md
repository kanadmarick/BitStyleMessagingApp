# Kubernetes Usage

This document explains how Kubernetes is used to deploy and manage the application.

## Deployment (`k8s/deployment.yaml`)

The `deployment.yaml` file defines the desired state for the application's deployment in the Kubernetes cluster.

### Key Features:

*   **Replicas**: The deployment is configured to run a specified number of application pods, ensuring high availability.
*   **Container Spec**: It defines the container image to be used, the ports to expose, and resource requests and limits to ensure the application has the resources it needs to run efficiently.
*   **Rolling Updates**: The deployment strategy is set to `RollingUpdate`, which ensures that the application is updated with zero downtime.

## Configuration (`k8s/configmap.yaml`)

The `configmap.yaml` file is used to store application configuration data as key-value pairs, which can be consumed by the application pods.

### Key Features:

*   **Decoupling**: This decouples the application's configuration from the container image, making it easier to manage and update the configuration without rebuilding the image.
*   **Environment Variables**: The ConfigMap can be used to inject configuration data into the application pods as environment variables.
