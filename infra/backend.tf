terraform {
  backend "s3" {
    bucket       = "terraform-state-8f45b0ac"
    key          = "t212-to-digrin/terraform.tfstate"
    region       = "eu-central-1"
    use_lockfile = true
    encrypt      = true
  }
}
