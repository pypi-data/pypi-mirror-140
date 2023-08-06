# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['odincontrib_aws', 'odincontrib_aws.dynamodb', 'tests', 'tests.test_dynamodb']

package_data = \
{'': ['*']}

install_requires = \
['boto3>=1,<2', 'odin>=1,<2', 'six']

setup_kwargs = {
    'name': 'odincontrib.aws',
    'version': '0.4.1',
    'description': 'Odin integration with AWS',
    'long_description': '##################\nOdin Contrib - AWS\n##################\n\nOdin integration with various AWS Services.\n\n- Dynamo DB\n\n  - Fields etc for working with DynamoDB documents.\n\n.. image:: https://travis-ci.org/python-odin/odincontrib.aws.svg?branch=master\n    :target: https://travis-ci.org/python-odin/odincontrib.aws\n',
    'author': 'Tim Savage',
    'author_email': 'tim@savage.company',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/python-odin/odin.contrib-dynamodb',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<3.10',
}


setup(**setup_kwargs)
