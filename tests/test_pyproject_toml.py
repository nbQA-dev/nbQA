"""Check configs from :code:`pyproject.toml` are picked up."""

import os
from pathlib import Path
from textwrap import dedent
from typing import TYPE_CHECKING

from nbqa.__main__ import main

if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture


def test_pyproject_toml_works(capsys: "CaptureFixture") -> None:
    """
    Check if config is picked up from pyproject.toml works.

    Parameters
    ----------
    capsys
        Pytest fixture to capture stdout and stderr.
    """
    Path("pyproject.toml").write_text(
        dedent(
            """
            [tool.nbqa.addopts]
            flake8 = [
                "--ignore=F401,E302",
                "--select=E303",
            ]
            """
        )
    )

    main(["flake8", "tests"])
    Path("pyproject.toml").unlink()

    out, _ = capsys.readouterr()
    expected_out = ""
    assert out == expected_out


def test_cli_overwrites_pyprojecttoml(capsys: "CaptureFixture") -> None:
    """
    Check CLI args overwrite pyproject.toml

    Parameters
    ----------
    capsys
        Pytest fixture to capture stdout and stderr.
    """
    Path("pyproject.toml").write_text(
        dedent(
            """
            [tool.nbqa.addopts]
            flake8 = [
                "--ignore=F401",
            ]
            """
        )
    )

    main(
        [
            "flake8",
            os.path.join("tests", "data", "notebook_for_testing.ipynb"),
            "--select=E303",
        ]
    )
    Path("pyproject.toml").unlink()

    out, _ = capsys.readouterr()
    expected_out = ""
    assert out == expected_out
