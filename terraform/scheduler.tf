resource "aws_scheduler_schedule" "scheduler" {
  name                         = local.project_name
  description                  = "Run at 14:01 on the 1st day of every month"
  schedule_expression          = "cron(1 14 1 * ? *)"
  schedule_expression_timezone = "Europe/Prague"
  flexible_time_window { mode = "OFF" }
  target {
    arn      = aws_lambda_function.lambda.arn
    role_arn = aws_iam_role.scheduler.arn
  }
}
