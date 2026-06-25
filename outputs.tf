output "s3_bucket_name" {
  description = "The name of the centralized logging bucket"
  value       = aws_s3_bucket.audit_logs.id
}

output "cloudtrail_arn" {
  description = "The ARN of the CloudTrail"
  value       = aws_cloudtrail.main.arn
}

output "config_recorder_id" {
  description = "The ID of the AWS Config recorder"
  value       = aws_config_configuration_recorder.main.id
}

output "athena_database_name" {
  description = "The name of the Athena database"
  value       = aws_athena_database.security_analytics.name
}

output "athena_workgroup_name" {
  description = "The name of the Athena workgroup"
  value       = aws_athena_workgroup.analytics.name
}
