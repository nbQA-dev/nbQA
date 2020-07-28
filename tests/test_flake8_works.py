"""
Check :code:`flake8` works as intended.
"""

import difflib
import os
from textwrap import dedent
from typing import TYPE_CHECKING

import pytest

from nbqa.__main__ import main

if TYPE_CHECKING:
    from pathlib import Path

    from _pytest.capture import CaptureFixture


def test_flake8_works(
    tmp_notebook_for_testing: "Path", capsys: "CaptureFixture"
) -> None:
    """
    Check flake8 works. Shouldn't alter the notebook content.

    Parameters
    ----------
    tmp_notebook_for_testing
        Temporary copy of :code:`notebook_for_testing.ipynb`.
    capsys
        Pytest fixture to capture stdout and stderr.
    """
    # check out and err
    path_0 = os.path.abspath(
        os.path.join("tests", "data", "notebook_for_testing.ipynb")
    )
    path_1 = os.path.abspath(
        os.path.join("tests", "data", "notebook_for_testing_copy.ipynb")
    )
    path_2 = os.path.abspath(
        os.path.join("tests", "data", "notebook_starting_with_md.ipynb")
    )

    # check diff
    with open(tmp_notebook_for_testing, "r") as handle:
        before = handle.readlines()
    with pytest.raises(SystemExit):
        main(["flake8", path_0, path_1, path_2])

    with open(tmp_notebook_for_testing, "r") as handle:
        after = handle.readlines()
    result = "".join(difflib.unified_diff(before, after))
    expected = ""
    assert result == expected

    out, err = capsys.readouterr()
    expected_out = dedent(
        f"""\
        {path_0}:cell_1:1:1: F401 'os' imported but unused
        {path_0}:cell_1:3:1: F401 'glob' imported but unused
        {path_0}:cell_1:5:1: F401 'nbqa' imported but unused
        {path_1}:cell_1:1:1: F401 'os' imported but unused
        {path_1}:cell_1:3:1: F401 'glob' imported but unused
        {path_1}:cell_1:5:1: F401 'nbqa' imported but unused
        {path_2}:cell_1:1:1: F401 'os' imported but unused
        {path_2}:cell_1:3:1: F401 'glob' imported but unused
        {path_2}:cell_1:5:1: F401 'nbqa' imported but unused
        {path_2}:cell_3:0:1: E303 too many blank lines (3)
        {path_2}:cell_3:2:1: E302 expected 2 blank lines, found 3
        """
    )
    expected_err = ""
    assert sorted(out.splitlines()) == sorted(expected_out.splitlines())
    assert sorted(err.splitlines()) == sorted(expected_err.splitlines())
