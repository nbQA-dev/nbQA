"""Check local config files are picked up by nbqa."""

import re
from pathlib import Path
from textwrap import dedent
from typing import TYPE_CHECKING

import pytest

from nbqa.__main__ import main

if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture


CLEAN_NOTEBOOK = Path("tests") / "data/clean_notebook.ipynb"


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

    with pytest.raises(SystemExit):
        main(["flake8", "tests", "--ignore", "E302", "--nbqa-config", ".flake8"])

    Path(".flake8").unlink()

    # check out and err
    out, _ = capsys.readouterr()
    expected_out = ""
    assert out == expected_out


def test_configs_work_in_setupcfg(capsys: "CaptureFixture") -> None:
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

    Path("setup.cfg").write_text(
        dedent(
            """\
            [nbqa.config]
            flake8=.flake8
            """
        )
    )

    with pytest.raises(SystemExit):
        main(["flake8", "tests", "--ignore", "E302"])

    Path(".flake8").unlink()
    Path("setup.cfg").unlink()

    # check out and err
    out, _ = capsys.readouterr()
    expected_out = ""
    assert out == expected_out


def test_configs_work_in_nbqaini(capsys: "CaptureFixture") -> None:
    """
    Check a .nbqa.ini file is picked up by nbqa.

    No longer "officially" supported but keeping this here
    for backwards compatibility.

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

    Path(".nbqa.ini").write_text(
        dedent(
            """\
            [flake8]
            config=.flake8
            """
        )
    )

    with pytest.raises(SystemExit):
        main(["flake8", "tests", "--ignore", "E302"])

    Path(".flake8").unlink()
    Path(".nbqa.ini").unlink()

    # check out and err
    out, _ = capsys.readouterr()
    assert out == ""


def test_setupcfg_is_preserved(capsys: "CaptureFixture") -> None:
    """
    Check setup.cfg file is automatically picked up by nbqa.

    Parameters
    ----------
    capsys
        Pytest fixture to capture stdout and stderr.
    """
    Path("setup.cfg").write_text(
        dedent(
            """\
            [flake8]
            ignore=F401
            select=E303
            quiet=1
            """
        )
    )

    with pytest.raises(SystemExit):
        main(["flake8", "tests", "--ignore", "E302"])

    # check out and err
    out, _ = capsys.readouterr()
    assert out == ""


def test_invalid_config():
    msg = re.escape(
        """\
pyproject.toml is not a valid config file for 'flake8'.

If you believe it is, please file an issue at https://github.com/nbQA-dev/nbQA/issues.
"""
    )
    with pytest.raises(ValueError, match=msg):
        main(["flake8", "tests", "--nbqa-config=pyproject.toml"])


def test_nonexistent_config():
    with pytest.raises(FileNotFoundError, match=r"situp\.cfg not found\."):
        main(["flake8", "tests", "--nbqa-config=situp.cfg"])


def test_non_supported_tool():
    with pytest.raises(SystemExit):
        main(
            ["py_compile", str(CLEAN_NOTEBOOK), "--nbqa-config=.pre-commit-config.yaml"]
        )
