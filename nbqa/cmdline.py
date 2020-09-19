import argparse
import sys
from textwrap import dedent
from typing import List, Optional

from nbqa import __version__


class CLIArgs:
    command: str
    root_dirs: List[str]
    nbqa_addopts: List[str]
    nbqa_mutate: bool
    nbqa_config: Optional[str] = None

    def __init__(self, args: argparse.Namespace, cmd_args: List[str]) -> None:
        self.command = args.command
        self.root_dirs = args.root_dirs
        self.nbqa_addopts = cmd_args
        self.nbqa_mutate = args.nbqa_mutate or False
        if args.nbqa_config is not None:
            self.nbqa_config = args.nbqa_config

    def __str__(self) -> str:
        args: List[str] = ["nbqa", self.command]
        args.extend(self.root_dirs)
        if self.nbqa_mutate:
            args.append("--nbqa-mutate")
        if self.nbqa_config:
            args.append(f"--nbqa-config={self.nbqa_config}")
        args.extend(self.nbqa_addopts)

        return " ".join(args)

    @staticmethod
    def parse_args(raw_args: Optional[List[str]]) -> "CLIArgs":
        """
        Parse command-line arguments.
        Parameters
        ----------
        raw_args
            Passed via command-line.
        Returns
        -------
        command
            The third-party tool to run (e.g. :code:`mypy`).
        root_dirs
            The notebooks or directories to run third-party tool on.
        allow_mutation
            Whether to allow 3rd party tools to modify notebooks.
        nbqa_config
            Config file for 3rd party tool (e.g. :code:`.mypy.ini`)
        cmd_args
            Any additional flags passed to third-party tool (e.g. :code:`--quiet`).
        Raises
        ------
        ValueError
            If user doesn't specify both a command and a notebook/directory to run it
            on (e.g. if the user runs :code:`nbqa flake8` instead of :code:`nbqa flake8 .`).
        """
        parser = argparse.ArgumentParser(
            description="Adapter to run any code-quality tool on a Jupyter notebook.",
            usage=dedent(
                """\
                nbqa <command> <notebook or directory> <flags>
                example:
                    nbqa flake8 my_notebook.ipynb --ignore=E203\
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
            "--version", action="version", version=f"nbQA {__version__}"
        )
        try:
            args, cmd_args = parser.parse_known_args(raw_args)
        except SystemExit as exception:
            if exception.code != 0:
                msg = (
                    "Please specify both a command and a notebook/directory, e.g.\n"
                    "nbqa flake8 my_notebook.ipynb"
                )
                raise ValueError(msg) from exception
            sys.exit(0)  # pragma: nocover
        else:
            return CLIArgs(args, cmd_args)
