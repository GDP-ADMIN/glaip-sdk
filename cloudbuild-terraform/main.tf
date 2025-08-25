resource "google_cloudbuildv2_repository" "gdp_admin" {
  provider = google-beta
  project  = local.project_id["gdplabs"]
  location = var.region

  name              = "${local.repository.owner}-${local.repository.name}"
  parent_connection = local.repository.owner
  remote_uri        = "https://github.com/${local.repository.owner}/${local.repository.name}.git"
}