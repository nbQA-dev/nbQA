"""Parses the command line arguments provided."""
import argparse
from textwrap import dedent
from typing import Optional, Sequence

from nbqa import __version__
from nbqa.text import BOLD, RESET

CONFIGURATION_URL = "https://nbqa.readthedocs.io/en/latest/configuration.html"
DOCS_URL = "https://nbqa.readthedocs.io/en/latest/index.html"
USAGE_MSG = dedent(
    f"""\
    nbqa <code quality tool> <notebook or directory> <nbqa options> <code quality tool arguments>

    {BOLD}Please specify:{RESET}
    - 1) a code quality tool (e.g. `black`, `pyupgrade`, `flake`, ...)
    - 2) some notebooks (or, if supported by the tool, directories)
    - 3) (optional) flags for nbqa (e.g. `--nbqa-mutate`)
    - 4) (optional) flags for code quality tool (e.g. `--line-length` for `black`)

    {BOLD}Examples:{RESET}
        nbqa flake8 notebook.ipynb
        nbqa black notebook.ipynb --line-length=96
        nbqa pyupgrade notebook_1.ipynb notebook_2.ipynb

    {BOLD}Mutation:{RESET} to let `nbqa` modify your notebook(s), also pass `--nbqa-mutate`, e.g.:
        nbqa black notebook.ipynb --nbqa-mutate

    See {DOCS_URL} for more details on how to run `nbqa`.
    """
)


class CLIArgs:  # pylint: disable=R0902,R0903
    """
    Stores the command line arguments passed.

    Attributes
    ----------
    command
        The third-party tool to run (e.g. :code:`mypy`).
    root_dirs
        The notebooks or directories to run third-party tool on.
    nbqa_mutate
        Whether to allow 3rd party tools to modify notebooks.
    nbqa_config
        Config file for 3rd party tool (e.g. :code:`.mypy.ini`)
    nbqa_ignore_cells
        Deprecated.
    nbqa_process_cells
        Process code within these cell magics.
    nbqa_addopts
        Any additional flags passed to third-party tool (e.g. :code:`--quiet`).
    nbqa_files
        Global file include pattern.
    nbqa_exclude
        Global file exclude pattern.
    """

    command: str
    root_dirs: Sequence[str]
    nbqa_addopts: Sequence[str]
    nbqa_mutate: bool
    nbqa_ignore_cells: Optional[str]
    nbqa_process_cells: Optional[str]
    nbqa_config: Optional[str]
    nbqa_diff: bool
    nbqa_files: Optional[str]
    nbqa_exclude: Optional[str]

    def __init__(self, args: argparse.Namespace, cmd_args: Sequence[str]) -> None:
        """
        Initialize this instance with the parsed command line arguments.

        Parameters
        ----------
        args
            Command line arguments passed to nbqa
        cmd_args
            Additional options to pass to the tool
        """
        self.command = args.command
        self.root_dirs = args.root_dirs
        self.nbqa_addopts = cmd_args
        self.nbqa_mutate = args.nbqa_mutate or False
        self.nbqa_config = args.nbqa_config or None
        self.nbqa_ignore_cells = args.nbqa_ignore_cells or None
        self.nbqa_process_cells = args.nbqa_process_cells or None
        self.nbqa_diff = args.nbqa_diff or False
        self.nbqa_files = args.nbqa_files or None
        self.nbqa_exclude = args.nbqa_exclude or None

    @staticmethod
    def parse_args(argv: Optional[Sequence[str]]) -> "CLIArgs":
        """
        Parse command-line arguments.

        Parameters
        ----------
        argv
            Passed via command-line.
        Returns
        -------
        CLIArgs
            Object that holds all the parsed command line arguments.
        """
        parser = argparse.ArgumentParser(
            description="Run any standard Python code-quality tool on a Jupyter notebook.",
            usage=USAGE_MSG,
        )
        parser.add_argument("command", help="Command to run, e.g. `flake8`.")
        parser.add_argument(
            "root_dirs", nargs="+", help="Notebooks or directories to run command on."
        )
        parser.add_argument(
            "--nbqa-files",
            help="Global file include pattern.",
        )
        parser.add_argument(
            "--nbqa-exclude",
            help="Global file exclude pattern.",
        )
        parser.add_argument(
            "--nbqa-mutate",
            action="store_true",
            help="Allows `nbqa` to modify notebooks.",
        )
        parser.add_argument(
            "--nbqa-diff",
            action="store_true",
            help="Show diff which would result from running --nbqa-mutate.",
        )
        parser.add_argument(
            "--nbqa-config",
            required=False,
            help="Config file for third-party tool (e.g. `setup.cfg`)",
        )
        parser.add_argument(
            "--nbqa-ignore-cells",
            required=False,
            help=dedent(
                r"""
                Deprecated, do not use.
                """
            ),
        )
        parser.add_argument(
            "--nbqa-process-cells",
            required=False,
            help=dedent(
                r"""
                Process code within these cell magics. You can pass multiple options,
                e.g. `nbqa black my_notebook.ipynb --nbqa-process-cells add_to,write_to`
                by placing commas between them.
                """
            ),
        )
        parser.add_argument(
            "--version", action="version", version=f"nbqa {__version__}"
        )
        args, cmd_args = parser.parse_known_args(argv)
        return CLIArgs(args, cmd_args)
