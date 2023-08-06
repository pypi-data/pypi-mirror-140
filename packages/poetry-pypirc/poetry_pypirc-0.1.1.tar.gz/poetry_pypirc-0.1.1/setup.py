# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['poetry_pypirc']

package_data = \
{'': ['*']}

install_requires = \
['configparser', 'pathlib>=1.0.1,<2.0.0', 'sh>=1.14.2,<2.0.0']

entry_points = \
{'console_scripts': ['poetry-pypirc = poetry_pypirc.main:main']}

setup_kwargs = {
    'name': 'poetry-pypirc',
    'version': '0.1.1',
    'description': 'Sets poetry repository configs from a pypirc file.',
    'long_description': None,
    'author': 'Narek Amirbekian',
    'author_email': None,
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
