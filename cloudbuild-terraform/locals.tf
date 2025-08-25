locals {
  repository = {
    name                 = "glaip-sdk"
    owner                = "GDP-ADMIN"
  }

  # Discover module names by listing directories in python/ that match the pattern
  python_versions      = ["3.11", "3.12", "3.13"]
  python_modules_dirs  = distinct(flatten([for _, v in fileset("${path.module}/../python", "**") : regex("([^/]*).*", dirname(v))]))
  python_modules_names = slice(local.python_modules_dirs, 1, length(local.python_modules_dirs))
  python_combined = flatten([
    for module in local.python_modules_names : [
      for version in local.python_versions : {
        module  = module
        version = version
      }
    ]
  ])
}