# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['hyperstate', 'hyperstate.schema']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.0.3,<9.0.0',
 'dill>=0.3.4,<0.4.0',
 'msgpack-numpy>=0.4.7,<0.5.0',
 'msgpack>=1.0.3,<2.0.0',
 'python-ron>=0.1.6,<0.2.0']

setup_kwargs = {
    'name': 'hyperstate',
    'version': '0.2.5',
    'description': 'Library for managing hyperparameters and mutable state of machine learning training systems.',
    'long_description': None,
    'author': 'Clemens Winter',
    'author_email': 'clemenswinter1@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
