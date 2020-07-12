import json
import subprocess


def main(python_file, notebook):
    with open(notebook, "r") as handle:
        nb = handle.read()

    subprocess.run(["ipynb-py-convert", python_file, notebook])

    with open(notebook, "r") as handle:
        new_sources = json.loads(handle.read())["cells"]
    notebook_json = json.loads(nb)
    new_cells = [
        {
            **{key: val for key, val in i.items() if i != "source"},
            **{"source": new_sources[n]["source"]},
        }
        for n, i in enumerate(notebook_json["cells"])
    ]
    notebook_json.update({"cells": new_cells})
    with open(notebook, "w") as handle:
        json.dump(notebook_json, handle, indent=1, ensure_ascii=False)
        handle.write("\n")
