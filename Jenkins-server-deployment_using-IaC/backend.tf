terraform {
  backend "s3" {
    bucket = var.bucket-name
    region = var.aws_region
    tags = {
        Name = "Jenkins-Server"
  }
  }
}
