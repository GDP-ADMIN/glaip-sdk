resource "google_cloudbuildv2_repository" "gdp_admin" {
  provider = google-beta
  project  = local.project_id["gdplabs"]
  location = var.region

  name              = "${local.repository.owner}-${local.repository.name}"
  parent_connection = local.repository.owner
  remote_uri        = "https://github.com/${local.repository.owner}/${local.repository.name}.git"
}

resource "google_cloudbuildv2_repository" "gdp_admin_new" {
  provider = google-beta
  project  = local.project_id["gdplabs"]
  location = var.region

  name              = "${local.repository.host-asia-southeast2}-${local.repository.name}"
  parent_connection = local.repository.host-asia-southeast2
  remote_uri        = "https://github.com/${local.repository.owner}/${local.repository.name}.git"
}