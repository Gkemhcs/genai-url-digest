resource "google_compute_network" "vpc_network" {
  name = "urldigest-network"
}

resource "google_compute_subnetwork" "subnet_us" {
  name          = "subnet-us"
  ip_cidr_range = "10.0.0.0/16"
  region        = "us-central1"
  network       = google_compute_network.vpc_network.id
}