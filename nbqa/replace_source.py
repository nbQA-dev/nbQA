"""
Replace :code:`source` code cells of original notebook with ones from converted file.

The converted file will have had the third-party tool run against it by now.
"""

import json
from typing import TYPE_CHECKING, Dict, List

from nbqa.save_source import CODE_SEPARATOR

if TYPE_CHECKING:
    from pathlib import Path


def main(
    python_file: "Path",
    notebook: "Path",
    trailing_semicolons: List[int],
    temporary_lines: Dict[str, str],
) -> None:
    """
    Replace :code:`source` code cells of original notebook.

    Parameters
    ----------
    python_file
        Temporary Python file notebook was converted to.
    notebook
        Jupyter Notebook third-party tool is run against (unmodified).
    trailing_semicolons
        Cells which originally had trailing semicolons.
    temporary_lines
        Mapping from temporary lines to original lines.
    """
    with open(notebook) as handle:
        notebook_json = json.load(handle)

    with open(str(python_file)) as handle:
        pyfile = handle.read()

    pycells = pyfile[len(CODE_SEPARATOR) :].split(CODE_SEPARATOR)

    def _reinstate_magics(
        source: str,
        trailing_semicolons: List[int],
        cell_number: int,
        temporary_lines: Dict[str, str],
    ) -> List[str]:
        """
        Put (commented-out) magics back in.

        Parameters
        ----------
        source
            Portion of Python file between cell separators.
        trailing_semicolons
            List of cells which originally had trailing semicolons.
        cell_number
            Number of current cell.
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
        # we take [1:] because the first cell is just '\n'
        for key, val in temporary_lines.items():
            source = source.replace(key, val)
        return "\n{}".format(source.strip("\n")).splitlines(True)[1:]

    new_sources = (
        {
            "source": _reinstate_magics(i, trailing_semicolons, n, temporary_lines),
            "cell_type": "code",
        }
        for n, i in enumerate(pycells)
    )

    new_cells = []
    for i in notebook_json["cells"]:
        if i["cell_type"] == "markdown":
            new_cells.append(i)
            continue
        i["source"] = next(new_sources)["source"]
        new_cells.append(i)

    notebook_json.update({"cells": new_cells})
    with open(notebook, "w") as handle:
        json.dump(notebook_json, handle, indent=1, ensure_ascii=False)
        handle.write("\n")
