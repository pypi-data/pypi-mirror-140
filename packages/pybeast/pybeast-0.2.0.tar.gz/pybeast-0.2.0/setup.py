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
    'version': '0.2.0',
    'description': '',
    'long_description': '# pyBEAST\n\n[![PyPi](https://img.shields.io/pypi/v/pybeast.svg)](https://pypi.org/project/pybeast/)\n[![tests](https://github.com/Wytamma/pybeast/actions/workflows/test.yml/badge.svg)](https://github.com/Wytamma/pybeast/actions/workflows/test.yml)\n[![cov](https://codecov.io/gh/Wytamma/pybeast/branch/master/graph/badge.svg)](https://codecov.io/gh/Wytamma/pybeast)\n\nPyBEAST helps with running BEAST with best practices. Configure a beast run in a reproducible manner can be time consuming. pyBEAST is designed to making running beast as simple as possible. \n\n## Install\nInstall `pybeast` with pip (requires python -V >= 3.6.2).\n\n```bash\npip install pybeast\n```\n\n## Command line interface\n\n### Basic usage \n\n```bash\npybeast beast.xml\n```\n\n1. Create output folder and run command\n2. Ensures the run is self-contained and reproducible.\n\n\n```bash\npybeast --template slurm_template.pbs beast.xml\n```\n1. Create output folder and run command (using template)\n\n\n### SLURM example \n\nThis example using the SLURM template in the examples folder to submit the beast run as a job.\n\n```bash\npybeast --run sbatch --template examples/slurm.template examples/beast.xml\n```\n\nHere we use the -v (--template-variable) option to request 4 cpus. \n```bash\npybeast --run sbatch --template examples/slurm.template -v ncpus=4 exmaples/beast.xml\n```\n\n## dynamic variables\n\nPyBEAST uses [dynamic-beast]() to create dynamic xml files that can be modified at runtime. \n\nHere we use the -d (--dynamic-variable) option to set the chain length to 1000000. \n\n```bash\npybeast -d mcmc.chainLength=1000000 examples/beast.xml\n```\n\n## create a dynamic variables file \n',
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
