variable "aws_region" {
  description = "AWS region for the resources"
  type        = string
  default     = "eu-central-1"
}

variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "cloud-sec-audit"
}

variable "environment" {
  description = "Deployment environment"
  type        = string
  default     = "prod"
}

variable "retention_days" {
  description = "Days to retain logs in S3"
  type        = number
  default     = 7
}
