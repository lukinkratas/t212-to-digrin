resource "aws_s3_bucket" "bucket" {
  bucket = local.project_name
  tags   = aws_servicecatalogappregistry_application.app.application_tag
}
