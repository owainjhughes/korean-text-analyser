output "bucket_name" {
  description = "S3 bucket holding the main Terraform state. Copy this into ../backend.tf."
  value       = aws_s3_bucket.state.id
}

output "dynamodb_table_name" {
  description = "DynamoDB table used for state locking. Copy this into ../backend.tf."
  value       = aws_dynamodb_table.lock.name
}

output "region" {
  value = var.region
}
