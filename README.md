# Python Boto3 Demo CLI

A demonstration of using the Boto3 library to interact with Amazon Web Services (AWS) from Python.
Overview

------------
This repository provides the use of Boto3 to perform the following tasks on AWS:

- Check if the s3 buckets have public access and remove it to avoid undesired access.
- Check if the RDS Instances have public access and remove it to avoid undesired access
- Check if the EC2 account instances have assigned the SSM policy on their roles and remove that policy from all instances

## Requirements

- Python 3.10+
- Boto3 library (`pip install boto3`)
- Typer library (`pip install typer`)
- Pytest library (`pip install pytest`)
- Moto library (`pip install moto`)
- AWS account with necessary credentials and permissions

## Usage

1. Clone the repository: git clone https://github.com/whoisbryan/python_boto3_demo.git
2. Install the required libraries: `pip install -r requirements.txt`
3. Configure your AWS credentials (e.g., using the ~/.aws/credentials file)
4. Run the script using Python (e.g., `python_boto3_demo/app.py`)
