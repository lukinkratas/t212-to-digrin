resource "aws_lambda_function" "lambda" {
  function_name = local.project_name
  runtime       = "python3.14"
  handler       = "t212_to_digrin.lambda_function.lambda_handler"
  role          = aws_iam_role.lambda.arn
  # layers           = ["arn:aws:lambda:eu-central-1:336392948345:layer:AWSSDKPandas-Python314:1"]
  timeout          = 301 # 5min
  memory_size      = 128
  filename         = "../lambda.zip"
  source_code_hash = filesha256("../lambda.zip")
  tags             = aws_servicecatalogappregistry_application.app.application_tag
}
