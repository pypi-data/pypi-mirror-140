import time
from argparse import ArgumentParser

import boto3
import jwt
import requests
from cryptography.hazmat.backends import default_backend


def main():
    parser = ArgumentParser(description="Get a GitHub App token")
    parser.add_argument("--app-id", required=True, help="GitHub App ID")
    parser.add_argument(
        "--private-key-secret-arn",
        required=True,
        help="ARN of the secret containing the GitHub App private key",
    )
    args = parser.parse_args()

    client = boto3.client(
        "secretsmanager", region_name=args.private_key_secret_arn.split(":")[3]
    )
    private_key = default_backend().load_pem_private_key(
        client.get_secret_value(SecretId=args.private_key_secret_arn)["SecretBinary"],
        None,
    )

    def app_headers():
        time_since_epoch_in_seconds = int(time.time())
        payload = {
            "iat": time_since_epoch_in_seconds,
            "exp": time_since_epoch_in_seconds + (10 * 60),
            "iss": args.app_id,
        }
        actual_jwt = jwt.encode(payload, private_key, algorithm="RS256")

        headers = {
            "Authorization": "Bearer {}".format(actual_jwt),
            "Accept": "application/vnd.github.machine-man-preview+json",
        }
        return headers

    resp = requests.get(
        "https://api.github.com/app/installations", headers=app_headers()
    )
    assert resp.ok
    resp = resp.json()
    assert len(resp) == 1, "Unexpected number of installations, only one expected"

    resp = requests.post(resp[0]["access_tokens_url"], headers=app_headers())
    assert resp.ok
    print(resp.json()["token"])
