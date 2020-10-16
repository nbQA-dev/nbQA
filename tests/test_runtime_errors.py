"""Check that users are encouraged to report bugs if reconstructing notebook fails."""

import os
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from nbqa.__main__ import main

if TYPE_CHECKING:
    from _pytest.monkeypatch import MonkeyPatch


def test_missing_command() -> None:
    """Check useful error is raised if :code:`nbqa` is run with an invalid command."""
    command = "some-fictional-command"
    msg = (
        f"Command `{command}` not found. "
        "Please make sure you have it installed in the same environment as nbqa.\n"
        "See e.g. https://realpython.com/python-virtual-environments-a-primer/ for how to "
        "set up a virtual environment in Python."
    )
    with pytest.raises(ValueError, match=msg):
        main([command, "tests", "--some-flag"])


def test_missing_root_dir() -> None:
    """Check useful error message is raised if :code:`nbqa` is called without root_dir."""
    msg = (
        "Please specify both a command and a notebook/directory, e.g.\n"
        "nbqa flake8 my_notebook.ipynb"
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
