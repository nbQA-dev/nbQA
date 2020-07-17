import json


def main(python_file, notebook):
    """
    Replace `source` of original notebook.
    """
    with open(notebook, "r") as handle:
        notebook_json = json.load(handle)

    with open(str(python_file), "r") as handle:
        pyfile = handle.read()

    pycells = pyfile[len("# %%") :].split("\n\n\n# %%")

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
