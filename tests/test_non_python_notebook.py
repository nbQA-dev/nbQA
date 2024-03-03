"""Test non-Python notebook."""

import os
from typing import TYPE_CHECKING

from nbqa.__main__ import main

if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture


def test_non_python_notebook(capsys: "CaptureFixture") -> None:
    """
    Should ignore non-Python notebook.

    Parameters
    ----------
    capsys
        Pytest fixture to capture stdout and stderr.
    """
    path = os.path.join("tests", "invalid_data", "non_python_notebook.ipynb")
    result = main(["black", path, "--nbqa-diff"])
    out, err = capsys.readouterr()
    assert out == ""
    assert err == "No valid Python notebooks found in given path(s)\n"
    assert result == 0
