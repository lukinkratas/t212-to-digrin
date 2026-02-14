resource "aws_iam_user" "cli_user" {
  name = "${local.project_name}-cli"
  tags = aws_servicecatalogappregistry_application.app.application_tag
}

resource "aws_iam_user_policy" "s3_get" {
  name = "S3Read${local.policy_suffix}"
  user = aws_iam_user.cli_user.name
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = "s3:GetObject"
        Resource = "${aws_s3_bucket.bucket.arn}/*"
      }
    ]
  })
}

resource "aws_iam_user_policy_attachment" "cli_user_s3_put" {
  user       = aws_iam_user.cli_user.name
  policy_arn = aws_iam_policy.s3_put.arn
}

resource "aws_iam_user_policy_attachment" "cli_user_secrets_manager" {
  user       = aws_iam_user.cli_user.name
  policy_arn = aws_iam_policy.secrets_manager.arn
}
