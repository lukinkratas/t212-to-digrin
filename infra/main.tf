terraform {
  required_version = ">= 1.10" # use_lockfile needs 1.10+
  required_providers {
    aws = { source = "hashicorp/aws", version = "~> 6.31" }
  }
  backend "s3" {
    bucket       = "terraform-state-8f45b0ac"
    key          = "t212-to-digrin/terraform.tfstate"
    region       = "eu-central-1"
    use_lockfile = true
    encrypt      = true
  }
}

locals { project_name = "t212-to-digrin" }

provider "aws" {
  region = "eu-central-1"
  default_tags {
    tags = { Project = local.project_name }
  }
}

resource "aws_iam_user" "cli" {
  name = "${local.project_name}-cli"
  path = "/${local.project_name}/"
}

resource "aws_iam_user_policy" "cli_s3_put" {
  name = "s3-put"
  user = aws_iam_user.cli.name

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
}

resource "aws_s3_bucket" "bucket" {
  bucket = local.project_name
}

resource "aws_resourcegroups_group" "rg" {
  name = local.project_name
  resource_query {
    type = "TAG_FILTERS_1_0"
    query = jsonencode({
      ResourceTypeFilters = ["AWS::AllSupported"]
      TagFilters          = [{ Key = "Project", Values = [local.project_name] }]
    })
  }
}
