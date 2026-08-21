variable "aws_region" {
  description = "AWS region for infrastructure"
  type        = string
  default     = "eu-west-2"
}

variable "environment" {
  description = "Environment name (e.g., staging, production)"
  type        = string
}

variable "aws_account_id" {
  description = "AWS Account ID for globally unique names"
  type        = string
}

variable "db_username" {
  description = "PostgreSQL username"
  type        = string
  sensitive   = true
}

variable "db_password" {
  description = "PostgreSQL password"
  type        = string
  sensitive   = true
}

variable "replicate_api_token" {
  description = "Token for Replicate AI API"
  type        = string
  sensitive   = true
}

variable "cors_allowed_origins" {
  description = "List of allowed origins for CORS (e.g. S3 direct uploads)"
  type        = list(string)
  default     = ["http://localhost:3000"]
}

variable "domain_name" {
  description = "Primary domain name for Route 53"
  type        = string
  default     = "example.com"
}
