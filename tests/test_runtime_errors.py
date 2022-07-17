"""Check that users are encouraged to report bugs if reconstructing notebook fails."""

import os
import re
import subprocess
import sys
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from nbqa.__main__ import main

if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture
    from _pytest.monkeypatch import MonkeyPatch


def test_missing_command() -> None:
    """Check useful error is raised if :code:`nbqa` is run with an invalid command."""
    msg = (
        "\x1b\\[1mCommand `some-fictional-command` not found by nbqa.\x1b\\[0m\n"
        "\n"
        "Please make sure you have it installed in the same Python environment as nbqa. See\n"
        "e.g. https://realpython.com/python\\-virtual\\-environments\\-a\\-primer/ for how to set up\n"
        "a virtual environment in Python, and run:\n"
        "\n"
        "    `python -m pip install some-fictional-command`.\n"
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
- 3) (optional) flags for nbqa (e.g. `--nbqa-diff`, `--nbqa-shell`)
- 4) (optional) flags for code quality tool (e.g. `--line-length` for `black`)

{prefix}Examples:{suffix}
    nbqa flake8 notebook.ipynb
    nbqa black notebook.ipynb --line-length=96
    nbqa pyupgrade notebook_1.ipynb notebook_2.ipynb

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
    main(["remove_comments", path])
    _, err = capsys.readouterr()
    assert f"\n\x1b[1mnbQA failed to process {path} with exception " in err
    assert (
        "Tool did not preserve code separators and cannot be safely used with nbQA"
        in err
    )


@pytest.mark.usefixtures("tmp_remove_all")
def test_remove_all_no_trailing_sc(capsys: "CaptureFixture") -> None:
    """Check error message shows if we're unable to reconstruct notebook."""
    path = os.path.abspath(os.path.join("tests", "data", "t.ipynb"))
    main(["remove_all", path, "--nbqa-diff"])
    out, err = capsys.readouterr()
    expected_out = (
        "\x1b[1mCell 1\x1b[0m\n"
        "------\n"
        f"\x1b[1;37m--- {path}\n"
        f"\x1b[0m\x1b[1;37m+++ {path}\n"
        "\x1b[0m\x1b[36m@@ -1 +1 @@\n"
        "\x1b[0m\x1b[31m-from t import A\n"
        "\x1b[0m\x1b[32m+\n"
        "\x1b[0m\n"
        "To apply these changes, remove the `--nbqa-diff` flag\n"
    )
    assert out == expected_out
    assert err == ""


@pytest.mark.usefixtures("tmp_remove_all")
def test_remove_all_trailing_semicolon(capsys: "CaptureFixture") -> None:
    """Check error message shows if we're unable to reconstruct notebook."""
    path = os.path.abspath(
        os.path.join("tests", "data", "notebook_with_trailing_semicolon.ipynb")
    )
    main(["remove_all", path, "--nbqa-diff"])
    out, err = capsys.readouterr()
    expected_out = (
        "\x1b[1mCell 1\x1b[0m\n"
        "------\n"
        f"\x1b[1;37m--- {path}\n"
        f"\x1b[0m\x1b[1;37m+++ {path}\n"
        "\x1b[0m\x1b[36m@@ -1,3 +1 @@\n"
        "\x1b[0m\x1b[31m-import glob;\n"
        "\x1b[0m\x1b[31m-import nbqa;\n"
        "\x1b[0m\n"
        "\x1b[1mCell 2\x1b[0m\n"
        "------\n"
        f"\x1b[1;37m--- {path}\n"
        f"\x1b[0m\x1b[1;37m+++ {path}\n"
        "\x1b[0m\x1b[36m@@ -1,3 +1 @@\n"
        "\x1b[0m\x1b[31m-def func(a, b):\n"
        "\x1b[0m\x1b[31m-    pass;\n"
        "\x1b[0m\x1b[31m- \n"
        "\x1b[0m\x1b[32m+\n"
        "\x1b[0m\n"
        "To apply these changes, remove the `--nbqa-diff` flag\n"
    )
    assert out == expected_out
    assert err == ""


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
        [sys.executable, "-m", "nbqa", "remove_comments", path],
        stderr=subprocess.PIPE,
        env=os.environ,
        text=True,
    )
    expected_stderr = f"\n\x1b[1mnbQA failed to process {path} with exception "
    expected_returncode = 123
    assert expected_stderr in output.stderr
    assert output.returncode == expected_returncode


def test_unable_to_parse(capsys: "CaptureFixture") -> None:
    """Check error message shows if we're unable to parse notebook."""
    path = Path("tests") / "data/invalid_notebook.ipynb"
    path.write_text("foo")
    main(["flake8", str(path)])
    path.unlink()
    message = "No valid .ipynb notebooks found"
    _, err = capsys.readouterr()
    assert message in err


def test_unable_to_parse_with_valid_notebook(capsys: "CaptureFixture") -> None:
    """Check error message shows if we're unable to parse notebook."""
    path_0 = Path("tests") / "data/invalid_notebook.ipynb"
    path_0.write_text("foo")
    path_1 = Path("tests") / "data/notebook_for_testing.ipynb"
    main(["flake8", str(path_0), str(path_1), "--select", "E402"])
    path_0.unlink()
    out, err = capsys.readouterr()
    expected_out = (
        f"{str(path_1)}:cell_4:1:1: E402 module level import not at top of file\n"
        f"{str(path_1)}:cell_5:1:1: E402 module level import not at top of file\n"
        f"{str(path_1)}:cell_5:2:1: E402 module level import not at top of file\n"
    )
    expected_err = f"\n\x1b[1mnbQA failed to process {str(path_0)} with exception "
    assert expected_out == out
    assert expected_err in err


def test_unable_to_parse_with_valid_notebook_md(capsys: "CaptureFixture") -> None:
    """Check error message shows if we're unable to parse notebook."""
    path_0 = Path("tests") / "data/invalid_notebook.ipynb"
    path_0.write_text("foo")
    path_1 = Path("tests") / "data/notebook_for_testing.ipynb"
    main(["mdformat", str(path_0), str(path_1), "--nbqa-md", "--nbqa-diff"])
    path_0.unlink()
    out, err = capsys.readouterr()
    expected_out = (
        "\x1b[1mCell 2\x1b[0m\n"
        "------\n"
        f"\x1b[1;37m--- {str(path_1)}\n"
        f"\x1b[0m\x1b[1;37m+++ {str(path_1)}\n"
        "\x1b[0m\x1b[36m@@ -1,2 +1 @@\n"
        "\x1b[0m\x1b[31m-First level heading\n"
        "\x1b[0m\x1b[31m-===\n"
        "\x1b[0m\x1b[32m+# First level heading\n"
        "\x1b[0m\n"
        "To apply these changes, remove the `--nbqa-diff` flag\n"
    )
    expected_err = f"\n\x1b[1mnbQA failed to process {str(path_0)} with exception "
    assert expected_out == out
    assert expected_err in err


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
    main(["print_6174", str(path)])
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
