# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['src']

package_data = \
{'': ['*']}

install_requires = \
['fastapi[all]>=0.74.1,<0.75.0']

entry_points = \
{'console_scripts': ['start = src.main:start']}

setup_kwargs = {
    'name': 'cse546backend',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'adityakrshnn',
    'author_email': 'adityakrshnn@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
