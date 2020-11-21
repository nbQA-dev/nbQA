"""Check that users are encouraged to report bugs if reconstructing notebook fails."""

import os
import re
import sys
from pathlib import Path
from textwrap import dedent
from typing import TYPE_CHECKING

import pytest

from nbqa.__main__ import main

if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture
    from _pytest.monkeypatch import MonkeyPatch


def test_missing_command() -> None:
    """Check useful error is raised if :code:`nbqa` is run with an invalid command."""
    msg = dedent(
        """\
    \x1b\\[1mCommand `some\\-fictional\\-command` not found by nbqa\\.\x1b\\[0m

    Please make sure you have it installed in the same Python environment as nbqa\\. \
See
    e\\.g\\. https://realpython\\.com/python\\-virtual\\-environments\\-a\\-primer/\
 for how to set up
    a virtual environment in Python\\.

    Since nbqa is installed at .* and uses the Python executable found at
    .*, you could fix this issue by running `.* \\-m pip install some\\-fictional\\-command`\\.
        """
    )
    with pytest.raises(ModuleNotFoundError, match=msg):
        main(["some-fictional-command", "tests", "--some-flag"])


def test_missing_root_dir(capsys: "CaptureFixture") -> None:
    """Check useful error message is raised if :code:`nbqa` is called without root_dir."""
    prefix = "\x1b[1m"
    suffix = "\x1b[0m"
    pattern = re.escape(
        f"""\
usage: nbqa <code quality tool> <notebook or directory> <nbqa options> \
<code quality tool arguments>

{prefix}Please specify:{suffix}
- 1) a code quality tool (e.g. `black`, `pyupgrade`, `flake`, ...)
- 2) some notebooks (or, if supported by the tool, directories)
- 3) (optional) flags for nbqa (e.g. `--nbqa-mutate`)
- 4) (optional) flags for code quality tool (e.g. `--line-length` for `black`)

{prefix}Examples:{suffix}
    nbqa flake8 notebook.ipynb
    nbqa black notebook.ipynb --line-length=96
    nbqa pyupgrade notebook_1.ipynb notebook_2.ipynb

{prefix}Mutation:{suffix} to let `nbqa` modify your notebook(s), \
also pass `--nbqa-mutate`, e.g.:
    nbqa black notebook.ipynb --nbqa-mutate

See https://nbqa.readthedocs.io/en/latest/index.html for more details on \
how to run `nbqa`.\
"""
    )

    pattern = pattern + ".*: error: the following arguments are required: root_dirs\n"

    with pytest.raises(SystemExit):
        main(["flake8", "--ignore=E203"])
    _, err = capsys.readouterr()
    assert re.fullmatch(pattern, err, re.DOTALL)


@pytest.mark.usefixtures("tmp_remove_comments")
def test_unable_to_reconstruct_message() -> None:
    """Check error message shows if we're unable to reconstruct notebook."""
    path = os.path.abspath(os.path.join("tests", "data", "notebook_for_testing.ipynb"))
    message = f"Error reconstructing {path}"
    with pytest.raises(RuntimeError) as excinfo:
        main(["remove_comments", path, "--nbqa-mutate"])
    assert message in str(excinfo.value)


def test_unable_to_reconstruct_message_pythonpath(monkeypatch: "MonkeyPatch") -> None:
    """
    Same as ``test_unable_to_reconstruct_message`` but we check ``PYTHONPATH`` updates correctly.

    Parameters
    ----------
    monkeypatch
        Pytest fixture, we use it to override ``PYTHONPATH``.
    """
    path = os.path.abspath(os.path.join("tests", "data", "notebook_for_testing.ipynb"))
    message = f"Error reconstructing {path}"
    monkeypatch.setenv("PYTHONPATH", os.path.join(os.getcwd(), "tests"))
    monkeypatch.setattr("sys.path", sys.path + [os.path.join(os.getcwd(), "tests")])
    with pytest.raises(RuntimeError, match=message):
        main(["remove_comments", path, "--nbqa-mutate"])


def test_unable_to_parse() -> None:
    """Check error message shows if we're unable to parse notebook."""
    path = Path("tests") / "data/invalid_notebook.ipynb"
    path.write_text("foo")
    message = f"Error parsing {str(path)}"
    with pytest.raises(RuntimeError) as excinfo:
        main(["flake8", str(path), "--nbqa-mutate"])
    path.unlink()
    assert message in str(excinfo.value)


@pytest.mark.usefixtures("tmp_print_6174")
def test_unable_to_parse_output(capsys: "CaptureFixture") -> None:
    """
    Check user is encouraged to report bug if we're unable to parse tool's output.

    Parameters
    ----------
    capsys
        Pytest fixture to capture stdout and stderr.
    """
    path = Path("tests") / "data/notebook_for_testing.ipynb"
    expected_err = dedent(
        """\
        \x1b\\[1mKeyError(.*) while parsing output from applying print_6174 to \
tests.data.notebook_for_testing\\.ipynb
        Please report a bug at https://github\\.com/nbQA\\-dev/nbQA/issues \x1b\\[0m
        """
    )
    expected_out = f"{str(path)}:6174:0 some silly warning\n"
    with pytest.raises(SystemExit):
        main(["print_6174", str(path), "--nbqa-mutate"])
    out, err = capsys.readouterr()
    re.match(expected_err, err)
    assert expected_out == out


def test_directory_without_notebooks(capsys: "CaptureFixture") -> None:
    """
    Check sensible error message is returned if none of the directories passed have notebooks.

    Parameters
    ----------
    capsys
        Pytest fixture to capture stdout and stderr.
    """
    with pytest.raises(SystemExit):
        main(["black", "docs"])
    _, err = capsys.readouterr()
    assert err == "No .ipynb notebooks found in given directories: docs\n"
