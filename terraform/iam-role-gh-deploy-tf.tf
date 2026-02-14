resource "aws_iam_role" "gh_deploy_tf" {
  name = "${local.project_name}-gh-deplot-tf"
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

resource "aws_iam_role_policy" "s3_tf_state" {
  name = "S3TfState${local.policy_suffix}"
  role = aws_iam_role.gh_deploy_tf.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow",
        Action   = "s3:ListBucket",
        Resource = "arn:aws:s3:::terraform-state-8f45b0ac"
      },
      {
        Effect = "Allow",
        Action = [
          "s3:GetObject",
          "s3:PutObject"
        ],
        Resource = "arn:aws:s3:::terraform-state-8f45b0ac/t212-to-digrin/terraform.tfstate"
      },
      {
        Effect = "Allow",
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject"
        ],
        Resource = "arn:aws:s3:::terraform-state-8f45b0ac/t212-to-digrin/terraform.tfstate.tflock"
      }
    ]
  })
}

resource "aws_iam_role_policy" "app" {
  name = "ServiceCatalogApplication${local.policy_suffix}"
  role = aws_iam_role.gh_deploy_tf.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow",
        Action   = "servicecatalog:*",
        Resource = aws_servicecatalogappregistry_application.app.arn
      }
    ]
  })
}

resource "aws_iam_role_policy" "resource_group" {
  name = "ResourceGroup${local.policy_suffix}"
  role = aws_iam_role.gh_deploy_tf.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow",
        Action   = "resource-groups:*",
        Resource = aws_resourcegroups_group.rg.arn
      }
    ]
  })
}

resource "aws_iam_role_policy" "iam" {
  name = "IAM${local.policy_suffix}"
  role = aws_iam_role.gh_deploy_tf.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "iam:CreateUser",
          "iam:CreateRole",
          "iam:CreatePolicy",
        ],
        Resource = "*"
      },
      {
        Effect = "Allow",
        Action = "iam:*",
        Resource = [
          aws_iam_user.cli_user.arn,
          aws_iam_role.lambda.arn,
          aws_iam_role.scheduler.arn,
          aws_iam_role.gh_update_lambda.arn,
          aws_iam_role.gh_deploy_tf.arn,
          aws_iam_policy.s3_put.arn,
          aws_iam_policy.secrets_manager.arn
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy" "s3" {
  name = "S3${local.policy_suffix}"
  role = aws_iam_role.gh_deploy_tf.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow",
        Action   = "s3:*",
        Resource = aws_s3_bucket.bucket.arn
      }
    ]
  })
}

resource "aws_iam_role_policy" "secrets_manager" {
  name = "Secretsmanager${local.policy_suffix}"
  role = aws_iam_role.gh_deploy_tf.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow",
        Action   = "secretsmanager:*",
        Resource = aws_secretsmanager_secret.sm.arn
      }
    ]
  })
}

resource "aws_iam_role_policy" "lambda" {
  name = "Lambda${local.policy_suffix}"
  role = aws_iam_role.gh_deploy_tf.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow",
        Action   = "lambda:*",
        Resource = aws_lambda_function.lambda.arn
      }
    ]
  })
}

resource "aws_iam_role_policy" "scheduler" {
  name = "Scheduler${local.policy_suffix}"
  role = aws_iam_role.gh_deploy_tf.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow",
        Action   = "scheduler:*",
        Resource = aws_scheduler_schedule.scheduler.arn
      }
    ]
  })
}
