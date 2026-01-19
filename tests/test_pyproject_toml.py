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
        dedent("""
            [tool.nbqa.addopts]
            flake8 = [
                "--ignore=F401,E302",
                "--select=E303",
            ]
            """),
        encoding="utf-8",
    )

    main(["flake8", "tests"])
    Path("pyproject.toml").unlink()

    out, _ = capsys.readouterr()
    expected_out = ""
    assert out == expected_out


def test_cli_extends_pyprojecttoml(capsys: "CaptureFixture") -> None:
    """
    Check CLI args overwrite pyproject.toml

    Parameters
    ----------
    capsys
        Pytest fixture to capture stdout and stderr.
    """
    Path("pyproject.toml").write_text(
        dedent("""
            [tool.nbqa.addopts]
            flake8 = [
                "--ignore=F401",
            ]
            """),
        encoding="utf-8",
    )

    main(
        [
            "flake8",
            os.path.join("tests", "data", "notebook_for_testing.ipynb"),
            "--ignore=E402,W291",
        ]
    )
    out, _ = capsys.readouterr()
    Path("pyproject.toml").unlink()

    # if arguments are specified on command line, they will take precedence
    # over those specified in the pyproject.toml
    notebook_path = os.path.join("tests", "data", "notebook_for_testing.ipynb")
    expected_out = dedent(f"""\
        {notebook_path}:cell_1:1:1: F401 'os' imported but unused
        {notebook_path}:cell_1:3:1: F401 'glob' imported but unused
        {notebook_path}:cell_1:5:1: F401 'nbqa' imported but unused
        {notebook_path}:cell_4:1:1: F401 'random.randint' imported but unused
        """)
    assert out == expected_out
