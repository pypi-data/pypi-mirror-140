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
    'version': '0.0.3',
    'description': 'Infuses make with the ability to read .env files',
    'long_description': '# make.env\n![PyPI](https://img.shields.io/pypi/v/make.env?style=for-the-badge)\n![GitHub](https://img.shields.io/github/license/smac89/make.env?style=for-the-badge)\n![PyPI - Python Version](https://img.shields.io/pypi/pyversions/make.env?style=for-the-badge)\n\nInfuses [GNU make](https://www.gnu.org/software/make/) with the ability to read .env files\n',
    'author': 'smac89',
    'author_email': 'nobleman.code@gmx.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/smac89/make.env',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
