# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['happy_bank_core',
 'happy_bank_core.cli',
 'happy_bank_core.config',
 'happy_bank_core.data',
 'happy_bank_core.logic']

package_data = \
{'': ['*']}

install_requires = \
['Flask>=2.0,<3.0', 'click>=8.0,<9.0', 'toml>=0.10.1,<0.11.0']

entry_points = \
{'console_scripts': ['happy-bank-core = happy_bank_core.app:main']}

setup_kwargs = {
    'name': 'happy-bank-core',
    'version': '0.5.0',
    'description': 'A simple bank core app for mentoring purpose',
    'long_description': None,
    'author': 'JanMate',
    'author_email': 'JanMate@github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9',
}


setup(**setup_kwargs)
