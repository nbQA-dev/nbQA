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
    _, err = capsys.readouterr()
    expected_err = (
        "No valid Python notebooks found in given path(s)\n"
        "\x1b[1m\n"
        "If you believe the notebook(s) to be valid, please report a bug "
        "at https://github.com/nbQA-dev/nbQA/issues \x1b[0m\n"
        "\n"
    )
    assert err == expected_err
