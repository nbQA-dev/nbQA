"""Check local config files are picked up by nbqa."""

from pathlib import Path
from textwrap import dedent
from typing import TYPE_CHECKING

from nbqa.__main__ import main

if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture


def test_configs_work(capsys: "CaptureFixture") -> None:
    """
    Check a flake8 cfg file is picked up by nbqa.

    Parameters
    ----------
    capsys
        Pytest fixture to capture stdout and stderr.
    """
    Path(".flake8").write_text(
        dedent(
            """\
            [flake8]
            ignore=F401
            select=E303
            quiet=1
            """
        )
    )

    main(["flake8", "tests", "--ignore", "E302"])

    Path(".flake8").unlink()

    # check out and err
    out, _ = capsys.readouterr()
    expected_out = ""
    assert out == expected_out
