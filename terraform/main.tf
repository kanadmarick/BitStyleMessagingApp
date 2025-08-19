# Terraform configuration for GCP free tier infrastructure

terraform {
  required_version = ">= 1.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 4.84"
    }
  }
}

# Configure the Google Cloud Provider
provider "google" {
  credentials = file(var.credentials_file)
  project     = var.project_id
  region      = var.region
  zone        = var.zone
}

# Variables
variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "credentials_file" {
  description = "Path to GCP service account credentials JSON file"
  type        = string
  default     = "gcp-key.json"
}

variable "region" {
  description = "GCP region"
  type        = string
  default     = "us-central1"  # Free tier eligible
}

variable "zone" {
  description = "GCP zone"
  type        = string
  default     = "us-central1-a"  # Free tier eligible
}

variable "machine_type" {
  description = "Machine type for VM instances"
  type        = string
  default     = "e2-micro"  # Free tier eligible
}

# Enable required APIs
resource "google_project_service" "compute_api" {
  service = "compute.googleapis.com"
}

resource "google_project_service" "container_api" {
  service = "container.googleapis.com"
}

# Create VPC Network
resource "google_compute_network" "vpc_network" {
  name                    = "messaging-app-network"
  auto_create_subnetworks = false
  depends_on              = [google_project_service.compute_api]
}

# Create subnet
resource "google_compute_subnetwork" "subnet" {
  name          = "messaging-app-subnet"
  ip_cidr_range = "10.0.0.0/24"
  region        = var.region
  network       = google_compute_network.vpc_network.id
}

# Create firewall rules
resource "google_compute_firewall" "allow_ssh" {
  name    = "allow-ssh"
  network = google_compute_network.vpc_network.name

  allow {
    protocol = "tcp"
    ports    = ["22"]
  }

  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["ssh-allowed"]
}

resource "google_compute_firewall" "allow_http" {
  name    = "allow-http"
  network = google_compute_network.vpc_network.name

  allow {
    protocol = "tcp"
    ports    = ["80", "443", "5000-5010"]
  }

  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["http-allowed"]
}

resource "google_compute_firewall" "allow_k8s" {
  name    = "allow-k8s"
  network = google_compute_network.vpc_network.name

  allow {
    protocol = "tcp"
    ports    = ["6443", "2379-2380", "10250-10252", "10255", "30000-32767"]
  }

  source_ranges = ["10.0.0.0/24"]
  target_tags   = ["k8s-cluster"]
}

# Create static IP for load balancer
resource "google_compute_global_address" "default" {
  name = "messaging-app-ip"
}

# Create VM instance for Kubernetes master
resource "google_compute_instance" "k8s_master" {
  name         = "k8s-master"
  machine_type = var.machine_type
  zone         = var.zone

  tags = ["ssh-allowed", "http-allowed", "k8s-cluster"]

  boot_disk {
    initialize_params {
      image = "ubuntu-os-cloud/ubuntu-2204-lts"
      size  = 20  # GB, within free tier limit
      type  = "pd-standard"  # Free tier eligible
    }
  }

  network_interface {
    network    = google_compute_network.vpc_network.id
    subnetwork = google_compute_subnetwork.subnet.id

    access_config {
      # Ephemeral public IP
    }
  }

  metadata = {
    ssh-keys = "${var.ssh_user}:${file(var.public_key_path)}"
  }

  metadata_startup_script = file("${path.module}/startup-script.sh")

  service_account {
    scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]
  }

  depends_on = [
    google_project_service.compute_api,
    google_compute_subnetwork.subnet
  ]
}

# SSH key variables
variable "ssh_user" {
  description = "SSH username"
  type        = string
  default     = "ubuntu"
}

variable "public_key_path" {
  description = "Path to public SSH key"
  type        = string
  default     = "~/.ssh/id_rsa.pub"
}

# Outputs
output "master_external_ip" {
  description = "External IP of Kubernetes master"
  value       = google_compute_instance.k8s_master.network_interface[0].access_config[0].nat_ip
}

output "master_internal_ip" {
  description = "Internal IP of Kubernetes master"
  value       = google_compute_instance.k8s_master.network_interface[0].network_ip
}

output "static_ip" {
  description = "Static IP for load balancer"
  value       = google_compute_global_address.default.address
}

output "network_name" {
  description = "VPC network name"
  value       = google_compute_network.vpc_network.name
}
