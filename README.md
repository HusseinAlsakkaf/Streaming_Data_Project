# Streaming Data Project: Guardian API to AWS Kinesis

This project is a data engineering proof-of-concept that demonstrates a serverless ETL pipeline. It fetches articles from The Guardian's Open Platform API based on a search term, transforms the data into a clean JSON format, and publishes it to an AWS Kinesis data stream for downstream consumption.

The entire cloud infrastructure is managed via Terraform, and the application is designed to be deployed as an AWS Lambda function. With a Streamlit dashboard for real-time view of the data.

-----------------------------------------------------------------------------------------------------------------------------------

## Architecture Overview

The project follows a standard Extract, Transform, Publish (ETP) pattern:

1.  **Trigger**: The process is initiated either manually for local testing or via an event trigger on AWS Lambda.
2.  **Extractor**: A Python module connects to the Guardian API to fetch articles based on a given search query.
3.  **Transformer**: The raw API response is transformed into a clean JSON structure.
4.  **Publisher**: The formatted JSON records are published to an AWS Kinesis stream.

A Streamlit dashboard is also included to provide a simple, real-time view of the data flowing through the Kinesis stream.

---

## Getting Started: Initial Setup

This section covers the one-time setup required to run the project in any mode (local or deployed).

### Prerequisites

*   Python 3.10+
*   An AWS Account
*   Terraform installed locally
*   Guardian's API key

### 1. Clone the Repository

Clone this project to your local machine:
```bash
git clone https://github.com/HusseinAlsakkaf/Streaming_Data_Project.git
cd Streaming_Data_Project
```

### 2. Configure Credentials & Secrets

This project requires two sets of credentials. **These files should never be committed to Git.**

**A. Guardian API Key:**
1.  Obtain a free developer API key from [The Guardian Open Platform](https://open-platform.theguardian.com/access/).
2.  Create a file named `.env` in the project root and add your key:
    ```
    API_KEY="your-guardian-api-key"
    ```
3.  Create a file named `terraform/terraform.tfvars` and add the same key. This is used to securely pass the key to the Lambda function during deployment.
    ```
    guardian_api_key = "your-guardian-api-key"
    ```

**B. AWS Credentials:**
1.  Create an IAM user in your AWS account with `AdministratorAccess` permissions. This user will be used to run Terraform.
2.  Create an access key for this user.
3.  Configure your local AWS credentials by creating a file at `~/.aws/credentials` with the following content:
    ```ini
    [default]
    aws_access_key_id = YOUR_ACCESS_KEY
    aws_secret_access_key = YOUR_SECRET_KEY
    ```


### 3. Set Up the Python Environment

Create a virtual environment and install all required dependencies for development, testing, and running the application.

```bash
# Create the virtual environment
python3 -m venv venv

# Activate it (on Linux)
source venv/bin/activate

# Install all production and development libraries
pip install -r requirements-dev.txt
```

## Infrastructure Deployment (One-Time Setup)

Before running the application in any mode, you must first create the required cloud infrastructure using Terraform. This step provisions the Kinesis stream, IAM roles, and the Lambda function placeholder.

1.  **Navigate to the Terraform directory:**
    ```bash
    cd terraform
    ```
2.  **Initialize the Terraform providers:**
    ```bash
    terraform init
    ```
3.  **Apply the configuration to create the infrastructure:**
    ```bash
    terraform apply
    ```
    You will be prompted to type `yes` to confirm. After this step is complete, you are ready to use the application.


-----------------------------------------------------------------------------------------------------------------------------------

## Project Usage

This application can be run in three distinct modes: as a local script, as a deployed AWS Lambda function, or as a visual dashboard.

### Mode 1: Local Development & Testing

The `main.py` script provides a command-line interface to run the entire pipeline from your local machine. This is the fastest way to test code changes.

```bash
# Example: Run the pipeline with a search term
python3 src/main.py "\"data science\""

# Example: Run with a search term and a start date
python3 src/main.py "\"data science\"" --date-from "2022-10-01"
```

### Mode 2: Deploying and Running on AWS Lambda

To run the application in its intended serverless environment, you first build the deployment package and then use Terraform to upload the new code.

**Deployment Steps:**

1.  **Build the Deployment Package:** From the project's root directory, run the build script.
    ```bash
    bash build.sh
    ```
2.  **Deploy the New Code:** Run `terraform apply` again from the `terraform` directory. Terraform will detect the updated code package and deploy it to the existing Lambda function.
    ```bash
    cd terraform
    terraform apply
    ```

**Invoking the Deployed Function:**

1.  Navigate to the AWS Lambda Console and find the `GuardianArticlePublisher` function.
2.  Go to the "Test" tab and configure a test event:
    ```json
    {
      "search_term": "\"cloud computing\"",
      "date_from": "2023-01-01"
    }
    ```
3.  Click the "Test" button to invoke the function.

### Mode 3: Visualizing the Live Data Stream

The project includes a powerful, interactive dashboard built with Streamlit that provides a real-time view of the articles flowing through your Kinesis stream. It's the perfect way to visualize the end-to-end success of the data pipeline.

**Prerequisites:**
*   You must have published some data to the Kinesis stream using either the local `main.py` script (Mode 1) or the deployed Lambda function (Mode 2). It's best to run the pipeline with a few different search terms to see the full filtering capability.

**Launch the Dashboard:**

From the project's root directory, simply run:
```bash
streamlit run dashboard.py
```
This will automatically open the dashboard in a new browser tab.

**Dashboard Features:**

*   **Real-Time Data Consumption:** The dashboard connects directly to your AWS Kinesis stream and fetches all available article records.
*   **Interactive Filtering:** A dropdown menu is automatically populated in the sidebar with all the unique search terms found in the stream. You can instantly filter the view to show only articles from a specific search query (e.g., `"data science"`).
*   **Clean and Readable UI:** Each article is displayed in a clean, card-like format showing its headline, publication date, and a clickable URL.
*   **Content Preview:** An expandable section for each article allows you to view the first 1000 characters of the article's body, giving you a quick glimpse without leaving the dashboard.
*   **Smart Caching:** The dashboard intelligently caches the data from Kinesis for 60 seconds to provide a fast, responsive user experience while still feeling "live."


-----------------------------------------------------------------------------------------------------------------------------------

## Code Quality & Testing

This project adheres to professional development standards.

*   **Formatting:** `black src/ tests/`
*   **Security:** `bandit -r src/`
*   **Unit Tests:** `pytest`

-----------------------------------------------------------------------------------------------------------------------------------

## Infrastructure Cleanup

To remove all cloud infrastructure created by this project, run the destroy command from the `terraform` directory.

```bash
cd terraform
terraform destroy
```