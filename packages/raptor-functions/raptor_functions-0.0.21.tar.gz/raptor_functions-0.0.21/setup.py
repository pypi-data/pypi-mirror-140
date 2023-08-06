# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['raptor_functions']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'raptor-functions',
    'version': '0.0.21',
    'description': 'raptor functions',
    'long_description': None,
    'author': 'Daniel Fiuza, Ibrahim Animashaun',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Bryant-Dental/raptor_functions.git',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
