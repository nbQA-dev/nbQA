"""Check :code:`mypy` works as intended."""

import os
from pathlib import Path
from textwrap import dedent
from typing import TYPE_CHECKING

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
    main(
        [
            "mypy",
            "--ignore-missing-imports",
            "--allow-untyped-defs",
            str(Path("tests") / "data"),
        ]
    )

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
        Found 3 errors in 3 files (checked 25 source files)
        """  # noqa
    )
    expected_err = ""
    assert sorted(out.splitlines()) == sorted(expected_out.splitlines())
    assert sorted(err.splitlines()) == sorted(expected_err.splitlines())


def test_mypy_with_local_import(capsys: "CaptureFixture") -> None:
    """
    Check mypy can find local import.

    Parameters
    ----------
    capsys
        Pytest fixture to capture stdout and stderr
    """
    main(
        [
            "mypy",
            str(Path("tests") / "data/notebook_with_local_import.ipynb"),
        ]
    )

    # check out and err
    out, _ = capsys.readouterr()
    expected = "Success: no issues found in 1 source file\n"
    assert out == expected


def test_notebook_doesnt_shadow_python_module(capsys: "CaptureFixture") -> None:
    """Check that notebook with same name as a Python file doesn't overshadow it."""
    cwd = os.getcwd()
    try:
        os.chdir(os.path.join("tests", "data"))
        main(["mypy", "t.ipynb"])
    finally:
        os.chdir(cwd)
    result, _ = capsys.readouterr()
    expected = "Success: no issues found in 1 source file\n"
    assert result == expected
