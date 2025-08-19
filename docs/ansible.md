# Ansible Usage

This document explains how Ansible is used for configuration management and application deployment.

## Playbooks (`ansible/playbook.yml`)

The `playbook.yml` file defines a set of tasks to be executed on the target servers.

### Key Features:

*   **Automation**: Ansible playbooks automate the process of configuring servers, installing software, and deploying the application.
*   **Idempotent**: Playbooks are idempotent, which means they can be run multiple times without causing unintended side effects.
*   **YAML**: Playbooks are written in YAML, which is a human-readable data serialization language.

## Inventory (`ansible/inventory`)

The `inventory` file defines the servers that Ansible will manage.

### Key Features:

*   **Grouping**: You can group servers together (e.g., `webservers`, `dbservers`) to easily target specific sets of servers with your playbooks.
*   **Variables**: You can define variables for each host or group to customize the configuration for different environments.
