
# terraform/main.tf
# ===================================================================
# GLOBAL SETTINGS
# ===================================================================
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "eu-west-2" # London region
}

# ===================================================================
# 1. Define the Kinesis Stream
# ===================================================================
resource "aws_kinesis_stream" "guardian_stream" {
  name             = "guardian_content"
   stream_mode_details {
  stream_mode = "ON_DEMAND"
}
  retention_period = 72 # 3 days as required in the project brief
}
# ===================================================================
# 2. Define IAM Role and Policy for the Lambda Function
# ===================================================================

resource "aws_iam_policy" "lambda_policy" {
  name        = "GuardianLambdaKinesisPolicy-TF"
  description = "Allows Lambda to put records into Kinesis and write logs."

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "kinesis:PutRecords"
        ]
        Effect   = "Allow"
        # Restrict to the specific stream's ARN
        Resource = aws_kinesis_stream.guardian_stream.arn
      },
      {
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Effect   = "Allow"
        # Allow logging to any log group created by this function
        Resource = "arn:aws:logs:*:*:*"
      }
    ]
  })
}

resource "aws_iam_role" "lambda_role" {
  name = "GuardianLambdaRole-TF"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

#  attaches the policy to the role .
resource "aws_iam_role_policy_attachment" "lambda_policy_attachment" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.lambda_policy.arn
}

# ===================================================================
# 3. Define the AWS Lambda Function
# ===================================================================
resource "aws_lambda_function" "article_publisher" {
  # The name of the function in the AWS console
  function_name = "GuardianArticlePublisher"

  # The zip file created build.sh script
  filename      = "../deployment_package.zip" 
  
  # The IAM role the function will use for permissions
  role          = aws_iam_role.lambda_role.arn
  
  # The entry point for the function.
  handler       = "handler.lambda_handler"
  
  # The runtime environment
  runtime       = "python3.12"

  # So that Terraform will redeploy the function automatically if the content of the zip file changes.
  source_code_hash = filebase64sha256("../deployment_package.zip")

  #Increase the timeout if the API is slow.
  timeout = 30 #in  seconds

  # Store key  here instead of .env for Lambda which it gets form terraform.tfvars
  environment {
    variables = {
      API_KEY               = var.guardian_api_key
      KINESIS_STREAM_NAME   = aws_kinesis_stream.guardian_stream.name
 
    }
  }
}


# ===================================================================
# 4. Define the Application's IAM User ( python script)
# ===================================================================
resource "aws_iam_user" "app_user" {
  name = "guardian-project-publisher-tf" 
}

# ===================================================================
# 5. Define the IAM Policy (user)
# ===================================================================
resource "aws_iam_policy" "app_policy" {
  name        = "GuardianKinesisPutRecordsPolicy-TF"
  description = "Allows putting records into any Kinesis stream."

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "kinesis:PutRecords"
        ]
        Effect   = "Allow"
        Resource = "*"
      },
    ]
  })
}

# ===================================================================
# 6. Attach the Policy to the User
# ===================================================================
resource "aws_iam_user_policy_attachment" "app_user_attachment" {
  user       = aws_iam_user.app_user.name
  policy_arn = aws_iam_policy.app_policy.arn
}