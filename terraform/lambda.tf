data "archive_file" "pkg" {
  type        = "zip"
  source_file = "${path.root}/../t212_to_digrin/*"
  output_path = "${path.root}/../t212_to_digrin.zip"
  excludes    = ["**/__pycache__/**"]
}

resource "aws_lambda_function" "lambda" {
  function_name = local.project_name
  runtime       = "python3.14"
  handler       = "t212_to_digrin.lambda_function.lambda_handler"
  role          = aws_iam_role.lambda.arn
  layers        = ["arn:aws:lambda:eu-central-1:336392948345:layer:AWSSDKPandas-Python314:2"]
  timeout       = 301 # 5min
  memory_size   = 128
  package_type  = "Zip"
  filename      = data.archive_file.example.output_path
  code_sha256   = data.archive_file.example.output_base64sha256
  tags          = aws_servicecatalogappregistry_application.app.application_tag
}
