import json
import os
import glob
from pathlib import Path
from re import S
import textwrap
import typer
from typing import Optional, List, final
import shutil
import random
from dynamic_beast import create_dynamic_xml
from typing import List, Optional
from dataclasses import dataclass, field

from pybeast import Template, Command

app = typer.Typer()


def create_beast_run_command(
    dynamic_xml_path: Path,
    run_directory: Path,
    threads: int,
    json_path: Path,
    seed: int,
    resume: bool,
):
    """Create the BEAST run command"""

    cmd = Command("beast")

    if resume:
        cmd.add_arg("-resume")
    cmd.add_arg("-overwrite")
    cmd.add_arg("-beagle")
    cmd.add_arg(f"-statefile {str(dynamic_xml_path).replace('.dynamic.', '.')}.state")
    cmd.add_arg(f"-seed {seed}")
    cmd.add_arg(f"-prefix {run_directory}/logs/")
    cmd.add_arg(f"-instances {threads}")
    cmd.add_arg(f"-threads {threads}")
    cmd.add_arg(f"-DF {json_path}")
    cmd.add_arg(f"-DFout {str(dynamic_xml_path).replace('.dynamic.', '.')}")
    cmd.add_arg(str(dynamic_xml_path))

    cmd.add_output_handler("2>&1 | tee", f"{run_directory}/{run_directory.stem}.out")

    return cmd


def populate_template(
    outfile: Path,
    cmd: Command,
    template_path: Path = None,
    template_variables: dict = None,
) -> Path:
    """Fill in a given template"""

    if template_path:
        template = Template(template_path)
        template.populate(BEAST=cmd.format(2), **template_variables)
        template.write(outfile)
    else:
        with open(outfile, "w") as f:
            f.write(cmd.format(2))

    return outfile


def create_dynamic_template(
    beast_xml_file: Path, outdir: Path, mc3: bool, ps: bool, ns: bool
) -> Path:
    """Given a BEAST2 xml file create a dynamic xml file and return it's path"""
    basename = beast_xml_file.stem
    dynamic_filename = Path(basename).with_suffix(".dynamic.xml")
    json_filename = Path(basename).with_suffix(".json")
    dynamic_outfile = f"{outdir}/{dynamic_filename}"
    json_outfile = f"{outdir}/{json_filename}"
    create_dynamic_xml(
        beast_xml_file,
        outfile=dynamic_outfile,
        json_out=json_outfile,
        mc3=mc3,
        ps=ps,
        ns=ns,
    )
    return Path(dynamic_outfile), Path(json_outfile)


def create_run_directory(
    beast_xml_path: Path,
    description: str,
    group: str,
    overwrite: bool,
    duplicate: int,
    resume: bool,
) -> Path:
    if resume:
        run_directory = Path(f"{beast_xml_path.parent}_RESUMED")
        run_directory_numbered = Path(
            f"{beast_xml_path.parent}_RESUMED_{duplicate:03d}"
        )
    else:
        basename = beast_xml_path.stem
        run_directory = f"{basename}"
        if description:
            run_directory = f"{description}_{run_directory}"
        if group:
            run_directory = f"{group}/{run_directory}"
        run_directory_numbered = Path(f"{run_directory}_{duplicate:03d}")
    if overwrite and run_directory_numbered.exists():
        shutil.rmtree(run_directory_numbered)
    while run_directory_numbered.exists():
        duplicate += 1
        run_directory_numbered = Path(f"{run_directory}_{duplicate:03d}")
    os.makedirs(run_directory_numbered)
    os.makedirs(f"{run_directory_numbered}/logs")
    if resume:
        shutil.copytree(
            f"{beast_xml_path.parent}/logs/",
            f"{run_directory_numbered}/logs/",
            dirs_exist_ok=True,
        )
        state_file = glob.glob(f"{beast_xml_path.parent}/*.state")[0]
        shutil.copy(state_file, f"{run_directory_numbered}")
        shutil.copy(f"{beast_xml_path.parent}/seed.txt", f"{run_directory_numbered}")
    return Path(run_directory_numbered)


def set_dynamic_vars(json_path, samples, chain_length, dynamic_variables):
    with open(json_path) as f:
        data = json.load(f)
        if chain_length:
            data["mcmc.chainLength"] = chain_length
        else:
            chain_length = data["mcmc.chainLength"]
        if samples:
            sample_frequency = int(chain_length) // samples
            for key in data.keys():
                if key.startswith("treelog") and key.endswith("logEvery"):
                    data[key] = str(sample_frequency)
                if key.startswith("tracelog") and key.endswith("logEvery"):
                    data[key] = str(sample_frequency)
        data.update(dynamic_variables)
        json.dump(data, open(json_path, "w"), indent=4)


@app.command()
def main(
    beast_xml_path: Path,
    run: str = typer.Option(None, help="Run the run.sh file using this command."),
    resume: bool = typer.Option(False, help="Resume the specified run."),
    group: str = typer.Option(None, help="Group runs in this folder."),
    description: str = typer.Option("", help="Text to prepend to output folder name."),
    overwrite: bool = typer.Option(False, help="Overwrite run folder if exists."),
    seed: int = typer.Option(None, help="Seed to use in beast analysis."),
    duplicates: int = typer.Option(1, help="Number for duplicate runs to create."),
    dynamic_variable: Optional[List[str]] = typer.Option(
        None,
        "--dynamic-variable",
        "-d",
        help="Dynamic variable in the format <key>=<value>.",
    ),
    template: Path = typer.Option(
        None, help="Template for run.sh. Beast command is append to end of file."
    ),
    template_variable: Optional[List[str]] = typer.Option(
        None,
        "--template-variable",
        "-v",
        help="Template variable in the format <key>=<value>.",
    ),
    chain_length: int = typer.Option(None, help="Number of step in MCMC chain."),
    samples: int = typer.Option(None, help="Number of samples to collect."),
    threads: int = typer.Option(
        1,
        help="Number of threads and beagle instances to use (one beagle per core). If not specified defaults to number of cores.",
    ),
    mc3: bool = typer.Option(
        False, help="Use dynamic-beast to set default options for running MCMCMC."
    ),
    ps: bool = typer.Option(
        False, help="Use dynamic-beast to set default options for running PathSampler."
    ),
    ns: bool = typer.Option(
        False,
        help="Use dynamic-beast to set default options for running multi threaded nested sampling.",
    ),
):
    for i in range(duplicates):

        run_directory = create_run_directory(
            beast_xml_path,
            description,
            group=group,
            overwrite=overwrite,
            duplicate=i + 1,
            resume=resume,
        )

        dynamic_xml_path, json_path = create_dynamic_template(
            beast_xml_path, outdir=run_directory, mc3=mc3, ps=ps, ns=ns
        )
        dynamic_variables = {
            d.split("=")[0]: "".join(d.split("=")[1:]) for d in dynamic_variable
        }
        for dv in dynamic_variables:
            dynamic_variables[dv] = dynamic_variables[dv].replace(
                "{{run_directory}}", str(run_directory)
            )

        set_dynamic_vars(
            json_path,
            samples=samples,
            chain_length=chain_length,
            dynamic_variables=dynamic_variables,
        )

        beast_seed = str(random.randint(1, 10000000))
        if seed:
            beast_seed = str(seed)
        elif resume:
            with open(f"{run_directory}/seed.txt") as f:
                beast_seed = f.read()

        with open(f"{run_directory}/seed.txt", "w") as f:
            f.write(beast_seed)

        cmd_list = create_beast_run_command(
            dynamic_xml_path, run_directory, threads, json_path, beast_seed, resume
        )

        run_file = f"{run_directory}/run.sh"

        template_variables = {
            d.split("=")[0]: "".join(d.split("=")[1:]) for d in template_variable
        }

        populate_template(
            run_file,
            cmd_list,
            template_path=template,
            template_variables=template_variables,
        )
        typer.echo(f"Created run file -> {run_file}")

        if run:
            os.system(f"{run} {run_file}")
