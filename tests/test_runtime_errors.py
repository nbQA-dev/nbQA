"""Check that users are encouraged to report bugs if reconstructing notebook fails."""

import os
import re
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
    # pylint: disable=C0301
    msg = dedent(
        """\
        \x1b\\[1;31mCommand `some-fictional-command` not found by nbqa.\x1b\\[0m

        Please make sure you have it installed in the same Python environment as nbqa. See
        e.g. https://realpython\\.com/python\\-virtual\\-environments\\-a\\-primer/ for how to set up
        a virtual environment in Python.

        Since nbqa is installed at .* and uses the Python executable found at
        .*, you could fix this issue by running `.* -m pip install some-fictional-command`.
        """
    )
    # pylint: disable=C0301
    with pytest.raises(ModuleNotFoundError, match=msg):
        main(["some-fictional-command", "tests", "--some-flag"])


def test_missing_root_dir() -> None:
    """Check useful error message is raised if :code:`nbqa` is called without root_dir."""
    msg = dedent(
        """\
        \x1b\\[1;31mPlease specify both a command and a notebook/directory\x1b\\[0m, e.g.:

            nbqa flake8 my_notebook.ipynb

        To know all the options supported by nbqa, use `nbqa --help`. To
        read in detail about the various configuration options supported by
        nbqa, refer to https://nbqa\\.readthedocs\\.io/en/latest/configuration\\.html
        """
    )
    with pytest.raises(ValueError, match=msg):
        main(["flake8", "--ignore=E203"])


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
    with pytest.raises(RuntimeError) as excinfo:
        main(["remove_comments", path, "--nbqa-mutate"])
    assert message in str(excinfo.value)


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
        rf"""\
        \x1b\[1;31m😭 KeyError(.*) while parsing output from applying print_6174 to {str(path)} 😭
        Please report a bug at https://github\.com/nbQA\-dev/nbQA/issues 🙏\x1b\[0m
        """
    )
    with pytest.raises(SystemExit):
        main(["print_6174", str(path), "--nbqa-mutate"])
    out, err = capsys.readouterr()
    expected_out = f"{str(path)}:6174:0 some silly warning{os.linesep}"
    re.match(expected_err, err)
    assert expected_out in out
