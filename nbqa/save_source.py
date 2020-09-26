"""
Extract code cells from notebook and save them to temporary Python file.

Markdown cells, output, and metadata are ignored.
"""

import json
import secrets
from collections import defaultdict
from itertools import takewhile
from typing import TYPE_CHECKING, Dict, Iterator, List, Optional, Tuple

if TYPE_CHECKING:
    from pathlib import Path

CODE_SEPARATOR = "# %%"
BLANK_SPACES = defaultdict(lambda: "\n\n")
BLANK_SPACES["isort"] = "\n"
MAGIC = ["%%script", "%%bash"]
IGNORE_CELL_REPLACEMENT = "# nbqa"
IGNORE_LINE_REPLACEMENT = "pass  # nbqa"


def _replace_magics(
    source: List[str], ignore_cells: List[str]
) -> Iterator[Tuple[str, Optional[str]]]:
    """
    Comment out lines with magic commands.

    If it's a script/bash cell, comment out the entire cell.

    Parameters
    ----------
    source
        Source from notebook cell.
    ignore_cells
        Extra cells which nbqa should ignore.

    Yields
    ------
    str
        Line from cell, possibly commented out.
    """
    ignore = MAGIC + [i.strip() for i in ignore_cells]

    ignore_cell = source and any(source[0].lstrip().startswith(i) for i in ignore)
    for line in source:
        if (
            line.lstrip().startswith("!") or line.lstrip().startswith("%")
        ) or ignore_cell:
            token = secrets.token_hex(3)
            if ignore_cell:
                # Comment out entire cell.
                replacement = IGNORE_CELL_REPLACEMENT
                leading_space = ""
            else:
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
    command: str,
    ignore_cells: List[str],
    temporary_lines: Dict[str, str],
) -> str:
    """
    Parse cell, replacing magics with temporary lines.

    Parameters
    ----------
    source
        Source from notebook cell.
    command
        Third-party tool we're running.
    ignore_cells
        Extra cells which nbqa should ignore.
    temporary_lines
        Mapping from temporary lines to original lines.

    Returns
    -------
    str
        Parsed cell.
    """
    parsed_cell = f"{BLANK_SPACES[command]}{CODE_SEPARATOR}\n"
    for new, old in _replace_magics(source, ignore_cells):
        parsed_cell += new
        if old is not None:
            temporary_lines[new] = old
    parsed_cell += "\n"
    return parsed_cell


def main(
    notebook: "Path",
    temp_python_file: "Path",
    command: str,
    ignore_cells: List[str],
) -> Tuple[Dict[int, str], List[int], Dict[str, str]]:
    """
    Extract code cells from notebook and save them in temporary Python file.

    Parameters
    ----------
    notebook
        Jupyter Notebook third-party tool is being run against.
    temp_python_file
        Temporary Python file to save converted notebook in.
    command
        Third party tool which you're running on your notebook.
    ignore_cells
        Extra cells which nbqa should ignore.

    Returns
    -------
    cell_mapping
        Mapping from Python line numbers to Jupyter notebooks cells.
    trailing_semicolons
        Cell numbers where there were originally trailing semicolons.
    temporary_lines
        Mapping from temporary lines to original lines.
    """
    with open(notebook, "r") as handle:
        cells = json.load(handle)["cells"]

    result = []
    cell_mapping = {}
    line_number = 0
    cell_number = 0
    trailing_semicolons = []
    temporary_lines: Dict[str, str] = {}

    for i in cells:
        if i["cell_type"] != "code":
            continue
        parsed_cell = _parse_cell(i["source"], command, ignore_cells, temporary_lines)
        result.append(parsed_cell)
        split_parsed_cell = parsed_cell.splitlines()
        cell_mapping.update(
            {
                j + line_number + 1: f"cell_{cell_number+1}:{j}"
                for j in range(len(split_parsed_cell))
            }
        )
        if parsed_cell.rstrip().endswith(";"):
            trailing_semicolons.append(cell_number)
        line_number += len(split_parsed_cell)
        cell_number += 1

    with open(str(temp_python_file), "w") as handle:
        handle.write("".join(result)[len(BLANK_SPACES[command]) : -len("\n")])

    return cell_mapping, trailing_semicolons, temporary_lines
