resource "aws_ssm_parameter" "api_key" {
  name        = local.api_key_param
  description = "KRDict API key consumed by the app at runtime. Real value set out-of-band via aws ssm put-parameter --overwrite."
  type        = "SecureString"
  value       = "PLACEHOLDER_SET_VIA_AWS_CLI"

  lifecycle {
    ignore_changes = [value]
  }
}
