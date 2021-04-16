"""Check function which lists notebooks in directory."""

import re
import shutil
import sys
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from nbqa.__main__ import _get_notebooks, _temp_python_file_for_notebook

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


@pytest.mark.skipif("win" in sys.platform, reason="got no time for that")
def test_name_with_dot() -> None:
    "Check conversion happens as expected when name contains dot."
    try:
        Path("UJ1.1 .ipynb").touch()
        result = _temp_python_file_for_notebook(Path("UJ1.1 .ipynb"), "tmp", Path.cwd())
        expected = r"tmp/UJ1\.1 _\d+\.py"
        assert re.search(expected, str(result)) is not None
    finally:
        Path("UJ1.1 .ipynb").unlink()
