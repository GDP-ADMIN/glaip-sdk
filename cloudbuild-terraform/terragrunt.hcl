remote_state {
  backend = "gcs" 
  generate = {
    path      = "main_backend.tf"
    if_exists = "overwrite_terragrunt"
  }

  config = {
    project     = "gdp-labs"
    bucket      = "gl-terraform-state"
    prefix      = "terragrunt/glaip-sdk/${path_relative_to_include()}"
    credentials = "key/tf-key.json"
  }

  disable_init = tobool(get_env("TERRAGRUNT_DISABLE_INIT", false))
}

generate "variables" {
  path      = "main_variables.tf"
  if_exists = "overwrite_terragrunt"
  contents = <<EOF
    variable "path_cred" {
      description = "Path to Service Account Credential .json"
      type        = string
      default     = "key/tf-key.json"
    }

    variable "project_id" {
      description = "Default Project ID"
      type        = string
      default     = "gdp-labs"
    }

    variable "region" {
      description = "Default region to put resources"
      type        = string
      default     = "asia-southeast2"
    }
  EOF
}

generate "provider" {
  path      = "main_provider.tf"
  if_exists = "overwrite_terragrunt"
  contents = <<EOF
    terraform {
      required_providers {
        google = {
          version = "~> 6.24.0"
        }

        google-beta = {
          version = "~> 6.24.0"
        }
      }

      required_version = ">= 1.9.4"
    }

    provider "google" {
      credentials = file(var.path_cred)
      project     = var.project_id
      region      = var.region
    }

    provider "google-beta" {
      credentials = file(var.path_cred)
      project     = var.project_id
      region      = var.region
    }
  EOF
}

generate "locals" {
  path      = "main_locals.tf"
  if_exists = "overwrite_terragrunt"
  contents = <<EOF
    locals {
      project_id = {
        gdplabs  = "gdp-labs"
      }
    }
  EOF
}