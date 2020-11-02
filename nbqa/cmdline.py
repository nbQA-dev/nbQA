"""Parses the command line arguments provided."""
import argparse
import sys
from textwrap import dedent
from typing import List, Optional

from nbqa import __version__

RED = "\x1b[1;31m"
BOLD = "\033[1m"
RESET = "\x1b[0m"
CONFIGURATION_URL = "https://nbqa.readthedocs.io/en/latest/configuration.html"
DOCS_URL = "https://nbqa.readthedocs.io/en/latest/index.html"


class CLIArgs:
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
        Ignore cells whose first line starts with the input token
    nbqa_addopts
        Any additional flags passed to third-party tool (e.g. :code:`--quiet`).
    """

    command: str
    root_dirs: List[str]
    nbqa_addopts: List[str]
    nbqa_mutate: bool
    nbqa_ignore_cells: Optional[str]
    nbqa_config: Optional[str]

    def __init__(self, args: argparse.Namespace, cmd_args: List[str]) -> None:
        """
        Initialize this instance with the parsed command line arguments.

        Parameters
        ----------
        args (argparse.Namespace):
            Command line arguments passed to nbqa
        cmd_args (List[str]):
            Additional options to pass to the tool
        """
        self.command = args.command
        self.root_dirs = args.root_dirs
        self.nbqa_addopts = cmd_args
        self.nbqa_mutate = args.nbqa_mutate or False
        self.nbqa_config = args.nbqa_config or None
        self.nbqa_ignore_cells = args.nbqa_ignore_cells or None

    def __str__(self) -> str:
        """Return the command from the parsed command line arguments."""
        args: List[str] = ["nbqa", self.command]
        args.extend(self.root_dirs)
        if self.nbqa_mutate:
            args.append("--nbqa-mutate")
        if self.nbqa_config:
            args.append(f"--nbqa-config={self.nbqa_config}")
        if self.nbqa_ignore_cells:
            args.append(f"--nbqa-ignore-cells={self.nbqa_ignore_cells}")
        args.extend(self.nbqa_addopts)

        return " ".join(args)

    @staticmethod
    def parse_args(argv: Optional[List[str]]) -> "CLIArgs":
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
            usage=dedent(
                f"""\
                nbqa <code quality tool> <notebook or directory> <flags>

                {BOLD}Please specify:{RESET}
                - 1) a code quality tool
                - 2) some notebooks (or, if supported by the tool, directories)
                - 3) (optional) extra flags

                {BOLD}Examples:{RESET}
                    nbqa black notebook.ipynb
                    nbqa black notebook.ipynb --line-length=96
                    nbqa black notebook_1.ipynb notebook_2.ipynb

                If you want to let `nbqa` modify your notebook(s), also pass `--nbqa-mutate`:
                    nbqa black notebook.ipynb --nbqa-mutate

                See {DOCS_URL} for more details on how to run `nbqa`.
                """
            ),
        )
        parser.add_argument("command", help="Command to run, e.g. `flake8`.")
        parser.add_argument(
            "root_dirs", nargs="+", help="Notebooks or directories to run command on."
        )
        parser.add_argument(
            "--nbqa-mutate",
            action="store_true",
            help="Allows `nbqa` to modify notebooks.",
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
                Ignore cells whose first line starts with this. You can pass multiple options,
                e.g. `nbqa black my_notebook.ipynb --nbqa-ignore-cells %%%%cython,%%%%html`
                by placing commas between them.
                """
            ),
        )
        parser.add_argument(
            "--version", action="version", version=f"nbqa {__version__}"
        )
        try:
            args, cmd_args = parser.parse_known_args(argv)
        except SystemExit as exception:
            sys.exit(exception.code)  # pragma: nocover
        else:
            return CLIArgs(args, cmd_args)
