variable "credentials" {
  description = "credentials"
  default     = "../.google/credentials/google_credentials.json"
}

variable "project_name" {
  description = "Project name"
  default     = "my-project-name" # Update me
}

variable "location" {
  description = "Project Location"
  default     = "US" # Update me (if needed)
}

variable "region" {
  description = "Region"
  default     = "us-central1" # Update me (if needed)
}

variable "google_bigquery_dataset_name" {
  description = "BigQuery dataset name"
  default     = "hard_drive_dataset"
}

variable "google_storage_bucket_name" {
  description = "Bucket storage name"
  default     = "my-gcs-bucket-name" # Update me
}

variable "google_storage_class" {
  description = "Bucket storage class"
  default     = "STANDARD"
}