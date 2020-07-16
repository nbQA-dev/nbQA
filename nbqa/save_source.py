import json

CODE_SEPARATOR = "\n\n# %%\n"

MARKDOWN_SEPARATOR = "\n\n# %% [markdown]\n"


def main(path, temp_file):

    with open(path, "r") as handle:
        notebook = json.load(handle)

    cells = notebook["cells"]

    result = [
        f"{CODE_SEPARATOR}{''.join(i['source'])}\n"
        if i["cell_type"] == "code"
        else f"{MARKDOWN_SEPARATOR}{''.join(i['source'])}\n"
        for i in cells
        if i["cell_type"] == "code"
    ]

    with open(str(temp_file), "w") as handle:
        handle.write("".join(result)[len("\n\n") : -len("\n")])
