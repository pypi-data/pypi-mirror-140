# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pytest_ptera']

package_data = \
{'': ['*']}

install_requires = \
['ptera>=1.0.0', 'pytest>=6.2.4,<7.0.0']

entry_points = \
{'pytest11': ['ptera = pytest_ptera.main']}

setup_kwargs = {
    'name': 'pytest-ptera',
    'version': '0.3.0',
    'description': 'Use ptera probes in tests',
    'long_description': None,
    'author': 'Olivier Breuleux',
    'author_email': 'breuleux@gmail.com',
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
