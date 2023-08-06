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
    'version': '0.0.5',
    'description': 'Infuses GNU make with the ability to read .env files',
    'long_description': '# make.env\n[![GitHub Workflow Status (event)](https://img.shields.io/github/workflow/status/smac89/make.env/Python%20application?event=push&label=tests&style=for-the-badge)](https://github.com/smac89/make.env/actions/workflows/python-app.yml)\n[![PyPI](https://img.shields.io/pypi/v/make.env?style=for-the-badge)](https://pypi.org/project/make.env/)\n[![GitHub](https://img.shields.io/github/license/smac89/make.env?style=for-the-badge)](https://github.com/smac89/make.env/blob/main/LICENSE)\n[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/make.env?style=for-the-badge)](https://pypi.org/project/make.env/)\n\nInfuses [GNU make](https://www.gnu.org/software/make/) with the ability to read .env files\n',
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
