"""Check configs from :code:`setup.cfg` are picked up."""

from pathlib import Path
from textwrap import dedent
from typing import TYPE_CHECKING

import pytest

from nbqa.__main__ import main

if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture


def test_nbqa_ini_works(capsys: "CaptureFixture") -> None:
    """
    Check setup.cfg config is picked up works.

    Parameters
    ----------
    capsys
        Pytest fixture to capture stdout and stderr.
    """
    Path("setup.cfg").write_text(
        dedent(
            """\
            [nbqa.addopts]
            flake8 = --ignore=F401 \
                      --select=E303 \
                      --quiet
            """
        )
    )

    with pytest.raises(SystemExit):
        main(["flake8", "tests", "--ignore", "E302"])

    Path("setup.cfg").unlink()

    # check out and err
    out, _ = capsys.readouterr()
    expected_out = ""
    assert out == expected_out
