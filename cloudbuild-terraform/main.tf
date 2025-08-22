resource "google_cloudbuildv2_repository" "gdp_admin" {
  provider = google-beta
  project  = local.project_id["gdplabs"]
  location = "asia-southeast2"
  for_each = toset(local.repositories["jakarta"])


  name              = "${local.repository.owner}-${each.value}"
  parent_connection = local.repository.owner
  remote_uri        = "https://github.com/${local.repository.owner}/${local.repository.name}.git"
}