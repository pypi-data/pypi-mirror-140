# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['make_env']

package_data = \
{'': ['*']}

install_requires = \
['python-dotenv>=0.19.2,<0.20.0']

entry_points = \
{'console_scripts': ['make.env = make_env:main']}

setup_kwargs = {
    'name': 'make.env',
    'version': '0.0.1',
    'description': 'wraps make command with the ability to load .env files',
    'long_description': None,
    'author': 'smac89',
    'author_email': 'nobleman.code@gmx.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/smac89/make.env',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
