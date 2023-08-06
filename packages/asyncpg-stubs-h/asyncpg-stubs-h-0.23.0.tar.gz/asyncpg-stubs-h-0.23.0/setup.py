# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['asyncpg-stubs']

package_data = \
{'': ['*'],
 'asyncpg-stubs': ['_testbase/*',
                   'exceptions/*',
                   'pgproto/*',
                   'protocol/*',
                   'protocol/codecs/*']}

install_requires = \
['asyncpg>=0.23.0,<0.24.0', 'mypy>=0.800', 'typing-extensions>=3.10.0,<4.0.0']

setup_kwargs = {
    'name': 'asyncpg-stubs-h',
    'version': '0.23.0',
    'description': 'asyncpg stubs (pypi-upload copy)',
    'long_description': None,
    'author': 'Bryan Forbes',
    'author_email': 'bryan@reigndropsfall.net',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6.2,<4.0.0',
}


setup(**setup_kwargs)
