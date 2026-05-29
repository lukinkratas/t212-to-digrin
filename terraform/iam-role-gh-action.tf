resource "aws_iam_role" "gh_action" {
  name = "${local.project_name}-gh-action"
  path = "/${local.project_name}/"
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
  name = "s3-tf-state"
  role = aws_iam_role.gh_action.id
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
        Resource = "arn:aws:s3:::terraform-state-8f45b0ac/${local.project_name}/terraform.tfstate"
      },
      {
        Effect = "Allow",
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject"
        ],
        Resource = "arn:aws:s3:::terraform-state-8f45b0ac/${local.project_name}/terraform.tfstate.tflock"
      }
    ]
  })
}

resource "aws_iam_role_policy" "app" {
  name = "app"
  role = aws_iam_role.gh_action.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "servicecatalog:CreateApplication",
          "servicecatalog:DeleteApplication",
          "servicecatalog:GetApplication",
          "servicecatalog:UpdateApplication",
          "servicecatalog:TagResource",
          "servicecatalog:UntagResource"
        ],
        Resource = aws_servicecatalogappregistry_application.app.arn
      }
    ]
  })
}

resource "aws_iam_role_policy" "resource_group" {
  name = "resource-group"
  role = aws_iam_role.gh_action.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "resource-groups:CreateGroup",
          "resource-groups:DeleteGroup",
          "resource-groups:GetGroup",
          "resource-groups:GetGroupQuery",
          "resource-groups:UpdateGroup",
          "resource-groups:UpdateGroupQuery",
          "resource-groups:Tag",
          "resource-groups:Untag",
          "resource-groups:GetTags",
          "tag:TagResources",
          "tag:UntagResources"
        ],
        Resource = aws_resourcegroups_group.rg.arn
      }
    ]
  })
}

resource "aws_iam_role_policy" "s3" {
  name = "s3"
  role = aws_iam_role.gh_action.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "s3:CreateBucket",
          "s3:DeleteBucket",
          "s3:GetBucketAcl",
          "s3:GetBucketPolicy",
          "s3:PutBucketPolicy",
          "s3:DeleteBucketPolicy",
          "s3:GetBucketVersioning",
          "s3:PutBucketVersioning",
          "s3:GetBucketTagging",
          "s3:PutBucketTagging",
          "s3:GetBucketPublicAccessBlock",
          "s3:PutBucketPublicAccessBlock",
          "s3:GetEncryptionConfiguration",
          "s3:PutEncryptionConfiguration",
          "s3:GetLifecycleConfiguration",
          "s3:PutLifecycleConfiguration",
          "s3:ListBucket",
        ]
        Resource = aws_s3_bucket.bucket.arn
      }
    ]
  })
}

resource "aws_iam_role_policy" "secrets_manager" {
  name = "secrets-manager"
  role = aws_iam_role.gh_action.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "secretsmanager:CreateSecret",
          "secretsmanager:DeleteSecret",
          "secretsmanager:DescribeSecret",
          "secretsmanager:GetSecretValue",
          "secretsmanager:PutSecretValue",
          "secretsmanager:UpdateSecret",
          "secretsmanager:TagResource",
          "secretsmanager:UntagResource",
          "secretsmanager:GetResourcePolicy",
          "secretsmanager:PutResourcePolicy",
          "secretsmanager:DeleteResourcePolicy",
        ]
        Resource = aws_secretsmanager_secret.sm.arn
      }
    ]
  })
}

resource "aws_iam_role_policy" "lambda" {
  name = "lambda"
  role = aws_iam_role.gh_action.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "lambda:CreateFunction",
          "lambda:DeleteFunction",
          "lambda:GetFunction",
          "lambda:GetFunctionConfiguration",
          "lambda:UpdateFunctionCode",
          "lambda:UpdateFunctionConfiguration",
          "lambda:AddPermission",
          "lambda:RemovePermission",
          "lambda:GetPolicy",
          "lambda:TagResource",
          "lambda:UntagResource",
          "lambda:ListTags",
          "lambda:PutFunctionEventInvokeConfig",
          "lambda:GetFunctionEventInvokeConfig",
          "lambda:DeleteFunctionEventInvokeConfig",
        ]
        Resource = aws_lambda_function.lambda.arn
      }
    ]
  })
}

resource "aws_iam_role_policy" "scheduler" {
  name = "scheduler"
  role = aws_iam_role.gh_action.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "scheduler:CreateSchedule",
          "scheduler:DeleteSchedule",
          "scheduler:GetSchedule",
          "scheduler:UpdateSchedule",
          "scheduler:ListTagsForResource",
          "scheduler:TagResource",
          "scheduler:UntagResource",
        ]
        Resource = aws_scheduler_schedule.scheduler.arn
      }
    ]
  })
}

resource "aws_iam_role_policy" "ses" {
  name = "ses"
  role = aws_iam_role.gh_action.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = [
        "ses:VerifyEmailIdentity",
        "ses:DeleteIdentity",
        "ses:GetIdentityVerificationAttributes"
      ],
      Resource = aws_ses_email_identity.email.arn
    }]
  })
}

resource "aws_iam_role_policy" "iam_self" {
  name = "iam-self"
  role = aws_iam_role.gh_action.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow",
        Action   = "iam:CreateRole"
        Resource = "arn:aws:iam::*:role/${local.project_name}/*"
      },
      {
        Effect = "Allow"
        Action = [
          "iam:GetRole",
          "iam:GetRolePolicy",
          "iam:ListAttachedRolePolicies",
          "iam:ListRolePolicies",
        ]
        Resource = aws_iam_role.gh_action.arn
      },
      {
        Effect = "Deny"
        Action = [
          "iam:AttachRolePolicy",
          "iam:DetachRolePolicy",
          "iam:PutRolePolicy",
          "iam:DeleteRolePolicy",
          "iam:CreatePolicyVersion",
          "iam:SetDefaultPolicyVersion",
        ]
        Resource = aws_iam_role.gh_action.arn
      }
    ]
  })
}

resource "aws_iam_role_policy" "iam_cli_user" {
  name = "iam-cli-user"
  role = aws_iam_role.gh_action.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow",
        Action   = "iam:CreateUser"
        Resource = "arn:aws:iam::*:user/${local.project_name}/*"
      },
      {
        Effect = "Allow"
        Action = [
          "iam:GetUser",
          "iam:DeleteUser",
          "iam:AttachUserPolicy",
          "iam:DetachUserPolicy",
          "iam:ListAttachedUserPolicies",
          "iam:CreateAccessKey",
          "iam:DeleteAccessKey",
          "iam:ListAccessKeys",
          "iam:TagUser",
          "iam:UntagUser",
        ]
        Resource = aws_iam_user.cli.arn
      }
    ]
  })
}

resource "aws_iam_role_policy" "iam_scheduler_role" {
  name = "iam-scheduler-role"
  role = aws_iam_role.gh_action.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow",
        Action   = "iam:CreateRole"
        Resource = "arn:aws:iam::*:user/${local.project_name}/*"
      },
      {
        Effect = "Allow"
        Action = [
          "iam:GetRole",
          "iam:DeleteRole",
          "iam:UpdateRole",
          "iam:UpdateAssumeRolePolicy",
          "iam:AttachRolePolicy",
          "iam:DetachRolePolicy",
          "iam:ListAttachedRolePolicies",
          "iam:PutRolePolicy",
          "iam:GetRolePolicy",
          "iam:DeleteRolePolicy",
          "iam:ListRolePolicies",
          "iam:TagRole",
          "iam:UntagRole",
          "iam:PassRole", # needed for scheduler to pass role to EventBridge
        ]
        Resource = aws_iam_role.scheduler.arn
      }
    ]
  })
}

resource "aws_iam_role_policy" "iam_lambda_role" {
  name = "iam-lambda-role"
  role = aws_iam_role.gh_action.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow",
        Action   = "iam:CreateRole"
        Resource = "arn:aws:iam::*:user/${local.project_name}/*"
      },
      {
        Effect = "Allow"
        Action = [
          "iam:GetRole",
          "iam:DeleteRole",
          "iam:UpdateRole",
          "iam:UpdateAssumeRolePolicy",
          "iam:AttachRolePolicy",
          "iam:DetachRolePolicy",
          "iam:ListAttachedRolePolicies",
          "iam:PutRolePolicy",
          "iam:GetRolePolicy",
          "iam:DeleteRolePolicy",
          "iam:ListRolePolicies",
          "iam:TagRole",
          "iam:UntagRole",
        ]
        Resource = aws_iam_role.lambda.arn
      }
    ]
  })
}
