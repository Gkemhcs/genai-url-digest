resource "google_compute_instance" "vm_instance" {
  name         = "jenkins-master"
  machine_type = "e2-standard-4"
  zone         = "us-central1-a"
  tags         = ["allow-ssh", "allow-8080"]

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-10"
    }
  }

  network_interface {
    network    = google_compute_network.vpc_network.id
    subnetwork = google_compute_subnetwork.subnet_us.id
    access_config {
    }
  }

  service_account {
    email  = google_service_account.vm_service_account.email
    scopes = ["cloud-platform"]
  }
   metadata = {
    ssh-keys = "${var.SSH_USERNAME}:${file(var.SSH_PUBLIC_KEY_FILE)}"
  }

  labels = {
    environment = "dev"
    ansible     = "master"
  }
}
