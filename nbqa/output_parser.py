"""Parse output from code quality tools."""
import os
import re
from functools import partial
from pathlib import Path
from typing import Callable, Mapping, Match, NamedTuple, Sequence, Tuple, Union


def _line_to_cell(match: Match[str], cell_mapping: Mapping[int, str]) -> str:
    """Replace Python line with corresponding Jupyter notebook cell."""
    return str(cell_mapping[int(match.group())])


class Output(NamedTuple):
    """Captured stdout and stderr."""

    out: str
    err: str


def _get_pattern(
    notebook: Path, command: str, cell_mapping: Mapping[int, str]
) -> Sequence[Tuple[str, Union[str, Callable[[Match[str]], str]]]]:
    """
    Get pattern and substitutions with which to process code quality tool's output.

    Parameters
    ----------
    notebook
        Notebook command is being run on.
    command
        Code quality tool.
    cell_mapping
        Mapping from Python file lines to Jupyter notebook cells.

    Returns
    -------
    List
        Patterns and substitutions for reported output.
    """
    standard_substitution = partial(_line_to_cell, cell_mapping=cell_mapping)

    if command == "black":
        return [
            (
                rf"(?<=^error: cannot format {re.escape(str(notebook))}: Cannot parse: )\d+",
                standard_substitution,
            ),
            (r"(?<=line )\d+(?=\)\nOh no! )", standard_substitution),
            (r"line cell_(?=\d+:\d+\)\nOh no! )", "cell_"),
        ]

    if command == "doctest":
        return [
            (
                rf'(?<=^File "{re.escape(os.path.abspath(str(notebook)))}", line )\d+',
                standard_substitution,
            ),
            (rf'(?<=^File "{re.escape(os.path.abspath(str(notebook)))}",) line', ""),
        ]

    # This is the most common one and is used by flake, pylint, mypy, and more.
    return [(rf"(?<=^{re.escape(str(notebook))}:)\d+", standard_substitution)]


def map_python_line_to_nb_lines(
    command: str, out: str, err: str, notebook: Path, cell_mapping: Mapping[int, str]
) -> Output:
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
    Output
        Stdout, stderr with references to temporary Python file's lines replaced with references
        to notebook's cells and lines.
    """
    patterns = _get_pattern(notebook, command, cell_mapping)
    for pattern_, substitution_ in patterns:
        out = re.sub(pattern_, substitution_, out, flags=re.MULTILINE)
        err = re.sub(pattern_, substitution_, err, flags=re.MULTILINE)

    return Output(out, err)
