"""Check function which lists notebooks in directory."""

import shutil
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from nbqa.__main__ import _get_notebooks

if TYPE_CHECKING:
    from py._path.local import LocalPath

CLEAN_NOTEBOOK = Path("tests") / "data/clean_notebook.ipynb"


@pytest.mark.parametrize("dir_", [".git", "venv", "_build"])
def test_get_notebooks(tmpdir: "LocalPath", dir_: str):
    """
    Check that unwanted directories are excluded.

    Parameters
    ----------
    tmpdir
        Pytest fixture, gives us a temporary directory.
    dir_
        Directory where we expected notebooks to be ignored.
    """
    Path(tmpdir / f"{dir_}/tests/data").mkdir(parents=True)
    shutil.copy(str(CLEAN_NOTEBOOK), str(tmpdir / dir_ / CLEAN_NOTEBOOK))
    result = list(_get_notebooks(tmpdir))
    assert not result
