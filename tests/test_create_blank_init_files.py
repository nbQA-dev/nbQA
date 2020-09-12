"""
Check that blank :code:`__init__.py` files are created.

This is necessary for :code:`mypy` to work.
"""

import os
from pathlib import Path
from typing import TYPE_CHECKING

from nbqa.__main__ import _create_blank_init_files

if TYPE_CHECKING:
    from py._path.local import LocalPath


def test_create_blank_init_files(tmpdir: "LocalPath") -> None:
    """
    Check that if a notebook is in current working directory then no init file is made.

    Parameters
    ----------
    tmpdir
        Pytest fixture, gives us a temporary directory.
    """
    _create_blank_init_files(
        Path(os.path.join("tests", "data", "notebook_for_testing.ipynb")),
        tmpdir,
        Path.cwd(),
    )
    result = list(Path(tmpdir).rglob("__init__.py"))
    expected = [
        Path(tmpdir).joinpath(os.path.join("tests", "__init__.py")),
        Path(tmpdir).joinpath(os.path.join("tests", "data", "__init__.py")),
    ]
    assert result == expected
