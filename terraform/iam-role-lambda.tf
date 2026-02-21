resource "aws_iam_role" "lambda" {
  name = "${local.project_name}-lambda"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })
  tags = aws_servicecatalogappregistry_application.app.application_tag
}

resource "aws_iam_role_policy_attachment" "lambda_exec" {
  role       = aws_iam_role.lambda.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "lambda_secrets_manager" {
  role       = aws_iam_role.lambda.name
  policy_arn = aws_iam_policy.secrets_manager.arn
}

resource "aws_iam_role_policy_attachment" "lambda_s3_put" {
  role       = aws_iam_role.lambda.name
  policy_arn = aws_iam_policy.s3_put.arn
}

resource "aws_iam_role_policy" "s3_get" {
  name = "S3Read${local.policy_suffix}"
  role = aws_iam_user.lambda.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = "s3:GetObject"
      Resource = "${aws_s3_bucket.bucket.arn}/*"
    }]
  })
}

resource "aws_iam_role_policy" "ses_send_mail" {
  name = "SesSendMail${local.policy_suffix}"
  role = aws_iam_role.lambda.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = "ses:SendEmail"
      Resource = aws_ses_email_identity.email.arn
    }]
  })
}
