# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pybeast']

package_data = \
{'': ['*']}

install_requires = \
['dynamic-beast>=1.8.1', 'typer>=0.3.2']

entry_points = \
{'console_scripts': ['pybeast = pybeast.main:app']}

setup_kwargs = {
    'name': 'pybeast',
    'version': '0.3.2',
    'description': '',
    'long_description': '# pyBEAST\n\n[![PyPi](https://img.shields.io/pypi/v/pybeast.svg)](https://pypi.org/project/pybeast/)\n[![tests](https://github.com/Wytamma/pybeast/actions/workflows/test.yml/badge.svg)](https://github.com/Wytamma/pybeast/actions/workflows/test.yml)\n[![cov](https://codecov.io/gh/Wytamma/pybeast/branch/master/graph/badge.svg)](https://codecov.io/gh/Wytamma/pybeast)\n\nPyBEAST helps with running BEAST with best practices. Configure a beast run in a reproducible manner can be time consuming. pyBEAST is designed to making running beast as simple as possible. \n\n## Install\nInstall `pybeast` with pip (requires python -V >= 3.7).\n\n```bash\npip install pybeast\n```\n\n## Command line interface\n\n### Basic usage \n\n```bash\npybeast beast.xml\n```\n\n1. Create output folder and run command\n2. Ensures the run is self-contained and reproducible.\n\n```\npybeast --run bash beast.xml\n```\n\nThe --run flag tells pybeast how to run the run.sh file. \n\n### SLURM example \n\nThis example using the SLURM template in the examples folder to submit the beast run as a job.\n\n```bash\npybeast --run sbatch --template examples/slurm.template examples/beast.xml\n```\n\nAt a minimum the template must contain `{{BEAST}}` key. This will be replaced with the beast2 run command.\n\nHere we use the -v (--template-variable) option to request 4 cpus. \n\n```bash\npybeast --run sbatch --template examples/slurm.template -v cpus-per-task=4 exmaples/beast.xml\n```\n\nDefault template variables can be specified in the template in the format `{{<key>=<value>}}` e.g. {{cpus-per-task=4}}.\n\n## dynamic variables\n\nPyBEAST uses [dynamic-beast](https://github.com/Wytamma/dynamic-beast) to create dynamic xml files that can be modified at runtime. \n\nHere we use the -d (--dynamic-variable) option to set the chain length to 1000000. \n\n```bash\npybeast -d mcmc.chainLength=1000000 examples/beast.xml\n```\n\nThe dynamic variables are saved to a `.json` file in the run directory. This file can be further edited before runtime. At run time the values in the JSON file will be used in the analysis. \n\n## Example \n\n### BETS\n\nUse pybeast + feast to run BETS.\n\n```bash\nALIGNMENT=${1?Must provide an ALIGNMENT}\nfor XML_FILE in $(ls examples/BETS-templates/*)\ndo  \n    GROUP_NAME="BETS/$(basename "${ALIGNMENT}" .fasta)/$(basename "${XML_FILE}" .xml)"\n    pybeast \\\n        --run sbatch \\\n        --overwrite \\\n        --threads 8 \\\n        --duplicates 3 \\\n        --template examples/slurm.template \\\n        -v cpus-per-task=8 \\\n        --group $GROUP_NAME \\\n        -d "alignment=$ALIGNMENT" \\\n        -d "Date.delimiter=_" \\\n        -d "Date.dateFormat=yyyy/M/dd" \\\n        --ps \\\n        -d "ps.nrOfSteps=50" \\\n        -d "ps.chainLength=250000" \\\n        -d "ps.rootdir={{run_directory}}/logs" \\\n        $XML_FILE\ndone\n```\n\n## Help\n\n```\n❯ pybeast --help\nUsage: pybeast [OPTIONS] BEAST_XML_PATH\n\nArguments:\n  BEAST_XML_PATH  [required]\n\nOptions:\n  --run TEXT                    Run the run.sh file using this command.\n  --resume / --no-resume        Resume the specified run.  [default: no-\n                                resume]\n  --group TEXT                  Group runs in this folder.\n  --description TEXT            Text to prepend to output folder name.\n  --overwrite / --no-overwrite  Overwrite run folder if exists.  [default: no-\n                                overwrite]\n  --seed INTEGER                Seed to use in beast analysis.\n  --duplicates INTEGER          Number for duplicate runs to create.\n                                [default: 1]\n  -d, --dynamic-variable TEXT   Dynamic variable in the format <key>=<value>.\n  --template PATH               Template for run.sh. Beast command is append\n                                to end of file.\n  -v, --template-variable TEXT  Template variable in the format <key>=<value>.\n  --chain-length INTEGER        Number of step in MCMC chain.\n  --samples INTEGER             Number of samples to collect.\n  --threads INTEGER             Number of threads and beagle instances to use\n                                (one beagle per core). If not specified\n                                defaults to number of cores.  [default: 1]\n  --mc3 / --no-mc3              Use dynamic-beast to set default options for\n                                running MCMCMC.  [default: no-mc3]\n  --ps / --no-ps                Use dynamic-beast to set default options for\n                                running PathSampler.  [default: no-ps]\n  --ns / --no-ns                Use dynamic-beast to set default options for\n                                running multi threaded nested sampling.\n                                [default: no-ns]\n  --install-completion          Install completion for the current shell.\n  --show-completion             Show completion for the current shell, to copy\n                                it or customize the installation.\n  --help                        Show this message and exit.\n  ```',
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
