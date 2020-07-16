import json
import tempfile
from pathlib import Path

CODE_SEPARATOR = "\n\n# %%\n"

MARKDOWN_SEPARATOR = "\n\n# %% [markdown]\n"


def main(path, tmpdir):

    with open(path, "r") as handle:
        notebook = json.load(handle)

    cells = notebook["cells"]

    result = [
        f"{CODE_SEPARATOR}{''.join(i['source'])}\n"
        if i["cell_type"] == "code"
        else f"{MARKDOWN_SEPARATOR}{''.join(i['source'])}\n"
        for i in cells
    ]

    # make filename from path and tmpdir
    temp_file = Path(tmpdir).joinpath(path.stem).with_suffix('.py')
    with open(str(temp_file), "w") as handle:
        handle.write("".join(result)[len("\n\n") : -len("\n")])

    return temp_file
