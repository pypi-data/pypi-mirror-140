# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['billy_penn']

package_data = \
{'': ['*'], 'billy_penn': ['data/*']}

install_requires = \
['openpyxl>=3.0.9,<4.0.0', 'pandas>=1.4.0,<2.0.0', 'pydantic>=1.9.0,<2.0.0']

setup_kwargs = {
    'name': 'billy-penn',
    'version': '0.1.4',
    'description': "A package for meta information about the City of Philadelphia's government.",
    'long_description': None,
    'author': 'Nick Hand',
    'author_email': 'nick.hand@phila.gov',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
