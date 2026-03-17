# ------------------------------------------------------------------------------
# Production GKE Cluster with Least-Privilege IAM 
# ------------------------------------------------------------------------------

provider "google" {
  project = "equal-experts-demo-project"
  region  = "asia-south1"
}

# 1. Custom IAM Service Account for GKE Nodes (Best Practice)
resource "google_service_account" "gke_node_sa" {
  account_id   = "gist-api-gke-sa"
  display_name = "GKE Node Pool Service Account"
}

# 2. Grant only the exact IAM roles needed for observability
resource "google_project_iam_member" "gke_sa_roles" {
  for_each = toset([
    "roles/logging.logWriter",
    "roles/monitoring.metricWriter",
    "roles/monitoring.viewer"
  ])
  project = "equal-experts-demo-project"
  role    = each.key
  member  = "serviceAccount:${google_service_account.gke_node_sa.email}"
}

# 3. The GKE Cluster
resource "google_container_cluster" "primary" {
  name     = "gist-api-cluster"
  location = "asia-south1"

  # Delete default node pool immediately to use our separately managed, secure one
  remove_default_node_pool = true
  initial_node_count       = 1

  # Enable Workload Identity (Crucial for modern pod-to-GCP authentication)
  workload_identity_config {
    workload_pool = "equal-experts-demo-project.svc.id.goog"
  }
}

# 4. Managed Node Pool using the custom Service Account
resource "google_container_node_pool" "primary_nodes" {
  name       = "gist-api-node-pool"
  location   = "asia-south1"
  cluster    = google_container_cluster.primary.name
  node_count = 3 # High Availability

  node_config {
    machine_type    = "e2-standard-2"
    service_account = google_service_account.gke_node_sa.email
    oauth_scopes    = ["https://www.googleapis.com/auth/cloud-platform"]
  }
}