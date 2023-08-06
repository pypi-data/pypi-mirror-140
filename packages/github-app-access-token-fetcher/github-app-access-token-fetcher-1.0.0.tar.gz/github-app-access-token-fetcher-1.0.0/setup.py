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
    'version': '1.0.0',
    'description': 'Utility script to produce a github app access token.',
    'long_description': None,
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
