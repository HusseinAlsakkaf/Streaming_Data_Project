# terraform/variables.tf
variable "guardian_api_key" {
  description = "The API key for The Guardian's Open Platform."
  type        = string
  sensitive   = true 
}