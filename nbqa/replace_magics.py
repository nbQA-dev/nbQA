"""Comment-out magic IPython lines from converted notebook."""

import fileinput
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


def main(temp_python_file: "Path") -> None:
    """
    Temporarily comment-out "magic" IPython lines (e.g. :code:`%%timeit`).

    Parameters
    ----------
    temp_python_file
        Temporary Python file notebook was converted to.
    """
    for i in fileinput.input(str(temp_python_file), inplace=True):
        if not (i.startswith("!") or i.startswith("%")):
            print(i, end="")
        else:
            print(f"# {i}", end="")
