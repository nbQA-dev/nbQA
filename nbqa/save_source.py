"""
Extract code cells from notebook and save them to temporary Python file.

Markdown cells, output, and metadata are ignored.
"""

import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

CODE_SEPARATOR = "\n\n# %%\n"


def main(notebook: "Path", temp_python_file: "Path") -> None:
    """
    Extract code cells from notebook and save them in temporary Python file.

    Parameters
    ----------
    notebook
        Jupyter Notebook third-party tool is being run against.
    temp_python_file
        Temporary Python file to save converted notebook in.
    """
    with open(notebook, "r") as handle:
        parsed_notebook = json.load(handle)

    cells = parsed_notebook["cells"]

    result = []
    mapping = {}
    total = 0
    code_cells = 0
    for i in cells:
        if i['cell_type'] != 'code':
            continue
        parsed_cell = f"{CODE_SEPARATOR}{''.join(i['source'])}\n"
        result.append(parsed_cell)
        split_parsed_cell = parsed_cell.split('\n')
        mapping.update({j+total+1: f"cell_{code_cells+1}:{j}" for j in range(len(split_parsed_cell)-1)})
        total += len(split_parsed_cell)-1
        code_cells += 1
        breakpoint()

    with open(str(temp_python_file), "w") as handle:
        handle.write("".join(result)[len("\n\n") : -len("\n")])

    return mapping
