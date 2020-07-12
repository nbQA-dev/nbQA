def main(path, dest):

    # with open(path, "r") as handle:
    #     notebook = handle.read()

    # with open(dest, "w") as handle:
    #     handle.write(
    #         "\n# magicseparator\n".join(
    #             ["#lineseparator".join(i["source"]) for i in json.loads(notebook)["cells"]]
    #         )
    #     )
    import os

    os.system(f"ipynb-py-convert {path} {dest}")
