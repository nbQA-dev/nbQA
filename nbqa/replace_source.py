"""
Replace :code:`source` code cells of original notebook with ones from converted file.

The converted file will have had the third-party tool run against it by now.
"""

import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


def main(python_file: "Path", notebook: "Path") -> None:
    """
    Replace :code:`source` code cells of original notebook.

    Parameters
    ----------
    python_file
        Temporary Python file notebook was converted to.
    notebook
        Jupyter Notebook third-party tool is run against (unmodified).
    """
    with open(notebook, "r") as handle:
        notebook_json = json.load(handle)

    with open(str(python_file), "r") as handle:
        pyfile = handle.read()

    pycells = pyfile[len("# %%") :].split("\n\n\n# %%")

    # we take [1:] because the first cell is just '\n'
    new_sources = (
        {"source": i.splitlines(True)[1:], "cell_type": "code"} for i in pycells
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
