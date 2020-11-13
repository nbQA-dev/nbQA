"""Tests the parsing of command line parameters."""

import os
from typing import List

from nbqa.cmdline import CLIArgs


def test_cli_command_str() -> None:
    """Checks the command representation from the parsed CLI arguments."""
    path = os.path.abspath(os.path.join("tests", "data", "notebook_for_testing.ipynb"))

    args: List[str] = [
        "nbqa",
        "flake8",
        path,
        "--nbqa-mutate",
        "--nbqa-config=setup.cfg",
        "--ignore=F401",
        r"--nbqa-ignore-cells=%%%%cython,%%%%html",
        "--nbqa-diff",
        r"--nbqa-files=^tests/data",
        r"--nbqa-exclude=^tests/data/notebook_for",
    ]
    cli_args = CLIArgs.parse_args(args[1:])
    command: str = str(cli_args)
    for arg in args:
        assert arg in command
