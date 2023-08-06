# pyBEAST

[![PyPi](https://img.shields.io/pypi/v/pybeast.svg)](https://pypi.org/project/pybeast/)
[![tests](https://github.com/Wytamma/pybeast/actions/workflows/test.yml/badge.svg)](https://github.com/Wytamma/pybeast/actions/workflows/test.yml)
[![cov](https://codecov.io/gh/Wytamma/pybeast/branch/master/graph/badge.svg)](https://codecov.io/gh/Wytamma/pybeast)

PyBEAST helps with running BEAST with best practices. Configure a beast run in a reproducible manner can be time consuming. pyBEAST is designed to making running beast as simple as possible. 

## Install
Install `pybeast` with pip (requires python -V >= 3.7).

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

```
pybeast --run bash beast.xml
```

The --run flag tells pybeast how to run the run.sh file. 

### SLURM example 

This example using the SLURM template in the examples folder to submit the beast run as a job.

```bash
pybeast --run sbatch --template examples/slurm.template examples/beast.xml
```

At a minimum the template must contain `{{BEAST}}` key. This will be replaced with the beast2 run command.

Here we use the -v (--template-variable) option to request 4 cpus. 

```bash
pybeast --run sbatch --template examples/slurm.template -v cpus-per-task=4 exmaples/beast.xml
```

Default template variables can be specified in the template in the format `{{<key>=<value>}}` e.g. {{cpus-per-task=4}}.

## dynamic variables

PyBEAST uses [dynamic-beast](https://github.com/Wytamma/dynamic-beast) to create dynamic xml files that can be modified at runtime. 

Here we use the -d (--dynamic-variable) option to set the chain length to 1000000. 

```bash
pybeast -d mcmc.chainLength=1000000 examples/beast.xml
```

The dynamic variables are saved to a `.json` file in the run directory. This file can be further edited before runtime. At run time the values in the JSON file will be used in the analysis. 

## Example 

### BETS

Use pybeast + feast to run BETS.

```bash
ALIGNMENT=${1?Must provide an ALIGNMENT}
for XML_FILE in $(ls examples/BETS-templates/*)
do  
    GROUP_NAME="BETS/$(basename "${ALIGNMENT}" .fasta)/$(basename "${XML_FILE}" .xml)"
    pybeast \
        --run sbatch \
        --overwrite \
        --threads 8 \
        --duplicates 3 \
        --template examples/slurm.template \
        -v cpus-per-task=8 \
        --group $GROUP_NAME \
        -d "alignment=$ALIGNMENT" \
        -d "Date.delimiter=_" \
        -d "Date.dateFormat=yyyy/M/dd" \
        --ps \
        -d "ps.nrOfSteps=50" \
        -d "ps.chainLength=250000" \
        -d "ps.rootdir={{run_directory}}/logs" \
        $XML_FILE
done
```
