resource "google_service_account" "trace_agent" {
  account_id   = "trace-agent"
  display_name = "Trace Agent"
}

resource "google_project_iam_member" "trace_agent_role" {
  role   = "roles/cloudtrace.agent"
  project = var.PROJECT_ID
  member = "serviceAccount:${google_service_account.trace_agent.email}"
}

resource "google_service_account" "ai_platform_user" {
  account_id   = "ai-platform-user"
  display_name = "AI Platform User"

}

resource "google_project_iam_member" "ai_platform_user_role" {
  project=var.PROJECT_ID
  role   = "roles/aiplatform.user"
  member = "serviceAccount:${google_service_account.ai_platform_user.email}"

}

resource "google_service_account" "vm_service_account" {
  account_id   = "vm-service-account"
  display_name = "VM Service Account"
}