output "elastic_ip" {
  description = "Public IPv4 address. Point your DNS A record(s) for the configured domain at this."
  value       = aws_eip.app.public_ip
}

output "ecr_url" {
  description = "ECR repository URI (for docker push)."
  value       = aws_ecr_repository.app.repository_url
}

output "oidc_role_arn" {
  description = "Role ARN for GitHub Actions to assume. Add as repo variable AWS_DEPLOY_ROLE_ARN."
  value       = aws_iam_role.github_actions.arn
}

output "instance_id" {
  description = "EC2 instance ID. Add as repo variable EC2_INSTANCE_ID."
  value       = aws_instance.app.id
}

output "ssm_param_name" {
  description = "SSM Parameter Store key holding the API_KEY (set the value via aws ssm put-parameter --overwrite)."
  value       = aws_ssm_parameter.api_key.name
}

output "log_group_name" {
  value       = aws_cloudwatch_log_group.app.name
  description = "CloudWatch log group with container stdout/stderr."
}
