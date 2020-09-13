"""Check local config files are picked up by nbqa."""

import difflib
import os
from pathlib import Path
from textwrap import dedent
from typing import TYPE_CHECKING

import pytest

from nbqa.__main__ import main

if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture


def test_configs_work(tmp_notebook_for_testing: Path, capsys: "CaptureFixture") -> None:
    """
    Check a flake8 cfg file is picked up by nbqa.

    Parameters
    ----------
    tmp_notebook_for_testing
        Temporary copy of :code:`notebook_for_testing.ipynb`.
    capsys
        Pytest fixture to capture stdout and stderr.
    """
    with open(".flake8", "w") as handle:
        handle.write("[flake8]\nignore=F401\nselect=E303\nquiet=1\n")

    # check diff
    with open(tmp_notebook_for_testing, "r") as handle:
        before = handle.readlines()
    with pytest.raises(SystemExit):
        main(["flake8", "tests", "--ignore", "E302", "--nbqa-config", ".flake8"])

    Path(".flake8").unlink()

    with open(tmp_notebook_for_testing, "r") as handle:
        after = handle.readlines()
    result = "".join(difflib.unified_diff(before, after))
    expected = ""
    assert result == expected

    # check out and err
    out, err = capsys.readouterr()
    notebook = os.path.abspath(
        os.path.join("tests", "data", "notebook_starting_with_md.ipynb")
    )
    expected_out = f"{notebook}\n"
    expected_err = ""
    assert sorted(out.splitlines()) == sorted(expected_out.splitlines())
    assert sorted(err.splitlines()) == sorted(expected_err.splitlines())


def test_configs_work_in_nbqa_ini(
    tmp_notebook_for_testing: Path, capsys: "CaptureFixture"
) -> None:
    """
    Check a flake8 cfg file is picked up by nbqa.

    Parameters
    ----------
    tmp_notebook_for_testing
        Temporary copy of :code:`notebook_for_testing.ipynb`.
    capsys
        Pytest fixture to capture stdout and stderr.
    """
    with open(".flake8", "w") as handle:
        handle.write(
            dedent(
                """\
            [flake8]
            ignore=F401
            select=E303
            quiet=1
            """
            )
        )

    with open("setup.cfg", "w") as handle:
        handle.write(
            dedent(
                """\
            [nbqa.flake8]
            config=.flake8
            """
            )
        )

    # check diff
    with open(tmp_notebook_for_testing, "r") as handle:
        before = handle.readlines()
    with pytest.raises(SystemExit):
        main(["flake8", "tests", "--ignore", "E302"])

    Path(".flake8").unlink()
    Path("setup.cfg").unlink()

    with open(tmp_notebook_for_testing, "r") as handle:
        after = handle.readlines()
    result = "".join(difflib.unified_diff(before, after))
    expected = ""
    assert result == expected

    # check out and err
    out, err = capsys.readouterr()
    notebook = os.path.abspath(
        os.path.join("tests", "data", "notebook_starting_with_md.ipynb")
    )
    expected_out = f"{notebook}\n"
    expected_err = ""
    assert sorted(out.splitlines()) == sorted(expected_out.splitlines())
    assert sorted(err.splitlines()) == sorted(expected_err.splitlines())
