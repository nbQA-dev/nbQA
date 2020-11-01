"""Parse output from code quality tools."""

import re
from pathlib import Path
from typing import Mapping, Match, Tuple


def _get_pattern(notebook: Path, command: str) -> str:
    """
    Get pattern with which code quality tool reports output.

    Parameters
    ----------
    notebook
        Notebook command is being run on.
    command
        Code quality tool.

    Returns
    -------
    str
        Patter of reported output.
    """
    if command == "black":
        return (
            rf"(?<=^error: cannot format {re.escape(str(notebook))}: Cannot parse: )\d+"
        )
    if command == "doctest":
        return rf'(?<=^File "{re.escape(str(notebook))}", line )\d+'
    # This next one is the most common one and is used by flake, pylint, mypy, and more.
    return rf"(?<=^{re.escape(str(notebook))}:)\d+"


def _extra_substitution(
    out: str, err: str, notebook: Path, command: str
) -> Tuple[str, str]:
    """
    Make extra substitution as required by some tools.

    Parameters
    ----------
    out
        Captured stdout from third-party tool.
    err
        Captured stdout from third-party tool.
    notebook
        Original Jupyter notebook.
    command:
        Code quality tool.

    Returns
    -------
    str
        stdout with substitution applied.
    str
        stderr with substitution applied.
    """
    if command == "doctest":
        pattern = rf'(?<=^File "{re.escape(str(notebook))}",) line'
        out = re.sub(pattern, "", out, flags=re.MULTILINE)
        err = re.sub(pattern, "", err, flags=re.MULTILINE)
    return out, err


def map_python_line_to_nb_lines(
    command: str, out: str, err: str, notebook: Path, cell_mapping: Mapping[int, str]
) -> Tuple[str, str]:
    """
    Make sure stdout and stderr make reference to Jupyter Notebook cells and lines.

    Parameters
    ----------
    command
        Code quality tool.
    out
        Captured stdout from third-party tool.
    err
        Captured stdout from third-party tool.
    notebook
        Original Jupyter notebook.
    cell_mapping
        Mapping from Python file lines to Jupyter notebook cells.

    Returns
    -------
    str
        Stdout with references to temporary Python file's lines replaced with references
        to notebook's cells and lines.
    str
        Stderr with references to temporary Python file's lines replaced with references
        to notebook's cells and lines.
    """

    def substitution(match: Match[str]) -> str:
        """Replace Python line with corresponding Jupyter notebook cell."""
        return str(cell_mapping[int(match.group())])

    pattern = _get_pattern(notebook, command)
    out = re.sub(pattern, substitution, out, flags=re.MULTILINE)
    err = re.sub(pattern, substitution, err, flags=re.MULTILINE)

    out, err = _extra_substitution(out, err, notebook, command)

    return out, err
