# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['github_app_access_token_fetcher']

package_data = \
{'': ['*']}

install_requires = \
['PyJWT>=2.3.0,<3.0.0',
 'boto3>=1.21.8,<2.0.0',
 'cryptography>=36.0.1,<37.0.0',
 'requests>=2.27.1,<3.0.0']

entry_points = \
{'console_scripts': ['get-github-app-token = '
                     'github_app_access_token_fetcher:main']}

setup_kwargs = {
    'name': 'github-app-access-token-fetcher',
    'version': '1.0.1',
    'description': 'Utility script to produce a github app access token.',
    'long_description': '# GitHub App Access Token Fetcher\n\nUtility to get access tokens for a GitHub App. \n\n## Prerequisites\n* The GitHub App must be created **and installed**.\n* A private key must be generated (from the GitHub App settings UI) and its content should be written as binary data to\n  an AWS Secretsmanager secret.\n\n\nTo set up the private key, do something like this (assuming the secret is created already):\n```python\nimport boto3\nsecret_arn = "arn:aws:secretsmanager:us-east-1:1234:secret:my-secret-name"\npem_file = "/path/to/private_key.pem"\nclient = boto3.client(\'secretsmanager\', region_name=secret_arn.split(\':\')[3])\nwith open(pem_file, \'rb\') as f:\n    client.put_secret_value(SecretId=secret_arn, SecretBinary=f.read())\n```\n\n\n## Install\n\n```bash\npip install github-app-access-token-fetcher\n```\n\n\n## Usage\n\n```\nget-github-app-token --help\n\nusage: get-github-app-token [-h] --app-id APP_ID --private-key-secret-arn PRIVATE_KEY_SECRET_ARN\n\nGet a GitHub App token\n\noptional arguments:\n  -h, --help            show this help message and exit\n  --app-id APP_ID       GitHub App ID\n  --private-key-secret-arn PRIVATE_KEY_SECRET_ARN\n                        ARN of the secret containing the GitHub App private key\n```\n\nExample:\n\n```bash\nexport AWS_PROFILE=...  # Something with access to the private key secret.\nget-github-app-token \\\n    --app-id 1234 \\\n    --private-key-secret-arn arn:aws:secretsmanager:us-west-1:4321:secret:abc-1234\n```\n',
    'author': 'Bendik Samseth',
    'author_email': 'bendik.samseth@inspera.no',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
