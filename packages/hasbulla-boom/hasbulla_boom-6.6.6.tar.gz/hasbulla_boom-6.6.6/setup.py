# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['hasbulla_boom']

package_data = \
{'': ['*']}

install_requires = \
['aiomisc>=15.6.8,<16.0.0',
 'asyncio>=3.4.3,<4.0.0',
 'pytest-asyncio>=0.18.1,<0.19.0',
 'pytest-cov>=3.0.0,<4.0.0',
 'pytest>=7.0.1,<8.0.0']

setup_kwargs = {
    'name': 'hasbulla-boom',
    'version': '6.6.6',
    'description': '',
    'long_description': None,
    'author': 'Your Name',
    'author_email': 'you@example.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
