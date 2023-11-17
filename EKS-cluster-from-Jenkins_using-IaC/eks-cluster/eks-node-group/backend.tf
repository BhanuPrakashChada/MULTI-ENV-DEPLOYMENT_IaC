terraform {
  backend "s3" {
    bucket = var.eks_bucket_name
    region = var.aws_region
    tags = {
        Name = "EKS"
  }
  }
}
