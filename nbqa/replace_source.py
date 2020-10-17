"""
Replace :code:`source` code cells of original notebook with ones from converted file.

The converted file will have had the third-party tool run against it by now.
"""

import json
from typing import TYPE_CHECKING, Iterator, List, Set

from nbqa.handle_magics import MagicSubstitution
from nbqa.notebook_info import NotebookInfo
from nbqa.save_source import CODE_SEPARATOR

if TYPE_CHECKING:
    from pathlib import Path


def _restore_semicolon(
    source: str,
    cell_number: int,
    trailing_semicolons: Set[int],
) -> str:
    """
    Restore the semicolon at the end of the cell.

    Restore the trailing semicolon if the cell originally contained semicolon
    and the third party tool removed it.

    Parameters
    ----------
    source
        Portion of Python file between cell separators.
    cell_number
        Number of current cell.
    trailing_semicolons
        List of cells which originally had trailing semicolons.

    Returns
    -------
    str
        New source with removed semicolon restored.
    """
    rstripped_source = source.rstrip()
    if cell_number in trailing_semicolons and not rstripped_source.endswith(";"):
        source = rstripped_source + ";"

    return source


def _reinstate_magics(
    source: str,
    temporary_lines: List[MagicSubstitution],
) -> List[str]:
    """
    Put (preprocessed) line magics back in.

    Parameters
    ----------
    source
        Portion of Python file between cell separators.
    temporary_lines
        Mapping from temporary magic substitutions to original ipython magics

    Returns
    -------
    List[str]
        New source that can be saved into Jupyter Notebook.
    """
    for magic_substitution in temporary_lines:
        source = magic_substitution.restore_magic(source)
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
    notebook_json = json.loads(notebook.read_text())

    pyfile = python_file.read_text()

    pycells: Iterator[str] = iter(pyfile[len(CODE_SEPARATOR) :].split(CODE_SEPARATOR))
    code_cell_number = 0
    new_cells = []
    for cell in notebook_json["cells"]:
        if cell["cell_type"] == "code":
            code_cell_number += 1
            if code_cell_number not in notebook_info.code_cells_to_ignore:
                source = _restore_semicolon(
                    next(pycells), code_cell_number, notebook_info.trailing_semicolons
                )
                cell["source"] = _reinstate_magics(
                    source,
                    notebook_info.temporary_lines.get(code_cell_number, []),
                )

        new_cells.append(cell)

    notebook_json.update({"cells": new_cells})
    notebook.write_text(f"{json.dumps(notebook_json, indent=1, ensure_ascii=False)}\n")
