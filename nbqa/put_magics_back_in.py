import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: nocover
    from pathlib import Path


def main(path: "Path") -> None:

    with open(str(path), "r") as handle:
        file = handle.read()

    file = re.sub(r"# (%%\w+)", r"\1", file)

    with open(str(path), "w") as handle:
        handle.write(file)
