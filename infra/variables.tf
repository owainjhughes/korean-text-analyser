variable "region" {
  description = "AWS region."
  type        = string
  default     = "eu-west-2"
}

variable "project_name" {
  description = "Short identifier baked into resource names and the Project tag."
  type        = string
  default     = "korclass"
}

variable "domain" {
  description = "Apex hostname Caddy serves and requests a Let's Encrypt cert for."
  type        = string
  default     = "saebae.com"
}

variable "github_repo" {
  description = "GitHub repository allowed to assume the deploy role via OIDC. Format: owner/repo."
  type        = string
  default     = "owainjhughes/korean-text-analyser"
}

variable "instance_type" {
  description = "EC2 instance type."
  type        = string
  default     = "t3.micro"
}

variable "admin_email" {
  description = "Contact email for Let's Encrypt cert expiry notifications. Defaults to admin@<domain>."
  type        = string
  default     = ""
}
