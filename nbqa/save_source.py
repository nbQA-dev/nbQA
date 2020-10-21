"""
Extract code cells from notebook and save them to temporary Python file.

Markdown cells, output, and metadata are ignored.
"""

import ast
import json
import re
from collections import defaultdict
from itertools import takewhile
from typing import TYPE_CHECKING, DefaultDict, Dict, Iterator, List

from nbqa.handle_magics import MagicHandler, MagicSubstitution
from nbqa.notebook_info import NotebookInfo

if TYPE_CHECKING:
    from pathlib import Path

CODE_SEPARATOR = "# %%"
MAGIC = [
    "%%bash",
    "%%cython",
    "%%html",
    "%%javascript",
    "%%js",
    "%%latex",
    "%%markdown",
    "%%perl",
    "%%python2",
    "%%ruby",
    "%%script",
    "%%sh",
    "%%svg",
    "%%writefile",
]
NEWLINES = defaultdict(lambda: "\n\n")
NEWLINES["isort"] = "\n"


def _is_src_code_indentation_valid(source: str) -> bool:
    """
    Return True is the indentation of the input source code is valid.

    Parameters
    ----------
    source : str
        Source code present in the notebook cell

    Returns
    -------
    bool
        True if the source indentation is valid otherwise False
    """
    valid: bool = True
    try:
        ast.parse(source)
    except IndentationError:
        valid = False
    except SyntaxError:
        # Ignore any other exceptions. Let the syntax issues
        # be reported by the third party tool.
        pass

    return valid


def _handle_magic_indentation(
    source: List[str], line_magic: str, magic_replacement: MagicSubstitution
) -> str:
    """
    Handle the indentation of line magics. Remove unnecessary indentation.

    Parameters
    ----------
    source : List[str]
        Source code of the notebook cell
    line_magic : str
        Line magic present in the notebook cell
    magic_replacement : MagicSubstitution
        Object containing information on ipython magic replacement.
    Returns
    -------
    str
        Replacement line for the original line magic statement.
    """
    leading_space = "".join(takewhile(lambda c: c == " ", line_magic))

    # preserve the leading spaces and check if the syntax is valid
    replacement = magic_replacement.indent_magic_replacement(leading_space)

    if leading_space and not _is_src_code_indentation_valid(
        "".join(source + [replacement])
    ):
        # Remove the line magic indentation assuming these leading spaces
        # lead the source to have invalid indentation
        # Currently we don't check if the original source
        # code itself had IndentationError
        replacement = magic_replacement.replacement_line

    if line_magic.endswith("\n"):
        replacement += "\n"

    return replacement


def _replace_magics(
    source: List[str], magic_substitutions: List[MagicSubstitution]
) -> Iterator[str]:
    """
    Replace IPython line magics with valid python code.

    Parameters
    ----------
    source
        Source from notebook cell.
    magic_substitutions
        List to store all the ipython magics substitutions

    Yields
    ------
    str
        Line from cell, with line magics replaced with python code
    """
    for line_no, line in enumerate(source):
        trimmed_line: str = line.strip()
        if MagicHandler.is_ipython_magic(trimmed_line):
            magic_handler = MagicHandler.get_magic_handler(trimmed_line)
            magic_substitution = magic_handler.replace_magic(trimmed_line)
            magic_substitutions.append(magic_substitution)
            line = _handle_magic_indentation(source[:line_no], line, magic_substitution)

        yield line


def _parse_cell(
    source: List[str],
    cell_number: int,
    temporary_lines: Dict[int, List[MagicSubstitution]],
    command: str,
) -> str:
    """
    Parse cell, replacing line magics with python code as placeholder.

    Parameters
    ----------
    source
        Source from notebook cell.
    cell_number
        Number identifying the notebook cell.
    temporary_lines
        Mapping to store the cell number to all the ipython magics replaced in those cells.
    command
        The third-party tool being run.

    Returns
    -------
    str
        Parsed cell.
    """
    substituted_magics: List[MagicSubstitution] = []
    parsed_cell = f"{NEWLINES[command]}{CODE_SEPARATOR}\n"

    for parsed_line in _replace_magics(source, substituted_magics):
        parsed_cell += parsed_line

    if substituted_magics:
        temporary_lines[cell_number] = substituted_magics

    parsed_cell = parsed_cell.rstrip("\n") + "\n"
    return parsed_cell


def _should_ignore_code_cell(source: List[str], ignore_cells: List[str]) -> bool:
    """
    Return True if the current cell should be ignored from processing.

    Parameters
    ----------
    source : List[str]
        Source from the notebook cell
    ignore_cells : List[str]
        Extra cells which nbqa should ignore.

    Returns
    -------
    bool
        True if the cell should ignored else False
    """
    ignore = MAGIC + [i.strip() for i in ignore_cells]
    return source != [] and any(source[0].lstrip().startswith(i) for i in ignore)


def main(
    notebook: "Path", temp_python_file: "Path", ignore_cells: List[str], command: str
) -> NotebookInfo:
    """
    Extract code cells from notebook and save them in temporary Python file.

    Parameters
    ----------
    notebook
        Jupyter Notebook third-party tool is being run against.
    temp_python_file
        Temporary Python file to save converted notebook in.
    ignore_cells
        Extra cells which nbqa should ignore.
    command
        The third-party tool being run.

    Returns
    -------
    NotebookInfo

    """
    cells = json.loads(notebook.read_text())["cells"]

    result = []
    cell_mapping = {}
    line_number = 0
    cell_number = 0
    trailing_semicolons = set()
    temporary_lines: DefaultDict[int, List[MagicSubstitution]] = defaultdict(list)
    code_cells_to_ignore = set()

    for cell in cells:
        if cell["cell_type"] == "code":
            cell_number += 1

            if _should_ignore_code_cell(cell["source"], ignore_cells):
                code_cells_to_ignore.add(cell_number)
                continue

            parsed_cell = _parse_cell(
                cell["source"], cell_number, temporary_lines, command
            )
            cell_mapping.update(
                {
                    j + line_number + 1: f"cell_{cell_number}:{j}"
                    for j in range(len(parsed_cell.splitlines()))
                }
            )
            if parsed_cell.rstrip().endswith(";"):
                trailing_semicolons.add(cell_number)
            result.append(re.sub(r";(\s*)$", "\\1", parsed_cell))
            line_number += len(parsed_cell.splitlines())

    temp_python_file.write_text("".join(result).lstrip("\n"))

    return NotebookInfo(
        cell_mapping, trailing_semicolons, temporary_lines, code_cells_to_ignore
    )
