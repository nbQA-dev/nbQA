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
        Found 3 errors in 3 files (checked 26 source files)
        """  # noqa
    )
    expected_out = (
        'tests/data/notebook_starting_with_md.ipynb:cell_3:18: \x1b[1m\x1b[31merror:\x1b(B\x1b[m Argument 1 to \x1b(B\x1b[m\x1b[1m"hello"\x1b(B\x1b[m has incompatible type \x1b(B\x1b[m\x1b[1m"int"\x1b(B\x1b[m; expected \x1b(B\x1b[m\x1b[1m"str"\x1b(B\x1b[m\x1b(B\x1b[m\n'  # noqa: E501
        'tests/data/notebook_for_testing_copy.ipynb:cell_2:18: \x1b[1m\x1b[31merror:\x1b(B\x1b[m Argument 1 to \x1b(B\x1b[m\x1b[1m"hello"\x1b(B\x1b[m has incompatible type \x1b(B\x1b[m\x1b[1m"int"\x1b(B\x1b[m; expected \x1b(B\x1b[m\x1b[1m"str"\x1b(B\x1b[m\x1b(B\x1b[m\n'  # noqa: E501
        'tests/data/notebook_for_testing.ipynb:cell_2:19: \x1b[1m\x1b[31merror:\x1b(B\x1b[m Argument 1 to \x1b(B\x1b[m\x1b[1m"hello"\x1b(B\x1b[m has incompatible type \x1b(B\x1b[m\x1b[1m"int"\x1b(B\x1b[m; expected \x1b(B\x1b[m\x1b[1m"str"\x1b(B\x1b[m\x1b(B\x1b[m\n'  # noqa: E501
        "\x1b[1m\x1b[31mFound 3 errors in 3 files (checked 26 source files)\x1b(B\x1b[m\n"
    )
    assert out == expected_out
    assert err == ""


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
    expected = "\x1b[1m\x1b[32mSuccess: no issues found in 1 source file\x1b(B\x1b[m\n"
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
    expected = "\x1b[1m\x1b[32mSuccess: no issues found in 1 source file\x1b(B\x1b[m\n"
    assert result == expected
