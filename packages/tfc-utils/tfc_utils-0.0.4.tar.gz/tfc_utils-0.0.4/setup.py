# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tfc_utils']

package_data = \
{'': ['*']}

install_requires = \
['terrasnek', 'typer']

setup_kwargs = {
    'name': 'tfc-utils',
    'version': '0.0.4',
    'description': 'A helper tool (CLI) for Terraform Cloud',
    'long_description': None,
    'author': 'Ilya Sotkov',
    'author_email': 'ilya@sotkov.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
