# pyBEAST

[![PyPi](https://img.shields.io/pypi/v/pybeast.svg)](https://pypi.org/project/pybeast/)
[![tests](https://github.com/Wytamma/pybeast/actions/workflows/test.yml/badge.svg)](https://github.com/Wytamma/pybeast/actions/workflows/test.yml)
[![cov](https://codecov.io/gh/Wytamma/pybeast/branch/master/graph/badge.svg)](https://codecov.io/gh/Wytamma/pybeast)

PyBEAST helps with running BEAST with best practices. Configure a beast run in a reproducible manner can be time consuming. pyBEAST is designed to making running beast as simple as possible. 

## Install
Install `pybeast` with pip (requires python -V >= 3.6.2).

```bash
pip install pybeast
```

## Command line interface

### Basic usage 

```bash
pybeast beast.xml
```

1. Create output folder and run command
2. Ensures the run is self-contained and reproducible.


```bash
pybeast --template slurm_template.pbs beast.xml
```
1. Create output folder and run command (using template)


### SLURM example 

This example using the SLURM template in the examples folder to submit the beast run as a job.

```bash
pybeast --run sbatch --template examples/slurm.template examples/beast.xml
```

Here we use the -v (--template-variable) option to request 4 cpus. 
```bash
pybeast --run sbatch --template examples/slurm.template -v ncpus=4 exmaples/beast.xml
```

## dynamic variables

PyBEAST uses [dynamic-beast]() to create dynamic xml files that can be modified at runtime. 

Here we use the -d (--dynamic-variable) option to set the chain length to 1000000. 

```bash
pybeast -d mcmc.chainLength=1000000 examples/beast.xml
```

## create a dynamic variables file 
