"""Check mdformat works."""

import difflib
import os
from pathlib import Path
from typing import TYPE_CHECKING

from nbqa.__main__ import main

if TYPE_CHECKING:

    from _pytest.capture import CaptureFixture


def test_mdformat(tmp_notebook_for_testing: Path) -> None:
    """Check mdformat works"""
    with open(tmp_notebook_for_testing, encoding="utf-8") as handle:
        before = handle.readlines()
    path = os.path.join("tests", "data", "notebook_for_testing.ipynb")

    main(["mdformat", os.path.abspath(path), "--nbqa-md"])
    with open(tmp_notebook_for_testing, encoding="utf-8") as handle:
        after = handle.readlines()

    diff = difflib.unified_diff(before, after)
    result = "".join(i for i in diff if any([i.startswith("+ "), i.startswith("- ")]))
    expected = (
        '-    "First level heading\\n",\n-    "==="\n+    "# First level heading"\n'
    )
    assert result == expected


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
