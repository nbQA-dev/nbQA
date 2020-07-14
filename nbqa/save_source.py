import json
import tempfile

CODE_SEPARATOR = "\n\n# %%\n"

MARKDOWN_SEPARATOR = "\n\n# %% [markdown]\n"


def main(path):

    _, filename = tempfile.mkstemp(suffix=".py")

    with open(path, "r") as handel:
        notebook = json.load(handel)

    cells = notebook["cells"]

    result = [
        f"{CODE_SEPARATOR}{''.join(i['source'])}\n"
        if i["cell_type"] == "code"
        else f"{MARKDOWN_SEPARATOR}{''.join(i['source'])}\n"
        for i in cells
    ]

    with open(filename, "w") as handle:
        handle.write("".join(result)[len("\n\n") : -len("\n")])

    return filename
