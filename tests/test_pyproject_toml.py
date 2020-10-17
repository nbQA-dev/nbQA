"""Check configs from :code:`pyproject.toml` are picked up."""

from pathlib import Path
from textwrap import dedent
from typing import TYPE_CHECKING

import pytest

from nbqa.__main__ import main

if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture


def test_pyproject_toml_works(
    tmp_pyprojecttoml: Path, capsys: "CaptureFixture"
) -> None:
    """
    Check if config is picked up from pyproject.toml works.

    Parameters
    ----------
    tmp_pyprojecttoml
        Temporary pyproject.toml file.
    capsys
        Pytest fixture to capture stdout and stderr.
    """
    tmp_pyprojecttoml.write_text(
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

    tmp_pyprojecttoml.unlink()

    # check out and err
    out, _ = capsys.readouterr()
    expected_out = ""
    assert out == expected_out
