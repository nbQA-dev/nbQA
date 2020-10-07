"""
Extract code cells from notebook and save them to temporary Python file.

Markdown cells, output, and metadata are ignored.
"""

import ast
import json
import secrets
from collections import defaultdict
from itertools import takewhile
from typing import TYPE_CHECKING, DefaultDict, Dict, Iterator, List, Optional, Tuple

from nbqa.handle_magics import get_magic_replacement, is_ipython_magic
from nbqa.notebook_info import NotebookInfo

if TYPE_CHECKING:
    from pathlib import Path

CODE_SEPARATOR = "# %%"
MAGIC = ["%%script", "%%bash"]


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
    source: List[str], line_magic: str, replacement_line: str
) -> Tuple[str, str]:
    """
    Handle the indentation of line magics. Remove unnecessary indentation.

    Parameters
    ----------
    source : List[str]
        Source code of the notebook cell
    line_magic : str
        Line magic present in the notebook cell
    replacement : str
        Replacement python code for the ipython magic
    Returns
    -------
    Tuple[str, str]
        Tuple of replacement line and the original line magic statement.
    """
    leading_space = "".join(takewhile(lambda c: c == " ", line_magic))

    # preserve the leading spaces and check if the syntax is valid
    replacement = f"{leading_space}{replacement_line}"

    if leading_space and not _is_src_code_indentation_valid(
        "".join(source + [replacement])
    ):
        # Remove the line magic indentation assuming these leading spaces
        # lead the source to have invalid indentation
        # Currently we don't check if the original source
        # code itself had IndentationError
        replacement = replacement_line
        line_magic = line_magic.lstrip()

    if line_magic.endswith("\n"):
        replacement += "\n"

    return replacement, line_magic


def _replace_line_magics(source: List[str]) -> Iterator[Tuple[str, Optional[str]]]:
    """
    Replace IPython line magics with valid python code.

    Parameters
    ----------
    source
        Source from notebook cell.

    Yields
    ------
    str
        Lines from cell, with line magics replaced with python code
    """
    for line_no, line in enumerate(source):
        trimmed_line: str = line.strip()
        if is_ipython_magic(trimmed_line):
            replacement_line = get_magic_replacement(trimmed_line, secrets.token_hex(3))
            yield _handle_magic_indentation(source[:line_no], line, replacement_line)
        else:
            yield line, None


def _parse_cell(
    source: List[str], cell_number: int, temporary_lines: Dict[int, Dict[str, str]]
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
        Mapping from placeholder python code to the original statement(line magic).

    Returns
    -------
    str
        Parsed cell.
    """
    parsed_cell = f"\n{CODE_SEPARATOR}\n"
    for new, old in _replace_line_magics(source):
        parsed_cell += new
        if old is not None:
            temporary_lines[cell_number][new] = old
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
    notebook: "Path",
    temp_python_file: "Path",
    ignore_cells: List[str],
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

    Returns
    -------
    NotebookInfo

    """
    with open(notebook) as handle:
        cells = json.load(handle)["cells"]

    result = []
    cell_mapping = {}
    line_number = 0
    cell_number = 0
    trailing_semicolons = set()
    temporary_lines: DefaultDict[int, Dict[str, str]] = defaultdict(dict)
    code_cells_to_ignore = set()

    for cell in cells:
        if cell["cell_type"] == "code":
            cell_number += 1

            if _should_ignore_code_cell(cell["source"], ignore_cells):
                code_cells_to_ignore.add(cell_number)
                continue

            parsed_cell = _parse_cell(cell["source"], cell_number, temporary_lines)
            result.append(parsed_cell)
            split_parsed_cell = parsed_cell.splitlines()
            cell_mapping.update(
                {
                    j + line_number + 1: f"cell_{cell_number}:{j}"
                    for j in range(len(split_parsed_cell))
                }
            )
            if parsed_cell.rstrip().endswith(";"):
                trailing_semicolons.add(cell_number)
            line_number += len(split_parsed_cell)

    with open(str(temp_python_file), "w") as handle:
        handle.write("".join(result)[len("\n") :])

    return NotebookInfo(
        cell_mapping, trailing_semicolons, temporary_lines, code_cells_to_ignore
    )
