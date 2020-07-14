import json


def main(python_file, notebook):
    with open(notebook, "r") as handle:
        notebook_json = json.load(handle)

    with open(python_file, "r") as handle:
        pyfile = handle.read()

    pycells = pyfile[len("# %%") :].split("\n\n\n# %%")

    new_sources = []
    for i in pycells:
        cells = i.splitlines(True)
        if cells[0] == "\n":
            new_sources.append({"source": cells[1:], "cell_type": "code"})
        else:
            new_sources.append({"source": cells[1:], "cell_type": "markdown"})

    new_sources = [
        {
            **{key: val for key, val in i.items() if i != "source"},
            **{"source": new_sources[n]["source"]},
        }
        for n, i in enumerate(notebook_json["cells"])
    ]
    notebook_json.update({"cells": new_sources})
    with open(notebook, "w") as handle:
        json.dump(notebook_json, handle, indent=1, ensure_ascii=False)
        handle.write("\n")
