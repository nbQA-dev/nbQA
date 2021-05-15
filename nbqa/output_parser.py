"""Parse output from code quality tools."""
import re
from functools import partial
from typing import Callable, Mapping, Match, NamedTuple, Sequence, Tuple, Union

from nbqa.path_utils import get_relative_and_absolute_paths


def _line_to_cell(match: Match[str], cell_mapping: Mapping[int, str]) -> str:
    """Replace Python line with corresponding Jupyter notebook cell."""
    return str(cell_mapping[int(match.group())])


class Output(NamedTuple):
    """Captured stdout and stderr."""

    out: str
    err: str


def _get_pattern(
    notebook: str, command: str, cell_mapping: Mapping[int, str]
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

    relative_path, absolute_path = get_relative_and_absolute_paths(notebook)

    if command == "black":
        return [
            (
                rf"(?<=^error: cannot format {re.escape(relative_path)}: Cannot parse: )\d+"
                rf"|(?<=^error: cannot format {re.escape(absolute_path)}: Cannot parse: )\d+",
                standard_substitution,
            ),
            (r"(?<=line )\d+(?=\)\nOh no! )", standard_substitution),
            (r"line cell_(?=\d+:\d+\)\nOh no! )", "cell_"),
        ]

    if command == "doctest":
        return [
            (
                rf'(?<=^File "{re.escape(relative_path)}", line )\d+'
                rf'|(?<=^File "{re.escape(absolute_path)}", line )\d+',
                standard_substitution,
            ),
            (
                rf'(?<=^File "{re.escape(relative_path)}",) line'
                rf'|(?<=^File "{re.escape(absolute_path)}",) line',
                "",
            ),
        ]

    # This is the most common one and is used by flake, pylint, mypy, and more.
    return [
        (
            rf"(?<=^{re.escape(absolute_path)}:)\d+"
            rf"|(?<=^{re.escape(relative_path)}:)\d+",
            standard_substitution,
        )
    ]


def map_python_line_to_nb_lines(
    command: str, out: str, err: str, notebook: str, cell_mapping: Mapping[int, str]
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
        try:
            out = re.sub(pattern_, substitution_, out, flags=re.MULTILINE)
        except KeyError:
            pass
        try:
            err = re.sub(pattern_, substitution_, err, flags=re.MULTILINE)
        except KeyError:  # pragma: nocover (defensive check)
            pass

    return Output(out, err)
