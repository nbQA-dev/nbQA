"""
Check useful error message is raised if :code:`nbqa` is called without root_dir.

Some tools, like :code:`flake8`, can be run without this argument, but we always require
it.
"""

import pytest

from nbqa.__main__ import main


def test_missing_root_dir() -> None:
    """
    Check useful error message is raised if :code:`nbqa` is called without root_dir.
    """
    msg = (
        "Please specify both a command and a notebook/directory, e.g.\n"
        "nbqa flake8 my_notebook.ipynb"
    )
    with pytest.raises(ValueError, match=msg):
        main(["flake8", "--ignore=E203"])
