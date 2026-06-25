data "aws_caller_identity" "current" {}
data "aws_region" "current" {}
data "aws_partition" "current" {}

resource "random_string" "suffix" {
  length  = 6
  special = false
  upper   = false
}
