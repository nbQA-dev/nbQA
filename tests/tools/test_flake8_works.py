"""Check :code:`flake8` works as intended."""

import os
from textwrap import dedent
from typing import TYPE_CHECKING

import pytest

from nbqa.__main__ import main

if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture


def test_flake8_works(capsys: "CaptureFixture") -> None:
    """
    Check flake8 works. Shouldn't alter the notebook content.

    Parameters
    ----------
    capsys
        Pytest fixture to capture stdout and stderr.
    """
    # check passing both absolute and relative paths
    path_0 = os.path.join("tests", "data", "notebook_for_testing.ipynb")
    path_1 = os.path.join("tests", "data", "notebook_for_testing_copy.ipynb")
    path_2 = os.path.abspath(
        os.path.join("tests", "data", "notebook_starting_with_md.ipynb")
    )

    with pytest.raises(SystemExit):
        main(["flake8", path_0, path_1, path_2])

    out, err = capsys.readouterr()
    expected_out = dedent(
        f"""\
        {path_0}:cell_1:1:1: F401 'os' imported but unused
        {path_0}:cell_1:3:1: F401 'glob' imported but unused
        {path_0}:cell_1:5:1: F401 'nbqa' imported but unused
        {path_0}:cell_2:19:9: W291 trailing whitespace
        {path_1}:cell_1:1:1: F401 'os' imported but unused
        {path_1}:cell_1:3:1: F401 'glob' imported but unused
        {path_1}:cell_1:5:1: F401 'nbqa' imported but unused
        {path_2}:cell_1:1:1: F401 'os' imported but unused
        {path_2}:cell_1:3:1: F401 'glob' imported but unused
        {path_2}:cell_1:5:1: F401 'nbqa' imported but unused
        {path_2}:cell_3:2:1: E302 expected 2 blank lines, found 0
        """
    )
    expected_err = ""
    assert sorted(out.splitlines()) == sorted(expected_out.splitlines())
    assert sorted(err.splitlines()) == sorted(expected_err.splitlines())
