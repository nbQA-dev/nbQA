"""Check that :code:`black` works as intended."""

import os
from typing import TYPE_CHECKING

import pytest

from nbqa.__main__ import main

if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture


def test_pylint_works(capsys: "CaptureFixture") -> None:
    """
    Check pylint works. Check all the warnings raised by pylint on the notebook.

    Parameters
    ----------
    capsys
        Pytest fixture to capture stdout and stderr.
    """
    # Pass one file with absolute path and the other one with relative path
    notebook1 = os.path.abspath(
        os.path.join("tests", "data", "notebook_for_testing.ipynb")
    )
    notebook2 = os.path.join("tests", "data", "notebook_with_indented_magics.ipynb")

    with pytest.raises(SystemExit):
        main(["pylint", notebook1, notebook2, "--disable=C0114"])

    notebook1_expected_warnings = [
        f"{str(notebook1)}:cell_2:19:8: C0303: Trailing whitespace (trailing-whitespace)",
        f"{str(notebook1)}:cell_1:1:0: W0611: Unused import os (unused-import)",
        f"{str(notebook1)}:cell_1:3:0: W0611: Unused import glob (unused-import)",
        f"{str(notebook1)}:cell_1:5:0: W0611: Unused import nbqa (unused-import)",
    ]

    notebook2_expected_warnings = [
        f'{str(notebook2)}:cell_2:1:0: C0413: Import "from random import randint"'
        + " should be placed at the top of the module (wrong-import-position)"
    ]

    # check out and err
    out, err = capsys.readouterr()

    # This is to ensure no additional warnings get generated apart
    # from the expected ones. This will also help to update the test when the
    # notebooks used for testing are modified later.
    assert out.count(rf"{str(notebook1)}:cell_") == 4
    assert out.count(rf"{str(notebook2)}:cell_") == 1

    assert all(warning in out for warning in notebook1_expected_warnings)
    assert all(warning in out for warning in notebook2_expected_warnings)

    assert err == ""
