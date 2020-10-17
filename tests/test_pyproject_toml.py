"""Check configs from :code:`pyproject.toml` are picked up."""

from pathlib import Path
from textwrap import dedent
from typing import TYPE_CHECKING

import pytest

from nbqa.__main__ import main

if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture


def test_pyproject_toml_works(
    temporarily_delete_pyprojecttoml: Path, capsys: "CaptureFixture"
) -> None:
    """
    Check if config is picked up from pyproject.toml works.

    Parameters
    ----------
    capsys
        Pytest fixture to capture stdout and stderr.
    """
    temporarily_delete_pyprojecttoml.write_text(
        dedent(
            """
            [tool.nbqa.addopts]
            flake8 = [
                "--ignore=F401",
                "--select=E303",
                "--quiet"
            ]
            """
        )
    )

    with pytest.raises(SystemExit):
        main(["flake8", "tests", "--ignore", "E302"])

    temporarily_delete_pyprojecttoml.unlink()

    # check out and err
    out, _ = capsys.readouterr()
    expected_out = ""
    assert out == expected_out
