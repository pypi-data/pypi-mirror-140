from pathlib import Path
from typing import Any, Optional

import click

# from beepy import beep
from click import ClickException


from . import __version__
from .build_html import HTMLBuilder
from .core import Core
from .setup import setup_github_action

from .pandoc import print_pandoc_info

# from .build_latex import build_latex
from .report import Report
from rich import print

import toml


def logo(version: str) -> str:
    return (
        R""" ___ __  __ ____ ____ ____ __  __   __   ____ _  _
/ __|  )(  |  _ ( ___|  _ (  \/  ) /__\ (  _ ( )/ )
\__ \)(__)( )___/)__) )   /)    ( /(__)\ )   /)  (
(___(______|__) (____|_)\_|_/\/\_|__)(__|_)\_|_)\_) """
        + version
    )


def logo_2(version: str) -> str:
    return """[bold]SUPERMARK[/bold] """ + version


@click.version_option(version=__version__)
@click.group()
# @click.version_option(__version__)
def supermark():
    ...


def ensure_path(path: Any) -> Optional[Path]:
    if path is None:
        return None
    elif isinstance(path, Path):
        return path
    elif isinstance(path, bytes):
        return Path(path.decode("utf-8"))
    elif isinstance(path, str):
        return Path(path)
    else:
        raise ValueError()


@supermark.command(help="Build a project, site or document.")
@click.option(
    "-a",
    "--all",
    is_flag=True,
    default=False,
    help="Rebuild all pages, not only modified ones.",
)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    default=False,
    help="Provide more feedback on what is happening.",
)
@click.option(
    "-d",
    "--draft",
    is_flag=True,
    default=False,
    help="Also print draft parts of the documents.",
)
@click.option(
    "-c",
    "--continuous",
    is_flag=True,
    default=False,
    help="Observe the source directory and run continuously.",
)
@click.option(
    "-p",
    "--path",
    "path",
    type=click.Path(exists=True, readable=True, path_type=Path),
    help="Base path pointing to the folder that contains input, template, output path and an optional config file.",
)
@click.option(
    "-i",
    "--input",
    "input",
    type=click.Path(exists=True, readable=True, path_type=Path),
    help="Input directory containing the source files.",
)
@click.option(
    "-o",
    "--output",
    "output",
    type=click.Path(exists=True, writable=True, path_type=Path),
    help="Output directory.",
)
@click.option(
    "-t",
    "--template",
    "template",
    type=click.File("rb"),
    help="Template file for the transformation.",
)
@click.option(
    "-r",
    "--reformat",
    is_flag=True,
    default=False,
    help="Reformat the input file.",
)
@click.option(
    "-l",
    "--log",
    is_flag=True,
    default=False,
    help="Write messages to a log file instead of standard output.",
)
def build(
    all: bool,
    verbose: bool,
    draft: bool,
    continuous: bool,
    path: Optional[Path] = None,
    input: Optional[Path] = None,
    output: Optional[Path] = None,
    template: Optional[Path] = None,
    reformat: bool = False,
    log: bool = False,
):
    report = Report()
    core = Core(report=report)
    print(logo_2(__version__))
    print_pandoc_info()

    path = ensure_path(path)
    input = ensure_path(input)
    output = ensure_path(output)
    template = ensure_path(template)

    base_path = path or Path.cwd()
    input_path = None
    output_path = None
    template_path = None

    # read configuration file
    config_file = Path("config.toml")
    if config_file.exists():
        report.info("Found configuration file.", path=config_file)
        config = toml.load(config_file)
        if "input" in config and input is None:
            input_path = base_path / config["input"]
        if "output" in config and output is None:
            output_path = base_path / config["output"]
        if "template" in config and template is None:
            template_path = base_path / config["template"]

    if input_path is None:
        input_path = base_path / "pages"
    if output_path is None:
        output_path = output or Path.cwd()
    if template_path is None:
        template_path = template or (base_path / "templates/page.html")

    format = "html"
    
    builder = HTMLBuilder(
        input_path,
        output_path,
        template_path,
        report,
        rebuild_all_pages=all,
        abort_draft=not draft,
        verbose=verbose,
        reformat=reformat,
    )
    builder.set_core(core)
    builder.build()
    if log:
        report.print_to_file(base_path / "supermark.log")
    else:
        report.print(verbose=verbose)
    if report.has_error():
        # beep(3)  # sad error
        ex = ClickException("Something is wrong.")
        ex.exit_code = 1
        raise ex
    # else:
    # beep(5)


@supermark.command(help="Show info about a project and installation.")
def info():
    report = Report()
    core = Core(report=report)
    core.info()


@supermark.command(help="Setup a project.")
@click.option(
    "-g",
    "--githubaction",
    "githubaction",
    is_flag=True,
    default=False,
    help="Add a Github action so that projects are built after each commit.",
)
@click.option(
    "-p",
    "--path",
    "path",
    type=click.Path(exists=True, readable=True, path_type=Path),
    help="Base path containing the source files. Current working directory is default.",
)
def setup(
    githubaction: bool = False,
    path: Optional[Path] = None,
):
    base_path = path or Path.cwd()
    if githubaction:
        setup_github_action(base_path)
