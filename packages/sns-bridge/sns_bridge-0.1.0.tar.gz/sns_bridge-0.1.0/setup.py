# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['sns_bridge']

package_data = \
{'': ['*']}

install_requires = \
['boto3>=1.21.8,<2.0.0',
 'bottle>=0.12.19,<0.13.0',
 'pyngrok>=5.1.0,<6.0.0',
 'requests>=2.27.1,<3.0.0']

entry_points = \
{'console_scripts': ['sns_bridge = sns_bridge.main:main']}

setup_kwargs = {
    'name': 'sns-bridge',
    'version': '0.1.0',
    'description': 'Run an AWS Chalice SNS listener locally',
    'long_description': None,
    'author': 'Jake Wood',
    'author_email': 'jake@testbox.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
