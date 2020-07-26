"""
Check that files end with the correct new-line separator.
"""

import os
import subprocess

DIRTY_NOTEBOOK = os.path.join("tests", "data", "notebook_for_testing.ipynb")


def test_last_line() -> None:
    """
    Check that files end with the correct new-line separator.
    """
    subprocess.run(["python", "-m", "nbqa", "flake8", DIRTY_NOTEBOOK])

    with open(DIRTY_NOTEBOOK, "r") as handle:
        last_line = handle.readlines()[-1]

    assert last_line == f"{str('}')}{os.linesep}"
