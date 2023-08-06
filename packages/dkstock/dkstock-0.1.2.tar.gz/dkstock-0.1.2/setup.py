# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dkstock', 'dkstock.stock']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'dkstock',
    'version': '0.1.2',
    'description': 'python package',
    'long_description': None,
    'author': 'czl8769',
    'author_email': 'dkkevincheng@outlook.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
