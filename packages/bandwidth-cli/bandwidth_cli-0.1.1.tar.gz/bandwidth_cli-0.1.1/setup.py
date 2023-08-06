# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['bandwidth_cli', 'bandwidth_cli.commands']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.0.4,<9.0.0',
 'python-dotenv>=0.19.2,<0.20.0',
 'requests>=2.27.1,<3.0.0',
 'xmltodict>=0.12.0,<0.13.0']

entry_points = \
{'console_scripts': ['bandwidth-cli = bandwidth_cli.main:cli']}

setup_kwargs = {
    'name': 'bandwidth-cli',
    'version': '0.1.1',
    'description': 'CLI for Bandwidth API calls',
    'long_description': 'Bandwidth Subscriptions CLI Tool\n\nThis tool presents a CLI interface allowing you to manage Bandwidth webhook subscriptions with the Bandwidth API.  \n(See https://dev.bandwidth.com/docs/account/subscriptions)\n\nRequires Python 3.7+\n\nThis tool depends upon the following environment variables to be set:\n    - bandwidth_account_id=<your account_id>\n    - bandwidth_password=<your password>\n    - bandwidth_site_id=<your site id>\n    - bandwidth_url=https://dashboard.bandwidth.com/api\n    - bandwidth_username=<your username>\n\nUsage:\n\n    - pip install bandwidth_cli\n    - set env vars above\n    - bandwidth_cli --help\n',
    'author': 'Malaney J Hill',
    'author_email': 'mhill@phone.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
