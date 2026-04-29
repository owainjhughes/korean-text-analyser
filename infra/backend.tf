terraform {
  backend "s3" {
    key            = "korclass/terraform.tfstate"
    region         = "eu-west-2"
    dynamodb_table = "korclass-tfstate-lock"
    encrypt        = true
    # bucket is supplied at init time:
    #   terraform init -backend-config="bucket=<output-from-bootstrap>"
  }
}
