import difflib
import os
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from nbqa.__main__ import main

if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture


def test_nbqa_ini_works(
    tmp_notebook_for_testing: Path, capsys: "CaptureFixture"
) -> None:
    """
    Check .nbqa.ini config is picked up works.

    Parameters
    ----------
    tmp_notebook_for_testing
        Temporary copy of :code:`notebook_for_testing.ipynb`.
    capsys
        Pytest fixture to capture stdout and stderr.
    """
    with open(".nbqa.ini", "w") as f:
        f.write("[flake8]\nignore=F401\nselect=E303\nquiet\n")

    # check diff
    with open(tmp_notebook_for_testing, "r") as handle:
        before = handle.readlines()
    with pytest.raises(SystemExit):
        main(["flake8", ".", "--ignore", "E302"])

    Path(".nbqa.ini").unlink()

    with open(tmp_notebook_for_testing, "r") as handle:
        after = handle.readlines()
    result = "".join(difflib.unified_diff(before, after))
    expected = ""
    assert result == expected

    # check out and err
    out, err = capsys.readouterr()
    expected_out = f"{os.path.abspath(os.path.join('tests', 'data', 'notebook_starting_with_md.ipynb'))}\n"
    expected_err = ""
    assert sorted(out.splitlines()) == sorted(expected_out.splitlines())
    assert sorted(err.splitlines()) == sorted(expected_err.splitlines())
