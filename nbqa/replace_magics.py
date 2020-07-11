import re

import typer


def main(path):

    with open(path, "r") as handle:
        file = handle.read()

    file = re.sub(r"(%%\w+)", r"# \1", file)

    with open(path, "w") as handle:
        handle.write(file)


if __name__ == "__main__":
    typer.run(main)
