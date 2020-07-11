import json


def main(python_file, notebook):
    with open(notebook, "r") as handle:
        nb = handle.read()

    with open(python_file, "r") as handle:
        new_source = handle.read()
    new_sources = new_source.split("\n# magicseparator\n")

    notebook_json = json.loads(nb)
    new_cells = [
        {
            **{key: val for key, val in i.items() if i != "source"},
            **{"source": new_sources[n]},
        }
        for n, i in enumerate(notebook_json["cells"])
    ]
    notebook_json.update({"cells": new_cells})
    with open(notebook, "w") as handle:
        json.dump(notebook_json, handle, indent=2)
