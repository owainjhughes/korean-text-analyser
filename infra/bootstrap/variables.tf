variable "region" {
  description = "AWS region for the state backend (must match the main module)."
  type        = string
  default     = "eu-west-2"
}

variable "project_name" {
  description = "Short identifier used in resource names."
  type        = string
  default     = "korclass"
}
