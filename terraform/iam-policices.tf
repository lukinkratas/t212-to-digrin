resource "aws_iam_policy" "s3_put" {
  name        = "S3Write${local.policy_suffix}"
  description = "PutObject to S3 bucket t212-to-digrin"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = "s3:PutObject"
        Resource = "${aws_s3_bucket.bucket.arn}/*"
      }
    ]
  })
  tags = aws_servicecatalogappregistry_application.app.application_tag
}

resource "aws_iam_policy" "secrets_manager" {
  name        = "SecretsManager${local.policy_suffix}"
  description = "GetSecretValue from Secrets Manager secret t212-to-digrin"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = "secretsmanager:GetSecretValue"
        Resource = "${aws_secretsmanager_secret.sm.arn}"
      }
    ]
  })
  tags = aws_servicecatalogappregistry_application.app.application_tag
}

