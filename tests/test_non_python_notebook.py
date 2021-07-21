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
    main(["black", path, "--nbqa-diff"])
    out, _ = capsys.readouterr()
    expected_out = ""
    assert out == expected_out
