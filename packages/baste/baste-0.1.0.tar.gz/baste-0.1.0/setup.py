# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['baste']

package_data = \
{'': ['*']}

install_requires = \
['blessings==1.7', 'fabric==2.6.0', 'patchwork==1.0.1']

setup_kwargs = {
    'name': 'baste',
    'version': '0.1.0',
    'description': 'A simple wrapper around fabric for multi-repo projects',
    'long_description': None,
    'author': 'Lakin Wecker',
    'author_email': 'lakin@structuredabstraction.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
