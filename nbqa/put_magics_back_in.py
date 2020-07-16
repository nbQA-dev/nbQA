import re


def main(path):

    with open(str(path), "r") as handle:
        file = handle.read()

    file = re.sub(r"# (%%\w+)", r"\1", file)

    with open(str(path), "w") as handle:
        handle.write(file)
