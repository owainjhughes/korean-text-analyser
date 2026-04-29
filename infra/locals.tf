data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

locals {
  account_id    = data.aws_caller_identity.current.account_id
  region        = data.aws_region.current.name
  admin_email   = var.admin_email != "" ? var.admin_email : "admin@${var.domain}"
  ecr_url       = "${local.account_id}.dkr.ecr.${local.region}.amazonaws.com/${var.project_name}"
  api_key_param = "/${var.project_name}/API_KEY"
  log_group     = "/${var.project_name}/app"
}
