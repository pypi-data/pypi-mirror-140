# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['jambot_client', 'jambot_client.clients', 'jambot_client.clients.bridge']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.8.1,<4.0.0',
 'fast-json>=0.3.2,<0.4.0',
 'pydantic>=1.9.0,<2.0.0',
 'yarl>=1.7.2,<2.0.0']

setup_kwargs = {
    'name': 'jambot-client',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Vladislav Bakaev',
    'author_email': 'vlad@bakaev.tech',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
