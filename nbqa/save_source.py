"""
Extract code cells from notebook and save them to temporary Python file.

Markdown cells, output, and metadata are ignored.
"""

import json
import secrets
from itertools import takewhile
from typing import TYPE_CHECKING, Dict, Iterator, List, Optional, Tuple

from nbqa.notebook_info import NotebookInfo

if TYPE_CHECKING:
    from pathlib import Path

CODE_SEPARATOR = "# %%"
MAGIC = ["%%script", "%%bash"]
IGNORE_LINE_REPLACEMENT = "pass  # nbqa"


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
    for line in source:
        if line.lstrip().startswith(("!", "%", "?")) or line.rstrip().endswith("?"):
            token = secrets.token_hex(3)
            # Replace line with `pass`.
            replacement = IGNORE_LINE_REPLACEMENT
            leading_space = "".join(takewhile(lambda c: c == " ", line))
            line_tokenised = f"{leading_space}{replacement}{token}"
            if line.endswith("\n"):
                line_tokenised += "\n"
            yield line_tokenised, line
        else:
            yield line, None


def _parse_cell(
    source: List[str],
    temporary_lines: Dict[str, str],
) -> str:
    """
    Parse cell, replacing line magics with python code as placeholder.

    Parameters
    ----------
    source
        Source from notebook cell.
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
            temporary_lines[new] = old
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
    temporary_lines: Dict[str, str] = {}
    code_cells_to_ignore = set()

    for cell in cells:
        if cell["cell_type"] == "code":
            cell_number += 1

            if _should_ignore_code_cell(cell["source"], ignore_cells):
                code_cells_to_ignore.add(cell_number)
                continue

            parsed_cell = _parse_cell(cell["source"], temporary_lines)
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
