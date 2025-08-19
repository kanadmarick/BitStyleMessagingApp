# Helm Usage

This document explains how Helm is used to manage the Kubernetes application.

## Charts (`helm/messaging-app`)

The `messaging-app` directory contains the Helm chart for this application.

### Key Features:

*   **Templates**: The `templates` directory contains Kubernetes manifest files that are templated with Go template syntax. This allows you to create reusable and configurable Kubernetes configurations.
*   **Values**: The `values.yaml` file contains the default values for the templates. You can override these values when you install or upgrade a chart, which makes it easy to configure the application for different environments.
*   **Chart Metadata**: The `Chart.yaml` file contains metadata about the chart, such as its name, version, and description.

## Benefits of Using Helm:

*   **Simplified Deployments**: Helm simplifies the process of deploying and managing complex applications on Kubernetes.
*   **Version Control**: Helm charts can be versioned and stored in a chart repository, which makes it easy to track and manage your deployments.
*   **Reusability**: Helm charts are reusable, which means you can share them with other teams and projects.
