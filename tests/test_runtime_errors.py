"""Check that users are encouraged to report bugs if reconstructing notebook fails."""

import os
import re
import subprocess
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
def test_unable_to_reconstruct_message(capsys: "CaptureFixture") -> None:
    """Check error message shows if we're unable to reconstruct notebook."""
    path = os.path.abspath(os.path.join("tests", "data", "notebook_for_testing.ipynb"))
    message = f"Error reconstructing {path}"
    main(["remove_comments", path, "--nbqa-mutate"])
    _, err = capsys.readouterr()
    assert message in err


def test_unable_to_reconstruct_message_pythonpath(monkeypatch: "MonkeyPatch") -> None:
    """
    Same as ``test_unable_to_reconstruct_message`` but we check ``PYTHONPATH`` updates correctly.

    Parameters
    ----------
    monkeypatch
        Pytest fixture, we use it to override ``PYTHONPATH``.
    """
    path = os.path.abspath(os.path.join("tests", "data", "notebook_for_testing.ipynb"))
    monkeypatch.setenv("PYTHONPATH", os.path.join(os.getcwd(), "tests"))
    # We need to run the command via subprocess, so PYTHONPATH influences python
    output = subprocess.run(
        [sys.executable, "-m", "nbqa", "remove_comments", path, "--nbqa-mutate"],
        stderr=subprocess.PIPE,
        env=os.environ,
        universal_newlines=True,  # from Python3.7 this can be replaced with `text`
    )
    expected_stderr = (
        f'nbQA failed while processing {path} with exception "StopIteration()"\n'
        "\x1b[1m\nIf you believe the notebook(s) to be valid, please report a bug at https://github.com/nbQA-dev/nbQA/issues \x1b[0m\n"  # pylint: disable=C0301  # noqa: E501
    )
    expected_returncode = 123
    assert expected_stderr == output.stderr
    assert output.returncode == expected_returncode


def test_unable_to_parse(capsys: "CaptureFixture") -> None:
    """Check error message shows if we're unable to parse notebook."""
    path = Path("tests") / "data/invalid_notebook.ipynb"
    path.write_text("foo")
    main(["flake8", str(path), "--nbqa-mutate"])
    path.unlink()
    message = f"Error parsing {str(path)}"
    _, err = capsys.readouterr()
    assert message in err


@pytest.mark.usefixtures("tmp_print_6174")
def test_unable_to_parse_output(capsys: "CaptureFixture") -> None:
    """
    Check that nbQA doesn't crash when output can't be parsed.

    Parameters
    ----------
    capsys
        Pytest fixture to capture stdout and stderr.
    """
    path = Path("tests") / "data/notebook_for_testing.ipynb"
    main(["print_6174", str(path), "--nbqa-mutate"])
    out, _ = capsys.readouterr()
    expected_out = f"{str(path)}:6174:0 some silly warning\n"
    assert out == expected_out


def test_directory_without_notebooks(capsys: "CaptureFixture") -> None:
    """
    Check sensible error message is returned if none of the directories passed have notebooks.

    Parameters
    ----------
    capsys
        Pytest fixture to capture stdout and stderr.
    """
    main(["black", "docs"])
    _, err = capsys.readouterr()
    assert err == "No .ipynb notebooks found in given directories: docs\n"
