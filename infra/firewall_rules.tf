resource "google_compute_firewall" "allow_ssh" {
  name    = "allow-ssh"
  network = google_compute_network.vpc_network.id

  allow {
    protocol = "tcp"
    ports    = ["22"]
  }
   source_ranges = ["0.0.0.0"]

  target_tags = ["allow-ssh"]
}

resource "google_compute_firewall" "allow_http" {
  name    = "allow-8080"
  network = google_compute_network.vpc_network.id

  allow {
    protocol = "tcp"
    ports    = ["8080"]
  }
  source_ranges =[ "0.0.0.0"]
  target_tags = ["allow-8080"]
}