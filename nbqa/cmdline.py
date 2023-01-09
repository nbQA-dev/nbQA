"""Parses the command line arguments provided."""
import argparse
import sys
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
    - 3) (optional) flags for nbqa (e.g. `--nbqa-diff`, `--nbqa-shell`)
    - 4) (optional) flags for code quality tool (e.g. `--line-length` for `black`)

    {BOLD}Examples:{RESET}
        nbqa flake8 notebook.ipynb
        nbqa black notebook.ipynb --line-length=96
        nbqa pyupgrade notebook_1.ipynb notebook_2.ipynb

    See {DOCS_URL} for more details on how to run `nbqa`.
    """
)
DEPRECATED = {
    "--nbqa-skip-bad-cells": (
        "was deprecated in 0.13.0\n"
        "Cells with invalid syntax are now skipped by default"
    ),
    "--nbqa-ignore-cells": "was deprecated in 0.8.0 and is now unnecessary",
    "--nbqa-config": "was deprecated in 0.8.0 and is now unnecessary",
    "--nbqa-mutate": "was deprecated in 1.0.0 and is now unnecessary",
}


class CLIArgs:  # pylint: disable=R0902
    """Stores the command line arguments passed."""

    command: str
    root_dirs: Sequence[str]
    addopts: Optional[Sequence[str]]
    process_cells: Optional[Sequence[str]]
    diff: Optional[bool]
    files: Optional[str]
    exclude: Optional[str]
    dont_skip_bad_cells: Optional[bool]
    md: Optional[bool]
    shell: Optional[bool]

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
        if cmd_args:
            for flag, msg in DEPRECATED.items():
                if flag in cmd_args:
                    sys.stderr.write(f"Flag {flag} {msg}\n")
                    cmd_args = [arg for arg in cmd_args if arg != flag]
        self.command = args.command
        self.root_dirs = args.root_dirs
        self.addopts = cmd_args or None
        if args.nbqa_process_cells is not None:
            self.process_cells = args.nbqa_process_cells.split(",")
        else:
            self.process_cells = None
        self.diff = args.nbqa_diff or None
        self.files = args.nbqa_files
        self.exclude = args.nbqa_exclude
        self.dont_skip_bad_cells = args.nbqa_dont_skip_bad_cells or None
        if args.nbqa_skip_celltags is not None:
            self.skip_celltags = args.nbqa_skip_celltags.split(",")
        else:
            self.skip_celltags = None
        self.md = args.nbqa_md or None
        self.shell = args.nbqa_shell or None

    def __repr__(self) -> str:  # pragma: nocover
        """Print prettily."""
        return str(self.__dict__)

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
            "--nbqa-diff",
            action="store_true",
            help="Show diff which would result from running tool.",
        )
        parser.add_argument(
            "--nbqa-shell",
            action="store_true",
            help="Run `command` directly rather than `python -m command`",
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
        parser.add_argument(
            "--nbqa-dont-skip-bad-cells",
            action="store_true",
            help="Don't skip cells with invalid syntax.",
        )
        parser.add_argument(
            "--nbqa-skip-celltags",
            required=False,
            help=dedent(
                r"""
                Skip cells with have any of the given celltags.
                """
            ),
        )
        parser.add_argument(
            "--nbqa-md",
            action="store_true",
            help=dedent(
                r"""
                Process markdown cells, rather than Python ones.
                """
            ),
        )
        args, cmd_args = parser.parse_known_args(argv)
        return CLIArgs(args, cmd_args)
