resource "aws_s3_bucket" "athena_results" {
  bucket        = "${local.name_prefix}-athena-results-${random_string.suffix.result}"
  force_destroy = true
  tags          = local.common_tags
}

resource "aws_s3_bucket_lifecycle_configuration" "athena_results_lifecycle" {
  bucket = aws_s3_bucket.athena_results.id

  rule {
    id     = "auto-delete-after-retention"
    status = "Enabled"
    
    filter {}

    expiration {
      days = var.retention_days
    }
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "athena_results_encryption" {
  bucket = aws_s3_bucket.athena_results.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "athena_results_pab" {
  bucket                  = aws_s3_bucket.athena_results.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_athena_workgroup" "analytics" {
  name = "${local.name_prefix}-workgroup"

  configuration {
    result_configuration {
      output_location = "s3://${aws_s3_bucket.athena_results.bucket}/output/"
      encryption_configuration {
        encryption_option = "SSE_S3"
      }
    }
  }
  force_destroy = true
  tags          = local.common_tags
}

resource "aws_athena_database" "security_analytics" {
  name          = "security_analytics_${replace(random_string.suffix.result, "-", "_")}"
  bucket        = aws_s3_bucket.athena_results.id
  force_destroy = true
}
