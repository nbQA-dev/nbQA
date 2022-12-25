"""Check mdformat works."""

import os
from typing import TYPE_CHECKING

from nbqa.__main__ import main

if TYPE_CHECKING:

    from _pytest.capture import CaptureFixture


def test_mdformat_works_with_empty_file(capsys: "CaptureFixture") -> None:
    """
    Check mdformat works with empty notebook.

    Parameters
    ----------
    capsys
        Pytest fixture to capture stdout and stderr.
    """
    path = os.path.abspath(os.path.join("tests", "data", "footer.ipynb"))

    main(["mdformat", path, "--nbqa-diff", "--nbqa-md"])

    out, err = capsys.readouterr()
    assert out == "Notebook(s) would be left unchanged\n"
    assert err == ""
