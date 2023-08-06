# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['opennews']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp', 'requests']

setup_kwargs = {
    'name': 'opennews',
    'version': '0.0.0',
    'description': 'An open source scraper to get current news.',
    'long_description': None,
    'author': 'Zeb Taylor',
    'author_email': 'zceboys@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8',
}


setup(**setup_kwargs)
