resource "aws_cloudwatch_log_group" "lambda" {
  name              = "/aws/lambda/${local.project_name}"
  retention_in_days = 90
  tags              = aws_servicecatalogappregistry_application.app.application_tag
}
