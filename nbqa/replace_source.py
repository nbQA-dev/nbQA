"""
Replace :code:`source` code cells of original notebook with ones from converted file.

The converted file will have had the third-party tool run against it by now.
"""

import json
from typing import TYPE_CHECKING, Iterator, List, Mapping, Set

from nbqa.notebook_info import NotebookInfo
from nbqa.save_source import CODE_SEPARATOR

if TYPE_CHECKING:
    from pathlib import Path


def _reinstate_magics(
    source: str,
    cell_number: int,
    trailing_semicolons: Set[int],
    temporary_lines: Mapping[str, str],
) -> List[str]:
    """
    Put (preprocessed) line magics back in.

    Parameters
    ----------
    source
        Portion of Python file between cell separators.
    cell_number
        Number of current cell.
    trailing_semicolons
        List of cells which originally had trailing semicolons.
    temporary_lines
        Mapping from temporary lines to original lines.

    Returns
    -------
    List[str]
        New source that can be saved into Jupyter Notebook.
    """
    rstripped_source = source.rstrip()
    if cell_number in trailing_semicolons and not rstripped_source.endswith(";"):
        source = rstripped_source + ";"
    for key, val in temporary_lines.items():
        source = source.replace(key, val)
    # we take [1:] because the first cell is just '\n'
    return "\n{}".format(source.strip("\n")).splitlines(True)[1:]


def main(python_file: "Path", notebook: "Path", notebook_info: NotebookInfo) -> None:
    """
    Replace :code:`source` code cells of original notebook.

    Parameters
    ----------
    python_file
        Temporary Python file notebook was converted to.
    notebook
        Jupyter Notebook third-party tool is run against (unmodified).
    notebook_info
        Information about notebook cells used for processing
    """
    with open(notebook) as handle:
        notebook_json = json.load(handle)

    with open(str(python_file)) as handle:
        pyfile = handle.read()

    pycells: Iterator[str] = iter(pyfile[len(CODE_SEPARATOR) :].split(CODE_SEPARATOR))
    code_cell_number = 0
    new_cells = []
    for cell in notebook_json["cells"]:
        if cell["cell_type"] == "code":
            code_cell_number += 1
            if code_cell_number not in notebook_info.code_cells_to_ignore:
                cell["source"] = _reinstate_magics(
                    next(pycells),
                    code_cell_number,
                    notebook_info.trailing_semicolons,
                    notebook_info.temporary_lines,
                )

        new_cells.append(cell)

    notebook_json.update({"cells": new_cells})
    with open(notebook, "w") as handle:
        json.dump(notebook_json, handle, indent=1, ensure_ascii=False)
        handle.write("\n")
