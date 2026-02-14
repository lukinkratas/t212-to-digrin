resource "aws_iam_role" "gh_update_lambda" {
  name = "${local.project_name}-gh-update-lambda"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      "Effect" : "Allow",
      "Principal" : {
        "Federated" : "arn:aws:iam::${data.aws_caller_identity.current.account_id}:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action" : "sts:AssumeRoleWithWebIdentity",
      "Condition" : {
        "StringEquals" : {
          "token.actions.githubusercontent.com:sub" : "repo:lukinkratas/${local.project_name}:ref:refs/heads/main",
          "token.actions.githubusercontent.com:aud" : "sts.amazonaws.com"
        }
      }
    }]
  })
  tags = aws_servicecatalogappregistry_application.app.application_tag
}

resource "aws_iam_role_policy" "lambda_update" {
  name = "LambdaUpdate${local.policy_suffix}"
  role = aws_iam_role.gh_update_lambda.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = "lambda:UpdateFunctionCode"
      Resource = aws_lambda_function.lambda.arn
    }]
  })
}
