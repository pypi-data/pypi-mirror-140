# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['camel_model']

package_data = \
{'': ['*']}

install_requires = \
['pydantic>=1.9.0,<2.0.0']

setup_kwargs = {
    'name': 'domain-infomoto',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'todotom',
    'author_email': 'tomasdarioam@protonmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
