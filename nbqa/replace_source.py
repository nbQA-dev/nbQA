import json


def _parse_python_cell(cell):
    source = cell.splitlines(True)
    if source[0] == "\n":
        return {"source": source[1:], "cell_type": "code"}
    return {"source": source[1:], "cell_type": "markdown"}


def main(python_file, notebook):
    with open(notebook, "r") as handle:
        notebook_json = json.load(handle)

    with open(str(python_file), "r") as handle:
        pyfile = handle.read()

    pycells = pyfile[len("# %%") :].split("\n\n\n# %%")

    new_sources = (_parse_python_cell(i) for i in pycells)

    new_cells = [
        {
            **{key: val for key, val in i.items() if i != "source"},
            **{"source": j["source"]},
        }
        for n, (i, j) in enumerate(zip(notebook_json["cells"], new_sources))
    ]
    notebook_json.update({"cells": new_cells})
    with open(notebook, "w") as handle:
        json.dump(notebook_json, handle, indent=1, ensure_ascii=False)
        handle.write("\n")
