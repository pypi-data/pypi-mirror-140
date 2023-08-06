# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pybeast']

package_data = \
{'': ['*']}

install_requires = \
['dynamic-beast>=1.8.0,<2.0.0', 'typer>=0.4.0,<0.5.0']

entry_points = \
{'console_scripts': ['pybeast = pybeast.main:app']}

setup_kwargs = {
    'name': 'pybeast',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Wytamma Wirth',
    'author_email': 'wytamma.wirth@me.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6.2,<4.0',
}


setup(**setup_kwargs)
