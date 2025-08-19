# Terraform Usage

This document explains how Terraform is used to provision and manage the infrastructure for this project.

## Infrastructure as Code (`terraform/main.tf`)

The `main.tf` file defines the infrastructure resources that need to be created, such as virtual machines, networks, and firewall rules.

### Key Features:

*   **Declarative**: The infrastructure is defined in a declarative language, which makes it easy to understand and manage.
*   **Providers**: Terraform uses providers to interact with the APIs of cloud providers (e.g., AWS, Google Cloud, Azure) to provision the infrastructure.
*   **State Management**: Terraform keeps track of the state of the infrastructure, which allows it to plan and apply changes in an intelligent and predictable way.

## Variables (`terraform/terraform.tfvars`)

The `terraform.tfvars` file is used to provide values for the variables defined in the Terraform configuration.

### Key Features:

*   **Parameterization**: This allows you to parameterize your infrastructure, making it easy to create different environments (e.g., development, staging, production) with the same configuration.
*   **Separation of Concerns**: It separates the configuration from the infrastructure definition, which makes the code cleaner and easier to maintain.
