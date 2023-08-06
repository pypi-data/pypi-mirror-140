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
    'version': '0.0.6',
    'description': 'Infuses GNU make with the ability to read .env files',
    'long_description': "# make.env\n[![GitHub Workflow Status (event)](https://img.shields.io/github/workflow/status/smac89/make.env/Python%20application?event=push&label=tests&style=for-the-badge)](https://github.com/smac89/make.env/actions/workflows/python-app.yml)\n[![PyPI](https://img.shields.io/pypi/v/make.env?style=for-the-badge)](https://pypi.org/project/make.env/)\n[![GitHub](https://img.shields.io/github/license/smac89/make.env?style=for-the-badge)](https://github.com/smac89/make.env/blob/main/LICENSE)\n[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/make.env?style=for-the-badge)](https://pypi.org/project/make.env/)\n\nInfuses [GNU make](https://www.gnu.org/software/make/) with the ability to read .env files\n\n## Motivation\nOften when working with Makefiles, you might have the need to read environment variables from a `.env` file, and have `make` treat them as if the environment variables were actually variables in the Makefile.\n\nThe most [popular](https://unix.stackexchange.com/a/348432/44793) solution is to import the `.env` file into the Makefile, and then export every varaible declared so far:\n\n```makefile\ninclude .env\nexport\n```\n\nThe problem with this is that it is prone to errors. For example, if your `.env` file contains the following:\n\n```sh\nAPP_PASSWORD='8oyy!r#vNpRy2TT'\n```\n\nThe variable `APP_PASSWORD` will be exported with the value `'8oyy!r`. Likewise, if your `.env` file contains the following:\n\n```sh\nAPP_PASSWORD='Qy%$%J9$rD#jqVw'\n```\n\nThe variable `APP_PASSWORD` will be exported with the value `'Qy%J9D`.\n\nWhat's more, any attempt to use this variable will result in an error in `make` concerning the lack of a closing quote:\n\n> unexpected EOF while looking for matching `''\n\n### Explanaition\n\nIn both cases, `APP_PASSWORD` contained values which `make` treats specially.\n\n_The `#` is used to start comments, therefore as soon as make sees a `#`, it will ignore the rest of the line._\n\n_The `$` is used to reference a variable or function, so when make sees a `$`, it will treat whatever comes after it as a variable or function reference._\n\n## The solution\nThat's where this wrapper comes in. *It allows us to read a `.env` file and pass them to `make`* in a way that allows `make` to treat them as variables and copy their values literally rather than attempting to interpret them.\n",
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
