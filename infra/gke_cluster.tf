resource "google_container_cluster" "cluster_us" {
  name               = "cluster-us"
  location           = "us-central1-a" 
  initial_node_count = 1


  node_config {
    machine_type = "e2-standard-4"
    disk_size_gb = 100
    disk_type    = "pd-standard"
    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]
  }

  network    = google_compute_network.vpc_network.self_link
  subnetwork = google_compute_subnetwork.subnet_us.name

  workload_identity_config {
  workload_pool = "${var.PROJECT_ID}.svc.id.goog"
}
  addons_config {
    http_load_balancing {
      disabled = false
    }

    horizontal_pod_autoscaling {
      disabled = false
    }

    network_policy_config {
      disabled = true
    }


  }

}