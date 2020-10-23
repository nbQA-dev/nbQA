"""Check :code:`mypy` works as intended."""

import os
from textwrap import dedent
from typing import TYPE_CHECKING

import pytest

from nbqa.__main__ import main

if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture


def test_mypy_works(capsys: "CaptureFixture") -> None:
    """
    Check mypy works. Shouldn't alter the notebook content.

    Parameters
    ----------
    capsys
        Pytest fixture to capture stdout and stderr.
    """
    with pytest.raises(SystemExit):
        main(["mypy", "--ignore-missing-imports", "--allow-untyped-defs", "tests"])

    # check out and err
    out, err = capsys.readouterr()
    path_0 = os.path.join("tests", "data", "notebook_for_testing.ipynb")
    path_1 = os.path.join("tests", "data", "notebook_for_testing_copy.ipynb")
    path_2 = os.path.join("tests", "data", "notebook_starting_with_md.ipynb")
    expected_out = dedent(
        f"""\
        {path_2}:cell_3:18: error: Argument 1 to "hello" has incompatible type "int"; expected "str"
        {path_1}:cell_2:18: error: Argument 1 to "hello" has incompatible type "int"; expected "str"
        {path_0}:cell_2:19: error: Argument 1 to "hello" has incompatible type "int"; expected "str"
        Found 3 errors in 3 files (checked 15 source files)
        """  # noqa
    )
    expected_err = ""
    assert sorted(out.splitlines()) == sorted(expected_out.splitlines())
    assert sorted(err.splitlines()) == sorted(expected_err.splitlines())
