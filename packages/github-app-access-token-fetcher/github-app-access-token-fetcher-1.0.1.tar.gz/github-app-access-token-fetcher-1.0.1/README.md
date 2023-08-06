# GitHub App Access Token Fetcher

Utility to get access tokens for a GitHub App. 

## Prerequisites
* The GitHub App must be created **and installed**.
* A private key must be generated (from the GitHub App settings UI) and its content should be written as binary data to
  an AWS Secretsmanager secret.


To set up the private key, do something like this (assuming the secret is created already):
```python
import boto3
secret_arn = "arn:aws:secretsmanager:us-east-1:1234:secret:my-secret-name"
pem_file = "/path/to/private_key.pem"
client = boto3.client('secretsmanager', region_name=secret_arn.split(':')[3])
with open(pem_file, 'rb') as f:
    client.put_secret_value(SecretId=secret_arn, SecretBinary=f.read())
```


## Install

```bash
pip install github-app-access-token-fetcher
```


## Usage

```
get-github-app-token --help

usage: get-github-app-token [-h] --app-id APP_ID --private-key-secret-arn PRIVATE_KEY_SECRET_ARN

Get a GitHub App token

optional arguments:
  -h, --help            show this help message and exit
  --app-id APP_ID       GitHub App ID
  --private-key-secret-arn PRIVATE_KEY_SECRET_ARN
                        ARN of the secret containing the GitHub App private key
```

Example:

```bash
export AWS_PROFILE=...  # Something with access to the private key secret.
get-github-app-token \
    --app-id 1234 \
    --private-key-secret-arn arn:aws:secretsmanager:us-west-1:4321:secret:abc-1234
```
