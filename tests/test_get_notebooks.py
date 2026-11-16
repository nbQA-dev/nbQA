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
def test_get_notebooks(tmpdir: "LocalPath", dir_: str) -> None:
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


@pytest.mark.parametrize("dir_", ["build", "dist", "venv"])
def test_get_notebooks_in_excluded_parent_dir(tmpdir: "LocalPath", dir_: str) -> None:
    """
    Check that excluded directory names only apply below the given directory.

    Parameters
    ----------
    tmpdir
        Pytest fixture, gives us a temporary directory.
    dir_
        Directory which the project being checked lives in.
    """
    root_dir = Path(tmpdir) / dir_ / "project"
    root_dir.mkdir(parents=True)
    shutil.copy(str(CLEAN_NOTEBOOK), str(root_dir))
    result = list(_get_notebooks(str(root_dir)))
    assert result == [root_dir / CLEAN_NOTEBOOK.name]
