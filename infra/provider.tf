terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 4.0"
    }
  }

  backend "gcs" {
    bucket  = "GCS_BUCKET_NAME"
    prefix  = "terraform/state"
  }
}

provider "google" {
  project = "${var.PROJECT_ID}"
  region  = "us-central1"
  zone    = "us-central1-a"
}
