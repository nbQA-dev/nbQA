"""Check function which lists notebooks in directory."""

import shutil
from pathlib import Path
from typing import TYPE_CHECKING

from nbqa.__main__ import _get_notebooks

if TYPE_CHECKING:
    from py._path.local import LocalPath

CLEAN_NOTEBOOK = Path("tests") / "data/clean_notebook.ipynb"


def test_get_notebooks(tmpdir: "LocalPath"):
    """
    Check that unwanted directories are excluded.

    Parameters
    ----------
    tmpdir
        Pytest fixture, gives us a temporary directory.

    """
    Path(tmpdir / ".git/tests/data").mkdir(parents=True)
    shutil.copy(str(CLEAN_NOTEBOOK), str(tmpdir / ".git" / CLEAN_NOTEBOOK))
    result = list(_get_notebooks(tmpdir))
    assert not result
