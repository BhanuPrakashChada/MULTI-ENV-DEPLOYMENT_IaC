variable "vpc_cidr_block" {
	type = string
}

variable "private_subnet_cidr_blocks" {
	type = list(string)
}
variable "public_subnet_cidr_blocks" {
	type = list(string)
}
variable "instance_type" {
	type = string
	description = "To desired instance type for AWS EC2 instance"
}
variable "eks_aws_region" {
    type = string
    description = "To set AWS availability region"  
}
variable "ami_id" {
    type    = string
    default = "ami-0fa399d9c130ec923"
}

variable "key_name" {
    type    = string
    default = "eks-keypair"
}
variable "eks_bucket_name" {
    type    = string
    default = "s3-bucket-eks-bhanuadmin"
}