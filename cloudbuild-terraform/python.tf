module "gcb_ai_agent_platform_pr_python_sdk" {
  source     = "s3::https://s3.amazonaws.com/gl-terraform-modules/terraform-gcp-gcb/terraform-gcp-gcb-1.0.2.zip"
  location   = var.region
  project_id = local.project_id.gdplabs
  for_each   = { for idx, val in local.python_combined : "${val.module}-${val.version}" => val }

  name        = lower(replace("${local.repository["name"]}-pr-${each.value.module}-python${each.value.version}", ".", "-"))
  description = "AI Agent Platform SDK"
  owner       = local.repository["owner"]
  repo_name   = local.repository["name"]
  substitutions = {
    "_MODULE"   = each.value.module
    "_VERSION"  = each.value.version
    "_LANGUAGE" = "python"
  }
  filename       = "cloudbuild-pr.yml"
  included_files = ["python/${each.value.module}/**"]
  trigger_config = {
    trigger_type    = "PR"
    branch_regex    = ".*"
    tag_regex       = null
    comment_control = "COMMENTS_ENABLED_FOR_EXTERNAL_CONTRIBUTORS_ONLY"
  }
}

module "gcb_ai_agent_platform_push_tag_python_sdk" {
  source     = "s3::https://s3.amazonaws.com/gl-terraform-modules/terraform-gcp-gcb/terraform-gcp-gcb-1.0.2.zip"
  location   = var.region
  project_id = local.project_id.gdplabs
  for_each   = { for idx, val in local.python_combined : "${val.module}-${val.version}" => val }

  name        = lower(replace("${local.repository["name"]}-push-tag-${each.value.module}-python${each.value.version}", ".", "-"))
  description = "AI Agent Plaform SDK"
  owner       = local.repository["owner"]
  repo_name   = local.repository["name"]
  substitutions = {
    "_MODULE"   = each.value.module
    "_VERSION"  = each.value.version
    "_LANGUAGE" = "python"
  }
  filename = "cloudbuild.yml"
  trigger_config = {
    trigger_type    = "PUSH"
    branch_regex    = null
    tag_regex       = "python_${replace(each.value.module, "-", "_")}-v*"
    comment_control = null
  }
}
