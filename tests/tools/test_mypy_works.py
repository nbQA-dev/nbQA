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
    expected_out = dedent(
        """\
        has incompatible type
        has incompatible type
        has incompatible type
        """
    )
    # Unfortunately, the colours don't show up in CI. Seems to work fine locally though.
    # So, we can only do a partial test.
    for result, expected in zip(
        sorted(out.splitlines()[:-1]), sorted(expected_out.splitlines())
    ):
        assert expected in result
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
    expected = "Success: no issues found in 1 source file"
    assert expected in out


def test_notebook_doesnt_shadow_python_module(capsys: "CaptureFixture") -> None:
    """Check that notebook with same name as a Python file doesn't overshadow it."""
    cwd = os.getcwd()
    try:
        os.chdir(os.path.join("tests", "data"))
        main(["mypy", "t.ipynb"])
    finally:
        os.chdir(cwd)
    result, _ = capsys.readouterr()
    expected = "Success: no issues found in 1 source file"
    assert expected in result
