resource "aws_cloudwatch_log_group" "app" {
  name              = local.log_group
  retention_in_days = 7
}
