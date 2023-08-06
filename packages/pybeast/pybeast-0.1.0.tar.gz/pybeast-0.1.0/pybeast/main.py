import json
import os
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

app = typer.Typer()


@dataclass
class Command:
    command: str
    final: Optional[str] = None
    args: List[str] = field(default_factory=list)

    def add_arg(self, arg: str):
        self.args.append(arg)

    def add_output_handler(self, pipe, value):
        self.final = f"{pipe} {value}"

    def format(self, indent=4):
        join_str = f' \\\n{" " * indent}'
        return f"""{self.command}{join_str}{join_str.join(self.args)} {self.final if self.final else ''}"""

    def __str__(self) -> str:
        return (
            f"{self.command} {' '.join(self.args)} {self.final if self.final else ''}"
        )


def create_beast_run_command(
    dynamic_xml_path: Path,
    working_directory: Path,
    threads: int,
    json_path: Path,
    seed: int,
):
    """Create the BEAST run command"""

    cmd = Command("beast")

    cmd.add_arg("-overwrite")
    cmd.add_arg("-beagle")
    cmd.add_arg(f"-statefile {str(dynamic_xml_path).replace('.dynamic.', '.')}.state")
    cmd.add_arg(f"-seed {seed}")
    cmd.add_arg(f"-prefix {working_directory}/")
    cmd.add_arg(f"-instances {threads}")
    cmd.add_arg(f"-threads {threads}")
    cmd.add_arg(f"-DF {json_path}")
    cmd.add_arg(f"-DFout {str(dynamic_xml_path).replace('.dynamic.', '.')}")
    cmd.add_arg(str(dynamic_xml_path))

    cmd.add_output_handler(
        ">>", f"{working_directory}/{working_directory.stem}.out 2>&1"
    )

    return cmd


def populate_template(
    outfile: Path,
    cmd: Command,
    template_path: Path = None,
) -> Path:
    """Fill in a given template"""

    if template_path:
        with open(template_path) as f:
            template = "".join(f.readlines())

        with open(outfile, "w") as f:
            f.write(template)

    with open(outfile, "a") as f:
        f.write(cmd.format(2))

    return outfile


def create_dynamic_template(beast_xml_file: Path, outdir: Path) -> Path:
    """Given a BEAST2 xml file create a dynamic xml file and return it's path"""
    basename = beast_xml_file.stem
    dynamic_filename = Path(basename).with_suffix(".dynamic.xml")
    json_filename = Path(basename).with_suffix(".json")
    dynamic_outfile = f"{outdir}/{dynamic_filename}"
    json_outfile = f"{outdir}/{json_filename}"
    create_dynamic_xml(beast_xml_file, outfile=dynamic_outfile, json_out=json_outfile)
    return Path(dynamic_outfile), Path(json_outfile)


def create_working_directory(
    fasta_file_path: Path,
    description: str,
    group: str,
    overwrite: bool,
    duplicate: int,
) -> Path:
    basename = fasta_file_path.stem
    working_directory = f"{basename}"
    if description:
        working_directory = f"{description}_{working_directory}"
    if group:
        working_directory = f"{group}/{working_directory}"
    number = duplicate
    working_directory_numbered = Path(f"{working_directory}_{number:03d}")
    if overwrite and working_directory_numbered.exists():
        shutil.rmtree(working_directory_numbered)
    while working_directory_numbered.exists():
        number += 1
        working_directory_numbered = Path(f"{working_directory}_{number:03d}")
    os.makedirs(working_directory_numbered)
    return Path(working_directory_numbered)


def set_dynamic_vars(json_path, sample_frequency, chain_length, dynamic_variables):
    with open(json_path) as f:
        data = json.load(f)
        for key in data.keys():
            if key.startswith("treelog") and key.endswith("logEvery"):
                data[key] = str(sample_frequency)
            if key.startswith("tracelog") and key.endswith("logEvery"):
                data[key] = str(sample_frequency)
        data["mcmc.chainLength"] = chain_length
        data.update(dynamic_variables)
        json.dump(data, open(json_path, "w"), indent=4)


@app.command()
def main(
    beast_xml_path: Path,
    run: str = typer.Option(None, help="Run the run.sh file using this command."),
    group: str = typer.Option(None, help="Group runs in this folder."),
    description: str = typer.Option("", help="Text to prepend to output folder name."),
    overwrite: bool = typer.Option(False, help="Overwrite run folder if exists."),
    seed: int = typer.Option(None, help="Seed to use in beast analysis."),
    duplicates: int = typer.Option(1, help="Number for duplicate runs to create."),
    dynamic_variable: Optional[List[str]] = typer.Option(
        None,
        "--dynamic-variable",
        "-d",
        help="Dynamic variable in the format key=value.",
    ),
    template: Path = typer.Option(
        None, help="Template for run.sh. Beast command is append to end of file."
    ),
    chain_length: int = typer.Option(10000000, help="Number of step in MCMC chain."),
    samples: int = typer.Option(10000, help="Number of samples to collect."),
    threads: int = typer.Option(
        1,
        help="Number of threads and beagle instances to use (one beagle per core). If not specified defaults to number of cores.",
    ),
):
    for i in range(duplicates):

        sample_frequency = chain_length // samples

        working_directory = create_working_directory(
            beast_xml_path,
            description,
            group=group,
            overwrite=overwrite,
            duplicate=i + 1,
        )

        dynamic_xml_path, json_path = create_dynamic_template(
            beast_xml_path, outdir=working_directory
        )
        dynamic_variables = {d.split("=")[0]: d.split("=")[1] for d in dynamic_variable}
        set_dynamic_vars(
            json_path,
            sample_frequency=sample_frequency,
            chain_length=chain_length,
            dynamic_variables=dynamic_variables,
        )

        beast_seed = str(random.randint(1, 10000000))

        if seed:
            beast_seed = seed

        with open(f"{working_directory}/seed.txt", "w") as f:
            f.write(beast_seed)

        cmd_list = create_beast_run_command(
            dynamic_xml_path, working_directory, threads, json_path, beast_seed
        )

        run_file = f"{working_directory}/run.sh"

        populate_template(
            run_file,
            cmd_list,
            template_path=template,
        )
        typer.echo(f"Created run file -> {run_file}")

        if run:
            os.system(f"{run} {run_file}")
