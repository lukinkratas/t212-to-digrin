resource "aws_secretsmanager_secret" "sm" {
  name        = local.project_name
  description = "T212 API keys (all history perms)"
  tags        = aws_servicecatalogappregistry_application.app.application_tag
}
