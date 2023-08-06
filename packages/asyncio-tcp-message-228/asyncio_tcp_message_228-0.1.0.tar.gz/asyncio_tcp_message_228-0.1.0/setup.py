# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['asyncio_tcp_message_228']

package_data = \
{'': ['*']}

install_requires = \
['install>=1.3.5,<2.0.0', 'poetry>=1.1.13,<2.0.0']

setup_kwargs = {
    'name': 'asyncio-tcp-message-228',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'eale',
    'author_email': 'novode25@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
