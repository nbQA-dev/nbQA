"""Comment-out magic IPython lines from converted notebook."""

import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: nocover
    from pathlib import Path


def main(temp_python_file: "Path") -> None:
    """
    Temporarily comment-out "magic" IPython lines (e.g. :code:`%%timeit`).

    Parameters
    ----------
    temp_python_file
        Temporary Python file notebook was converted to.
    """
    with open(str(temp_python_file), "r") as handle:
        file = handle.read()

    # line magics
    file = re.sub(r"(?<!%)(%\w+)", r"# \1", file)
    # cell magics
    file = re.sub(r"(%%\w+)", r"# \1", file)

    with open(str(temp_python_file), "w") as handle:
        handle.write(file)
