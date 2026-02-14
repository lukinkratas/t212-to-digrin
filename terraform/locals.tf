locals {
  project_name  = "t212-to-digrin"
  policy_suffix = join("", [for part in split("-", local.project_name) : title(part)])
}
