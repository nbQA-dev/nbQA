"""
Extract code cells from notebook and save them to temporary Python file.

Markdown cells, output, and metadata are ignored.
"""

import json
from collections import defaultdict
from typing import TYPE_CHECKING, Dict, Iterator, List, Optional, Tuple

if TYPE_CHECKING:
    from pathlib import Path

CODE_SEPARATOR = "# %%"
MAGIC_SEPARATOR = "# NBQAMAGIC"
BLANK_SPACES = defaultdict(lambda: "\n\n")
BLANK_SPACES["isort"] = "\n"
MAGIC = ["%%script", "%%bash"]


def _replace_magics(source: List[str], ignore_cells: Optional[str]) -> Iterator[str]:
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
    if ignore_cells is not None:
        ignore = MAGIC + [i.strip() for i in ignore_cells.split(",")]
    else:
        ignore = MAGIC
    ignore_cell = source and any(source[0].lstrip().startswith(i) for i in ignore)
    for j in source:
        if (j.lstrip().startswith("!") or j.lstrip().startswith("%")) or ignore_cell:
            yield f"{MAGIC_SEPARATOR}{j}"
        else:
            yield j


def main(
    notebook: "Path",
    temp_python_file: "Path",
    command: str,
    ignore_cells: Optional[str],
) -> Tuple[Dict[int, str], List[int]]:
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
    """
    with open(notebook, "r") as handle:
        cells = json.load(handle)["cells"]

    result = []
    cell_mapping = {}
    line_number = 0
    cell_number = 0
    trailing_semicolons = []

    for i in cells:
        if i["cell_type"] != "code":
            continue
        source = _replace_magics(i["source"], ignore_cells)
        parsed_cell = f"{BLANK_SPACES[command]}{CODE_SEPARATOR}\n{''.join(source)}\n"
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

    return cell_mapping, trailing_semicolons
